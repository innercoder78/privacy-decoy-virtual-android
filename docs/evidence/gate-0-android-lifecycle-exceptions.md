# Gate 0: exceptional isolated-worker lifetime and cleanup observation

Review: **2026-10-17–18, America/Fortaleza**. **Source investigation only.**
Gate 0 **Unresolved**; Gates A–G **Not reached**. ADR-0001 **Accepted**;
ADR-0002 **Proposed**. No production VM engine selected. No phone, ADB, QEMU,
emulator, guest, APK installation, Codex Cloud or privileged Android execution.

**Inference — disposition: STOP dependent implementation.** The last-binding
candidate in [PR #19's evidence](gate-0-android-lifetime-authority.md) survives as
a conditional system-owned termination trigger. It does not become a complete
ordinary-app cleanup contract. This continuation finds additional startup and
death paths, limits to predecessor ordering, and a concrete negative witness
against treating public process-exit history as a completion receipt. No reviewed
public mechanism certifies the exact hostile instance's entire descendant tree
and delegated authority. Uncertain cleanup must retain fail-closed lockout across
manager restart; this is a research disposition, not an implemented safeguard.

## Scope, baseline and preflight

**Observation:** live main matched `edc1d4ead49b8f5ac9696e91ceb070925e01e854`.
There were **zero open PRs**, so no open diffs, heads, jobs, reviews or threads
needed reconciliation. [PR #19](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/19)
was merged from `9767b8db871536c2a89d6d90df2457052beeab78`, base
`0af04da8fcaad1c69db5b4f3c6459c8f9d433116`; its head tree equals current main.
Its complete three-file change, reviews, conversation comments, inline comments
and review-thread inventory were inspected; the latter inventories were empty.
Its [foundation job](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39077212476/job/117526748664)
succeeded at that exact head.

**Observation:** exact-main [foundation run 39078326307](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39078326307)
succeeded. Logs identify the exact checkout, 96 files/54 Markdown files,
54 requirements/two ADRs, 138 passing repository tests, harness validation,
seven native wait controls and the injected assertion failure, four real Linux
lifetime cases/four mutations, and four real seccomp cases with independent
cleanup. The runner was Ubuntu 24.04.5, x86_64, Linux `6.17.0-1022-azure`.
These are existing **Linux** results, not Android lifecycle evidence. No Android
build run was returned for this exact main; the documentation-only merge did not
match its path filter. All three workflows were active; checkout pin,
exact-head selection, read-only permissions and path filters were inspected.
Combined status had zero contexts (`pending` is not an extra failing job).
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational, page update `2026-10-17T18:55:09.599Z`.

**Observation:** on resumption on 2026-10-18, main was unchanged and open PRs
were still empty. The three intended documentation changes remained uncommitted;
no publication had occurred. Existing exact-main CI findings above remain scoped
to that verified SHA; no new CI run was requested.

**Observation:** the checkout was clean, with one worktree and no stashes. The
prior branch and ignored assets were preserved; this branch starts at the exact
main above. No applicable AGENTS.md was found. All 96 baseline files were regular
mode `100644`. Requirements, governance, boundaries, gates, evidence criteria,
both ADRs, lifetime/containment/source/seccomp records, isolated-worker harness,
native launch/integration evidence, source catalog and dependency/adoption
records were consulted. Historical Privacy-Decoy remains read only.

This addresses PDVA-REQ-002–003, 009–015, 036–045 and 054 without amending them.
`compileSdk 37`, `targetSdk 37` and research `minSdk 30` remain unchanged;
the supported host minimum remains **Unknown** under PDVA-REQ-044.
The 185-component/322-artifact build ledger remains unchanged, SHA-256
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.
No runtime dependency, binary, permission, policy or production behavior changes.

## Source identities and interpretation

**Observation:** this uses the same Android 17 reference revisions as PR #19:
frameworks/base `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`, system/core
`545d2487e38192a2ce25040897ced877cf6b4f53`, and the existing policy/Bionic/kernel
references in the [immutable ledger](gate-0-worker-containment-sources.md).
Fifty-two retained AOSP ledger files were independently rehashed successfully.
Thirteen files were fetched at full commits for this continuation, including two
already cataloged files; the [eleven additional identities](gate-0-worker-containment-sources.md#exceptional-lifecycle-and-observation-continuation-2026-10-17)
record decoded-byte SHA-256 and license scope. No upstream implementation is
copied into tracked source or executed. These project snapshots are **not** an
OEM build manifest or proof of compiled flags, installed policy or kernel behavior.

Below, **Fact** means behavior in those identified source bytes; **Observation**
means this review's retrieval/repository/check results; **Inference** is a scoped
consequence; **Hypothesis** awaits proof; **Unknown** is missing evidence.
**Unsupported** identifies authority excluded by the ordinary-app contract.
Line ranges refer to decoded source, not generated documentation. Abbreviations:
AS = `ActiveServices.java`, AMS = `ActivityManagerService.java`, PL =
`ProcessList.java`, PR = `ProcessRecord.java`; their full paths and hashes are in
the ledger. `psc/` files are under `services/core/java/com/android/server/am/psc/`.

The stages must remain separate:

| Stage | What is established | What does not follow |
|---|---|---|
| Framework request | Bind/unbind transaction or bookkeeping transition | Worker exited |
| Kill eligibility | Isolated host has no running services/custom entry point and passes trim guards | Trim ran or signal was sent |
| Scheduled/requested kill | PID signal attempted; group work queued | Successful signal, observed death or empty cgroup |
| Observed endpoint/process death | Scoped Binder obituary or appropriate process observation | Every descendant exited |
| Descendant cleanup | Actual identified membership became empty under an enforcing authority | External recipients lost FDs/mappings/data |
| Capability revocation | Each relevant authority rejects further use, with identity/epoch closure | Previously copied information is erased |

## Exceptional call chains A–I

### A. Last binding disappears during process creation or attachment

**Fact:** AS `removeConnectionLocked` (7084–7214) first removes connection
records. On its `!serviceDead` path, no remaining connections and no started
request remove the service from **both** `mPendingServices` and
`mPendingBringups` (7191–7196), before conditional teardown. This closes a gap in
reading only `bringDownServiceIfNeededLocked`'s pending-service early return
(6743–6760). Removing a pending service is not cancellation/join of an already
issued asynchronous zygote start; PL maintains separate `mPendingStarts` and
start-sequence state (2155–2229, 2907–3035).

**Fact:** AS `attachApplicationLocked` (7445–7534) matches the actual
`isolationHostProc`, or the explicit UID/process-name alternative (7418–7426).
A removed pending service is no longer in this iteration. A retained matching
service is started, then rechecked for need and brought down if no longer needed.
Its boolean describes whether it did service work, not cleanup completion.
AMS `finishAttachApplicationInner` (5581–5689) checks PID/start UID/start sequence,
clears pending-finish-attach, dispatches components, and requests a process OOM
update when `didSomething` is false. Thus a dedicated orphan that completes this
attachment path has another system-owned update route. Initialization exceptions
take `killLocked("error during init")` and application cleanup.

**Fact:** trimming explicitly skips `isPendingFinishAttach()` (psc/OomAdjuster
1403–1409). Pre-attachment process-start timeout reaches AMS cleanup and
`killLocked("start timeout")` (5100–5189); AS `processStartTimedOutLocked`
(7536–7564) removes matching pending service state. A different timeout for
finishing application initialization has soft-extension and hard-ANR paths
(AMS 5765–5792), not an app-selected unconditional kill deadline.

**New negative source witness:** PL invalid-start handling (2957–2975) signals
the returned `pid`, but calls group kill only when **`app.getPid() != 0`**, using
that recorded PID. AMS unknown-record attachment (5227–5254) signals the incoming
PID and has only a TODO for group kill. **Inference:** not every exceptional
attachment branch contains the normal complete group-cleanup request. **Unknown:**
reachability with a descendant-bearing worker, recovery by other paths and an
actual surviving descendant on a stock build. This is not a demonstrated Android
escape or leak; it falsifies deriving universal tree cleanup from the normal path.

### B. Manager crashes while a worker runs

**Fact:** AMS `appDiedLocked` (4036–4129) validates current record, PID and Binder
thread. For the ordinary non-instrumented death path, `doOomAdj` is true:
`forEachConnectionHost` enqueues bound hosts **before** application cleanup, then
pending OOM work runs afterward. PR `forEachConnectionHost` (1894–1912) traverses
actual service/sandbox/provider connection hosts. AMS `handleAppDiedLocked` →
`cleanUpApplicationRecordLocked` → AS `killServicesLocked` (7797–8025) removes
the dead client's connections with `skipApp=app`, then runs pending updates or
closes the outer service batch. Worker cooperation is not involved in these steps.

**Inference:** this strengthens the manager-death trigger beyond PR #19's
connection-removal observation. It is not identical to explicit unbind: there
is no `unbindServiceConnectionsLocked` post-removal enqueue for each connection.
The pre-enqueued host may be processed by an intervening legacy update; section F
explains why enqueue ordering matters. Other live auto-create clients or started
need preserve the service. Instrumentation and stale-death branches have separate
guards. No manager-death callback carries the native cleanup result to a future
manager, and no independent manager-selected completion deadline is established.

### C. Worker suppresses callbacks or blocks native threads

**Fact:** removal of running-service bookkeeping precedes the one-way
`scheduleStopService`; executing callbacks are tracked separately. The existing
isolated-not-needed predicate does not require destruction acknowledgement.
Blocking a callback therefore does not itself veto that predicate once the
process reaches the eligible attached state. **Inference:** this part of PR #19's
candidate survives. It does not cover the pending-finish-attach exclusion, kill
queue delays, uninterruptible kernel work or group-cleanup failure. ANR dispatch
does not establish guaranteed termination. Worker CLEAN, self-reported PID,
`onDestroy` completion or worker-side owner-death handling cannot certify cleanup.

### D. Connection removal encounters an exception or Binder failure

**Fact:** ContextImpl 2374–2389 forgets the client dispatcher before AMS unbind;
the public void API discards AMS's boolean. A remote exception is rethrown after
that local removal. The manager cannot infer whether server-side removal happened
from a failed reply, and cannot assume its old dispatcher still monitors death.
AS `unbindServiceLocked` returns false when no connection record exists, not a
positive death receipt (4765–4807).

**Fact:** AS catches exceptions from `scheduleUnbindService` (7185–7187),
bring-down unbind (6830–6832), and `scheduleStopService` (6993–6996), calling
`serviceProcessGoneLocked`. That helper calls `serviceDoneExecutingLocked` with
finishing=true (7334–7413). **Its name is not an observation of OS process death.**
It decrements `executeNesting`; only when the count reaches zero does the shown
path clear execution state, enqueue/run the process update, remove a nonpersistent
running service and clear the process reference. With remaining nesting, those
actions are not all performed immediately. Client disconnect notification
exceptions are caught separately and teardown continues (AS 6796–6802).

**Inference:** an exception can change which record/reference is available to
the later OOM enqueue. It neither proves liveness nor death; it does not create
a cleanup result. Repeating unbind after forgetting a dispatcher is not an
identity-safe proof of recovery. Preserve uncertainty.

### E. Multiple bindings or isolated-service instances

**Fact:** AS 5130–5144 derives a named instance's lookup component from the
explicit component plus instance name. Reusing that name can retrieve an existing
ServiceRecord. Removing one ConnectionRecord leaves other auto-create bindings;
ServiceRecord 1978–2003 retains need for started state or any auto-create connection.
The trim predicate counts **all running services in the host**, not just the
service whose connection was removed. Shared/package-isolated binding modes are
distinct paths (AS 4302–4317, 6280–6378); PR #19's dedicated-host assumption cannot
be silently applied to them.

**Inference:** retain separate connection, service-record and process-incarnation
identities. Neither a component name nor a package UID identifies a closed
descendant set. A fresh random instance name avoids accidental lookup reuse; it
does not prove older instances cleaned up. A remaining binding is a direct
falsifier of “one unbind kills the service.”

### F. OOM updates deferred, skipped or superseded

**Fact:** psc/ProcessStateController 240–340 routes update requests into an active
batch. BatchSession 52–88 closes only at the outermost depth; SyncBatchSession
70–85 rejects null/skipped records, and 166–191 runs only requested work.
Try-with-resources closes on ordinary exception unwinding; it is not protection
against system_server death. OomAdjuster 1107–1133 handles a pending full update
first, returns on an empty target set, defers during an ongoing update and revisits
pending work in `finally`. A full update superseding individual targets is not
itself lost work. The trim iterates the LRU list, including eligible isolated
records beyond the targets computed in that pass (1347–1491).

**Fact:** ServiceRecord `wasOomAdjUpdated` compares the host adjustment sequence
with a saved sequence (1951–1958); it is not a cleanup bit. AS
`bumpServiceExecutingLocked` can run a legacy update before sending a callback
(5578–5593). Bring-down samples/updates `oomAdjusted`, removes the running service
later, and only enqueues at its tail when `!oomAdjusted` (6806, 6960, 6990,
7010–7020). `removeRunningService` itself is just bookkeeping
(psc/ProcessStateController 1017–1019).

**Inference — limited counterexample condition:** with batching disabled, if an
earlier callback-related update consumed the targets while the service was still
running, and later `wasOomAdjUpdated` suppresses another request, the mere call to
“run pending updates” can be a no-op. Explicit normal unbind's post-removal enqueue
closes that hole when its host reference survives; manager death and exception
callers must be traced separately. This identifies a missing implication, **not**
an observed indefinite leak or proof that no other update runs. Exact scheduling,
flag selection, nesting, state and later triggers remain necessary qualifications.

### G. One worker dies while another starts

**Fact:** AMS rejects stale process-death identity before cleaning the current
record (4036–4059); AS checks the current instance-map ServiceRecord before restart
decisions (7924–7934). PL validates pending-start state, record identity and start
sequence (2907–2975). These checks protect bookkeeping identity; they are not a
join on prior cgroup cleanup.

**New Fact:** PL's ordinary dying-process predecessor mechanism explicitly
excludes isolated processes: isolated start sets `app=null` (2799–2802), the
dying-map lookup is under `!isolated` (2843–2846), and `noteAppKill` puts only
non-isolated processes into that map (5864–5869). `handlePrecedingAppDiedLocked`
(5711–5735) can release a successor when applicable, but cannot be promoted into
an isolated-worker tree-empty barrier. **Inference:** a new isolated instance
can have independent startup state while the old group's cleanup is queued or
uncertain. Live auto-create bindings can also lead AS to schedule service restart
(7935–7970). New connection/UID/PID success is not evidence about the old tree.

### H. Primary kill or cgroup cleanup fails

**Fact:** PR 1394–1413 calls `noteAppKill`, signals the primary PID and schedules
group cleanup, then marks killed state. JNI `sendSignalQuiet` (1120–1124) ignores
the `kill()` return. PL KillHandler (799–810) ignores the boolean returned by
hidden `Process.killProcessGroup`; this branch neither delivers that result to
an app nor retries based on false. AMS `appDiedLocked` skips its group request
when the record is already marked killed (4066–4077). These are bookkeeping and
request facts, not proof of successful signal delivery or complete retry coverage.

**Fact:** system/core `KillProcessGroup` (567–681) can return -EINVAL, fail
signaling, fail opening `cgroup.events`, encounter population-read/poll/removal
errors or reach its attempt deadline. It returns the removal result on the
applicable path. With no cgroups, successful signaling can return zero without
population observation. Its native deadline is not an unbind-to-exit bound.
**Inference:** neither marked-killed state, a queued message, a kill-history reason
nor a successful request establishes descendant cleanup. Unknown recovery paths
and OEM behavior cannot be filled in with an assumed retry guarantee.

### I. Manager restarts while previous cleanup remains uncertain

**Fact/Inference:** a new manager has no old ServiceDispatcher registration or
death subscription, and no public result in the reviewed chains joins old group
cleanup. A reconstructed PID/UID/name is not the old Binder object or framework
start sequence. New binding may recreate/retrieve a service and does not inspect
old cgroup completion. The predecessor mechanism in G does not solve this.
Therefore restarting management cannot transition uncertainty to verified cleanup.

## Ordinary-app observation candidates and falsifiers

**Observation:** reviewed the pinned public SDK signatures (`core/api/current.txt`),
public class contracts, their AMS implementations and the documented
[ServiceConnection](https://developer.android.com/reference/android/content/ServiceConnection),
[Binder death recipient](https://developer.android.com/reference/android/os/IBinder.DeathRecipient),
[ActivityManager](https://developer.android.com/reference/android/app/ActivityManager) and
[Process](https://developer.android.com/reference/android/os/Process) references.
The web pages are mutable supplementary contracts; immutable source carries the
implementation findings. This is a bounded candidate search, not a proof that
every Android subsystem has been exhaustively searched.

Every row below is a **Fact/Inference** assessment. No row certifies transferred
capabilities. A timeout, denial, exception or missing record never means success.

| Candidate; authority | Identity, observation and cooperation | Falsifier, restart/failure meaning and descendant limit |
|---|---|---|
| `ServiceConnection.onServiceDisconnected`; public | Connection/component; framework dispatch for lost service endpoint, no CLEAN needed | Binding remains active and can reconnect. Normal unbind removes the dispatcher monitor. A live descendant with a dead endpoint falsifies tree completion; absent callback is inconclusive. |
| `onBindingDied`; public | Binding no longer usable; not a process-incarnation receipt | AS can notify clients before stop/kill. Death of the binding does not mean death of host/tree. Must still unbind; restart gives a new connection, not old cleanup evidence. |
| `onNullBinding`; public | Worker returned null from onBind; depends on worker return | A live null-returning service is the falsifier. Unusable interface is not a dead process; binding still needs release. |
| `IBinder.linkToDeath`, `isBinderAlive`, `pingBinder`; public | Exact retained remote Binder endpoint. Death notification itself is independent of worker CLEAN, but trusting a worker-returned arbitrary endpoint as its own process identity is an additional problem | Remote endpoint death is not a census of descendants. Manager crash loses subscription; fresh Binder or stale callback must not clear a different epoch. Transaction failure/timeout is not whole-tree death. An independently registered recipient may survive unbind; that still does not enlarge scope. |
| `getHistoricalProcessExitReasons` / `ApplicationExitInfo`; public API 30 | System diagnostic history scoped by package/caller UID and optional numeric PID. Isolated UIDs can map to the package UID; not categorically inaccessible. No cooperative CLEAN needed | Kill-decision records, bounded retention, asynchronous loading, PID/UID reuse and no start-sequence/tree handle defeat a completion certificate. Empty history is inconclusive; details below. |
| `getRunningAppProcesses`; public | Framework LRU snapshot, restricted by caller UID unless special task authority; not a kernel census | PL 4411–4462 filters actual `app.uid`, null thread, crashing/ANR state. A running isolated UID can be absent from ordinary manager results. Absence is not death; same package does not defeat UID filtering. |
| `getRunningServices`; public but deprecated diagnostic interface | Own-service bookkeeping, with PID if attached; not all native processes | Bring-down removes service lookup before process/group cleanup. Empty list or absent service cannot certify host or descendants. Multiple bindings/instances make name-only correlation weaker. |
| Startup history / `addApplicationStartInfoCompletionListener`; public | Startup diagnostics/completion of the caller's application-start information | A new successful startup while an old group remains uncertain falsifies its use as a cleanup result. No teardown result is documented. |
| `IProcessObserver.onProcessDied`; hidden, signature-gated | Framework PID/UID process notification; AMS requires `SET_ACTIVITY_WATCHER` | Unsupported ordinary-app authority. Even privileged notification is process bookkeeping, not returned native group-cleanup status. A surviving descendant falsifies the stronger claim. |
| `IUidObserver`, `OnUidImportanceListener`, `IMPORTANCE_GONE`; hidden/SystemApi | Framework UID state; UID registration checks usage-stats authority | Usage-access consent does not turn a hidden/SystemApi into a public API. UID reuse and framework process accounting are not an incarnation-bound descendant registry or cgroup receipt. No hidden Binder shortcut is used. |
| Java `Process.waitForProcessDeath` / `openPidFd`; hidden | Numeric-PID wait or pidfd creation, not public SDK methods at this pin | Unsupported Java API route. Even an authentic single-process wait says nothing about children or external recipients; opening after PID reuse can identify another process. |
| Native `pidfd_open`/poll or `waitpid`; public native interfaces, with runtime conditions | Bionic exposes pidfd functions since API 31. A correctly acquired pidfd binds one process identity; parent wait is for waitable children | Manager is not zygote worker's Linux parent. ECHILD is not dead. A worker-supplied FD/number needs independent identity validation; a post-restart numeric open cannot prove the old incarnation. Actual kernel/policy availability remains Unknown for a particular stock build; even successful access does not enumerate/observe arbitrary descendants. |
| `/proc`, signal-zero, UID scans, cgroup files; native access subject to DAC/LSM/mount policy | Names/snapshots, or actual cgroup membership only if legitimately accessible and correctly identified | Hidden proc entries, EACCES/EPERM, PID reuse, group migration, reused paths or incomplete scans defeat absence inference. No documented public exact-worker cgroup handle/receipt found. A readable snapshot is not capability revocation. |
| Worker CLEAN, EOF/closed FD, destruction acknowledgement; public IPC/FD mechanisms | Cooperative report or state of a particular channel/reference | Worker can lie/close a channel while alive; a descendant can close that FD yet retain another. No timeout or EOF certifies all processes or transferred handles. |

### Exit-history negative witness

**Fact:** ActivityManager 4787–4819 documents bounded historical records;
AMS 10974–11010 allows own-package/caller-UID queries and requires DUMP for a
different package UID. AppExitInfoTracker 475–498 maps an isolated real UID through
its owner mapping before storing package history. Public ApplicationExitInfo
exposes PID, real/package/defining UID, process name, timestamp, reason and status,
but no cgroup-empty result or framework start-sequence completion token
(`current.txt` 5505–5542).

**Fact — request precedes death:** PR `killLocked` calls PL `noteAppKill` **before**
`killProcessQuiet` and group cleanup. PL forwards to `scheduleNoteAppKill`;
AppExitInfoTracker 312–330 queues `MSG_APP_KILL`. Its handler
`handleNoteAppKillLocked` (457–472) can insert/update history without requiring
`handleNoteProcessDiedLocked` or zygote SIGCHLD first. It sets reason/subreason and,
on update, status zero and a current wall-clock timestamp. Later process-death,
zygote and lmkd information are separate paths (298–309, 385–433).

**Inference:** a returned kill-reason record is not an independent proof that
the kill succeeded. Even when enriched by real direct-process exit information,
there is no descendant-empty or transferred-capability field. This is the
deterministic source falsifier for “exit-history entry means cleanup completed.”
It does not assert that an app query was observed racing the signal at runtime.

**Fact:** unloaded history drops incoming records (303–304, 316–317); retention
evicts oldest entries (1474–1507). PID filtering and timestamp sorting
(1420–1469) do not compare a manager epoch or framework start sequence. The
optional process-state summary is supplied by the calling process, is nullable
and diagnostic (ActivityManager 4822–4849). **Inference:** embedding an epoch in
compromised worker state does not make it a trusted certificate. Missing history,
reused identifiers or a newer manager process cannot safely release lockout.

### Process, UID and cgroup access

**Fact:** AMS 10818–10834 obtains `allUids` through ATMS `isGetTasksAllowed`
(3800–3829): recents/special permission or privileged legacy compatibility, not
package ownership. Ordinary UID filtering hides the isolated host from this
snapshot. `IProcessObserver` and `IUidObserver` declare `@hide`; AMS 8660–8663
requires signature `SET_ACTIVITY_WATCHER` (manifest 6276–6277). UID observation
checks usage-stats authority (AMS 8816–8825); ActivityManager 4971–5067 additionally
marks the convenience listener `@hide`/`@SystemApi`. DUMP is separately protected.

**Fact:** system/core `init/first_stage_init.cpp` 358 mounts proc with
`hidepid=2,gid=AID_READPROC`. Cross-UID proc visibility cannot be assumed from a
PID string. `createProcessGroupInternal` (processgroup.cpp 691–735) defaults to
system:system/0750 and, on successful stat, inherits the hierarchy's ownership
and mode. The reviewed cgroups.json v2 root is system:system/0775. Existing
SELinux domain rules exclude appdomain from the broad cgroup write grants
(private/domain.te 458–463). **Inference:** the isolated UID in a cgroup pathname
is not ownership or a grant to management. These facts do **not** prove every
cgroup file unreadable; file-specific DAC, SELinux and OEM configuration still
matter. No public API returns an authenticated per-incarnation cgroup handle or
the internal cleanup result. Absence/denial from a path remains Unknown.

**Fact:** unlike the hidden Java wrappers, Bionic's public `sys/pidfd.h`
(42–87) declares `pidfd_open`, `pidfd_getfd` and `pidfd_send_signal` since API 31,
with success/error returns. `libc/bionic/pidfd.cpp` (36–45) wraps the open/getfd
syscalls with FD tracking. **Inference:** this is a legitimate single-process
observation lead, not a forbidden hidden-API route. Public declaration does not
establish kernel support, signal/getfd permission, trusted acquisition of the
exact worker incarnation, or complete descendant registration. A genuinely
acquired pidfd resists subsequent numeric PID reuse; it does not retrospectively
authenticate a PID supplied after restart. Even successful death polling leaves
descendant and external-capability closure unresolved. No native call was executed,
and the API-31 declaration does not change research minSdk 30 or establish the
supported host minimum.

## Falsification, lockout and recommendation

**Inference:** the strongest candidate remains conditional framework enforcement
plus separately proven confinement of descendants and capabilities. The reviewed
sources reject these implications individually:

- Unbind returned → worker died: void request/bookkeeping, with asynchronous work.
- Binder died → entire tree died: one endpoint, independently surviving descendants possible.
- Cgroup kill requested → cleanup succeeded: explicit native failure returns, discarded upstream.
- Manager restarted → old worker gone: no old completion join; isolated predecessor exclusion.
- Process disappeared → copied data/external FDs revoked: independent recipients retain references/data.
- Same package → cross-UID signaling permission: actual credentials/LSM decide, not package text.
- Exit history exists → completed cleanup: kill-decision insertion precedes death observation.

**Inference — enduring fail-closed conditions:** any uncertain launch identity,
partial bind/unbind transaction, manager death before reconciliation, callback
loss, stale process/connection identity, unexpected extra binding/instance,
unverified descendant topology, kill/cleanup failure or lack of independent
completion keeps the prior epoch **CleanupUnknown**. A timeout is not a recovery
edge. The hypothesis requires durable uncertainty recorded before releasing
capabilities, so a fresh manager cannot interpret missing in-memory state as clean.
Do not reuse writable mappings/storage or start another hostile instance against
resources whose prior authority remains uncertain. Stop accepting old broker
epochs where management can enforce that, but do not call this erasure of copied
bytes or closure of external FDs. No public transition to verified whole-scope
revocation was established; lockout can therefore be indefinite. This document
does not retrofit the existing research harness or claim it implements durability.

| Remaining gap | Disposition |
|---|---|
| Exact reachability and alternate cleanup for invalid-start/unknown-record attachment; legacy manager-death OOM ordering | Source-resolvable further research: trace all callers and flag combinations before claiming an exploitable leak or guaranteed recovery. No need to repeat normal unbind. |
| A public independent exact-instance/tree completion contract | None found in the reviewed candidates. Additional research must name a concrete legitimate authority and falsifier; repeatedly probing the same callbacks does not supply a missing contract. |
| Native pidfd access and complete trusted no-descendant setup | Source/ABI/policy closure first; any resulting narrow mechanism still needs stock physical evidence. PR #18's Linux controls do not establish Android setup or authority. |
| Installed flags, startup/death ordering, Binder starvation, OEM timeout/ANR policy, actual cgroup errors, native blocked threads and latency | Physical-device-only runtime Unknowns after exact build/configuration identification. No testing performed or newly authorized here. |
| External FD/mapping/broker/data closure | Requires capability inventory and enforceable ownership/revocation design; neither a source trace nor phone observation alone proves global erasure. |

**Recommendation:** STOP guest/engine integration and production lifecycle claims.
Further work is defensible only as bounded source closure of the named gaps or
assessment of a concrete independent observer. If usable recovery requires a
weaker cleanup promise, privileged supervision, or changed containment/ownership,
Tony must explicitly approve an ADR for redesign before implementation. Neither
this PR nor its merge approves that change. Gate 0 remains Unresolved.

## Reproduction and validation

1. Check out the stated baseline and compare PR #19's base/head/merge trees.
   Query open PRs and the exact-main run; do not substitute a nearby green SHA.
2. Fetch each immutable ledger URL with `?format=TEXT`, base64-decode to bytes,
   verify SHA-256, and read the full named methods and callers. Reject mismatch
   or retrieval failure; never substitute a moving branch.
3. Reproduce the exit-history witness by following PR `killLocked` → PL
   `noteAppKill` → tracker `scheduleNoteAppKill` → `MSG_APP_KILL` →
   `handleNoteAppKillLocked` → `addExitInfoLocked`. Compare the separate process-death
   handler and public fields. No execution or synthetic Android result is involved.
4. Reproduce the startup falsifiers by contrasting the returned start PID with
   `app.getPid()` in PL 2957–2975, then AMS's unknown-record attachment branch.
   Reproduce the predecessor exclusion with PL 2799–2802, 2843–2846, 5864–5869.
5. Reproduce the access classification using public signatures **and** `@hide`,
   `@SystemApi`, AMS permission enforcement, manifest protection levels and proc/
   cgroup ownership. A Java `public` declaration alone is not public SDK authority.

No synthetic lifecycle model or new test is needed to establish these source
witnesses, and none is offered as Android runtime proof. **Observation:** foundation
validation passed (97 files, 55 Markdown files, 54 requirements, two ADRs), as did
harness authority validation. The existing regression suite completed 138 tests:
134 passed and four existing Windows-specific skips. The interrupted run's result
was unavailable on resumption, so the suite was rerun and its completed result
retained. All 63 retained AOSP ledger identities, including the eleven additions,
matched their SHA-256 values. Full change review covered local Markdown targets,
source references, license scope, whitespace, regular text-file modes and public
data; only the three intended documentation files change. No private paths,
credentials, upstream implementation, binary or dependency is added.

No Android rebuild or native execution was needed for this documentation-only
change. Hosted CI for the new PR remains **pending/unobserved at publication**;
stop after one immediate identity/native-attachment verification.
