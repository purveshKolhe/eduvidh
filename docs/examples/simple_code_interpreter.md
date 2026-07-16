# Build a stateful, sandboxed code interpreter | Modal Docs

Source: https://modal.com/docs/examples/simple_code_interpreter

---

---

[View on GitHub](https://github.com/modal-labs/modal-examples/blob/main/13_sandboxes/simple_code_interpreter.py)

 

Copy page

# Build a stateful, sandboxed code interpreter

This example demonstrates how to build a stateful code interpreter using a Modal [Sandbox](https://modal.com/docs/guide/sandbox).

Weâll create a Modal Sandbox that listens for code to execute and then
executes the code in a Python interpreter. Because weâre running in a sandboxed
environment, we can safely use the âunsafeâ `exec()` to execute the code.

## Setting up a code interpreter in a Modal SandboxÂ

Our code interpreter uses a Python âdriver programâ to listen for code
sent in JSON format to its standard input (`stdin`), execute the code,
and then return the results in JSON format on standard output (`stdout`).

```
import inspect
import json
import sys
from typing import Any, Iterator

import modal

def driver_program():
    import json
    import sys
    from contextlib import redirect_stderr, redirect_stdout
    from io import StringIO

    # When you `exec` code in Python, you can pass in a dictionary
    # that defines the global variables the code has access to.

    # We'll use that to store state.

    globals: dict[str, Any] = {}
    while True:
        command = json.loads(input())  # read a line of JSON from stdin
        if (code := command.get("code")) is None:
            print(json.dumps({"error": "No code to execute"}))
            continue

        # Capture the executed code's outputs
        stdout_io, stderr_io = StringIO(), StringIO()
        with redirect_stdout(stdout_io), redirect_stderr(stderr_io):
            try:
                exec(code, globals)
            except Exception as e:
                print(f"Execution Error: {e}", file=sys.stderr)

        print(
            json.dumps(
                {"stdout": stdout_io.getvalue(), "stderr": stderr_io.getvalue()}
            ),
            flush=True,
        )
```

We run this driver program in a [Modal Sandbox](https://modal.com/docs/guide/sandboxes).

```
app = modal.App.lookup("example-simple-code-interpreter", create_if_missing=True)
sb = modal.Sandbox.create(app=app)
```

We have to convert the driver program to a string to pass it to the Sandbox.
Here we use `inspect.getsource` to get the source code as a string,
but you could also keep the driver program in a separate file and read it in.

```
driver_program_text = inspect.getsource(driver_program)
driver_program_command = f"""{driver_program_text}\n\ndriver_program()"""
```

We then kick off the program with [`Sandbox.exec`](https://modal.com/docs/reference/modal.Sandbox#exec),
which creates a process inside the Sandbox (see [`modal.container_process`](https://modal.com/docs/reference/modal.container_process) for details).

```
p = sb.exec("python", "-c", driver_program_command, bufsize=1)
```

 

## Running code in a Modal SandboxÂ

Now we need a way to run code inside that running driver process.
Our driver program already defined a JSON interface on its `stdin` and `stdout`,
so we just need to write a quick wrapper to write to the remote `stdin` and read from the remote `stdout`.

```
reader, writer = p.stdin, iter(p.stdout)

def run_code(writer: modal.io_streams.StreamWriter, reader: Iterator[str], code: str):
    writer.write(json.dumps({"code": code}) + "\n")
    writer.drain()
    result = json.loads(next(reader))
    print(result["stdout"], end="")
    if result["stderr"]:
        print("\033[91m" + result["stderr"] + "\033[0m", end="", file=sys.stderr)
```

Now we can execute some code in the Sandbox!

```
run_code(reader, writer, "print('hello, world!')")  # hello, world!
```

The Sandbox and our code interpreter are stateful,
so we can define variables and use them in subsequent code.

```
run_code(reader, writer, "x = 10")
run_code(reader, writer, "y = 5")
run_code(reader, writer, "result = x + y")
run_code(reader, writer, "print(f'The result is: {result}')")  # The result is: 15
```

We can also see errors when code fails.

```
run_code(reader, writer, "print('Attempting to divide by zero...')")
run_code(reader, writer, "1 / 0")  # Execution Error: division by zero
```

Finally, letâs clean up after ourselves and terminate the Sandbox.

```
sb.terminate()
```

[Build a stateful, sandboxed code interpreter](#build-a-stateful-sandboxed-code-interpreter)[Setting up a code interpreter in a Modal Sandbox](#setting-up-a-code-interpreter-in-a-modal-sandbox)[Running code in a Modal Sandbox](#running-code-in-a-modal-sandbox)

 

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
python 13_sandboxes/simple_code_interpreter.py
```