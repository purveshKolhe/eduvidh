# modal.method | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.method

---

---

Copy page

# modal.method

```
method(*, is_generator=None)
```

Decorator for methods that should be transformed into a Modal Function registered against this classâs App.

**Usage**

```
@app.cls(cpu=8)
class MyCls:

    @modal.method()
    def f(self):
        ...
```

[modal.method](#modalmethod)