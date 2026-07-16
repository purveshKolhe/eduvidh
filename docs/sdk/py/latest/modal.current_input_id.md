# modal.current_input_id | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.current_input_id

---

---

Copy page

# modal.current\_input\_id

```
current_input_id()
```

Returns the input ID for the current input.

Can only be called from Modal function (i.e. in a container context).

```
from modal import current_input_id

@app.function()
def process_stuff():
    print(f"Starting to process {current_input_id()}")
```

[modal.current\_input\_id](#modalcurrent_input_id)