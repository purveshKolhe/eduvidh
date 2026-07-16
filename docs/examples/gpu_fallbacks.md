# Set âfallbackâ GPUs | Modal Docs

Source: https://modal.com/docs/examples/gpu_fallbacks

---

---

[View on GitHub](https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/gpu_fallbacks.py)

 

Copy page

# Set âfallbackâ GPUs

GPU availabilities on Modal can fluctuate, especially for
tightly-constrained requests, like for eight co-located GPUs
in a specific region.

If your code can run on multiple different GPUs, you can specify
your GPU request as a list, in order of preference, and whenever
your Function scales up, we will try to schedule it on each requested GPU type in order.

The code below demonstrates the usage of the `gpu` parameter with a list of GPUs.

```
import subprocess

import modal

app = modal.App("example-gpu-fallbacks")

@app.function(
    gpu=["h100", "a100", "any"],  # "any" means any of L4, A10, or T4
    single_use_containers=True,  # new container each input, so we re-roll the GPU dice every time
)
async def remote(_idx):
    gpu = subprocess.run(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    print(gpu)
    return gpu

@app.local_entrypoint()
def local(count: int = 32):
    from collections import Counter

    gpu_counter = Counter(remote.map([i for i in range(count)], order_outputs=False))
    print(f"ran {gpu_counter.total()} times")
    print(f"on the following {len(gpu_counter.keys())} GPUs:", end="\n")
    print(
        *[f"{gpu.rjust(32)}: {'ð¥' * ct}" for gpu, ct in gpu_counter.items()],
        sep="\n",
    )
```

[Set âfallbackâ GPUs](#set-fallback-gpus)

 

## Try this on Modal!

You can run this example on Modal in 60 seconds.

[Create account to run](/signup)

After creating a free account, install the Modal Python package, and
create an API token.

$

```
pip install modal
```

$

```
modal setup
```

Clone the [modal-examples](https://github.com/modal-labs/modal-examples) repository and run:

$

```
git clone https://github.com/modal-labs/modal-examples
```

$

```
cd modal-examples
```

$

```
modal run 06_gpu_and_ml/gpu_fallbacks.py
```