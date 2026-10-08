# Gate 0 isolated-worker substrate harness

**Implementation slice dated 2026-10-07. Physical outcomes Unknown. Gate 0
Unresolved; A–G Not reached. No engine selected.**

This is a preparatory **pre-QEMU** slice of the
[governing isolated-QEMU proof](gate-0-isolated-qemu-proof.md), not a new
architecture decision or gate pass. It asks whether an ordinary APK can run a
native isolated-UID worker with explicit capabilities while keeping management
state outside that worker. Complete Android 17 guest behavior remains unimplemented.

## Verified starting point and scope

Live canonical main was `f85f1505c0c320ce7b3bdbb2cd817d56ef1dbcbb`; no open
PDVA PR existed. Its exact-head foundation check and push workflow had succeeded;
the combined-status endpoint had no separate status contexts. GitHub Status
reported operational. Historical main was
`5320b3b44b38df4b8f3361ecbcb530386ff195e9`, with no open PRs. Historical source
and scaffolding were not adopted. The local clean prior-PR branch was preserved,
and this work began on a new branch from canonical main.

The preflight tree consisted of 38 regular mode-100644 text files, with no
Android build or binary dependency. Governing requirements, ADR-0001, provenance,
governance, roadmap, CI and experiment records were inspected. This explicit
research implementation request moves beyond the bootstrap-only source whitelist;
it does not reinterpret foundation-stage restrictions as product approval.
No requirements or ADRs change.

## Implemented capability contract

| Component/capability | Authority and limits |
|---|---|
| Management Activity | Creates synthetic resources, owns epoch and expected sentinel digest, verifies results, provides manual copy. Stops/cancels on background or recreation. No custom Application preload. |
| Dedicated worker | Non-exported isolated Service, no app zygote or shared isolated process. Unique `bindIsolatedService` instance name per random 128-bit epoch. No fallback to management UID. |
| Synthetic sentinel | 4096 random bytes in private app storage. Worker receives neither contents, digest nor FD. It constructs exactly the fixed sentinel locator, and receives the manager's numeric sentinel FD only to test the known proc route. No arbitrary path input exists. |
| Canary FD | A 4096-byte synthetic file opened read-only. Positive read, direct write rejection, duplicate-close lifetime and proc-self-FD reopen observations. |
| Scratch FD | Read/write access to one synthetic 4096-byte initial file; no directory FD. The fixture writes byte zero and management checks all remaining bytes. The descriptor authorizes the whole file, including potential growth; initial size is not a kernel quota or byte-range sandbox. |
| Shared frame | Exactly 64x64 RGBA bytes, 256-byte stride, 16384 bytes. Worker RW mapping, management RO mapping. Two frames maximum; byte sequence and SHA-256 checked by management. No display device passthrough. |
| Input | Integer sequence and token 0–255, deterministic XOR acknowledgement, 16 events maximum, replay/out-of-order/flood rejected. |
| Synthetic memory control | Management JNI allocates a 4096-byte known-filled region only for cross-process access tests. Worker gets its address and targets the authenticated calling manager PID. No real management objects or sentinel content are transferred. |
| Owner Binder | Empty management Binder serving only as a death token. No management command/broker methods. Worker links owner death to self-termination. |

The typed hand-written Binder protocol has six fixed operations: INIT, RUN,
FRAME, INPUT, STOP, KILL. Every operation carries the interface descriptor and
epoch; all except the single INIT require the active epoch. Service checks the
calling management UID, rejects one-way/oversized/unknown/trailing requests,
validates regular-file FD modes/sizes, and rejects excess frame/input work.
No Bundle, arbitrary command, generic Binder proxy, arbitrary path-open,
directory capability, shell, exec, QMP, or worker-initiated FD forwarding exists.
INIT failure permanently closes that worker to retries.

An absolute 30-second worker lease runs on the Service main thread, independently
of Binder probe work. Normal STOP closes resources and self-terminates.
KILL deliberately self-terminates with open capabilities to exercise kernel
cleanup; management never kills a PID merely supplied by a worker response.
Owner death and unbind also trigger worker self-termination. Management observes
Binder death, waits up to three seconds during cleanup, and refuses another
session if prior worker death is uncertain. It does not claim independent
kernel reaping or absence of surviving descendants. Management/native memory is
not reused when worker lifetime remains uncertain.

## Probe interpretation

The C library is PDVA-owned C11, loaded in the worker. Its small management-only
JNI allocation helper exists solely for the synthetic memory control. Both
paths run with their ordinary process authority.

| Probe | Observation and interpretation |
|---|---|
| Native identity | PID, UID/eUID, GID/eGID, up to 32 supplementary groups, compiled ABI, page size, framework isolated predicate and distinct management/worker identity. Group overflow/read failures remain incomplete. |
| Proc inventory | Counts of self FDs, mappings and executable mappings; bounded SELinux-context string if readable. No raw mapping/FD targets are exported. Complete inherited-handle attribution remains Unknown. |
| Generated executable memory | On ARM64, fixed little-endian `mov w0,42; ret` words `52800540 d65f03c0`; one anonymous RW page, cache flush, mprotect RX, call and exact return check, unmap. Never RWX and no bypass fallback. mmap/mprotect failures retain errno. memfd_create is a separate diagnostic, not an alternate executable path. Other compiled ABI reports Unsupported/UNKNOWN. |
| Sentinel | libc open read/write, direct openat syscall, and exact manager proc-FD route. Management verifies pre/post integrity. Unexpected success is FAIL/blocker. Only EACCES/EPERM supports the scoped denial proposition; missing resource or unsupported syscall is Unknown. No sentinel mutation is attempted even if open succeeds. |
| Process/memory | Only manager proc mem/fd/status, process_vm_readv/writev of the synthetic allocation, self controls, signal zero and non-stopping ptrace PEEKDATA. A successful memory access is FAIL. PEEK error is Unknown: no attach was attempted because it would stop the management UI. |
| Network | IPv4/IPv6 TCP/UDP socket creation. Successful creation is FAIL for the expected absence of that authority. If created, nonblocking connect to synthetic loopback port 9 only, no data or DNS. Raw numeric return/errno recorded. No external destination or traffic capture; all-route/no-egress claim remains Unknown. |
| Host surfaces | Permission checks for network/storage/camera/microphone/location; safe service-wrapper visibility only; fixed open-only external-storage, KVM, GPU, video and sound-node probes. Missing nodes are Unknown. No camera/audio/location data collection or unrelated app scan. |
| FD transport | Canary read, EBADF on original read-only FD write, scratch write, duplicate lifetime and proc-self-FD reopen read/write. A writable reopen is a separate FAIL rather than hidden by original-FD denial. |
| Display/input | Synthetic pattern/hash and token acknowledgement, malformed sizes, overflow-size input, range/replay/flood rejection. This is capability transport, not Android guest graphics. |

Generated execution success **does not prove QEMU TCG**. Sentinel denial **does
not prove universal containment**. No INTERNET permission **does not prove all
future networking is safe**. There is no guest kernel, guest Linux boot, QEMU,
guest image, Google package or selected production engine.

PASS/FAIL belongs only to each row's stated proposition. A harness test may pass
while the architecture hypothesis fails. Incomplete setup, inability to observe,
native crash, malformed result, unsupported syscall and absent physical device
must not become a security success. A confirmed native-load failure, executable
substrate failure, sentinel/memory access, shared UID or stale accepted authority
blocks dependent work on that configuration; do not weaken the design.

## Result schema and privacy

Management exports a JSON array of version-1 experiment objects. Each object
contains synthetic epoch, app version, host API, unchanged gate state, explicit
physical-evidence UNKNOWN, and ordered probe rows. Every row has probe name,
expected/observed values, numeric errno (zero when inapplicable), PASS/FAIL/UNKNOWN
and limitations. Native ABI, public OS release/security patch and SELinux context
are rows. PID/UID are experiment observations, not persistent device identifiers.

Only fixed labels, bounded numbers and sanitized public fields are admitted.
Worker JSON is bounded, parsed, checked for schema/epoch and reconstructed by
management. Untrusted exceptions, raw paths, raw /proc lines, memory addresses,
serials, Android ID, IMEI, account/Wi-Fi values, IP strings, sentinel data/digests,
keys and Persona values are never export fields. The serializer rejects slashes,
backslashes, quotes/control characters and oversized labels. UI copy is explicit;
there is no network upload, provider, exported worker, logging or automatic export.

## Validation and limits

See [build/run instructions](../../android/README.md) and
[adoption inventory](gate-0-isolated-worker-adoption.md). Implementation validation
uses Windows, Python 3.12.14, Temurin 17.0.20.1+1, the declared Android packages,
and hash-verified Gradle. ARM64/x86-64 debug and non-debuggable release builds,
development instrumentation compilation, JVM protocol/redaction tests, lint,
manifest/APK inspection, native dependency inspection and repository hygiene are
local build evidence only. No emulator or physical phone was used.

| Local implementation validation | Outcome |
|---|---|
| Debug and release APKs; ARM64 and x86-64 C/JNI compilation | PASS |
| Development instrumentation APK compilation | PASS; execution not run |
| Dependency-free protocol/serialization assertions | PASS, 48 checks |
| Repository/manifest regression tests | PASS, 17 tests with negative-case subtests |
| Android debug lint | PASS, no issues |
| Actual release APK manifest inspection | PASS, zero permissions and non-debuggable |
| Release native dependency inventory | Two PDVA libraries, platform libc/libdl/libm only |
| Repository validator, links, IDs, modes and whitespace | PASS |
| Public-data marker and APK private-build-path review | No matches in reviewed scope; not a universal secret scan |
| Authorized connected ADB device count | Zero; no install or device experiment |

AGP warns that the explicit built-in-Kotlin and AndroidX opt-outs will be removed
in AGP 10. These warnings are not suppressed; an AGP upgrade requires review.
The pinned 9.4.0 build succeeds with these settings.

The dependency-free JVM runner covers epoch initialization/stop/replay,
dimensions/overflow, quotas and deterministic/redacted serialization.
Repository regression tests exercise narrow path admission, binaries, sensitive
names, modes/conflicts, requirements/history/links and prohibited manifest authority.
Instrumentation hooks exercise actual Binder/FD/frame/native/lifecycle behavior
when installed, but were **not executed** here.

Physical native loading, generated execution, all denials, FD transport, frame/input
transport, management-death revocation, bind/stop/kill/rebind, rotation/background,
resource pressure, SELinux enforcement and independent process reaping are
**Unknown / not measured**. Binder/service enumeration is intentionally incomplete.
The 30-second lease is a harness mechanism needing physical testing, not a proven
orphan/reaping guarantee. Sustained resource/thermal/battery behavior, concurrent
peer isolation, QEMU TCG and complete Android 17 remain outside this slice.

The next QEMU source/adoption PR is conditional on review and physical substrate
results. This PR neither adopts QEMU nor authorizes that dependent integration.
