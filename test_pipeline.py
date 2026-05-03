import os
import time
import requests
from supabase import create_client

url = "https://nimishtijare7--edu-video-generator-start-generation.modal.run"
prompt = "Explain the solar system"

print(f"Triggering video generation for: {prompt}")
res = requests.post(url, json={"prompt": prompt})
data = res.json()

if "job_id" not in data:
    print("Failed to start job:", data)
    exit(1)

job_id = data["job_id"]
print(f"Job ID: {job_id}")

supabase_url = "https://nfmijieocgwmitjcuwix.supabase.co"
supabase_key = "sb_publishable_seNgNIhdgIiIHrHg0fQGog_LFZDKkB6"
supabase = create_client(supabase_url, supabase_key)

print("Polling Supabase for status...")
while True:
    response = supabase.table("videos").select("status, video_url, error_message").eq("id", job_id).execute()
    if not response.data:
        print("No data found for job_id")
        break
    
    status = response.data[0]["status"]
    print(f"Current Status: {status}")
    
    if status == "completed":
        video_url = response.data[0]["video_url"]
        print(f"Success! Video URL: {video_url}")
        print("Downloading to output.mp4...")
        vid_res = requests.get(video_url)
        with open("output.mp4", "wb") as f:
            f.write(vid_res.content)
        print("Done. Saved as output.mp4")
        break
    elif status == "failed":
        print("Job failed:", response.data[0]["error_message"])
        break
        
    time.sleep(5)
