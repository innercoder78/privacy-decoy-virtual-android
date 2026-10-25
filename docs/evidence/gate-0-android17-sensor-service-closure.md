# Gate 0: Android 17 sensor service and ordinary-app communication closure

Review: **2026-10-25; source-only, Windows x86_64.** No guest, simulator,
Android host, VM or phone execution. **Gate 0 Unresolved; Gates A–G Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No engine is selected.

## Result and exact question

Can the selected Android 17 ARM64 phone sensor subsystem receive its required
virtual devices and a complete matching peer inside a distributable ordinary
application on stock nonrooted Android, with management and Persona authority
outside the hostile guest and worker?

**Disposition: scoped incompatibility / STOP for the unchanged examined
configuration.** Its simulator is explicitly a non-Android build-host executable,
and its launcher/QEMU pipe backend opens ambient FIFO paths rather than accepting
the confined connected-endpoint arrangement under investigation. The complete
ordinary-app sensor peer is **not established**. This is not a universal
impossibility result: guest virtio consoles and the simulator's descriptor-based
channel implementation are real source mechanisms. An Android port with explicit
endpoint ownership remains a **conditional research lead**, requiring source,
build, protocol and enforcement work; it is not a Gate 0 pass. [C-hostbuild]
[C-defaults] [C-launch] [Q-pipe]

New closure beyond the merged surveys:

1. The framework-facing service is **AIDL V3 multihal**, loading a **HIDL 2.1
   sub-HAL ABI** with the Cuttlefish entry point and goldfish implementation.
   It is not the separate goldfish `qemud` transport. Both guest console opens
   and raw-terminal setup precede a synchronous sensor-mask handshake and service
   registration. Missing devices can abort; present devices without a reply can
   block initialization without a deadline. [I-build] [I-service] [C-entry] [G-hal]
2. The actual peer needs four guest-transport FDs and a valid WebRTC-side FD.
   The selected launcher also supplies a kernel-log event pipe for reboot state.
   Default synthetic data does not require host sensor acquisition or Internet
   traffic; a live control producer is distinct from a valid control descriptor.
   [C-main] [C-proxy] [C-pair]
3. Phone enumeration advertises eight sensors, but the selected proxy sends only
   five periodically. Temperature, proximity and humidity constants exist in the
   simulator but are excluded from that reporter. The guest's on-change activation
   path can emit its `-1e+30` no-value sentinel for those three. Pressure is generated
   as 1013.25 hPa while the selected sensor descriptor declares maxRange 800.
   These are concrete consistency gaps, not observed device failures. [C-model]
   [C-proxy] [G-list] [G-header] [G-hal]
4. The proxy ignores `time:`, `set-delay:` and `set:` control payloads, replying
   only to a `list-sensors` prefix. Continuous events are cached and restamped by
   guest batching; fresh timestamps do not prove fresh provider values. Console
   backpressure can lose bytes, and the framing layer allocates from an untrusted
   length before the guest's small-buffer limit. No epoch, authorization or
   fail-closed sensor policy is supplied by these mechanisms. [C-proxy] [G-wire]
   [G-hal] [T-channel] [T-message] [Q-console] [Q-bus]

The [boot/HAL assessment](gate-0-android17-boot-hal.md) and its
[ledger](gate-0-android17-boot-hal-sources.md) already identified hvc18/19 and the
simulator. [Userspace communication](gate-0-userspace-communication.md), its
[ledger](gate-0-userspace-communication-sources.md), and
[backend endpoints](gate-0-backend-endpoints.md) preserve the distinct vsock
blockers. This record resolves the sensor selection/peer/protocol questions;
it does not repeat their complete-guest surveys or repair unrelated blockers in
[complete Android](gate-0-complete-android.md) and its
[ledger](gate-0-complete-android-sources.md).

## Live preflight and scope

GitHub's main API and fetched `origin/main` agreed on
`7461205687c6eb0f4a4845726520b926fd335ac1`, the merge of
[PR #38](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/38).
Recent history includes PR #37 and PR #36; the initial local PR #38 head tree
had no difference from current main. Connector open-PR search and the REST
open-PR inventory both returned zero. Consequently there were no open heads,
bases, diffs/files, reviews, comments, threads or associated checks/jobs/logs to
reconcile, and no existing sensor research PR to update.

Existing exact-main [foundation run 40170473195](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40170473195)
completed successfully: foundation job `121100102124` and Windows job
`121100102267`. [Android run 40170473074](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40170473074)
and job `121100101913` also succeeded. Job steps and full logs were retrieved;
checkout receipts match main. Foundation logs include 141 repository tests,
27 readiness tests, 45 image controls, four frame controls and existing native
controls; Windows records 45 image and four frame controls. Android logs record
the existing substrate build/inspection, not sensor or guest execution. These
are pre-existing hosted results, not tests performed by this investigation.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational with no incidents during preflight.

The initial tracked tree was clean, one worktree, no stashes; branch and ignored
Gradle/CMake/build inventories were inspected and preserved. No applicable
AGENTS.md was found. The focused branch starts at verified main. Existing native
sources, dependency inventory, Gradle verification metadata, source catalog,
provenance policy, workflow pins and path filters were reviewed. No retained
binary is newly attested or executed. The change contains only this record and
the evidence index, with regular file modes and no dependency or binary addition.
Initial shell network denial was resolved through approved network operations;
no system security setting or permission was changed.

Governing inputs remain requirements, architecture, acceptance criteria, gates,
security boundaries, threat model, Persona policy, testing, roadmap, governance
and both ADRs. Inherited limits come from
[host display](gate-0-host-display-boundary.md),
[worker containment](gate-0-worker-containment.md),
[capability revocation](gate-0-capability-revocation.md),
[Android lifetime](gate-0-android-lifetime-authority.md), and
[research recovery](gate-0-research-recovery.md). No normative document is changed.

Evidence terms: **S** source observation; **I** inference from those sources;
**H** conditional hypothesis; **U** Unknown. All sensor runtime cases are **Not
run**. Required below means required by this selection, not by every Android
product. No synthetic source channel or hand-authored test substitutes for it.

## Selected product, services and device graph

Selection is the existing Android 17 r1 `aosp_cf_arm64_phone`, `vsoc_arm64`,
nonprotected phone reference, with default sensor package/feature selection and
the QEMU manager's console layout. No custom `LOCAL_SENSOR_PRODUCT_PACKAGE` or
`LOCAL_SENSOR_FILE_OVERRIDES=true` is assumed. These hooks are conditional
configuration, not a supplied replacement. Full resolved release configuration,
generated image and runtime artifact correspondence remain U. [C-product]
[C-phone] [C-product-sensors]

```text
Guest SensorService / AidlSensorHalWrapper
  -> guest Binder ISensors/default, AIDL V3; event/wakelock FMQs
  -> android.hardware.sensors-service.multihal / HalProxyAidl / HalProxy
  -> /vendor/etc/sensors/hals.conf (also supports /odm config)
  -> android.hardware.sensors@2.1-impl.cuttlefish.so
  -> sensorsHalGetSubHal_2_1 / goldfish::MultihalSensors
  -> VconsoleSensorsTransport: /dev/hvc18 control + /dev/hvc19 data
  -> guest virtio_console + hvc tty driver, virtqueues
  -> QEMU virtconsole on virtio-serial.0
  -> pipe chardev: sensors_{control,data}_fifo_vm.{in,out}
  -> SensorsHalProxy control/report threads -> SensorsSimulator
       <- separate AF_UNIX control peer (WebRTC-facing commands)
       <- kernel_log_monitor event pipe (BootloaderLoaded notification)

PDVA trusted manager / Persona policy provider -> MISSING authorized adapter
Confined Android-host peer/build/lifetime ownership -> MISSING implementation
```

| Stage | Selection, authority and enforcement classification |
|---|---|
| Framework and service | S: `AidlSensorHalWrapper::connect` finds declared `ISensors/default`, waits for service, prepares event and wake-lock queues and calls initialize. Service constructs HalProxyAidl (which inherits HalProxy) before addService, checks registration success, joins Binder pool. Required guest-side Binder/FMQ; no host Binder passthrough. Guest framework and HAL are untrusted for host protection. [N-wrapper] [I-service] [I-aidl] [I-aidlheader] |
| Multihal load | S: vendor binary, rc class `hal`, user `system`, groups including wakelock/input/context_hub, BLOCK_SUSPEND and rtprio limit. VINTF fragment is AIDL version 3. HalProxy loads config library and resolves the 2.1 entry point; vendor config names the Cuttlefish library. These privileges exist inside the guest, not in the ordinary host app. Guest linker/init/SELinux/generated manifest correspondence U. [I-rc] [I-vintf] [I-loader] [C-conf] |
| Virtual transport | S: two O_RDWR guest tty opens; `SetTerminalRaw` performs tcgetattr/cfmakeraw/tcsetattr and verifies settings. Either open/raw failure is fatal. ueventd sets both nodes 0660 system:system; guest file contexts label both sensors_device. The guest kernel owns device operations; no real host hvc device is needed. [C-entry] [F-fd] [C-uevent] [C-contexts] |
| Virtual device | S: virtio-serial PCI controller plus ordered virtconsole devices; guest virtio-console dispatches console-port announcements to hvc allocation. Device model parses hostile guest queues; host sandbox would have to contain device-model compromise. Exact built kernel/module config, PCI and feature negotiation remain U. [C-qemu] [K-console] [K-hvc] [Q-console] [Q-bus] |
| Host peer | S: launcher creates four named FIFOs, passes FDs plus control/event FDs to host executable. Sensor proxy uses bytes, not guest RAM FDs or vhost-user. H: separately confined app peer with admitted channels. Actual Android entrypoint, packaging, cross-UID transfer and resource limits are missing/U. [C-launch] [C-main] [C-hostbuild] |
| Policy owner | Required PDVA authority stays outside guest/device worker. Existing simulator has no Real/Decoy/Empty/Deny API, caller identity, epoch or trusted stop receipt. It cannot enforce manager policy against a compromised peer. Missing implementation; enforcement U. |

The phone feature set includes accelerometer and compass via
`handheld_core_hardware.xml`, plus ambient temperature, barometer, gyroscope,
light, proximity and relative humidity from the sensor product file. The proxy's
phone/default mask is bits 0,1,2,4,5,6,7,8 = **503 (0x1f7)**, intersected with
goldfish's sensor-count mask. This is a source-derived value, not a measured
enumeration. Orientation ID 3, uncalibrated IDs, hinge and wear-only off-body
detection are not in this phone mask; other form factors have separate branches.
The host's ID 31 is an internal orientation input, not an advertised Android
rotation-vector sensor. Guest fusion may derive additional sensors; a full
framework-visible/fused inventory is U. [N-features] [C-product-sensors] [C-ids]
[C-proxy] [G-list] [G-hal]

The installed `cuttlefish_sensor_injection` utility calls guest AIDL directly
and requests DATA_INJECTION mode. It is a separate explicit guest diagnostic
path; package inclusion is not evidence it runs during normal startup. It neither
opens the two consoles nor replaces their initialization handshake. Invoking it
through shell grants, or injecting into the host HAL, is not the proposed
ordinary-app sensor solution. It was not run. [C-inject] [G-hal]

## Ports, initialization, framing and ownership

**S:** the QEMU manager increments `hvc_num` for every console, including null
sinks for disabled features. Positions 0–17 are retained before sensors; 18 maps
to `sensors_control_fifo_vm` and 19 to `sensors_data_fifo_vm`. `add_hvc` creates
`pipe,id=hvcN,path=...` and a `virtconsole,bus=virtio-serial.0,chardev=hvcN`.
The pipe backend reads `.in` and writes `.out`, each opened O_RDWR. The launcher
therefore gives the simulator `*_from_guest_fd` from `.out` and
`*_to_guest_fd` from `.in`. It unlinks/recreates FIFOs at mode 0660; SharedFD's
FIFO helper opens O_RDWR. Missing split files cause QEMU to try the unsuffixed
path, then fail if that cannot open. This fallback is a different channel source,
not safe endpoint admission. [C-qemu] [C-launch] [F-fd] [Q-pipe]

**I:** names alone do not guarantee device identity. Kernel
`init_port_console` allocates a virtual-terminal number and calls `hvc_alloc`;
the latter chooses tty indices from registered/empty slots and then a counter.
Preserving console creation/discovery order and the selected driver configuration
is necessary for the expected hvc18/19 assignment. A different layout, omitted
sink, extra console provider or generic `virtserialport` is not demonstrated
compatible merely by giving a host chardev the same name. No actual numbering
was observed. This path is neither AF_VSOCK nor `/dev/qemu_pipe`; the goldfish
`entry.cpp` with `qemud_channel_open("sensors")` belongs to the separate ranchu
module, not the selected Cuttlefish entry. [K-console] [K-hvc] [G-entry] [G-build]

**S: initialization sequence.**

1. Host launcher establishes FIFOs, an AF_UNIX/SOCK_STREAM socketpair and event
   pipe; command FD handling retains duplicates for the subprocess. Simulator
   duplicates the four FIFO FDs and WebRTC FD, closes original numeric arguments,
   and fatally rejects invalid duplicates. Kernel-event FD is duplicated too but
   is not subjected to the same IsOpen fatal check. [C-pair] [C-launch] [C-main]
   [C-subprocess]
2. Simulator constructs synthetic state and three proxy threads: control
   responder, periodic reporter, reboot monitor. Main waits for WebRTC messages.
   A quiet valid WebRTC endpoint does not prevent HAL threads from serving
   defaults. No complete WebRTC network stack is linked by the simulator module;
   it expects a framed local stream peer. EOF/error in its main loop is logged
   and retried without backoff. [C-main] [C-proxy] [C-hostbuild]
3. Guest sub-HAL opens both raw consoles, constructs a transport and sends
   `list-sensors`. Receive is synchronous, with a 63-byte destination limit;
   negative receive/send or failed `%u` parse is fatal. A numeric prefix with
   trailing content is not strictly rejected. A silent open channel can block
   indefinitely in ReadExact. HalProxy construction therefore need not reach
   Binder registration. Zero mask is parseable but conflicts with the selected
   advertised feature set; it is not an approved Empty implementation. [G-hal]
   [C-entry] [T-channel] [F-buf] [I-service]
4. Host replies with decimal mask plus newline and sets `hal_activated_` true.
   Guest starts a listener and batch thread, sends `time:<guest ns>`,
   `set-delay:<ms>` and `set:<sensor-name>:1` for every available sensor. The
   host control handler consumes but does nothing with these commands. Its
   reporter uses a fixed 1000-ms interval; framework activation/batching filters
   and schedules guest delivery separately. `set:magnetic-field:1` is the
   control vocabulary; `magnetic:x:y:z` is the data vocabulary. [C-proxy]
   [G-hal] [G-wire] [G-list]
5. `BootloaderLoaded` resets only `hal_activated_` in the host proxy. It is not
   a PDVA instance/Persona change, data wipe, FD revocation or authenticated
   reboot receipt. A valid event FD with EOF/parse failure trips CHECK; an invalid
   FD simply prevents the monitor loop from running. The selected event producer
   watches the guest kernel-log transport, not privileged host kernel logs.
   Its length-prefixed JSON uses native `size_t`, adding host ABI correspondence
   and unbounded-length parsing obligations. [C-proxy] [C-events] [C-loglaunch]

**Wire contract:** `RawMessage` has a 31-bit uint32 command, 1-bit response flag,
uint32 payload size and payload bytes. SharedFdChannel reads/writes the native
struct representation using `sizeof(RawMessage)`, without endian conversion,
version, authentication, epoch, checksum or application size cap. Exact compiler
bitfield layout/endian agreement must be established for any port; do not assume
a portable wire ABI from these declarations. Guest sends command 0; host response
helper uses command 2 and SendResponse sets the response bit. The HAL transport
and host control parser do not validate these header fields as protocol identity.
The text payload, not a sensor ioctl, selects list/set/data behavior. [T-header]
[T-message] [T-channel] [C-entry] [C-proxy]

Receive allocates the declared payload before reading it and before the guest
transport applies 63/255-byte caller limits. Truncated header/payload yields an
error only once the underlying read ends/fails; a peer holding the channel open
can stall it. The guest listener holds `m_mtx` while parsing/receiving, so a partial
frame can delay other HAL operations. No length quota, deadline or resynchronization
is established. Malformed numeric data generally logs an unparsed message;
`sscanf` success does not establish finiteness, range or exact trailing syntax.
[T-channel] [T-message] [F-buf] [G-epoll] [G-wire]

**Lifetime and pressure:** guest transport owns SharedFD references and extra
unmanaged duplicates used for epoll; destructor closes the latter. The static
MultihalSensors instance is deliberately retained for process lifetime. Listener
restart constructs another transport from the **same captured FDs**, not new
opens or an authenticated new peer. EPOLLHUP/ERR causes that restart attempt;
control setup sends are fatal on failure. A 60-second epoll timeout is only a
wait interval, not a liveness deadline. [C-entry] [G-hal] [G-epoll]

The proxy's threads reference its state and simulator; the header provides no
explicit stop/join lifecycle, while main loops forever. Control/report errors
set `running_` false but do not terminate main or necessarily unblock another
blocking read. SharedFD closes only when references end. Both FIFO sides' O_RDWR
opens can retain readers/writers and mask peer disappearance as EOF. Manager FD
close cannot revoke inherited/duplicated FDs. No bound on total process memory,
thread queues, logs, CPU or descriptor use is supplied. [C-proxy] [C-proxy-header]
[C-main] [F-fd]; inherited revocation/lifetime limits remain binding.

QEMU `flush_buf` consumes output when no backend is connected. On a short write,
it throttles generic serial ports but **not console ports**; the bus advances the
unthrottled element, allowing lost console bytes. Source explicitly distinguishes
console behavior from reliable serial-port expectations. Framed sensor traffic
cannot assume backpressure is lossless, and changing to `virtserialport` would
also change the guest device contract. Host-to-guest flow uses guest-ready capacity
and virtqueues; eventual service, bounded latency and recovery are U. [Q-console]
[Q-bus] [Q-fd]

## Sensor values, time and policy separation

| Phone sensor ID / data label | Units and selected source behavior | Functional limitation |
|---|---|---|
| 0 acceleration | m/s²; rotated synthetic gravity (phone baseline along +Y), magnitude 9.80665 | Reporter sends once per second; guest batch can repeat cached value at requested schedule. |
| 1 gyroscope | rad/s; axis-angle of previous/current rotation over host high_resolution_clock elapsed seconds | No periodic decay to zero when rotation input stops; cached nonzero motion can persist. Clock monotonicity and host/guest rate agreement U. |
| 2 magnetic | SensorType magnetic field; synthetic fixed vector rotated with the same matrix (Android magnetic-field unit convention is microtesla) | No actual host magnetometer read. Geographic coherence with Persona/location is not provided. |
| 4 temperature | degrees Celsius; model holds 25 | Advertised, but excluded from reporter; guest activation emits no-value sentinel. |
| 5 proximity | cm; model holds 1 | Advertised, excluded from reporter; cached no-value sentinel until some other source supplies data. |
| 6 light | lux; model holds 1000 | Included in host's continuous-update mask although guest descriptor is on-change; guest suppresses unchanged repeats. |
| 7 pressure | hPa; model holds 1013.25 | Exceeds descriptor maxRange 800; no range correction in this path. |
| 8 humidity | percent; model holds 40 | Advertised, excluded from reporter; activation can report no-value sentinel. |

These are source values, not private Persona examples or measured host data.
The three missing scalar reports are not cured by `kGetSensorsData`: that reply
goes to the separate control peer, not the guest data channel. Host sends each
selected data record as `name:values\n`, with colon-separated vectors; model's
intermediate serialization uses spaces between sensors. [C-model] [C-proxy]
[C-main] [G-list] [G-wire] [G-hal]

The WebRTC command called rotation vector actually parses three Euler angles in
degrees. Matrix is Rz(-z) Ry(-y) Rx(-x); ID 31 is described as orientation relative
to East-North-Up. It is not an Android quaternion event. Gyro, gravity and magnetic
values share this calculation, but virtual display rotation, input transforms,
GPS and network geography have separate contracts. No automatic coupling or
coordinate correctness across those interfaces has been proven. [C-ids] [C-model]
[C-main]; see the existing host-display and Persona policy records.

Guest parsing initially uses elapsedRealtimeNano plus **-500,000,000 ns** bias.
`guest-sync` can adjust bias using a weighted average of microsecond input, but
this proxy emits neither guest-sync nor sync and ignores guest time commands.
Continuous batch delivery overwrites the cached event's timestamp with its
scheduled guest time. On-change activation uses current guest time; normal
on-change parsing uses biased time. Ordering, suspend/resume, stale-data detection
and replay rejection are not guaranteed by timestamp presence. [G-header]
[G-wire] [G-hal] [C-proxy]

| Existing policy obligation | What this source supplies; remaining enforcement question |
|---|---|
| Decoy | Synthetic gravity/motion/field/scalars need no real host sensor feed. Constants and Euler state are not a coherent Persona service: missing scalar reports, range conflict, cached gyro, placement metadata and timing need review. Protected master state and atomic cross-interface changes are absent. |
| Real | No reviewed host SensorManager/listener path exists here. Any future Real feed needs separate explicit, visible scope, permitted sensor/rate, caller/instance/epoch binding, independent revocation and no queued stale delivery. Guest activation is never host consent. Sensor-specific host permission/lifecycle limits remain U; no ambient listener is authorized. |
| Empty | Zero vectors and stale/no-value samples are not empty results. A zero enumeration mask is syntactically accepted, but contradicts retained product declarations and is not a per-app absence mechanism. Legitimate method-specific absence semantics are unimplemented. Do not remove sensors to label this solved. |
| Deny | The peer has no explicit policy-denial transaction. Unknown handle returns BAD_VALUE; direct reporting is unsupported; these are API results, not a host policy boundary. Silence, fatal startup or transport corruption is not an honest per-request Deny implementation. |
| Provider failure | Cached continuous samples can continue with new timestamps; scalar sentinel behavior is not a failure contract. Fail-closed genuine disclosure and distinguishable failure need an external trusted owner. No inspected simulator call automatically reads real host sensors, but this static absence is not a complete fallback/leakage proof. |
| Persona/instance change | No instance/epoch field or cache invalidation transaction. Host reboot flag resets activation only; guest cached state and adversarial copies are not revoked. Fresh FDs/names cannot alone prove old worker cleanup. |
| Hostile guest commands | Selected handler parses list-sensors and ignores other payloads; no reviewed dispatch from those strings to privileged host operations. Unbounded frame allocation/blocking still exposes the peer. Control-stream rotation updates need independent caller authorization; sharing that FD with the guest would expose policy input. |

Sensor availability must agree with feature XML, HAL list, modes and actual data;
framework fusion and native/Binder/cached access need later independent evidence.
Master Persona/manager state must never be delegated with the sensor channels.
No host-GPS fallback, passthrough, production permission change or revision of
Real/Decoy/Empty/Deny is proposed. Full protection remains **Unknown**.

## Ordinary Android-app authority matrix

| Mechanism / actual user | Access class and boundary | Disposition |
|---|---|---|
| Guest hvc18/19, tty operations, Binder/HAL service | Guest kernel/init authority; device modes/labels and service rc apply inside guest | Required guest resources, not host device-node grants. Generated guest policy/build correspondence U. Host platform signing or host BLOCK_SUSPEND is not inferred from guest rc. |
| Software virtio-console device model | H: ordinary packaged native computation; no host console driver or sensor hardware intrinsically required by this model | Source mechanism exists. Exact Android VMM device build, execution, memory and containment remain U; unchanged broader launcher still has prior KVM/kernel-vhost blockers. |
| Four reference FIFOs and pathname opens | App-owned filesystem IPC is distinct from restricted host devices. Exact DAC/SELinux labels govern access; isolated workers cannot assume access to manager app-data paths | **Unsupported unchanged confined path**: launcher creates/unlinks names and QEMU reopens names. Same-UID placement would expose manager authority after compromise and is not an approved remedy. [S-isolated] [C-launch] [Q-pipe] |
| Already connected AF_UNIX streams, inherited/received FDs | S: appdomain policy allows specified use of received connected unnamed Unix streams; Binder and object/FD access checks still apply | Conditional mechanism for a separately reviewed adapter. Framework-created isolated services do not inherit launcher FDs from app management; explicit Binder/PFD admission is missing. Numeric FD flags are not transferable authority or identity. [S-app] |
| SharedFdChannel over an admitted FD | S: read/write byte-channel implementation with separate input/output references | Real lower-level API; needs bounded parsing, correct framing and trusted lifecycle. Does not create missing Android target or automatic QEMU pipe-FD selector. |
| WebRTC-facing control | Selected local socketpair, not a mandatory network socket inside the simulator | Valid FD mandatory; actual input may stay idle for defaults. Full remote UI stack is not established as mandatory for basic synthetic reporting. Any replacement control producer is an explicit adaptation, not selected configuration proof. |
| Kernel event peer | Launcher-owned guest-log event pipe; event parser and monitor thread | Required by selected launch; invalid FD bypasses monitor, valid EOF aborts. No need to read real host dmesg. Omission changes reboot behavior; synthetic event injection is not trusted manager-loss enforcement. |
| Simulator native binary / helpers | `cc_binary_host`, `cuttlefish_buildhost_only`, device_supported false; runtime uses C++ threads, allocation, locks, clocks and logging | **Unsupported as supplied Android app artifact**. New Android library/entrypoint, dependency closure and ownership required. A successful desktop build would not prove ordinary-app execution. |
| Real host sensor API | Ordinary app access is sensor/permission/rate/background dependent; direct driver or sensor HAL ownership is restricted/platform-specific | Not used or authorized here. Exact Android 17 host access remains U; shell injection, privileged service access, root/OEM grants are excluded. |
| Host process/thread and resource control | System sandbox/SELinux/seccomp enforce actual authority; app cooperation does not contain compromised native code | Whole-tree completion, manager death, FD closure, total budgets and safe restart U under existing evidence. Host build and a thread-only honest code path confer no enforcement. |

No sensor path inspected requires `/dev/vhost-vsock`, `/dev/kvm`, host input
devices, host sensor ioctls or a VPN slot. That narrowly scoped absence does not
remove such dependencies from the **complete reference launcher**, nor prove all
transitive code safe. App sandbox permission is not inferred from POSIX API
availability. Stock host minimum, OEM policy, arm64-v8a/Bionic linkage, 4/16-KiB
alignment, JNI/native-load order, FD quotas and lifecycle behavior remain U.

## Source-level negative controls and falsifiers

Every row is **Not run**, with expected behavior derived from the cited source.
No PASS, successful rejection, Android measurement or independent runtime oracle
is claimed. A falsifier below rejects the asserted closure/recovery claim; it is
not an instruction to execute the case in this task.

| Case | Expected source behavior | Exact falsifier of claimed closure |
|---|---|---|
| Required endpoint absent | Entry open/raw setup fatal; HAL construction cannot complete. [C-entry] | Either required guest node/driver/access missing, or raw-terminal setup fails. Successful unrelated service registration cannot substitute. |
| Wrong console/port | Wrong peer's bytes reach control/data parser; may block, fail parse or accidentally accept a numeric prefix. [C-qemu] [G-hal] | Actual device order does not map both channels as traced, even if host names say hvc18/19. |
| Simulator exits before init | Guest nodes may still exist. O_RDWR FIFO references and console-open semantics can hide absence; list receive may wait. [F-fd] [Q-console] [G-hal] | Claim of bounded graceful failure lacks a deadline/independent peer-liveness witness. |
| Alive but never supplies data | No list reply blocks initialization; list reply without samples permits construction but leaves no-value/cache state. [G-hal] [C-proxy] | Registration/activation accepted as complete readings without actual first valid values for every advertised sensor. |
| Truncated/malformed frame | Exact read blocks or errors; allocation precedes size check; malformed mask fatal, unparsed data logged. [T-channel] [G-wire] | Oversize allocation, indefinite partial frame, accepted invalid numeric range, or framing loss accepted as safe rejection. |
| Disconnect after registration | Guest epoll HUP/ERR restarts transport with same captured FDs; send failures can abort; no new list/epoch admission on that loop. Host errors stop proxy loops, not necessarily main. [G-epoll] [G-hal] [C-proxy] | Successful authenticated reconnect or cache reset claimed without an actual new-peer/lifetime contract. |
| Unknown sensor type/name | Unknown data logs warning; invalid public handle BAD_VALUE; mask is clipped to compiled list. [G-wire] [G-hal] | Unknown input becomes authorized Real data, arbitrary host operation, or a claimed supported feature. |
| Timestamp/order inconsistency | Initial negative bias; optional guest-sync; continuous cache timestamp replaced at batch delivery. [G-header] [G-wire] [G-hal] | Fresh timestamps treated as provider freshness, or old values cross a policy boundary undetected. |
| Stalled backend while requests continue | Blocking exact reads/writes, ignored set-delay, fixed reporter period, console short-write loss; no global quota/deadline. [F-buf] [C-proxy] [Q-console] | Lossless bounded traffic claimed under saturation without independently observed frame integrity/resource bounds. |
| Manager ownership lost/death | No manager enrollment/lease in simulator; valid remaining FDs can continue serving cached/default state | EOF, process liveness or guest success accepted as trusted policy ownership or completed teardown. |
| Worker keeps duplicated FDs after stop | Close of one reference leaves duplicates; no per-operation policy on raw channels | New instance/resource reuse after a stop acknowledgement without independent reference/work closure. |
| Provider falls back to real host data | No such acquisition call in inspected simulator; total enforcement not proven | Any unapproved host reading/GPS/listener introduced on error/default path. Static absence cannot certify it impossible after compromise. |
| Instance/epoch mismatch | Wire has no instance/epoch; reboot event only disables reporting until another list request | Old data/control FD or queued frame accepted for a new Persona/instance. |
| Guest reports success without enforcement | activate/batch/flush results describe guest behavior; cache can outlive source | Guest success, uptime or timestamps used as independent proof of host containment/revocation. |
| Advertised scalar never initialized | Proxy omits temperature/proximity/humidity; activation can return sentinel. [C-proxy] [G-hal] | Full matching peer claimed while any advertised scalar lacks a valid initial event or declared legitimate absence semantics. |
| Host control/event peer malformed or gone | WebRTC parse errors retry/log; event EOF/error CHECKs; native-size length allocation is unbounded. [C-main] [C-events] | Silent fail-open, bounded-resource or robust recovery claim without accounting for these exact paths. |

No desktop control was added: source establishes these missing branches and
interfaces directly. A synthetic test encoding this table would add no independent
evidence. The loss and stale-cache findings remain preserved even if a future
Android build becomes available.

## Build, provenance, licensing and correspondence limits

| Component and artifact role | Source/build dependencies and license evidence | Remaining blocker |
|---|---|---|
| Guest Cuttlefish sub-HAL shared library | C entry + G virtual defaults: multihal_sensors, epoll, qemu parser and sensor_list; HIDL 2.0/2.1, ScopedWakelock, libbase/hidlbase/log/utils, multihal headers; adds libcuttlefish_fs/transport/utils_result. Apache-2.0 file headers and package declarations. [C-guestbuild] [G-build] | ARM64 guest vendor ABI, generated HIDL interfaces, linker namespace, final module/notice graph and exact product outputs not built/attested. Ranchu entry/libqemud are not selected. |
| Guest AIDL multihal service | I build/service, HalProxyAidl/converters + 2.X HalProxy, AIDL sensors-V3-ndk, Binder NDK, HIDL, FMQ, power, base/cutils/log/utils, scoped wake-lock and aidlcommonsupport; selected rc/VINTF. Apache-2.0 headers/package metadata. [I-build] [I-aidlbuild] | Generated AIDL/HIDL/FMQ types and complete transitive build/license closure U. Guest framework/kernel/init/SELinux are not supplied by host binary. |
| Host sensors_simulator executable | Three sources main/proxy/model; Eigen header dependency; shared libbase, libcuttlefish_fs, kernel_log_monitor_utils, transport, utils, jsoncpp, log, protobuf-cpp-full; static host_config, guest_config_proto, gflags. Explicit non-Android defaults; darwin enabled separately. Apache-2.0 on inspected C files. [C-hostbuild] [C-defaults] | No Android device target, library/JNI entry or qualified APK. Generated config protobuf and all transitive native dependencies/toolchain/link imports need immutable manifest and per-file notices. Do not assume libbase/private platform libraries are public app linkage. |
| Common transport/FD libraries | Transport includes channel.cpp/channel_sharedfd.cpp; FS includes shared_buf.cc/shared_fd.cpp/shared_fd_stream.cpp and Linux epoll.cpp, with base/log/utils environment/result dependencies. Their `cuttlefish_host` defaults support host and device variants. [T-build] [F-build] [C-defaults] | Lower-level device variants are positive source evidence, not a simulator Android build or full app ABI. Raw struct ABI, blocking I/O, allocation limits and exposed helpers remain review work. |
| Launcher/control/event peers | Named FIFO creation, AF_UNIX socketpair, subprocess FD delegation, guest kernel-log monitor and JSON event utility; Apache-2.0 inspected headers | Full launcher/import is excluded. Replacement authority/lifecycle/configuration interface is missing. No proprietary helper is identified as necessary for the inspected synthetic calculation; full dependency availability remains U. |
| QEMU console/pipe/bus and guest kernel | Existing QEMU pin; console declares GPLv2; bus distinguishes original GPLv2 and later GPLv2-or-later contributions; pipe/fd have permissive file notices. Guest virtio-console is GPL-2.0-or-later and hvc GPL-2.0+; kernel pin inherited from boot/HAL evidence. | No new engine/component adoption. Existing constrained cross-build does not attest this complete transport. Kernel/modules/generated config and exact image correspondence remain unresolved. Preserve component-specific source/notice obligations. |
| Policy and framework witnesses | Existing immutable system/sepolicy and frameworks/native revisions; policy is documentary evidence, not an imported host grant | Compiled OEM policy, public host APIs, supported version/ABI and independent containment evidence U. |

No source license is treated as permission to redistribute an unexamined binary
image. Dependency module names do not close Eigen/jsoncpp/protobuf/gflags,
generated interfaces, libc++/Bionic, compiler or transitive license obligations.
No prebuilt helper, firmware, SDK or guest image was acquired/adopted. Security
history, maintenance ownership, reproducible artifacts, complete NOTICE/source
delivery and redistribution rights must be settled before adoption under the
[source policy](../source-provenance-policy.md). Existing firmware, module,
Rust/backend and complete-guest blockers remain separate and unchanged.

## Smallest next proof and preserved outcome

**Supported:** exact source-selected service/sub-HAL, two-console mapping intent,
framed byte peer and synthetic calculations exist; they do not inherently require
real host sensors. Common transport has device build variants. **Unsupported:**
unchanged non-Android simulator as an ordinary-app artifact, unchanged ambient
FIFO launcher as the confined endpoint arrangement, silent sensor deletion,
privileged helper substitution, and claiming complete behavior from registration.
**Unknown:** complete matching app-hosted peer, Android source/build correspondence,
resource/lifetime enforcement, protected Persona modes and all stock-host runtime.

The **single smallest next falsifiable proof** is a source/build correspondence
review for an explicitly identified Android-target sensor-peer variant retaining
this guest entry and wire contract. It must exhibit a real build target and full
dependency graph, an owned connected-FD entrypoint for both guest channels and
explicit control/reboot ownership, and actual code handling all eight advertised
sensor types with initial values and declared timing/failure behavior. Falsifiers:
host-only target/private unresolved import, ambient path reopen or privileged
helper, missing scalar path, unchanged pressure-range conflict, missing bounded
framing/failure handling, or a claimed epoch mechanism that merely trusts the
guest. If no such source exists, preserve that precise missing-implementation
result; do not build a synthetic success test or proceed to phone work.

This review authorizes no port or implementation. A proposal changing process
placement, trust boundaries, transport/product behavior or policy needs a concrete
ADR and explicit owner approval before implementation. The independently
supportable lead is adapting the existing byte-channel/synthetic-model mechanism,
not adopting another product, suppressing sensors or widening host privilege.
Even successful future correspondence would leave actual stock Android 17 host
execution, confinement, resource use, full Android guest and gates unresolved.

## Actual validation and unrun work

Source retrieval and manual caller/build comparison are the only sensor
observations. Local checks used the existing bundled Python **3.12.14**, with no
tool installation:

| Validation | Actual local result |
|---|---|
| `python .github/scripts/validate-foundation.py` | PASS: 133 files, 81 Markdown files, 54 requirements, two ADRs; includes local file targets and regular modes. |
| `python .github/scripts/validate-harness.py` | PASS: source/manifest authority hygiene only. |
| `python .github/scripts/test-repository-validation.py` | 141 tests: 137 passed, four existing platform skips; no failures. Skips cover Linux host C, real symlinks and POSIX executable modes. |
| `python .github/scripts/test-desktop-readiness.py` | 27 passed, no skips. |
| `python .github/scripts/test-offline-image-inspect.py` | 45 passed, no skips; synthetic fixtures only. |
| `python .github/scripts/test-frame-copy.py` | Four passed, no skips; existing desktop controls, not sensor tests. |
| Source consistency | Cited byte hashes recomputed; original sensor receipts compared; build target, call graph, port directions, masks, flags, initial cache values and framing inspected directly. |
| Diff, links and public hygiene | Two Markdown files only; complete exact-base change, local targets, source links/IDs, regular modes, whitespace and public text reviewed. No dependency or binary changes. |

`git diff --check` passed. Linux native/lifetime/seccomp/revocation suites were
not rerun locally; existing hosted results retain their earlier scope. Android
build/lint and sensor compilation were **Not run**: no Android/build source changed
and the source contract already identifies missing target/ownership behavior.
Foundation applies to this PR; Android and QEMU workflow path filters do not
select these two documentation files. Absent workflows are not successes.
No tests of sensor behavior, guest boot, simulator execution, QEMU, JNI/native
integration, phone/ADB/USB, APK installation, Android diagnostic activation,
host sensor listener, GPS, host VPN or privileged service were performed.
No real Persona data was created or used. No CI check was changed or weakened.

An ignored local checkpoint retains source receipts, progress, blockers and
publication recovery steps. It is not independently backed-up canonical evidence.
This research is preserved through one intended evidence PR; canonical acceptance
still requires merge and independent review. New PR hosted CI is
**pending/unobserved at publication**. Publication is followed only by one native
association check and one exact PR head/base check, then STOP; no hosted CI,
review, status, comment, job or mergeability polling follows.

## Immutable source receipts and method

Pins are inherited from the merged source ledgers, without revision changes:
C = device/google/cuttlefish `283645aacf6cdb56cc31a9362f54d412dbc132a1`;
G = device/generic/goldfish `296e55aa0244e8929e393e00e34471fef2a5d662`;
I = platform/hardware/interfaces `0162af698935100a590b7359581ac8b1b80693e5`;
N = platform/frameworks/native `ae266dcb706d083868578cfedce381ef44488a07`;
S = platform/system/sepolicy `e066568e98d86db31a9346d30977f3632fa7073c`;
K = kernel/common `3ec022196c4e9d5c1434599cdda63f622dd6f586`;
Q = qemu/qemu `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`.
T/F IDs below are files in C. K is a source witness, not newly proved correspondence
to the selected prebuilt kernel/module graph.

Retrieve Gitiles immutable file URLs with `?format=TEXT`, base64-decode to bytes
without newline conversion, then SHA-256. Q files use immutable raw GitHub URLs.
Hashes below were recomputed from saved bytes. Review build declarations and
callers, not filenames alone. Original boot/HAL sensor receipts match the new
retrieval. Only public text was fetched; no external implementation is committed.

Exploratory wrong paths returned 404 (sensor config outside multihal, goldfish
headers outside include, service files under default or guessed names, guessed
sensor SELinux filenames, sockets/auto_cmds filenames, shared_buf.cpp and
kernel-log utils.cpp). One guessed default service rc request returned 503.
Actual build/include declarations and directory metadata resolved the selected
service, headers, sockets and `.cc` utilities. The unsuccessful sensor-specific
SELinux paths do not prove policy absence: node labels/uevent modes were retrieved,
but complete generated guest policy remains U. Unselected example-service source
was retrieved while locating the multihal; it is not evidence for this selection.

| ID / immutable file | SHA-256 of retrieved bytes |
|---|---|
| [C-product: vsoc_arm64/phone/aosp_cf.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/phone/aosp_cf.mk) | `ba74bdb141f2346a53b516fecb9cda9337c903185cdf7b4603b25a7293c77579` |
| [C-phone: shared/phone/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk) | `69645517941d7013eb798376faeee588cc86f9bfd117dd5eecd27b250b6ad176` |
| [C-product-sensors: shared/sensors/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/device_vendor.mk) | `f55bf215c446d97e0ee8b009f5f047733093d4a99854ed895cd4db634d3b258b` |
| [C-entry: shared/sensors/multihal/entry.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/entry.cpp) | `8063cd2e5f58b6202826546738ff04b1388eb49f6c78226dd59f578243795f53` |
| [C-guestbuild: shared/sensors/multihal/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/Android.bp) | `732677a4f80e34fa333103195b08bbed5bcd33c6a4a8322f6e27d56f28e59011` |
| [C-conf: shared/sensors/multihal/hals.conf](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/hals.conf) | `c725951b4115ef2bf2ee7ac0f650a7d89b0e61e68a16746e3e93e787106e9123` |
| [C-launch: host/commands/run_cvd/launch/sensors_simulator.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/sensors_simulator.cpp) | `5308ddd96d5ed5ae574de49416117690f415e4595987e32966e504b33939318b` |
| [C-main: host/commands/sensors_simulator/main.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/main.cpp) | `2f84b0563ff7b347ccd99de97d08b6eef725970dd9c0a98666ec6845dc9333cc` |
| [C-model: host/commands/sensors_simulator/sensors_simulator.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/sensors_simulator.cpp) | `13cfcce005c151e9f094887712d5f0aa3205f0f4b467b81ac309c94afc0db38d` |
| [C-proxy: host/commands/sensors_simulator/sensors_hal_proxy.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/sensors_hal_proxy.cpp) | `ff691c84babc6245638f5d5c88fce74745831920c144ebc61c7c350d91223af9` |
| [C-proxy-header: host/commands/sensors_simulator/sensors_hal_proxy.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/sensors_hal_proxy.h) | `5c39a2cc770a68378a0a41e0338ede5d4f8c376a98637e198916782863437d41` |
| [C-hostbuild: host/commands/sensors_simulator/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/Android.bp) | `be46966ab320857d6bd136bd26f4a8ebb9de9c5b1ff336b4bd1ab54264c37fa3` |
| [C-defaults: Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/Android.bp) | `2580299ebf86ef24dbf06e497dae23ae91d8db61262fd9aea07721dee234143b` |
| [C-ids: common/libs/sensors/sensors.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/sensors/sensors.h) | `a60df84a0d89e8f2e7fa9a9bdaa667f5754cb7a1668ebc5a9e31246e8c8414f9` |
| [C-qemu: host/libs/vm_manager/qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` |
| [C-uevent: shared/config/ueventd.rc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/ueventd.rc) | `0fb64e3398ba7cb74b0d81fa8f2a1d41ae6987a6d627a6b126c121634efe6a8d` |
| [C-contexts: shared/sepolicy/vendor/file_contexts](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sepolicy/vendor/file_contexts) | `9395af4a4210323fcb6a367d714424c2fe5428117060e7dd9af3029f6fa83da4` |
| [C-pair: host/commands/run_cvd/launch/sensors_socket_pair.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/sensors_socket_pair.cpp) | `561341b0f5876fa971d58cb56b1fc1322aa7189f2474095b6486f8dcebdca03a` |
| [C-events: host/commands/kernel_log_monitor/utils.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/kernel_log_monitor/utils.cc) | `54a4e3f7f725e5579a03062dfb0121e1c104b20dd4d4a092cc674b3449ce923d` |
| [C-loglaunch: host/commands/run_cvd/launch/kernel_log_monitor.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/kernel_log_monitor.cpp) | `155b98733404a6bbbe1abf2af8dd68c61521359e49eb8abdf48e44edb9d0751f` |
| [C-subprocess: common/libs/utils/subprocess.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/utils/subprocess.cpp) | `a56d6fc24008cc8d59484d4c08ac3455611cedf5ec850eba4c7f79d8646ea04c` |
| [C-inject: guest/commands/sensor_injection/main.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/commands/sensor_injection/main.cpp) | `f114e8908ff36214fb4585eb49f39ac447760399030b8b7958a1793609975b27` |
| [G-hal: hals/sensors/multihal_sensors.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/multihal_sensors.cpp) | `aa26e75a6bc4447140e4a34c39bd3c8e1b486a0a1f1ac2e633f0672fadf6381c` |
| [G-header: hals/sensors/include/multihal_sensors.h](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/include/multihal_sensors.h) | `d83794bd4e9edc9491bcca5234c1b6b6cece6d2152e17b59428c4db72acbb55f` |
| [G-build: hals/sensors/Android.bp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/Android.bp) | `7717b3a0d381ca56e5e5776d19ab3a6ea51bd3bc377aa901837806f3106dc4e9` |
| [G-entry: hals/sensors/entry.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/entry.cpp) | `4432571cb2125e9569fb145c17bac8916794d2aec7cd89b5bca4f6809d2cae94` |
| [G-list: hals/sensors/sensor_list.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/sensor_list.cpp) | `a91c4803da8bd6040e8a3c04f58b35e34fb95fd6953506a4c0847907f54b0db1` |
| [G-wire: hals/sensors/multihal_sensors_qemu.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/multihal_sensors_qemu.cpp) | `1e8747be7d9419a1093627f8e244d10ee0f1846298e4f771d23ff14a671831dc` |
| [G-epoll: hals/sensors/multihal_sensors_epoll.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/multihal_sensors_epoll.cpp) | `dbdeb15b705c43ca9609723d8e9d8a03991a4d5f13e4ff6e2df5217e8f1d74b5` |
| [I-aidlheader: sensors/aidl/default/multihal/include/HalProxyAidl.h](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/default/multihal/include/HalProxyAidl.h) | `a517b2e19f595ebc69b4066a490a775e6292fbd62dae4e8d6482123f59803361` |
| [I-build: sensors/aidl/multihal/Android.bp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/Android.bp) | `74cdd47e83b7c0fb0d428c78968f462f4908d27c33c992c86a1e305a3adac15a` |
| [I-service: sensors/aidl/multihal/service.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/service.cpp) | `6800b4e58519c401af547e96536bf0e31895bd5acd3c837ec5ba1c252055ee95` |
| [I-rc: sensors/aidl/multihal/android.hardware.sensors-service-multihal.rc](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/android.hardware.sensors-service-multihal.rc) | `447f8a3de3a5bea7632593458c52e69dbcdeb92a4ac78c955f03a1d98848d833` |
| [I-vintf: sensors/aidl/multihal/android.hardware.sensors-multihal.xml](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/android.hardware.sensors-multihal.xml) | `1fec5262cdfb7c4c66113b5b738618d7b7627380668ae90fea88127d86e92e5f` |
| [I-aidl: sensors/aidl/default/multihal/HalProxyAidl.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/default/multihal/HalProxyAidl.cpp) | `11211bc07664ae697ba5f3f0ef1bca358221c45c3a47ed589413a23158da3fbb` |
| [I-aidlbuild: sensors/aidl/default/multihal/Android.bp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/default/multihal/Android.bp) | `b6ac17ebefa7a58ceab048e63f27fc132da142ecb6bfe47149f6c08d1e22697b` |
| [I-loader: sensors/common/default/2.X/multihal/HalProxy.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/common/default/2.X/multihal/HalProxy.cpp) | `4a9a2d5255e858669ab87abf88f52a5e58516cb73375b8ba77dcdd1aa4817243` |
| [N-wrapper: services/sensorservice/AidlSensorHalWrapper.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/sensorservice/AidlSensorHalWrapper.cpp) | `cb4a6cdde52d428256abd253980ae4f09d18726da47e716870c1086baa74355a` |
| [N-features: data/etc/handheld_core_hardware.xml](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/data/etc/handheld_core_hardware.xml) | `8dbd117a8c9a908a65cb43973d8d40504512c0afa1a220404fb14b1e552bf138` |
| [T-channel: common/libs/transport/channel_sharedfd.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/channel_sharedfd.cpp) | `f707794659d1e2a374ba85cd0d00514259b4fdc5ac1355076adc2b9bf8b04b21` |
| [T-header: common/libs/transport/channel.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/channel.h) | `b2a7d5aae713bf4c7d9f0d321b4bf3f45d1a650ff2b280aebe48672c35f791fa` |
| [T-message: common/libs/transport/channel.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/channel.cpp) | `958883dbaca62b933dd7c68041e2d6159c170f19f2ce755c3fe2521fc2cff991` |
| [T-build: common/libs/transport/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/Android.bp) | `f57f4f5356ac1aede0964c8e2a48bd1fcf9f25997aa836bf8493454b20bc2f1d` |
| [F-fd: common/libs/fs/shared_fd.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/shared_fd.cpp) | `7b14de57239c6d7383e96b6420acdeec841a04d6862fa3208da164932e633d1e` |
| [F-buf: common/libs/fs/shared_buf.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/shared_buf.cc) | `a71a3583c38adafcd6f94b17593965ef6b483086fa7889033bf88004d884620f` |
| [F-build: common/libs/fs/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/Android.bp) | `d250e9ed056858f4ed484c0f215bc47e0aa66b10d766c8d7c8dbfc0d945e4266` |
| [S-app: private/app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te) | `6a18ae176e35cf19ab022cc75887a5c77aae55f00e8a1ebddd7ebd75aea64525` |
| [S-isolated: private/isolated_app_all.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te) | `e65adb199d7fc26cd716f4e376f6068edcd3c350647f121e8d5937fa9bca4ad9` |
| [K-console: drivers/char/virtio_console.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/char/virtio_console.c) | `2d2e992ad1a1a1e0077d3787bf87ad5c681cef47ab6d5cc26732e7c7c9729c5d` |
| [K-hvc: drivers/tty/hvc/hvc_console.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/tty/hvc/hvc_console.c) | `ac8bbdeab024fbe66d4a71d2bd3bad3548d3ad0cfb6b65f46c248038f190f218` |
| [Q-console: hw/char/virtio-console.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/char/virtio-console.c) | `7088fe72aa863cbedb9157ebcc44850d580278c7aea481e2477f9433ecbd17d3` |
| [Q-bus: hw/char/virtio-serial-bus.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/char/virtio-serial-bus.c) | `1d901a8ca094ff41a55d87c44f57963e22f0defceef8d5af3bd37a34cdff558f` |
| [Q-pipe: chardev/char-pipe.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/chardev/char-pipe.c) | `4a987c4d0fa6264b91595716c56f6898944ccb55b966b177c884278d8b87e307` |
| [Q-fd: chardev/char-fd.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/chardev/char-fd.c) | `026b271f7d0d898eccf32923b7f5e255d637770e421793d892df13baf6a78b7d` |

[C-product]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/phone/aosp_cf.mk
[C-phone]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk
[C-product-sensors]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/device_vendor.mk
[C-entry]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/entry.cpp
[C-guestbuild]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/Android.bp
[C-conf]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/hals.conf
[C-launch]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/sensors_simulator.cpp
[C-main]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/main.cpp
[C-model]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/sensors_simulator.cpp
[C-proxy]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/sensors_hal_proxy.cpp
[C-proxy-header]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/sensors_hal_proxy.h
[C-hostbuild]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/Android.bp
[C-defaults]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/Android.bp
[C-ids]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/sensors/sensors.h
[C-qemu]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp
[C-uevent]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/ueventd.rc
[C-contexts]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sepolicy/vendor/file_contexts
[C-pair]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/sensors_socket_pair.cpp
[C-events]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/kernel_log_monitor/utils.cc
[C-loglaunch]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/kernel_log_monitor.cpp
[C-subprocess]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/utils/subprocess.cpp
[C-inject]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/commands/sensor_injection/main.cpp
[G-hal]: https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/multihal_sensors.cpp
[G-header]: https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/include/multihal_sensors.h
[G-build]: https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/Android.bp
[G-entry]: https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/entry.cpp
[G-list]: https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/sensor_list.cpp
[G-wire]: https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/multihal_sensors_qemu.cpp
[G-epoll]: https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/sensors/multihal_sensors_epoll.cpp
[I-aidlheader]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/default/multihal/include/HalProxyAidl.h
[I-build]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/Android.bp
[I-service]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/service.cpp
[I-rc]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/android.hardware.sensors-service-multihal.rc
[I-vintf]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/multihal/android.hardware.sensors-multihal.xml
[I-aidl]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/default/multihal/HalProxyAidl.cpp
[I-aidlbuild]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/aidl/default/multihal/Android.bp
[I-loader]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/sensors/common/default/2.X/multihal/HalProxy.cpp
[N-wrapper]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/sensorservice/AidlSensorHalWrapper.cpp
[N-features]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/data/etc/handheld_core_hardware.xml
[T-channel]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/channel_sharedfd.cpp
[T-header]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/channel.h
[T-message]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/channel.cpp
[T-build]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/transport/Android.bp
[F-fd]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/shared_fd.cpp
[F-buf]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/shared_buf.cc
[F-build]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/Android.bp
[S-app]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te
[S-isolated]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te
[K-console]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/char/virtio_console.c
[K-hvc]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/tty/hvc/hvc_console.c
[Q-console]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/char/virtio-console.c
[Q-bus]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/char/virtio-serial-bus.c
[Q-pipe]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/chardev/char-pipe.c
[Q-fd]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/chardev/char-fd.c
