# Run and share Streamlit apps | Modal Docs

Source: https://modal.com/docs/examples/serve_streamlit

---

---

[View on GitHub](https://github.com/modal-labs/modal-examples/blob/main/10_integrations/streamlit/serve_streamlit.py)

 

Copy page

# Run and share Streamlit apps

This example shows you how to run a Streamlit app with `modal serve`, and then deploy it as a serverless web app.

![example streamlit app](/_app/immutable/assets/streamlit.RHfhqFCX.png)

This example is structured as two files:

1. This module, which defines the Modal objects (name the script `serve_streamlit.py` locally).
2. `app.py`, which is any Streamlit script to be mounted into the Modal
   function ([download script](https://github.com/modal-labs/modal-examples/blob/main/10_integrations/streamlit/app.py)).

```
import shlex
import subprocess
from pathlib import Path

import modal
```

 

## Define container dependenciesÂ

The `app.py` script imports three third-party packages, so we include these in the exampleâs
image definition and then add the `app.py` file itself to the image.

```
streamlit_script_local_path = Path(__file__).parent / "app.py"
streamlit_script_remote_path = "/root/app.py"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .uv_pip_install("streamlit~=1.35.0", "numpy~=1.26.4", "pandas~=2.2.2")
    .add_local_file(
        streamlit_script_local_path,
        streamlit_script_remote_path,
    )
)

app = modal.App(name="example-serve-streamlit", image=image)

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "app.py not found! Place the script with your streamlit app in the same directory."
    )
```

 

## Spawning the Streamlit serverÂ

Inside the container, we will run the Streamlit server in a background subprocess using `subprocess.Popen`. We also expose port 8000 using the `@web_server` decorator.

```
@app.function()
@modal.concurrent(max_inputs=100)
@modal.web_server(8000)
def run():
    target = shlex.quote(streamlit_script_remote_path)
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)
```

 

## Iterate and DeployÂ

While youâre iterating on your screamlit app, you can run it âephemerallyâ with `modal serve`. This will
run a local process that watches your files and updates the app if anything changes.

```
modal serve serve_streamlit.py
```

Once youâre happy with your changes, you can deploy your application with

```
modal deploy serve_streamlit.py
```

If successful, this will print a URL for your app that you can navigate to from
your browser ð .

[Run and share Streamlit apps](#run-and-share-streamlit-apps)[Define container dependencies](#define-container-dependencies)[Spawning the Streamlit server](#spawning-the-streamlit-server)[Iterate and Deploy](#iterate-and-deploy)

 

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
modal serve 10_integrations/streamlit/serve_streamlit.py
```