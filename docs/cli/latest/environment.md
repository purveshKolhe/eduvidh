# modal environment | Modal Docs

Source: https://modal.com/docs/cli/latest/environment

---

---

Copy page

# `modal environment`

Create and interact with Environments

Environments are sub-divisions of workspaces, allowing you to deploy the same app
in different namespaces. Each environment has their own set of Secrets and any
lookups performed from an app in an environment will by default look for entities
in the same environment.

Typical use cases for environments include having one for development and one for
production, to prevent overwriting production apps when developing new features
while still being able to deploy changes to a live environment.

**Usage**:

```
modal environment [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `billing`: View billing and usage info for the given Environment.
* `create`: Create a new environment in the current workspace.
* `delete`: Delete an environment in the current workspace.
* `list`: List all environments in the current workspace.
* `members`: Manage members and their roles in a restricted Environment.
* `update`: Update environment-level settings.

## `modal environment billing`Â

View billing and usage info for the given Environment.

**Usage**:

```
modal environment billing [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `report`: Generate a billing report for the specified Environment.

### `modal environment billing report`Â

Generate a billing report for the specified Environment.

The report range can be provided by setting `--start` / `--end` dates (`--end` defaults to ânowâ)
or by requesting a date range using `--for` (e.g., `--for today`, `--for 'last month'`).

This command provides a CLI frontend for the [`Environment.billing.report`](https://modal.com/docs/sdk/py/latest/modal.Environment#billingreport) API.

Note that, as with the API, the start date is inclusive and the end date is exclusive.
Data will be reported for full intervals only. Using `--for` is a convenient way to define a
complete interval.

In addition, the `--show-resources` option further breaks the cost in each bucket by the resource
that generated it (CPU, Memory, specific GPU types, etc.). Note that the specific resource types
included in the report are subject to change as Modalâs billing model evolves.

Examples:

```
modal environment billing report --start 2025-12-01 --end 2026-01-01

modal environment billing report --for "last month" --tag-names team,project

modal environment billing report test_env --for today --resolution h

modal environment billing report test_env --for "this month" --show-resources

modal environment billing report prod_env --for yesterday -r h --tz local

modal environment billing report main_env --for "last month" --csv > report.csv

modal environment billing report main_env --start 2025-12-01 --json > report.json
```

**Usage**:

```
modal environment billing report [OPTIONS] [ENVIRONMENT_NAME]
```

**Options**:

* `--start TEXT`: Start date. Date (in UTC by default): ISO format (2025-01-01) or relative (yesterday, 3 days ago, etc.).
* `--end TEXT`: End date. Date (in UTC by default): ISO format (2025-01-01) or relative (yesterday, 3 days ago, etc.). Defaults to now.
* `--for TEXT`: Convenience range: today, yesterday, this week, last week, this month, last month.
* `-r, --resolution TEXT`: Time resolution: âdâ (daily) or âhâ (hourly).
* `--tz TEXT`: Timezone for date interpretation: âlocalâ, offset (5, -4, +05:30), or IANA name. Requires hourly resolution.
* `-t, --tag-names TEXT`: Comma-separated list of tag names to include.
* `--show-resources`: Further break down usage by resource type.
* `--json`: Output as JSON.
* `--csv`: Output as CSV.
* `--help`: Show this message and exit.

## `modal environment create`Â

Create a new environment in the current workspace.

**Usage**:

```
modal environment create [OPTIONS] NAME
```

**Options**:

* `--restricted`: Enable RBAC restrictions on the new environment
* `--help`: Show this message and exit.

## `modal environment delete`Â

Delete an environment in the current workspace.

Deletes all apps in the selected environment and deletes the environment irrevocably.

**Usage**:

```
modal environment delete [OPTIONS] NAME
```

**Options**:

* `-y, --yes`: Run without pausing for confirmation.
* `--help`: Show this message and exit.

## `modal environment list`Â

List all environments in the current workspace.

**Usage**:

```
modal environment list [OPTIONS]
```

**Options**:

* `--json`
* `--help`: Show this message and exit.

## `modal environment members`Â

Manage members and their roles in a restricted Environment.

Restricted Environments use RBAC to limit the actions that can be performed by
users (and service users) based on roles: <https://modal.com/docs/guide/rbac>.

**Usage**:

```
modal environment members [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List the members of a restricted Environment
* `remove`: Remove a member from a restricted Environment
* `update`: Add or update a memberâs role in a restricted Environment

### `modal environment members list`Â

List the members of a restricted Environment

**Usage**:

```
modal environment members list [OPTIONS] ENVIRONMENT
```

**Options**:

* `--json`
* `--help`: Show this message and exit.

### `modal environment members remove`Â

Remove a member from a restricted Environment

**Usage**:

```
modal environment members remove [OPTIONS] ENVIRONMENT MEMBER
```

**Options**:

* `--service-user`: Treat MEMBER as the name of a service user
* `--help`: Show this message and exit.

### `modal environment members update`Â

Add or update a memberâs role in a restricted Environment

**Usage**:

```
modal environment members update [OPTIONS] ENVIRONMENT MEMBER
```

**Options**:

* `--role [contributor|viewer]`: Role to assign to the member [required]
* `--service-user`: Treat MEMBER as the name of a service user
* `--help`: Show this message and exit.

## `modal environment update`Â

Update environment-level settings.

**Usage**:

```
modal environment update [OPTIONS] CURRENT_NAME
```

**Options**:

* `--set-name TEXT`: New name of the environment
* `--set-web-suffix TEXT`: New web suffix of environment (empty string is no suffix)
* `--help`: Show this message and exit.

[modal environment](#modal-environment)[modal environment billing](#modal-environment-billing)[modal environment billing report](#modal-environment-billing-report)[modal environment create](#modal-environment-create)[modal environment delete](#modal-environment-delete)[modal environment list](#modal-environment-list)[modal environment members](#modal-environment-members)[modal environment members list](#modal-environment-members-list)[modal environment members remove](#modal-environment-members-remove)[modal environment members update](#modal-environment-members-update)[modal environment update](#modal-environment-update)