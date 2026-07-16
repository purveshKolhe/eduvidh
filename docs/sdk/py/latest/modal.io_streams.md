# modal.io_streams | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.io_streams

---

---

Copy page

# modal.io\_streams

 

## modal.io\_streams.StreamReaderÂ

```
class StreamReader(typing.Generic)
```

Retrieve logs from a stream (`stdout` or `stderr`).

As an asynchronous iterable, the object supports the `for` and `async for` statements. Just loop over the object to read in chunks.

### file\_descriptorÂ

```
file_descriptor(self)
```

Possible values are `1` for stdout and `2` for stderr.

### readÂ

```
read(self)
```

Fetch the entire contents of the stream until EOF.

## modal.io\_streams.StreamWriterÂ

```
class StreamWriter(object)
```

Provides an interface to buffer and write logs to a sandbox or container process stream (`stdin`).

### writeÂ

```
write(self, data)
```

Write data to the stream but does not send it immediately.

This is non-blocking and queues the data to an internal buffer. Must be
used along with the `drain()` method, which flushes the buffer.

**Usage**

```
proc = sandbox.exec(
    "bash",
    "-c",
    "while read line; do echo $line; done",
)
proc.stdin.write(b"foo\n")
proc.stdin.write(b"bar\n")
proc.stdin.write_eof()
proc.stdin.drain()
```

 

### write\_eofÂ

```
write_eof(self)
```

Close the write end of the stream after the buffered data is drained.

If the process was blocked on input, it will become unblocked after `write_eof()`. This method needs to be used along with the `drain()` method, which flushes the EOF to the process.

### drainÂ

```
drain(self)
```

Flush the write buffer and send data to the running process.

This is a flow control method that blocks until data is sent. It returns
when it is appropriate to continue writing data to the stream.

**Usage**

```
writer.write(data)
writer.drain()
```

Async usage:

```
writer.write(data)  # not a blocking operation
await writer.drain.aio()
```

[modal.io\_streams](#modalio_streams)[StreamReader](#modalio_streamsstreamreader)[file\_descriptor](#file_descriptor)[read](#read)[StreamWriter](#modalio_streamsstreamwriter)[write](#write)[write\_eof](#write_eof)[drain](#drain)