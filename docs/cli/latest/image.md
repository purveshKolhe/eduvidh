# modal image | Modal Docs

Source: https://modal.com/docs/cli/latest/image

---

---

Copy page

# `modal image`

Manage Images.

**Usage**:

```
modal image [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `names`: Manage Modal Image names.

## `modal image names`Â

Manage Modal Image names.

**Usage**:

```
modal image names [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List named Images.

### `modal image names list`Â

List named Images.

**Usage**:

```
modal image names list [OPTIONS]
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--prefix TEXT`: Only include named image tags that start with this prefix.
* `--json`
* `--help`: Show this message and exit.

[modal image](#modal-image)[modal image names](#modal-image-names)[modal image names list](#modal-image-names-list)