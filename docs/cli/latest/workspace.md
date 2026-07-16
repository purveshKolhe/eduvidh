# modal workspace | Modal Docs

Source: https://modal.com/docs/cli/latest/workspace

---

---

Copy page

# `modal workspace`

Interact with the current Modal Workspace.

A Workspace is the top-level account that owns your Modal resources. Use these commands
to manage workspace-level settings such as proxy tokens.

**Usage**:

```
modal workspace [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `members`: View the members of the current Workspace.
* `proxy-tokens`: Manage the proxy tokens of the current Workspace.
* `settings`: Manage workspace settings.

## `modal workspace members`Â

View the members of the current Workspace.

**Usage**:

```
modal workspace members [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List the members of the current Workspace.

### `modal workspace members list`Â

List the members of the current Workspace.

**Usage**:

```
modal workspace members list [OPTIONS]
```

**Options**:

* `--json`
* `--help`: Show this message and exit.

## `modal workspace proxy-tokens`Â

Manage the proxy tokens of the current Workspace.

Proxy tokens provide authentication to HTTP interfaces on Modal Servers and Web Functions.
They are passed as request headers (`Modal-Key` and `Modal-Secret`). See <https://modal.com/docs/guide/webhook-proxy-auth> for more information.

Proxy tokens and secrets have `wk-` and `ws-` prefixes, respectively. The cannot be
interchanged with API tokens (which use `ak-` and `as-` prefixes).

On workspaces with RBAC enabled, tokens are scoped to specific environments;
use the `allow` and `revoke` commands to manage environment associations.

**Usage**:

```
modal workspace proxy-tokens [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `allow`: Allow a proxy token to authenticate to an environment.
* `create`: Create a proxy token in the current Workspace.
* `delete`: Delete a proxy token from the current Workspace.
* `list`: List the proxy tokens of the current Workspace.
* `revoke`: Revoke a proxy tokenâs access to an environment.

### `modal workspace proxy-tokens allow`Â

Allow a proxy token to authenticate to an environment.

**Usage**:

```
modal workspace proxy-tokens allow [OPTIONS] TOKEN_ID ENVIRONMENT_NAME
```

**Options**:

* `--help`: Show this message and exit.

### `modal workspace proxy-tokens create`Â

Create a proxy token in the current Workspace.

**Usage**:

```
modal workspace proxy-tokens create [OPTIONS]
```

**Options**:

* `--json`
* `--help`: Show this message and exit.

### `modal workspace proxy-tokens delete`Â

Delete a proxy token from the current Workspace.

**Usage**:

```
modal workspace proxy-tokens delete [OPTIONS] TOKEN_ID
```

**Options**:

* `-y, --yes`: Run without pausing for confirmation.
* `--help`: Show this message and exit.

### `modal workspace proxy-tokens list`Â

List the proxy tokens of the current Workspace.

**Usage**:

```
modal workspace proxy-tokens list [OPTIONS]
```

**Options**:

* `-e, --environment TEXT`: Only list tokens associated with this environment. Lists all tokens when omitted.
* `--json`
* `--help`: Show this message and exit.

### `modal workspace proxy-tokens revoke`Â

Revoke a proxy tokenâs access to an environment.

**Usage**:

```
modal workspace proxy-tokens revoke [OPTIONS] TOKEN_ID ENVIRONMENT_NAME
```

**Options**:

* `--help`: Show this message and exit.

## `modal workspace settings`Â

Manage workspace settings. Must be workspace manager or owner.

**Usage**:

```
modal workspace settings [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: View the current settings for the workspace.
* `set`: Update a workspace setting.

### `modal workspace settings list`Â

View the current settings for the workspace.

**Usage**:

```
modal workspace settings list [OPTIONS]
```

**Options**:

* `--json`
* `--help`: Show this message and exit.

### `modal workspace settings set`Â

Update a workspace setting. Must be workspace manager or owner.

The following settings can be updated:

* `image-builder-version`: The image builder version determines the software included in our base images.
* `default-environment`: The default environment to use when the environment is omitted from SDK or CLI methods.

Usage:

* `modal workspace settings set image-builder-version 2025.06`
* `modal workspace settings set default-environment main`

**Usage**:

```
modal workspace settings set [OPTIONS] SETTING VALUE
```

**Options**:

* `--help`: Show this message and exit.

[modal workspace](#modal-workspace)[modal workspace members](#modal-workspace-members)[modal workspace members list](#modal-workspace-members-list)[modal workspace proxy-tokens](#modal-workspace-proxy-tokens)[modal workspace proxy-tokens allow](#modal-workspace-proxy-tokens-allow)[modal workspace proxy-tokens create](#modal-workspace-proxy-tokens-create)[modal workspace proxy-tokens delete](#modal-workspace-proxy-tokens-delete)[modal workspace proxy-tokens list](#modal-workspace-proxy-tokens-list)[modal workspace proxy-tokens revoke](#modal-workspace-proxy-tokens-revoke)[modal workspace settings](#modal-workspace-settings)[modal workspace settings list](#modal-workspace-settings-list)[modal workspace settings set](#modal-workspace-settings-set)