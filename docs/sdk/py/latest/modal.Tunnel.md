# modal.Tunnel | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.Tunnel

---

---

Copy page

# modal.Tunnel

A port forwarded from within a running Modal container. Created by `modal.forward()`.

**Important:** This is an experimental API which may change in the future.

**Attributes**

host str

port int

unencrypted\_host str

unencrypted\_port int

 

## urlÂ

```
url(self)
```

Get the public HTTPS URL of the forwarded port.

## tls\_socketÂ

```
tls_socket(self)
```

Get the public TLS socket as a (host, port) tuple.

## tcp\_socketÂ

```
tcp_socket(self)
```

Get the public TCP socket as a (host, port) tuple.

[modal.Tunnel](#modaltunnel)[url](#url)[tls\_socket](#tls_socket)[tcp\_socket](#tcp_socket)