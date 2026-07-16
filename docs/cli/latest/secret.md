# modal secret | Modal Docs

Source: https://modal.com/docs/cli/latest/secret

---

---

Copy page

# `modal secret`

Manage secrets.

**Usage**:

```
modal secret [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new secret.
* `delete`: Delete a named Secret.
* `list`: List your published secrets.

## `modal secret create`Â

Create a new secret.

**Usage**:

```
modal secret create [OPTIONS] SECRET_NAME [KEYVALUES]...
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--from-dotenv PATH`: Path to a .env file to load secrets from.
* `--from-json PATH`: Path to a JSON file to load secrets from.
* `--force`: Overwrite the secret if it already exists.
* `--help`: Show this message and exit.

## `modal secret delete`Â

Delete a named Secret.

**Usage**:

```
modal secret delete [OPTIONS] NAME
```

**Options**:

* `--allow-missing`: Donât error if the Secret doesnât exist.
* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal secret list`Â

List your published secrets.

**Usage**:

```
modal secret list [OPTIONS]
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--json`
* `--help`: Show this message and exit.

[modal secret](#modal-secret)[modal secret create](#modal-secret-create)[modal secret delete](#modal-secret-delete)[modal secret list](#modal-secret-list)