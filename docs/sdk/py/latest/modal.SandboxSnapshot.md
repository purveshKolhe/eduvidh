# modal.SandboxSnapshot | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.SandboxSnapshot

---

---

Copy page

# modal.SandboxSnapshot

```
class SandboxSnapshot(modal.object.Object)
```

> Sandbox memory snapshots are in **early preview**.

A `SandboxSnapshot` object lets you interact with a stored Sandbox snapshot that was created by calling `._experimental_snapshot()` on a Sandbox instance. This includes both the filesystem and memory state of
the original Sandbox at the time the snapshot was taken.

## hydrateÂ

```
hydrate(self, client=None)
```

Synchronize the local object with its identity on the Modal server.

It is rarely necessary to call this method explicitly, as most operations
will lazily hydrate when needed. The main use case is when you need to
access object metadata, such as its ID.

*Added in v0.72.39*: This method replaces the deprecated `.resolve()` method.

## from\_idÂ

```
from_id(cls, sandbox_snapshot_id, client=None)
```

Construct a `SandboxSnapshot` for an existing snapshot ID.

**Parameters**

sandbox\_snapshot\_id str

Snapshot ID returned when the snapshot was created.

client "modal.client.Client | None"

Modal client to use; defaults to `Client.from_env()` when omitted.

**Returns**

A `SandboxSnapshot` handle (hydration validates the ID when used).

[modal.SandboxSnapshot](#modalsandboxsnapshot)[hydrate](#hydrate)[from\_id](#from_id)