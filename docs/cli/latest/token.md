# modal token | Modal Docs

Source: https://modal.com/docs/cli/latest/token

---

---

Copy page

# `modal token`

Manage tokens.

**Usage**:

```
modal token [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `info`: Display information about the token that is currently in use.
* `new`: Create a new token by using an authenticated web session.
* `set`: Set account credentials for connecting to Modal.

## `modal token info`Â

Display information about the token that is currently in use.

**Usage**:

```
modal token info [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `modal token new`Â

Create a new token by using an authenticated web session.

**Usage**:

```
modal token new [OPTIONS]
```

**Options**:

* `--profile TEXT`: Modal profile to set credentials for. If unspecified (and MODAL\_PROFILE environment variable is not set), uses the workspace name associated with the credentials.
* `--activate / --no-activate`: Activate the profile containing this token after creation.
* `--verify / --no-verify`: Make a test request to verify the new credentials.
* `--help`: Show this message and exit.

## `modal token set`Â

Set account credentials for connecting to Modal.

If the credentials are not provided on the command line, you will be prompted to enter them.

**Usage**:

```
modal token set [OPTIONS]
```

**Options**:

* `--token-id TEXT`: Account token ID.
* `--token-secret TEXT`: Account token secret.
* `--profile TEXT`: Modal profile to set credentials for. If unspecified (and MODAL\_PROFILE environment variable is not set), uses the workspace name associated with the credentials.
* `--activate / --no-activate`: Activate the profile containing this token after creation.
* `--verify / --no-verify`: Make a test request to verify the new credentials.
* `--help`: Show this message and exit.

[modal token](#modal-token)[modal token info](#modal-token-info)[modal token new](#modal-token-new)[modal token set](#modal-token-set)