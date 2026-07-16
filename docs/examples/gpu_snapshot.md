# Snapshot GPU memory to speed up cold starts | Modal Docs

Source: https://modal.com/docs/examples/gpu_snapshot

---

---

[View on GitHub](https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/gpu_snapshot.py)

 

Copy page

# Snapshot GPU memory to speed up cold starts

This example demonstrates how to use GPU memory snapshots to speed up model loading.
Note that GPU memory snapshotting is an experimental feature,
so test carefully before using in production!
You can read more about GPU memory snapshotting, and its caveats, [here](https://modal.com/docs/guide/memory-snapshot).

GPU snapshots can only be used with deployed Functions, so first deploy the App:

```
modal deploy -m 06_gpu_and_ml.gpu_snapshot
```

Next, invoke the Function:

```
python -m 06_gpu_and_ml.gpu_snapshot
```

The full code is below:

```
import modal

image = modal.Image.debian_slim().uv_pip_install("sentence-transformers<6")
app_name = "example-gpu-snapshot"
app = modal.App(app_name, image=image)

snapshot_key = "v1"  # change this to invalidate the snapshot cache

with image.imports():  # import in the global scope so imports can be snapshot
    from sentence_transformers import SentenceTransformer

@app.cls(
    gpu="a10",
    enable_memory_snapshot=True,
    experimental_options={"enable_gpu_snapshot": True},
)
class SnapshotEmbedder:
    @modal.enter(snap=True)
    def load(self):
        # during enter phase of container lifecycle,
        # load the model onto the GPU so it can be snapshot
        print("loading model")
        self.model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cuda")
        print(f"snapshotting {snapshot_key}")

    @modal.method()
    def run(self, sentences: list[str]) -> list[list[float]]:
        # later invocations of the Function will start here
        embeddings = self.model.encode(sentences, normalize_embeddings=True)
        return embeddings.tolist()

if __name__ == "__main__":
    # after deployment, we can use the class from anywhere
    SnapshotEmbedder = modal.Cls.from_name(app_name, "SnapshotEmbedder")
    embedder = SnapshotEmbedder()
    try:
        print("calling Modal Function")
        print(embedder.run.remote(sentences=["what is the meaning of life?"]))
    except modal.exception.NotFoundError:
        raise Exception(
            f"To take advantage of GPU snapshots, deploy first with modal deploy {__file__}"
        )
```

[Snapshot GPU memory to speed up cold starts](#snapshot-gpu-memory-to-speed-up-cold-starts)

 

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
python 06_gpu_and_ml/gpu_snapshot.py
```