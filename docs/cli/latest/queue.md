# modal queue | Modal Docs

Source: https://modal.com/docs/cli/latest/queue

---

---

Copy page

# `modal queue`

Manage `modal.Queue` objects and inspect their contents.

**Usage**:

```
modal queue [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clear`: Clear the contents of a queue by removing all of its data.
* `create`: Create a named Queue.
* `delete`: Delete a named Queue and all of its data.
* `len`: Print the length of the queue or one of its partitions.
* `list`: List all named Queues.
* `peek`: Print the next N items without removing them.

## `modal queue clear`Â

Clear the contents of a queue by removing all of its data.

**Usage**:

```
modal queue clear [OPTIONS] NAME
```

**Options**:

* `-p, --partition TEXT`: Name of the partition to use, otherwise use the default (anonymous) partition.
* `-a, --all`: Clear the contents of all partitions.
* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal queue create`Â

Create a named Queue.

Note: This is a no-op when the Queue already exists.

**Usage**:

```
modal queue create [OPTIONS] NAME
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal queue delete`Â

Delete a named Queue and all of its data.

**Usage**:

```
modal queue delete [OPTIONS] NAME
```

**Options**:

* `--allow-missing`: Donât error if the Queue doesnât exist.
* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal queue len`Â

Print the length of the queue or one of its partitions.

**Usage**:

```
modal queue len [OPTIONS] NAME
```

**Options**:

* `-p, --partition TEXT`: Name of the partition to use, otherwise use the default (anonymous) partition.
* `-t, --total`: Compute the sum of the queue lengths across all partitions
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal queue list`Â

List all named Queues.

**Usage**:

```
modal queue list [OPTIONS]
```

**Options**:

* `--json`
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal queue peek`Â

Print the next N items without removing them.

**Usage**:

```
modal queue peek [OPTIONS] NAME [N]
```

**Options**:

* `-p, --partition TEXT`: Name of the partition to use, otherwise use the default (anonymous) partition.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

[modal queue](#modal-queue)[modal queue clear](#modal-queue-clear)[modal queue create](#modal-queue-create)[modal queue delete](#modal-queue-delete)[modal queue len](#modal-queue-len)[modal queue list](#modal-queue-list)[modal queue peek](#modal-queue-peek)