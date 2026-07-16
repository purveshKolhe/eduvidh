# Developing and debugging | Modal Docs

Source: https://modal.com/docs/guide/developing-debugging

---

---

Copy page

# Developing and debugging

Modal makes it easy to run apps in the cloud, try code changes in the cloud, and
debug remotely executing code as if it were right there on your laptop. To speed
boost your inner dev loop, this guide provides a rundown of tools and techniques
for developing and debugging software in Modal.

## InteractivityÂ

You can launch a Modal App interactively and have it drop you right into the
middle of the action, at an interesting callsite or the site of a runtime
detonation.

### Interactive functionsÂ

It is possible to start the interactive Python debugger or start an `IPython` REPL right in the middle of your Modal App.

To do so, you first need to run your App in âinteractiveâ mode by using the `--interactive` / `-i` flag. In interactive mode, you can establish a connection
to the calling terminal by calling `interact()` from within your function.

For a simple example, you can accept user input with the built-in Python `input` function:

```
@app.function()
def my_fn(hidden):
    modal.interact()

    x = input("Enter a number: ")
    if hidden == x:
        print(f"Your number is {x}, which is the hidden value!")
    else:
        print(f"Your number is {x}, which is not the hidden value")
```

Now when you run your app with the `--interactive` flag, youâre able to send
inputs to your app, even though itâs running in a remote container!

```
modal run -i guess_number.py::my_fn --hidden 5
Enter a number: 5
Your number is 5, which is the hidden value!
```

For a more interesting example, you can [`pip_install("ipython")`](/docs/sdk/py/latest/modal.Image#pip_install) and start an `IPython` REPL dynamically anywhere in your code:

```
@app.function()
def f():
    model = expensive_function()
    # play around with model
    modal.interact()
    import IPython
    IPython.embed()
```

The built-in Python debugger can be initiated with the languageâs `breakpoint()` function. For convenience, breakpoints call `interact` automatically.

```
@app.function()
def f():
    x = "10point3"
    breakpoint()
    answer = float(x)
```

 

### Debugging Running ContainersÂ

 

#### Debug ShellsÂ

Modal also lets you run interactive commands on your running Containers from the
terminal â much like `ssh`-ing into a traditional machine or cloud VM.

To run a command inside a running Container, you first need to get the Container
ID. You can view all running Containers and their Container IDs with [`modal container list`](/docs/cli/latest/container).

After you obtain the Container ID, you can connect to the Container with `modal shell [container-id]`. This launches a âDebug Shellâ that comes with some preinstalled tools:

* `vim`
* `nano`
* `ps`
* `strace`
* `curl`
* `py-spy`
* and more!

You can use a debug shell to examine or terminate running processes, modify the Container filesystem, run commands, and more. You can also install additional packages using your Containerâs package manager (ex. `apt`).

Note that debug shells will terminate immediately once your Container has finished running.

#### `modal container exec`Â

You can also execute a specific command in a running Container with `modal container exec [container-id] [command...]`. For example, to see what files are in `/root`, you can run `modal container exec [container-id] ls /root`.

```
â¯ modal container list
                         Active Containers in environment: nathan-dev
âââââââââââââââââââââââââââââââââ³ââââââââââââââââââââââââââââ³âââââââââââ³âââââââââââââââââââââââ
â Container ID                  â App ID                    â App Name â Start Time           â
â¡ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ©
â ta-01JK47GVDMWMGPH8MQ0EW30Y25 â ap-FSuhQ4LpvNAt5b6mKi1CDw â my-app   â 2025-02-02 16:02 EST â
âââââââââââââââââââââââââââââââââ´ââââââââââââââââââââââââââââ´âââââââââââ´âââââââââââââââââââââââ

â¯ modal container exec ta-01JK47GVDMWMGPH8MQ0EW30Y25 ls /root
__pycache__  test00.py
```

Note that your executed command will terminate immediately once your Container
has finished running.

By default, commands will be run within a [pseudoterminal (PTY)](https://en.wikipedia.org/wiki/Pseudoterminal), but this
can be disabled with the `--no-pty` flag.

#### Live container profilingÂ

When a container or input is seemingly stuck or not making progress,
you can use the Modal web dashboard to find out what code thatâs executing in the
container in real time. To do so, look for **Live Profiling** in the **Containers** tab in your
function dashboard.

![Live container profiling](https://modal-public-assets.s3.us-east-1.amazonaws.com/live-profiling-bigger.gif)

### Debugging Container ImagesÂ

You can also launch an interactive shell in a new Container with the same
environment as your Function. This is handy for debugging issues with your
Image, interactively refining build commands, and exploring the contents of [`Volume`](/docs/sdk/py/latest/modal.Volume)s and [`NetworkFileSystem`](/docs/sdk/py/latest/modal.NetworkFileSystem)s.

The primary interface for accessing this feature is the [`modal shell`](/docs/cli/latest/shell) CLI command, which accepts a Function
name in your App (or prompts you to select one, if none is provided), and runs
an interactive command on the same image as the Function, with the same [`Secret`](/docs/sdk/py/latest/modal.Secret)s and [`NetworkFileSystem`](/docs/sdk/py/latest/modal.NetworkFileSystem)s attached as the selected Function.

The default command is `/bin/bash`, but you can override this with any other
command of your choice using the `--cmd` flag.

Note that `modal shell [filename].py` does not attach a shell to a running Container of the
Function, but instead creates a fresh instance of the underlying Image. To attach a shell to a running Container, use `modal shell [container-id]` instead.

## Live updatingÂ

 

### Hot reloading with `modal serve`Â

Modal has the command `modal serve <filename.py>`, which creates a loop that
live updates an App when any of the supporting files change.

Live updating works with Web Functions, syncing your changes as you make them,
and it also works well with cron schedules and job queues.

```
import modal

app = modal.App(image=modal.Image.debian_slim().pip_install("fastapi"))

@app.function()
@modal.fastapi_endpoint()
def f():
    return "I update on file edit!"

@app.function(schedule=modal.Period(seconds=5))
def run_me():
    print("I also update on file edit!")
```

If you edit this file, the `modal serve` command will detect the change and
update the code, without having to restart the command.

## ObservabilityÂ

Each running Modal App, including all ephemeral Apps, streams logs and resource
metrics back to you for viewing.

On start, an App will log a dashboard link that will take you its App page.

```
$ python3 main.py
â Initialized. View app page at https://modal.com/apps/ap-XYZ1234.
...
```

From this page you can access the following:

* logs, both from your application and system-level logs from Modal
* compute resource metrics (CPU, RAM, GPU)
* function call history, including historical success/failure counts

### Debug logsÂ

You can enable Modalâs client debug logs by setting the `MODAL_LOGLEVEL` environment variable to `DEBUG`.
Running the following will show debug logging from the Modal client running locally.

```
MODAL_LOGLEVEL=DEBUG modal run hello.py
```

To enable debug logs in the Modal client running in the remote container, you can set `MODAL_LOGLEVEL` using
a Modal [`Secret`](/docs/sdk/py/latest/modal.Secret).

```
@app.function(secrets=[modal.Secret.from_dict({"MODAL_LOGLEVEL": "DEBUG"})])
def f():
    print("Hello, world!")
```

 

### Client tracebacksÂ

To see a traceback (a.k.a [stack trace](https://en.wikipedia.org/wiki/Stack_trace)) for a client-side exception, you can set the `MODAL_TRACEBACK` environment variable to `1`.

```
MODAL_TRACEBACK=1 modal run my_app.py
```

We encourage you to report cases where you need to enable this functionality, as itâs indication of an issue in Modal.

[Developing and debugging](#developing-and-debugging)[Interactivity](#interactivity)[Interactive functions](#interactive-functions)[Debugging Running Containers](#debugging-running-containers)[Debug Shells](#debug-shells)[modal container exec](#modal-container-exec)[Live container profiling](#live-container-profiling)[Debugging Container Images](#debugging-container-images)[Live updating](#live-updating)[Hot reloading with modal serve](#hot-reloading-with-modal-serve)[Observability](#observability)[Debug logs](#debug-logs)[Client tracebacks](#client-tracebacks)