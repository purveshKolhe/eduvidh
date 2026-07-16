# modal deploy | Modal Docs

Source: https://modal.com/docs/cli/latest/deploy

---

---

Copy page

# `modal deploy`

Deploy a Modal application.

Examples:
modal deploy my\_script.py
modal deploy -m my\_package.my\_mod

**Usage**:

```
modal deploy [OPTIONS] APP_REF
```

**Options**:

* `--name TEXT`: Name of the deployment.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--stream-logs`: Stream logs from the app upon deployment.
* `--tag TEXT`: Tag the deployment with a version.
* `-m`: Interpret argument as a Python module path instead of a file/script path
* `--timestamps`: Show timestamps for each log line.
* `--strategy [rolling|recreate]`: Deployment strategy
* `--help`: Show this message and exit.

[modal deploy](#modal-deploy)