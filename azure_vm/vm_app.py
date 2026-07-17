import os
import sys
import json
import time
import uuid
import asyncio
import tempfile
import shutil
import resource
import subprocess
import pathlib
import logging
from typing import Any, Dict, List
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("azure_vm_pipeline")

# Add parent directory to path so we can import db_and_storage modules
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

from db_and_storage.adapter import get_adapter

# Load environment variables from the parent directory's .env file
dotenv_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Enforce OCI / S3 Checksum environment configurations
os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "WHEN_REQUIRED"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "WHEN_REQUIRED"

REMOTION_APP_DIR = pathlib.Path(__file__).parent.parent / "remotion-app"
BUNDLED_JS = REMOTION_APP_DIR / "bundled"

# ============================================================================
# Local Dependency Setup
# ============================================================================
def setup_local_environment():
    """Ensure npm dependencies are installed and pre-bundle the Remotion project."""
    logger.info("Checking local environment dependencies...")
    
    # 1. Check Node.js
    if not shutil.which("node") or not shutil.which("npm"):
        raise RuntimeError("Node.js and npm must be installed on the system to run Remotion rendering.")
        
    # 2. Check FFmpeg/FFprobe
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe must be installed on the system.")

    # 3. Install npm packages if node_modules is missing
    node_modules = REMOTION_APP_DIR / "node_modules"
    if not node_modules.exists():
        logger.info("node_modules not found. Running 'npm install' inside remotion-app...")
        subprocess.run(["npm", "install", "--legacy-peer-deps"], cwd=str(REMOTION_APP_DIR), check=True)

    # 4. Expect pre-bundled folder from local host (to prevent OOM on low-resource VM)
    if not BUNDLED_JS.exists():
        raise RuntimeError("Pre-compiled Remotion 'bundled' directory is missing. Please run npx remotion bundle on your host and sync it.")

# ============================================================================
# TTS Generation
# ============================================================================
async def generate_audio(text: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_path)

# ============================================================================
# Local Render Worker (runs slide render + loops via subprocess)
# ============================================================================
async def render_slide_local(slide_data: dict, slide_index: int, est_duration: float, temp_dir: str) -> Dict[str, Any]:
    """
    Renders a single slide locally by spawning npx remotion and ffmpeg as async subprocesses.
    Returns metrics and the output file path.
    """
    logger.info(f"Local Worker: Rendering slide {slide_index} | Est Duration: {est_duration:.1f}s")
    
    slide_data['durationInSeconds'] = est_duration
    props = {
        "slides": [slide_data],
        "audioUrls": []
    }
    
    # Paths for this specific worker run
    slide_temp_dir = os.path.join(temp_dir, f"slide_{slide_index}")
    os.makedirs(slide_temp_dir, exist_ok=True)
    
    props_path = os.path.join(slide_temp_dir, "props.json")
    with open(props_path, "w") as f:
        json.dump(props, f)
        
    rendered_mp4 = os.path.join(slide_temp_dir, "rendered.mp4")
    concated_mp4 = os.path.join(slide_temp_dir, "concated.mp4")
    static_frame = os.path.join(slide_temp_dir, "frame.png")
    
    # 1. Run Remotion render
    cmd = [
        "npx", "remotion", "render", 
        "bundled", "EducationalVideo", 
        rendered_mp4,
        "--props", props_path,
        "--frames=0-71",
        "--concurrency=2"
    ]
    
    remotion_start = time.perf_counter()
    remotion_proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(REMOTION_APP_DIR),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await remotion_proc.communicate()
    remotion_seconds = time.perf_counter() - remotion_start
    
    if remotion_proc.returncode != 0:
        raise RuntimeError(f"Remotion failed for slide {slide_index}: {stderr.decode()}")
        
    # 2. Extract static frame and loop it via FFmpeg
    ffmpeg_seconds = 0.0
    
    async def run_ffmpeg(args):
        nonlocal ffmpeg_seconds
        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        ffmpeg_seconds += time.perf_counter() - start
        if proc.returncode != 0:
            logger.error(f"FFmpeg failed with args: {' '.join(args)}")
            logger.error(f"FFmpeg stderr: {stderr.decode()}")
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

    # Extract last frame safely (frame index 71 of the 72 rendered frames)
    await run_ffmpeg([
        "-y", "-i", rendered_mp4,
        "-vf", "select='gte(n,71)'",
        "-vframes", "1",
        static_frame
    ])

    # Probe framerate and pixel format of rendered_mp4 to ensure exact compatibility during concat
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate,pix_fmt",
        "-of", "json",
        rendered_mp4
    ]
    probe_proc = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    probe_data = json.loads(probe_proc.stdout)
    stream = probe_data["streams"][0]

    fps_ratio = stream["r_frame_rate"]
    if "/" in fps_ratio:
        num, den = map(int, fps_ratio.split("/"))
        fps = str(round(num / den)) if den != 0 else "30"
    else:
        fps = fps_ratio
    pix_fmt = stream["pix_fmt"]
    loop_duration = max(est_duration - 3.0, 1.0)
    if loop_duration > 0.5:
        looped_mp4 = os.path.join(slide_temp_dir, "looped.mp4")
        # Match framerate and pixel format exactly with the source clip
        await run_ffmpeg([
            "-y", "-loop", "1", "-framerate", fps, "-i", static_frame,
            "-c:v", "libx264", "-preset", "ultrafast",
            "-t", str(loop_duration), "-pix_fmt", pix_fmt, "-crf", "35",
            looped_mp4
        ])
        
        # Use FFmpeg filter_complex concat to re-encode and merge the clips.
        # This completely avoids silent drops from timebase/metadata mismatches.
        await run_ffmpeg([
            "-y",
            "-i", rendered_mp4,
            "-i", looped_mp4,
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[outv]",
            "-map", "[outv]",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "32", "-movflags", "+faststart",
            concated_mp4
        ])
    else:
        shutil.copy(rendered_mp4, concated_mp4)
        
    return {
        "output_path": concated_mp4,
        "metrics": {
            "slide_index": slide_index,
            "remotion_seconds": round(remotion_seconds, 3),
            "ffmpeg_seconds": round(ffmpeg_seconds, 3),
            "total_seconds": round(remotion_seconds + ffmpeg_seconds, 3)
        }
    }

# ============================================================================
# Main Orchestrator Local Run
# ============================================================================
async def run_local_pipeline(prompt: str):
    logger.info("Initializing Azure VM Video Rendering Pipeline...")
    setup_local_environment()
    
    adapter = get_adapter()
    
    # Record job submission time and create DB record
    job_start_time = time.time()
    job_id = adapter.create_video(prompt)
    logger.info(f"Created video job with ID: {job_id}")
    
    # 1. Cold Start Time Calculation (instant local launch vs serverless queue delays)
    orchestrator_start_time = time.time()
    cold_start_time = max(orchestrator_start_time - job_start_time, 0.0)
    
    pipeline_stage = "llm_script_generation"
    from groq import Groq
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_prompt = """
    You are an educational video script writer. Based on the user's topic, generate a JSON array of exactly 6 slides.
    Use the following types: TitleSlide, AgendaSlide, SectionDividerSlide, ConceptExplanationSlide, ComparisonSlide, StepByStepProcessSlide, DataStatisticsSlide, ExampleCaseStudySlide, SummarySlide, QuestionDiscussionSlide.
    Each slide must have: 'type', 'title', 'content' (array of strings, or exactly 4 strings for ComparisonSlide), 'narration' (text to be spoken), and optionally 'latex' (a single string containing the math expression WITHOUT any $ delimiters) and 'icon' (lucide-react icon name like 'Brain').
    Respond ONLY with raw JSON, no markdown blocks.
    """
    
    logger.info("Calling Groq API for script generation...")
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-20b",
        temperature=0.7,
        max_tokens=4096,
    )
    
    try:
        raw_json = chat_completion.choices[0].message.content.strip()
        if raw_json.startswith("```json"):
            raw_json = raw_json[7:-3]
        slides = json.loads(raw_json)
        if not isinstance(slides, list) or len(slides) != 6:
            raise ValueError("LLM output must be a JSON array of exactly six slides")
    except Exception as e:
        adapter.update_video(video_id=job_id, status="failed", error_message=f"LLM script invalid: {str(e)}")
        raise e

    pipeline_stage = "script_persistence"
    for slide in slides:
        text = slide.get("narration", slide.get("title", ""))
        slide["durationInSeconds"] = max(len(text) * 0.07 + 2.0, 5.0)
    adapter.update_video(video_id=job_id, status="script_generated", slides_data=slides)

    # 2. Rendering Phase (Concurrent execution using local subprocesses)
    pipeline_stage = "rendering"
    rendering_start_time = time.time()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info("Spawning local Remotion renderers and TTS generators in parallel...")
        
        # Dispatch Slide rendering tasks with controlled concurrency to prevent VM OOM crashes
        concurrency_limit = int(os.getenv("VM_RENDER_CONCURRENCY", "2"))
        logger.info(f"Setting local render concurrency limit to: {concurrency_limit}")
        sem = asyncio.Semaphore(concurrency_limit)

        async def render_with_sem(slide_data, idx, duration, path):
            async with sem:
                return await render_slide_local(slide_data, idx, duration, path)

        render_tasks = []
        for i, slide in enumerate(slides):
            render_tasks.append(
                render_with_sem(slide, i, slide["durationInSeconds"], temp_dir)
            )
            
        # Dispatch TTS audio generation tasks
        tts_dir = os.path.join(temp_dir, "tts")
        os.makedirs(tts_dir, exist_ok=True)
        tts_tasks = []
        audio_paths = []
        for i, slide in enumerate(slides):
            text = slide.get("narration", slide.get("title", ""))
            audio_path = os.path.join(tts_dir, f"audio_{i}.mp3")
            audio_paths.append(audio_path)
            tts_tasks.append(generate_audio(text, audio_path))
            
        # Run everything
        logger.info("Executing render & TTS loops...")
        render_results, _ = await asyncio.gather(
            asyncio.gather(*render_tasks),
            asyncio.gather(*tts_tasks)
        )
        
        # Read the generated audios
        audio_bytes_list = []
        for path in audio_paths:
            with open(path, "rb") as audio_file:
                audio_bytes_list.append(audio_file.read())
                
        # 3. Audio/Video Merging (FFmpeg concatenation)
        pipeline_stage = "audio_merge"
        logger.info("Merging audio tracks and concatenating video slides...")
        
        merge_ffmpeg_seconds = 0.0
        
        async def run_merge_ffmpeg(args):
            nonlocal merge_ffmpeg_seconds
            start = time.perf_counter()
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            merge_ffmpeg_seconds += time.perf_counter() - start
            if proc.returncode != 0:
                logger.error(f"Merge FFmpeg failed: {' '.join(args)}")
                logger.error(f"Merge FFmpeg stderr: {stderr.decode()}")
                raise RuntimeError(f"Merge FFmpeg failed: {stderr.decode()}")

        merged_slides = []
        for i in range(len(slides)):
            slide_video_path = render_results[i]["output_path"]
            audio_mp3 = os.path.join(temp_dir, f"audio_{i}.mp3")
            final_mp4 = os.path.join(temp_dir, f"merged_{i}.mp4")
            
            with open(audio_mp3, "wb") as f:
                f.write(audio_bytes_list[i])
                
            await run_merge_ffmpeg([
                "-y", "-i", slide_video_path, "-i", audio_mp3,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-threads", "1", "-shortest", final_mp4
            ])
            merged_slides.append(final_mp4)

        list_file_path = os.path.join(temp_dir, "list.txt")
        with open(list_file_path, "w") as list_file:
            for path in merged_slides:
                list_file.write(f"file '{path}'\n")
                
        final_output = os.path.join(temp_dir, "final_output.mp4")
        await run_merge_ffmpeg([
            "-y", "-f", "concat", "-safe", "0", "-i", list_file_path,
            "-c", "copy", final_output
        ])
        
        # Calculate video duration via ffprobe
        duration_probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", final_output],
            check=True,
            capture_output=True,
            text=True,
        )
        video_length = float(duration_probe.stdout.strip())
        
        # Record wall-clock render duration
        rendering_time = time.time() - rendering_start_time
        
        # 4. Upload final video to object storage
        pipeline_stage = "video_upload"
        logger.info("Uploading final video to OCI Object Storage...")
        final_url = adapter.upload_video(final_output, job_id)
        
    # ============================================================================
    # Resource Usage Profiling
    # ============================================================================
    # Measure resources of the VM environment
    parent_usage = resource.getrusage(resource.RUSAGE_SELF)
    children_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    
    # Calculate child process metric sums
    worker_metrics = [res["metrics"] for res in render_results]
    remotion_seconds = sum(m["remotion_seconds"] for m in worker_metrics)
    worker_ffmpeg_seconds = sum(m["ffmpeg_seconds"] for m in worker_metrics)
    
    resources_used = {
        "environment": "Azure VM (Local Subprocesses)",
        "orchestrator_parent": {
            "cpu_seconds": round(parent_usage.ru_utime + parent_usage.ru_stime, 3),
            "max_ram_mb": round(parent_usage.ru_maxrss / 1024.0, 2),  # ru_maxrss is KB on Linux
            "cpu_count": os.cpu_count() or 1
        },
        "subprocess_children": {
            "cpu_seconds": round(children_usage.ru_utime + children_usage.ru_stime, 3),
            "max_ram_mb": round(children_usage.ru_maxrss / 1024.0, 2),
            "remotion_compute_seconds": round(remotion_seconds, 3),
            "worker_ffmpeg_seconds": round(worker_ffmpeg_seconds, 3),
            "merge_ffmpeg_seconds": round(merge_ffmpeg_seconds, 3)
        },
        "rendering_breakdown_seconds": {
            "total_compute_seconds": round(remotion_seconds + worker_ffmpeg_seconds + merge_ffmpeg_seconds, 3),
            "wall_clock_rendering_seconds": round(rendering_time, 3)
        },
        "render_workers_detail": worker_metrics
    }
    
    # Finalize state, writing metrics to DB
    pipeline_stage = "completion_persistence"
    adapter.update_video(
        video_id=job_id,
        status="completed",
        video_storage_url=final_url,
        cold_start_time=round(cold_start_time, 3),
        rendering_time=round(rendering_time, 3),
        video_length=round(video_length, 3),
        resources_used=resources_used
    )
    
    logger.info(f"Local job {job_id} completed successfully!")
    logger.info(f"Final Video URL: {final_url}")
    logger.info(f"Total Wall-Clock Rendering Duration: {rendering_time:.2f}s")
    return job_id

# ============================================================================
# CLI Entrypoint
# ============================================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vm_app.py '<prompt>'")
        sys.exit(1)
        
    prompt_input = sys.argv[1]
    
    # Run the main async loop
    asyncio.run(run_local_pipeline(prompt_input))
