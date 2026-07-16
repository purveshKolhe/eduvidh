# Run arbitrary code in a sandboxed environment | Modal Docs

Source: https://modal.com/docs/examples/safe_code_execution

---

---

[View on GitHub](https://github.com/modal-labs/modal-examples/blob/main/13_sandboxes/safe_code_execution.py)

 

Copy page

# Run arbitrary code in a sandboxed environment

This example demonstrates how to run arbitrary code
in multiple languages in a Modal [Sandbox](https://modal.com/docs/guide/sandbox).

## Setting up a multi-language environmentÂ

Sandboxes allow us to run any kind of code in a safe environment.
Weâll use an image with a few different language runtimes to demonstrate this.

```
import modal

image = modal.Image.debian_slim(python_version="3.11").apt_install(
    "nodejs", "ruby", "php"
)
app = modal.App.lookup("example-safe-code-execution", create_if_missing=True)
```

Weâll now create a Sandbox with this image. Weâll also enable output so we can see the image build
logs. Note that we donât pass any commands to the Sandbox, so it will stay alive, waiting for us
to send it commands.

```
with modal.enable_output():
    sandbox = modal.Sandbox.create(app=app, image=image)

print(f"Sandbox ID: {sandbox.object_id}")
```

 

## Running bash, Python, Node.js, Ruby, and PHP in a SandboxÂ

We can now use [`Sandbox.exec`](https://modal.com/docs/reference/modal.Sandbox#exec) to run a few different
commands in the Sandbox.

```
bash_ps = sandbox.exec("echo", "hello from bash")
python_ps = sandbox.exec("python", "-c", "print('hello from python')")
nodejs_ps = sandbox.exec("node", "-e", 'console.log("hello from nodejs")')
ruby_ps = sandbox.exec("ruby", "-e", "puts 'hello from ruby'")
php_ps = sandbox.exec("php", "-r", "echo 'hello from php';")

print(bash_ps.stdout.read(), end="")
print(python_ps.stdout.read(), end="")
print(nodejs_ps.stdout.read(), end="")
print(ruby_ps.stdout.read(), end="")
print(php_ps.stdout.read(), end="")
print()
```

The output should look something like

```
hello from bash
hello from python
hello from nodejs
hello from ruby
hello from php
```

We can use multiple languages in tandem to build complex applications.
Letâs demonstrate this by piping data between Python and Node.js using bash. Here
we generate some random numbers with Python and sum them with Node.js.

```
combined_process = sandbox.exec(
    "bash",
    "-c",
    """python -c 'import random; print(\" \".join(str(random.randint(1, 100)) for _ in range(10)))' |
    node -e 'const readline = require(\"readline\");
    const rl = readline.createInterface({input: process.stdin});
    rl.on(\"line\", (line) => {
      const sum = line.split(\" \").map(Number).reduce((a, b) => a + b, 0);
      console.log(`The sum of the random numbers is: ${sum}`);
      rl.close();
    });'""",
)

result = combined_process.stdout.read().strip()
print(result)
```

For long-running processes, you can use stdout as an iterator to stream the output.

```
slow_printer = sandbox.exec(
    "ruby",
    "-e",
    """
    10.times do |i|
      puts "Line #{i + 1}: #{Time.now}"
      STDOUT.flush
      sleep(0.5)
    end
    """,
)

for line in slow_printer.stdout:
    print(line, end="")
```

This should print something like

```
Line 1: 2024-10-21 15:30:53 +0000
Line 2: 2024-10-21 15:30:54 +0000
...
Line 10: 2024-10-21 15:30:58 +0000
```

Since Sandboxes are safely separated from the rest of our system,
we can run very dangerous code in them!

```
sandbox.exec("rm", "-rfv", "/", "--no-preserve-root")
```

This command has deleted the entire filesystem, so we canât run any more commands.
Letâs terminate the Sandbox to clean up after ourselves.

```
sandbox.terminate()
```

[Run arbitrary code in a sandboxed environment](#run-arbitrary-code-in-a-sandboxed-environment)[Setting up a multi-language environment](#setting-up-a-multi-language-environment)[Running bash, Python, Node.js, Ruby, and PHP in a Sandbox](#running-bash-python-nodejs-ruby-and-php-in-a-sandbox)

 

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
python 13_sandboxes/safe_code_execution.py
```