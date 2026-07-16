# modal.exception | Modal Docs

Source: https://modal.com/docs/sdk/py/latest/modal.exception

---

---

Copy page

# modal.exception

Modal-specific exception types.

## Notes on `grpclib.GRPCError` migrationÂ

Historically, the Modal SDK could propagate `grpclib.GRPCError` exceptions out
to user code. As of v1.3, we are in the process of gracefully migrating to
always raising a Modal exception type in these cases. To avoid breaking user
code that relies on catching `grpclib.GRPCError`, a subset of Modal exception
types temporarily inherit from `grpclib.GRPCError`.

We encourage users to migrate any code that currently catches `grpclib.GRPCError` to instead catch the appropriate Modal exception type. The following mapping
between GRPCError status codes and Modal exception types is currently in use:

```
CANCELLED -> ServiceError
UNKNOWN -> ServiceError
INVALID_ARGUMENT -> InvalidError
DEADLINE_EXCEEDED -> ServiceError
NOT_FOUND -> NotFoundError
ALREADY_EXISTS -> AlreadyExistsError
PERMISSION_DENIED -> PermissionDeniedError
RESOURCE_EXHAUSTED -> ResourceExhaustedError
FAILED_PRECONDITION -> ConflictError
ABORTED -> ConflictError
OUT_OF_RANGE -> InvalidError
UNIMPLEMENTED -> UnimplementedError
INTERNAL -> InternalError
UNAVAILABLE -> ServiceError
DATA_LOSS -> DataLossError
UNAUTHENTICATED -> AuthError
```

 

## modal.exception.AlreadyExistsErrorÂ

```
class AlreadyExistsError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when a resource creation conflicts with an existing resource.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.AsyncUsageWarningÂ

```
class AsyncUsageWarning(UserWarning)
```

Warning emitted when a blocking Modal interface is used in an async context.

## modal.exception.AuthErrorÂ

```
class AuthError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when a client has missing or invalid authentication.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.ClientClosedÂ

```
class ClientClosed(modal.exception.Error)
```

 

## modal.exception.ConflictErrorÂ

```
class ConflictError(modal.exception.InvalidError, modal.exception._GRPCErrorWrapper)
```

Raised when a resource conflict occurs between the request and current system state.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.ConnectionErrorÂ

```
class ConnectionError(modal.exception.Error)
```

Raised when an issue occurs while connecting to the Modal servers.

## modal.exception.DataLossErrorÂ

```
class DataLossError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when data is lost or corrupted.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.DeprecationErrorÂ

```
class DeprecationError(UserWarning)
```

UserWarning category emitted when a deprecated Modal feature or API is used.

## modal.exception.DeserializationErrorÂ

```
class DeserializationError(modal.exception.Error)
```

Raised to provide more context when an error is encountered during deserialization.

## modal.exception.ErrorÂ

```
class Error(Exception)
```

Base class for all Modal errors. See [`modal.exception`](https://modal.com/docs/sdk/py/latest/modal.exception) for the specialized error classes.

**Usage**

```
import modal

try:
    ...
except modal.Error:
    # Catch any exception raised by Modal's systems.
    print("Responding to error...")
```

 

## modal.exception.ExecTimeoutErrorÂ

```
class ExecTimeoutError(modal.exception.TimeoutError)
```

Raised when a container process exceeds its execution duration limit and times out.

## modal.exception.ExecutionErrorÂ

```
class ExecutionError(modal.exception.Error)
```

Raised when something unexpected happened during runtime.

## modal.exception.FilesystemExecutionErrorÂ

```
class FilesystemExecutionError(modal.exception.Error)
```

Raised when an unknown error is thrown during a container filesystem operation.

## modal.exception.FunctionTimeoutErrorÂ

```
class FunctionTimeoutError(modal.exception.TimeoutError)
```

Raised when a Function exceeds its execution duration limit and times out.

## modal.exception.InputCancellationÂ

```
class InputCancellation(BaseException)
```

Raised when the current input is cancelled by the task

Intentionally a BaseException instead of an Exception, so it wonât get
caught by unspecified user exception clauses that might be used for retries and
other control flow.

## modal.exception.InteractiveTimeoutErrorÂ

```
class InteractiveTimeoutError(modal.exception.TimeoutError)
```

Raised when interactive frontends time out while trying to connect to a container.

## modal.exception.InternalErrorÂ

```
class InternalError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when an internal error occurs in the Modal system.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.InternalFailureÂ

```
class InternalFailure(modal.exception.Error)
```

Retriable internal error.

## modal.exception.InvalidErrorÂ

```
class InvalidError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when user does something invalid.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.LogsFetchErrorÂ

```
class LogsFetchError(modal.exception.Error)
```

Raised when trying to fetch too many logs.

## modal.exception.ModuleNotMountableÂ

```
class ModuleNotMountable(Exception)
```

 

## modal.exception.MountUploadTimeoutErrorÂ

```
class MountUploadTimeoutError(modal.exception.TimeoutError)
```

Raised when a Mount upload times out.

## modal.exception.NotFoundErrorÂ

```
class NotFoundError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when a requested resource was not found.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.OutputExpiredErrorÂ

```
class OutputExpiredError(modal.exception.TimeoutError)
```

Raised when the Output exceeds expiration and times out.

## modal.exception.PermissionDeniedErrorÂ

```
class PermissionDeniedError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when a user does not have permission to perform the requested operation.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.RemoteErrorÂ

```
class RemoteError(modal.exception.Error)
```

Raised when an error occurs on the Modal server.

## modal.exception.RequestSizeErrorÂ

```
class RequestSizeError(modal.exception.Error)
```

Raised when an operation produces a gRPC request that is rejected by the server for being too large.

## modal.exception.ResourceExhaustedErrorÂ

```
class ResourceExhaustedError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when a server-side resource has been exhausted, e.g. a quota or rate limit.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.SandboxFilesystemDirectoryNotEmptyErrorÂ

```
class SandboxFilesystemDirectoryNotEmptyError(modal.exception.SandboxFilesystemError)
```

Raised when a directory is not empty.

## modal.exception.SandboxFilesystemErrorÂ

```
class SandboxFilesystemError(modal.exception.Error)
```

Base class for sandbox filesystem errors.

## modal.exception.SandboxFilesystemFileTooLargeErrorÂ

```
class SandboxFilesystemFileTooLargeError(modal.exception.SandboxFilesystemError)
```

Raised when a file exceeds the maximum allowed size for a read operation in the sandbox.

## modal.exception.SandboxFilesystemIsADirectoryErrorÂ

```
class SandboxFilesystemIsADirectoryError(modal.exception.SandboxFilesystemError)
```

Raised when a file operation in the sandbox targets a directory when it should target a non-directory file.

## modal.exception.SandboxFilesystemNotADirectoryErrorÂ

```
class SandboxFilesystemNotADirectoryError(modal.exception.SandboxFilesystemError)
```

Raised when a path component in the sandbox is not a directory.

## modal.exception.SandboxFilesystemNotFoundErrorÂ

```
class SandboxFilesystemNotFoundError(modal.exception.SandboxFilesystemError)
```

Raised when a file or directory is not found in the sandbox.

## modal.exception.SandboxFilesystemPathAlreadyExistsErrorÂ

```
class SandboxFilesystemPathAlreadyExistsError(modal.exception.SandboxFilesystemError)
```

Raised when a path already exists and the operation requires it to be absent.

## modal.exception.SandboxFilesystemPermissionErrorÂ

```
class SandboxFilesystemPermissionError(modal.exception.SandboxFilesystemError)
```

Raised when permission is denied for a file operation in the sandbox.

## modal.exception.SandboxTerminatedErrorÂ

```
class SandboxTerminatedError(modal.exception.Error)
```

Raised when a Sandbox is terminated for an internal reason.

## modal.exception.SandboxTimeoutErrorÂ

```
class SandboxTimeoutError(modal.exception.TimeoutError)
```

Raised when a Sandbox exceeds its execution duration limit and times out.

## modal.exception.SerializationErrorÂ

```
class SerializationError(modal.exception.Error)
```

Raised to provide more context when an error is encountered during serialization.

## modal.exception.ServerWarningÂ

```
class ServerWarning(UserWarning)
```

Warning originating from the Modal server and re-issued in client code.

## modal.exception.ServiceErrorÂ

```
class ServiceError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when an error occurs in basic client/server communication.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.TimeoutErrorÂ

```
class TimeoutError(modal.exception.Error)
```

Base class for Modal timeouts.

## modal.exception.UnimplementedErrorÂ

```
class UnimplementedError(modal.exception.Error, modal.exception._GRPCErrorWrapper)
```

Raised when a requested operation is not implemented or not supported.

```
__init__(self, message=None)
```

 

### messageÂ

```
message(self)
```

 

### statusÂ

```
status(self)
```

 

### detailsÂ

```
details(self)
```

 

## modal.exception.VersionErrorÂ

```
class VersionError(modal.exception.Error)
```

Raised when the current client version of Modal is unsupported.

## modal.exception.VolumeUploadTimeoutErrorÂ

```
class VolumeUploadTimeoutError(modal.exception.TimeoutError)
```

Raised when a Volume upload times out.

## modal.exception.WorkspaceManagementErrorÂ

```
class WorkspaceManagementError(modal.exception.Error)
```

Raised when an error occurs while managing a workspace.

## modal.exception.simulate\_preemptionÂ

```
simulate_preemption(wait_seconds, jitter_seconds=0)
```

Utility for simulating a preemption interrupt after `wait_seconds` seconds.
The first interrupt is the SIGINT signal. After 30 seconds, a second
interrupt will trigger.

This second interrupt simulates SIGKILL, and should not be caught.
Optionally add between zero and `jitter_seconds` seconds of additional waiting before first interrupt.

**Usage**

```
import time
from modal.exception import simulate_preemption

simulate_preemption(3)

try:
    time.sleep(4)
except KeyboardInterrupt:
    print("got preempted") # Handle interrupt
    raise
```

See <https://modal.com/docs/guide/preemption> for more details on preemption
handling.

[modal.exception](#modalexception)[Notes on grpclib.GRPCError migration](#notes-on-grpclibgrpcerror-migration)[AlreadyExistsError](#modalexceptionalreadyexistserror)[message](#message)[status](#status)[details](#details)[AsyncUsageWarning](#modalexceptionasyncusagewarning)[AuthError](#modalexceptionautherror)[message](#message-1)[status](#status-1)[details](#details-1)[ClientClosed](#modalexceptionclientclosed)[ConflictError](#modalexceptionconflicterror)[message](#message-2)[status](#status-2)[details](#details-2)[ConnectionError](#modalexceptionconnectionerror)[DataLossError](#modalexceptiondatalosserror)[message](#message-3)[status](#status-3)[details](#details-3)[DeprecationError](#modalexceptiondeprecationerror)[DeserializationError](#modalexceptiondeserializationerror)[Error](#modalexceptionerror)[ExecTimeoutError](#modalexceptionexectimeouterror)[ExecutionError](#modalexceptionexecutionerror)[FilesystemExecutionError](#modalexceptionfilesystemexecutionerror)[FunctionTimeoutError](#modalexceptionfunctiontimeouterror)[InputCancellation](#modalexceptioninputcancellation)[InteractiveTimeoutError](#modalexceptioninteractivetimeouterror)[InternalError](#modalexceptioninternalerror)[message](#message-4)[status](#status-4)[details](#details-4)[InternalFailure](#modalexceptioninternalfailure)[InvalidError](#modalexceptioninvaliderror)[message](#message-5)[status](#status-5)[details](#details-5)[LogsFetchError](#modalexceptionlogsfetcherror)[ModuleNotMountable](#modalexceptionmodulenotmountable)[MountUploadTimeoutError](#modalexceptionmountuploadtimeouterror)[NotFoundError](#modalexceptionnotfounderror)[message](#message-6)[status](#status-6)[details](#details-6)[OutputExpiredError](#modalexceptionoutputexpirederror)[PermissionDeniedError](#modalexceptionpermissiondeniederror)[message](#message-7)[status](#status-7)[details](#details-7)[RemoteError](#modalexceptionremoteerror)[RequestSizeError](#modalexceptionrequestsizeerror)[ResourceExhaustedError](#modalexceptionresourceexhaustederror)[message](#message-8)[status](#status-8)[details](#details-8)[SandboxFilesystemDirectoryNotEmptyError](#modalexceptionsandboxfilesystemdirectorynotemptyerror)[SandboxFilesystemError](#modalexceptionsandboxfilesystemerror)[SandboxFilesystemFileTooLargeError](#modalexceptionsandboxfilesystemfiletoolargeerror)[SandboxFilesystemIsADirectoryError](#modalexceptionsandboxfilesystemisadirectoryerror)[SandboxFilesystemNotADirectoryError](#modalexceptionsandboxfilesystemnotadirectoryerror)[SandboxFilesystemNotFoundError](#modalexceptionsandboxfilesystemnotfounderror)[SandboxFilesystemPathAlreadyExistsError](#modalexceptionsandboxfilesystempathalreadyexistserror)[SandboxFilesystemPermissionError](#modalexceptionsandboxfilesystempermissionerror)[SandboxTerminatedError](#modalexceptionsandboxterminatederror)[SandboxTimeoutError](#modalexceptionsandboxtimeouterror)[SerializationError](#modalexceptionserializationerror)[ServerWarning](#modalexceptionserverwarning)[ServiceError](#modalexceptionserviceerror)[message](#message-9)[status](#status-9)[details](#details-9)[TimeoutError](#modalexceptiontimeouterror)[UnimplementedError](#modalexceptionunimplementederror)[message](#message-10)[status](#status-10)[details](#details-10)[VersionError](#modalexceptionversionerror)[VolumeUploadTimeoutError](#modalexceptionvolumeuploadtimeouterror)[WorkspaceManagementError](#modalexceptionworkspacemanagementerror)[simulate\_preemption](#modalexceptionsimulate_preemption)