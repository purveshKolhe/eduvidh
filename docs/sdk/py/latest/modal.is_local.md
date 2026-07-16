# modal.is_local | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.is_local

---

---

Copy page

# modal.is\_local

```
is_local()
```

Indicate the execution context of the current process.

Note: this function specifically returns False when the current process is
running a Modal Function and True in all other cases. It will return True
when called from a child process of a Function or inside a Modal Sandbox,
even though those processes are running on Modal hardware.

[modal.is\_local](#modalis_local)