# Next physical experiment: isolated QEMU authority proof

**Specification dated 2026-10-07. NOT RUN. Gate 0: Unresolved. A–G: Not reached.**
All outcome fields are **Unknown / not measured**. This is a falsifiable experiment
specification, not an implementation, source-adoption decision or production-engine
selection. Read the [source ledger](gate-0-userspace-vmm-sources.md),
[candidate model](gate-0-userspace-vmm-candidate.md), [source policy](../source-provenance-policy.md)
and [acceptance rules](../acceptance-evidence-criteria.md) first.

## Question and bounded result

Can an ordinary sideloaded release-equivalent APK on an exact stock non-rooted
production Android/ARM64 device run source-built QEMU aarch64-softmmu/TCG in a
dedicated `android:isolatedProcess` worker, boot a tiny independent ARM64 Linux
kernel, and provide minimally useful disk/display/input capabilities while
withholding trusted management authority from arbitrary native worker code?

The guest fixture is a tiny auditable ARM64 Linux/Buildroot-style kernel plus
minimal userspace, solely to exercise the host mechanism. It is not Android 17,
not a product Linux mode and not permission to import a ready-made opaque image.
Prefer a read-only minimal root filesystem plus a bounded separate scratch disk;
record every selected source, build option and license before adopting it.

At most, a complete positive result can support:

> Ordinary-app isolated software-emulator mechanism demonstrated for the exact
> tested host/device/build configuration.

Report mechanism execution, delegated resources, denial probes, revocation and
resource behavior as **separate** outcomes. A Linux boot, a sentinel denial or a
passing harness alone does not establish containment or Gate 0 completion.

## Preconditions and run manifest

The experiment owner fills and freezes a run manifest before building/running.
These are experiment acceptance conditions, not additions to the product register.

| Field | Required content / current value |
|---|---|
| Run identity | Date, experiment revision, reviewer and synthetic run ID; **not assigned** |
| Host | Physical OEM/model, public build/version/API/security patch, production `user`, ABI, RAM, kernel, page size, SELinux enforcement/domain; **Unknown** |
| Authority | Ordinary user-installed APK. No root, Magisk, Shizuku, Xposed/LSPosed, custom host ROM/kernel, system/privileged install, platform signing, userdebug/eng, production ADB grants or KVM requirement. |
| Runtime sources | Exact QEMU commit/release, embedding patches, native dependencies, selected devices/backends, compiler/NDK/SDK and full build environment; **not selected** |
| Guest fixture | Exact Linux and minimal userspace/Buildroot revision, configs, device tree/boot settings, generated kernel/rootfs/scratch identities and licenses; **not built** |
| Artifact identity | Cryptographic hashes of APK, native payloads, boot inputs and build manifests; reviewed source-to-artifact correspondence and reproducibility limits; **none** |
| Release equivalence | Non-debuggable build, production-relevant target SDK/ABI/hardening/packaging, no test grants or weakened sandbox. Document probe code and any diagnostic-build differences. |
| Resource envelope | Predeclare vCPU, guest RAM, TCG cache, disk cap, maximum frame size/rate and IPC quotas, startup deadline, worker RSS/PSS ceiling and shutdown deadline. Include host baseline. |
| Instruments | In-app/native reports plus independent host observations where legitimately available; record every ADB command and its purpose. No result depends on ADB supplying runtime authority. |
| Privacy | Synthetic data only, no accounts, real Persona values, private files, device serials, signing keys or sensitive raw captures in public evidence. |

A concrete initial **fixture budget proposal**, to freeze or revise with rationale
before the run: one vCPU, 256 MiB guest RAM, 64 MiB TCG cache, 128 MiB scratch disk,
640x480 RGBA framebuffer, at most 10 frame updates/second, 4 KiB control messages,
100 input events/second, 120-second boot deadline, 768 MiB total worker RSS/PSS
ceiling, and 5-second stop-to-reap deadline. These are test hypotheses, not measured
capacity or product requirements. If normal host limits are lower, select a smaller
predeclared configuration or record failure for the tested scope; never raise
system limits with ADB. Runtime allocations are not bounded merely by guest RAM.
No numerical thermal/battery usability claim is permitted without a separate
predeclared workload and acceptance budget.

## Harness architecture and authority contract

1. Trusted management process owns a synthetic protected sentinel in its private
   storage, fixture verification, FD opening, presentation and bounded control.
   The sentinel is not copied into worker arguments, logs, resources or memory.
   Management alone records the expected digest and verifies integrity after tests.
2. A non-exported isolated Service contains the entire QEMU/JNI execution path.
   Primary hypothesis: a source-built, reviewed **aarch64-softmmu shared-library/JNI**
   adapter, with fixed internal launch options. A separately named process with
   management's UID is not an acceptable fallback. Use one fresh worker per instance;
   verify a distinct live UID/PID and do not opt into shared isolated processes.
3. No application startup/preload routine in the worker accesses management state.
   Inventory Android framework initialization as well as QEMU. An isolated process
   can fail before QEMU if ordinary app initialization assumes private storage.
4. Management passes only specifically inventoried boot/disk FDs, bounded display
   memory and a typed input/control endpoint. Specify access mode, ownership,
   byte/size limits, lifetime and instance/epoch for each. Avoid directory FDs,
   generic path-open RPC, general QMP passthrough, arbitrary shell or exec APIs.
5. For every kernel/initrd/firmware/image loader, establish how its bytes arrive
   through narrowly delegated authority. Investigate QEMU FD sets or a reviewed
   adapter. Do not assume block-FD support also solves kernel loading, auxiliary
   firmware, reopening or qcow2 backing-file resolution. Prefer explicit raw formats
   and no backing chain for the minimal fixture. Management authenticates identities
   before delegation; the worker cannot choose host paths to open.
6. Start without a guest NIC, SLIRP, external storage, clipboard, audio capture,
   camera, microphone, location or network broker. Request only minimal ordinary
   permissions needed for the declared harness/lifecycle. No broad storage grant,
   battery exemption or privileged helper may be required for a claimed result.
7. Management presents bounded software frames from the worker and sends bounded
   input to it. No direct GPU passthrough. Later nativeService/API 37 is an optional
   separately measured variant; it is not a prerequisite or an assumed JNI drop-in.

## Ordered procedure, controls and required records

### 1. Establish the host and authority baseline

Install the exact release-equivalent APK by ordinary sideload. Record stock state
and normal settings without unlocking, modifying SELinux or granting development
permissions. ADB installation/evidence collection may be used only as declared
development instrumentation; repeat normal launch and a basic run disconnected
from ADB. ADB cannot be a startup service, permission broker or production dependency.
Missing access to an observer is recorded Unknown, not treated as a permission denial.

Before guest boot, collect management/worker UID, PID, GID/groups, SELinux context,
manifest and effective permission observations. Inventory worker FDs, mapped native
libraries and executable mappings, Binder endpoints/handles, reachable host services,
UNIX sockets, device nodes and permitted properties/proc/sys surfaces. Describe
inspection coverage and blind spots: inability to list all Binder handles is not
proof there are none. Enumerate every intentionally transferred capability and
identify unexpected inherited FDs/handles. Do not publish confidential paths.

### 2. Prove native loading and actual TCG execution

Load the reviewed packaged library inside the isolated UID. Record load errors,
ABI/page-size/target-SDK and linker constraints. Exercise generated-code mappings
using the selected TCG configuration and observe the actual executing worker and
TCG translation path. Record relevant mmap/mprotect/memfd behavior and denials
where instrumentation permits. WebView/ART JIT success is not a substitute.

Use explicit TCG and no accelerator fallback; collect configuration plus
instrumented translation-block execution/counters or equivalent attributable
proof, not just a log label. Confirm no `/dev/kvm`, AVF, shell grant, subprocess
under management's UID or other hidden helper supplies execution. A diagnostic
build may explain failures but cannot replace the release-equivalent result;
record matching/minimized probe builds and their separate hashes.

### 3. Boot the tiny ARM64 full-system fixture through exact FDs

Record boot command/device list and the guest's independently built kernel identity,
boot log and a deterministic synthetic guest workload result. Exercise guest
syscalls inside the guest kernel and distinguish guest execution from a host-native
Linux userspace process. Trace successful reads of the deliberately passed boot/disk
resources; missing/closed/wrong-mode FD controls must prevent the corresponding
operation without broad filesystem fallback. Verify a read-only OS cannot be
modified and scratch writes affect only the dedicated disk. Keep a zero-network
configuration throughout the boot run.

### 4. Test authority as if QEMU were already compromised

Execute a reviewed **native adversarial probe inside the same isolated worker**,
with the same delegated authority, both before and after boot. Do not rely on
finding a QEMU exploit or only sending guest requests: the point is to model
arbitrary worker-native execution directly.

| Probe | Positive control | Required negative observation / interpretation |
|---|---|---|
| Protected management sentinel | Management reads its synthetic sentinel; worker reads a separate explicitly delegated synthetic canary FD | Worker cannot open/read/write sentinel by known path/direct syscall, alternate proc/FD route or management broker. An absent sentinel, wrong path or broken probe is inconclusive. Compare integrity afterward. |
| Delegated disk FD | Worker reads/writes permitted scratch regions and reads immutable fixture | Wrong access mode, undelegated file/peer resource, path traversal, reopen and backing-chain attempts cannot expand authority. Log actual errno/denial, not inferred success. |
| Process/memory | Probe identifies itself and accesses its own memory | Attempt protected management/peer proc, memory/ptrace/process_vm and service access using normal available authority. Unexpected access is a containment failure. |
| Network | A separate ordinary management/control context with INTERNET can reach a controlled synthetic endpoint in a separately identified control run | Worker tries AF_INET/AF_INET6 TCP/UDP sockets, connect/listen, resolution, inherited network FDs and relevant UNIX/Binder deputies. Record denial and independent absence/presence of attributed traffic. No guest NIC alone proves nothing. |
| Storage and device services | Known synthetic controls demonstrate the probe executes | No ambient external-storage, camera, microphone or location authority. Check relevant direct/native and Binder paths; lack of hardware or an unavailable observer is Unknown. |
| Binder/control | Valid bounded input/control operation works for current instance | Unauthorized instance, stale epoch, unknown command, descriptor injection, oversized/malformed/replayed requests cannot cause generic host actions or disclose management state. |
| Display/input | Guest-generated changing pattern reaches host; fixed key/touch event returns guest-visible acknowledgement | Reject invalid dimensions/stride/length, flood and out-of-range events. Verify management escape and input routing remain available. |

Positive controls run with synthetic data and are labeled separately so their
intentional access/egress cannot be mistaken for worker leakage. No exploit against
unrelated apps or real private data is part of the test. Negative results establish
only the tested routes; no finite probe suite proves universal absence of escapes.

### 5. Minimal interactive path

Use a guest framebuffer/test-pattern producer and minimal guest input consumer.
Record the actual emulated display/input devices, worker-to-presenter capability,
frame hash/sequence, maximum dimensions/bytes and observed latency. Test resize or
reject it explicitly. Input includes a fixed key and coordinate event with guest
acknowledgement. A serial boot log alone is insufficient for this row. Do not
upgrade the claim to Android rendering, IME, accessibility, camera or audio.

### 6. Death, revocation and repeatability

Perform at least five cold boot/stop cycles with a fresh worker each time; test
worker kill, normal stop, crash, management death/relaunch, foreground/background,
screen-off/resume, rotation and normal memory pressure. Record each PID/UID and
instance epoch. Test stale Binder handles, duplicated FDs, retained shared mappings
and queued input after revocation/restart, including access attempts from a previous
worker if still alive. Verify the old worker is dead/reaped and no child survives.
Do not assume closing management's FD revokes the recipient or that unbinding
immediately kills a worker. If revocation requires killing/reaping the worker, state
and test that contract, including management death; an orphaned capable worker is
not successful revocation.

Test at least two sequential instances for cross-instance residue. Any concurrent
peer-isolation claim additionally requires two simultaneous workers. Scratch state
and allowed logs may persist only as declared; capabilities and management tokens
must not silently carry over. Loss of observation, denied lifecycle controls or
inconclusive reap status is Unknown and prevents a full scoped positive result.

### 7. Resource and lifecycle observations

Measure management and worker separately: baseline/peak/steady RSS and PSS,
CPU usage, TCG cache, startup time, frame/input latency, disk growth, process
lifetime and death reasons. Run a predeclared 10-minute idle guest and 10-minute
bounded CPU/display load, recording thermal status, battery level/change and
power/charging/ambient conditions where observable. Distinguish estimates from
instrumented energy measurements. Include memory-pressure and background results,
without developer exemptions, changed memory limits or service tricks that violate
normal stock operation. A short successful run does not establish sustained
Android-guest usability or a production battery budget.

## Explicit falsifiers and disposition

**FAIL / stop this candidate direction for the tested scope** if any of these is
required or observed. Preserve diagnostics; do not relabel failure as a pass by
changing the authority contract.

- QEMU/TCG needs forbidden root, Magisk, Shizuku, platform/system privileges,
  development grants, custom policy/kernel/ROM, userdebug/eng, KVM or production ADB.
- TCG cannot execute in the isolated process on the declared target scope without
  an executable-policy bypass, or the worker has to share trusted management's UID.
- QEMU needs broad management-filesystem authority, arbitrary host opens, broad
  external storage, or required resources cannot be narrowly delegated.
- Native worker code can access the protected sentinel/management state, invoke
  unintended management operations, or obtain a peer's capabilities.
- Normal minimal operation requires broad device/permission authority inconsistent
  with the model; undelegated network/device authority is found and cannot be
  bounded without prohibited privileges.
- Revoked/stale capabilities remain usable contrary to the declared lifetime
  contract, or worker death/restart leaves management/peer authority exposed.
- Minimal boot/display/input cannot operate within preregistered budgets and normal
  stock lifecycle/memory constraints for the tested scope.

A source/build retrieval error, broken observer or incomplete control is
**inconclusive / Unknown**, never a success or universal impossibility. A scoped
failure does not rule out all user-space mechanisms or every OEM, but blocks work
dependent on the failed configuration. NARROW or material REDESIGN requires the
existing owner/ADR process. Budget changes require a new declared run, not a
retroactive pass.

## Evidence package and acceptance review

Publish a reviewed, bounded text record with exact source/build/artifact hashes,
public host build/model/ABI/page-size identity (no unique serials), permission and
SELinux observations, capability inventory, procedures, expected/actual outcomes,
positive/negative controls, failure logs and measurement methodology. Account for
all inherited FDs and known Binder/deputy surfaces, with blind spots explicit.
Preserve build environment/tool versions, patch/config identity and a reproducible
run recipe; this PR contains none of those future artifacts. Keep signing secrets
and confidential build paths outside public records. Redact sensitive raw captures
before publication and state how redaction limits reproducibility.

| Outcome axis | Current result |
|---|---|
| Ordinary APK / isolated native loading / TCG execution | Unknown — not run |
| Independent Linux kernel boot / disk FDs | Unknown — not run |
| Native authority probes / protected sentinel | Unknown — not run |
| No ambient network, storage, camera/microphone/location authority | Unknown — not run |
| Framebuffer/input / resource envelope / lifecycle | Unknown — not run |
| Revocation, restart and cross-instance separation | Unknown — not run |
| Complete controlled Android 17 guest and defensible boundary | Unknown — not implemented |

Only if all declared experiment conditions and controls are met may reviewers
record the bounded mechanism result quoted above. **A successful tiny Linux boot
MUST NOT equal Gate 0 Passed.** The complete interactive controlled Android path,
legitimate distribution/provenance and defensible prospective boundary still need
review. Gate 0 remains Unresolved until its own evidence and decision criteria
are satisfied; security still requires later adversarial and independent review.

Conditional follow-on: propose a controlled Android 17 complete-guest spike using
upstream QEMU `virt` plus selected virtio devices, with Cuttlefish/AOSP as references
for a stable virtual-hardware/broker contract. Do not implement that spike until
the required reviewed Gate 0 pass under PDVA-REQ-006. This experiment specification
creates neither a production-engine ADR nor authorization to bypass that sequence.
