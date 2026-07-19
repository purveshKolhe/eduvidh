import modal
import os
import json
import asyncio
import tempfile
import subprocess
import shutil
import pathlib

# Modal App Definition
app = modal.App("edu-video-generator")

# Image for Orchestrator
orchestrator_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "groq",
        "edge-tts",
        "aiohttp",
        "ffmpeg-python",
        "fastapi[standard]",
        "oracledb",
        "boto3"
    )
    .apt_install("ffmpeg")
    .env({
        "AWS_REQUEST_CHECKSUM_CALCULATION": "WHEN_REQUIRED",
        "AWS_RESPONSE_CHECKSUM_VALIDATION": "WHEN_REQUIRED"
    })
    .add_local_python_source("db_and_storage")
)

# Image for Render Worker (needs Node.js and Remotion)
render_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "curl", "git", "ffmpeg", "libnss3", "libnspr4", "libatk1.0-0",
        "libatk-bridge2.0-0", "libcups2", "libdrm2", "libxkbcommon0",
        "libxcomposite1", "libxdamage1", "libxfixes3", "libxrandr2",
        "libgbm1", "libasound2", "libpango-1.0-0", "libcairo2"
    )
    .run_commands(
        "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
        "apt-get install -y nodejs",
    )
    .pip_install("groq", "edge-tts", "aiohttp", "ffmpeg-python", "oracledb", "boto3")
    # Copy the Remotion project (excluding local node_modules to force a clean install)
    .add_local_dir("remotion-app", remote_path="/remotion-app", copy=True, ignore=["node_modules"])
    .run_commands(
        "cd /remotion-app && npm install --legacy-peer-deps",
        "cd /remotion-app && npx remotion bundle src/index.ts --out-dir=bundled --log=error" # PRE-BUNDLE FOR SPEED!
    )
    .env({
        "AWS_REQUEST_CHECKSUM_CALCULATION": "WHEN_REQUIRED",
        "AWS_RESPONSE_CHECKSUM_VALIDATION": "WHEN_REQUIRED"
    })
    .add_local_python_source("db_and_storage")
)

# --- Secrets ---
# Effortlessly load local .env variables for database/storage configuration.
# If .env does not exist, fall back to the custom-secret stored on modal.com.
env_file = pathlib.Path(".env")
if env_file.exists():
    app_secrets = [modal.Secret.from_dotenv()]
else:
    app_secrets = [
        modal.Secret.from_name("custom-secret")
    ]

# --- Helper Functions ---
async def generate_audio(text, output_path):
    import edge_tts
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_path)

# --- Render Worker ---
@app.function(
    image=render_image,
    # One CPU-bound slide renderer per container. Six workers plus two local VM
    # tabs cover the product's eight-slide maximum without paying for two cores
    # per remote slide.
    cpu=1.0,
    memory=1024,
    timeout=600,
    min_containers=0,
    max_containers=6,
    scaledown_window=2,
)
def render_slide_worker(slide_data, slide_index, est_duration):
    import socket
    import time
    import resource

    # Modal documents MODAL_TASK_ID as the identity of the container executing
    # this Function. Hostnames are not a stable or unique container identity.
    worker_id = os.environ.get("MODAL_TASK_ID", socket.gethostname())
    if slide_index == -1:
        # This is intentionally a real renderer warm-up, not a no-op. It starts
        # the same Remotion/Chromium execution path used by production renders.
        warm_output = os.path.join(tempfile.gettempdir(), f"warm_{worker_id}_{time.time_ns()}.mp4")
        warm_cmd = [
            "npx", "remotion", "render",
            "bundled", "EducationalVideo", warm_output,
            "--frames=0-0",
            "--concurrency=1",
            "--log=error",
        ]
        started_at = time.perf_counter()
        warm_process = subprocess.run(
            warm_cmd,
            cwd="/remotion-app",
            capture_output=True,
            text=True,
        )
        try:
            if warm_process.returncode != 0:
                raise RuntimeError(warm_process.stderr)
        finally:
            if os.path.exists(warm_output):
                os.remove(warm_output)
        return {
            "video_bytes": b"",
            "worker_id": worker_id,
            "metrics": {
                "remotion_seconds": time.perf_counter() - started_at,
                "ffmpeg_seconds": 0.0,
                "cpu_seconds": 0.0,
                "max_ram_mb": 0.0,
            }
        }

    print(f"Worker rendering slide {slide_index} | Est Duration: {est_duration:.1f}s")
    
    slide_data['durationInSeconds'] = est_duration
    
    props = {
        "slides": [slide_data],
        "audioUrls": [] # Audio merging is done by orchestrator now
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        props_path = os.path.join(tmpdir, "props.json")
        with open(props_path, "w") as f:
            json.dump(props, f)
            
        rendered_mp4 = os.path.join(tmpdir, "rendered.mp4")
        
        # Every worker emits only the three-second animation. The VM performs one
        # final assembly pass, freezing this last frame to the exact measured TTS
        # duration; this avoids eight separate per-slide muxes.
        cmd = [
            "npx", "remotion", "render", 
            "bundled", "EducationalVideo", 
            rendered_mp4,
            "--props", props_path,
            "--frames=0-71",
            "--concurrency=1",
            "--log=error",
        ]
        
        remotion_started_at = time.perf_counter()
        process = subprocess.run(cmd, cwd="/remotion-app", capture_output=True, text=True)
        remotion_seconds = time.perf_counter() - remotion_started_at
        if process.returncode != 0:
            print("Remotion Error:", process.stderr)
            raise Exception(f"Remotion failed: {process.stderr}")

        with open(rendered_mp4, "rb") as f:
            video_bytes = f.read()
            
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "video_bytes": video_bytes,
        "worker_id": worker_id,
        # Timers begin inside the already-started worker, excluding worker cold start.
        "metrics": {
            "remotion_seconds": remotion_seconds,
            "ffmpeg_seconds": 0.0,
            "cpu_seconds": usage.ru_utime + usage.ru_stime,
            "max_ram_mb": usage.ru_maxrss / 1024.0,
        },
    }

# --- Orchestrator ---
@app.function(
    image=orchestrator_image,
    cpu=1.0,
    memory=1024,
    timeout=1200,
    secrets=app_secrets,
    scaledown_window=2
)
async def orchestrate_job(job_id: str, prompt: str):
    import time
    import traceback
    import resource

    orchestrator_start_time = time.time()
    adapter = None
    cold_start_time = 0.0
    rendering_time = 0.0
    resources_used = {"pipeline_stage": "starting"}
    pipeline_stage = "adapter_initialization"

    try:
        from db_and_storage.adapter import get_adapter
        adapter = get_adapter()

        # Queue/container latency ends when this already-running orchestrator begins.
        pipeline_stage = "cold_start_measurement"
        video_data = adapter.get_video(job_id)
        if not video_data or not video_data.get("created_at"):
            raise RuntimeError("job record is missing its created_at timestamp")
        from datetime import datetime
        created_at = datetime.fromisoformat(video_data["created_at"].replace("Z", "+00:00"))
        cold_start_time = max(orchestrator_start_time - created_at.timestamp(), 0.0)
        print(f"Starting job {job_id} | Cold Start: {cold_start_time:.2f}s")

        pipeline_stage = "script_generation"
        from groq import AsyncGroq
        groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
        system_prompt = """
        You are an educational video script writer. Based on the user's topic, generate a JSON array of exactly 6 slides.
        Use the following types: TitleSlide, AgendaSlide, SectionDividerSlide, ConceptExplanationSlide, ComparisonSlide, StepByStepProcessSlide, DataStatisticsSlide, ExampleCaseStudySlide, SummarySlide, QuestionDiscussionSlide.
        Each slide must have: 'type', 'title', 'content' (array of strings, or exactly 4 strings for ComparisonSlide), 'narration' (text to be spoken), and optionally 'latex' (a single string containing the math expression WITHOUT any $ delimiters) and 'icon' (lucide-react icon name like 'Brain').
        Respond ONLY with raw JSON, no markdown blocks.
        """
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            model="openai/gpt-oss-20b",
            temperature=0.7,
            max_tokens=4096,
        )

        raw_json = chat_completion.choices[0].message.content.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3]
        slides = json.loads(raw_json)
        if not isinstance(slides, list) or len(slides) != 6:
            raise ValueError("LLM output must be a JSON array of exactly six slides")
        if not all(isinstance(slide, dict) for slide in slides):
            raise ValueError("every slide must be a JSON object")

        pipeline_stage = "script_persistence"
        adapter.update_video(video_id=job_id, status="script_generated", slides_data=slides)

        # State is persisted before any remote work can fail or wait for capacity.
        pipeline_stage = "render_dispatch"
        for slide in slides:
            text = slide.get("narration", slide.get("title", ""))
            slide["durationInSeconds"] = max(len(text) * 0.07 + 2.0, 5.0)
        adapter.update_video(video_id=job_id, status="rendering", slides_data=slides)
        print("Spawning Remotion render workers...")
        rendering_start_time = time.time()
        worker_calls = []
        for i, slide in enumerate(slides):
            worker_calls.append(await render_slide_worker.spawn.aio(slide, i, slide["durationInSeconds"]))

        # TTS is intentionally outside rendering_time.
        pipeline_stage = "tts_generation"
        print("Generating TTS concurrently...")
        with tempfile.TemporaryDirectory() as tts_dir:
            audio_paths = []
            tasks = []
            for i, slide in enumerate(slides):
                text = slide.get("narration", slide.get("title", ""))
                audio_path = os.path.join(tts_dir, f"audio_{i}.mp3")
                audio_paths.append(audio_path)
                tasks.append(generate_audio(text, audio_path))
            await asyncio.gather(*tasks)
            audio_bytes_list = []
            for path in audio_paths:
                with open(path, "rb") as audio_file:
                    audio_bytes_list.append(audio_file.read())

        pipeline_stage = "render_collection"
        print("Waiting for rendered video chunks...")
        worker_results = [await call.get.aio() for call in worker_calls]
        slide_videos_bytes = [result["video_bytes"] for result in worker_results]
        worker_metrics = [result["metrics"] for result in worker_results]

        pipeline_stage = "single_pass_assembly"
        print("Assembling the complete video in one FFmpeg pass...")
        merge_ffmpeg_seconds = 0.0
        with tempfile.TemporaryDirectory() as merge_dir:
            animation_paths = []
            audio_paths = []
            for i in range(len(slides)):
                animation_path = os.path.join(merge_dir, f"animation_{i}.mp4")
                audio_path = os.path.join(merge_dir, f"audio_{i}.mp3")
                with open(animation_path, "wb") as video_file:
                    video_file.write(slide_videos_bytes[i])
                with open(audio_path, "wb") as audio_file:
                    audio_file.write(audio_bytes_list[i])
                animation_paths.append(animation_path)
                audio_paths.append(audio_path)

            audio_durations = []
            for audio_path in audio_paths:
                probe = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                audio_durations.append(max(3.0, float(probe.stdout.strip())))

            command = ["ffmpeg", "-y"]
            for animation_path in animation_paths:
                command.extend(["-i", animation_path])
            for audio_path in audio_paths:
                command.extend(["-i", audio_path])

            filters = []
            concat_inputs = []
            slide_count = len(slides)
            for i, duration in enumerate(audio_durations):
                filters.append(
                    f"[{i}:v]tpad=stop_mode=clone:stop_duration={max(0.0, duration - 3.0):.3f},setpts=PTS-STARTPTS[v{i}]"
                )
                filters.append(
                    f"[{slide_count + i}:a]apad,atrim=duration={duration:.3f},asetpts=PTS-STARTPTS[a{i}]"
                )
                concat_inputs.extend([f"[v{i}]", f"[a{i}]"])
            filters.append("".join(concat_inputs) + f"concat=n={slide_count}:v=1:a=1[vout][aout]")

            final_output = os.path.join(merge_dir, "final_output.mp4")
            started_at = time.perf_counter()
            subprocess.run(
                command + [
                    "-filter_complex", ";".join(filters),
                    "-map", "[vout]", "-map", "[aout]",
                    "-r", "24", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "32",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", final_output,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            merge_ffmpeg_seconds = time.perf_counter() - started_at
            duration_probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", final_output],
                check=True,
                capture_output=True,
                text=True,
            )
            video_length = float(duration_probe.stdout.strip())

            # This is aggregate active render work; it excludes queue/cold start and TTS.
            remotion_seconds = sum(metric["remotion_seconds"] for metric in worker_metrics)
            worker_ffmpeg_seconds = sum(metric["ffmpeg_seconds"] for metric in worker_metrics)
            rendering_time = time.time() - rendering_start_time

            pipeline_stage = "video_upload"
            final_url = adapter.upload_video(final_output, job_id)

        orchestrator_usage = resource.getrusage(resource.RUSAGE_SELF)
        resources_used = {
            "orchestrator": {
                "cpu_seconds": orchestrator_usage.ru_utime + orchestrator_usage.ru_stime,
                "max_ram_mb": orchestrator_usage.ru_maxrss / 1024.0,
                "cpu_count": os.cpu_count() or 1,
            },
            "render_workers": worker_metrics,
            "rendering_breakdown_seconds": {
                "remotion": remotion_seconds,
                "worker_ffmpeg": worker_ffmpeg_seconds,
                "merge_ffmpeg": merge_ffmpeg_seconds,
                "total_compute_seconds": remotion_seconds + worker_ffmpeg_seconds + merge_ffmpeg_seconds,
                "wall_clock_rendering_seconds": rendering_time,
            },
        }

        pipeline_stage = "completion_persistence"
        adapter.update_video(
            video_id=job_id,
            status="completed",
            video_storage_url=final_url,
            cold_start_time=cold_start_time,
            rendering_time=rendering_time,
            video_length=video_length,
            resources_used=resources_used,
        )
        print(f"Job {job_id} completed successfully. URL: {final_url}")
    except Exception:
        error_trace = traceback.format_exc()
        print(f"Job {job_id} failed during {pipeline_stage}:\n{error_trace}")
        if adapter is not None:
            try:
                failure_resources = dict(resources_used)
                failure_resources.update({"pipeline_stage": pipeline_stage, "failed": True})
                adapter.update_video(
                    video_id=job_id,
                    status="failed",
                    error_message=error_trace,
                    cold_start_time=cold_start_time,
                    rendering_time=rendering_time if rendering_time else None,
                    resources_used=failure_resources,
                )
            except Exception:
                print(f"Could not persist failure for {job_id}:\n{traceback.format_exc()}")


# --- Webhook (Retired in favor of Azure VM control plane) ---
# The start_generation endpoint has been retired to avoid competing orchestrators.
# The Azure VM now serves the control plane.
