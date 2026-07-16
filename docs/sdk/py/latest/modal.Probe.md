# modal.Probe | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.Probe

---

---

Copy page

# modal.Probe

Probe configuration for the Sandbox Readiness Probe.

**Usage**

```
# Wait until a file exists.
readiness_probe = modal.Probe.with_exec(
    "sh", "-c", "test -f /tmp/ready",
)

# Wait until a TCP port is accepting connections.
readiness_probe = modal.Probe.with_tcp(8080)

app = modal.App.lookup('sandbox-readiness-probe', create_if_missing=True)
sandbox = modal.Sandbox.create(
    "python3", "-m", "http.server", "8080",
    readiness_probe=readiness_probe,
    app=app,
)
sandbox.wait_until_ready()
```

**Attributes**

tcp\_port int | None

exec\_argv tuple[str, ...] | None

interval\_ms int

(Default is 100)

 

## with\_tcpÂ

```
with_tcp(cls, port, *, interval_ms=100)
```

 

## with\_execÂ

```
with_exec(cls, *argv, interval_ms=100)
```

[modal.Probe](#modalprobe)[with\_tcp](#with_tcp)[with\_exec](#with_exec)