# modal.file_io | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.file_io

---

---

Copy page

# modal.file\_io

 

## modal.file\_io.FileIOÂ

```
class FileIO(typing.Generic)
```

[Alpha] FileIO handle, used in the Sandbox filesystem API.

Deprecated on 2026-03-09. Use the `Sandbox.filesystem` APIs instead.

The API is designed to mimic Pythonâs io.FileIO.

Currently this API is in Alpha and is subject to change. File I/O operations
may be limited in size to 100 MiB, and the throughput of requests is
restricted in the current implementation. For our recommendations on large file transfers
see the Sandbox [filesystem access guide](https://modal.com/docs/guide/sandbox-files).

**Usage**

```
import modal

app = modal.App.lookup("my-app", create_if_missing=True)

sb = modal.Sandbox.create(app=app)
f = sb.open("/tmp/foo.txt", "w")
f.write("hello")
f.close()
```

```
__init__(self, client, task_id)
```

 

### createÂ

```
create(cls, path, mode, client, task_id)
```

Create a new FileIO handle.

### readÂ

```
read(self, n=None)
```

Read n bytes from the current position, or the entire remaining file if n is None.

### readlineÂ

```
readline(self)
```

Read a single line from the current position.

### readlinesÂ

```
readlines(self)
```

Read all lines from the current position.

### writeÂ

```
write(self, data)
```

Write data to the current position.

Writes may not appear until the entire buffer is flushed, which
can be done manually with `flush()` or automatically when the file is
closed.

### flushÂ

```
flush(self)
```

Flush the buffer to disk.

### seekÂ

```
seek(self, offset, whence=0)
```

Move to a new position in the file.

`whence` defaults to 0 (absolute file positioning); other values are 1
(relative to the current position) and 2 (relative to the fileâs end).

### lsÂ

```
ls(cls, path, client, task_id)
```

List the contents of the provided directory.

### mkdirÂ

```
mkdir(cls, path, client, task_id, parents=False)
```

Create a new directory.

### rmÂ

```
rm(cls, path, client, task_id, recursive=False)
```

Remove a file or directory in the Sandbox.

### watchÂ

```
watch(cls, path, client, task_id, filter=None, recursive=False, timeout=None)
```

 

### closeÂ

```
close(self)
```

Flush the buffer and close the file.

## modal.file\_io.lsÂ

```
ls(path, client, task_id)
```

List the contents of the provided directory.

## modal.file\_io.mkdirÂ

```
mkdir(path, client, task_id, parents=False)
```

Create a new directory.

## modal.file\_io.rmÂ

```
rm(path, client, task_id, recursive=False)
```

Remove a file or directory in the Sandbox.

## modal.file\_io.watchÂ

```
watch(path, client, task_id, filter=None, recursive=False, timeout=None)
```

Watch a file or directory for changes.

[modal.file\_io](#modalfile_io)[FileIO](#modalfile_iofileio)[create](#create)[read](#read)[readline](#readline)[readlines](#readlines)[write](#write)[flush](#flush)[seek](#seek)[ls](#ls)[mkdir](#mkdir)[rm](#rm)[watch](#watch)[close](#close)[ls](#modalfile_iols)[mkdir](#modalfile_iomkdir)[rm](#modalfile_iorm)[watch](#modalfile_iowatch)