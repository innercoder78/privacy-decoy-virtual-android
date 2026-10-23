# Gate 0: backend entrypoint and preopened endpoint feasibility

Review: **2026-10-22, America/Fortaleza; Windows x86_64, source only.**
Gate 0 **Unresolved**; Gates A–G **Not reached**. ADR-0001 **Accepted**;
ADR-0002 **Proposed**. No architecture, runtime dependency or Android activation
is adopted. Immutable identities and reproduction are in the
[source ledger](gate-0-backend-endpoints-sources.md).

## Disposition and exact falsifier

**B. CONCRETE SOURCE/BUILD BLOCKER — STOP the unchanged configuration.**
The selected executable cannot be configured as an in-process isolated-service
backend consuming only preopened endpoints. This conclusion is about this exact
source/configuration, not all Android architectures or the impossibility of a port.

The decisive source call is V `VsockThreadBackend::handle_new_guest_conn`:
after a guest connection request it constructs `host_socket_path + "_" + dst_port`
and calls `UnixStream::connect`. There is no supplied-stream selection in that
path. In addition, V `VhostUserVsockThread::new` unlinks and binds `uds_path`,
and `start_backend_server` creates a fresh pathname `Listener`. A manager-created
listener at that name is not adopted: these constructors attempt to unlink it
and bind another. Preopening a descriptor without changing these callers does
not satisfy their contracts. V builds `main.rs` as a host executable and provides
no library/JNI entrypoint. [V]

**New distinction beyond PR #30:** the lower-level transport actually has FD
interfaces. D implements `Listener::from_raw_fd` and
`BackendReqHandler::from_stream`; QEMU accepts a socket FD and its QIO layer can
pass ancillary FDs. The blocker is therefore **not universal absence of an FD
mechanism**. It is the selected executable's initialization and per-connection
call graph, including the required radio direction. Connecting those lower-level
interfaces requires source changes, not an undocumented command-line option.
No such changes are made here. [D1–D3, Q1–Q4]

## One configuration under examination

All proposed fields below are **HYPOTHESIS**, not an implemented launch recipe.
**SOURCE OBSERVATION** means inspected immutable code; **FACT** is a repository
observation; **RUNTIME OBSERVATION** is absent. **UNKNOWN** is missing evidence;
**UNSUPPORTED** identifies an unavailable unchanged interface or prohibited route.

| Field | Exact selection and classification |
|---|---|
| Backend and build | SOURCE OBSERVATION: V `28233ae213b24a9a35f25e9e49bcadee2bf93821`, Soong `vhost_device_vsock`, `rust_binary_host`, crate root `src/main.rs`, edition 2021, package 0.1.0. No Android device/library variant declared in that file. |
| Transport dependencies | SOURCE OBSERVATION: D `1f5e95cd6e996995023c9c0f7df0f15a8a43269e`; `libvhost_user_backend` 0.17.0, `libvhost_android` 0.13.0, `libvm_memory_android` 0.16.2 are host libraries. QEMU pin Q `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, USER vsock device, not kernel vhost. |
| Actual target ABI | UNKNOWN: no backend artifact or compiler invocation produced. The selected module is host-only; its exact host triple is not established by its name. HYPOTHESIS for a port: Rust `aarch64-linux-android`, Android arm64-v8a/Bionic. Neither aarch64 Linux nor Android guest API 37 establishes this host ABI/minimum. |
| Entrypoint | SOURCE OBSERVATION: executable `fn main`, crate-private start functions, process-wide logging initialization and error `exit(1)`. UNSUPPORTED: loading that executable as a library or using a nonexistent JNI entry. |
| Process creator | HYPOTHESIS: framework/zygote creates two dedicated isolated-service processes with separate isolated UIDs, one for engine and one for backend. Manager is neither worker's Linux parent. No same-UID native child is substituted for the second scope. |
| Endpoint origin | HYPOTHESIS: trusted manager establishes exact connected AF_UNIX streams before hostile exposure and explicitly transfers descriptors via Binder/PFD. Descriptors are not inherited from management by framework-created workers. No pathname/directory-opening capability is delegated. |
| RAM ownership | HYPOTHESIS: one dedicated guest backing object, writable by engine and backend; no manager/Persona/policy/signing/other-guest object in it. QEMU's native memfd creation path is a source reference, not an implemented manager-FD injection interface. |
| Guest clients | SOURCE OBSERVATION from PR #30: selected radio initiates guest-to-host stream; lights listens in guest and requires host-to-guest stream for updates. Preserve both directions; conditional external camera remains separately conditional. |
| Admission | HYPOTHESIS: trusted manager authenticates live framework enrollment, caller and fresh generation, checks every protected operation and persists uncertainty before delegation. UNKNOWN: implemented independent enrollment/confinement and runtime transfer authority. V has no such PDVA admission interface. |
| Restrictions/loss | HYPOTHESIS: independently justified pre-exposure NNP/exact-zero TSYNC in both scopes, thread-only legacy clone policy, no process descendants, no restart after loss, indefinite lockout if required cleanup is unproved. No existing code is represented as implementing this contract. |

## Build closure and invocation

SOURCE OBSERVATION: V's complete direct Soong rustlibs list is `libbyteorder`,
`libclap`, `libconfig_rust`, `libenv_logger`, `libepoll`, `liblog_rust`, `libserde`,
`libserde_yaml`, `libthiserror`, `libvhost_android`, `libvhost_user_backend`,
`libvirtio_bindings`, `libvirtio_queue`, `libvirtio_vsock`, `libvm_memory_android`
and `libvmm_sys_util`. D backend depends on libc, log, vhost, virtio bindings/queue,
vm-memory and vmm-sys-util. D vhost adds bitflags/uuid; D vm-memory adds arc-swap,
libc and thiserror, with atomic/bitmap/mmap features. These names are graph edges,
not a completed transitive dependency or license closure. [V, D]

V's standalone Cargo graph requests backend 0.10, vhost 0.8 with
`vhost-user-slave`, vm-memory 0.12, virtio-queue 0.9 and vmm-sys-util 0.11.
It cannot stand in for the release Soong graph above. D's vhost features instead
include `vhost-user` and `vhost-user-backend`. Host arm64 enablement on vm-memory
does not create a device variant. Changing only the top module type would leave
host-only dependency edges unresolved. [V, D]

**UNKNOWN:** exact Android rustc/standard-library/compiler-runtime versions,
panic/unwind/TLS closure, complete proc-macro and native dependencies, Bionic
symbol/API availability, linker namespace, ELF type/imports/DT_NEEDED, 4/16-KiB
compatibility and supported host minimum. Rust std is required by the inspected
code (threads, Unix streams, files and synchronization); its Android target
artifacts are not supplied by the existing NDK alone. No reviewed Rust compiler,
Android std or complete Soong build inputs were located in the inspected desktop
toolchain. Existing CI builds C/QEMU, not this Rust graph.

**Compile/link experiment: NOT RUN.** The unchanged source already fails the
required entrypoint/endpoint contract, and complete pinned build inputs are absent.
Downloading a floating Rust toolchain or resolving standalone Cargo would test a
different claim. There is no output ABI to inspect and no successful-compilation
claim. Even a future successful link would not establish installed Android authority.

INFERENCE: a port needs a genuine library target/export and Android dependency
variants, explicit owned endpoint inputs, lifecycle/error handling and a reviewed
load/thread order. Renaming an executable `.so` supplies none of these. Packaging
and invoking a future library under ordinary app authority, including distribution
rights and transitive license compliance, remain UNKNOWN; existing native harness
packaging evidence is not backend execution or redistribution approval.

## Endpoint contracts, including the lower-level positive controls

| Plane | SOURCE OBSERVATION | Consequence for the selected configuration |
|---|---|---|
| QEMU control socket | `tcp_chr_parse` accepts mutually exclusive path/fd/host and maps fd to FD address. `socket_get_fd` resolves a monitor name or numeric FD and checks socket type. `socket_connect` returns it without pathname connect. Choose client mode and no reconnect; `reconnect-ms` is explicitly rejected for FD addresses. [Q1,Q2] | Existing preconnected socket input, with ownership/close semantics; a normal file or wrong peer is not a valid vhost-user endpoint. Type validation does not authenticate a session. No manager-to-worker adapter exists here. |
| QEMU ancillary transfer | `qio_channel_socket_set_fd` uses getsockname and enables QIO FD_PASS for AF_UNIX. `tcp_chr_set_msgfds` tests this QIO feature; char-fe dispatches to it. The separate chardev FD_PASS advertisement still has a TODO for FD addresses. [Q1,Q3,Q4] | The TODO alone is not proof that ancillary transfer fails. The inspected vsock/vhost-user path does not use that advertisement as its admission check. This is a source trace, not an observed transfer. |
| D listener injection | `unsafe Listener::from_raw_fd(fd)` owns a UnixListener with `path=None`; Drop does not unlink a path. `VhostUserDaemon::start(listener)` accepts one connection and starts a request thread. [D1,D3] | Real API for an already-listening socket, not a connected stream/socketpair endpoint. Caller must transfer unique FD ownership and provide correct socket state; it is not a credential check. |
| D connected stream | `BackendReqHandler::from_stream(UnixStream, Arc<S>)` is public; its handle_request path processes vhost-user requests. Daemon's handler field and `start_daemon` are private; public `start_client` takes a pathname. [D2,D3] | Real lower-level connected-stream API. No public daemon `start(stream)` overload or automatic V integration; an adapter/change must assemble the handler/lifecycle correctly. |
| V control startup | `start_backend_server` always calls `Listener::new(path,true)`. [V] | No existing CLI/config FD selector; startup source change required. |
| Host initiates to guest, including lights | `VhostUserVsockThread::new` removes/binds uds_path, sets nonblocking, registers epoll; later accepts streams and parses connect-port messages. [V] | A preopened connected stream cannot be inserted via current initialization. Changing only control-listener startup leaves this separate bind/accept path. |
| Guest initiates to host, including radio | `handle_new_guest_conn` connects to a path formed from the guest destination port, sets nonblocking, then privately `add_new_guest_conn` duplicates the stream and registers it. [V] | Mandatory late pathname opening, not merely startup naming. No fixed authorized port-to-FD map is exposed. Reconnect/repeated guest requests require their own admission/lifetime semantics. STOP this unchanged path. |

SOURCE OBSERVATION: S `app.te` explicitly permits already-connected unnamed
appdomain Unix streams received through IPC (`getopt getattr read write shutdown`)
and app-to-app Binder calls. Its comment explicitly distinguishes this from
sock_file/connectto permission. `isolated_app_all.te` permits specified received
file mappings but prohibits direct app-data-file open and non-Unix socket creation.
These sources support **conditional plausibility** of two separate scopes using
delegated connected streams; they do not prove cross-UID bind/listen/accept or
the whole compiled SELinux/DAC policy. Manager-owned listener delegation is not
interchangeable with connected-stream delegation. SCM_RIGHTS, Binder file-transfer
hooks, FD use, object labels, mmap and ioctl/epoll operations still need exact
installed-policy evidence. Mode 0666 and matching UID-derived names cannot supply it.

## RAM and descriptor authority

SOURCE OBSERVATION: Q `hostmem-memfd.c` calls `qemu_memfd_create`; that function
uses MFD_CLOEXEC, optional MFD_ALLOW_SEALING, ftruncate and F_ADD_SEALS. The
hostmem sealing selection is GROW/SHRINK/SEAL, **not WRITE**. Its allocation
failure returns an error; do not confuse it with the separate best-effort
`qemu_memfd_alloc` fallback. Normal non-hugetlb, share=true is the bounded source
selection to examine; no privileged hugepage allocation is proposed. [Q5,Q6]

SOURCE OBSERVATION: QEMU sends backing FDs plus guest-physical base, size and
offset in SET_MEM_TABLE, and notification descriptors through vring messages.
D receives owned `File`s, maps PROT_READ|PROT_WRITE/MAP_SHARED|MAP_NORESERVE,
replaces the atomic memory map and updates vrings/backend. Old memory snapshots
can remain referenced. V reads TX and writes RX/used-ring data. [PR #30 ledger]

INFERENCE: enforceable object separation must treat the backend as authorized
to mutate **every byte reachable through each delegated writable backing object**,
not just the honest queue ranges. A raw FD can expose more of an object than
the protocol-advertised range. Separate guest-only objects are required. Engine
private heaps/TCG metadata, backend private heaps, management memory, Persona
master, signing/security policy and other guests must never be in that backing.
Kernel process/mapping enforcement is the prospective boundary; parser discipline
is not a boundary after compromise. A read-only FD cannot satisfy this map.

The exact crossing inventory is: manager-to-each-worker authorized connected
stream endpoints (proposed Binder/PFD transfer); engine-to-backend guest RAM FDs,
range metadata and negotiated kick/call/error notification FDs (vhost-user
SCM_RIGHTS); separate service streams for radio and lights in opposite directions.
No directory FD, management database, Persona master, signing key, arbitrary
Binder proxy or host GPS capability belongs in that inventory. Exact API to inject
all these resources into V is missing. PFD/SCM_RIGHTS duplicate references rather
than copying a numeric FD into a new process's table. Queueing transfers can retain
references. Close-on-exec is not revocation or protection against dup.

INFERENCE: backend death releases its own maps/references; surviving engine,
queued transfers or other recipients can retain the object. Engine death leaves
backend maps. Closing management's copy or reducing future mapping protections
does not revoke existing maps or undo writes/copied bytes. Full reference and
outstanding-work closure remains UNKNOWN. See the existing
[revocation evidence](gate-0-capability-revocation.md).

## Confinement and session failure obligations

SOURCE OBSERVATION: V's eight source modules use Rust thread spawning, not an
explicit child-process launch on the inspected startup/transport path. Daemon
construction/request processing and event-index handling create further threads;
one event-index join handle is not retained. This is not proof about the complete
unbuilt dependency/constructor graph, nor a constraint on compromised native code.
The reference Cuttlefish process-restarter is excluded from this candidate.

HYPOTHESIS: trusted platform startup and reviewed native load closure must precede
NNP and exact-zero TSYNC; hostile parsing/FD exposure follows independently justified
installation in **each** scope. Existing ART/Binder threads require synchronization;
native constructors must not create an uncontrolled earlier descendant. Later
pthread creation requires the constrained legacy clone flags supported by the
reviewed Bionic path; blanket clone denial is not the candidate. Fork-like clone,
fork/vfork where present, clone3 and exec paths need their own denials/ABI coverage.
The dormant Android diagnostic is not activated and proves none of this. Independent
installation, inherited FD closure and no earlier descendants remain UNKNOWN.
See [seccomp](gate-0-seccomp-process-control.md) and
[bootstrap ordering](gate-0-android-seccomp-bootstrap.md).

| Failure | Required trusted disposition; current evidence limit |
|---|---|
| Backend refuses stop, or either worker survives the other | Deny future protected admissions; request legitimate framework teardown but retain CleanupUnknown until independently complete. Cooperative STOP, daemon wait and CLEAN are insufficient. |
| Manager dies/restarts | Persist uncertainty before delegation; fresh manager defaults deny, does not reauthorize or silently bind/restart. V has no manager-loss admission check; its loop attempts another backend iteration. Framework auto-create reconnection is not safe recovery. |
| Endpoint references remain; stale identifiers or replay | Trusted owner must reject stale generation/caller/replay at each mediated operation. CID, pathname and worker-supplied token do not authenticate. Existing raw streams need no new authorization to be used; V supplies no revocation barrier. |
| Backend attempts self-restart or workers overlap | Independently installed process restrictions would prevent new process creation, not in-process backend reconstruction. Uncertain old scope blocks replacement; a new UID or binding does not prove old cleanup. |
| Mapping survives elsewhere | Keep resource lockout; single-process death cannot certify reference closure. Never reuse the object based on EOF or a worker report. |
| Network/VPN becomes invalid | Deny further authorized egress; these Unix paths establish no external-VPN routing guarantee and introduce no host VpnService. Raw egress sockets would require separate closure. |
| Memory, queues or connections exceed limits | Fail closed under independently enforceable limits. V's unbounded channels/maps and per-connection buffers do not establish a total quota; a negotiated queue size is not a whole-process memory limit. |

Refusing future broker operations, refusing new connections, closing one FD,
terminating one process, proving every relevant exit, proving reference/work
closure and undoing disclosure are **seven distinct properties**. No inspected
mechanism provides all seven; undoing adversary copies is unsupported. Existing
[Android lifetime](gate-0-android-lifetime-authority.md) and
[exception evidence](gate-0-android-lifecycle-exceptions.md) still prohibit using
unbind, Binder death, timeout, restart or a reboot-clock shortcut to clear lockout.

## Negative controls and smallest next evidence

These are manual code-grounded rejection checks, **not executed behavioral tests**:

- Reject host ELF/glibc-as-Android, Cargo-as-Soong and executable-as-library claims
  using the actual build declarations; missing Android runtime imports stay UNKNOWN.
- Reject preopened-listener-as-connected-stream using D's distinct constructors.
  Reject prebinding-as-injection using V's unlink/bind; reject port naming as a
  supplied FD using its late connect. Wrong UID naming or mismatched peer does not
  become authorized because connect succeeds.
- Do not misread QEMU's chardev FD_PASS TODO as failure: inspect the actual QIO
  feature and send dispatch. Conversely socket-type acceptance is not peer/session
  authentication, and reconnect-ms is explicitly incompatible with fd addressing.
- Reject read-only RAM, protected manager backing and kernel vhost substitutions.
  Reject hidden-process/no-descendant claims based only on honest thread code;
  full load/filter ordering remains UNKNOWN.
- Reject automatic restart after loss, missing radio/lights peers, worker CLEAN
  as independent cleanup, and missing provenance/rights as distribution approval.
- No skipped, zero-step or prior unrelated test is reported as this backend's
  compilation, Android execution or successful rejection.

The unchanged configuration is already falsified; a phone test cannot supply its
missing source interfaces. The smallest useful next **source/build** experiment,
only after a separately reviewed research adaptation is in scope, is an Android
library build with the exact release dependency versions and explicit owned
connected-stream inputs for control **and both service directions**. Its independent
falsifier is any retained pathname bind/connect on those admitted paths, required
subprocess, unresolved/non-Android import, or failure to preserve the selected radio
and lights protocols. Pin compiler/std/full inputs first; inspect the actual ELF,
exports, imports, dependencies and constructors. No such adaptation or experiment
is implemented or approved by this record. Security/runtime qualification would
remain separate even after that scoped success.
