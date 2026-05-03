import modal
import os
import subprocess
import json
import asyncio
from pathlib import Path

app = modal.App("remotion-render-job")

remotion_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "ffmpeg",
        "libnss3",
        "libatk1.0-0",
        "libatk-bridge2.0-0",
        "libcups2",
        "libdrm2",
        "libxkbcommon0",
        "libxcomposite1",
        "libxdamage1",
        "libxfixes3",
        "libxrandr2",
        "libgbm1",
        "libasound2",
        "libpango-1.0-0",
        "libcairo2",
        "curl",
        "ca-certificates"
    )
    .run_commands(
        "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
        "apt-get install -y nodejs"
    )
    .pip_install("edge-tts", "firebase-admin", "requests", "fastapi[standard]", "azure-cognitiveservices-speech")
    .add_local_dir("./remotion-templates", remote_path="/app", copy=True)
    .run_commands(
        "cd /app && npm install",
        "cd /app && CI=true node node_modules/@remotion/cli/remotion-cli.js bundle src/index.ts --out-dir=bundled --log=error"
    )
)

def get_audio_duration(file_path):
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ], capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 5.0 # Fallback 5s

@app.function(
    image=remotion_image,
    cpu=2.0, # High CPU for fast Remotion burst
    memory=1280,
    timeout=300
)
def render_slide_worker(job_id: str, slide_index: int, slide_data: dict, video_title: str, est_duration: float, theme_id: str = "minimal_dark", bg_folder: str = "dark_blue") -> tuple[bytes, float]:
    """Renders 90-frame intro, loops last frame to estimated duration, concats via demuxer.
    Audio merge is handled by the orchestrator (trivial stream copy)."""
    import time
    start_time = time.time()
    import shutil
    import tempfile
    
    print(f"🛠️ [WORKER] Rendering Slide {slide_index} | Est Duration: {est_duration:.1f}s")
    
    work_dir = Path("/app")
    out_dir = Path(tempfile.mkdtemp())
    
    # 1. Setup Props
    props_path = out_dir / "content.json"
    payload = {
        "title": video_title, 
        "theme_id": theme_id,
        "bg_folder": bg_folder,
        "slides": [slide_data],
        "targetSlideIndex": 0,
        "slideDurations": [90]
    }
    with open(props_path, "w") as f:
        json.dump(payload, f)
        
    # 2. Remotion Render (90 frames = 3 seconds)
    rendered_mp4 = out_dir / "rendered.mp4"
    base_cmd = [
        "node", "node_modules/@remotion/cli/remotion-cli.js",
        "render", "bundled", "EducationalVideo"
    ]
    base_props = [f"--props={props_path}", "--concurrency=2", "--crf=30", "--log=info"]
    
    subprocess.run(
        base_cmd + [str(rendered_mp4)] + base_props + ["--frames=0-89"],
        cwd=str(work_dir), check=True
    )
    
    # 3. Extract the very last frame
    static_frame = out_dir / "frame.png"
    subprocess.run([
        "ffmpeg", "-y", "-sseof", "-0.1", "-i", str(rendered_mp4),
        "-update", "1", "-q:v", "2", str(static_frame)
    ], check=True, capture_output=True)
    
    concated_mp4 = out_dir / "concated.mp4"
    loop_duration = max(est_duration - 3.0, 1.0)  # subtract intro, minimum 1s
    
    if loop_duration > 0.5:
        # 4. Loop frame to estimated duration (NOT 30s)
        #    Match Remotion's yuvj420p output for seamless concat demuxer copy
        looped_mp4 = out_dir / "looped.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(static_frame),
            "-c:v", "libx264", "-preset", "ultrafast",
            "-t", str(loop_duration), "-pix_fmt", "yuvj420p", "-crf", "35",
            str(looped_mp4)
        ], check=True, capture_output=True)
        
        # 5. Concat demuxer with -c copy (ZERO re-encoding, ~0.2s instead of 12s)
        concat_list = out_dir / "concat_list.txt"
        with open(concat_list, "w") as f:
            f.write(f"file '{rendered_mp4}'\n")
            f.write(f"file '{looped_mp4}'\n")
        
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c", "copy", "-movflags", "+faststart", str(concated_mp4)
        ], check=True, capture_output=True)
    else:
        # Very short slide, just use the intro
        shutil.copy(rendered_mp4, concated_mp4)
    
    with open(concated_mp4, "rb") as f:
        vid_bytes = f.read()
        
    shutil.rmtree(out_dir, ignore_errors=True)
    worker_time = time.time() - start_time
    print(f"✅ [WORKER] Slide {slide_index} done in {worker_time:.2f}s. Silent MP4: {len(vid_bytes)//1024}KB")
    return (vid_bytes, worker_time)


@app.function(
    image=remotion_image,
    cpu=1.0,
    memory=1024,
    timeout=600,
    secrets=[modal.Secret.from_name("remotion-secrets")]
)
def orchestrator_job(job_id: str, script_json: dict):
    import edge_tts
    import azure.cognitiveservices.speech as speechsdk
    import firebase_admin
    from firebase_admin import credentials, firestore
    import requests
    import os
    import tempfile
    import shutil
    from concurrent.futures import ThreadPoolExecutor
    import time
    
    orchestrator_start_time = time.time()
    print(f"🚀 [ORCHESTRATOR] Starting job: {job_id}")

    # Initialize Firebase
    if not firebase_admin._apps:
        creds_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "").strip()
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"❌ [ORCHESTRATOR] Firebase error: {str(e)}")
                raise e
            
    db = firestore.client() if firebase_admin._apps else None
    
    try:
        if db:
            db.collection("render_jobs").document(job_id).update({"status": "rendering"})
        
        # Defensive: if script_json arrives as a list (LLM returned raw slides array),
        # wrap it in a proper dict structure
        if isinstance(script_json, list):
            print("⚠️ [ORCHESTRATOR] script_json is a list, wrapping in dict...")
            script_json = {"title": "Educational Video", "slides": script_json}
        
        slides = [s for s in script_json.get("slides", []) if isinstance(s, dict)]
        title = script_json.get("title", "Educational Video")
        if not slides:
            raise ValueError("No valid slides found in script_json")
        
        # ── TTS helpers ──
        async def generate_edge_tts(text: str) -> bytes:
            communicate = edge_tts.Communicate(text, "en-GB-AdaMultilingualNeural")
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
            
        def generate_azure_tts(text: str) -> bytes:
            speech_key = os.environ.get("AZURE_SPEECH_KEY")
            service_region = os.environ.get("AZURE_SPEECH_REGION")
            if not speech_key or not service_region:
                raise Exception("Azure credentials missing")
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
            speech_config.speech_synthesis_voice_name = "en-GB-AdaMultilingualNeural"
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            result = speech_synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                raise Exception(f"Azure TTS Failed: {result.reason}")

        # Check Firebase Usage Quota
        azure_quota_exceeded = False
        chars_to_add = sum([len(s.get("spoken_text", s.get("narration", ""))) for s in slides if isinstance(s, dict)])
        if db:
            try:
                usage_ref = db.collection("usage").document("tts")
                usage_doc = usage_ref.get()
                current_usage = usage_doc.to_dict().get("current_month_chars", 0) if usage_doc.exists else 0
                if current_usage + chars_to_add > 450000:
                    azure_quota_exceeded = True
                    print("⚠️ Azure limits exceeded. Falling back to Edge TTS.")
                else:
                    # Increment optimistically
                    usage_ref.set({"current_month_chars": current_usage + chars_to_add}, merge=True)
            except:
                pass
                
        async def process_single_audio(idx, slide):
            text = slide.get("spoken_text") or slide.get("narration") or slide.get("slide_text", "")
            if not text:
                return (None, 5.0)
            try:
                audio_bytes = None
                if not azure_quota_exceeded:
                    try:
                        audio_bytes = await asyncio.to_thread(generate_azure_tts, text)
                    except Exception as e:
                        print(f"Azure failed, fallback to Edge: {e}")
                        audio_bytes = await generate_edge_tts(text)
                else:
                    audio_bytes = await generate_edge_tts(text)
                    
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                    tf.write(audio_bytes)
                    tf_path = tf.name
                duration = get_audio_duration(tf_path) + 0.5 # 0.5s padding
                os.unlink(tf_path)
                return (audio_bytes, duration)
            except Exception as e:
                print(f"Failed TTS slide {idx}: {e}")
                return (None, 5.0)

        async def process_all_audio():
            tasks = [process_single_audio(idx, slide) for idx, slide in enumerate(slides)]
            return await asyncio.gather(*tasks)

        # ════════════════════════════════════════════════════════
        # PHASE 1: Spawn workers + TTS IN PARALLEL (the big win)
        # ════════════════════════════════════════════════════════
        
        # 1a. Spawn workers with estimated duration (from text length)
        #     Workers don't need exact audio duration — just a close estimate
        #     English TTS: ~14 chars/sec → 0.07 sec/char, +2s safety padding
        print("⚡ Fanning out Render Workers + TTS in parallel...")
        theme_id = script_json.get("theme_id", "minimal_dark")
        bg_folder = script_json.get("bg_folder", "dark_blue")
        print(f"🎨 Theme: {theme_id} | BG: {bg_folder}")
        
        worker_calls = []
        for idx, slide in enumerate(slides):
            text = slide.get("spoken_text") or slide.get("narration") or slide.get("slide_text", "")
            est_duration = max(len(text) * 0.07 + 2.0, 5.0)  # minimum 5s per slide
            worker_calls.append(render_slide_worker.spawn(job_id, idx, slide, title, est_duration, theme_id, bg_folder))
        
        # 1b. Generate TTS concurrently while workers render
        #     Using a thread so we can call asyncio.run without blocking worker.get()
        tts_result_holder = [None]
        def run_tts():
            print("🎙️ Generating TTS (parallel with rendering)...")
            tts_result_holder[0] = asyncio.run(process_all_audio())
            print(f"🎙️ TTS done! Got {len(tts_result_holder[0])} audio tracks.")
        
        tts_thread = ThreadPoolExecutor(max_workers=1)
        tts_future = tts_thread.submit(run_tts)
        
        # 1c. Collect worker results (blocks until all workers finish)
        #     Workers now return silent MP4 bytes and execution time
        silent_videos = []
        worker_times = []
        for idx, call in enumerate(worker_calls):
            vid_bytes, w_time = call.get()
            silent_videos.append(vid_bytes)
            worker_times.append(w_time)
        print(f"📦 All {len(silent_videos)} workers returned.")
            
        # 1d. Ensure TTS is also done
        tts_future.result()  # blocks until TTS thread completes
        audio_results = tts_result_holder[0]
        tts_thread.shutdown(wait=False)
        
        # ════════════════════════════════════════════════════════
        # PHASE 2: Lightweight audio merge (async, all concurrent)
        #   Workers already did the heavy video encoding.
        #   Orchestrator only does: normalize audio + merge with -c:v copy
        # ════════════════════════════════════════════════════════
        print("🔧 Merging audio into slides...")
        work_dir = Path("/app")
        slide_dirs = []
        
        async def merge_audio_for_slide(idx, silent_mp4_bytes, audio_bytes):
            """Merge TTS audio into the silent video. Uses -c:v copy (no re-encoding).
            Returns path to the final MP4."""
            slide_dir = Path(tempfile.mkdtemp())
            slide_dirs.append(slide_dir)
            
            silent_path = slide_dir / "silent.mp4"
            final_path = slide_dir / "final.mp4"
            
            with open(silent_path, "wb") as f:
                f.write(silent_mp4_bytes)
            
            if audio_bytes:
                audio_raw = slide_dir / "audio_raw"
                audio_norm = slide_dir / "audio.mp3"
                with open(audio_raw, "wb") as f:
                    f.write(audio_bytes)
                
                # Normalize audio format
                proc = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-y", "-i", str(audio_raw),
                    "-c:a", "libmp3lame", "-threads", "1", "-q:a", "4", str(audio_norm),
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
                )
                await proc.wait()
                
                # Merge: video is stream-copied, only audio is encoded (trivial)
                proc = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-y", "-i", str(silent_path), "-i", str(audio_norm),
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-threads", "1", "-shortest",
                    str(final_path),
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
                )
                await proc.wait()
            else:
                shutil.copy(silent_path, final_path)
            
            print(f"  ✅ Slide {idx} audio merged.")
            return final_path
        
        async def merge_all_audio():
            tasks = [
                merge_audio_for_slide(idx, silent_videos[idx], audio_results[idx][0])
                for idx in range(len(slides))
            ]
            return await asyncio.gather(*tasks)
        
        slide_finals = asyncio.run(merge_all_audio())
        
        # ════════════════════════════════════════════════════════
        # PHASE 3: Stitch all slides + Upload
        # ════════════════════════════════════════════════════════
        print("🔗 Stitching parallel outputs...")
        concat_txt = work_dir / "master_concat.txt"
        final_mp4 = work_dir / "master_final.mp4"
        
        with open(concat_txt, "w") as f:
            for idx, slide_path in enumerate(slide_finals):
                chunk_path = work_dir / f"chunk_{idx}.mp4"
                shutil.copy(slide_path, chunk_path)
                f.write(f"file '{chunk_path.name}'\n")
                
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-c:v", "copy", "-c:a", "aac", "-threads", "1", str(final_mp4)
        ], check=True)
        
        # Upload to Blob
        print("☁️ Uploading to Blob storage...")
        vercel_blob_token = os.environ.get("BLOB_READ_WRITE_TOKEN")
        if not vercel_blob_token:
            raise ValueError("BLOB_READ_WRITE_TOKEN is missing")

        upload_url = f"https://blob.vercel-storage.com/{job_id}.mp4"
        headers = {
            "Authorization": f"Bearer {vercel_blob_token}",
        }
        with open(final_mp4, "rb") as f:
            resp = requests.put(upload_url, headers=headers, data=f)
            resp.raise_for_status()
            
        download_url = resp.json().get("url")
        
        # Cleanup temp dirs
        for d in slide_dirs:
            shutil.rmtree(d, ignore_errors=True)
        for idx in range(len(slides)):
            (work_dir / f"chunk_{idx}.mp4").unlink(missing_ok=True)
        concat_txt.unlink(missing_ok=True)
        final_mp4.unlink(missing_ok=True)
        
        # Update Firebase
        orchestrator_time = time.time() - orchestrator_start_time
        num_workers = len(slides)
        total_ram_mb = (num_workers * 1280) + 1024
        total_cores = (num_workers * 2.0) + 1.0

        print(f"✅ Success! URL: {download_url}")
        if db:
            db.collection("render_jobs").document(job_id).update({
                "status": "done",
                "video_url": download_url,
                "analytics": {
                    "total_ram_mb": total_ram_mb,
                    "total_cores": total_cores,
                    "worker_times": worker_times,
                    "orchestrator_time": orchestrator_time,
                    "total_time_seconds": orchestrator_time
                }
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        if db:
            db.collection("render_jobs").document(job_id).update({"status": "failed"})
        raise e

@app.function(image=remotion_image)
@modal.fastapi_endpoint(method="POST")
def trigger_render(data: dict):
    job_id = data.get("job_id")
    script_json = data.get("script_json")
    
    if not job_id or not script_json:
        return {"error": "Missing job_id or script_json"}
        
    print(f"Webhook triggered! Spawning Orchestrator for job: {job_id}")
    orchestrator_job.spawn(job_id, script_json)
    return {"status": "started", "job_id": job_id}
