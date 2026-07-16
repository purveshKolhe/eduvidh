# modal container | Modal Docs

Source: https://modal.com/docs/cli/latest/container

---

---

Copy page

# `modal container`

Manage and connect to running containers.

**Usage**:

```
modal container [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `exec`: Execute a command in a container.
* `list`: List all containers that are currently running.
* `logs`: Fetch or stream logs for a specific container.
* `stop`: Terminate a running container.

## `modal container exec`Â

Execute a command in a container.

**Usage**:

```
modal container exec [OPTIONS] CONTAINER_ID COMMAND...
```

**Options**:

* `--pty / --no-pty`: Run the command using a PTY.
* `--help`: Show this message and exit.

## `modal container list`Â

List all containers that are currently running.

**Usage**:

```
modal container list [OPTIONS]
```

**Options**:

* `--app-id TEXT`: List containers running for a specific App.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--json`
* `--help`: Show this message and exit.

## `modal container logs`Â

Fetch or stream logs for a specific container.

By default, this command fetches the last 100 log entries and exits. Use `-f` to
live-stream logs from a running container instead. Fetch and follow are mutually exclusive.

Examples:

Get recent logs for a container:

```
modal container logs ta-123456
```

Follow (stream) logs from a running container:

```
modal container logs ta-123456 -f
```

Fetch logs from the last 2 hours:

```
modal container logs ta-123456 --since 2h
```

Fetch logs in a specific time range:

```
modal container logs ta-123456 --since 2026-03-01T05:00:00 --until 2026-03-01T08:00:00
```

Fetch the last 1000 entries:

```
modal container logs ta-123456 --tail 1000
```

Fetch all container logs:

```
modal container logs ta-123456 --all
```

**Usage**:

```
modal container logs [OPTIONS] CONTAINER_ID
```

**Options**:

* `-f, --follow`: Stream log output until Container stops
* `--all`: Show all logs for the container
* `--since TEXT`: Start of time range. Accepts ISO 8601 datetime or relative time, e.g. â1dâ (1 day ago), â2hâ, â30mâ, etc.
* `--until TEXT`: End of time range; accepts same argument types as âsince
* `-n, --tail INTEGER`: Show only the last N log entries
* `--search TEXT`: Filter by search text
* `-s, --source TEXT`: Filter by source: âstdoutâ, âstderrâ, or âsystemâ
* `--timestamps`: Prefix each line with its timestamp
* `--help`: Show this message and exit.

## `modal container stop`Â

Terminate a running container.

By default, this will send the container a SIGINT signal that Modal will handle.
For Functions, any inputs that are currently running on the container will be cancelled
and rescheduled on other containers.

With `--graceful`, the container will be allowed to finish the inputs it is currently
running, exiting once they complete. Graceful stops are only supported for containers
running a Modal Function.

**Usage**:

```
modal container stop [OPTIONS] CONTAINER_ID
```

**Options**:

* `--graceful`: Let the container finish its current inputs before exiting, instead of cancelling them.
* `-y, --yes`: Run without pausing for confirmation.
* `--help`: Show this message and exit.

[modal container](#modal-container)[modal container exec](#modal-container-exec)[modal container list](#modal-container-list)[modal container logs](#modal-container-logs)[modal container stop](#modal-container-stop)