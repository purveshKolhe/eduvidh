# modal.container_process | Modal Docs

Source: https://modal.com/docs/reference/modal.container_process

---

---

Copy page

# modal.container\_process

 

## modal.container\_process.ContainerProcessÂ

```
class ContainerProcess(typing.Generic)
```

Represents a running process in a container.

Container processes communicate via direct communication with
the Modal worker where the container is running.

```
__init__(self, process_id, task_id, client, command_router_client,
    stdout=StreamType.PIPE, stderr=StreamType.PIPE, exec_deadline=None,
    text=True, by_line=False)
```

 

### stdoutÂ

```
stdout(self)
```

StreamReader for the container processâs stdout stream.

### stderrÂ

```
stderr(self)
```

StreamReader for the container processâs stderr stream.

### stdinÂ

```
stdin(self)
```

StreamWriter for the container processâs stdin stream.

### returncodeÂ

```
returncode(self)
```

 

### pollÂ

```
poll(self)
```

Check if the container process has finished running.

Returns `None` if the process is still running, else returns the exit code.

### waitÂ

```
wait(self)
```

Wait for the container process to finish running. Returns the exit code.

[modal.container\_process](#modalcontainer_process)[ContainerProcess](#modalcontainer_processcontainerprocess)[stdout](#stdout)[stderr](#stderr)[stdin](#stdin)[returncode](#returncode)[poll](#poll)[wait](#wait)