# modal.current_function_call_id | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.current_function_call_id

---

---

Copy page

# modal.current\_function\_call\_id

```
current_function_call_id()
```

Returns the function call ID for the current input.

Can only be called from Modal function (i.e. in a container context).

```
from modal import current_function_call_id

@app.function()
def process_stuff():
    print(f"Starting to process input from {current_function_call_id()}")
```

[modal.current\_function\_call\_id](#modalcurrent_function_call_id)