# modal.Queue | Modal Docs

Source: https://modal.com/docs/reference/modal.Queue

---

---

Copy page

# modal.Queue

```
class Queue(modal.object.Object)
```

Distributed, FIFO queue for data flow in Modal apps.

The queue can contain any object serializable by `cloudpickle`, including Modal objects.

By default, the `Queue` object acts as a single FIFO queue which supports puts and gets (blocking and non-blocking).

**Usage**

```
from modal import Queue

# Create an ephemeral queue which is anonymous and garbage collected
with Queue.ephemeral() as my_queue:
    # Putting values
    my_queue.put("some value")
    my_queue.put(123)

    # Getting values
    assert my_queue.get() == "some value"
    assert my_queue.get() == 123

    # Using partitions
    my_queue.put(0)
    my_queue.put(1, partition="foo")
    my_queue.put(2, partition="bar")

    # Default and "foo" partition are ignored by the get operation.
    assert my_queue.get(partition="bar") == 2

    # Set custom 10s expiration time on "foo" partition.
    my_queue.put(3, partition="foo", partition_ttl=10)

    # Iterate through items in place (read immutably)
    my_queue.put(1)
    assert [v for v in my_queue.iterate()] == [0, 1]

# You can also create persistent queues that can be used across apps
queue = Queue.from_name("my-persisted-queue", create_if_missing=True)
queue.put(42)
assert queue.get() == 42
```

For more examples, see the [guide](https://modal.com/docs/guide/dicts-and-queues#modal-queues).

**Queue partitions**

Specifying partition keys gives access to other independent FIFO partitions within the same `Queue` object.
Across any two partitions, puts and gets are completely independent.
For example, a put in one partition does not affect a get in any other partition.

When no partition key is specified (by default), puts and gets will operate on a default partition.
This default partition is also isolated from all other partitions.
Please see the Usage section below for an example using partitions.

**Lifetime of a queue and its partitions**

By default, each partition is cleared 24 hours after the last `put` operation.
A lower TTL can be specified by the `partition_ttl` argument in the `put` or `put_many` methods.
Each partitionâs expiry is handled independently.

As such, `Queue`s are best used for communication between active functions and not relied on for persistent
storage.

On app completion or after stopping an app any associated `Queue` objects are cleaned up.
All its partitions will be cleared.

**Limits**

A single `Queue` can contain up to 100,000 partitions, each with up to 5,000 items. Each item can be up to
1 MiB.

Partition keys must be non-empty and must not exceed 64 bytes.

## hydrateÂ

```
hydrate(self, client=None)
```

Synchronize the local object with its identity on the Modal server.

It is rarely necessary to call this method explicitly, as most operations
will lazily hydrate when needed. The main use case is when you need to
access object metadata, such as its ID.

*Added in v0.72.39*: This method replaces the deprecated `.resolve()` method.

## objectsÂ

```
objects: QueueManager
```

Namespace with methods for managing named Queue objects.

### objects.createÂ

```
create(self, name, *, allow_existing=False, environment_name=None, client=None)
```

Create a new named Queue in the workspace environment.

This does not return a local handle; use `modal.Queue.from_name` to look up the Queue after creation.

Added in v1.1.2.

**Parameters**

name str

Name for the new Queue.

allow\_existing bool

If True, do nothing when a Queue with this name already exists. (Default is False)

environment\_name str | None

Environment to create in; defaults to the active environment.

client \_Client | None

Modal client to use; defaults to `Client.from_env()` when omitted.

**Usage**

```
modal.Queue.objects.create("my-queue")
```

Queues will be created in the active environment, or another one can be specified:

```
modal.Queue.objects.create("my-queue", environment_name="dev")
```

By default, an error is raised if the Queue already exists; `allow_existing=True` makes that case a no-op:

```
modal.Queue.objects.create("my-queue", allow_existing=True)
```

Note that this method does not return a local instance of the Queue. You can use `modal.Queue.from_name` to perform a lookup after creation.

### objects.listÂ

```
list(self, *, max_objects=None, created_before=None, environment_name="",
    client=None)
```

List named Queues in the workspace environment as hydrated handles.

Results are ordered newest to oldest. By default, all matching Queues are returned.

Added in v1.1.2.

**Parameters**

max\_objects int | None

Maximum number of Queues to return.

created\_before datetime | str | None

Only include Queues created before this time (datetime or ISO date string).

environment\_name str

Environment to list from; defaults to the active environment. (Default is "")

client \_Client | None

Modal client to use; defaults to `Client.from_env()` when omitted.

**Returns**

Hydrated `Queue` objects for each named Queue in the listing.

**Usage**

```
queues = modal.Queue.objects.list()
print([q.name for q in queues])
```

Queues will be retrieved from the active environment, or another one can be specified:

```
dev_queues = modal.Queue.objects.list(environment_name="dev")
```

By default, all named Queues are returned, newest to oldest. Itâs also possible to limit the
number of results and to filter by creation date:

```
queues = modal.Queue.objects.list(max_objects=10, created_before="2025-01-01")
```

 

### objects.deleteÂ

```
delete(self, name, *, allow_missing=False, environment_name=None, client=None)
```

Delete a named Queue entirely (not a single message or partition).

Deletion is irreversible and affects any Apps using this Queue.

Added in v1.1.2.

**Parameters**

name str

Name of the Queue to delete.

allow\_missing bool

If True, do nothing when the Queue does not exist. (Default is False)

environment\_name str | None

Environment to delete from; defaults to the active environment.

client \_Client | None

Modal client to use; defaults to `Client.from_env()` when omitted.

**Usage**

```
await modal.Queue.objects.delete("my-queue")
```

Queues will be deleted from the active environment, or another one can be specified:

```
await modal.Queue.objects.delete("my-queue", environment_name="dev")
```

 

## nameÂ

```
name(self)
```

 

## validate\_partition\_keyÂ

```
validate_partition_key(partition)
```

 

## ephemeralÂ

```
ephemeral(cls, client=None, environment_name=None)
```

Create an anonymous Queue that exists for the duration of the context manager.

**Parameters**

client \_Client | None

Modal client to use; defaults to `Client.from_env()` when omitted.

environment\_name str | None

Environment for the ephemeral Queue; defaults to the active environment.

**Usage**

```
from modal import Queue

with Queue.ephemeral() as q:
    q.put(123)
```

```
async with Queue.ephemeral() as q:
    await q.put.aio(123)
```

 

## from\_nameÂ

```
from_name(name, *, environment_name=None, create_if_missing=False, client=None)
```

Reference a named Queue, optionally creating it on the server first.

Hydration is lazy: metadata is fetched from Modal the first time the handle is used.

**Parameters**

name str

Deployment name of the Queue.

environment\_name str | None

Environment to resolve the name in; defaults to the active environment.

create\_if\_missing bool

If True, create the Queue when it does not already exist. (Default is False)

client \_Client | None

Modal client to use for loading; defaults to `Client.from_env()` when omitted.

**Returns**

A `Queue` handle (possibly not yet hydrated).

**Usage**

```
q = modal.Queue.from_name("my-queue", create_if_missing=True)
q.put(123)
```

 

## from\_idÂ

```
from_id(queue_id, client=None)
```

Construct a Queue from an id and look up the Queue metadata.

This is a lazy method that defers hydrating the local
object with metadata from Modal servers until the first
time it is actually used.

The ID of a Queue object can be accessed using `.object_id`.

**Parameters**

queue\_id str

Queue object ID to attach to.

client \_Client | None

Modal client to use for loading; defaults to `Client.from_env()` when omitted.

**Returns**

A `Queue` handle (possibly not yet hydrated).

**Usage**

```
@app.function()
def my_consumer(queue_id: str):
    queue = modal.Queue.from_id(queue_id)
    queue.put("Hello from remote function!")

with modal.Queue.ephemeral() as q:
    my_consumer.remote(q.object_id)
    print(q.get())  # "Hello from remote function!"
```

 

## infoÂ

```
info(self)
```

Return information about the Queue object.

## clearÂ

```
clear(self, *, partition=None, all=False)
```

Clear the contents of a single partition or all partitions.

Warning: this is a destructive operation and will irrevocably delete data.

**Parameters**

partition str | None

Partition to clear; omit with `all=True` to clear every partition.

all bool

If True, clear all partitions (`partition` must not be set). (Default is False)

**Usage**

```
q = modal.Queue.from_name("my-queue", create_if_missing=True)
q.clear()
```

 

## getÂ

```
get(self, block=True, timeout=None, *, partition=None)
```

Remove and return the next object in the queue.

If `block` is `True` (the default) and the queue is empty, `get` will wait indefinitely for
an object, or until `timeout` if specified. Raises a native `queue.Empty` exception
if the `timeout` is reached.

If `block` is `False`, `get` returns `None` immediately if the queue is empty. The `timeout` is
ignored in this case.

**Parameters**

block bool

If True, wait for an item; if False, return `None` immediately when empty. (Default is True)

timeout float | None

Seconds to wait when blocking; ignored when `block` is False.

partition str | None

FIFO partition to read from; uses the default partition when omitted.

 

## get\_manyÂ

```
get_many(self, n_values, block=True, timeout=None, *, partition=None)
```

Remove and return up to `n_values` objects from the queue.

If there are fewer than `n_values` items in the queue, return all of them.

If `block` is `True` (the default) and the queue is empty, `get_many` waits until at least one
object is present, or until `timeout` if specified. Raises the stdlibâs `queue.Empty` if the
timeout is reached before any item arrives.

If `block` is `False`, this returns an empty list immediately when the queue is empty. The `timeout` is ignored in that case.

**Parameters**

n\_values int

Maximum number of items to remove and return.

block bool

If True, wait until at least one item is available (or until `timeout`); if False, return immediately when empty. (Default is True)

timeout float | None

Seconds to wait when blocking; ignored when `block` is False.

partition str | None

FIFO partition to read from; uses the default partition when omitted.

 

## putÂ

```
put(self, v, block=True, timeout=None, *, partition=None, partition_ttl=24 *
    3600)
```

Add an object to the end of the queue.

If `block` is `True` and the queue is full, this method will retry indefinitely or
until `timeout` if specified. Raises the stdlibâs `queue.Full` exception if the `timeout` is reached.
If blocking it is not recommended to omit the `timeout`, as the operation could wait indefinitely.

If `block` is `False`, this method raises `queue.Full` immediately if the queue is full. The `timeout` is
ignored in this case.

**Parameters**

v Any

Value to enqueue (must be serializable).

block bool

If True, wait for capacity; if False, fail immediately when full. (Default is True)

timeout float | None

Max seconds to wait when blocking.

partition str | None

FIFO partition to write to; uses the default partition when omitted.

partition\_ttl int

Seconds after the last activity before this partition may be cleared (default 24 hours). (Default is 24 \* 3600)

 

## put\_manyÂ

```
put_many(self, vs, block=True, timeout=None, *, partition=None, partition_ttl=24
    * 3600)
```

Add several objects to the end of the queue.

If `block` is `True` and the queue is full, this method will retry indefinitely or
until `timeout` if specified. Raises the stdlibâs `queue.Full` exception if the `timeout` is reached.
If blocking it is not recommended to omit the `timeout`, as the operation could wait indefinitely.

If `block` is `False`, this method raises `queue.Full` immediately if the queue is full. The `timeout` is
ignored in this case.

**Parameters**

vs list[Any]

Values to enqueue (each must be serializable).

block bool

If True, wait for capacity; if False, fail immediately when full. (Default is True)

timeout float | None

Max seconds to wait when blocking.

partition str | None

FIFO partition to write to; uses the default partition when omitted.

partition\_ttl int

Seconds after the last activity before this partition may be cleared (default 24 hours). (Default is 24 \* 3600)

 

## lenÂ

```
len(self, *, partition=None, total=False)
```

Return the number of objects in the queue partition.

**Parameters**

partition str | None

Partition to measure; omit for the default partition.

total bool

If True, return the combined length of all partitions (do not pass `partition`). (Default is False)

**Returns**

Item count (capped by the server when very large).

## iterateÂ

```
iterate(self, *, partition=None, item_poll_timeout=0.0)
```

Iterate through items in the queue without mutation.

Specify `item_poll_timeout` to control how long the iterator should wait for the next time before giving up.

**Parameters**

partition str | None

Partition to scan; uses the default partition when omitted.

item\_poll\_timeout float

How long to wait for another item before stopping the iterator. (Default is 0.0)

[modal.Queue](#modalqueue)[hydrate](#hydrate)[objects](#objects)[create](#objectscreate)[list](#objectslist)[delete](#objectsdelete)[name](#name)[validate\_partition\_key](#validate_partition_key)[ephemeral](#ephemeral)[from\_name](#from_name)[from\_id](#from_id)[info](#info)[clear](#clear)[get](#get)[get\_many](#get_many)[put](#put)[put\_many](#put_many)[len](#len)[iterate](#iterate)