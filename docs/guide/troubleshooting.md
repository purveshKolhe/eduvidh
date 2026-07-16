# Troubleshooting | Modal Docs

Source: https://modal.com/docs/guide/troubleshooting

---

---

Copy page

# Troubleshooting

This guide page documents solutions for common Modal issues.

For tips on troubleshooting your own code running on Modal,
see [this guide page](/docs/guide/developing-debugging).

## âCommand not foundâ errorsÂ

If you installed Modal but youâre seeing an error like `modal: command not found` when trying to run the CLI, this means that the
installation location of Python package executables (âbinariesâ) are not present
on your system path. This is a common problem; you need to reconfigure your
systemâs environment variables to fix it.

One workaround is to use `python -m modal` instead of `modal`. However, this
is just a patch. Thereâs no single solution for the problem, because Python
installs dependencies on different locations depending on your environment. See
this [popular StackOverflow question](https://stackoverflow.com/q/35898734) for
pointers on how to resolve your system path issue.

## Function side effectsÂ

The same container *can* be reused for multiple invocations of the same Function
within an App. This means that if your Function has side effects like modifying
files on disk, they may or may not be present for subsequent calls to that
Function. You should not rely on the side effects to be present, but you might
have to be careful so they donât cause problems.

For example, if you create a disk-backed database using sqlite3:

```
import modal
import sqlite3

app = modal.App()

@app.function()
def db_op():
    db = sqlite3("db_file.sqlite3")
    db.execute("CREATE TABLE example (col_1 TEXT)")
    ...
```

This Function *can* (but will not necessarily) fail on the second invocation
with an `OperationalError: table foo already exists` error.

To get around this, take care to either clean up your side effects (e.g.
deleting the db file at the end your function call above) or make your Functions
take them into consideration (e.g. adding an `if os.path.exists("db_file.sqlite")` condition or randomize the filename
above). Alternatively, you can set `single_use_containers=True` so that every
Function call will spin up a new container; however, note that this will result
in higher cost and worse latency as every invocation will require a cold start.

## Heartbeat timeoutÂ

The Modal client in `modal.Function` containers runs a heartbeat loop that the host uses to healthcheck the containerâs main process.
If the container stops heartbeating for a long period (minutes), the container will be terminated due to a `heartbeat timeout`, which is displayed in logs.

Container heartbeat timeouts are rare, and they are typically caused by one of two application-level sources:

* [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock) is held for a long time, stopping the heartbeat thread from making progress. [py-spy](https://github.com/benfred/py-spy?tab=readme-ov-file#how-does-gil-detection-work) can detect GIL holding. We include `py-spy` [automatically in `modal shell`](/docs/guide/developing-debugging#debug-shells) for convenience. A quick fix for GIL holding is to run the code which holds the GIL [in a subprocess](https://docs.python.org/3/library/multiprocessing.html#the-process-class).
* Container process initiates shutdown, intentionally stopping the heartbeats, but it does not complete shutdown.

In both cases [turning on debug logging](/docs/guide/developing-debugging#debug-logs) will help diagnose the issue.

## `413 Content Too Large` errorsÂ

If you receive a `413 Content Too Large` error, this might be because you are
hitting our gRPC payload size limits.

The size limit is currently 100MB.

## Outdated kernel version (4.4.0)Â

Our secure runtime [reports a misleadingly old](https://github.com/google/gvisor/issues/11117) kernel version, 4.4.0.
Certain software libraries will detect this and report a warning. These warnings can be ignored because the runtime
actually implements Linux kernel features from versions 5.15+.

If the outdated kernel version reporting creates errors in your application please contact us [in our Slack](https://modal.com/slack).

## CUDA driver initialization failed on L4 GPU typeÂ

Certain L4 instance types within Modalâs fleet have a flaky issue in the NVIDIA driver which causes
the following CUDA context initialization error:

```
RuntimeError: CUDA driver initialization failed, you might not have a CUDA gpu.
```

A workaround to ensure reliable container startup is given below:

```
@modal.enter()
def warmup_cuda(self):
    import ctypes
    import time
    import modal
    cu = ctypes.CDLL("libcuda.so.1")
    max_retries = 10
    retry_delay_secs = 0.5
    for attempt in range(max_retries):
        rc = cu.cuInit(0)
        if rc == 0:
            break
        else:
            if attempt < max_retries - 1:
                print(f"cuInit failed on attempt {attempt + 1}/{max_retries} with code {rc}, retrying...")
                time.sleep(retry_delay_secs)
    else:
        print(f"CUDA initialization failed after {max_retries} attempts; stopping container")
        modal.experimental.stop_fetching_inputs()
```

We are investigating a root cause fix for this problem.
Multi-cloud GPU reliability at the scale of many thousands of GPUs is a tough technical challenge!
Read more about our solution [here](/blog/gpu-health).

## Connection issues in forked processesÂ

When a process is forked, the child may inherit stale network state from
the parent. If youâre using Modal from a forked process (e.g. Celery prefork
workers, `multiprocessing`), create a fresh client after the fork and pass it
explicitly:

```
import multiprocessing
import modal

def child():
    client = modal.Client.from_credentials(token_id, token_secret)
    fc = modal.FunctionCall.from_id(call_id, client=client)
    result = fc.get(timeout=0)

p = multiprocessing.Process(target=child)
p.start()
```

[Troubleshooting](#troubleshooting)[âCommand not foundâ errors](#command-not-found-errors)[Function side effects](#function-side-effects)[Heartbeat timeout](#heartbeat-timeout)[413 Content Too Large errors](#413-content-too-large-errors)[Outdated kernel version (4.4.0)](#outdated-kernel-version-440)[CUDA driver initialization failed on L4 GPU type](#cuda-driver-initialization-failed-on-l4-gpu-type)[Connection issues in forked processes](#connection-issues-in-forked-processes)