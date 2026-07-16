# modal dict | Modal Docs

Source: https://modal.com/docs/cli/latest/dict

---

---

Copy page

# `modal dict`

Manage `modal.Dict` objects and inspect their contents.

**Usage**:

```
modal dict [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clear`: Clear the contents of a named Dict by deleting all of its data.
* `create`: Create a named Dict object.
* `delete`: Delete a named Dict and all of its data.
* `get`: Print the value for a specific key.
* `items`: Print the contents of a Dict.
* `list`: List all named Dicts.

## `modal dict clear`Â

Clear the contents of a named Dict by deleting all of its data.

**Usage**:

```
modal dict clear [OPTIONS] NAME
```

**Options**:

* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal dict create`Â

Create a named Dict object.

Note: This is a no-op when the Dict already exists.

**Usage**:

```
modal dict create [OPTIONS] NAME
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal dict delete`Â

Delete a named Dict and all of its data.

**Usage**:

```
modal dict delete [OPTIONS] NAME
```

**Options**:

* `--allow-missing`: Donât error if the Dict doesnât exist.
* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal dict get`Â

Print the value for a specific key.

Note: When using the CLI, keys are always interpreted as having a string type.

**Usage**:

```
modal dict get [OPTIONS] NAME KEY
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal dict items`Â

Print the contents of a Dict.

Note: By default, this command truncates the contents. Use the `N` argument to control the
amount of data shown or the `--all` option to retrieve the entire Dict, which may be slow.

**Usage**:

```
modal dict items [OPTIONS] NAME [N]
```

**Options**:

* `-a, --all`: Ignore N and print all entries in the Dict (may be slow)
* `-r, --repr`: Display items using `repr()` to see more details
* `--json`
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal dict list`Â

List all named Dicts.

**Usage**:

```
modal dict list [OPTIONS]
```

**Options**:

* `--json`
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

[modal dict](#modal-dict)[modal dict clear](#modal-dict-clear)[modal dict create](#modal-dict-create)[modal dict delete](#modal-dict-delete)[modal dict get](#modal-dict-get)[modal dict items](#modal-dict-items)[modal dict list](#modal-dict-list)