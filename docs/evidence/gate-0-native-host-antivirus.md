# Gate 0 native host antivirus investigation

Date: 2026-10-11. Status: **source correction for review; exact-head Ubuntu CI pending**.
Gate 0 remains **Unresolved**; Gates A–G remain **Not reached**.
Scope: PDVA-REQ-039–043 evidence and PDVA-REQ-050–051 validation, under the
[existing governance](../governance.md) and
[provenance policy](../source-provenance-policy.md).

## Preflight and preservation

Live canonical main was `c2c63c86b5cee06d828d11377508cf54b3c0503e`, tree
`3e3998aa4ff273e9c07a81ec5ef4d5288acf4b4e`. PR #7 merged head
`ec7e5f9f5420025d6ae2e6d2755df4333ad87f8f` against base
`cb6eb6853b79f7035ea96e26068b3771409f3425`. Live queries returned no open PRs,
no PR #7 comments/reviews/review threads, and three active workflows. Main
foundation run `38111869400` and Android run `38111869279` both succeeded.
[GitHub Status](https://www.githubstatus.com/) reported All Systems Operational.
These are baseline results, not validation of this candidate.

One registered local worktree was clean at the PR #7 head; its tree matched main.
No stashes were listed. An existing ignored nested clone was clean at main.
Previous build outputs, two surviving host objects and an earlier read-only
incident audit were preserved. The correction branch starts at verified main.
Continuation preflight found exactly the five intended candidate files, one
registered worktree and no stashes. Main, open-PR inventory and PR #7 metadata
were rechecked and unchanged. The existing edits were reviewed and retained.
No quarantine, security setting, requirement, ADR, Android runtime dependency,
production source or physical-device state was changed. ADR-0001 remains Accepted
and ADR-0002 Proposed. No VM engine is selected.

## Direct antivirus observations

Read-only Malwarebytes RTP records identify both entries below. Times are
America/Fortaleza (UTC-03:00). Paths are relative to the repository, with no
personal absolute paths, raw logs or screenshots included.

| Detection time | Relative file | AV-reported SHA-256 |
|---|---|---|
| 2026-10-10 22:05:19 | `android/build/host-controls/launch-wait-test.exe` | `4f3af283dbbae9d391e6d9ff186c1a6d5dfc78d1c92bc2096b9d9b702b15cf1c` |
| 2026-10-11 02:33:58 | `android/build/g0/android/build/host-controls/launch-wait-test.exe` | `41c2102f6ea34735d1229d9a77f430295d61006a206a5dc978498b35632118e2` |

Both reports: Malwarebytes 5.7.2.358, `Malware.Heuristic.2107`, rule 1246552,
valid PE, 1,024 bytes, not report-only, quarantine successful two seconds after
detection. Rules versions were respectively 1.0.115581 and 1.0.115589. Both
original EXEs are absent. Hashes above were recorded by the AV, not independently
recomputed from quarantine. Neither report supplies a parent-process chain.

The prior command ledger records NDK clang targeting Windows x64 with
`-ffreestanding -O2`, followed by
`ld.lld -flavor link /entry:main /subsystem:console /nodefaultlib` and a bounded
attempt to run the EXE. Its exit-zero message overlaps the later quarantine.
The service excerpts retained by the earlier audit record access blocking and
quarantine. An unconditional Windows test pass is withdrawn; this is a real
interruption of the artifact lifecycle, even though the shell printed success.

Fresh hashes of surviving objects, in the same event order:

- `f070c6b58530ad82d1a6547ac786a44eacad5088e4c8a5ef863ff24ecfaf62e1`
- `e5e40b9885b02911ad618e52ebffe37fa4129be2348f4487defe5647f7e9d4cb`

The earlier static audit found the later object's `.text` was only `31 c0 c3`
(return zero), with the deterministic test folded away by optimization. This is
an object-file observation, not authentication of the quarantined EXE.
Path, timing, object and recorded command correlate the event to PDVA controls;
exact executable correspondence and creator ancestry remain **Unknown**.

The reviewed C test uses injected operations and bounded counters; it contains
no real fork, signal, sleep, network or filesystem access. This supports benign
source behavior within this narrow test, not a binary safety verdict. Minimal
PE construction is a possible heuristic contributor, not an independently proven
explanation. The different hashes have not been explained by byte comparison.
No false-positive or malicious classification has been established.

## Proposed correction

The test now uses the host's `<errno.h>` and `<assert.h>` instead of invented
Linux errno numbers and `__builtin_trap`. Each scenario resets errno and prints
its name after its assertions. `NDEBUG` is a compile-time error so a
release define cannot silently remove checks. All seven scenarios remain:
immediate reap, EINTR retry, timeout/reap, ECHILD without kill, kill failure,
clock failure, and frozen-clock iteration bound.

Continuation review strengthened the checks to exact wait/kill/pause counts and
explicit result/error fields. Expected counts are source-derived expectations,
not local runtime observations:

| Scenario | Wait calls | Kill calls | Pauses | Required outcome |
|---|---:|---:|---:|---|
| Immediate reap | 1 | 0 | 0 | Reaped, status 42, no timeout/errors |
| EINTR retry | 3 | 0 | 2 | Two retries then reap, status 42, no timeout/errors |
| Timeout and reap | 251 | 1 | 249 | Timeout then reap, status 42, no errors |
| ECHILD | 1 | 0 | 0 | ECHILD, no reap/timeout/kill |
| Kill failure | 300 | 1 | 299 | Timeout, EPERM kill error, bounded cleanup, no reap |
| Clock failure | 51 | 1 | 50 | Immediate timeout then bounded cleanup, no reap |
| Frozen clock | 350 | 1 | 350 | Iteration-bound timeout and cleanup, no reap |

Ubuntu CI runs the real binary under a five-second timeout and requires all seven
distinct result lines in order. A separate bounded run of the same binary with
`--fail-assert` must produce SIGABRT and the injected assertion diagnostic. Exit
zero, timeout, missing executable or any other failure cannot count as successful
negative-control evidence. Core dumps are disabled for that expected abort only.
The real test's exit status is checked independently before the negative step;
there is no continue-on-error or global expected-failure wrapper. Configured
counts: **7 positive scenarios + 1 assertion negative control**. Actual candidate
Ubuntu execution: **pending**, to be reviewed on the published exact head.

The [host procedure](../../android/README.md#native-wait-controls) uses normal
compiler-driver linking, C runtime startup and no optimization/LTO. Ubuntu's
required native execution and five-second timeout remain in foundation CI;
`-O0` is explicit. Windows instructions propose MSVC C11 with `/MD` and `/Od`.
Microsoft documents [default CRT entry-point handling](https://learn.microsoft.com/cpp/build/reference/entry-entry-point-symbol?view=msvc-170)
and [C language standard selection](https://learn.microsoft.com/en-us/cpp/build/reference/std-specify-language-standard-version).
No compiler or runtime was installed or adopted during this investigation.
The executable keeps its name. This changes test portability and diagnostics,
not signatures, concealment or the production wait algorithm. `launch_wait.h`
and all Android production files are unchanged.

## Separate Android review

Reviewed source: `launch.c`, `launch_payload.c`, `probe.c`, WorkerService,
Session, Protocol, manifest and build configuration at the main revision above.

**A — documented research operations:** the explicitly started research app
uses synthetic sentinels, scratch files, memory and frame/input data. JNI tests
RW-to-RX generated code, process-memory/ptrace authority, fixed device-node
opens and loopback socket authority. The isolated worker forks and attempts
execve of one fixed installer-owned ARM64 dynamic PIE, with fixed argv and
environment, descriptor closure, resource limits, parent-death signal and
bounded reap. The payload reads bounded self-process metadata and reports a
fixed record/exit 42. These operations could reasonably attract scanner scrutiny.
They are required experiments and were not removed.

**B — unnecessary/risky behavior:** native execution, generated code and process
authority probing are real risk surfaces, even with synthetic inputs. Review
found no independently justified Android change for this Windows incident.
There is no caller-supplied command, shell, executable download or path-search
launch in the reviewed path. Worker IPC checks caller UID, epoch, bounds and
operation order; Session persists uncertain cleanup before launch IPC. Those
checks do not prove containment. The app requests no permissions; only its
launcher activity is exported; the worker is non-exported and isolated. No
broad permission, persistence service or automatic external-data upload was
identified. Clipboard export requires a user operation.

**C — scanner Unknowns:** the APK and its ARM64 ELF payload are different formats,
architectures and source paths from the Windows PE test. The executable's
`libpdva_launch.so` name is the documented Android installer extraction convention,
not a JNI library; it is never dlopened. No Android scanner classification was
obtained or inferred from Malwarebytes. No artifact was submitted to scanners.

Build provenance remains the reviewed pinned Gradle 9.6.0 distribution, AGP 9.4.0,
NDK r28c and 185 Maven components/322 pinned artifacts in the existing dependency
record. There are no Maven app runtime dependencies. The earlier audit verified
320 cached files against pins and both Gradle extractions against the pinned ZIP;
this is historical evidence, not a fresh full-toolchain attestation. Signing is
development-only even for the non-debuggable release variant.

## Validation and blockers

The earlier supported Defender query returned Normal mode, antivirus enabled,
real-time protection enabled and behavior monitoring enabled. Malwarebytes
service was stopped. No security configuration was changed. Defender activity
does not resolve the Malwarebytes finding or establish a clean-machine verdict.
At continuation, Malwarebytes service was Running and Windows Security Center
reported Malwarebytes productState `397312` (`0x061000`, enabled). Defender was
Stopped and reported Not running. Protection was not altered. The RTP report
directory still contained the same two incident records; no new detection was
observed in that inventory. This is not a complete host-compromise assessment.

No `cl`, `gcc`, `cc` or host clang was found on PATH, nor Visual Studio/Windows
SDK development roots or common MinGW installations in the inspected locations.
The available compiler is the Android NDK. WSL reports no installed distribution.
A conventional trusted Windows host development runtime and local Ubuntu native
environment are therefore unavailable for this candidate. No substitute minimal
PE was built. No native control execution is claimed.

Fresh checks in this investigation:

Continuation reran foundation, all 108 repository regressions (four existing
Windows skips), harness source checks and static inspection of all three retained
APKs. Tracked Python files and both inline CI Python blocks passed AST syntax
checks. The foundation validator includes local Markdown-link checks and tracked
binary/provenance hygiene. No new native binary or Android build was executed.

| Check | Observed result and scope |
|---|---|
| Foundation validator | Passed: 77 files, 42 Markdown files, 54 requirements, 2 ADRs. |
| Repository regressions | 108 tests, OK, 4 pre-existing Windows skips. |
| Harness source/manifest authority | Passed. |
| Retained APK hashes and ZIP CRC | All three match the prior audit; no newly built APK is claimed. |
| Retained debug/release manifests | Passed packaged authority checks using static binary XML decoding; release non-debuggable, no permissions, expected components. |
| Exact packaged native bytes | Expected two JNI libraries and one ARM64 PIE; hashes match prior audit. Validator checks ABI, interpreter, PIE, RELRO, immediate binding, non-executable stack, no W+X, 16-KiB load alignment, payload stack protector and allowed direct dependencies. |
| Present Maven dependency files | 320 checked against pinned hashes, zero mismatches. Linux/macOS aapt2 JARs absent; not downloaded. An initial query used an incorrect XML namespace and failed its nonzero-count assertion; corrected namespace discovery yielded the stated count. |
| Diff/whitespace/modes | Reviewed five intended text files; no production-source, dependency or Android-build changes; no mode changes; whitespace check passed. |

Fresh retained artifact SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| Release APK | `10b7aa57b06b1832f77eac72b75108ef5bab1a6e10d0758488ad3d33dda87eae` |
| Debug APK | `8638d158b1c6cd9d09bcf2425f24a99065830f6f05ba571e8d880304f5ac0826` |
| Instrumentation APK | `e23b840945d58db280d4b56e4f63e0b229eb7237a2fe9acace900c6a143c736d` |
| ARM64 payload in both variants | `6c95e1aa9342422e7c70ce8bc63c318408e628bd7eea5507aca3d4081033e789` |
| Release ARM64 JNI | `b4572e1ae78dd0bbbc54a973fe6a3a9d0dbb6cb42a183ebea962f3a350e05985` |
| Release x86_64 JNI | `eff36c8d08b22b6a70de23d982534f8b0a749391d632e186e33ea408a5930a0a` |

The payload directly needs libc/libdl and the JNI libraries add libm. The dynamic
PIE interpreter is `/system/bin/linker64`. Actual device linker closure,
installer extraction and physical behavior remain Unknown. Instrumentation APK
verification here covered unchanged bytes and ZIP integrity, not execution.

Source identities use LF-normalized bytes:

- Candidate `launch_wait_test.c`: `78642a999efc9a9e0118456874aedf81a2973a60bef0e5ee8dddcb5db09cd3e5`.
- Unchanged `launch_wait.h`: `ecd9bacd370214fd87fd78c6680a2a3a5b3904b71e02d343fb9cc57a0c2f14be`.
- Unchanged verification metadata: `4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.

Native Windows and Ubuntu candidate runs remain **Not run**. New Android debug,
release, instrumentation, protocol and lint builds remain **Not run**; the
unresolved binary-provenance incident is not converted into a rebuild clearance.
Existing main CI success is historical only. Physical Android execution remains
**Not run**. The initial task withheld publication pending native validation.
The continuation explicitly authorizes this reviewed source-only correction for
PR review and required Ubuntu CI without a Windows toolchain, WSL installation
or vendor false-positive ruling. Those missing local results therefore no longer
block source publication. They remain Unknowns, not passes. Required exact-head
Ubuntu execution and Android CI are **pending**, not inherited from main.
Publication does not resolve the incident or approve installation of an APK.

## Disposition and vendor route

Obtain vendor or qualified analyst disposition using the two detection hashes,
rule/version, source and exact compiler/linker construction; do not restore or
allowlist samples. Malwarebytes offers an official
[suspected false-positive reporting procedure](https://help.malwarebytes.com/hc/en-us/articles/31589211404571-Report-a-false-positive-to-Malwarebytes-Support).
Owner review is required before sharing any private diagnostic records or samples;
no submission occurred here. Do not follow exclusion/restoration advice as part
of this task. Once security permits execution and a reviewed host environment
is available, run the seven controls and required fresh Android validations.
Stop and preserve evidence on any new detection; do not iterate to evade it.

A clean scan does not prove security. Green CI does not prove physical Android
safety. Malwarebytes has not approved this candidate, and universal Android
antivirus compatibility is not claimed.
