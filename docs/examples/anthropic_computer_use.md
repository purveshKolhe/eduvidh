# Run Anthropicâs computer use demo in a Modal Sandbox | Modal Docs

Source: https://modal.com/docs/examples/anthropic_computer_use

---

---

[View on GitHub](https://github.com/modal-labs/modal-examples/blob/main/13_sandboxes/anthropic_computer_use.py)

 

Copy page

# Run Anthropicâs computer use demo in a Modal Sandbox

This example demonstrates how to run Anthropicâs [Computer Use demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) in a Modal [Sandbox](https://modal.com/docs/guide/sandbox).

## Sandbox SetupÂ

All Sandboxes are associated with an App.

We start by looking up an existing App by name, or creating one if it doesnât exist.

```
import time
import urllib.request

import modal

app = modal.App.lookup("example-anthropic-computer-use", create_if_missing=True)
```

The Computer Use [quickstart](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) provides a prebuilt Docker image. We use this hosted image to create our sandbox environment.

```
sandbox_image = (
    modal.Image.from_registry(
        "ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest",
    )
    .env({"WIDTH": "1920", "HEIGHT": "1080"})
    .workdir("/home/computeruse")
    .entrypoint([])
)
```

Weâll provide the Anthropic API key via a Modal [Secret](https://modal.com/docs/guide/secrets) which the sandbox can access at runtime.

```
secret = modal.Secret.from_name("anthropic-secret", required_keys=["ANTHROPIC_API_KEY"])
```

Now, we can start our Sandbox.
We use `modal.enable_output()` to print the Sandboxâs image build logs to the console.
Weâll also expose the ports required for the demoâs interfaces:

* Port 8501 serves the Streamlit UI for interacting with the agent loop
* Port 6080 serves the VNC desktop view via a browser-based noVNC client

```
with modal.enable_output():
    sandbox = modal.Sandbox.create(
        "sudo",
        "--preserve-env=ANTHROPIC_API_KEY,DISPLAY_NUM,WIDTH,HEIGHT,PATH",
        "-u",
        "computeruse",
        "./entrypoint.sh",
        app=app,
        image=sandbox_image,
        secrets=[secret],
        encrypted_ports=[8501, 6080],
        timeout=60 * 60,  # stay alive for one hour, maximum one day
    )

print(f"ðï¸  Sandbox ID: {sandbox.object_id}")
```

After starting the sandbox, we retrieve the public URLs for the exposed ports.

```
tunnels = sandbox.tunnels()
for port, tunnel in tunnels.items():
    print(f"Waiting for service on port {port} to start at {tunnel.url}")
```

We can check on each serverâs status by making an HTTP request to the serverâs URL
and verifying that it responds with a 200 status code.

```
def is_server_up(url):
    try:
        response = urllib.request.urlopen(url)
        return response.getcode() == 200
    except Exception:
        return False

timeout = 60  # seconds
start_time = time.time()
up_ports = set()
while time.time() - start_time < timeout:
    for port, tunnel in tunnels.items():
        if port not in up_ports and is_server_up(tunnel.url):
            print(f"ðï¸  Server is up and running on port {port}!")
            up_ports.add(port)
    if len(up_ports) == len(tunnels):
        break
    time.sleep(1)
else:
    print("ðï¸  Timed out waiting for server to start.")
```

You can now open the URLs in your browser to interact with the demo!
Note: The sandbox logs may mention `localhost:8080`.
Ignore this and use the printed tunnel URLs instead.

When finished, you can terminate the sandbox from your [Modal dashboard](https://modal.com/containers) or by running `Sandbox.from_id(sandbox.object_id).terminate()`.
The Sandbox will also spin down after one hour.

[Run Anthropicâs computer use demo in a Modal Sandbox](#run-anthropics-computer-use-demo-in-a-modal-sandbox)[Sandbox Setup](#sandbox-setup)

 

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
python 13_sandboxes/anthropic_computer_use.py
```