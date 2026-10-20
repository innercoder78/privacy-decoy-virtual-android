# Gate 0: dormant Android seccomp bootstrap preparation

Review: **2026-10-20, America/Fortaleza**, local Windows x86_64. **READY FOR OWNER
REVIEW** as dormant, non-integrated source/build preparation. **NOT READY for
Android activation**: the independently observed isolated identity, platform load
closure, runtime-thread observation adapter and durable one-shot management
protocol below still need review and implementation. Android enforcement is
**Unknown / not run**. Gate 0 **Unresolved**; Gates A–G **Not reached**;
ADR-0001 **Accepted**, ADR-0002 **Proposed**. No production JNI/VM architecture is
selected. Scope: PDVA-REQ-002–003, 009–015, 036–045 and 054, unchanged.

## New preparation and falsifier

The [original C fixture](../../android/research/seccomp-bootstrap/bootstrap.c)
builds as an AArch64 shared library with one explicit C entry, intended for a
future reviewed JNI adapter. There is no Java adapter, executable entry,
JNI_OnLoad, constructor, Gradle target, packaged library or IPC operation. Neither
service creation nor ordinary RUN/LAUNCH invokes it. No arbitrary code, callback,
path, bytecode or payload argument is accepted. The fixed payload only stores 42.

The new experiment asks whether an added filter can change a **marked raw
getpid** from the actual PID to exactly **-1/EACCES** in the caller, a peer alive
before installation and a newly created/joined pthread. It checks the unmarked
raw getpid still returns the original PID. The filter compares native AArch64
audit architecture, syscall 172, and both halves of argument 0's fixed 64-bit
marker `0x5044564150524f42`; other calls are allowed by this additional filter.
An unexpected architecture is killed, not interpreted using AArch64 numbers.
The fixture compile guard rejects other Android ABIs; it is not a compat policy.

Linux's pinned `SYSCALL_DEFINE0(getpid)` returns `task_tgid_vnr(current)` and
does not consume arguments. Bionic's pinned syscall inventory includes getpid;
the inspected app/common blocklists do not remove it. See the existing
[immutable kernel/Bionic ledger](gate-0-worker-containment-sources.md). Raw
`syscall` avoids libc PID caching. The marker does not name a resource or change
kernel state; it selects only this otherwise unused-argument probe. Normal
runtime calls are not intentionally denied. This is a diagnostic assumption
about the exact fixed marker, not a universally reserved syscall namespace.
Any actual baseline mismatch or runtime conflict stops the experiment.

Both caller and preexisting peer must first return the same positive PID with
errno zero. Thus missing/baseline-denied calls cannot masquerade as an added
filter's success. The new thread must return the same unmarked PID, a distinct
TID from the caller, and the exact marked denial. Its TID may legitimately reuse
the joined peer's TID. Every tested thread reads NNP and seccomp mode. Mode 2
alone is not evidence of the new filter: Android may already supply it.

Three mutually exclusive attempts require separate disposable processes:

| Mode | Required future observation | Payload |
|---|---|---|
| 0, TSYNC | NNP set returns 0/readback 1; install returns exactly 0; caller and old peer denied; peer joined; normal new pthread created/joined and denied | Fixed 42 only after all checks |
| 1, omit TSYNC | Caller denied; old peer still returns baseline PID/errno 0; join succeeds; failure 9 | Never entered |
| 2, invalid empty filter | Actual installation rejection, expected -1/EINVAL; no post-filter probe release; old peer cancelled/joined | Never entered |

The raw receipt carries actual install result/errno, attempted flag, pthread
return codes, PID/TID/UID/eUID and per-thread samples. Unattempted operations use
-2 where appropriate; zero-initialized/missing fields are not successes. The
native entry consumes an atomic one-shot flag before validating its mode. A
second call returns NULL, including after failure. This is an internal guard,
not session authentication or durable manager lockout.

## Bootstrap ordering and actual generated load graph

Required future order: Android creates the isolated service → ART/Binder and
platform threads initialize → trusted adapter verifies enrollment/authorization
and loads only this reviewed fixture → baseline peer and native preconditions →
NNP set/readback → exact-zero TSYNC → explicit caller/peer observations → normal
new pthread and join → fixed research payload. Asynchronous ART/Binder threads
can exist throughout; neither a count nor one JNI caller proves all were tested.
Successful TSYNC is source-supported thread-group synchronization, while the
three samples remain scoped empirical coverage. A future adapter must identify
the service main/Binder invocation contexts it tests and account for untested
runtime threads; do not relabel them as directly observed.

**New generated-code finding:** an initial r28c build with `-nostartfiles` still
acquired compiler-runtime `.init_array` entries `init_have_lse_atomics` and
`__init_cpu_features_constructor` through outlined atomics. It imported
getauxval/system-property/string operations and weak memfd_create, and directly
needed libc/libdl. The inspection failed. No version was executed.

The final build uses `-mno-outline-atomics -nostartfiles -nodefaultlibs -lc`.
This selects normal inline AArch64 atomics and excludes implicit CRT/compiler
runtime loading; it is not an executable-memory or security-policy fallback.
Generated ELF checks require: no DT_INIT/DT_FINI or constructor arrays, no ELF
entry, sole export `pdva_bootstrap`, sole DT_NEEDED `libc.so`, and exactly ten
imports: `__errno`, `__stack_chk_fail`, clock_gettime, geteuid, getuid, nanosleep,
prctl, pthread_create, pthread_join and syscall. W^X, non-executable stack,
RELRO, immediate binding and at least 16-KiB load alignment are checked in bytes.
No libdl call, guest library or deferred dynamic load is present in the fixture.

This closes the **fixture's generated pre-filter graph** to its original C,
inline compiler output and platform libc. It does not identify an OEM's entire
already-loaded ART/Binder/libc/linker closure. Those existing platform components
are trusted preconditions, not automatically certified by this ELF check. Before
activation, identify their exact installed binaries, transitive dependencies,
constructors, loader namespaces and any instrumentation/interposition. NDK libc
is a link stub, not the installed libc. No complete physical load graph is claimed.

Pinned Bionic [linker_soinfo.cpp](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/linker/linker_soinfo.cpp)
SHA-256 `058687d0755c6d16439b69b8e83481c955e085709d72952c075fc91d6f5a4ba2`
shows dependencies' constructors before the object's DT_INIT/DT_INIT_ARRAY.
It was fetched as base64 Gitiles text and decoded; web-view retrieval initially
failed. File header is Bionic BSD; reference only, no implementation imported.
Existing kernel reference is GPL-2.0, likewise not copied. No inference about
an installed OEM image follows from these source snapshots.

**Ordering blocker:** if an untrusted library/dependency/constructor or asynchronous
callback can execute before successful restriction, stop that ordering. A late
JNI_OnLoad cannot repair it. The fixed store-42 payload is trusted and compiled
in; it does not justify loading an arbitrary VM library before restriction.

## Integration, observation and child-process safety gates

Existing `Session.run(false)` performs RUN then LAUNCH; LAUNCH uses fork/exec.
The existing instrumentation repeats that session. Reusing it would violate
this first experiment's no-child rule. A separate operation would also need
durable uncertainty before binding/dispatch, authenticated live enrollment,
bounded reporting and a reviewed restart/termination protocol. The current
`uncertain_child` marker is written before LAUNCH, not before this hypothetical
diagnostic. Consequently this change leaves Session, WorkerService, Protocol,
manifest, instrumentation, launch output and cleanup behavior untouched.

The ordinary different-UID manager has no established independently enforceable
identity/stop/accounting procedure for an unexpectedly successful process probe.
Worker PID reports, numeric PID signaling, cooperation, parent exit/direct reap,
Binder death, FD closure and timeouts do not fill that gap. **Defer the entire
clone/clone3/fork/vfork process-probe class.** None is introduced or armed here.
Normal pthread creation internally uses Bionic's reviewed thread clone path;
that is the explicitly requested thread operation, not a fork-like probe.

The first physical experiment may validate installation and this harmless syscall
without attempting child creation. It cannot claim process-creation prevention,
termination of existing processes, FD/mapping revocation, copied-data erasure,
Binder authorization, network isolation, QEMU compatibility or whole containment.

Native receipts are trusted-fixture diagnostics, never independent attestation
against a compromised worker. A future reviewed observer must correlate actual
source/APK identity, framework isolated predicate, kernel-authenticated IPC caller
identity and authorized epoch, observe the actual before/after calls and controls,
and reject missing or inconsistent data. UID inequality and self-reported PASS
are insufficient. No independent Android observer is implemented by this change.

| Failure | Trusted observation and required disposition |
|---|---|
| NNP denied/readback wrong | Fixture records set/error/readback; failure 5; no install/payload. Adapter reports failure only if complete authenticated receipt exists. |
| Invalid filter | Exact raw result/errno; failure 6, peer cancellation; independently require expected EINVAL for this negative control, not arbitrary crash. |
| TSYNC positive TID | Preserve positive result; exact-zero guard fails; no payload. TID is failure detail, not a kill target. |
| TSYNC negative error | Preserve result/errno; fail terminally; no retry or payload. |
| Incompatible preexisting ancestry | May produce positive TID/error; same terminal contract. Runtime cause cannot be inferred solely from a numeric receipt. |
| Unexpected marked success or wrong errno | Failure 9/13; fixed payload blocked; omission control requires exact peer baseline, not merely any failure 9. |
| Pthread creation/join failure | Record returned pthread error, not errno; failures 3/8/11/13; no payload. |
| Peer handshake/deadline failure | Failures 4/7/12; cleanup Unknown. Static thread scratch survives return; no unload or reuse. No timeout certifies join. |
| Partial/lost result | Manager/observer records Unknown; no accepted success and no automatic repetition. |
| Worker death | Lost observations remain Unknown; Binder death is not tree/resource closure. |
| Manager death | Durable pre-dispatch marker must survive restart; no receipt implies no clearance. Adapter absent: activation blocked. |
| Duplicate/stale/replayed request | Native duplicate returns NULL; future adapter must enforce authenticated one-shot epoch before native dispatch, including invalid modes. |
| Interrupted cleanup/uncertain restart | Preserve existing lockouts and add separately reviewed diagnostic uncertainty; never erase state, clear app data or repeat to obtain a result. |

Wait loops have a monotonic deadline plus iteration ceiling; joins happen only
after thread-completion publication. pthread_join itself has no enforced deadline,
and scheduling/platform failure can still prevent return. This is a physical
observation/cleanup prerequisite, not a guarantee of bounded whole-worker death.
No sensitive resources are delegated by this fixture. Future activation must
define external observation and durable lockout even for this fixed trusted code.

## Reproduction and validation

Use existing Python 3.11+ and NDK r28c; no package installation:

```text
python .github/scripts/android-seccomp-bootstrap.py --ndk <existing-NDK-28.2.13676358>
python .github/scripts/android-seccomp-bootstrap.py --model
```

First command cross-compiles, inspects the actual ELF and interprets the actual
88-byte cBPF section. An independent numeric specification covers 10,280 vectors:
four audit architectures, 514 syscall values and five argument values. Five byte
mutations weaken syscall/argument selection, errno or architecture and must fail.
This is compiled-byte/model evidence, **not kernel execution**. Temporary output
is removed, never loaded or uploaded. The static ordinary-harness reachability
and raw-syscall inventory checks run separately before compilation.

Second command requires Linux and compiles the actual C fixture with a separate
[fault driver](../../android/research/seccomp-bootstrap/model-test.c). Real host
pthreads run; **all prctl/seccomp behavior is modeled**. Nine cases cover TSYNC,
omission, invalid filter, positive TID, negative install, NNP denial, both thread
creation failures and inherited baseline denial. Two compiled continuation
mutants must emit the exact rejection and exit 42. In those models, probes
deliberately look restricted despite a failed install, exposing reliance on late
probe checks instead of the installation guard. No old Linux seccomp experiment
is repeated or extended. Existing CI regression steps remain unchanged.

Local results: AArch64 cross-build/ELF/BPF checks passed; model driver passed NDK
C11 warning-as-error syntax checking only. Linux model execution **not run locally**;
Windows guard rejects it rather than reporting a skip/pass. Foundation/harness
validators passed. Repository regression: **141 tests, 137 passed, four existing
platform skips**. Offline Android debug/release/instrumentation build tasks,
68 JVM protocol checks and lint completed successfully: 17 tasks executed,
115 up-to-date. This is an incremental build, not a clean rebuild or instrumented
Android execution. Initial sandbox Gradle native-library initialization failed;
the authorized offline retry completed. Existing AGP deprecation warnings remain.

Original PDVA C/Python only, no new dependency, binary, permission, proprietary
component, guest, source pin or license adoption. Existing NDK/tool licenses in
the [adoption record](gate-0-isolated-worker-adoption.md) apply; owner maintains
this research source. Maven verification metadata remains unchanged. CI adds
required model execution to foundation and NDK-byte inspection to the existing
Android job; exact checkout, read-only permissions, pins and all prior checks
are preserved. No optional failure, passing skip, download or artifact upload.
Generated Windows PE code, ADB, emulator, phone and Android native execution:
**not performed**. Historical Privacy-Decoy remains read only.

Release/debug APK authority and exact native inventories passed separate
inspection: only the existing two JNI ABI libraries and ARM64 launch executable,
with no bootstrap library. Release APK SHA-256:
`1445ddf0d06bbd0ca49ceac64c25fd386c55ed84401ff5a66f067d6c13477354`;
debug: `1236e0ca1cba0c6f915e5831da9ebb7d6d1f570a1f2aca9890aab6864e96f442`.
Lint reports no issues. Final foundation inventory: 112 files, 65 Markdown files,
54 requirements and two ADRs. NDK compiler SHA-256:
`7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579`.
The runner prints exact C source, compiler and generated ELF hashes on every
cross-build; emitted bytes are platform-toolchain evidence, not device identity.
Final local C source SHA-256:
`9254d5707b90c09603fb4f46768c311b124c40c7bd9d5ee1890cc31cdeea087b`;
generated ELF SHA-256:
`a3477715ef3bc9d1232ba0702695e0b1a0ee1256029c1c6d9e1a95fa48048dd7`.

## Live baseline and publication boundary

Canonical main independently resolved to `19a7a56838e118c7756119cbd8e42077b3907727`.
Open PR list was empty. PR #26: head `e7ac22fd1b949d6068a89da8a0e088dcf50aa340`,
base `1cdd679df2806ccd171ddd83697a9da4f4468598`, merge equal to main. Three changed
documentation files; empty reviews, conversation/inline comments and review
threads, with no further thread page. Main/head foundation runs
[39341745546](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39341745546)
and [39341297372](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39341297372)
executed real steps successfully: 141 repository tests, seven native wait cases,
assertion negative, four lifetime cases/mutations, four existing seccomp cases,
and ten revocation cases/mutations. The old seccomp log includes exact-zero TSYNC,
omission, invalid-install and positive-TID receipts with independent cleanup.
Those are existing Linux results; no new Android evidence is inherited.

No exact-main/head Android or QEMU workflow run was returned for this docs-only
change; path-filter absence is not success. All three workflows active; combined
statuses have zero contexts (aggregate pending is not an additional check).
GitHub Status reported All Systems Operational, update `2026-10-20T15:29:34.643Z`.
Starting main was clean, one worktree, no stashes; local/remote branches and
ignored build/reference assets inventoried and preserved. No applicable AGENTS.md
was found. This branch begins at verified main. No reset/clean/force push.

One narrow source PR is justified by the new generated-constructor finding,
constructor-free AArch64 fixture, compiled-byte filter falsifiers and source
failure controls. New hosted CI remains **pending/unobserved at publication**.
After one immediate exact PR identity/head/base and native attachment check,
stop without inspecting checks, Actions, bots, comments, reviews or mergeability.
