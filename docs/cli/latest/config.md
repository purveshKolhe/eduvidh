# modal config | Modal Docs

Source: https://modal.com/docs/cli/latest/config

---

---

Copy page

# `modal config`

Manage client configuration for the current profile.

Refer to <https://modal.com/docs/sdk/py/latest/modal.config> for a full explanation
of what these options mean, and how to set them.

**Usage**:

```
modal config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `set-environment`: Set the default Modal environment for the active profile
* `show`: Show current configuration values (debugging command).

## `modal config set-environment`Â

Set the default Modal environment for the active profile

The default environment of a profile is used when no âenv flag is passed to `modal run`, `modal deploy` etc.

If no default environment is set, and there exists multiple environments in a workspace, an error will be raised
when running a command that requires an environment.

**Usage**:

```
modal config set-environment [OPTIONS] ENVIRONMENT_NAME
```

**Options**:

* `--help`: Show this message and exit.

## `modal config show`Â

Show current configuration values (debugging command).

**Usage**:

```
modal config show [OPTIONS]
```

**Options**:

* `--redact / --no-redact`: Redact the `token_secret` value.
* `--help`: Show this message and exit.

[modal config](#modal-config)[modal config set-environment](#modal-config-set-environment)[modal config show](#modal-config-show)