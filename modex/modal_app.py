import modal
import os
import json
import asyncio
import tempfile
import time
import subprocess
import shutil
import pathlib
import uuid
from typing import Any, Dict, List, Tuple

# Modal App Definition
app = modal.App("modex-video-generator")

# Image for Single 8-Core Container (has Chrome, Node, Python packages)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "curl", "git", "ffmpeg", "libnss3", "libnspr4", "libatk1.0-0",
        "libatk-bridge2.0-0", "libcups2", "libdrm2", "libxkbcommon0",
        "libxcomposite1", "libxdamage1", "libxfixes3", "libxrandr2",
        "libgbm1", "libasound2", "libpango-1.0-0", "libcairo2",
        "chromium", # Install open-source Chromium in /usr/bin/chromium
        "fonts-liberation", "fonts-dejavu-core", "fonts-noto-core", "fontconfig" # System fonts to fix blank text rendering
    )
    .run_commands(
        "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
        "apt-get install -y nodejs",
    )
    .pip_install(
        "groq",
        "edge-tts",
        "aiohttp",
        "ffmpeg-python",
        "fastapi[standard]",
        "oracledb",
        "boto3"
    )
    # Copy the Remotion project (excluding local node_modules)
    .add_local_dir("remotion-app", remote_path="/remotion-app", copy=True, ignore=["node_modules"])
    # Copy our custom modex renderer service to overwrite the fallback renderer
    .add_local_file("modex/renderer_service.js", remote_path="/remotion-app/renderer_service.js", copy=True)
    .run_commands(
        "cd /remotion-app && npm install --legacy-peer-deps",
        "cd /remotion-app && npx remotion bundle src/index.ts --out-dir=bundled --log=error" # Pre-bundle for speed!
    )
    .env({
        "AWS_REQUEST_CHECKSUM_CALCULATION": "WHEN_REQUIRED",
        "AWS_RESPONSE_CHECKSUM_VALIDATION": "WHEN_REQUIRED"
    })
    .add_local_python_source("db_and_storage")
)

# Load secrets from local .env in the parent directory
env_file = pathlib.Path(".env")
if env_file.exists():
    app_secrets = [modal.Secret.from_dotenv(env_file)]
else:
    app_secrets = [modal.Secret.from_name("custom-secret")]

# --- Helper Functions ---
async def generate_audio(text: str, output_path: str):
    import edge_tts
    text = text.strip() if text else ""
    if not text:
        text = "Next slide."
    try:
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(output_path)
    except Exception as e:
        print(f"edge-tts failed: {e}. Writing fallback silence...")
        # Write 1 second of silence as fallback
        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "1", output_path]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        await process.communicate()

async def probe_duration(path: str) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {stderr.decode(errors='replace')}")
    return float(stdout.decode().strip())

async def run_ffmpeg(args: List[str]):
    cmd = ["ffmpeg"] + args
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {stderr.decode(errors='replace')}")

async def assemble_video_once(
    animation_paths: List[str], audio_paths: List[str], final_output: str
) -> Tuple[List[float], float]:
    """
    Freeze each three-second animation at its last frame for the real narration
    length, then concatenate all audio/video pairs in one FFmpeg complex filter.
    """
    if len(animation_paths) != len(audio_paths) or not animation_paths:
        raise ValueError("animation and audio inputs must be non-empty and equally sized")

    audio_durations = await asyncio.gather(*(probe_duration(path) for path in audio_paths))
    slide_durations = [max(3.0, duration) for duration in audio_durations]
    slide_count = len(animation_paths)

    command: List[str] = ["-y"]
    for path in animation_paths:
        command.extend(["-i", path])
    for path in audio_paths:
        command.extend(["-i", path])

    filters: List[str] = []
    concat_inputs: List[str] = []
    for index, duration in enumerate(slide_durations):
        freeze_seconds = max(0.0, duration - 3.0)
        filters.append(
            f"[{index}:v]tpad=stop_mode=clone:stop_duration={freeze_seconds:.3f},"
            f"setpts=PTS-STARTPTS[v{index}]"
        )
        audio_input_index = slide_count + index
        filters.append(
            f"[{audio_input_index}:a]apad,atrim=duration={duration:.3f},"
            f"asetpts=PTS-STARTPTS[a{index}]"
        )
        concat_inputs.extend([f"[v{index}]", f"[a{index}]"])

    filters.append(
        "".join(concat_inputs) + f"concat=n={slide_count}:v=1:a=1[vout][aout]"
    )
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-r",
            "24",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "32",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            final_output,
        ]
    )

    started_at = time.perf_counter()
    await run_ffmpeg(command)
    return slide_durations, time.perf_counter() - started_at


@app.cls(
    image=image,
    cpu=8.0,
    memory=8192,
    secrets=app_secrets,
    scaledown_window=2,
    timeout=1200
)
class ExplainerGenerator:
    @modal.enter()
    def initialize_state(self):
        self.renderer_proc = None
        self.renderer_started = False

    async def ensure_renderer_service(self):
        if self.renderer_started:
            return
        
        print("Spawning persistent Node renderer service in background...")
        # We redirect stdout/stderr to a local log file inside the container for debug/audit purposes
        env = dict(os.environ)
        env["POOL_SIZE"] = "8"
        
        self.renderer_proc = subprocess.Popen(
            ["node", "renderer_service.js"],
            cwd="/remotion-app",
            env=env,
            stdout=open("/tmp/node_renderer.log", "w"),
            stderr=subprocess.STDOUT
        )
        self.renderer_started = True

    async def wait_for_renderer_ready(self):
        import aiohttp
        print("Waiting for Node renderer service to report healthy status...")
        async with aiohttp.ClientSession() as session:
            for _ in range(60):
                try:
                    async with session.get("http://127.0.0.1:5000/status") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            print(f"Node renderer is ready with {data['pool_size']} tabs initialized!")
                            return
                except Exception:
                    pass
                await asyncio.sleep(0.5)
        
        # If it failed, print the stdout logs of the node service
        if os.path.exists("/tmp/node_renderer.log"):
            with open("/tmp/node_renderer.log", "r") as f:
                print("Node Renderer Logs on Failure:")
                print(f.read())
        raise RuntimeError("Timeout waiting for Node renderer service to start")

    async def render_slide_local(self, slide_data: dict, slide_index: int, output_path: str) -> Dict[str, Any]:
        import aiohttp
        url = "http://127.0.0.1:5000/render"
        payload = {
            "slide_data": slide_data,
            "slide_index": slide_index,
            "est_duration": 3.0,
            "output_path": output_path
        }
        
        start_time = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            # High 300s timeout to allow complex slide components to seek and paint
            timeout = aiohttp.ClientTimeout(total=300)
            async with session.post(url, json=payload, timeout=timeout) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"Local Node renderer failed for slide {slide_index}: {text}")
                
                res_data = await response.json()
                total_seconds = time.perf_counter() - start_time
                return {
                    "slide_index": slide_index,
                    "total_seconds": round(total_seconds, 3)
                }

    async def generate_audio_timed(self, text: str, index: int, output_path: str) -> Dict[str, Any]:
        started_at = time.perf_counter()
        await generate_audio(text, output_path)
        return {
            "slide_index": index,
            "seconds": round(time.perf_counter() - started_at, 3)
        }

    @modal.method()
    async def generate_video(self, prompt: str) -> dict:
        orchestrator_started_at = time.perf_counter()
        
        # 1. Spawn Chrome/Node in background immediately (cold start masking)
        bg_browser_task = asyncio.create_task(self.ensure_renderer_service())

        # 2. Concurrently call Groq to generate script
        print("Calling Groq API for script generation...")
        from groq import AsyncGroq
        groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
        system_prompt = """
        You are an educational video script writer. Based on the user's topic, generate a JSON array of exactly 8 slides.
        Use the following types: TitleSlide, AgendaSlide, SectionDividerSlide, ConceptExplanationSlide, ComparisonSlide, StepByStepProcessSlide, DataStatisticsSlide, ExampleCaseStudySlide, SummarySlide, QuestionDiscussionSlide.
        Each slide must have: 'type', 'title', 'content' (array of strings, or exactly 4 strings for ComparisonSlide), 'narration' (text to be spoken), and optionally 'latex' (a single string containing the math expression WITHOUT any $ delimiters) and 'icon' (lucide-react icon name like 'Brain').
        Respond ONLY with raw JSON, no markdown blocks.
        """
        
        script_started_at = time.perf_counter()
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=4096,
        )
        script_seconds = time.perf_counter() - script_started_at

        raw_json = chat_completion.choices[0].message.content.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3]
        elif raw_json.startswith("```"):
            raw_json = raw_json[3:-3]
        slides = json.loads(raw_json)
        if isinstance(slides, dict):
            if "slides" in slides:
                slides = slides["slides"]
            else:
                for val in slides.values():
                    if isinstance(val, list):
                        slides = val
                        break
        
        total_slides = len(slides)
        print(f"Script generated with {total_slides} slides in {script_seconds:.2f}s.")

        # 3. Wait for browser initialization to complete (usually it's already done)
        await bg_browser_task
        await self.wait_for_renderer_ready()

        # 4. Generate audio and render slides concurrently
        temp_dir = tempfile.mkdtemp(prefix="modex_render_")
        animation_paths = [os.path.join(temp_dir, f"animation_{i}.mp4") for i in range(total_slides)]
        audio_paths = [os.path.join(temp_dir, f"audio_{i}.mp3") for i in range(total_slides)]

        render_jobs = [
            self.render_slide_local(slides[i], i, animation_paths[i])
            for i in range(total_slides)
        ]
        tts_jobs = [
            self.generate_audio_timed(slides[i].get("narration", slides[i].get("title", "")), i, audio_paths[i])
            for i in range(total_slides)
        ]

        print(f"Dispatching {total_slides} parallel renders and TTS audios on a single container...")
        parallel_started_at = time.perf_counter()
        render_metrics, tts_metrics = await asyncio.gather(
            asyncio.gather(*render_jobs),
            asyncio.gather(*tts_jobs)
        )
        parallel_seconds = time.perf_counter() - parallel_started_at
        print(f"Parallel rendering & TTS finished in {parallel_seconds:.2f}s.")

        # 5. Assemble final video using single-pass FFmpeg Complex Filter
        print("Assembling video and audio clips into final output...")
        final_output = os.path.join(temp_dir, "final_output.mp4")
        slide_durations, assembly_seconds = await assemble_video_once(
            animation_paths, audio_paths, final_output
        )
        video_length = await probe_duration(final_output)

        # 6. Upload final video to S3 compatible object storage (OCI)
        print("Uploading final output to storage...")
        upload_started_at = time.perf_counter()
        from db_and_storage.adapter import get_adapter
        adapter = get_adapter()
        
        job_id = str(uuid.uuid4())
        final_url = ""
        try:
            adapter.create_video(video_id=job_id, prompt=prompt)
            adapter.update_video(video_id=job_id, status="completed", slides_data=slides)
            final_url = adapter.upload_video(final_output, job_id)
        except Exception as db_err:
            print(f"Warning: Database update failed ({db_err}). Executing direct file upload...")
            final_url = adapter.upload_video(final_output, job_id)
            
        upload_seconds = time.perf_counter() - upload_started_at
        print(f"Upload complete. File URL: {final_url}")

        # Clean up temp folder
        shutil.rmtree(temp_dir, ignore_errors=True)

        # Calculate max metrics
        max_render_seconds = max((m["total_seconds"] for m in render_metrics), default=0.0)
        max_tts_seconds = max((m["seconds"] for m in tts_metrics), default=0.0)
        total_seconds = time.perf_counter() - orchestrator_started_at

        resources_used = {
            "environment": "Single 8-Core Modal Container (modex-concurrent-tabs)",
            "allocation_counts": {
                "total_slides": total_slides,
                "concurrent_local_tabs": total_slides
            },
            "timings_wall_clock_seconds": {
                "script_generation": round(script_seconds, 3),
                "max_slide_render": round(max_render_seconds, 3),
                "max_tts_generation": round(max_tts_seconds, 3),
                "parallel_render_and_tts": round(parallel_seconds, 3),
                "single_pass_assembly": round(assembly_seconds, 3),
                "upload": round(upload_seconds, 3),
                "total_wall_clock": round(total_seconds, 3)
            },
            "slide_durations_seconds": [round(d, 3) for d in slide_durations],
            "render_metrics": render_metrics,
            "tts_metrics": tts_metrics,
            "video_url": final_url,
            "video_length_seconds": round(video_length, 3)
        }
        
        return resources_used
