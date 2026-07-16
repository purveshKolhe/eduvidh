# modal endpoint | Modal Docs

Source: https://modal.com/docs/cli/latest/endpoint

---

---

Copy page

# `modal endpoint`

Create and manage LLM inference endpoints.

Modal Endpoints deploy production-ready LLM inference servers with minimal coding or configuration.
Endpoints support pre-trained open models along with custom weights from a private Hugging Face repo
or Modal Volume.

See <https://modal.com/docs/guide/endpoints> for more information.

**Usage**:

```
modal endpoint [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Deploy a new Endpoint.
* `list`: List Endpoints that are provisioning or running in an environment.
* `stop`: Permanently stop an Endpoint and terminate any running containers.

## `modal endpoint create`Â

Deploy a new Endpoint.

Examples:

Create an Endpoint from a base model:

```
modal endpoint create --model Qwen/Qwen3.6-27B-FP8
```

Create an Endpoint with an explicit name:

```
modal endpoint create --name qwen-chat --model Qwen/Qwen3.6-27B-FP8
```

Create an Endpoint from a private Hugging Face model:

```
modal endpoint create --name my-ft --model Qwen/Qwen3.6-27B-FP8 \
  --custom-hf-repo acme/qwen-ft --custom-hf-token $HF_TOKEN
```

Create an Endpoint from custom weights in a Modal Volume:

```
modal endpoint create --name my-ft --model Qwen/Qwen3.6-27B-FP8 \
  --custom-volume-name qwen-ft --custom-volume-path /models/qwen
```

**Usage**:

```
modal endpoint create [OPTIONS]
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--name TEXT`: Endpoint name. If not provided, a default will be derived from the model name.
* `--model TEXT`: Hugging Face repo ID for the base model architecture (e.g., âQwen/Qwen3.6-27B-FP8â). [required]
* `--routing-region TEXT`: Region to route inference requests through. Defaults to us-west.
* `--colocate-compute`: Run all containers within the routing region. This incurs a region selection price multiplier.
* `--unauthenticated`: Allow unauthenticated HTTP requests to the endpoint.
* `--custom-hf-repo TEXT`: Hugging Face repo ID for fine-tuned model weights.
* `--custom-hf-revision TEXT`: Git revision for âcustom-hf-repo.
* `--custom-hf-token TEXT`: Hugging Face token for private âcustom-hf-repo.
* `--custom-volume-name TEXT`: Modal Volume name containing custom model weights.
* `--custom-volume-path TEXT`: Path within Volume containing model weights.
* `--help`: Show this message and exit.

## `modal endpoint list`Â

List Endpoints that are provisioning or running in an environment.

**Usage**:

```
modal endpoint list [OPTIONS]
```

**Options**:

* `--json`
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal endpoint stop`Â

Permanently stop an Endpoint and terminate any running containers.

**Usage**:

```
modal endpoint stop [OPTIONS] ENDPOINT_IDENTIFIER
```

**Options**:

* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

[modal endpoint](#modal-endpoint)[modal endpoint create](#modal-endpoint-create)[modal endpoint list](#modal-endpoint-list)[modal endpoint stop](#modal-endpoint-stop)