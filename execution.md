# Production pipeline execution handoff

This is an implementation brief for Gemini. It intentionally contains no code. Preserve the public request/status contract so the frontend can switch endpoints through environment configuration only.

## Target workflow

`POST /` reaches the Azure VM orchestrator. It creates the job, immediately starts warming the Modal render pool, generates the script and TTS in parallel, then splits the slides deterministically:

| Slide count `N` | VM slides | Modal slides |
| --- | --- | --- |
| `0` | `0` | `0` |
| `1` | `1` | `0` |
| `2` | `2` | `0` |
| `>2` | first `2` | slides `2..N-1` |

The VM and Modal renders run concurrently. TTS runs concurrently with both. The VM collects results by original slide index, merges audio, concatenates in order, uploads once, and persists `completed` or `failed`. `GET /status/{job_id}` must retain its current response shape.

## Existing implementation to change

- `azure_vm/vm_app.py` currently renders every slide by spawning a new `npx remotion` process. Make it the hybrid orchestrator and local-render client; do not leave its all-local fan-out path active.
- `modal_app.py` currently owns the public webhook and renders all slides remotely. Keep it as the Modal worker application, but do not let it create a second competing orchestrator/job.
- `remotion-app/src/Root.tsx` still declares 30 fps even though worker commands render 72 frames as if they were 24 fps. Fix this before measuring performance.
- `remotion-app/src/templates/MainVideo.tsx` already calculates slide lengths at 24 fps. Audit all hard-coded frame timings in `Shared.tsx` and `Slides.tsx` so the visual timing remains intentional after the root composition changes to 24 fps.
- `frontend/src/app/page.tsx` already accepts either `NEXT_PUBLIC_WEBHOOK_URL` or `NEXT_PUBLIC_MODAL_WEBHOOK_URL`. Point the former at the VM API; no frontend behavior change is needed if the API contract above is preserved.

## Implementation order

### 1. Establish one configuration contract

Create explicit, documented settings for VM capacity (`2`), target FPS (`24`), animation duration (`3 seconds` / `72 frames`), expected max slide count, Modal remote-worker cap, worker idle time, VM API URL, and Modal authentication/secrets. Do not rely on the current `VM_RENDER_CONCURRENCY` alone: it limits concurrency but still queues all six slides on the VM.

Validate `N`, slide payloads, durations, and every remote result before merging. Keep a stable `slide_index` on every task/result; completion order must never affect final-video order.

### 2. Move the control plane to the Azure VM

Run a persistent authenticated HTTP service on the VM with the existing submit/status endpoints. It must:

1. Create the database job and record a monotonic start timestamp.
2. Start a non-blocking Modal warm-pool request immediately, before calling Groq.
3. Generate and validate the slide script, calculate durations, persist `script_generated`, then persist `rendering`.
4. Dispatch precisely the first `min(N, 2)` slides to the local renderer and the remainder to Modal at the same time.
5. Generate all TTS files in parallel and overlap it with rendering.
6. Collect, merge, upload, and persist results exactly once.

Retire or make private the Modal `start_generation` endpoint so one user action cannot start both the old all-Modal pipeline and the new hybrid pipeline. Use server-side secrets only for database/storage/Groq/Modal credentials; never expose them in the frontend or logs.

### 3. Build the persistent local renderer

Replace per-slide `npx remotion render` calls on the VM with one long-lived Node-based renderer service. Python talks to it through a local-only request channel; it should not be publicly exposed.

The service requirements are:

1. Launch exactly one Chromium process at service startup with a fixed remote-debugging endpoint.
2. Create a pool of exactly two isolated tabs, load the pre-bundled Remotion app in each, and wait until each has a positive ready signal.
3. For each local request, assign one free tab, inject only validated slide props into the supported page bridge (`window.remotion_setProps`), wait for the React commit/paint acknowledgment, render frames `0..71` at 24 fps, then produce the same silent MP4 contract the current local worker returns.
4. Reuse the tab after clearing per-slide state. If a tab/browser fails, replace only the failed tab; fail the job only if recovery fails.
5. Enforce a queue of two active local jobs. Extra local work must be sent to Modal by the allocator, not queued locally.
6. Gracefully drain and close Chromium on VM service shutdown.

Add the explicit page bridge and readiness acknowledgment to the Remotion app. Do not assume a global called `remotion_setProps` exists today. Verify the installed Remotion API before selecting the rendering implementation; the current CLI path does not itself provide persistent-page reuse.

Keep the existing three-second animation plus static-frame extension behavior. Generate the animation clip at 24 fps, capture its final frame deterministically, and loop it for `max(estimated_duration - 3, 1)` seconds. Ensure both video pieces have compatible frame rate, time base, pixel format, and codec before concatenation.

### 4. Make 24 fps a single source of truth

Set the root composition to 24 fps and derive duration/frame limits from the shared config. The render frame range must remain 72 frames (`0..71`); do not accidentally change it to 72 seconds or 71 frames.

Review every frame-based animation threshold. Either scale it to preserve its current wall-clock duration or intentionally document the new timing. Render a representative slide of every supported type and inspect the last animation frame, because text/LaTex/icon animations are easy to truncate.

### 5. Implement real Modal pre-warming

Treat a dummy render call as a best-effort signal, not proof that the later render will get the same container. Use the render function's own autoscaling pool so warm containers can actually serve render inputs.

For the current six-slide product, request capacity for four remote workers at submission time. For variable `N`, derive the count from `max(N - 2, 0)` once `N` is known, and use a safe upper bound for the initial warm request. Set a `max_containers` ceiling to prevent a multi-job burst from exceeding the credit budget.

Use Modal's warm-pool controls (`min_containers`/`buffer_containers` and a suitable `scaledown_window`) or a deployment-supported dynamic autoscaler update. The worker's container initialization—including loading the bundle and browser prerequisites—must finish before it is counted warm. Reduce the warm target back to zero (or the normal baseline) in `finally`, after all success/failure paths. Record the requested count, ready time, and actual render queue/cold-start time.

Do not move the existing `scaledown_window=2` forward unchanged: it is too short to be a useful warm window and must be an intentional cost/latency setting. Do not add GPUs without a benchmark showing a renderer benefit; the current workers are CPU workers.

### 6. Keep the Modal worker narrowly scoped

Modify `render_slide_worker` so it accepts a single slide and returns the existing silent-video result plus complete timing metadata. It must render only the slides allocated by the VM. Limit one CPU-bound render per container; Modal input concurrency is not appropriate for simultaneous Chromium renders in a 1 GB worker.

Keep the bundle built into the image. Confirm the image build excludes local `node_modules`, uses lockfile-respecting installation, and is deployed before measuring. Avoid returning duplicate input data or logs containing slides, prompts, keys, or audio.

### 7. Preserve correctness and observability

Use a single job state machine: `pending` → `script_generated` → `rendering` → `completed` or `failed`. Every exception path must update the same job record and release the Modal warm capacity.

Record separately:

- request-to-orchestrator time;
- Modal warm requested/ready/queue time;
- script generation, TTS, VM render, Modal render, merge, upload, and total wall-clock time;
- local browser restarts/tab replacement count;
- VM peak RSS, local active count, Modal per-worker CPU/RSS, and allocation counts.

Never label summed worker CPU time as wall-clock time. Do not change the database schema unless the current JSON `resources_used` field cannot hold these fields.

## Acceptance tests and rollout

1. Unit-test the allocator for `N=0,1,2,3,6` and an upper-bound slide count. It must always assign exactly `min(N,2)` local slides and preserve all indices.
2. Test the VM renderer with two concurrent slides, then repeated jobs. Confirm one Chromium process and two reused tabs; peak VM memory must remain below the no-swap budget.
3. Test one local-only (`N=2`), one hybrid (`N=6`), a Modal failure, a browser-tab failure, invalid LLM JSON, storage failure, and a retry after failure. Verify terminal DB state and warm-pool cleanup in each case.
4. Render all slide types at 24 fps and verify output duration, frame count, audio synchronization, no black/blank first frame, and seamless concat.
5. Capture at least five cold and five warm six-slide runs. Compare p50/p95 end-to-end time, render time, VM RSS, Modal queue time, and billed compute against the current all-Modal baseline. Only claim the projected 13-second/51% targets if the measured definitions match the blueprint.
6. Deploy in a feature-flagged mode: retain the current all-Modal path as rollback, enable hybrid for one controlled job at a time, then raise traffic after metrics are stable. Roll back on incorrect ordering, failed cleanup, VM swapping, or a cost regression.

## Minimal Gemini task prompt

Implement `production_pipeline_optimizations.md` exactly as scoped by `execution.md`. First inspect the named files and the installed Remotion/Modal APIs. Make no frontend UI changes and preserve the current `POST /` and `GET /status/{job_id}` JSON contracts. Build the hybrid VM-owned pipeline, true two-tab persistent Chromium/CDP renderer, 24-fps single source of truth, Modal warm-pool lifecycle, indexed merge, metrics, tests, and a feature-flagged rollback path. Do not add GPUs, new database schema, or unrelated refactors. Run the listed acceptance tests and report measured metrics plus any target that is not met.
