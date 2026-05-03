import modal
import os
import json
import asyncio
import tempfile
import subprocess
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
    .apt_install("curl", "git", "ffmpeg")
    .run_commands(
        "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
        "apt-get install -y nodejs",
    )
    .pip_install("supabase")
    # Copy the Remotion project
    .add_local_dir("remotion-app", remote_path="/remotion-app", copy=True)
    .run_commands("cd /remotion-app && npm install --legacy-peer-deps")
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
def render_slide_worker(slide_data, slide_index, audio_url):
    print(f"Worker rendering slide {slide_index}")
    props = {
        "slides": [slide_data],
        "audioUrls": [audio_url]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        props_path = os.path.join(tmpdir, "props.json")
        with open(props_path, "w") as f:
            json.dump(props, f)
            
        output_mp4 = os.path.join(tmpdir, f"out_{slide_index}.mp4")
        
        # Run Remotion render
        cmd = [
            "npx", "remotion", "render", 
            "src/index.ts", "EducationalVideo", 
            output_mp4,
            "--props", props_path
        ]
        
        process = subprocess.run(cmd, cwd="/remotion-app", capture_output=True, text=True)
        if process.returncode != 0:
            print("Remotion Error:", process.stderr)
            raise Exception(f"Remotion failed: {process.stderr}")
            
        with open(output_mp4, "rb") as f:
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
    
    # 1. Init Supabase
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # 2. Call Groq for script
    groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_prompt = """
    You are an educational video script writer. Based on the user's topic, generate a JSON array of 10 slides.
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
    )
    
    try:
        raw_json = chat_completion.choices[0].message.content.strip()
        if raw_json.startswith('```json'):
            raw_json = raw_json[7:-3]
        slides = json.loads(raw_json)
    except Exception as e:
        print("Failed to parse LLM JSON:", chat_completion.choices[0].message.content)
        supabase.table("videos").update({"status": "failed", "error_message": "LLM output invalid"}).eq("id", job_id).execute()
        return

    # Update state
    supabase.table("videos").update({"status": "script_generated", "slides_data": slides}).eq("id", job_id).execute()
    
    # 3. Generate Audio locally via EdgeTTS in parallel
    audio_urls = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tasks = []
        for i, slide in enumerate(slides):
            out_path = os.path.join(tmpdir, f"audio_{i}.mp3")
            tasks.append(generate_audio(slide.get('narration', slide['title']), out_path))
            
        await asyncio.gather(*tasks)
        
        # Determine duration using ffprobe
        for i, slide in enumerate(slides):
            audio_path = os.path.join(tmpdir, f"audio_{i}.mp3")
            cmd = ["ffprobe", "-i", audio_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
            duration = float(subprocess.check_output(cmd).decode('utf-8').strip())
            slide['durationInSeconds'] = duration
            
            # Upload to Supabase Storage
            with open(audio_path, "rb") as f:
                storage_path = f"{job_id}/audio_{i}.mp3"
                supabase.storage.from_("video-assets").upload(file=f.read(), path=storage_path, file_options={"content-type": "audio/mpeg"})
                
            public_url = supabase.storage.from_("video-assets").get_public_url(storage_path)
            audio_urls.append(public_url)

    supabase.table("videos").update({"status": "rendering", "slides_data": slides}).eq("id", job_id).execute()

    # 4. Spawn Workers to Render Slides
    print("Spawning Remotion render workers...")
    worker_calls = []
    for i, slide in enumerate(slides):
        call = render_slide_worker.spawn(slide, i, audio_urls[i])
        worker_calls.append(call)
        
    slide_videos_bytes = [call.get() for call in worker_calls]
    
    # 5. Concatenate
    with tempfile.TemporaryDirectory() as tmpdir:
        list_file_path = os.path.join(tmpdir, "list.txt")
        with open(list_file_path, "w") as list_file:
            for i, video_bytes in enumerate(slide_videos_bytes):
                vid_path = os.path.join(tmpdir, f"slide_{i}.mp4")
                with open(vid_path, "wb") as f:
                    f.write(video_bytes)
                list_file.write(f"file '{vid_path}'\n")
                
        final_output = os.path.join(tmpdir, "final_output.mp4")
        concat_cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file_path, "-c", "copy", final_output]
        subprocess.run(concat_cmd, check=True)
        
        # 6. Upload final
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
    
    # Fire and forget
    orchestrate_job.spawn(job_id, prompt)
    
    return {"job_id": job_id, "status": "pending"}
