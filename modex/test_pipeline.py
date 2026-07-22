import os
import json
import modal

def main():
    print("Connecting to Modal app 'modex-video-generator'...")
    try:
        # Load the deployed Modal class
        generator = modal.Cls.from_name("modex-video-generator", "ExplainerGenerator")()
    except Exception as e:
        print(f"Error: Could not find deployed Modal app. Did you deploy it first using 'modal deploy modal_app.py'? | Error: {e}")
        return

    prompt = "Explain dynamic programming in under 60 seconds with math code and examples."
    print(f"Submitting video generation request for prompt: '{prompt}'...")
    
    # Execute the remote Modal function
    result = generator.generate_video.remote(prompt)
    
    print("\n" + "="*80)
    print("JOB COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"Video URL: {result.get('video_url')}")
    print(f"Video Length: {result.get('video_length_seconds')} seconds")
    print("\nRESOURCES USED TIMINGS:")
    print(json.dumps(result, indent=2))
    print("="*80)

if __name__ == "__main__":
    main()
