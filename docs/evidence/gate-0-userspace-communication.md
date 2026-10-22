# Android 17 userspace guest communication boundary

Review: **2026-10-22, America/Fortaleza; Windows x86_64, source only.**
**Gate 0 Unresolved; Gates A–G Not reached. ADR-0001 Accepted; ADR-0002 Proposed.**
No engine, backend, guest build, security policy or production architecture is
adopted. The [source ledger](gate-0-userspace-communication-sources.md) identifies
the exact files, revisions and retrieved-byte hashes. Source facts below are not
observed execution. Inferences, proposed constraints and Unknowns are explicit.

## Decision and scope

**INSUFFICIENT EVIDENCE** for a qualifying ordinary-app configuration. The decisive
missing source/configuration fact is a concrete independently confined startup,
endpoint and loss-of-authority arrangement that preserves the selected guest
clients. The upstream executable and launcher do not supply that arrangement.
Userspace transport remains a credible mechanism lead; neither the failed
unchanged arrangement nor this incomplete review proves universal impossibility.

This advances the [boot/HAL assessment](gate-0-android17-boot-hal.md), rather than
repeating its backend existence proof. New findings are:

1. The selected Cuttlefish radio build defines `ON_CUTTLEFISH`, selecting guest
   AF_VSOCK/stream to the modem simulator. The alternate file-channel branch is
   real source, but is not selected by that build. Lights must bind a guest
   vsock listener before Binder registration; a connected host is a different
   requirement. The external vsock camera is conditional, not the default just
   because its source exists. [C, G]
2. The release manifest locates transitive Rust dependencies in
   `platform/external/rust/android-crates-io`. Its Soong backend is version
   0.17.0 and vm-memory 0.16.2, both host-library targets. The vsock executable's
   standalone Cargo file instead requests backend 0.10 and vm-memory 0.12.
   A Cargo build cannot silently stand in for this Android-release build. [M, V, D]
3. The actual receive path maps transferred RAM with read/write `MAP_SHARED`,
   retaining it through atomic guest-memory and queue objects. This is raw RAM
   authority, not bounded message-only authority. [Q, D, V]
4. The executable attempts another backend iteration after daemon disconnect;
   Cuttlefish additionally invokes a process restarter. The guest-to-host
   connection-failure reset routine is a TODO. Neither disconnect nor an absent
   peer establishes PDVA's required terminal rejection or cleanup. [V, C]
5. Cuttlefish Unix endpoint names incorporate the calling host UID. Splitting
   unchanged helpers into different isolated UIDs does not automatically preserve
   endpoint naming. CID and group checks do not authenticate a PDVA session
   against compromised host backend code. [C, V]

R means the unchanged Android 17 r1 ARM64 phone/QEMU reference described in the
earlier records. The comparison target is one guest, QEMU USER vsock device, one
separately constrained backend, and fixed Unix service peers, with no multi-VM
sharing. This is a review target, **not an implemented or fully sourced launch
configuration**. Full phone functionality, OEM-lock, sensors, audio and other
non-vsock channels remain in scope. No service is deleted to make transport fit.

## Guest clients and initialization contracts

The Cuttlefish revision is `283645aacf6cdb56cc31a9362f54d412dbc132a1` [C].
The selected Goldfish radio implementation is
`296e55aa0244e8929e393e00e34471fef2a5d662` [G]. Paths below resolve in the ledger.
This is a source-derived inventory of inspected clients, not a generated complete
product/VINTF/init dependency graph. Unreviewed transitive clients remain Unknown.

| Client and selection | Transport, endpoint and order | Missing endpoint, alternative and classification |
|---|---|---|
| Phone radio: `shared/telephony/device_vendor.mk` → `apex/com.google.cf.rild/Android.bp` → G `hals/radio/main.cpp`, `AtChannel.cpp` | Default CF RILD APEX compiles with `ON_CUTTLEFISH`. Reads `ro.boot.modem_simulator_ports`; opens guest AF_VSOCK/SOCK_STREAM to host CID 2 and that port. AT request/response initialization precedes usable modem operations. C `launch/modem.cpp` creates stream listeners, selecting Unix service sockets when configured for userspace vsock. | Nonpositive port exits 1. Failed socket/connect returns an invalid channel; channel initialization failure is fatal when that initialization is reached. A disconnected reader resets the channel; later requests can reopen it. Required selected phone service, not diagnostics. G's non-Cuttlefish branch opens `vendor.qemu.vport.modem` O_RDWR, but product/device/peer compatibility of selecting it is unverified. This does not authorize removing telephony. |
| Lights: `shared/device.mk` includes `com.google.cf.light`; `guest/hals/light/main.rs`, `lights.rs`, `lights/lights_vsock_server.rs` | Service construction reads `ro.boot.vsock_lights_port` and binds guest CID ANY/stream before Binder registration. A thread accepts host connections; messages are little-endian u32 length plus JSON start/update/stop events. Host must initiate to guest port to observe lights. | Bind error is unwrapped during construction. An absent host connection does not block Binder registration, but updates enter an unbounded Rust channel while accept waits; this is not a bounded no-peer mode. Some send errors end the thread, others break back to accept. Selected runtime HAL; host visualization is separate from HAL registration. The virtio-console alternative is only a TODO, not an implementation. |
| External camera: `shared/camera/device_vendor.mk`, `guest/hals/camera/vsock_camera_provider_2_7.cpp`, `vsock_camera_server.cpp` | Selected only when `TARGET_USE_VSOCK_CAMERA_HAL_IMPL=true`. Positive boot port starts a guest listener; valid JSON width/height/frame-rate settings precede announcing the external camera. Frames/session protocol requires the additional camera implementation. | No positive port means no server start. No valid host settings means no added external device; disconnect removes it. Product else-branch names emulated camera HAL/APEX alternatives, whose complete protocol/rights closure is not established here. Conditional transport, not permission to remove camera behavior required by product policy. |
| Tombstone transmitter: `guest/monitoring/tombstone_transmit/tombstone_transmit.cpp`; host `launch/tombstone_receiver.cpp` | Watches guest tombstone creation, connects to CID 2/boot-selected port, streams file bytes; host receiver can select the Unix listener. Guest filesystem/init must exist first. | Zero port sleeps indefinitely; connect failure logs failure, and removal defaults false. The special init-done property is under MICRODROID. Diagnostic forwarding, not evidence that the phone's init waits for host receipt. Complete product init-trigger closure remains unverified; no diagnostic was removed. |
| ADB/proxy: `shared/device.mk`, `shared/config/init.vendor.rc` | Selected reference properties list `vsock:8382,vsock:5555`; proxy listens at guest vsock 6520 and targets guest TCP 5555. | Debugging transport is not a required PDVA production host grant. Exact adbd failure/guest build selection is not traced here, so its removal is not asserted safe merely from these declarations. No host production ADB is authorized. |
| OEM-lock during firmware boot and selected guest OEM-lock service | Prior [U-Boot investigation](gate-0-android17-uboot.md) traces virtio console index 10 and host `secure_env` peer. | Mandatory retained boot/trust contract; replacing vsock does not satisfy it. Existing unlocked/test-key/rollback blockers remain. Guest-local KeyMint/Gatekeeper do not remove OEM-lock. |
| Sensors, selected local key services, audio and remaining phone interfaces | [Boot/HAL source ledger](gate-0-android17-boot-hal-sources.md) traces sensors hvc18/19 and simulator, and selected guest-local KeyMint/Gatekeeper. C `launch/streamer.cpp` uses a separate local audio socket. | Sensors require their real console peers; absence can be fatal. Local key services are not remote vsock requirements, but their security qualification remains blocking. Audio, display/input, Bluetooth/GNSS and all remaining generated service contracts are not closed by the vsock review. Automotive boot properties do not by themselves select automotive services for this phone. |

Guest AF_VSOCK belongs to the **guest kernel** and virtio driver. It does not
require host AF_VSOCK if the device/backend and all host peers use the Unix path.
Guest driver/module ABI remains subject to the earlier kernel/module Unknowns.
No inspected source establishes that a complete phone can discard every host
communication channel. Conversely, a selected listener is not automatically a
boot dependency on a connected host client.

## Device, memory, routing and failure trace

QEMU pin `4fc49f46dc95d4a27de2509e7fceb2931e91faeb` [Q] requires a chardev in
`vuv_device_realize`, initializes `VHOST_BACKEND_TYPE_USER` and obtains the guest
CID through backend config. Missing chardev or failed initialization/config
retrieval rejects realization. Status changes start/stop the common vsock path.
The device is marked unmigratable; this is not a snapshot/restore solution.
The original Linux QEMU launcher still selects kernel vhost-vsock. TCG alone does
not alter that selection, and the earlier flag restriction remains in force.

The pinned Rust executable [V] advertises three queues (size 256), VERSION_1,
NOTIFY_ON_EMPTY, EVENT_IDX and protocol-feature negotiation; its protocol feature
set is CONFIG. Queue mask 0b11 selects RX/TX handling. Do not assume every QEMU
advertised feature is negotiated, or infer datagram/seqpacket support: the host
route explicitly drops non-stream packet types. Guest feature/driver agreement
has source leads but no executed negotiation result.

QEMU's `vhost_user_fill_set_mem_table_msg` obtains each shareable memory-region
FD, guest address, size, userspace address and backing offset. It rejects a table
with no FDs; memory-region count limits also apply. Its protocol specification
uses Unix ancillary descriptor transfer, not copying RAM in socket messages.
`SET_VRING_KICK/CALL/ERR` carry notification FDs through the vhost-user path.
The selected userspace backend needs Unix sockets, SCM_RIGHTS, shared RAM,
eventfd/epoll, and threads, not `/dev/vhost-vsock` for this path. Optional QEMU
postcopy, shared-object and other protocol branches are not selected merely
because they exist in `vhost-user.c`.

At the release's actual transitive pin [D], `set_mem_table` receives `Vec<File>`,
uses `VhostUserMemoryRegion::mmap_region`, constructs guest regions and replaces
the atomic map. `MmapRegion::from_file` requests PROT_READ|PROT_WRITE with
MAP_SHARED|MAP_NORESERVE. Thus the supplied backing capability must support
writable shared mappings; read-only RAM delegation cannot satisfy this path.
The exact FD creation/open flags of a future Android configuration are **Unknown**,
not inferred from a protocol field. QEMU and backend both access guest RAM; the
backend reads TX descriptors/data and writes RX buffers/used-ring state. Mapping
the supplied regions is broader authority than the ranges used by an honest
queue handler. A compromised backend must be treated as a compromised guest-RAM
owner. No management/Persona/signing memory may share those backing objects.

Two Unix planes must not be confused: the VMM control socket carries vhost-user
and FDs; `uds_path` carries host application streams. Host-initiated connections
send `connect PORT\n`; backend parsing is case-insensitive and the reply on guest
response is `OK PORT\n`. Guest-initiated connections to CID 2 connect to
`uds_path_PORT`. The Cuttlefish SharedFD helper implements both directions, but
derives its path from temporary directory, CID **and getuid()**, and creates the
service socket with mode 0666. Directory DAC/SELinux still matter. Different
isolated UIDs cannot assume the same derived name or sufficient connect rights.

The backend checks guest packet source CID against its configured CID. Non-host
destinations use a process-wide CID map and group intersection; default group
permits sibling communication among configured devices. One device in a backend
avoids that configured sibling route, but is not authentication of management.
CID/group checks in compromised code cannot protect management, and a session
name supplied by that code is not trusted identity. Unix peer credentials,
descriptor provenance and a fresh trusted session binding need their own contract.

Concrete failure limits: failed guest-to-host Unix connect invokes `enq_rst`,
whose body is a TODO/debug message. Do not promise immediate guest connection
reset or a bounded failure deadline. The executable's outer loop attempts to
recreate its backend after daemon wait, while Cuttlefish's wrapper restarts on
killed/dumped/failure exits. Re-creation is **not proven successful**: the shared
CID map persists and the constructor rejects an existing CID. The inspected
code supplies no PDVA manager/epoch enrollment or terminal-loss authorization.

The transitive handler Drop signals and joins vring workers; daemon wait joins
its request thread. The vsock implementation also creates an event-index thread
through an unbounded channel without retaining a join handle. These are honest
cleanup paths, not bounded independent cleanup receipts. Shared mappings,
duplicated service streams, queued work and references held elsewhere require
accounting. VMM death does not itself kill a separately running backend; manager
death has no special authority check in this source. The existing
[capability-revocation record](gate-0-capability-revocation.md) governs survivors
and copied bytes; closing management's FDs cannot revoke another mapping.

## Ordinary Android authority and resources

| Resource | Authority classification and evidence | Remaining falsifier |
|---|---|---|
| Packaged ARM64/Bionic executable and transitive Rust/native libraries | **Unknown** for this backend. Soong uses `rust_binary_host`; dependency libraries are host targets, even where arm64 is enabled. Existing QEMU cross-link is unrelated proof. | Exact Android target/link map must close all imports, libc/TLS/unwind/ABI and 4/16-KiB requirements; reject host glibc artifacts or missing target library. Compilation still does not prove installed execution admission. |
| App-owned storage and public SharedMemory/PFD mechanisms | **Ordinary public app authority**, with existing source semantics; backend use is **narrow explicitly delegated resource / unverified**. | Exact backing object, size, labels, access flags, seals and transfer must support selected mappings without exposing protected files or reuse after uncertainty. |
| Isolated worker received RAM/file FDs | **Narrow explicitly delegated resource**; pinned `isolated_app_all.te` permits specified received-file read/write/map while forbidding direct app-data open. | Actual label/DAC/SELinux transfer and mapping on supported stock builds; no directory grant or arbitrary-open rescue. |
| Unix listeners/connections and SCM_RIGHTS | AF_UNIX is not excluded by isolated policy's other-family creation neverallow; complete **isolated-process authority is Unknown** for these pathname endpoints. | Prove exact create/bind/connect/sendmsg/recvmsg and cross-UID label rules. A Unix socket or a permissive mode alone is not permission or authentication. |
| Host AF_VSOCK and kernel vhost | Isolated policy prohibits creating vsock sockets; host kernel-device route is **restricted/privileged or unqualified**, not ordinary delegated authority. | Reject any retained host AF_VSOCK/vhost requirement; a preopened FD is not a source of otherwise unavailable authority. Guest AF_VSOCK is separate. |
| epoll/eventfd, mmap, futex and pthreads | Native API mechanisms exist; actual composed **isolated-process authority is conditional/unverified**. | Exact Android libc/syscall/filter/label behavior, resource errors and late threads must work without grants. No inference from Linux success. |
| Process creation and seccomp | Platform isolated identity does not imply no fork. Additional pre-exposure NNP/TSYNC restriction remains **conditional/unverified** under the [seccomp findings](gate-0-seccomp-process-control.md). | Successful exact-zero TSYNC across every existing thread before hostile bytes/FDs; compatible later pthreads, no preexisting descendants, no process creation. Dormant diagnostic remains inactive. |
| Executable guest translation memory | **Unknown** Android authority, governed by existing strict TCG analysis; backend RAM transport itself does not require executable guest-RAM maps. | No RWX/fallback or new grant; actual selected QEMU runtime remains unproved. |
| Independent process-tree termination and cleanup receipt | No public app-controlled complete mechanism established; privileged cgroup/force-stop remedies are **root/OEM/development-only or restricted**, outside scope. | Independent closure and durable uncertainty handling after either worker or manager loss, not a compromised worker's CLEAN response. |
| Host networking/external VPN | No Internet socket is intrinsic to the inspected Unix vsock data path; service peers may add egress. **Unknown** end-to-end authority/route control. | Inventory every peer and retained socket; fail closed under required VPN loss with independent packet evidence. Do not import the reference streamer/modem network environment as approved. |

Resource cost includes another address space and RAM mappings (shared backing
does not imply a second physical RAM copy), per-connection TX buffers (default
64 KiB), socket/queue maps, epoll/eventfds, request/vring/event-index threads and
service parsers. Source does not establish a total connection/memory/work budget.
Unbounded channels/maps need explicit limits or independent resource enforcement.
No measured RSS, performance, supported-host minimum or thermal claim is made.

## Four alternatives under the no-uncontrolled-descendants requirement

| Alternative | Source-supported part | Authority/lifetime assessment |
|---|---|---|
| A. Separate untrusted backend, independently confined | Real standalone backend and Unix protocol; does not need to be a child spawned by QEMU. Android framework isolated-service creation is an existing research mechanism. | Prospective minimum lead: trusted startup enrolls two disposable isolated scopes, delegates guest-only RAM and exact endpoints, installs restrictions before exposure. No reviewed backend Android adapter/launch arrangement implements this. Backend's own thread creation is compatible in principle with thread-only filtering, not all-clone denial. Worker death leaves backend authority until independently ended; manager death/restart and exact cleanup remain Unknown. |
| B. Backend within the same constrained worker | Internal modules and functions exist, but are `pub(crate)` under executable `main.rs`; no library target or QEMU embedding adapter is established. | **Unsupported by inspected source/build as a configuration.** Calling an executable main or assuming Rust modules are an embeddable Android library is insufficient. If developed later, RAM is still hostile and resident framework handles still need confinement; one process is not itself a stronger boundary. |
| C. Separate trusted backend/broker without secrets | Concrete backend parser and Unix services exist, but source has no PDVA trusted enrollment/authorization broker. | Trusting the full backend adds vhost control/virtqueue/RAM and application parsers to TCB. Same management UID/address space would not supply the desired separation. No loss/replay policy or independent termination receipt is present. Raw RAM ownership must stay outside protected management. New trusted adapter and its authority remain unverified, not an adopted shortcut. |
| D. Different source-supported transport | Goldfish radio's non-Cuttlefish file channel, existing sensor/OEM-lock consoles and conditional camera product alternatives are real mechanisms. | No source-supported replacement is established for **all** mandatory contracts. The lights console proposal is a TODO. File-channel radio requires coherent product/peer selection. Replacing vsock does not remove OEM-lock, sensors or guest-security blockers. No universal alternate transport is qualified. |

For A/C, the trusted launcher/controller must account for every retained RAM FD,
mapping, eventfd, service stream and IPC endpoint before starting work. Neither
upstream source restricts hostile descendants by itself. No seccomp installation
is implemented here; filtering only QEMU leaves the backend unconstrained.
Late thread creation must remain compatible with the actual linked runtime.
Any compromised backend can attack reachable service parsers and falsify its own
CID/session claims. Only an external enforcing boundary can limit that authority.

## Mandatory configuration disposition and concrete falsifiers

| Requirement | Disposition for proposed comparison target | Falsifier / evidence needed |
|---|---|---|
| Userspace device and stream routing without privileged vhost | **SUPPORTED BY SOURCE** as a mechanism; unchanged R is **CONTRADICTED BY SOURCE** | Inspect exact selected device/config/link objects; any kernel vhost or host AF_VSOCK requirement rejects the userspace target. |
| Every mandatory guest service preserved | **UNKNOWN** | A resolved product/init/VINTF/client-to-peer inventory must account for phone radio, lights, OEM-lock, sensors and other selected clients; any unserved mandatory protocol rejects closure. |
| No uncontrolled descendants, including backend | **CONDITIONAL / UNVERIFIED** | Independently observe pre-exposure restrictions and thread compatibility in each scope; preexisting or post-filter process creation rejects it. |
| No protected management/Persona authority | **CONDITIONAL / UNVERIFIED** | Enumerated backing objects/handles and independent denial of protected resources; same-UID trust or writable protected alias rejects it. |
| Explicit descriptor/memory ownership | **SUPPORTED BY SOURCE** for upstream RW sharing; Android ownership arrangement **UNKNOWN** | Exact FD flags, sizes, labels, receivers and mapping inventory; undocumented aliases or assuming read-only transfer suffices rejects it. |
| Narrow bounded communication | **CONTRADICTED BY SOURCE** for treating unchanged backend as a bounded PDVA bridge | Unbounded channel/connection growth and missing connect-error reset cannot count as bounded rejection. Need actual bounds, error outcomes and independent resource enforcement. |
| No networking/VPN bypass | **UNKNOWN** across service peers | Exact peer egress inventory and independent route/loss evidence; any direct forbidden egress rejects it. |
| Source/build/ABI/license paths | **SUPPORTED BY SOURCE** for identified references; Android build, transitive rights and artifact qualification **CONDITIONAL / UNVERIFIED** | Reproduce the selected Soong or explicitly different pinned build; mismatched Cargo graph, unqualified binary or missing corresponding source rejects it. |
| Reject lost backend/manager/session authority | **CONTRADICTED BY SOURCE** for unchanged executable/wrapper as the enforcer | Drop the control connection or manager authority; no reconnection/restart admission without fresh external authorization. Source supplies no such session check. Missing/ambiguous outcome remains Unknown. |
| Proven cleanup and safe reuse | **UNKNOWN** | Independent completion of every admitted operation and retained scope, including manager loss; FD close, timeout, Binder death or host helper self-report cannot pass. |
| Full configuration qualified under PDVA | **UNSUPPORTED UNDER PDVA REQUIREMENTS** at present | Any mandatory Conditional, Unknown or Unsupported row prevents qualification. This is not a universal impossibility result. |

The strongest next falsifiable experiment is **a source/build closure check of
alternative A's exact endpoint/bootstrap arrangement**, before runtime work:
require one immutable Android-target build graph and explicit preopened endpoint
contract that preserves both routing directions for retained clients across the
two isolated identities, with terminal lost-session admission and no restarter.
Positive means actual source/build artifacts implement that arrangement and
expose no management backing object or kernel-vhost dependency. A hidden pathname
reopen, UID-derived wrong endpoint, missing mandatory peer, new process after
exposure or missing external loss check falsifies it. Merely drawing that
arrangement or cross-compiling the standalone executable does not pass.

Only after that source result could a separately authorized stock release-equivalent
Android experiment test actual FD transfer/mapping, socket labels, thread-only
filter admission and independent teardown using synthetic guest-memory/queue
fixtures. Its negative controls would include wrong endpoint/epoch, read-only
RAM, absent backend, malformed negotiation and manager loss, with independently
observed rejection and cleanup rather than timeout-as-success. **Not run or
authorized here; no phone use is requested.** The existing diagnostic is untouched.

No synthetic test was added to restate code-visible conclusions. No complete
Android build/boot, backend build/integration/execution, third-party binary,
physical-device operation, security-setting change or new runtime dependency was
performed. The independent firmware/trust, kernel/module, guest key-service,
graphics/audio, lifecycle, network and redistribution blockers remain for Gate 0.
