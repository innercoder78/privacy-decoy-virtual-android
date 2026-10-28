# Gate 0: native-launch admission and physical-test readiness audit

Review: **2026-10-28, America/Fortaleza; local Windows x86_64.**
**Physical-test readiness: NOT READY — STOP.** No experiment is authorized.
Gate 0 remains **Unresolved**; Gates A–G **Not reached**. ADR-0001 remains
Accepted; ADR-0002 Proposed. Scope: PDVA-REQ-002–003, 008–015, 036, 039–045,
047–048 and 054. This is an evidence audit, not a production-code correction.

The original manager records child uncertainty before its valid LAUNCH request,
but **not before binding or INIT capability transfer**. It clears that marker
from a worker-supplied direct-child result before STOP and worker observation.
The remaining ACTIVE guard is process-local. These are source contradictions
to complete durable attempt enrollment and independent cleanup admission, not
an observed Android escape. Missing independent recovery and the unresolved
security-incident prerequisite separately block the proposed phone procedure.

The [integrated decision](gate-0-integrated-feasibility-decision.md) remains:
R STOP; H unassembled. The fixed native executable is still a separately useful
execution-authority question. Its usefulness does not satisfy admission,
observation, artifact or recovery preconditions. No guest/device-service survey
is reopened, and no new supervisor, broker, privilege or Persona authority is adopted.

## Live preflight and preservation

Before edits, GitHub main and local main agreed on
`4dda568196f10e114d4381984c47a7ad4c9e61b9`, tree
`f493d6df15f55f87459a24f2fc0f669c2794879c`, the merge of PR #44.
The live open-PR collection returned **zero**. Thus all open heads/bases,
complete diffs/files, reviews/comments/threads and checks/jobs/logs comprised an
empty set; no intended audit PR existed to duplicate. Local relevant history and
the two-file PR #44 merge change were inspected. Main application source history
identifies the original harness and native-launch changes; this audit reads the
current-main bytes rather than treating earlier descriptions as implementation.

[Foundation run 40455324528](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40455324528)
has completed successful jobs `122027188679` (foundation) and `122027188413`
(offline-image-windows). Both actual logs identify this exact main. Foundation
records 141 repository tests, 27 journal tests, 45 image tests, four frame tests,
seven native wait cases and the assertion negative control, plus the existing
bootstrap/lifetime/seccomp/revocation controls. Windows records 45 image and
four frame tests. These are existing hosted receipts, not fresh local native or
Android executions. [GitHub Status](https://www.githubstatus.com/api/v2/status.json)
reported All Systems Operational, page update `2026-10-28T05:13:30.151Z`.

Initial checkout: clean tracked state, one registered worktree, no stashes,
137 tracked files, all regular `100644`. Branches and ignored research,
Gradle/CMake, toolchain and artifact directories were inventoried and preserved.
No applicable AGENTS.md was found. Sandbox approval was used for the requested
new Git branch and ignored checkpoint writes; no reset, clean, restore, stash
pop, force push or security-control change occurred. The ignored resumable
checkpoint and desktop witnesses are **locally retained, independently unbacked**.
Prior private incident/recovery evidence backup is not re-attested.

Requirements, architecture, gates, acceptance criteria, security boundaries,
threat model, testing, governance, provenance policy, roadmap and both ADRs were
consulted, together with all twelve task-specified evidence records. Relevant
build/adoption/license and dependency inventories, all workflow definitions,
manifest, original Java/C sources, validators and desktop journal were inspected.
Only this record and the evidence index change. Foundation applies; Android and
QEMU workflow path filters do not select these two Markdown files. Filtered
workflows are not passes. New-PR hosted results remain unobserved at publication.

## Exact source and analysis procedure

Read complete methods and their callers in the files below, then compare local
CRLF-to-LF-normalized bytes with `git show <baseline>:<path>`. All nine matched.
Hashes below are SHA-256 of Git's LF source bytes. Reproduce identities at the
full baseline above; line references below use those bytes, not generated code.

| Source under `android/gate0-harness/src/main/` | SHA-256 |
|---|---|
| [MainActivity.java](../../android/gate0-harness/src/main/java/org/pdva/gate0/MainActivity.java) | `25590a0d64b26db4ddd168a74ab74dad69e1f386e6b837bc7b8923949017ed70` |
| [Session.java](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java) | `78ec8a68f5efb801a006042106603377be6d5bd800718c798a483d8157516cba` |
| [WorkerService.java](../../android/gate0-harness/src/main/java/org/pdva/gate0/WorkerService.java) | `48e52e6861621dda2caa5a5a1d127122559ee9b1efadb10c0c671c26c61bf101` |
| [LaunchResult.java](../../android/gate0-harness/src/main/java/org/pdva/gate0/LaunchResult.java) | `3b6723e111d5f16dbd80ad6e00265ac0ddf5633d0a91a9faf34824f303503f71` |
| [Protocol.java](../../android/gate0-harness/src/main/java/org/pdva/gate0/Protocol.java) | `6daf673f3ed0182e31cfbdbb1ea1425f79157e0b93380d6c7f9bc7c989c19c8d` |
| [launch.c](../../android/gate0-harness/src/main/cpp/launch.c) | `def91eb93e67e3fde07bfb37db9392eefe7f9e92b72c81b87a50661140a6a050` |
| [launch_wait.h](../../android/gate0-harness/src/main/cpp/launch_wait.h) | `ecd9bacd370214fd87fd78c6680a2a3a5b3904b71e02d343fb9cc57a0c2f14be` |
| [launch_payload.c](../../android/gate0-harness/src/main/cpp/launch_payload.c) | `80e9acaf8a14cac4df2d968480ac5dd2548ba21b5fde67ba860456ed0ac98c88` |
| [AndroidManifest.xml](../../android/gate0-harness/src/main/AndroidManifest.xml) | `c9cdc91cb4889ee4c433934145d0c864bea17b0811e89fd1d3567d31e2d9f62c` |

Supporting reads: NativeProbe, Report, probe.c, launch_wire.h, CMakeLists,
build.gradle, build.py, backup rules, ProtocolTest, launch_wait_test,
[validate-harness.py](../../.github/scripts/validate-harness.py) and
[desktop-readiness.py](../../.github/scripts/desktop-readiness.py).
The nine-file comparison does not authenticate an installed application.

For each cut, trace the branch predicates, synchronous calls, callbacks,
exception/finally exits and surviving state. **Source observation** establishes
the actual order; **inference** identifies the consequence under an explicitly
named event; **Unknown** retains unobserved scheduling, persistence and resource
closure. No mock Session or synthetic Android lifecycle was executed.

## Manager, worker and child lifecycle

```text
UI: fresh epoch / five cycles / death-rebind exercise
  -> new Session (fresh UUID; app Context; owner Binder)
  -> read uncertain_child, default false -> true: return lockout report
  -> process-local ACTIVE CAS -> busy: return report
  -> create/truncate synthetic files; open FDs; map frame; allocate native control
  -> bindIsolatedService(BIND_AUTO_CREATE, fresh instance name)
  -> callback stores worker Binder, links death, counts connected
  -> INIT transfers canary RO, scratch RW, frame, owner Binder; number/address only
  -> worker validates/maps resources, links owner death, returns PID/UID
  -> manager rejects own PID/UID; runs fixed protocol controls
     | death exercise: KILL -> finally (no child marker)
     ` normal: RUN -> bounded report/epoch validation
       -> stale-epoch and trailing-data LAUNCH rejection controls
       -> commit uncertain_child=true; false return throws
       -> valid LAUNCH IPC -> worker consumes protocol launch slot
          -> isolated predicate -> native fixed-path fork/exec/wait
          -> direct child result -> worker LaunchResult validation -> reply
       -> manager validates exact 24 longs and no trailing data; append report
       -> cleanupKnown: commit uncertain_child=false (before worker cleanup)
  -> finally: if initialized and not dead, synchronous STOP
  -> wait up to 3 seconds for Binder death; worker_reaped explicitly UNKNOWN
  -> unbind; local checks/free/FD close/unmap
  -> ACTIVE cleared only if (worker absent OR Binder dead) AND marker false
  -> next Session / process restart eligibility
```

**Enrollment witness.** Session lines 78–123 and 196–198 have a successful path
from absent/false marker and ACTIVE=false through resource preparation, bind,
connection and INIT with no persistent attempt write. Worker INIT reads and maps
the delegated objects before registering owner death (lines 60–82). A cut after
successful INIT and before line 196 therefore loses enrollment on manager death.
This is a reachable prefix of the intended successful control flow, conditional
on ordinary API success; it does not require malformed input or a code exploit.
The restarted manager's static ACTIVE is new and the absent/false marker passes
admission. **Overlap with a surviving old worker remains Unknown**, since it also
requires actual old-worker survival through independent framework cleanup.

Before INIT, a bound/starting worker can exist without the marker or owner-death
subscription. A lost INIT reply can leave the worker initialized with capabilities
while manager `initialized` remains false; finally then skips STOP. The lease,
INIT exception cleanup and unbind are useful honest-worker paths, not durable
enrollment or independent observed completion. Resource creation earlier than
bind is local only; it is not itself proof of delegated authority.

**Pre-LAUNCH qualification.** Not every LAUNCH IPC follows line 196: lines 191–194
send a wrong epoch and extra trailing integer. For the original honest worker,
`protocol.check` and `dataAvail` reject these before `protocol.launch` and native
entry; the fixed all-zero epoch cannot equal a generated version-4 UUID. Thus
these probes do not prove an unguarded valid child launch. A compromised worker
need not honor them or any worker-side rule. The manager's `report.bool` records
failed rejection controls but does not globally abort on FAIL, another reason
not to interpret this UI as an independent safety admission controller.

**Child scope.** Only WorkerService's private native entry accepts the framework
installation directory. It selects literal `libpdva_launch.so`, checks bounded
ARM64 ELF/interpreter/file properties, uses fixed argv/environment, then forks.
The child closes inherited descriptors 4–65535, uses CLOEXEC error FD 3,
PDEATHSIG with a parent check, CPU/core limits and an alarm, and execs the fixed
payload. Payload source does not fork; it computes 42 and writes 40 bytes.
The worker uses nonblocking waitpid on its direct child, bounded retries and a
conditional SIGKILL. An ownership-losing wait error does not authorize PID kill.
PDEATHSIG relates to the creating worker thread, not management. These mechanisms
do not independently constrain an arbitrarily compromised worker or descendants.

**Clear witness.** Native CLEAN starts true when no child exists, becomes false
after fork, and becomes true on matching direct-child reap. LaunchResult enforces
shape/ranges and created+CLEAN implies WAIT=1; `cleanupKnown()` is exactly
`v[13] == 1`. It accepts consistent worker-supplied numbers, not a kernel receipt
available to management. Session clears before STOP, Binder wait and unbind.
If worker death is unobserved, ACTIVE stays set in that manager; after manager
death that volatile restriction is lost while the cleared preference remains.
Even observed Binder death permits ACTIVE reset without proving descendant or
external-reference closure. The code correctly labels worker reaping Unknown;
that label is **not included in its subsequent-session admission predicate**.

The worker still owns canary/scratch/frame references after child reap and before
STOP closes them. Fork initially inherits worker mappings/FDs; successful exec
replaces child mappings, not the worker's. Manager close/unmap only drops its own
references. Fixed canary/scratch filenames are truncated by later sessions; no
per-epoch replacement or complete old-holder revocation is implemented. This is
an authority-reuse concern conditional on survival, not an observed stale write.
The [capability audit](gate-0-capability-revocation.md) supplies the resource scope.

## Crash-window and negative-control matrix

All Android event injections below are **NOT RUN**. “Validated” here means
source control-flow validation, except the explicitly identified JVM predicates.
Each unresolved row names evidence needed to reject the unsafe transition;
timeouts, cooperative assertions and missing observations cannot supply it.

| Cut / proposed false inference | Original-code result and reachability | Independent evidence needed |
|---|---|---|
| A: manager dies after bind begins, before marker | Successful bind/start prefix precedes enrollment. No owner Binder subscription until INIT. Restart sees no durable attempt. Old-worker survival/overlap UNKNOWN. | Exact bind/start identity and proof of completion or durable uncertainty covering the request even when callback never arrives. |
| B: dies after INIT, before guard | Valid INIT has transferred/mapped resources; marker still false. Includes lost INIT reply before manager `initialized=true`. Restart admission gap source-confirmed. | Complete attempt/capability enrollment before transfer, and independently justified reconciliation after owner loss. |
| C: dies after true commit, before valid IPC | With intact committed state, new Session blocks even if no child started: conservative false-positive lockout. No code rollback for this window. | Actual persistence/restart evidence; never infer that IPC did not dispatch from missing reply or timing. |
| D: LAUNCH ran; reply lost or malformed | True marker remains on missing reply, wrong long-array size, invalid LaunchResult or trailing Parcel data before clear. Worker may reap independently; manager cannot infer it. | Identity-bound direct-child observation plus worker/resource closure and durable result receipt. JVM malformed-result rejection is narrower. |
| E: direct child completes, worker/FDs/maps remain | Honest success itself reaches child CLEAN before worker STOP. Marker clear is reachable without worker-death observation; same-process ACTIVE may still block. | Scope-complete independent worker and capability closure before reuse, including manager crash after clear. |
| F: internally consistent CLEAN claim | JVM accepts consistent claimed WAIT/CLEAN; malformed created+CLEAN without WAIT is rejected. A malicious worker can supply consistent values. This demonstrates predicate scope, not a forged Binder attack. | Observer independent of worker report, bound to the correct attempt and complete resource scope. |
| G: commit returns true | Explicit synchronous commit precedes valid launch. Full device durability, rollback and restore semantics not independently established. No claim that commit randomly loses ordinary writes. | Exact platform/storage fault contract and interrupted-persistence/restore proof; successful commit is not complete-history freshness. |
| H: process restart with new ACTIVE | Static AtomicBoolean and previousEpoch do not survive process death. True intact marker blocks; missing/false or earlier cleared state does not. | A complete current attempt record, not just a process-local singleton or new UUID. |
| I: stale/missing/corrupt/restored preferences | Missing key defaults false; old false snapshot admits. Wrong-typed value can throw before Session's try block. XML corruption behavior is UNKNOWN here, not assumed false. Restore while an old worker lives is an explicit unproved fault-model condition. | Independent freshness/completeness or proof that the concrete restore path necessarily ends all affected authority first. Backup exclusions alone do not supply it. |
| J: worker outlives owner / system kill only scheduled | Owner-death callback, 30-second Looper lease and onUnbind self-kill reside in worker. Existing framework source establishes independent conditional kill paths, no app-visible complete receipt. | Exact installed-build termination/observation contract, including pending binding, scheduler delays and cleanup errors. |
| K: multi-cycle UI | Loop creates new Session after each return without parsing failure/Unknown. Intact marker blocks each subsequent run; ACTIVE blocks known live endpoint in the same process. Clean child plus Binder death can permit next cycle despite worker_reaped UNKNOWN. Death/rebind action's second cycle is normal RUN+LAUNCH. | Separate one-attempt admission and outcome-dependent continuation protocol; no authorization for either multi-cycle button follows from a one-shot proposal. |
| L: death/unbind/timeout treated as revocation | ACTIVE can reset on Binder death, while source reports no independent reap. Worker-null path can reset after incomplete bind; a late callback/old host remaining is UNKNOWN. Unbind itself is outside a local catch and can abort the rest of finally. | Exact-instance enrollment, callback-race closure and all-reference completion. Worker null, onNullBinding, unbind return or a scheduled kill is not that proof. |

Backgrounding calls `cancel()` and stops future cycles. `request()` checks the
volatile flag before a transaction except STOP; it does not cancel an already
entered synchronous Binder transaction. Cancellation after true commit but before
IPC retains uncertainty. Cancellation earlier leaves no durable child marker.
Activity destruction shuts down the executor without joining or terminating a
worker. Report JSON is memory-only until explicitly copied; manager death can
lose the failure record. Finally's three-second death wait does not bound earlier
synchronous STOP or RUN/LAUNCH calls. `returned=true` records RUN's reply before
JSON validation and is also used for freeing the synthetic control allocation;
it must not be read as completed worker cleanup.

[Android lifetime authority](gate-0-android-lifetime-authority.md),
[lifecycle exceptions](gate-0-android-lifecycle-exceptions.md),
[containment](gate-0-worker-containment.md) and
[diagnostic recovery](gate-0-diagnostic-recovery.md) retain their distinct source
scope. Android system-owned process/cgroup cleanup exists; this audit does **not**
claim all cleanup requires worker cooperation or prove indefinite survival.
Its result is absence of a qualified complete enrollment/observation/recovery
contract in this original harness. No new native observer is implemented.

The public [SharedPreferences API](https://developer.android.com/reference/android/content/SharedPreferences)
specifies a supplied default for a missing boolean and a type exception for a
non-boolean. [Editor.commit](https://developer.android.com/reference/android/content/SharedPreferences.Editor#commit())
is synchronous and reports persistent-write success. Neither API establishes
an independent current-attempt inventory after restoration of old valid state.
Those mutable contracts were consulted on the review date; device fault behavior
remains untested. The desktop journal's fsync/locking/hash-chain controls are
separate: Android Session neither imports nor consults that journal, and the
journal explicitly provides no phone dispatch or cleanup-clear authority.

## New executable desktop falsifier

Compiled the **unchanged original** Protocol.java, Report.java, LaunchResult.java
and ProtocolTest.java with existing Temurin 17.0.20.1+1. The existing suite passed
68 checks. The additional complete witness below passed **eight checks** against
the same original LaunchResult/Report classes. It runs no Android, JNI, Binder,
native child, signal or phone code. It is included here for independent reproduction
without adding a production/test-framework change.

Save as `AdmissionAudit.java` in a new ignored audit directory, compile with
`javac -d <classes> <original-Protocol.java> <original-Report.java>
<original-LaunchResult.java> <original-ProtocolTest.java> <AdmissionAudit.java>`
using the exact baseline sources, then run
`java -cp <classes> org.pdva.gate0.AdmissionAudit`.
No Android stubs or replacement result predicate are used.

```java
package org.pdva.gate0;

public final class AdmissionAudit {
    private static int checks;
    private static void check(boolean value) {
        if (!value) throw new AssertionError("audit " + (checks + 1));
        checks++;
    }
    private static long[] initial() {
        long[] v = new long[24];
        v[10] = v[19] = v[20] = v[23] = -1;
        v[13] = 1;
        return v;
    }
    public static void main(String[] args) {
        long[] v = initial();
        check(new LaunchResult(v).cleanupKnown()); // No child created.
        v[0] = v[1] = v[3] = 1;
        boolean rejected = false;
        try { new LaunchResult(v); }
        catch (IllegalArgumentException expected) { rejected = true; }
        check(rejected); // Created + CLEAN without WAIT must be rejected.
        v[13] = 0; v[12] = 1;
        check(!new LaunchResult(v).cleanupKnown()); // Timeout, no reap.
        LaunchResult retained = new LaunchResult(v);
        v[8] = v[13] = 1;
        check(!retained.cleanupKnown()); // Constructor owns a clone.
        LaunchResult reaped = new LaunchResult(v);
        check(reaped.cleanupKnown()); // Reap and timeout can coexist.
        Report report = new Report("1".repeat(32), 37);
        reaped.append(report);
        String json = report.json();
        check(json.contains("\"probe\":\"launch_timeout\"")
                && json.contains("\"status\":\"FAIL\""));
        v[12] = 0; v[14] = -1;
        check(new LaunchResult(v).cleanupKnown()); // Invalid child output, reaped.
        v[14] = 0;
        check(new LaunchResult(v).cleanupKnown()); // Consistent claimed reap.
        System.out.println("Admission audit checks: " + checks);
    }
}
```

The controls distinguish an invalid typed record (rejected) from validly encoded
invalid child output (can still have a reaped child). They falsify using
cleanupKnown as either “the experiment passed” or an independent worker/tree
certificate. They **do not** demonstrate that a true incomplete-child record is
promoted to clean: that negative stays false, and the constructor clones input.
The timeout case contains the only FAIL row in that constructed report, so its
FAIL check is not satisfied by an unrelated injected failure. No expected-failure
wrapper hides a failing positive check. Actual Android parcel/crash ordering is
source-only, not exercised by this JVM witness.

## Retained artifact, signing and security prerequisites

Read-only inspection of the existing release APK passed the actual packaged
manifest/native validator using installed SDK command tools 22.0. Direct invocation
of desktop-readiness's original `inspect` function also passed source cleanliness
at the baseline, APK identity, exact three stripped-local-native byte mappings,
and before/after APK/analyzer/validator checks. This was offline inspection only;
no phone journal or new build was created. Declared source association is **not**
independent reconstruction of DEX/resources/native outputs from that revision.

| Freshly read retained bytes | SHA-256 |
|---|---|
| Release APK | `1445ddf0d06bbd0ca49ceac64c25fd386c55ed84401ff5a66f067d6c13477354` |
| ARM64 fixed executable | `6c95e1aa9342422e7c70ce8bc63c318408e628bd7eea5507aca3d4081033e789` |
| ARM64 JNI | `71bb7cbb85665f30c6dd92e9b3039ce34d9a04cdb1c0a2a8ebeba10dd4676b35` |
| x86_64 JNI | `8e78104351acc567691562e644af0e3b80ef5b75277db4d742b1fec73c365bea` |
| APK signer certificate | `64089e41f44aad90538bed50865f9c8575d1d568da2ab2b6a24480ca1932d3f7` |

Existing SDK build-tools 36.0.0 `apksigner.jar verify --verbose --print-certs`
exited zero: one signer, v2 true; v1/v3/v3.1/v4 false. Certificate details beyond
the fingerprint are omitted. This verifies this retained APK under that trusted
local tool; it does not authenticate the source build, establish trusted key
custody, prove absence of compromise or make it safe to install. Gradle explicitly
uses `signingConfigs.debug` for non-debuggable release: ordinary development
signing, not platform authority or a production identity. No key was opened,
copied or published, and no new signing operation occurred.

Release construction sets debuggable=false, minSdk 30, target/compile 37, no app
runtime Maven dependencies and compressed/extracted native entries. Manifest has
zero permissions, one exported launcher and one non-exported isolated worker;
no shared UID, app zygote, provider, receiver or foreground/persistent supervisor.
Backup and transfer exclusions include shared preferences; they are not proof
against every loss/restore mechanism. The ordinary-app manifest is a source and
packaged observation, not evidence of ordinary installed execution.

Validator acceptance covers ARM64 dynamic PIE, entry/interpreter
`/system/bin/linker64`, NDK r28c/API-30 notes, RELRO/immediate binding, non-executable
stack, no W+X load, payload stack-canary reference, permitted dependencies and
16-KiB load alignment. Fresh imports are libc/libdl for the executable and
libc/libdl/libm for JNI. No x86_64 executable is packaged; that launch branch is
Unsupported. ELF alignment, compressed installer extraction and actual runtime
page/mapping behavior are separate; neither 4-KiB nor 16-KiB phone compatibility,
installed symbol/namespace closure or host minimum is established.

The [adoption](gate-0-isolated-worker-adoption.md) and
[dependency ledger](gate-0-isolated-worker-dependencies.md) retain 185 Maven
components/322 pinned artifacts, Gradle 9.6.0, AGP 9.4.0, NDK 28.2.13676358 and
CMake 3.22.1. Pins are build-integrity controls, not independent tool rebuilds or
a fresh transitive security/file-license audit. Local tool installations,
extractions, caches, signing environment and generated outputs remain trusted,
not comprehensively attested. No dependency, binary or license grant is added.
Source provenance remains original PDVA research; referenced upstream licenses
do not supply a general repository or product distribution license.

The [antivirus incident](gate-0-native-host-antivirus.md) and
[REC-07 recovery](gate-0-research-recovery.md#rec-07-preserve-the-correction-not-a-renewed-safety-claim)
remain unresolved. Two Windows research EXEs were quarantined; source review and
surviving object observations did not authenticate quarantined bytes or determine
maliciousness versus false positive. Those PE controls are distinct from the APK
and ARM64 ELF. Later successful Linux CI is genuine scoped test evidence, not
vendor clearance, host-compromise exclusion or permission to rebuild/install.
No new private security diagnostics, quarantine content or vendor submission was
accessed; no protection setting was changed. Applicable execution clearance needs
vendor or qualified security disposition and qualified artifact/environment
provenance. Tony must approve any sharing of private incident material separately.

## Prerequisite disposition

SATISFIED applies only to the stated scope. CONTRADICTED rejects a concrete
source claim; BLOCKED is an unmet mandatory condition; UNKNOWN lacks sufficient
evidence; NOT RUN identifies an unexecuted experiment. No row transfers a scoped
pass into readiness.

| Prerequisite | Disposition | Exact scope / remaining condition |
|---|---|---|
| Non-debuggable, ordinary zero-permission package | SATISFIED | Source and retained packaged manifest only; no installation. |
| Fixed ARM64 executable and allowed direct ELF dependencies | SATISFIED | Actual retained bytes passed original validator; no runtime/linker closure. |
| Retained APK cryptographic signature | SATISFIED | One development certificate, v2 verification with existing local tool; key provenance/suitability separately UNKNOWN. |
| Independently established exact source-to-APK/build/signing trust | UNKNOWN | Byte correspondence and declared revision pass; reproducible build and trusted environment/key custody absent. |
| ABI/page-size/installer/linker authority on stock phone | NOT RUN | No physical compatibility or native-launch result. |
| Durable enrollment before binding and capability transfer | CONTRADICTED | Actual Session enrolls only near valid LAUNCH; A/B leave no persistent attempt. |
| Guard before valid native launch; reject malformed typed reply | SATISFIED | Honest source path and JVM checks only, intact persistence assumed; preguard invalid IPC distinguished. |
| cleanupKnown independently certifies worker/tree/resources | CONTRADICTED | Predicate is worker-supplied direct-child CLEAN; clear precedes worker shutdown. |
| Complete uncertainty lockout across manager restart | CONTRADICTED | ACTIVE volatile; absent/false preference admits unrecorded or earlier-cleared attempts. Actual overlap remains UNKNOWN. |
| Persistence freshness, corruption/restore handling | UNKNOWN | No independent freshness/completeness authority; backup exclusions insufficient. |
| Independent exact-attempt worker/descendant/resource observer | BLOCKED | No qualified ordinary-app observer/reconciliation procedure in existing harness. |
| Failure/cancellation evidence durable through manager death | CONTRADICTED | Memory-only reports; cancellation is pre-call cooperative state, not completion. |
| One-shot eligibility and safe repetition | BLOCKED | UI has multi-cycle and death-then-normal-launch paths; guard is not all-failures/whole-resource admission. |
| Security incident execution prerequisite | BLOCKED | No vendor/qualified disposition or independently qualified replacement environment supplied. |
| Sanitized public review | SATISFIED | This text and bounded desktop receipts reviewed; no raw private incident data or binaries. |
| Private backing evidence durability | UNKNOWN | Local checkpoints retained; independent private backup not verified. |
| Physical native launch, crash injection and recovery | NOT RUN | No phone/USB/ADB/install/Android/VM/emulator/guest execution. |

**Overall: NOT READY — STOP.** This is stronger than “we have not tried a phone”:
mandatory admission and observation conditions are demonstrably unmet in the
existing source, with independent security prerequisites still blocked. It is
not a finding of exploitability or product-wide impossibility. An indefinite
lockout would preserve uncertainty, not establish completed revocation. A fresh
token, preferences clear, reinstall, app restart, force-stop or reboot inference
must not be used to replace an unaccounted earlier attempt.

## Validation and smallest next action

Actually executed locally with existing Python 3.11.4 and Temurin 17.0.20.1+1:

| Check | Result / limits |
|---|---|
| `validate-foundation.py`, `validate-harness.py` | PASS; repository/links and source/retained merged-manifest authority. |
| `test-repository-validation.py` | 141 tests: 137 passed, four existing platform skips; skips are not passes. |
| `test-desktop-readiness.py` | 27 passed, no skips; original offline journal/validator controls, not Session. |
| `test-offline-image-inspect.py` | 45 passed, no skips; synthetic fixtures, no guest boot. |
| `test-frame-copy.py` | Four passed, no skips; bounded desktop mapping/copy controls. |
| Original JVM suite / new predicate witness | 68 / eight checks passed; no substituted production logic. |
| Retained release APK validator / original correspondence inspector | PASS; exact hashes above, not fresh build. |
| Existing apksigner verification | PASS, exit zero, v2 true; no safety verdict. |
| Nine source identities / final diff, links, whitespace, modes and privacy | Reviewed; only two documentation files intended; dependencies/source unchanged. |

Sandbox denied Git/build writes and initial javac output. Two sandbox Python
suites stalled at their first temporary-file test and were interrupted; no pass
is attributed to those attempts. Authorized outside-sandbox retries completed
unchanged suites and JVM compilation. No assertion, skip rule or workflow was
weakened. New Gradle APK/lint builds and local native C/process suites are NOT RUN:
no production source changed, no approved native environment/incident clearance
is inferred. Baseline Linux CI was inspected separately. All physical results
and original-code Android crash ordering remain NOT RUN/source-only.

**Single smallest next independent proof:** a separately reviewed, source-level
enrollment/reconciliation contract for this exact bind/INIT/LAUNCH path that
accounts for every attempt before delegated work and remains closed after A/B
and E/H manager-loss cuts. Its falsifier is any reachable post-restart admission
with an earlier issued capability/attempt unaccounted for. It must name a concrete
ordinary-app independent observation/freshness authority and its failure behavior;
merely moving the boolean earlier, adding a UUID/MAC, or rerunning this JVM witness
does not close recovery. No such candidate is supplied or implemented here.

If Tony supplies a concrete candidate, desktop control-flow review can reject
missing enrollment/identity edges before any device request. Without that input,
another synthetic lifecycle model or generic API survey would not establish the
missing authority: **the corresponding physical procedure stays stopped**.
Security disposition and exact artifact/environment qualification remain separate
mandatory owner inputs even if that proof later succeeds. Any material ownership,
supervisor or security redesign needs a reviewed ADR and Tony's explicit approval.
Do not try a phone merely to generate logs. A later authorized successful trusted
one-shot child would still not qualify hostile-worker containment.

Publication scope is exactly one evidence PR, native association and one immediate
identity/association verification, then STOP without CI/review polling. The PR is
pending independent review before merge; it is not canonical merged evidence or
physical authorization. Publication/association failure requires preserving the
same branch/PR and reporting UNPRESERVED pending recovery, never a duplicate PR.
