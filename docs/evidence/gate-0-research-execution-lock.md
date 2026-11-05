# Research APK execution lock

Date: **2026-11-04, America/Fortaleza**. Base main:
`7789896dd870246889aa2faa93bfa1e1962ae7fa`.
**Gate 0 Unresolved; Gates A–G Not reached; Physical NOT READY — STOP.**
Scope: accidental activation of the existing research harness, under
PDVA-REQ-008, 012–013, 039–043, 048 and 054. No physical experiment is authorized.

## Source discrepancy and reachable paths

**Confirmed in original source, not demonstrated on an Android device.** A person
opening the original APK could select either visible research button. With app
state accepted by the existing reservation predicate and successful platform
operations, the callbacks reached unfinished experiments despite the displayed
`Physical NOT READY — STOP`. The label was not consulted by execution code.
The reservation limits attempts; it does not establish readiness or authorization.

| Entry or transition at the base | Reachability and authority |
|---|---|
| Exported launcher `MainActivity.onCreate` | MAIN/LAUNCHER installs two click listeners: `run(false)` and `run(true)`. No approval/readiness check. Opening alone did not start an attempt; pressing a button did. |
| Activity `run(boolean)` | Creates `Session`, queues `session.run(death)` on its executor. An `active` check prevents overlapping UI submissions, not unauthorized first execution. |
| `Session.run(boolean)` | Checks cancellation, then reserves through the process-wide `ResearchAttempt`; accepted fresh state permits progression. Allocates sentinel/canary/scratch files and descriptors, shared memory and native control memory. |
| `bindIsolatedService` and connection callback | Binds the non-exported isolated `WorkerService`; adopts the first endpoint and links death. Session is the only application bind site. |
| Manager `request` / worker `onTransact` | INIT transfers owner Binder, descriptors, shared memory and synthetic control address. Worker checks caller UID, message bounds, fixed operations and epoch. These are protocol checks, not owner readiness approval. |
| Ordinary mode | FRAME/INPUT controls, RUN to `runProbes`/`NativeProbe.run`, then LAUNCH to private `WorkerService.launchNative`. ARM64 JNI reaches the retained fixed installer-directory payload through `fork`/`execve`; x86_64 reports Unsupported for that launch fixture. |
| Worker-death mode | Same reservation, resources, bind, INIT and transport controls, followed by KILL and delayed self-termination. |
| Stop/background/recreation | Cancellation hooks do not independently prevent the first request. Reservation persists conditionally across subsequent activity/process lifetime; it does not authorize the first request. |
| Development instrumentation | One direct Session request bypassed UI, then original probe and lifecycle assertions. Test APK is separate from the ordinary APK. |

Manifest review found one exported launcher, one non-exported isolated service,
no receivers/providers/aliases, no deep-link filter, no permissions, no shared UID
and no service intent filter. No other application bind/start-service route was
found. Worker lifecycle methods, Binder operations, `NativeProbe` JNI methods,
native launch and the dormant bootstrap were inspected. Worker/native internals
are retained executable research code; their mere presence is not a supported
activation route from this locked manager, nor a hostile-code containment proof.

## Minimal trusted-management correction

`Session.run(Context, boolean)` is now the only accessible session execution
entry. Its first operation calls a private unconditional rejection method that
throws `SecurityException("research_execution_disabled")`. Only after that call
would it construct a Session and invoke the preserved body. Both the constructor
and instance `run(boolean)` are private. Thus denial precedes the instance Binder,
epoch, reservation marker, research resource allocation, worker binding, delegated
calls, INIT, RUN, LAUNCH and worker-death experiment. Static class initialization
only constructs the existing Java reservation guard; it does not reserve.

There is no Boolean enable field, build-variant exception, environment/CLI input,
intent extra, preference, deep link or alternate UI callback to reopen execution.
The rule applies to debug and release from the same main source. The launcher is
information-only: both launch actions, executor, Stop and empty report-copy
controls are removed. Its status explicitly says experimental execution,
including death tests, is disabled and retains physical STOP.

Future execution requires a **separately reviewed, owner-approved code change
after readiness requirements are satisfied**. This change provides no enable
mechanism or approval credential. Repeated requests, a new Activity or process,
fresh app data and reinstalls cannot change an unconditional code rule; actual
Android lifecycle observations remain Unknown.

This is an operational accident-prevention lock in trusted management. It is
**not** an authenticated authorization system, hostile-worker boundary, defense
against modified/debugger-controlled code, complete lifetime authority, or proof
of physical Android security. Historical installed APKs are not retroactively
changed by a source PR.

The reservation implementation, filesystem fixtures, real symlink tests,
NOFOLLOW_LINKS mutation runner, protocol/report tests, worker, JNI/native policy,
manifest, dependency/signing configuration and prior research evidence are
unchanged. Existing source assertions for reservation order, irreversibility and
cleanup remain. UI/caller expectations are updated for the intentionally removed
launch route, and strengthened with denial/private-entry checks and mutations.
The foundation allowlist admits only the two new test source paths. Android CI
adds one mandatory desktop lock-control step; existing steps and triggers remain.

The original development instrumentation retains every probe/lifecycle assertion;
only its call uses the new static entry. If invoked now it would report failure
at denial before those assertions. It was **compiled, not run**, and is not
represented as a passing lock test. Its original probe assertions must be revisited
under a separately approved future execution change, never bypassed here.

## Preflight and preservation

Live main matched the base SHA above. Both connector and CLI inventories returned
**zero open PRs**: no open heads/bases, diffs, files, modes, checks, jobs, logs,
reviews, comments or threads existed to audit. Relevant history includes the
one-way reservation (#49), owner procedure (#53), residual admission (#54), and
symlink correction (#55). Merged #55 head was
`a3169ff2989afdd3226e48d11e7479a25f128da1`, base
`1a49bc2f495cee543d505b6d2ae8846ef467a1a6`; reviews/comments/threads were empty.

Main [Android run 41914859020](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41914859020)
and [foundation run 41914858871](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41914858871)
were successful. Job/step records and logs were inspected, including all 15 real
Linux symlink cases, the precise no-follow mutant rejection, Linux controls and
packaged checks. These are **base results**, not candidate CI evidence.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported operational
components and no incidents at preflight. Local sandbox network failure was not
classified as a GitHub incident.

Requirements, ADRs, security boundaries, readiness/incident records, source/tool
adoption, dependencies, workflows and artifact rules were reviewed. ADR-0001 is
Accepted; ADR-0002/0003 retain their recorded proposed dispositions, with only
ADR-0003 Option A approved. No lifecycle/platform survey is reopened.

Initial checkout: clean main, one registered worktree, no stashes; no applicable
AGENTS.md found. Work uses a new `codex/research-execution-lock` branch. Existing
branches, ignored outputs and private evidence remain. New build/inspection data
uses a separate ignored directory and source copy. The 23 current application,
instrumentation, manifest/resource and Gradle/configuration input files were
byte-compared to that build copy. No prior APK was overwritten. Independent backup
of private evidence is not newly attested.

## Validation methods and actual results

Host tools: Windows, Python 3.12.14, existing Temurin 17.0.20.1+1, Gradle 9.6.0
(archive SHA-256 verified against the repository pin), AGP 9.4.0, SDK API 37,
build-tools 36.0.0, NDK 28.2.13676358 and CMake 3.22.1. No dependency or verification
pin changed. Commands below use the existing JDK/SDK paths through environment
variables; machine-specific paths and raw logs remain private.

| Check actually performed | Observation and limit |
|---|---|
| Foundation/source manifest validators | Passed; text/modes/links/requirements and declared authority checks only. |
| `test-repository-validation.py` | 152 tests: 148 executed successfully, four existing platform skips on Windows (Linux C, destination/ancestor symlinks, POSIX modes/types). No skip policy added or changed; not a complete Linux run. |
| `test-execution-lock.py --android-jar <SDK>/platforms/android-37.0/android.jar` | Actual Session compiled against SDK stubs. Three fresh JVMs each denied 100 ordinary and 100 death calls: 600 total. Private constructor/body checked; read-only inspection confirms actual reservation guard remains unconsumed. No fixture file created. |
| Lock negative controls | Three disposable source copies: remove denial, deny ordinary mode only, deny death mode only. Each compiles, then fails the test at the SDK Binder-constructor tripwire with the required AssertionError and `RuntimeException: Stub!` cause. Successful exit, compilation failure, timeout or unrelated error is not accepted. Production sources remain byte-identical after testing. |
| Source entry/lifecycle controls | Launcher has no Session/worker/native/button/executor callback, including no new-intent path. Sole construction is behind the static denial; sole bind remains in private retained body. Mutations removing denial, exposing constructor/body or adding a launcher call are rejected. This is source evidence, not Activity recreation on Android. |
| Debug/release/instrumentation APK assembly; `lintDebug`, `lintRelease` | All completed; both lint reports say no issues. Full Gradle invocation used `--continue` and **failed overall**, preserving the JVM failure below. |
| Existing `protocolTest` and no-follow mutation runner | **Failed locally**: 217 reservation assertions pass, then real `Files.createSymbolicLink` throws Windows missing-privilege `FileSystemException`. The 15 symlink cases and subsequent 71 protocol/report assertions do not complete here; mutation runner refuses this baseline failure. No skip, weakened assertion, elevated symlink privilege or modified test is used. Base Linux results remain separate. |
| Desktop readiness / offline-image / frame-copy suites | 28 / 45 / 4 tests passed. Synthetic fixtures do not establish a physical result. |
| Both APK packaged authority/native/extraction validators | Passed for the exact new APK bytes below, including release non-debuggable and the existing three-entry native inventory. |
| Packaged-policy mutation suite | All five tests passed in the full committed-source rerun, including genuine compiled policy/reference/payload mutations and journal completion/failure. Initial full run passed four tests and correctly rejected the dirty source in the journal test; no validator bypass was used. |
| Compiled debug/release DEX inspection | APK analyzer disassembly shows the first entry instruction invokes unconditional rejection before `new Session`; rejection throws, constructor and body remain private. Both Activities contain only constructor/onCreate, with no Session/worker/native/button callback reference. Static inspection only. |
| Dormant ARM64 bootstrap cross-build/inspection | Passed 10,280 BPF vectors and five semantic mutants, no ELF constructors/entry, exact imports/exports and existing hardening checks. Android output not loaded or executed. |
| Native Windows research controls and Linux process suites on this host | **Not run** under the explicit execution prohibition and host constraints. Unchanged Linux CI remains applicable; no VM/emulator substitute used. |

Initial offline Gradle resolution failed for an uncached pinned plugin marker;
normal verified dependency resolution then built the APKs. Initial sandboxed
desktop fixture creation stalled in `tempfile.mkdtemp` (bounded diagnostic and
interruption retained); unchanged suites passed outside that sandbox. These
infrastructure attempts are not recast as passing runs.

The complete packaged suite passed against implementation commit
`40d14f45a2532aefe9d7da2be4526631e90f8c38`; the final follow-up only records that
observation in this evidence file. A preliminary packaged invocation interrupted
before completion supplies no result. Malformed-resource diagnostics in the
completed suite are expected negative-control observations, not ignored failures.

Exact inspected debug APK SHA-256:
`2051e4cc82bc8d83439f9a22df6243b0ef1c3057566bbd9fd2fb39f29d42c021`.
Exact inspected release APK SHA-256:
`cfdd23b599d65e8d6411c1c7b377f4984cf68d75d8f855e89d5bf91bbba5ceb0`.
Hashes identify these local artifacts only. No APK is committed, uploaded,
installed or qualified for physical use; no whole-APK reproducibility assertion.

## Limitations and publication boundary

Android installation, launcher rendering, real Activity recreation/process
restart, platform Binder behavior, isolated-worker execution, native launch,
worker death, physical durability and containment are **Unknown / not run**.
JVM process restart is not Android restart. The deny-before-side-effects claim
rests on actual JVM entry tests plus source and both-variant DEX control flow;
it is not a device observation or independent no-survivor certificate.

The [physical readiness prerequisites](gate-0-first-physical-test-procedure.md)
remain unsatisfied: independent enrollment/freshness/observation/closure,
source/build/signing qualification, incident disposition and evidence retention.
The [Malwarebytes investigation](gate-0-native-host-antivirus.md) remains deferred
and unresolved; no antivirus configuration was changed.

All new code is original PDVA work using existing standard-library/SDK tools;
no imported upstream implementation, license grant, new dependency, privilege,
host lifecycle authority, VM design, network or Google component is introduced.
Final review covers the full base diff and new files, regular 100644 modes,
whitespace, links and public-data hygiene. No private paths, credentials, keys,
raw incident evidence or binaries belong in this PR.

Publish exactly one focused evidence PR, attach it natively to the requesting
chat, check association once, then stop without polling candidate CI, reviews,
comments, bots or mergeability. Candidate hosted results are **unobserved at
publication**. The final chat reports the actual association outcome; failed
association requires repair of this same PR, not another PR or a false VERIFIED.
