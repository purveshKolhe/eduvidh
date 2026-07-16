# modal.Cls | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.Cls

---

---

Copy page

# modal.Cls

```
class Cls(modal.object.Object)
```

Cls adds method pooling and [lifecycle hook](https://modal.com/docs/guide/lifecycle-functions) behavior
to [modal.Function](https://modal.com/docs/sdk/py/latest/modal.Function).

Generally, you will not construct a Cls directly.
Instead, use the [`@app.cls()`](https://modal.com/docs/sdk/py/latest/modal.App#cls) decorator on the App object.

## hydrateÂ

```
hydrate(self, client=None)
```

Synchronize the local object with its identity on the Modal server.

It is rarely necessary to call this method explicitly, as most operations
will lazily hydrate when needed. The main use case is when you need to
access object metadata, such as its ID.

*Added in v0.72.39*: This method replaces the deprecated `.resolve()` method.

## from\_nameÂ

```
from_name(cls, app_name, name, *, version=None, environment_name=None,
    client=None)
```

Reference a Cls from a deployed App by its name.

This is a lazy method that defers hydrating the local
object with metadata from Modal servers until the first
time it is actually used.

**Parameters**

app\_name str

Name of the deployed App that defines this class.

name str

Object tag of the Cls within that App.

environment\_name str | None

Workspace environment for the lookup; defaults to the active environment.

client "\_Client | None"

Optional Modal client; defaults to the process client.

**Returns**

A `Cls` reference that hydrates on first use.

**Usage**

```
Model = modal.Cls.from_name("other-app", "Model")
```

The `version` parameter constructs a version-pinned Cls:

```
Modelv3 = modal.Cls.from_name("other-app", "Model", version=3)
```

 

## with\_optionsÂ

```
with_options(self, *, cpu=None, memory=None, gpu=None, env=None, secrets=None,
    volumes={}, retries=None, max_containers=None, buffer_containers=None,
    scaledown_window=None, timeout=None, region=None, cloud=None,
    routing_region=None)
```

Override the static Cls configuration with invocation-specific values.

This method will return a new variant of the Cls that will autoscale independently of the
base configuration.

Note that options cannot be âunsetâ with this method (i.e., if a GPU is configured in the `@app.cls()` decorator, passing `gpu=None` here will not create a CPU-only instance).

Container arguments (`volumes` and `secrets`) from later calls replace earlier values; they are not merged.

**Parameters**

cpu float | tuple[float, float] | None

CPU cores for instances created from this Cls (see `@app.function` / `@app.cls` resource options).

memory int | tuple[int, int] | None

Memory in MiB, or min/max pair, for those instances.

gpu str | None

GPU type string, for example `A100`.

env dict[str, str | None] | None

Environment variables merged into a temporary secret for this configuration.

secrets Collection[\_Secret] | None

Additional secrets attached to the service function.

volumes dict[str | PurePosixPath, \_Volume | \_CloudBucketMount]

Volume and cloud-bucket mounts (paths to `Volume` or `CloudBucketMount`). (Default is {})

retries int | Retries | None

Retry policy or count for invocations.

max\_containers int | None

Cap on concurrently running containers for this Cls configuration.

buffer\_containers int | None

Extra idle containers kept warm while the Function is active.

scaledown\_window int | None

Seconds a container may stay idle before scaling down.

timeout int | None

Function timeout in seconds.

region str | Sequence[str] | None

One region or a list of regions to schedule on.

cloud str | None

Cloud provider (for example `aws`, `gcp`, `oci`, or `auto`).

routing\_region str | None

Region that inputs and outputs are routed through for this Cls.

**Returns**

A new `Cls` with the merged options.

**Usage**

You can use this method after looking up the Cls from a deployed App or if you have a
direct reference to a Cls from another Function or local entrypoint on its App:

```
Model = modal.Cls.from_name("my_app", "Model")
ModelUsingGPU = Model.with_options(gpu="A100")
ModelUsingGPU().generate.remote(input_prompt)  # Run with an A100 GPU
```

The method can be called multiple times to âstackâ updates:

```
Model.with_options(gpu="A100").with_options(scaledown_window=300)  # Use an A100 with slow scaledown
```

 

## with\_concurrencyÂ

```
with_concurrency(self, *, max_inputs, target_inputs=None)
```

Override the static Cls configuration with invocation-specific input concurrency settings.

**Parameters**

max\_inputs int

Maximum number of inputs processed concurrently per container.

target\_inputs int | None

Optional target concurrency; see `@app.cls` / Function concurrency docs.

**Returns**

A new `Cls` with the merged concurrency settings.

**Usage**

```
Model = modal.Cls.from_name("my_app", "Model")
ModelUsingGPU = Model.with_options(gpu="A100").with_concurrency(max_inputs=100)
ModelUsingGPU().generate.remote(42)  # will run on an A100 GPU with input concurrency enabled
```

 

## with\_batchingÂ

```
with_batching(self, *, max_batch_size, wait_ms)
```

Override the static Cls configuration with invocation-specific dynamic batching settings.

**Parameters**

max\_batch\_size int

Maximum batch size for dynamic batching.

wait\_ms int

Maximum time to wait to fill a batch, in milliseconds.

**Returns**

A new `Cls` with the merged batching settings.

**Usage**

```
Model = modal.Cls.from_name("my_app", "Model")
ModelUsingGPU = Model.with_options(gpu="A100").with_batching(max_batch_size=100, wait_ms=1000)
ModelUsingGPU().generate.remote(42)  # A100 with dynamic batching
```

[modal.Cls](#modalcls)[hydrate](#hydrate)[from\_name](#from_name)[with\_options](#with_options)[with\_concurrency](#with_concurrency)[with\_batching](#with_batching)