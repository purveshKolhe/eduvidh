# Azure VM Local Video Pipeline

This folder contains the Azure side of the hybrid production pipeline. It owns job orchestration, renders two slides through one persistent Chrome process with two tabs, and sends the remaining slides to Modal.

---

## File Structure
* **[vm_app.py](vm_app.py)**: The FastAPI control plane and hybrid orchestrator.
* **[../remotion-app/renderer_service.js](../remotion-app/renderer_service.js)**: The local-only persistent Chrome renderer. Start it before the API.

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
3. **Google Chrome and Python dependencies**:
   Ensure Google Chrome plus `aiohttp`, `fastapi`, `modal`, `oracledb`, `boto3`, `edge-tts`, `groq`, `python-dotenv`, and `uvicorn` are installed. `setup_vm.sh` installs these prerequisites and bundles Remotion.
   ```bash
   pip install aiohttp fastapi modal oracledb boto3 edge-tts groq python-dotenv uvicorn
   ```

---

## Running the Pipeline

Start the persistent local renderer, then start the VM API:
```bash
cd ../remotion-app
node renderer_service.js

# In a second terminal:
cd ../azure_vm
python vm_app.py
```

Deploy `modal_app.py` before starting the VM API. The VM requires the deployed Modal application name `edu-video-generator` (or `MODAL_APP_NAME`) and its usual database, storage, and Groq environment variables.

---

## How Resource Tracking Works on the VM

Rather than relying on separate container logs, the VM script captures precise OS-level resource usage:
1. **Orchestrator Parent (`RUSAGE_SELF`)**: Tracks user/system CPU seconds and peak RSS memory of the main Python orchestrator script.
2. **Workers/Subprocesses (`RUSAGE_CHILDREN`)**: Python's standard `resource.getrusage(resource.RUSAGE_CHILDREN)` captures the **cumulative CPU usage and peak RAM** of all child subprocesses (all 6 parallel `npx remotion render` calls and all `ffmpeg`/`ffprobe` executions) that have exited and been waited for. 

This profiling payload is packaged as a JSON block and saved to the `resources_used` column in your Oracle Database.
