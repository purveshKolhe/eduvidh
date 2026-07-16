# Dicts | Modal Docs

Source: https://modal.com/docs/guide/dicts

---

---

Copy page

# Dicts

Modal Dicts provide distributed key-value storage to your Modal Apps.

```
import modal

app = modal.App()
kv = modal.Dict.from_name("kv", create_if_missing=True)

@app.local_entrypoint()
def main(key="cloud", value="dictionary", put=True):
    if put:
        kv[key] = value
    print(f"{key}: {kv[key]}")
```

This page is a high-level guide to using Modal Dicts.
For reference documentation on the `modal.Dict` object, see [this page](/docs/sdk/py/latest/modal.Dict).
For reference documentation on the `modal dict` CLI command, see [this page](/docs/cli/latest/dict).

## Modal Dicts are Python dicts in the cloudÂ

Dicts provide distributed key-value storage to your Modal Apps.
Much like a standard Python dictionary, a Dict lets you store and retrieve
values using keys. However, unlike a regular dictionary, a Dict in Modal is
accessible from anywhere, concurrently and in parallel.

```
# create a remote Dict
dictionary = modal.Dict.from_name("my-dict", create_if_missing=True)

dictionary["key"] = "value"  # set a value from anywhere
value = dictionary["key"]    # get a value from anywhere
```

Dicts are persisted, which means that the data in the dictionary is
stored and can be retrieved even after the application is redeployed.

## You can access Modal Dicts asynchronouslyÂ

Modal Dicts live in the cloud, which means reads and writes
against them go over the network. That has some unavoidable latency overhead,
relative to just reading from memory, of a few dozen ms.
Reads from Dicts via `["key"]`-style indexing are synchronous,
which means that latency is often directly felt by the application.

But like all Modal objects, you can also interact with Dicts asynchronously
by putting the `.aio` suffix on methods â in this case, `put` and `get`,
which are synonyms for bracket-based indexing.
Just add the `async` keyword to your `local_entrypoint`s or remote Functions
and `await` the method calls.

```
import modal

app = modal.App()
dictionary = modal.Dict.from_name("async-dict", create_if_missing=True)

@app.local_entrypoint()
async def main():
    await dictionary.put.aio("key", "value")  # setting a value asynchronously
    assert await dictionary.get.aio("key")   # getting a value asynchronously
```

See the guide to [asynchronous functions](/docs/guide/async) for more
information.

## Modal Dicts are not *exactly* Python dictsÂ

Python dicts can have keys of any hashable type and values of any type.

You can store Python objects of any serializable type within Dicts as keys or values.

Objects are serialized using [`cloudpickle`](https://github.com/cloudpipe/cloudpickle),
so precise support is inherited from that library. `cloudpickle` can serialize a surprising variety of objects,
like `lambda` functions or even Python modules, but it canât serialize a few things that donât
really make sense to serialize, like live system resources (sockets, writable file descriptors).

Note that you will need to have the library defining the type installed in the environment
where you retrieve the object so that it can be deserialized.

Unlike with normal Python dictionaries, updates to mutable value types will not
be reflected in other containers unless the updated object is explicitly put
back into the Dict. As a consequence, patterns like chained updates
(`my_dict["outer_key"]["inner_key"] = value`) cannot be used the same way as
they would with a local dictionary.

Currently, the per-object size limit is 100 MiB and the maximum number of entries
per update is 10,000. Itâs recommended to use Dicts for smaller objects (under 5 MiB).
Each object in the Dict will expire after 7 days of inactivity (no reads or writes).

Dicts also provide a locking primitive. See [this blog post](/blog/cache-dict-launch) for details.

[Dicts](#dicts)[Modal Dicts are Python dicts in the cloud](#modal-dicts-are-python-dicts-in-the-cloud)[You can access Modal Dicts asynchronously](#you-can-access-modal-dicts-asynchronously)[Modal Dicts are not exactly Python dicts](#modal-dicts-are-not-exactly-python-dicts)

See it in action

[Use Dicts and Queues to coordinate a web scraper](/docs/examples/dicts_and_queues)

[Store 100k checkboxes in a Dict](/docs/examples/fasthtml_checkboxes)