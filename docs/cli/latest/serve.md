# modal serve | Modal Docs

Source: https://modal.com/docs/cli/latest/serve

---

---

Copy page

# `modal serve`

Expose Web Functions with hot-reloading on code changes.

Examples:

```
modal serve hello_world.py
```

Modal-generated URLs will have a `-dev` suffix appended to them when running with `modal serve`.
To customize this suffix (i.e., to avoid collisions with other users in your workspace who are
concurrently serving the App), you can set the `dev_suffix` in your `.modal.toml` file or the
`MODAL_DEV_SUFFIX` environment variable.

**Usage**:

```shell
modal serve [OPTIONS] APP_REF
```

**Options**:

* `-n, --name TEXT`: Name for this run of the App.
* `--timeout FLOAT`
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `-m`: Interpret argument as a Python module path instead of a file/script path
* `--timestamps`: Show timestamps for each log line.
* `--help`: Show this message and exit.

[modal serve](#modal-serve)