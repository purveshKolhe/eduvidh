# Installing the CUDA Toolkit on Modal | Modal Docs

Source: https://modal.com/docs/examples/install_cuda

---

---

[View on GitHub](https://github.com/modal-labs/modal-examples/blob/main/02_building_containers/install_cuda.py)

 

Copy page

# Installing the CUDA Toolkit on Modal

This code sample is intended to quickly show how different layers of the CUDA stack are used on Modal.
For greater detail, see our [guide to using CUDA on Modal](https://modal.com/docs/guide/cuda).

All Modal Functions with GPUs already have the NVIDIA CUDA drivers,
NVIDIA System Management Interface, and CUDA Driver API installed.

```
import modal

app = modal.App("example-install-cuda")

@app.function(gpu="T4")
def nvidia_smi():
    import subprocess

    subprocess.run(["nvidia-smi"], check=True)
```

This is enough to install and use many CUDA-dependent libraries, like PyTorch.

```
@app.function(gpu="T4", image=modal.Image.debian_slim().uv_pip_install("torch"))
def torch_cuda():
    import torch

    print(torch.cuda.get_device_properties("cuda:0"))
```

If your application or its dependencies need components of the CUDA toolkit,
like the `nvcc` compiler driver, installed as system libraries or command-line tools,
youâll need to install those manually.

We recommend the official NVIDIA CUDA Docker images from Docker Hub.
Youâll need to add Python 3 and pip with the `add_python` option because the image
doesnât have these by default.

```
ctk_image = modal.Image.from_registry(
    "nvidia/cuda:12.4.0-devel-ubuntu22.04", add_python="3.11"
).entrypoint([])  # removes chatty prints on entry

@app.function(gpu="T4", image=ctk_image)
def nvcc_version():
    import subprocess

    return subprocess.run(["nvcc", "--version"], check=True)
```

You can check that all these functions run by invoking this script with `modal run`.

```
@app.local_entrypoint()
def main():
    nvidia_smi.remote()
    torch_cuda.remote()
    nvcc_version.remote()
```

[Installing the CUDA Toolkit on Modal](#installing-the-cuda-toolkit-on-modal)

 

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
modal run 02_building_containers/install_cuda.py
```