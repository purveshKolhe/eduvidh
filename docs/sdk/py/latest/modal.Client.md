# modal.Client | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.Client

---

---

Copy page

# modal.Client

```
class Client(object)
```

 

## is\_closedÂ

```
is_closed(self)
```

Check if the client is closed.

**Returns**

True if the client is closed, False otherwise.

## helloÂ

```
hello(self)
```

Connect to server and retrieve version information; raise appropriate error for various failures.

**Usage**

```
client = modal.Client.from_env()
client.hello()
```

 

## from\_credentialsÂ

```
from_credentials(cls, token_id, token_secret)
```

Constructor based on token credentials; useful for managing Modal on behalf of third-party users.

Also useful when itâs necessary to explicitly manage the lifecycle of the client
(e.g. when running Modal in a forked subprocess) â see [troubleshooting](/docs/guide/troubleshooting#connection-issues-in-forked-processes).

**Parameters**

token\_id str

API token ID.

token\_secret str

API token secret.

**Returns**

An authenticated `Client` with its connection opened.

**Usage**

```
client = modal.Client.from_credentials("my_token_id", "my_token_secret")

modal.Sandbox.create("echo", "hi", client=client, app=app)
```

 

## get\_input\_plane\_metadataÂ

```
get_input_plane_metadata(self, input_plane_region)
```

Get the metadata for the input plane.

**Parameters**

input\_plane\_region str

The region of the input plane.

**Returns**

The metadata for the input plane as a list of header/value tuples.

[modal.Client](#modalclient)[is\_closed](#is_closed)[hello](#hello)[from\_credentials](#from_credentials)[get\_input\_plane\_metadata](#get_input_plane_metadata)