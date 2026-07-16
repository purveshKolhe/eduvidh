# modal.FunctionCall | Modal Docs

Source: https://modal.com/docs/reference/modal.FunctionCall

---

---

Copy page

# modal.FunctionCall

```
class FunctionCall(typing.Generic, modal.object.Object)
```

A reference to an executed function call.

Constructed using `.spawn(...)` on a Modal function with the same
arguments that a function normally takes. Acts as a reference to
an ongoing function call that can be passed around and used to
poll or fetch function results at some later time.

Conceptually similar to a Future/Promise/AsyncResult in other contexts and languages.

## hydrateÂ

```
hydrate(self, client=None)
```

Synchronize the local object with its identity on the Modal server.

It is rarely necessary to call this method explicitly, as most operations
will lazily hydrate when needed. The main use case is when you need to
access object metadata, such as its ID.

*Added in v0.72.39*: This method replaces the deprecated `.resolve()` method.

## num\_inputsÂ

```
num_inputs(self)
```

Get the number of inputs in the function call.

**Returns**

How many inputs this function call includes (e.g. `1` for `.spawn()`, more for `.spawn_map()`).

## getÂ

```
get(self, timeout=None, *, index=0)
```

Get the result of the index-th input of the function call.

`.spawn()` calls have a single output, so only specifying `index=0` is valid.
A non-zero index is useful when your function has multiple outputs, like via `.spawn_map()`.

This function waits indefinitely by default. It takes an optional `timeout` argument that specifies the maximum number of seconds to wait,
which can be set to `0` to poll for an output immediately.

The returned coroutine is not cancellation-safe.

**Parameters**

timeout float | None

Maximum seconds to wait for a result, or `None` to wait indefinitely.

index int

Which input's result to retrieve (typically `0` for `.spawn()`). (Default is 0)

**Returns**

The deserialized return value from that input.

## iterÂ

```
iter(self, *, start=0, end=None)
```

Iterate in-order over the results of the function call.

Optionally, specify a range [start, end) to iterate over.

If `end` is not provided, it will iterate over all results.

**Parameters**

start int

First input index to include (inclusive). (Default is 0)

end int | None

One past the last index to include, or `None` for all remaining inputs.

**Returns**

Each result value in index order.

**Usage**

```
@app.function()
def my_func(a):
    return a ** 2

@app.local_entrypoint()
def main():
    fc = my_func.spawn_map([1, 2, 3, 4])
    assert list(fc.iter()) == [1, 4, 9, 16]
    assert list(fc.iter(start=1, end=3)) == [4, 9]
```

 

## get\_call\_graphÂ

```
get_call_graph(self)
```

Returns a structure representing the call graph from a given root
call ID, along with the status of execution for each node.

See [`modal.call_graph`](https://modal.com/docs/sdk/py/latest/modal.call_graph) reference page
for documentation on the structure of the returned `InputInfo` items.

**Returns**

A list of `InputInfo` nodes describing the call graph.

## cancelÂ

```
cancel(self, terminate_containers=False)
```

Cancels the function call, which will stop its execution and mark its inputs as [`TERMINATED`](https://modal.com/docs/sdk/py/latest/modal.call_graph#modalcall_graphinputstatus).

If `terminate_containers=True` - the containers running the cancelled inputs are all terminated
causing any non-cancelled inputs on those containers to be rescheduled in new containers.

**Parameters**

terminate\_containers bool

If True, forcibly terminate workers running cancelled inputs. (Default is False)

 

## from\_idÂ

```
from_id(cls, function_call_id, client=None)
```

Instantiate a FunctionCall object from an existing ID.

Note that itâs only necessary to re-instantiate the `FunctionCall` with this method
if you no longer have access to the original object returned from `Function.spawn`.

**Parameters**

function\_call\_id str

Object ID of an existing function call (e.g. from `FunctionCall.object_id`).

client "modal.client.Client | None"

Modal client to use; defaults to `Client.from_env()` when omitted.

**Returns**

A `FunctionCall` handle for the given ID.

**Usage**

```
# Spawn a FunctionCall and keep track of its object ID
fc = my_func.spawn()
fc_id = fc.object_id

# Later, use the ID to re-instantiate the FunctionCall object
fc = FunctionCall.from_id(fc_id)
result = fc.get()
```

 

## gatherÂ

```
gather(*function_calls)
```

Wait until all Modal FunctionCall objects have results before returning.

Accepts a variable number of `FunctionCall` objects, as returned by `Function.spawn()`.

Raises an exception from the first failing function call.

*Added in v0.73.69*: This method replaces the deprecated `modal.functions.gather` function.

**Parameters**

\*function\_calls "\_FunctionCall[T]"

`FunctionCall` instances to wait on (same order as the returned sequence).

**Returns**

Results in the same order as `function_calls` (like `asyncio.gather`).

**Usage**

```
fc1 = slow_func_1.spawn()
fc2 = slow_func_2.spawn()

result_1, result_2 = modal.FunctionCall.gather(fc1, fc2)
```

[modal.FunctionCall](#modalfunctioncall)[hydrate](#hydrate)[num\_inputs](#num_inputs)[get](#get)[iter](#iter)[get\_call\_graph](#get_call_graph)[cancel](#cancel)[from\_id](#from_id)[gather](#gather)