import modal
import os
import json
import asyncio
import tempfile
import subprocess
import shutil
from supabase import create_client, Client
from groq import AsyncGroq
import edge_tts

# Modal App Definition
app = modal.App("edu-video-generator")

# Image for Orchestrator
orchestrator_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("supabase", "groq", "edge-tts", "aiohttp", "ffmpeg-python", "fastapi[standard]")
    .apt_install("ffmpeg")
)

# Image for Render Worker (needs Node.js and Remotion)
render_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "git", "ffmpeg", "libnss3", "libnspr4", "libatk1.0-0", "libatk-bridge2.0-0", "libcups2", "libdrm2", "libxkbcommon0", "libxcomposite1", "libxdamage1", "libxfixes3", "libxrandr2", "libgbm1", "libasound2", "libpango-1.0-0", "libcairo2")
    .run_commands(
        "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
        "apt-get install -y nodejs",
    )
    .pip_install("supabase", "groq", "edge-tts", "aiohttp", "ffmpeg-python")
    # Copy the Remotion project (excluding local node_modules to force a clean install)
    .add_local_dir("remotion-app", remote_path="/remotion-app", copy=True, ignore=["node_modules"])
    .run_commands(
        "cd /remotion-app && npm install --legacy-peer-deps",
        "cd /remotion-app && npx remotion bundle src/index.ts --out-dir=bundled --log=error" # PRE-BUNDLE FOR SPEED!
    )
)

# --- Secrets ---
groq_secret = modal.Secret.from_dotenv()
supabase_secret = modal.Secret.from_dotenv()

# --- Helper Functions ---
async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_path)

# --- Render Worker ---
@app.function(
    image=render_image,
    cpu=2.0,
    memory=1024,
    timeout=600
)
def render_slide_worker(slide_data, slide_index, est_duration):
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
        
        process = subprocess.run(cmd, cwd="/remotion-app", capture_output=True, text=True)
        if process.returncode != 0:
            print("Remotion Error:", process.stderr)
            raise Exception(f"Remotion failed: {process.stderr}")
            
        static_frame = os.path.join(tmpdir, "frame.png")
        subprocess.run([
            "ffmpeg", "-y", "-sseof", "-0.1", "-i", rendered_mp4,
            "-update", "1", "-q:v", "2", static_frame
        ], check=True, capture_output=True)
        
        loop_duration = max(est_duration - 3.0, 1.0)
        concated_mp4 = os.path.join(tmpdir, "concated.mp4")
        
        if loop_duration > 0.5:
            looped_mp4 = os.path.join(tmpdir, "looped.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-loop", "1", "-framerate", "24", "-i", static_frame,
                "-c:v", "libx264", "-preset", "ultrafast",
                "-t", str(loop_duration), "-pix_fmt", "yuvj420p", "-crf", "35",
                looped_mp4
            ], check=True, capture_output=True)
            
            concat_list = os.path.join(tmpdir, "concat_list.txt")
            with open(concat_list, "w") as f:
                f.write(f"file '{rendered_mp4}'\n")
                f.write(f"file '{looped_mp4}'\n")
            
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                "-c", "copy", "-movflags", "+faststart", concated_mp4
            ], check=True, capture_output=True)
        else:
            shutil.copy(rendered_mp4, concated_mp4)
            
        with open(concated_mp4, "rb") as f:
            video_bytes = f.read()
            
    return video_bytes

# --- Orchestrator ---
@app.function(
    image=orchestrator_image,
    cpu=1.0,
    memory=1024,
    timeout=1200,
    secrets=[groq_secret, supabase_secret]
)
async def orchestrate_job(job_id: str, prompt: str):
    print(f"Starting job {job_id} for prompt: {prompt}")
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_prompt = """
    You are an educational video script writer. Based on the user's topic, generate a JSON array of exactly 6 slides.
    Use the following types: TitleSlide, AgendaSlide, SectionDividerSlide, ConceptExplanationSlide, ComparisonSlide, StepByStepProcessSlide, DataStatisticsSlide, ExampleCaseStudySlide, SummarySlide, QuestionDiscussionSlide.
    Each slide must have: 'type', 'title', 'content' (array of strings, or exactly 4 strings for ComparisonSlide), 'narration' (text to be spoken), and optionally 'latex' and 'icon' (lucide-react icon name like 'Brain').
    Respond ONLY with raw JSON, no markdown blocks.
    """
    
    chat_completion = await groq_client.chat.completions.create(
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
        if raw_json.startswith('```json'):
            raw_json = raw_json[7:-3]
        slides = json.loads(raw_json)
    except Exception as e:
        supabase.table("videos").update({"status": "failed", "error_message": "LLM output invalid"}).eq("id", job_id).execute()
        return

    supabase.table("videos").update({"status": "script_generated", "slides_data": slides}).eq("id", job_id).execute()
    
    print("Spawning Remotion render workers...")
    worker_calls = []
    for i, slide in enumerate(slides):
        text = slide.get("narration", slide.get("title", ""))
        est_duration = max(len(text) * 0.07 + 2.0, 5.0)
        slide['durationInSeconds'] = est_duration
        call = await render_slide_worker.spawn.aio(slide, i, est_duration)
        worker_calls.append(call)
        
    supabase.table("videos").update({"status": "rendering", "slides_data": slides}).eq("id", job_id).execute()

    print("Generating TTS concurrently...")
    audio_results = []
    with tempfile.TemporaryDirectory() as tts_dir:
        tasks = []
        for i, slide in enumerate(slides):
            text = slide.get("narration", slide.get("title", ""))
            out_path = os.path.join(tts_dir, f"audio_{i}.mp3")
            audio_results.append(out_path)
            tasks.append(generate_audio(text, out_path))
            
        await asyncio.gather(*tasks)
        
        audio_bytes_list = []
        for path in audio_results:
            with open(path, "rb") as f:
                audio_bytes_list.append(f.read())
                
    print("Waiting for silent video chunks from workers...")
    slide_videos_bytes = []
    for call in worker_calls:
        slide_videos_bytes.append(await call.get.aio())
        
    print("Merging audio and concatenating slides...")
    with tempfile.TemporaryDirectory() as merge_dir:
        merged_slides = []
        
        for i in range(len(slides)):
            silent_mp4 = os.path.join(merge_dir, f"silent_{i}.mp4")
            audio_mp3 = os.path.join(merge_dir, f"audio_{i}.mp3")
            final_mp4 = os.path.join(merge_dir, f"merged_{i}.mp4")
            
            with open(silent_mp4, "wb") as f:
                f.write(slide_videos_bytes[i])
            with open(audio_mp3, "wb") as f:
                f.write(audio_bytes_list[i])
                
            subprocess.run([
                "ffmpeg", "-y", "-i", silent_mp4, "-i", audio_mp3,
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-threads", "1", "-shortest", final_mp4
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            merged_slides.append(final_mp4)
            
        list_file_path = os.path.join(merge_dir, "list.txt")
        with open(list_file_path, "w") as list_file:
            for path in merged_slides:
                list_file.write(f"file '{path}'\n")
                
        final_output = os.path.join(merge_dir, "final_output.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file_path,
            "-c", "copy", final_output
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        storage_path = f"{job_id}/final.mp4"
        with open(final_output, "rb") as f:
            supabase.storage.from_("video-assets").upload(file=f.read(), path=storage_path, file_options={"content-type": "video/mp4"})
            
        final_url = supabase.storage.from_("video-assets").get_public_url(storage_path)
        
    supabase.table("videos").update({"status": "completed", "video_url": final_url}).eq("id", job_id).execute()
    print(f"Job {job_id} completed successfully. URL: {final_url}")

# --- Webhook ---
@app.function(image=orchestrator_image, secrets=[supabase_secret])
@modal.fastapi_endpoint(method="POST")
async def start_generation(request: dict):
    prompt = request.get("prompt")
    if not prompt:
        return {"error": "Missing prompt"}
        
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    res = supabase.table("videos").insert({"prompt": prompt, "status": "pending"}).execute()
    job_id = res.data[0]['id']
    
    await orchestrate_job.spawn.aio(job_id, prompt)
    
    return {"job_id": job_id, "status": "pending"}
