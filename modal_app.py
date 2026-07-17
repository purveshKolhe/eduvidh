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
    cpu=2.0,
    memory=1024,
    timeout=600,
    scaledown_window=2
)
def render_slide_worker(slide_data, slide_index, est_duration):
    import time
    import resource

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
        
        # Run Remotion render on PRE-BUNDLED code (first 3s @ 24fps = 71 frames)
        cmd = [
            "npx", "remotion", "render", 
            "bundled", "EducationalVideo", 
            rendered_mp4,
            "--props", props_path,
            "--frames=0-71",
            "--concurrency=2"
        ]
        
        remotion_started_at = time.perf_counter()
        process = subprocess.run(cmd, cwd="/remotion-app", capture_output=True, text=True)
        remotion_seconds = time.perf_counter() - remotion_started_at
        if process.returncode != 0:
            print("Remotion Error:", process.stderr)
            raise Exception(f"Remotion failed: {process.stderr}")

        ffmpeg_seconds = 0.0

        def run_ffmpeg(command):
            nonlocal ffmpeg_seconds
            started_at = time.perf_counter()
            result = subprocess.run(command, check=True, capture_output=True)
            ffmpeg_seconds += time.perf_counter() - started_at
            return result
            
        static_frame = os.path.join(tmpdir, "frame.png")
        run_ffmpeg([
            "ffmpeg", "-y", "-sseof", "-0.1", "-i", rendered_mp4,
            "-update", "1", "-q:v", "2", static_frame
        ])
        
        loop_duration = max(est_duration - 3.0, 1.0)
        concated_mp4 = os.path.join(tmpdir, "concated.mp4")
        
        if loop_duration > 0.5:
            looped_mp4 = os.path.join(tmpdir, "looped.mp4")
            run_ffmpeg([
                "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-i", static_frame,
                "-c:v", "libx264", "-preset", "ultrafast",
                "-t", str(loop_duration), "-pix_fmt", "yuvj420p", "-crf", "35",
                looped_mp4
            ])
            
            concat_list = os.path.join(tmpdir, "concat_list.txt")
            with open(concat_list, "w") as f:
                f.write(f"file '{rendered_mp4}'\n")
                f.write(f"file '{looped_mp4}'\n")
            
            run_ffmpeg([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                "-c", "copy", "-movflags", "+faststart", concated_mp4
            ])
        else:
            shutil.copy(rendered_mp4, concated_mp4)
            
        with open(concated_mp4, "rb") as f:
            video_bytes = f.read()
            
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "video_bytes": video_bytes,
        # Timers begin inside the already-started worker, excluding worker cold start.
        "metrics": {
            "remotion_seconds": remotion_seconds,
            "ffmpeg_seconds": ffmpeg_seconds,
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

        pipeline_stage = "audio_merge"
        print("Merging audio and concatenating slides...")
        merge_ffmpeg_seconds = 0.0
        with tempfile.TemporaryDirectory() as merge_dir:
            merged_slides = []

            def run_merge_ffmpeg(command):
                nonlocal merge_ffmpeg_seconds
                started_at = time.perf_counter()
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                merge_ffmpeg_seconds += time.perf_counter() - started_at

            for i in range(len(slides)):
                silent_mp4 = os.path.join(merge_dir, f"silent_{i}.mp4")
                audio_mp3 = os.path.join(merge_dir, f"audio_{i}.mp3")
                final_mp4 = os.path.join(merge_dir, f"merged_{i}.mp4")
                
                with open(silent_mp4, "wb") as f:
                    f.write(slide_videos_bytes[i])
                with open(audio_mp3, "wb") as f:
                    f.write(audio_bytes_list[i])

                run_merge_ffmpeg([
                    "ffmpeg", "-y", "-i", silent_mp4, "-i", audio_mp3,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-threads", "1", "-shortest", final_mp4
                ])
                merged_slides.append(final_mp4)

            list_file_path = os.path.join(merge_dir, "list.txt")
            with open(list_file_path, "w") as list_file:
                for path in merged_slides:
                    list_file.write(f"file '{path}'\n")

            final_output = os.path.join(merge_dir, "final_output.mp4")
            run_merge_ffmpeg([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file_path,
                "-c", "copy", final_output
            ])
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


# --- Webhook ---
@app.function(image=orchestrator_image, secrets=app_secrets, scaledown_window=2)
@modal.asgi_app()
def start_generation():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    web_app = FastAPI()

    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @web_app.post("/")
    async def start_generation_endpoint(request: dict):
        from db_and_storage.adapter import get_adapter
        prompt = request.get("prompt")
        if not prompt:
            return {"error": "Missing prompt"}
            
        adapter = get_adapter()
        # Create initial record in db
        job_id = adapter.create_video(prompt)
        
        await orchestrate_job.spawn.aio(job_id, prompt)
        
        return {"job_id": job_id, "status": "pending"}

    # Dynamic status endpoint to effortlessly support frontend polling on Oracle / Custom DBs
    @web_app.get("/status/{job_id}")
    async def get_generation_status(job_id: str):
        from db_and_storage.adapter import get_adapter
        adapter = get_adapter()
        try:
            video_data = adapter.get_video(job_id)
            if not video_data:
                return {"error": "Job not found"}
            return video_data
        except Exception as e:
            return {"error": str(e)}

    return web_app
