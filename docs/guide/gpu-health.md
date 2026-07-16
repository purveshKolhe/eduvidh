# GPU Health | Modal Docs

Source: https://modal.com/docs/guide/gpu-health

---

---

Copy page

# GPU Health

Modal constantly monitors host GPU health, draining Workers with critical issues
and surfacing warnings for customer triage.

Application level observability of GPU health is facilitated by [metrics](/docs/guide/gpu-metrics) and event logging to container log streams.

## `[gpu-health]` loggingÂ

Containers with attached NVIDIA GPUs are connected to our `gpu-health` monitoring system
and receive event logs which originate from either application software behavior, system software behavior, or hardware failure.

These logs are in the following format: `[gpu-health] [LEVEL] GPU-[UUID]: EVENT_TYPE: MSG`

* `gpu-health`: Name indicating the source is Modalâs observability system.
* `LEVEL`: Represents the severity level of the log message.
* `GPU_UUID`: A unique identifier for the GPU device associated with the event, if any.
* `EVENT_TYPE`: The type of event source. Modal monitors for multiple types of errors,
  including Xid, SXid, and uncorrectable ECC. See below for more details.
* `MSG`: The message component is either the original message taken from the event source, or a description provided by Modal of the problem.

## LevelÂ

The severity level may be `CRITICAL` or `WARN`. Modal automatically responds to `CRITICAL` level events by draining the underlying Worker and migrating customer containers. `WARN` level logs may be benign or indication of an application or library bug. No automatic action is taken by our system for warnings.

## Handling Application-level health issuesÂ

As noted above, Modal will automatically respond to critical GPU events, but warning level events can still
be associated with application exceptions. Applications should catch exceptions caused by GPU-related faults
and call `modal.experimental.stop_fetching_inputs()`:

```
import modal.experimental
...

@app.function(gpu="H100")
def demo():
    try:
        ... # code which may hit GPU fault (e.g. illegal memory access)
    except RuntimeError:
        modal.experimental.stop_fetching_inputs()
        return
```

 

## Xid & SXidÂ

The Xid message is an error report from the NVIDIA driver. The SXid, or âSwitch Xidâ is a report for the NVSwitch component used in GPU-to-GPU communication, and is thus only relevant in multi-GPU containers.

A classic critical Xid error is the âfell off the busâ report, code 79. The `gpu-health` event log looks like this:

```
[gpu-health] [CRITICAL] GPU-1234: XID: NVRM: Xid (PCI:0000:c6:00): 79, pid=1101234, name=nvc:[driver], GPU has fallen off the bus.
```

There are over 100 Xid codes and they are of highly varying frequency, severity, and specificity. [NVIDIAâs official documentation](https://docs.nvidia.com/deploy/xid-errors/index.html) provides limited information, so
we maintain our own tabular information below.

### Xid Details

| XID | Name | Critical | Causes |
| --- | --- | --- | --- |
| 1 | Invalid or corrupted push buffer stream | No | driver error, system memory corruption, bus error, framebuffer corruption |
| Unused ID. If you see an error emitted with this ID contact support. | | | |
| 2 | Invalid or corrupted push buffer stream | No | driver error, system memory corruption, bus error, framebuffer corruption |
| 3 | Invalid or corrupted push buffer stream | No | driver error, system memory corruption, bus error, framebuffer corruption |
| 4 | Invalid or corrupted push buffer stream OR GPU semaphore timeout | No | driver error, user app error, system memory corruption, bus error, framebuffer corruption |
| This ID (4) is overloaded. It can be either invalid or corrupted push buffer stream or GPU semaphore timeout. In the latter case user app error is a potential cause. | | | |
| 6 | Invalid or corrupted push buffer stream | No | driver error, system memory corruption, bus error, framebuffer corruption |
| 7 | Invalid or corrupted push buffer address | No | driver error, system memory corruption, bus error, framebuffer corruption |
| 8 | GPU stopped processing | No | driver error, user app error, bus error, thermal issue |
| 9 | Driver error programming GPU | Yes | driver error |
| Official NVIDIA documentation implicates only the driver as cause of error, thus recommended action is rebooting the system. | | | |
| 11 | Invalid or corrupted push buffer stream | No | driver error, system memory corruption, bus error, framebuffer corruption |
| 12 | Driver error handling GPU exception | Yes | driver error |
| Official NVIDIA documentation implicates only the driver as cause of error, thus recommended action is rebooting the system. | | | |
| 13 | Graphics Engine Exception | No | hardware error, driver error, user app error, system memory corruption, bus error, thermal issue, framebuffer corruption |
| Marked as non-critical, this error indicates GPU memory anomalies affecting code and data segments, arrays being out of their declared ranges, applications having illegal memory access issues, or instruction errors.   Restart applications and check whether the same Xid is returned. To debug, refer to [cuda-memcheck](https://developer.nvidia.com/cuda-memcheck) or [CUDA-GDB](https://docs.nvidia.com/cuda/cuda-gdb/index.html). In rare cases it can be caused by the hardware degradation. Please contact Modal support if the issue persists.     * The official NVIDIA documentation explains Xid 13 has many potential causes, including hardware, driver, user app, system memory corruption, bus, thermal issue, and fb corruption.    + [NVIDIA Xid 13: GR: SW Notify Error](https://docs.nvidia.com/deploy/xid-errors/index.html#xid-13-gr-sw-notify-error)   + ["NVIDIA Xid Errors" (PDF)](https://docs.nvidia.com/deploy/pdf/XID_Errors.pdf)   + [NVIDIA Xid Errors](https://docs.nvidia.com/deploy/xid-errors/index.html)   + [NVIDIA GPU debug guidelines](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#xid-messages) * DeepSeek AI paper explains Xid 13 indicates GPU memory anomalies, but can be a hardware error.   [Fire-Flyer AI-HPC: A Cost-Effective Software-Hardware Co-Design for Deep Learning](https://arxiv.org/abs/2408.14158v1) (Aug 2024) * The official nvidia memory error doc does not mention Xid 13.   [NVIDIA GPU Memory Error Management](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/index.html) * The official nvidia k8s device plugin implements Xid 13 as an application error.   [NVIDIA/k8s-device-plugin health check](https://github.com/NVIDIA/k8s-device-plugin/blob/v0.17.0/internal/rm/health.go#L65-L71) * The [imbue-ai GPU health check](https://github.com/imbue-ai/cluster-health/blob/8f5964ac620931138ed29f43557557048e826cd7/health_checks/health_checks.py#L769-L782) implements Xid 13 as a non-hardware error. * The AWS support doc [*Troubleshoot Xid errors*](https://repost.aws/knowledge-center/ec2-linux-troubleshoot-xid-errors) does not mention Xid 13. * The Google Cloud doc [*Troubleshoot GPU VMs*](https://cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus#xid_messages) explains Xid 13 is returned when applications have illegal memory access issues, and recommends cuda-memcheck and CUDA-GDB for debugging. * The Alibaba Cloud doc explains Xid 13 requires self-check by the user and users to resubmit the load to see if the issue goes away   [Diagnose GPU-accelerated nodes](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-node-diagnosis-to-self-troubleshoot-gpu-node-problems) * The Tencent Cloud doc [*How to handle common Xid events*](https://cloud.tencent.com/document/product/560/106781) does not mention Xid 13. * The [Azure HPC GPU node problem detector](https://github.com/Azure/azurehpc/blob/master/experimental/aks_npd_draino/npd/deployment/node-problem-detector-config.yaml#L293) does not implement any health check for Xid 13. | | | |
| 16 | Display engine hung | Yes | driver error |
| Because this error is attributed only to the driver, the recommended operator action is rebooting the system. | | | |
| 18 | Bus mastering disabled in PCI Config Space | Yes | driver error |
| Because this error is attributed only to the driver, the recommended operator action is rebooting the system. | | | |
| 19 | Display Engine error | Yes | driver error |
| Because this error is attributed only to the driver, the recommended operator action is rebooting the system. | | | |
| 20 | Invalid or corrupted Mpeg push buffer | No | â |
| 21 | Invalid or corrupted Motion Estimation push buffer | No | â |
| 22 | Invalid or corrupted Video Processor push buffer | No | â |
| 24 | GPU semaphore timeout | No | â |
| It is expected that the timeout is recoverable. | | | |
| 25 | Invalid or illegal push buffer stream | No | â |
| 26 | Framebuffer timeout | Yes | driver error |
| Indicates framebuffer timeout, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 27 | Video processor exception | Yes | driver error |
| Indicates a video processor exception, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 28 | Video processor exception | Yes | driver error |
| Indicates video processor exception, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 29 | Video processor exception | Yes | driver error |
| Indicates video processor exception, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 30 | GPU semaphore access error | Yes | driver error |
| Indicates GPU semaphore access error, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 31 | GPU memory page fault | No | hardware error, driver error, user app error |
| Debug the user application unless the issue is new and there have been no changes to the application but there has been changes to GPU driver or other GPU system software. Restart applications and check whether the same Xid is returned. To debug, refer to [cuda-memcheck](https://developer.nvidia.com/cuda-memcheck) or [CUDA-GDB](https://docs.nvidia.com/cuda/cuda-gdb/index.html). In rare cases it can be caused by the hardware degradation. If the issue persists, please contact support for hardware inspection and repair.   The official NVIDIA docs explains Xid 31 as a user application issue, but can also be driver bugs or hardware issues. This event is logged when MMU reports a fault when an illegal address access is made by an application unit on the chip.     * [NVIDIA Xid 31: FIFO: MMU Error](https://docs.nvidia.com/deploy/xid-errors/index.html#xid-31-fifo-mmu-error) * [NVIDIA Xid Errors PDF](https://docs.nvidia.com/deploy/pdf/XID_Errors.pdf) (September 2024) * [NVIDIA Xid Errors](https://docs.nvidia.com/deploy/xid-errors/index.html) * The official [NVIDIA debugging guideline](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#xid-messages) explains Xid 31 requires user application debugging. * The official [NVIDIA memory error documentation](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/index.html) does not mention Xid 31. * The official [NVIDIA Kubernetes device plugin (v0.170.8)](https://github.com/NVIDIA/k8s-device-plugin/blob/v0.17.0/internal/rm/health.go#L65-L71) implements Xid 31 as a user application issue. * The [imbue-ai GPU health check](https://github.com/imbue-ai/cluster-health/blob/8f5964ac620931138ed29f43557557048e826cd7/health_checks/health_checks.py#L769-L782) does not implement any Xid 31 health checks. * The AWS support doc [*Troubleshoot Xid errors*](https://repost.aws/knowledge-center/ec2-linux-troubleshoot-xid-errors) does not mention Xid 31. * The Google Cloud [troubleshooting guide](https://cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus#xid_messages) explains Xid 31 is returned when applications have illegal memory access issues, and recommends cuda-memcheck and CUDA-GDB for debugging. * The Alibaba Cloud guide [*Diagnose GPU-accelerated nodes*](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-node-diagnosis-to-self-troubleshoot-gpu-node-problems) explains Xid 31 requires self-check by users and users to resubmit the workload to see if the same Xid is returned. * The Tencent Cloud doc [*How to handle common Xid events*](https://cloud.tencent.com/document/product/560/106781) does not mention Xid 31. * The Azure HPC GPU [node problem detector](https://github.com/Azure/azurehpc/blob/master/experimental/aks_npd_draino/npd/deployment/node-problem-detector-config.yaml#L293) does not implement any Xid 31 health checks. * [DeepSeek AI paper on Fire-Flyer](https://arxiv.org/abs/2408.14158v1) explains Xid 31 is a user application issue, which may indicate the GPU memory anomalies, but can also be hardware issues. | | | |
| 32 | Invalid or corrupted push buffer stream | Yes | driver error, system memory corruption, bus error, thermal issue, framebuffer corruption |
| The event is reported by the DMA controller of the PCIE bus that manages communication between the NVIDIA driver and GPU. In most cases, a PCI quality issue occurs.     * The official NVIDIA docs explains Xid 32 is a DMA controller error which manages the communication between the NVIDIA driver and GPU over the PCI-E bus. This indicates PCI quality issues, not user application issues. * "NVIDIA Xid 32: PBDMA Error", <https://docs.nvidia.com/deploy/xid-errors/index.html#xid-32-pbdma-error> (accessed on Nov 3, 2024) | | | |
| 33 | Internal micro-controller error | Yes | driver error |
| Indicates internal micro-controller error, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 34 | Video processor exception | Yes | driver error |
| Indicates video processor exception, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 35 | Video processor exception | Yes | driver error |
| Indicates video processor exception, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 36 | Video processor exception | Yes | driver error |
| Indicates video processor exception, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 37 | Driver firmware error | No | â |
| 38 | Driver firmware error | Yes | driver error |
| Marked as critical, indicates NVIDIA driver firmware issues. Reboot the system to check whether the firmware issue persists.     * The official [NVIDIA docs](https://docs.nvidia.com/deploy/xid-errors/index.html) explains Xid 38 as a potential driver firmware error. * The Alibaba Cloud guide [*Diagnose GPU-accelerated nodes*](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-node-diagnosis-to-self-troubleshoot-gpu-node-problems) explains Xid 38 as a driver firmware issue. | | | |
| 39 | Copy Engine Exception | No | hardware error, driver error |
| 40 | Copy Engine Exception | No | hardware error, driver error |
| 41 | Copy Engine Exception | No | hardware error, driver error |
| 42 | Video processor exception | Yes | driver error |
| Indicates a video processor exception, and because a driver error is the only possible reason, the recommended operator action is rebooting the system. | | | |
| 43 | GPU stopped processing | No | driver error, user app error |
| Marked as non-critical, indicates GPU stopped processing, due to a user application encountering a software induced fault. Restart applications and check whether the same Xid is returned. And report if the issue persists.     * The official NVIDIA docs explains Xid 43 as a user application hitting a software induced faults.    + NVIDIA Xid 43: Reset Channel Verif Error, <https://docs.nvidia.com/deploy/xid-errors/index.html#xid-43-reset-channel-verif-error> (accessed on Nov 3, 2024) * The [official NVIDIA k8s device plugin (v0.17.0)](https://github.com/NVIDIA/k8s-device-plugin/blob/v0.17.0/internal/rm/health.go#L65-L71) implements Xid 43 as a user application error, indicating GPU stopped processing.   The [Alibaba Cloud guide](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-node-diagnosis-to-self-troubleshoot-gpu-node-problems) explains Xid 43 as a user application error encountering a software induced fault, as a result, GPU stopped processing. * DeepSeek [Fire-Flyer AI-HPC](https://arxiv.org/abs/2408.14158v1) AI paper explains Xid 43 as a user application error, but may indicate GPU memory anomalies. | | | |
| 44 | Graphics Engine fault during context switch | Yes | driver error |
| Marked as critical, indicates uncorrectable GPU errors. Stop existing workloads and reboot the system (or reset GPUs) to clear this error. Marked as critical, indicates uncorrectable GPU errors. If the uncorrectable GPU error persists after rebooting the system, contact provider for inspection and repair of the hardware.   The [official NVIDIA docs](https://docs.nvidia.com/deploy/xid-errors/index.html) explains Xid 44 as a potential driver issue. DeepSeek's [Fire-Flyer AI paper](https://arxiv.org/abs/2408.14158v1) explains Xid 44 indicates uncorrectable GPU errors, recommends GPU reset or node reboot. | | | |
| 45 | Preemptive cleanup, due to previous errors â Most likely to see when running multiple CUD applications and hitting a Double Bit ECC Error (DBE). | No | driver error, user app error |
| Robust Channel Preemptive Removal. No action, informative only. Indicates channels affected by another failure. On A100, this error could be seen by itself due to unexpected Fabric Manager shutdown when FM is running in the same OS environment as the GPU. Otherwise, this error is safe to ignore as an informational message.   The official NVIDIA docs explains Xid 45 is returned when the kernel driver terminates a GPU application, as a result of a user of system action. [NVIDIA Xid 45: OS: Preemptive Channel Removal](https://docs.nvidia.com/deploy/xid-errors/index.html#xid-45-os-preemptive-channel-removal)     * The official [NVIDIA debugging guideline](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#xid-messages) explains Xid 45 indicates channel affected by another failure, or may indicate unexpected Fabric Manager shutdown. * The official nvidia k8s device plugin implements Xid 45 as a user application error, being preemptive cleanup due to previous errors.   NVIDIA/k8s-device-plugin health check, <https://github.com/NVIDIA/k8s-device-plugin/blob/v0.17.0/internal/rm/health.go#L65-L71> (Aug 2024) * The AWS [*Troubleshoot Xid* guide](https://repost.aws/knowledge-center/ec2-linux-troubleshoot-xid-errors) does not mention Xid 45. * The Google Cloud [troubleshooting guide](https://cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus#xid_messages) does not mention Xid 45. * The [Alibaba Cloud guide](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-node-diagnosis-to-self-troubleshoot-gpu-node-problems) explains Xid 45 may indicate multiple cuda applications hitting a DBE, or the result of application being stopped due to another error. * DeepSeek's Fire-Flyer AI paper explains Xid 45 indicates GPU memory anomalies, affecting code and data segments, but can be hardware-related. | | | |
| 46 | GPU stopped processing | Yes | driver error |
| Indicates GPU stopped processing, labeling a driver error as an only possible reason, thus we recommend rebooting the system. | | | |
| 47 | Video processor exception | Yes | driver error |
| Indicates a video processor exception, labeling a driver error as an only possible reason, thus we recommend rebooting the system. | | | |
| 48 | Double Bit ECC Error | Yes | driver error |
| This event is logged when the GPU detects that an uncorrectable error occurs on the GPU. A GPU reset or node reboot is needed to clear this error. Marked as critical, indicates uncorrectable double bit ECC errors (DBE), which also reports back to the user application. Stop existing workloads and reboot the system (or reset GPUs) to clear this error.     * If Xid 48 is followed by Xid 63 or 64: Drain/cordon the node, wait for all work to complete, and reset GPU(s) reporting the XID (refer to GPU reset capabilities/limitations section below). * If Xid 48 is not followed by Xid 63 or 64: see [Running Field Diagnostics](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#running-field-diag) to collect additional debug information.   The error is also reported to your application. In most cases, you need to reset the GPU or node to fix this error. | | | |
| 54 | Auxiliary power is not connected to the GPU board | No | â |
| 56 | Display Engine error | No | driver error, hardware error |
| 57 | Error programming video memory interface | No | driver error, hardware error, framebuffer corruption |
| 58 | Unstable video memory interface detected | No | driver error, hardware error |
| Overloaded ID, could be unstable video memory interface detected or EDC error, clarified in printout (driver error=false) | | | |
| 59 | Internal micro-controller error (older drivers) | Yes | driver error |
| As driver error is only potential cause, recommended operator action is rebooting the system. | | | |
| 60 | Video processor exception | Yes | driver error |
| As driver error is only potential cause, recommended operator action is rebooting the system. | | | |
| 61 | Internal micro-controller breakpoint/warning (newer drivers) | Yes | â |
| PMU Breakpoint. Report a GPU Issue and Reset GPU(s) reporting the XID (refer GPU reset capabilities/limitations section below). Marked as critical, indicates internal micro-controller breakpoint/warning and GPU internal engine stops working. Stop existing workloads and reboot the system (or reset GPUs) to clear this error.   Internal micro-controller breakpoint/warning. The GPU internal engine stops working. Consequently, your businesses are affected.     * The official [NVIDIA docs](https://docs.nvidia.com/deploy/xid-errors/index.html) explains Xid 61 indicates internal micro-controller warning. * The official NVIDIA [debugging guidelines](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#xid-messages) recommend resetting the GPU that reports the Xid 61. * The Alibaba Cloud ["Diagnose GPU-accelerated nodes"](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-node-diagnosis-to-self-troubleshoot-gpu-node-problems) guide explains Xid 61 indicates GPU internal engine stops working, thus affecting the business. * DeepSeek [Fire-Flyer AI-HPC](https://arxiv.org/abs/2408.14158v1) paper explains Xid 61 indicates uncorrectable GPU errors, which reports back to the user application,   recommending GPU reset or node reboot to clear this error. | | | |
| 62 | Internal micro-controller halt (newer drivers) | Yes | hardware error, driver error, thermal issue |
| This event is similar to Xid 61. PMU Halt Error. Report a GPU Issue to support. | | | |
| 63 | ECC page retirement or row remapping recording event | No | hardware error, driver error, framebuffer corruption |
| These events are logged when the GPU handles ECC memory errors on the GPU.   **A100:** Row-remapping recording event. This XID indicates successful recording of a row-remapping entry to the InfoROM. If associated with XID 94, the application that encountered the error needs to be restarted. All other applications on the system can keep running as is until there is a convenient time to reset the GPU (refer GPU reset capabilities/limitations section below) or reboot for row remapping to activate.   **Legacy GPU:** ECC page retirement recording event. If associated with XID 48, drain/cordon the node, wait for all work to complete, and reset GPU(s) reporting the XID (refer GPU reset capabilities/limitations section below). If not, it is from a single bit error and the system can keep running as is until there is a convenient time to reboot it. Xid 63 indicates that the retirement or remapping information is successfully recorded in infoROM. | | | |
| 64 | ECC page retirement or row remapper recording failure | Yes | hardware error, driver error |
| These events are logged when the GPU handles ECC memory errors on the GPU.   **A100 and later:** Row-remapping recording failure. This XID indicates a failure in recording a row-remapping entry to the InfoROM. The node should be rebooted immediately since there is a recording failure. If the errors continue, drain, triage, and see [*Report a GPU Issue*](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#reporting-gpu-issue) for further operator instructions.   **Legacy GPU:** ECC page retirement recording failure.   See above, however the node should be monitored closely. If there is no associated XID 48 error, then these are related to single bit-errors. The GPU(s) reporting the error must be reset (refer to GPU reset capabilities/limitations section below) immediately since there is a recording failure. If the errors continue, drain, triage, and see Report a GPU Issue. See [guidelines on when to RMA GPUs based on excessive errors](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#reporting-gpu-issue). ECC page retirement or row remapper recording failure. This event is similar to XID 63. However, Xid 63 indicates that the retirement or remapping information is successfully recorded in infoROM. Xid 64 indicates that the retirement or remapping information fails to be recorded. | | | |
| 65 | Video processor exception | Yes | hardware error, driver error |
| Triggered when the GPU handles memory ECC errors on the GPU. Most instances can be resolved by simply resetting the GPU to retain optimal performance. | | | |
| 66 | Illegal access by driver | No | driver error, user app error |
| 67 | Illegal access by driver | No | driver error, user app error |
| 68 | NVDEC0 Exception | Yes | hardware error, driver error |
| Video processor exception. | | | |
| 69 | Graphics Engine class error | Yes | hardware error, driver error |
| Xid 69 indicates uncorrectable GPU errors. Stop the workloads and reboot the system. If the same Xid is reported again after rebooting the system, the GPU hardware should be inspected and repaired. This error has zero observations on Modal GPUs.     * The official NVIDIA docs explains Xid 69 as a potential hardware/driver issue.    + [NVIDIA Xid Errors](https://docs.nvidia.com/deploy/xid-errors/index.html)   + [NVIDIA Xid Errors PDF](https://docs.nvidia.com/deploy/pdf/XID_Errors.pdf) (Sep 2024) * The official [NVIDIA debugging guideline](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#xid-messages) does not mention Xid 69. * The official [NVIDIA Memory Error Management](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/index.html) doc does not mention Xid 69. * The official [NVIDIA k8s device plugin (v0.17.0)](https://github.com/NVIDIA/k8s-device-plugin/blob/v0.17.0/internal/rm/health.go#L65-L71) does not treat Xid 69 as an application error. * The [AWS support document](https://repost.aws/knowledge-center/ec2-linux-troubleshoot-xid-errors) does not mention Xid 69. * The [Google Cloud document](https://cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus#xid_messages) does not mention Xid 69. * The Alibaba Cloud doc [*Diagnose GPU-accelerated nodes*](https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/use-node-diagnosis-to-self-troubleshoot-gpu-node-problems) does not mention Xid 69. * The Tencent Cloud doc [*How to handle common Xid events*](https://cloud.tencent.com/document/product/560/106781) does not mention Xid 69. * The Azure HPC [GPU node problem detector](https://github.com/Azure/azurehpc/blob/master/experimental/aks_npd_draino/npd/deployment/node-problem-detector-config.yaml#L293)) implements Xid 69 detection. * DeepSeek AI paper [*Fire-Flyer AI-HPC*](https://arxiv.org/abs/2408.14158v1) explains Xid 69 indicates GPU uncorrectable errors, recommending GPU reset or node reboot. | | | |
| 70 | CE3: Unknown Error | No | hardware error, driver error |
| Indicates an unknown error. It is marked as a warning and does not require immediate action. | | | |
| 71 | CE4: Unknown Error | No | hardware error, driver error |
| 72 | CE5: Unknown Error | No | hardware error, driver error |
| 73 | NVENC2 Error | No | hardware error, driver error |
| 74 | NVLINK Error | Yes | hardware error, driver error, bus error |
| This event is logged when the GPU detects that a problem with a connection from the GPU to another GPU or NVSwitch over NVLink. A GPU reset or node reboot is needed to clear this error.   This event may indicate a hardware failure with the link itself, or may indicate a problem with the device at the remote end of the link. For example, if a GPU fails, another GPU connected to it over NVLink may report an Xid 74 simply because the link went down as a result. The `nvidia-smi nvlink` command can provide additional details on NVLink errors, and connection information on the links.   If this error is seen repeatedly and GPU reset or node reboot fails to clear the condition, contact your hardware vendor for support.   Extract the hex strings from the XID error message. eg: (`0x12345678`, `0x12345678`, `0x12345678`, `0x12345678`, `0x12345678`, `0x12345678`, `0x12345678`) Look at the bolded DWORD (the first) and take the following paths if the particular bits (counting from LSB side) are set.     * Bits 4 or 5: Likely HW issue with ECC/Parity. If seen more than 2 times on the same link, report a bug. * Bits 21 or 22: Marginal channel SI issue. Check link mechanical connections. If other errors accompany, follow the resolution for those. * Bits 8, 9, 12, 16, 17, 24, 28: Could possibly be a HW issue: Check link mechanical connections and re-seat if a field resolution is required. Run diags if issue persists.   ["Fire-Flyer AI-HPC: A Cost-Effective Software-Hardware Co-Design for Deep Learning"](https://arxiv.org/abs/2408.14158) says that Xid 74 indicates errors in NVLink. For PCIe A100, it's mainly occurred on the NVLink Bridge between two GPUs. Its occurrence rate is several orders of magnitude higher than other hardware faults. Apart from stress testing to exclude those that are constantly repeating errors, there isn't a good way to avoid the occurrence of Xid 74 issues. | | | |
| 75 | CE6: Unknown Error | No | hardware error, driver error |
| 76 | CE7: Unknown Error | No | hardware error, driver error |
| 77 | CE8: Unknown Error | No | hardware error, driver error |
| 78 | vGPU Start Error | Yes | driver error |
| vGPU start error. Reboot the system. | | | |
| 79 | GPU has fallen off the bus | Yes | hardware error, driver error, system memory corruption, bus error, thermal issue |
| This event is logged when the driver attempts to access the GPU over PCIe and finds it is not accessible. Often caused by hardware failures on the PCIe link bringing the link down. May also be failing GPU hardware or other driver issues. Review system and kernel PCI event logs for indications of link failures.   **Example:** `"NVRM: Xid (PCI:0000:b1:00): 79, GPU has fallen off the bus.` | | | |
| 80 | Corrupted data sent to GPU | No | hardware error, driver error, system memory corruption, bus error, framebuffer corruption |
| 81 | VGA Subsystem Error | No | hardware error |
| Xid 81 indicates a VGA subsystem error, labeling a hardware failure as the only possible reason. It is recommended to contact support for hardware inspection. This error has zero observations on Modal GPUs. | | | |
| 82 | NVJPG0 Error | No | hardware error, driver error |
| 83 | NVDEC1 Error | No | hardware error, driver error |
| 84 | NVDEC2 Error | No | hardware error, driver error |
| 85 | CE9: Unknown Error | No | hardware error, driver error |
| 86 | OFA Exception | No | hardware error, driver error |
| 88 | NVDEC3 Error | No | hardware error, driver error |
| 89 | NVDEC4 Error | No | hardware error, driver error |
| 92 | High single-bit ECC error rate | No | hardware error, driver error |
| A hardware or driver error occurs. This error is marked non-critical as single-bit errors can be handled by the GPU. See [*Running Field Diagnostics*](https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html#running-field-diag.) to collect additional debug information. | | | |
| 93 | Non-fatal violation of provisioned InfoROM wear limit | No | driver error, user app error |
| 94 | Contained ECC error | No | hardware error, driver error, framebuffer corruption |
| This XID indicates a contained ECC error has occurred. These events are logged when GPU drivers handle errors in GPUs that support error containment, starting with NVIDIAÂ® A100 GPUs.   For Xid 94, these errors are contained to one application, and the application that encountered this error must be restarted.   All other applications running at the time of the Xid are unaffected. It is recommended to reset the GPU container when convenient. Applications can continue to be run until the reset can be performed.   **NOTE**: This XID is only expected on the NVIDIA Ampere A100s, Hopper, and later architectures. If observed on earlier architectures (e.g. Turing), contact support for investigation. | | | |
| 95 | Uncontained ECC error | Yes | hardware error, driver error, framebuffer corruption |
| This XID indicates an uncontained ECC error has occurred.   These events are logged when GPU drivers handle errors in GPUs that support error containment, starting with NVIDIAÂ® A100 GPUs.   For Xid 95, these errors affect multiple applications, and the affected GPU must be reset before applications can restart. Refer <https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html> for GPU Reset capabilities & limitations   **A100 only:**     * If MIG is enabled, drain any work on the other GPU instances, wait for all work to complete, and reset GPU(s) reporting the XID (refer to the GPU reset capabilities/limitations section below). * If MIG is disabled, the node should be rebooted immediately since there is an uncorrectable uncontained ECC error.   (Modal does not support MIG.)   **References:**   <https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/index.html#user-visible-statistics>   This event is similar to Xid 94. However, Xid 94 indicates that the error is suppressed. Xid 95 indicates that the error fails to be suppressed. Other applications on the GPU-accelerated node are also affected. | | | |
| 96 | NVDEC5 Error | No | â |
| 97 | NVDEC6 Error | No | â |
| 98 | NVDEC7 Error | No | â |
| 99 | NVJPG1 Error | No | â |
| 100 | NVJPG2 Error | No | â |
| 101 | NVJPG3 Error | No | â |
| 102 | NVJPG4 Error | No | â |
| 103 | NVJPG5 Error | No | â |
| 104 | NVJPG6 Error | No | â |
| 105 | NVJPG7 Error | No | hardware error, driver error |
| 106 | SMBPBI Test Message | No | â |
| 107 | SMBPBI Test Message Silent | No | user app error |
| 109 | Context Switch Timeout Error | No | hardware error, driver error, user app error, system memory corruption, bus error, thermal issue, framebuffer corruption |
| An error with all possible causes, and usually recoverable. | | | |
| 110 | Security Fault Error | Yes | â |
| This event should be uncommon unless there is a hardware failure. Modal will drain the worker and reset the GPU, and if the problem persists, contact the hardware vendor for support. | | | |
| 111 | Display Bundle Error Event | No | hardware error, driver error, bus error |
| 112 | Display Supervisor Error | No | hardware error, driver error |
| 113 | DP Link Training Erro | No | hardware error, driver error |
| 114 | Display Pipeline Underflow Error | No | hardware error, driver error, framebuffer corruption |
| 115 | Display Core Channel Error | No | hardware error, driver error |
| 116 | Display Window Channel Error | No | hardware error, driver error |
| 117 | Display Cursor Channel Error | No | hardware error, driver error |
| 118 | Display Pixel Pipeline Error | No | hardware error, driver error |
| 119 | GSP RPC Timeout | Yes | hardware error, driver error, system memory corruption, bus error, thermal issue, framebuffer corruption |
| The official NVIDIA docs explains Xid 119 indicates GSP module failures to respond to RPC messages, recommending GPU reset or node power cycle if the issue persists. | | | |
| 120 | GSP Error | Yes | hardware error, driver error, system memory corruption, bus error, thermal issue, framebuffer corruption |
| The official NVIDIA docs explains Xid 120 indicates GSP module failures to respond to RPC messages, recommending GPU reset or node power cycle if the issue persists. | | | |
| 121 | C2C Link Error | Yes | hardware error, bus error |
| The official NVIDIA docs explains Xid 121 indicates corrected errors on the C2C NVLink connection to a Grace CPU, with no operational impact, recommending the GPU reset to retrain the link.     * ["NVIDIA Xid 121: C2C Link corrected error"](https://docs.nvidia.com/deploy/xid-errors/index.html#xid-121-c2c-link-corrected-error) * ["NVIDIA Xid Errors"](https://docs.nvidia.com/deploy/xid-errors/index.html) * ["NVIDIA Xid Errors (PDF)](https://docs.nvidia.com/deploy/pdf/XID_Errors.pdf) | | | |
| 122 | SPI PMU RPC Read Failure | No | hardware error, driver error |
| 123 | SPI PMU RPC Write Failure | Yes | hardware error, driver error |
| Refer to GPU reset capabilities/limitations section provided in Section D.9 of the [Fabric Manager User Guide](https://docs.nvidia.com/datacenter/tesla/pdf/fabric-manager-user-guide.pdf). | | | |
| 124 | SPI PMU RPC Erase Failure | No | hardware error, driver error |
| 125 | Inforom FS Failure | No | hardware error, driver error |
| 126 | CE10: Unknown Error | No | hardware error, driver error |
| 127 | CE11: Unknown Error | No | hardware error, driver error |
| 128 | CE12: Unknown Error | No | hardware error, driver error |
| 129 | CE13: Unknown Error | No | hardware error, driver error |
| 130 | CE14: Unknown Error | No | hardware error, driver error |
| 131 | CE15: Unknown Error | No | hardware error, driver error |
| 132 | CE16: Unknown Error | No | hardware error, driver error |
| 133 | CE17: Unknown Error | No | hardware error, driver error |
| 134 | CE18: Unknown Error | No | hardware error, driver error |
| 135 | CE19: Unknown Error | No | hardware error, driver error |
| 136 | Link Training Failed | Yes | hardware error, bus error |
| 137 | NVLink FLA privilege error | No | user app error |
| This event is logged when a fault is reported by the remote memory management unit (MMU), such as when an illegal NVLink peer-to-peer access is made by an applicable unit on the chip. Typically these are application-level bugs, but can also be driver bugs or hardware bugs. | | | |
| 139 | OFA1 Error | No | hardware error, driver error |
| 140 | Unrecovered ECC Error | Yes | hardware error, driver error, framebuffer corruption |
| This event may occur when the GPU driver has observed uncorrectable errors in GPU memory, in such a way as to interrupt the GPU driverâs ability to mark the pages for dynamic page offlining or row remapping. Modal will drain the worker and reset the GPU, and if the problem persists, contact the hardware vendor for support. | | | |
| 141 | ROBUST\_CHANNEL\_FAST\_PATH\_ERROR | No | â |
| 142 | ROBUST\_CHANNEL\_NVENC3\_ERROR | No | â |
| 143 | GPU Initialization Failure | Yes | hardware error, driver error, framebuffer corruption |
| GPU initialization failure. `GPU_INIT_ERROR` in driver (e.g. error status while polling for FSP boot complete). | | | |
| 144 | NVLINK\_SAW\_ERROR | No | â |
| 145 | NVLINK\_RLW\_ERROR | No | â |
| 146 | NVLINK\_TLW\_ERROR | No | â |
| 147 | NVLINK\_TREX\_ERROR | No | â |
| 148 | NVLINK\_NVLPW\_CTRL\_ERROR | No | â |
| 149 | NVLINK\_NETIR\_ERROR | No | â |
| 150 | NVLINK\_MSE\_ERROR | No | â |
| Example error on NVIDIA B200: `'NVRM: Xid (PCI:0000:5b:00): 150, MSE Degraded Fatal XC0 i0 Link -1 (0x00000000 0x00000000 0x00000000 0x00000000 0x00000000 0x00000000)'`   This error is not expected on non-Hopper GPU architectures. | | | |
| 151 | ROBUST\_CHANNEL\_KEY\_ROTATION\_ERROR | No | â |
| 152 | RESERVED7\_ERROR | No | â |
| 153 | RESERVED8\_ERROR | No | â |
| 154 | GPU Recovery Action Changed | Yes | â |
| Recovery action changed for GPU device. The following state transitions are observed:     * 0x0 (None) to 0x1 (GPU Reset Required) * 0x0 (None) to 0x2 (Node Reboot Required) * 0x0 (None) to 0x4 (Drain and Reset)   Unobserved transitions:     * 0x0 (None) to 0x3   Because all observed transitions require a reset or reboot, this XID is critical. | | | |
| 155 | NVLINK\_SW\_DEFINED\_ERROR | No | â |
| 156 | RESOURCE\_RETIREMENT\_EVENT | No | â |
| 157 | RESOURCE\_RETIREMENT\_FAILURE | No | â |
| 158 | GPU\_FATAL\_TIMEOUT | No | â |
| 159 | ROBUST\_CHANNEL\_CHI\_NON\_DATA\_ERROR | No | â |
| 160 | CHANNEL\_RETIREMENT\_EVENT | No | â |
| 161 | CHANNEL\_RETIREMENT\_FAILURE | No | â |
| 162 | ROBUST\_CHANNEL\_LAST\_ERROR | No | â |
| 163 | Power Smoothing HW Circuitry capability disengaged | No | â |
| No GPU reset required. If power smoothing functionality is desired, the customer needs to resolve the thermal events. If disabled due to timeout, reload the driver or reset the GPU. | | | |
| 164 | Power Smoothing HW Circuitry low lifetime reached | No | â |
| Monitor power swings and expect to replace GPUs if power smoothing is desired. Power smoothing functionality will be disabled soon. Investigate if power swings are acceptable, and if not, take action. | | | |
| 165 | Power Smoothing HW Circuitry lifetime exhausted | No | â |
| Replace GPUs if power swings are not acceptable, and power smoothing is desired. Power smoothing will be disabled by the driver and power swings will occur. Analyze datacenter infrastructure to ensure ability to absorb power swings. | | | |
| 166 | CC traffic seen prior to link properly being configured for encrypted traffic | No | â |
| Applicable to CC (confidential computing) mode only. | | | |
| 167 | PCIe Fatal Timeout | Yes | hardware error, bus error |
| 168 | Reduced GPU Memory Capacity | No | hardware error |
| Errors found in WPR (write protected region). Should only be seen when ECC is disabled. Either ECC should be enabled (to enable row-remapping) or boot re-attempted with shifted WPR. | | | |
| 169 | Internal micro-controller halt (SEC2) | Yes | hardware error, driver error |
| 170 | Interrupt seen in CC mode | No | â |
| Applicable to CC (confidential computing) mode only. | | | |
| 171 | Uncorrectable DRAM Error | Yes | hardware error |
| Additional to Xid 48 providing more details on particulars of fault to differentiate DRAM/SRAM. | | | |
| 172 | Uncorrectable SRAM Error | Yes | hardware error |
| Additional to Xid 48 providing more details on particulars of fault to differentiate DRAM/SRAM. | | | |

[GPU Health](#gpu-health)[[gpu-health] logging](#gpu-health-logging)[Level](#level)[Handling Application-level health issues](#handling-application-level-health-issues)[Xid & SXid](#xid--sxid)