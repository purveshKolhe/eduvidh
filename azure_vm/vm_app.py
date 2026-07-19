import asyncio
import json
import logging
import os
import pathlib
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import modal
import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

from db_and_storage.adapter import get_adapter


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("azure_vm_pipeline")

dotenv_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "WHEN_REQUIRED"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "WHEN_REQUIRED"

# The public product contract is at most eight slides: two local and six remote.
VM_CAPACITY = 2
MAX_SLIDES = 8
MAX_MODAL_WORKERS = MAX_SLIDES - VM_CAPACITY
TARGET_FPS = 24
ANIMATION_DURATION_SECONDS = 3.0
MODAL_SCALEDOWN_WINDOW_SECONDS = 2
LOCAL_RENDERER_URL = os.getenv("LOCAL_RENDERER_URL", "http://127.0.0.1:5000")
MODAL_APP_NAME = os.getenv("MODAL_APP_NAME", "edu-video-generator")
MODAL_RENDER_FUNCTION = os.getenv("MODAL_RENDER_FUNCTION", "render_slide_worker")
FEATURE_FLAG_HYBRID = os.getenv("FEATURE_FLAG_HYBRID", "true").lower() == "true"


# Modal autoscaler settings are shared by every job served by this VM process.
# Track reservations so one completed job cannot scale down capacity still needed by another.
_modal_pool_lock = asyncio.Lock()
_modal_reservations: Dict[str, int] = {}


def _render_function() -> modal.Function:
    return modal.Function.from_name(MODAL_APP_NAME, MODAL_RENDER_FUNCTION)


async def _apply_modal_pool_target() -> int:
    """Apply the total active reservation, capped by the product's six-worker budget."""
    target = min(MAX_MODAL_WORKERS, sum(_modal_reservations.values()))
    render_function = _render_function()
    await asyncio.to_thread(
        render_function.update_autoscaler,
        min_containers=target,
        max_containers=MAX_MODAL_WORKERS,
        buffer_containers=0,
        scaledown_window=MODAL_SCALEDOWN_WINDOW_SECONDS,
    )
    logger.info("Modal render pool target is now %s container(s)", target)
    return target


async def set_modal_reservation(job_id: str, container_count: int) -> int:
    """Reserve remote-worker capacity for one job and update the shared pool safely."""
    if not 0 <= container_count <= MAX_MODAL_WORKERS:
        raise ValueError(f"invalid Modal worker reservation: {container_count}")

    async with _modal_pool_lock:
        if container_count:
            _modal_reservations[job_id] = container_count
        else:
            _modal_reservations.pop(job_id, None)
        return await _apply_modal_pool_target()


async def generate_audio(text: str, output_path: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_path)


async def generate_audio_timed(text: str, slide_index: int, output_path: str) -> Dict[str, Any]:
    started_at = time.perf_counter()
    await generate_audio(text, output_path)
    return {
        "slide_index": slide_index,
        "seconds": round(time.perf_counter() - started_at, 3),
    }


async def render_slide_local_service(
    slide_data: dict, slide_index: int, output_path: str
) -> Dict[str, Any]:
    """Render the three-second animated clip on one of two persistent local tabs."""
    started_at = time.perf_counter()
    payload = {
        "slide_data": slide_data,
        "slide_index": slide_index,
        "output_path": output_path,
    }
    timeout = aiohttp.ClientTimeout(total=180)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(f"{LOCAL_RENDERER_URL}/render", json=payload) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"local renderer failed for slide {slide_index}: {await response.text()}"
                )
            result = await response.json()

    metrics = dict(result.get("metrics", {}))
    metrics.update(
        {
            "slide_index": slide_index,
            "request_seconds": round(time.perf_counter() - started_at, 3),
        }
    )
    return {"output_path": result["output_path"], "metrics": metrics}


async def warm_modal_pool(job_id: str) -> Dict[str, Any]:
    """
    Start and verify six *actual* Modal render workers. A warm request performs a
    one-frame Remotion render in the worker, so readiness means more than merely
    importing Python or returning from a dummy function.
    """
    started_at = time.perf_counter()
    await set_modal_reservation(job_id, MAX_MODAL_WORKERS)
    render_function = _render_function()

    # A sequence of `spawn()` calls can be greedily routed to the first worker
    # that becomes ready. `map()` submits one batch of six concurrent inputs,
    # which is the Modal API intended for parallel batch execution. Together
    # with the six-container floor above, this forces the pool to materialize.
    responses = [
        response
        async for response in render_function.map.aio(
            [None] * MAX_MODAL_WORKERS,
            [-1] * MAX_MODAL_WORKERS,
            [0.0] * MAX_MODAL_WORKERS,
            order_outputs=False,
        )
    ]
    worker_ids = {
        str(response.get("worker_id", ""))
        for response in responses
        if response.get("worker_id")
    }
    if len(worker_ids) != MAX_MODAL_WORKERS:
        raise RuntimeError(
            "Modal warm-up did not reach six distinct render workers "
            f"(received {len(worker_ids)})"
        )

    return {
        "requested_count": MAX_MODAL_WORKERS,
        "ready_count": len(worker_ids),
        "worker_ids": sorted(worker_ids),
        "seconds": round(time.perf_counter() - started_at, 3),
    }


async def run_ffmpeg(args: List[str]) -> None:
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        *args,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode(errors='replace')}")


async def probe_duration(path: str) -> float:
    process = await asyncio.create_subprocess_exec(
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {stderr.decode(errors='replace')}")
    return float(stdout.decode().strip())


async def assemble_video_once(
    animation_paths: List[str], audio_paths: List[str], final_output: str
) -> Tuple[List[float], float]:
    """
    Freeze each three-second animation at its last frame for the real narration
    length, then concatenate all audio/video pairs in one FFmpeg invocation.
    """
    if len(animation_paths) != len(audio_paths) or not animation_paths:
        raise ValueError("animation and audio inputs must be non-empty and equally sized")

    audio_durations = await asyncio.gather(*(probe_duration(path) for path in audio_paths))
    slide_durations = [max(ANIMATION_DURATION_SECONDS, duration) for duration in audio_durations]
    slide_count = len(animation_paths)

    command: List[str] = ["-y"]
    for path in animation_paths:
        command.extend(["-i", path])
    for path in audio_paths:
        command.extend(["-i", path])

    filters: List[str] = []
    concat_inputs: List[str] = []
    for index, duration in enumerate(slide_durations):
        freeze_seconds = max(0.0, duration - ANIMATION_DURATION_SECONDS)
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
            str(TARGET_FPS),
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


async def generate_script(prompt: str) -> List[dict]:
    from groq import AsyncGroq

    system_prompt = """
    You are an educational video script writer. Based on the user's topic, generate a JSON array of between 5 and 8 slides.
    Use the following types: TitleSlide, AgendaSlide, SectionDividerSlide, ConceptExplanationSlide, ComparisonSlide, StepByStepProcessSlide, DataStatisticsSlide, ExampleCaseStudySlide, SummarySlide, QuestionDiscussionSlide.
    Each slide must have: 'type', 'title', 'content' (array of strings, or exactly 4 strings for ComparisonSlide), 'narration' (text to be spoken), and optionally 'latex' (a single string containing the math expression WITHOUT any $ delimiters) and 'icon' (lucide-react icon name like 'Brain').
    Respond ONLY with raw JSON, no markdown blocks.
    """
    client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
    completion = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        model="openai/gpt-oss-20b",
        temperature=0.7,
        max_tokens=4096,
    )
    raw_json = completion.choices[0].message.content.strip()
    if raw_json.startswith("```json"):
        raw_json = raw_json[7:-3]
    slides = json.loads(raw_json)
    if not isinstance(slides, list) or not 5 <= len(slides) <= MAX_SLIDES:
        raise ValueError(f"LLM output must contain 5 to {MAX_SLIDES} slides")
    if not all(isinstance(slide, dict) for slide in slides):
        raise ValueError("every slide must be a JSON object")
    return slides


async def orchestrate_hybrid_job(job_id: str, prompt: str) -> None:
    """Run one hybrid job with six verified remote workers and two local tabs."""
    adapter = get_adapter()
    orchestrator_started_at = time.perf_counter()
    temp_dir: Optional[str] = None
    warm_task: Optional[asyncio.Task] = None
    request_to_orchestrator = 0.0

    try:
        video_data = adapter.get_video(job_id)
        created_at = video_data.get("created_at") if video_data else None
        if created_at:
            created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            request_to_orchestrator = max(time.time() - created_at_dt.timestamp(), 0.0)

        if not FEATURE_FLAG_HYBRID:
            fallback = modal.Function.from_name(MODAL_APP_NAME, "orchestrate_job")
            await fallback.spawn.aio(job_id, prompt)
            return

        # This task gets CPU time as soon as generate_script awaits Groq. The old
        # synchronous Groq request prevented the warm-up from starting at all.
        warm_task = asyncio.create_task(warm_modal_pool(job_id))

        script_started_at = time.perf_counter()
        slides = await generate_script(prompt)
        script_seconds = time.perf_counter() - script_started_at

        for slide in slides:
            text = slide.get("narration", slide.get("title", ""))
            # Only a provisional value for UI/legacy consumers. Final media uses
            # probed TTS duration, never this character-count estimate.
            slide["durationInSeconds"] = max(len(text) * 0.07 + 2.0, ANIMATION_DURATION_SECONDS)

        adapter.update_video(video_id=job_id, status="script_generated", slides_data=slides)

        # Do not dispatch a render until six actual workers have completed their
        # renderer warm-up. If this is slower than Groq, this is the only wait.
        warm_metrics = await warm_task

        total_slides = len(slides)
        local_count = min(total_slides, VM_CAPACITY)
        remote_count = total_slides - local_count
        await set_modal_reservation(job_id, remote_count)

        adapter.update_video(video_id=job_id, status="rendering", slides_data=slides)
        temp_dir = tempfile.mkdtemp(prefix=f"eduvidh_{job_id}_")
        animation_paths = [os.path.join(temp_dir, f"animation_{index}.mp4") for index in range(total_slides)]
        audio_paths = [os.path.join(temp_dir, f"audio_{index}.mp3") for index in range(total_slides)]

        modal_worker = _render_function()

        async def render_remote(slide: dict, index: int, output_path: str) -> Dict[str, Any]:
            started_at = time.perf_counter()
            result = await modal_worker.remote.aio(slide, index, ANIMATION_DURATION_SECONDS)
            await asyncio.to_thread(pathlib.Path(output_path).write_bytes, result["video_bytes"])
            metrics = dict(result.get("metrics", {}))
            metrics.update(
                {
                    "slide_index": index,
                    "request_seconds": round(time.perf_counter() - started_at, 3),
                }
            )
            return {"output_path": output_path, "metrics": metrics}

        local_jobs = [
            render_slide_local_service(slides[index], index, animation_paths[index])
            for index in range(local_count)
        ]
        remote_jobs = [
            render_remote(slides[index], index, animation_paths[index])
            for index in range(local_count, total_slides)
        ]
        tts_jobs = [
            generate_audio_timed(
                slides[index].get("narration", slides[index].get("title", "")),
                index,
                audio_paths[index],
            )
            for index in range(total_slides)
        ]

        parallel_started_at = time.perf_counter()
        local_render_task = asyncio.ensure_future(asyncio.gather(*local_jobs))
        remote_render_task = asyncio.ensure_future(asyncio.gather(*remote_jobs))
        tts_task = asyncio.ensure_future(asyncio.gather(*tts_jobs))

        # Release Modal capacity as soon as the video clips are rendered. TTS,
        # assembly, and upload do not need those containers, so holding them
        # through those stages would spend credits for no latency benefit.
        local_results, remote_results = await asyncio.gather(local_render_task, remote_render_task)
        await set_modal_reservation(job_id, 0)
        tts_metrics = await tts_task
        parallel_seconds = time.perf_counter() - parallel_started_at

        final_output = os.path.join(temp_dir, "final_output.mp4")
        slide_durations, assembly_seconds = await assemble_video_once(
            animation_paths, audio_paths, final_output
        )
        video_length = await probe_duration(final_output)
        upload_started_at = time.perf_counter()
        final_url = await asyncio.to_thread(adapter.upload_video, final_output, job_id)
        upload_seconds = time.perf_counter() - upload_started_at

        local_metrics = [result["metrics"] for result in local_results]
        remote_metrics = [result["metrics"] for result in remote_results]
        local_render_seconds = max((metric["request_seconds"] for metric in local_metrics), default=0.0)
        remote_render_seconds = max((metric["request_seconds"] for metric in remote_metrics), default=0.0)
        tts_seconds = max((metric["seconds"] for metric in tts_metrics), default=0.0)
        parent_usage = resource.getrusage(resource.RUSAGE_SELF)

        resources_used = {
            "environment": "Azure VM + Modal Hybrid Orchestrator",
            "allocation_counts": {
                "total_slides": total_slides,
                "local_vm_count": local_count,
                "remote_modal_count": remote_count,
            },
            "modal_warm_pool": warm_metrics,
            "timings_wall_clock_seconds": {
                "request_to_orchestrator": round(request_to_orchestrator, 3),
                "script_generation": round(script_seconds, 3),
                "local_render": round(local_render_seconds, 3),
                "remote_render": round(remote_render_seconds, 3),
                "tts_generation": round(tts_seconds, 3),
                "parallel_render_and_tts": round(parallel_seconds, 3),
                "single_pass_assembly": round(assembly_seconds, 3),
                "upload": round(upload_seconds, 3),
                "total_wall_clock": round(time.perf_counter() - orchestrator_started_at, 3),
            },
            "slide_durations_seconds": [round(duration, 3) for duration in slide_durations],
            "local_renderer": {
                "peak_orchestrator_rss_mb": round(parent_usage.ru_maxrss / 1024.0, 2),
                "detail": local_metrics,
            },
            "modal_workers": {"detail": remote_metrics},
            "tts": {"detail": tts_metrics},
        }

        adapter.update_video(
            video_id=job_id,
            status="completed",
            video_storage_url=final_url,
            cold_start_time=round(request_to_orchestrator, 3),
            rendering_time=round(parallel_seconds, 3),
            video_length=round(video_length, 3),
            resources_used=resources_used,
        )
        logger.info("Hybrid job %s completed in %.2fs", job_id, time.perf_counter() - orchestrator_started_at)
    except Exception as error:
        logger.exception("Hybrid job %s failed", job_id)
        adapter.update_video(
            video_id=job_id,
            status="failed",
            error_message=str(error),
            cold_start_time=round(request_to_orchestrator, 3),
            resources_used={"failed": True, "error": str(error)},
        )
    finally:
        if warm_task and not warm_task.done():
            warm_task.cancel()
            await asyncio.gather(warm_task, return_exceptions=True)
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        try:
            await set_modal_reservation(job_id, 0)
        except Exception:
            logger.exception("Could not release Modal reservation for job %s", job_id)


app = FastAPI(title="Azure VM Orchestration Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if origin],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


@app.post("/")
async def start_generation_endpoint(payload: dict, background_tasks: BackgroundTasks) -> Dict[str, str]:
    prompt = str(payload.get("prompt", "")).strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")
    job_id = get_adapter().create_video(prompt)
    background_tasks.add_task(orchestrate_hybrid_job, job_id, prompt)
    return {"job_id": job_id, "status": "pending"}


@app.get("/status/{job_id}")
async def get_generation_status(job_id: str) -> Dict[str, Any]:
    video_data = get_adapter().get_video(job_id)
    if not video_data:
        raise HTTPException(status_code=404, detail="Job not found")
    return video_data


if __name__ == "__main__":
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        cli_prompt = sys.argv[1]
        cli_job_id = get_adapter().create_video(cli_prompt)
        asyncio.run(orchestrate_hybrid_job(cli_job_id, cli_prompt))
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
