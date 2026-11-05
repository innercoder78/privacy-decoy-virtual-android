# Java-only executable-memory feasibility: candidate identified, artifact STOP

Date: **2026-11-04, America/Fortaleza**. Reviewed main:
`78c4d550a81ef5e96940a4fafac18a5d983665f2` (merged PR #56).
**Gate 0 Unresolved; Gates A–G Not reached.**
**Separate companion artifact: NO-GO / not built. Original native-launch
readiness: NOT READY — STOP. No phone operation authorized or performed.**

## Decision and exact scope

A useful public-SDK, Java-only mapping-admission experiment exists in principle.
It does not require JNI, generated instructions or a subprocess. The closest
candidate uses `Os.memfd_create`, `Os.ftruncate`, two `Os.mmap` requests and
`Os.munmap`/`Os.close`. This is a positive API-surface finding, **not a prepared,
independently qualified safe physical experiment**. Implementation and artifact
production stop at unresolved applicable build-environment qualification below.
No companion APK, application identity, signing identity or installation packet
is supplied. This is the requested focused STOP evidence, not a finding that
Java memory-policy research or Android emulation is universally impossible.

Traceability: PDVA-REQ-002–003, 006, 008, 010–013, 036–042, 044–045, 048, 051,
054; [Gate 0](../feasibility-gates.md), specifically ordinary-app executable
behavior and legitimate distribution. The existing
[TCG split-mapping hypothesis](gate-0-tcg-executable-memory.md) remains unproved.
The companion would exercise trusted diagnostic code in its own ordinary app
process; it would not move the engine or hostile execution into management.

## API authority and direct SDK check

Official references were consulted on the date above. References are mutable
contracts, not immutable source snapshots or observed Samsung behavior.

| Surface | Authority / availability | Narrow meaning |
|---|---|---|
| `Build.VERSION.SDK_INT` | [Build.VERSION](https://developer.android.com/reference/android/os/Build.VERSION#SDK_INT), API 4 | Runtime API integer; not proof of stock/nonrooted production state. Require 37 for this experiment's scope. |
| `Build.SUPPORTED_ABIS`, `Process.is64Bit()` | [Build](https://developer.android.com/reference/android/os/Build#SUPPORTED_ABIS), API 21; [Process](https://developer.android.com/reference/android/os/Process#is64Bit()), API 23 | Reduce to ARM64-supported/other and current process bitness. Supported ABI is not evidence of an actually selected native engine ABI. |
| `Os.sysconf(_SC_PAGESIZE)` | [Os](https://developer.android.com/reference/android/system/Os#sysconf(int)) and [OsConstants](https://developer.android.com/reference/android/system/OsConstants#_SC_PAGESIZE), API 21 | Page-size input to bounds/alignment, not executable permission. |
| `Os.memfd_create(name, MFD_CLOEXEC)` | [Os](https://developer.android.com/reference/android/system/Os#memfd_create(java.lang.String,%20int)), API 30 | Public creation of an anonymous descriptor; actual admission can fail. |
| `ftruncate`, `mmap`, `munmap`, `close` | [Os reference](https://developer.android.com/reference/android/system/Os), API 21 | Size, map and release app-owned memory/descriptor. Mapping returns an address; no pointer dereference or execution is needed. |
| `ErrnoException.errno` | [ErrnoException](https://developer.android.com/reference/android/system/ErrnoException#errno), API 21 | Report stage and numeric errno with fixed categories; avoid exception messages, paths, addresses or stack traces. |
| `SharedMemory.create/map/setProtect/unmap/close` | [SharedMemory](https://developer.android.com/reference/android/os/SharedMemory), API 27 | Alternate bounded public interface. A protection ceiling is not a per-VMA protection transition; removal affects future mappings, not existing ones. |

Direct observation: existing Temurin JDK `javap` inspected the installed API
37.0 SDK stub JAR. It exposes the listed memory operations and constants,
including `memfd_create`, `MFD_CLOEXEC`, `MAP_SHARED`, `PROT_READ`, `PROT_WRITE`,
`PROT_EXEC` and `_SC_PAGESIZE`. No public `Os.mprotect` signature was present;
the official reference also contains no such method. Do not invent that Java
API or use reflection, hidden interfaces, Unsafe or JNI to obtain it.

Inspected SDK package: Android 17, revision 2, extension 22, preview SDK 0;
JAR SHA-256 `bf1b4387cc7ca94fc6ef684f040d9d16fbf16248e181819f020736ea2053f177`.
This binds the signature inspection only, not toolchain trust, OEM behavior,
compiled application correctness or an APK. Existing Android CLI
`1.1.16717390` performed the documentation search. Its initial sandbox launch
was access-denied; the permitted documentation-only retry succeeded. No SDK
installation, CLI update, device discovery, ADB or emulator command was used.

## Smallest falsifiable physical candidate, not implemented

**H-map:** on the specifically qualified stock API-37 host, an ordinary app
process can obtain simultaneous shared RW and RX mappings of one app-created
memfd page using public SDK calls, with neither mapping individually RWX.
This is a necessary allocation condition for a comparable split-W/X strategy
in that process context, not a necessary condition for every CPU-emulation
strategy. In particular, an interpreter need not use executable mappings.

Proposed bounded method for later independent review:

1. One visible, explicitly pressed action; no startup/lifecycle/intent trigger,
   retry loop, service, worker, native library, external dependency, network or
   permission. No persistent private results or automatic export.
2. Check API 37, ARM64 support and 64-bit process; query page size once. Admit
   only 4,096 or 16,384 bytes for this initial scope; anything else is Unsupported,
   not evidence of an Android limitation. No device identifiers or generic survey.
3. Create one fixed-name memfd with `MFD_CLOEXEC`, resize to exactly one admitted
   page, request one `MAP_SHARED` RW mapping and one `MAP_SHARED` RX mapping at
   offset zero with address hint zero. Maximum two VMAs / 32 KiB virtual mapping
   extent over at most 16 KiB backing storage. Never request `MAP_FIXED` or RWX.
   Do not write instructions, dereference raw addresses or execute mapping bytes.
4. Track each successful acquisition separately. Attempt each owned unmap and
   descriptor close even if another cleanup operation fails; do not replace the
   first failure with a later apparent success. No fallback allocator, pathname,
   broader flags/authority, alternate process or automatic second attempt.
5. Show a fixed-size, fixed-vocabulary stage/result record. Success requires both
   mapping returns and completed cleanup calls. An interrupted run, cleanup error,
   unexpected exception or incomplete record is Unknown and stops further use.

An `EACCES`/`EPERM` at a named mapping operation would reject H-map for those
parameters and that context. `ENOMEM` is a resource failure; `EINVAL` may mean
parameters or platform support; `ENOSYS` means the requested operation is
unavailable. None alone identifies SELinux as the cause or proves universal
platform impossibility. Preserve exact numeric errno; unknown errors remain
Unknown. No runtime observations exist here.

Successful calls would establish only admission and reported cleanup. They do
not test writing/executing code, cache coherence, BTI, QEMU flags/seals/allocator
closure, actual VMA permissions by an independent observer, hostile isolation,
resource exhaustion, process death or complete virtual-phone viability. The
ordinary app's policy context differs from an isolated worker's. Separate RW/RX
aliases can modify executable storage through the RW alias and are not a
security boundary. Bounds on calls/bytes do not establish a hard syscall latency
bound or a safe cancellation implementation. Activity interruption and cleanup
must be designed and fault-tested before this method becomes runnable software.

`SharedMemory` is an alternative, not equivalent evidence for QEMU memfd policy.
Its `setProtect` cannot substitute for RW-to-RX `mprotect`: existing mappings
retain their permissions. A later ceiling-removal experiment could test future
map rejection but would not demonstrate revocation of retained writable aliases.
An API/ABI/page-size-only APK would be insufficient and was not constructed.

## Why this separate scope still stops at artifact qualification

The [incident record](gate-0-native-host-antivirus.md) and
[readiness audit](gate-0-native-launch-readiness-audit.md) distinguish quarantined
Windows PE controls from Android APK/ELF artifacts. A Java-only companion would
not build or execute those controls, load their native libraries, use the old
worker, or inherit its incomplete bind/descendant lifecycle. **Those runtime
blockers are not mechanically imposed on this distinct diagnostic.**

The shared dependency is the proposed build/signing environment: existing JDK,
SDK, Gradle, AGP/transitive caches, extracted tools and signing material. The
records provide neither a qualified incident disposition excluding an effect on
that environment nor an independently qualified replacement environment. Source
separation, hash pins and a successful build do not establish that exclusion.
This is an **unresolved applicability/trust prerequisite**, not a claim of host
compromise or contamination of Java output. No new detection is asserted.
No private security records or quarantine were accessed; no exclusions, restoration,
vendor submission or security-setting changes were made.

The reviewed tooling candidate remains Gradle 9.6.0, AGP 9.4.0, JDK 17, SDK
37.0/revision 2 and build-tools 36.0.0; the existing
[dependency ledger](gate-0-isolated-worker-dependencies.md) has 185 components /
322 pinned artifacts and no app runtime Maven dependencies. These are existing
pins, not a newly attested build chain. NDK/CMake/native payload construction
would have no role in the Java-only candidate. The current module's native build
graph is unsuitable for merely relabeling its APK as a companion.

[ADR-0003 Option A](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md)
remains intact. Fifteen historical signed-byte equality failures are not new
companion results, and no prediction of a particular companion APK hash is made.
No route satisfying the unchanged qualification requirements is supplied.
Do not disable dependency metadata, normalize signed bytes, alter signing,
resurrect D1/D2 or treat source/ZIP correspondence as strict signed-APK equality.

**Stop before implementation/build qualification:** the task explicitly requires
NO-GO and STOP if applicable findings cannot be qualified. A qualified analyst
must resolve applicability to this Java-only build chain, or independently qualify
a replacement chain, with exact provenance and signing custody. Then independent
review must qualify the separate implementation/artifact under unchanged policy.
No architecture change is needed merely to investigate H-map. Any proposal to
waive existing security/reproducibility obligations would require an explicit
owner-approved governance decision; this record requests and grants no waiver.

## Live preflight, preservation and validation

GitHub commit API and Git `ls-remote` both returned the main SHA above. Connector
and CLI inventories each returned zero open PRs: no open head/base/diff/file,
check/job/log/review/comment/thread inventory existed to reconcile. The merged
PR #56 diff and relevant #8/#49/#50/#53–56 evidence/history were inspected.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational (page update `2026-11-05T01:44:18.406Z`). A sandbox network
denial was resolved by a permitted read-only CLI retry, not classified as an outage.

Exact-main [foundation run 41954841857](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41954841857)
and [Android run 41954841886](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41954841886)
completed successfully. All three job/step records and downloaded logs were
checked: Linux controls and their negative controls, Windows 45 image / four
frame-copy tests, Android assembly/protocol, no-follow mutation, 600 JVM entry
denials / three rejected lock mutants and five packaged-policy tests. These are
**baseline receipts**, not candidate physical or fresh APK evidence. The connector's
PR-event-only workflow query returned no runs; the all-event CLI query found the
push runs above. Absence from the first query was not treated as absence of CI.

Initial local state: clean main, one worktree, existing branches and no stashes;
no applicable AGENTS.md found. Work uses `codex/java-memory-feasibility-stop`.
Existing ignored build/native/APK/reference/private assets were preserved. The
ignored inventory emitted Windows long-path warnings, so complete recursive
inventory of those directories is not claimed. Independent backup of private
evidence remains unverified. No new private device data or APK was produced.

Only this evidence document and its index entry change. Requirements, ADRs,
dependencies, workflows, signing configuration, original harness and execution
lock remain byte-identical to main. No binary, mode change or adopted source.
All three workflow definitions were reviewed: foundation applies to this PR;
unchanged Android/QEMU path filters do not select this documentation-only diff.
No mandatory step/filter/assertion is changed, skipped or masked by this PR.

Actual local validation used existing CPython 3.12.14 and Temurin 17.0.20.1+1:

| Validation | Actual result / limit |
|---|---|
| Foundation and harness validators | PASS; 155 files, 97 Markdown files, 54 requirements, three ADRs; source manifest authority only. |
| Repository regressions | 152 tests: 148 passes and four existing Windows skips, not a complete Linux run. Includes rejection of injected permissions and unsafe manifest changes. |
| Desktop readiness, offline-image, frame-copy suites | 28 / 45 / four passed; synthetic fixtures and desktop process/mapping controls, not Android execution. |
| Existing execution-lock JVM test | 600 denials over three fresh JVMs before Android SDK access. All three compiled mutants (remove lock, ordinary-only lock, death-only lock) rejected at the required Binder-stub tripwire. This is a meaningful unsafe-regression control on the unchanged lock, not a companion test. |
| SDK signature inspection | PASS for the identified stub JAR; no compiled companion or Android runtime test. |
| New Android builds, signing, compiled companion APK tests, physical test | NOT RUN; artifact qualification stopped. No qualified APK exists. |
| Local Linux/native controls | NOT RUN; baseline hosted receipts above are separate. Required foundation CI remains applicable and unobserved for this new PR. |

The initial PATH `python` was a nonworking Microsoft Store alias. Validation
used the existing bundled interpreter by explicit path; no runtime was installed.
No mandatory test was removed or reclassified. Complete two-file diff, file
modes, unchanged non-documentation inputs, local links, whitespace and public-data
hygiene were reviewed before commit. No private artifacts are published.

New companion
source/JVM/compiled-APK tests are **not applicable: no implementation or APK**.
They are not passing tests. A future implementation needs actual cleanup/error,
initiation/lifecycle, sanitization, bounds and compiled-manifest/DEX/inventory
tests, with a precise unsafe-regression negative control. Existing controls do
not substitute for that qualification.

## Remaining proof and owner decision

There is no reviewed artifact to install, so no Windows 10/Samsung installation
procedure is issued. After environment clearance and independent source/artifact
qualification, the next specific physical proof would be one deliberately
initiated H-map attempt using exact reviewed source/APK/signer identity and an
ordinary permitted installer route. Preparation must define cancellation,
interruption/cleanup classification, bounded private capture and independent
backup without identifiers. Unexpected behavior or unexplained failure means
stop, retain Unknown and obtain review, never retry or work around protection.

Tony's explicit authorization must follow that complete packet and independent
review. PR publication or merge cannot authorize installation or execution.
The original isolated-worker/native-launch experiment stays locked, with no
switch, alternate entry or readiness change. Publish exactly one evidence PR,
attach it to this chat, check association once, then stop without CI/review polling.
