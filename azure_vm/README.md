# Azure VM Local Video Pipeline

This folder contains the standalone local version of the video rendering pipeline. Instead of spawning serverless containers on Modal, it executes rendering tasks concurrently on the local machine (e.g. your Azure VM) as child subprocesses, tracking metrics and resource spikes.

---

## File Structure
* **[vm_app.py](file:///home/purvi/Desktop/eduvidh/azure_vm/vm_app.py)**: The main orchestrator script that generates scripts via Groq, executes Remotion/FFmpeg rendering concurrently via `asyncio.create_subprocess_exec`, and profiles CPU/RAM resources.

---

## Setup Requirements

Before running the script, make sure the VM has:
1. **Node.js & npm**: Required to run Remotion.
2. **FFmpeg & FFprobe**: Required to encode and merge video frames and audio.
   ```bash
   sudo dnf install ffmpeg ffmpeg-free-devel -y # Fedora
   # OR
   sudo apt-get install ffmpeg -y # Ubuntu/Debian
   ```
3. **Python Dependencies**:
   Ensure `oracledb`, `boto3`, `edge-tts`, `groq`, and `python-dotenv` are installed in your Python environment:
   ```bash
   pip install oracledb boto3 edge-tts groq python-dotenv
   ```

---

## Running the Pipeline

To execute the pipeline locally, pass a video prompt to the script:
```bash
python vm_app.py "The French Revolution"
```

---

## How Resource Tracking Works on the VM

Rather than relying on separate container logs, the VM script captures precise OS-level resource usage:
1. **Orchestrator Parent (`RUSAGE_SELF`)**: Tracks user/system CPU seconds and peak RSS memory of the main Python orchestrator script.
2. **Workers/Subprocesses (`RUSAGE_CHILDREN`)**: Python's standard `resource.getrusage(resource.RUSAGE_CHILDREN)` captures the **cumulative CPU usage and peak RAM** of all child subprocesses (all 6 parallel `npx remotion render` calls and all `ffmpeg`/`ffprobe` executions) that have exited and been waited for. 

This profiling payload is packaged as a JSON block and saved to the `resources_used` column in your Oracle Database.
