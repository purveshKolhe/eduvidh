# modal volume | Modal Docs

Source: https://modal.com/docs/cli/latest/volume

---

---

Copy page

# `modal volume`

Read and edit `modal.Volume` volumes.

Note: users of `modal.NetworkFileSystem` should use the `modal nfs` command instead.

**Usage**:

```
modal volume [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `cp`: Copy within a modal.Volume.
* `create`: Create a named, persistent modal.Volume.
* `dashboard`: Open the Volumeâs dashboard page in your web browser.
* `delete`: Delete a named Volume and all of its data.
* `get`: Download files from a modal.Volume object.
* `list`: List the details of all modal.Volume volumes in an Environment.
* `ls`: List files and directories in a modal.Volume volume.
* `put`: Upload a file or directory to a modal.Volume.
* `rename`: Rename a modal.Volume.
* `rm`: Delete a file or directory from a modal.Volume.

## `modal volume cp`Â

Copy within a modal.Volume.

Copy source file to destination file or multiple source files to destination directory.

**Usage**:

```
modal volume cp [OPTIONS] VOLUME_NAME PATHS...
```

**Options**:

* `-r, --recursive`: Copy directories recursively
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal volume create`Â

Create a named, persistent modal.Volume.

**Usage**:

```
modal volume create [OPTIONS] NAME
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--version INTEGER`: VolumeFS version. (Experimental)
* `--help`: Show this message and exit.

## `modal volume dashboard`Â

Open the Volumeâs dashboard page in your web browser.

**Usage**:

```
modal volume dashboard [OPTIONS] VOLUME_NAME
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal volume delete`Â

Delete a named Volume and all of its data.

**Usage**:

```
modal volume delete [OPTIONS] NAME
```

**Options**:

* `--allow-missing`: Donât error if the Volume doesnât exist.
* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal volume get`Â

Download files from a modal.Volume object.

If a folder is passed for REMOTE\_PATH, the contents of the folder will be downloaded
recursively, including all subdirectories.

Examples:

```
modal volume get <volume_name> logs/april-12-1.txt
modal volume get <volume_name> / volume_data_dump
```

Use "-" as LOCAL_DESTINATION to write file contents to standard output.

**Usage**:

```shell
modal volume get [OPTIONS] VOLUME_NAME REMOTE_PATH [LOCAL_DESTINATION]
```

**Options**:

* `--force`
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal volume list`Â

List the details of all modal.Volume volumes in an Environment.

**Usage**:

```
modal volume list [OPTIONS]
```

**Options**:

* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--json`
* `--help`: Show this message and exit.

## `modal volume ls`Â

List files and directories in a modal.Volume volume.

**Usage**:

```
modal volume ls [OPTIONS] VOLUME_NAME [PATH]
```

**Options**:

* `--json`
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal volume put`Â

Upload a file or directory to a modal.Volume.

Remote parent directories will be created as needed.

Ending the REMOTE\_PATH with a forward slash (/), itâs assumed to be a directory
and the file will be uploaded with its current name under that directory.

**Usage**:

```
modal volume put [OPTIONS] VOLUME_NAME LOCAL_PATH [REMOTE_PATH]
```

**Options**:

* `-f, --force`: Overwrite existing files.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal volume rename`Â

Rename a modal.Volume.

**Usage**:

```
modal volume rename [OPTIONS] OLD_NAME NEW_NAME
```

**Options**:

* `-y, --yes`: Run without pausing for confirmation.
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

## `modal volume rm`Â

Delete a file or directory from a modal.Volume.

**Usage**:

```
modal volume rm [OPTIONS] VOLUME_NAME REMOTE_PATH
```

**Options**:

* `-r, --recursive`: Delete directory recursively
* `-e, --env TEXT`: Environment to interact with. If unspecified, defers to `MODAL_ENVIRONMENT`, your active local profile, or your workspace default, in that order.
* `--help`: Show this message and exit.

[modal volume](#modal-volume)[modal volume cp](#modal-volume-cp)[modal volume create](#modal-volume-create)[modal volume dashboard](#modal-volume-dashboard)[modal volume delete](#modal-volume-delete)[modal volume get](#modal-volume-get)[modal volume list](#modal-volume-list)[modal volume ls](#modal-volume-ls)[modal volume put](#modal-volume-put)[modal volume rename](#modal-volume-rename)[modal volume rm](#modal-volume-rm)