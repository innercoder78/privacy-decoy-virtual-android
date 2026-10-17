# Gate 0: Android 17 isolated-worker lifetime authority

Review: **2026-10-17, America/Fortaleza**. **Source investigation only; no Android
execution.** Gate 0 remains **Unresolved**; Gates A–G **Not reached**. ADR-0001
remains **Accepted**, ADR-0002 **Proposed**. No production engine is selected.

**Inference — decision:** no complete ordinary-app termination, descendant
cleanup and independently observed revocation contract is established. There is,
however, a concrete system-owned termination candidate worth further bounded
source investigation: remove the last auto-create binding to a dedicated,
never-started isolated service, then let the framework's **isolated-not-needed**
process trimming kill its process and schedule cgroup cleanup. The kill predicate
does not require the worker's destruction acknowledgement. This is stronger than
cooperative `onUnbind`/`onDestroy`, but is neither an app-selected deadline nor an
app-visible tree-empty receipt. It does not authorize guest integration.

This extends [PR #15's containment audit](gate-0-worker-containment.md), which
explicitly left last-binding removal and destruction timing unresolved. New
findings are the running-service versus executing-service distinction, the actual
Android 17 `am/psc` OOM-adjuster path, loss of the native cleanup return value, and
the client's removal of its ServiceConnection death monitor **before** unbinding.
The earlier [seccomp work](gate-0-seccomp-process-control.md) remains separate:
preventing descendants is a conditional additional restriction, not kill authority.

## Classification, scope and baseline

Every finding below uses **Fact** (identified source behavior), **Observation**
(repository, retrieval or test observation), **Inference** (reasoned implication),
**Hypothesis** (unproved candidate), **Unknown** (missing evidence), or
**Unsupported** (excluded production route). A source Fact is not a claim about
every installed Android 17 build. Tables inherit the explicit class in their row
or introductory sentence. The research model is a Hypothesis, not production code.

**Observation:** live canonical main was the expected
`0af04da8fcaad1c69db5b4f3c6459c8f9d433116`, merge of
[PR #18](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/18),
head `ef56d11b131a7dd1acbc7b9f39782c5ff641660e`, base
`c2c3b19d0c75f508c52608bb2ed80a8bb974c69a`. Merge and head trees match.
Open PR inventory was empty; there were no open diffs/heads to reconcile.
PR #18 reviews, conversation comments, inline comments and review threads were
empty, with no next thread page. Relevant PR #12–18 history and controls were
inspected. The clean checkout, existing branches, one registered worktree, no
stashes and ignored build/research assets were preserved. The new branch starts
at that exact main. No applicable AGENTS.md was found.

**Observation:** exact-main
[foundation run 39056805319](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39056805319)
and [Android run 39056805310](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39056805310)
succeeded. Logs identify the exact checkout. Foundation executed all four real
Linux seccomp scenarios, not just the modeled oracle:

| Observation: scenario | Actual log evidence and limit |
|---|---|
| `tsync` | Successful installation; pre/post-thread process creation EPERM, clone3 ENOSYS, exec EPERM, NNP reset EINVAL, added ALLOW still denied; zero created processes |
| `thread-only` | Main denied, peer created a process; worker exit 42, probe exit 95; negative control demonstrates missing synchronization |
| `invalid-install` | EINVAL, terminal state, zero probes, worker exit 43 |
| `divergent-tsync` | Positive peer TID installation result, terminal state, zero probes, worker exit 43 |

**Observation:** final receipt was `PASS: seccomp real cases=4
all-owned-children-reaped; not Android evidence`. Source SHA-256 was
`f4702f368a09989f5359b63852aabe22e7bf93afeda0649a53304a4871d169fc`.
Runner was Ubuntu 24.04.5, x86_64, Linux `6.17.0-1022-azure`. The four earlier
Linux lifetime controls and four assertion mutations also passed. Android logged
68 protocol/report checks, successful builds/lint and APK authority/inventory
inspection. These are historical CI observations, never physical Android results.

**Observation:** all three workflows were active. Their checkout pins, permissions,
path filters and steps were inspected. Combined commit status had zero contexts;
aggregate `pending` was not a failed or additional check. Main was unprotected.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational, page update `2026-10-17T10:34:18.081Z`. All 95 baseline tracked files
had mode `100644`. Dependency/provenance ledgers and the existing native inventory
were inspected; no dependency or binary is added or executed. Existing antivirus
uncertainty is not cleared by this review. Historical Privacy-Decoy is untouched.

**Observation:** governing [requirements](../requirements.md),
[boundaries](../security-boundaries.md), [gates](../feasibility-gates.md),
[roadmap](../roadmap.md), both ADRs, [provenance policy](../source-provenance-policy.md),
containment/source/seccomp records, [harness](gate-0-isolated-worker-harness.md),
[native launcher](gate-0-isolated-native-launch.md), and
[integration review](gate-0-qemu-worker-integration.md) were consulted. This evidence
addresses PDVA-REQ-002–003, 009–015, 036–045 and 054 without changing them.

## Exact source scope and reproduction

**Observation:** framework source uses the existing Android 17 reference commit
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`; system/core uses
`545d2487e38192a2ce25040897ced877cf6b4f53`. The
[immutable ledger](gate-0-worker-containment-sources.md#android-lifetime-authority-continuation-2026-10-17)
adds exact paths and decoded-byte hashes. All 31 retained AOSP files from the
original containment ledger were independently rehashed successfully. New files
were fetched by full commit, base64-decoded without newline conversion and hashed.
No upstream code was compiled, imported into tracked source or executed.

**Fact:** the OOM implementation is now under `services/core/java/com/android/server/am/psc/`.
The previously recorded 404 for `am/OomAdjuster.java` is not evidence that Android
lacks isolated-process trimming. The pinned directory listings resolve this path.
**Unknown:** correspondence to a particular OEM image, compiled feature flags,
kernel/configuration, scheduling and installed SELinux policy. These per-project
reference commits are not a complete Android release manifest.

For independent reproduction, fetch the ledger URLs with `?format=TEXT`, decode,
verify SHA-256, then inspect the complete methods and their callers below. Line
numbers refer to those decoded bytes. A text match alone is not a control-flow
proof. Failed retrieval or a hash mismatch makes that witness Unknown.

## Caller-to-enforcer trace

### 1. Public binding, identity and service-needed state

**Fact:** `ContextImpl.bindService` and `bindIsolatedService` converge on
`bindServiceCommon` (2168–2318), which creates a client service dispatcher and
calls `IActivityManager.bindServiceInstance`, including `instanceName`.
`ActivityManagerService.bindServiceInstance` (14752 onward) rejects isolated
callers, validates caller/package/instance and dispatches to
`ActiveServices.bindServiceLocked`. Service resolution checks exported status and
component permission; ownership of PDVA's non-exported service permits management
binding, not a grant to arbitrary callers. Special bind flags have separate checks.
No extra privileged permission is needed for the harness's ordinary binding.

**Fact:** `ActiveServices.bringUpServiceLocked` uses `isolationHostProc` for the
isolated service (6310–6378); `ProcessList.newProcessRecordLocked` allocates an
isolated UID (3509 onward). The normal zygote path creates its cgroup while
privileged, as already traced in the original ledger. Neither package identity,
instance name nor knowledge of the PID makes management the worker's Linux parent
or gives it signal permission across isolated UIDs.

**Fact:** `ServiceRecord.getNeededReasonsLocked` (1978–2003) tests **startRequested
OR auto-create connections**. `ActiveServices.bringDownServiceIfNeededLocked`
(6743–6760) returns while needed or pending launch. Therefore stopping a started
service with an auto-create binding still present does not tear it down.

**Fact:** `ContextImpl.stopServiceCommon` (2148–2164) maps the internal integer
result to a boolean; AMS passes a **null instanceName** (14582–14611).
`ActiveServices.stopServiceLocked` (1694–1771) clears started state and returns 1
for a found service after requesting conditional teardown, -1 for denied lookup,
0 for no service. **Inference:** this public call is not a named-isolated-instance
kill API and its true result is not proof of exit. For a named binding, retain its
actual ServiceConnection identity; do not invent an instance parameter for stop.

### 2. Unbind and cooperative destruction are distinct from kill

**Fact:** `ContextImpl.unbindService` (2374–2389) first calls
`LoadedApk.forgetServiceDispatcher`, then AMS unbind. `LoadedApk.doForget`
(2345–2354) unlinks the dispatcher's death monitors, clears active connections
and marks it forgotten. AMS returns `ActiveServices.unbindServiceLocked`'s
boolean; Context's public method is **void** and discards it. The internal true
means a recorded connection was removed, not that its host or descendants exited.
A remote error can occur after local dispatcher removal.

**Fact:** `ActiveServices.unbindServiceConnectionsLocked` →
`removeConnectionLocked` (4725–4807, 7084–7214) removes framework connection
records, may schedule unbind on the worker, computes remaining auto-create
bindings and calls conditional service teardown. These are system_server actions.
`bringDownServiceLocked` (6762–7046) removes service lookup/restart state and calls
`stopServiceAndUpdateAllowlistManagerLocked` **before** `scheduleStopService`.
The helper (4133–4141) calls `ProcessServiceRecord.stopService` (135–144), which
calls the controller's `removeRunningService`. Its underlying implementation
removes from `mServices`; `numberOfRunningServices` is that set's size
(`ProcessServiceRecordInternal`, 321–340).

**Fact:** running-service bookkeeping is different from `mExecutingServices` and
`executeNesting`. `bumpServiceExecutingLocked` tracks callbacks and ANR timing.
`IApplicationThread` is a **oneway** interface; its schedule calls do not wait for
the callback body. `ActivityThread.handleStopService` (5838–5868) invokes
`onDestroy`, drains queued work, then reports `serviceDoneExecuting` (itself
oneway in `IActivityManager`). `serviceDoneExecutingLocked` updates execution
bookkeeping and clears the service's process reference. **Inference:** a hostile
worker can suppress or fabricate cooperative completion; this is not a trusted
cleanup certificate. A surviving Binder/native thread need not run onDestroy.

### 3. Independent isolated-not-needed kill, with scheduling qualifications

**Fact:** `psc/OomAdjuster.updateAndTrimProcessLSP` (1347–1491) iterates framework
LRU records. For a running process not already killed by AM, after the
pending-finish-attach exclusion, it tests `isolated`, zero running services and
no isolated custom entry point. It calls `killLocked` with reason
`isolated not needed` and `SUBREASON_ISOLATED_NOT_NEEDED` (1469–1479).
It does **not** test service-destruction acknowledgement or zero executing services.
This branch is separate from excessive cached-process trimming policy.

**Fact:** the caller is `postUpdateOomAdjInnerLSP` (1176–1183), reached by both
full and partial updates in `OomAdjusterImpl` (794, 908).
`ProcessStateController.runPendingUpdateImpl` (338–340) commits events and calls
`updateOomAdjPendingTargetsLocked`; empty pending sets and ongoing updates have
explicit guards (OomAdjuster 1107–1133). Binding teardown requests OOM work via
`unbindServiceConnectionsLocked`, `bringDownServiceLocked` and
`bumpServiceExecutingLocked`. With `pscBatchServiceUpdates`, updates are deferred
to the outer batch close; `SyncBatchSession.onLastClose` calls
`updateIfNecessary`, which only runs an update if one was requested. Without that
flag, explicit legacy calls run pending updates.

**Fact — closing the normal unbind trigger:**
`getServiceBindingOomAdjPolicyForRemovalLocked` (ActiveServices 6454–6468)
asks `evaluateServiceConnectionRemoval`. Its prelude (OomAdjuster 2878–2888)
explicitly returns true for an **isolated** host, before importance comparisons.
For distinct manager and isolated host this retains the legacy update policy.
After `removeConnectionLocked` returns, `unbindServiceConnectionsLocked`
(4738–4757) enqueues the remaining host record and sets `needOomAdj` for that
policy. `unbindServiceLocked` then runs pending targets or closes the outer
batch (4790–4807). `SyncBatchSession.maybeEnqueueProcess` sets `mShouldUpdate`
when it accepts the record. Thus the normal attached, dedicated, last-binding
path has an explicit **post-removal** update request; it does not rely solely on
the earlier callback-related OOM update or a later onDestroy acknowledgement.
An ongoing OOM update defers pending work to its own completion path.

**Inference:** removing the last hosted service makes a dedicated normal isolated
worker eligible for an externally owned kill without its cooperation **when this
trim pass runs**. Blocking onDestroy does not restore the removed running-service
record. A hostile isolated caller cannot simply invoke public bind/start as its
management UID. **Unknown:** all startup/error/concurrent-death interleavings,
manager-death removal timing (a different caller), and installed-build latency.
`wasOomAdjUpdated`, pending attach, callback exceptions and record replacement
still need path-specific treatment. The explicit normal-path update establishes
more than bare eligibility, but does not create a public time bound or a
completion receipt. Do not promote it into an unconditional immediate-unbind-kills
guarantee.

**Fact:** callback timeouts are another path: `ActiveServices.serviceTimeout`
(8278–8342) validates execution state and forwards to `AnrHelper`; it can discard
or reschedule. `ProcessErrorStateRecord.appNotResponding` has a conditional silent
background-ANR kill (779 onward) and a distinct UI/controller path. **Inference:**
ANR policy is not a PDVA-selected immutable lease or guaranteed user-independent
termination deadline. Neither ANR nor callback completion is needed in the
isolated-not-needed predicate itself.

### 4. System-owned kill and the lost completion result

**Fact:** `ProcessRecordInternal.killLocked` overloads default to asynchronous
group cleanup. `ProcessRecord.killLocked` (1367–1415) signals the primary PID and
calls `killProcessGroupIfNecessaryLocked`; normal zygote workers use group cleanup,
while app/webview-zygote paths have creation-state guards. Killed flags are set
after requesting termination, without waiting for every descendant to exit.
AMS `appDiedLocked` (4036–4093) validates current record/PID/thread identity and
requests group cleanup on its applicable not-already-killed path.

**Fact:** `ProcessList.killProcessGroup` (1689–1699) normally queues a message.
`KillHandler` (799–810) calls hidden `Process.killProcessGroup(uid,pid)` and
**ignores its boolean result**. JNI `android_util_Process.cpp` (1308–1316) returns
`libprocessgroup_platform::killProcessGroup`; that wrapper (26–29) returns whether
`KillProcessGroup(..., SIGKILL, ...) == 0`. The early-system fallback also ignores
the boolean. There is no result delivery from this chain to the ServiceConnection
or unbind caller. An invocation is not an independently observed completed kill.

**Fact:** `libprocessgroup/processgroup.cpp` (413–520, 567–688) uses system-owned
UID/PID cgroup paths. SIGKILL takes `cgroup.kill` when supported; otherwise the
membership-scanning path signals processes/groups. The cgroup.kill path returns
false on write failure. `KillProcessGroup` opens `cgroup.events`, observes
population, retries signaling/removal and can return errors. Its default 2200-ms
attempt deadline starts in native code, **after** queue/scheduling delay; it is
not a public maximum lifetime. A no-cgroups branch can return without the
cgroup-population observation. Even native success is scoped to its actual path.

**Inference:** system cgroup cleanup can cover descendants that changed POSIX
session/group, assuming inherited membership and enforced inability to migrate
out. The existing pinned Linux cgroup source supports this distinction. The
fallback scan must not inherit atomic cgroup.kill semantics. **Unknown:** installed
cgroup hierarchy, kernel behavior, migration restrictions and failure recovery.
No ordinary-app access to the system's completion observation is established.

**Fact:** `PhantomProcessList` scans cgroup membership and applies trimming/stale
policy; it skips certain already-killed/app-zygote parents and has scheduled work.
`PhantomProcessRecord` distinguishes kill requests, death observation and zombie
timeout. **Inference:** phantom handling is additional system policy, not an app's
complete descendant registry, selected lease or tree-empty receipt.

## Authority matrix

All rows concern a completely compromised native worker. **Fact/Inference** means
the operation/path is a source Fact and its fitness assessment an Inference.
The shared residual-authority rule below applies to every row.

| Class; operation | SDK, caller and availability | Isolated UID / exact instance | Independent enforcement and descendant coverage | Completion, restart and remaining gap |
|---|---|---|---|---|
| Fact/Inference; bind / bindIsolatedService | Public; ordinary non-isolated manager, component access and valid flags | Named isolated instance supported; no kill capability returned | Framework creates process/UID/cgroup; binding retains service need | Boolean request result, later connection; no cleanup acknowledgement; auto-create can recreate after death |
| Fact/Inference; unbind last auto-create connection | Public void; manager with registered connection; no privileged grant | Targets that connection; other bindings/started services can retain host | Framework removes records; eligible isolated host is killed by OOM trimming independently of callbacks; system group cleanup follows kill | No tree receipt or app deadline; dispatcher death monitor removed; errors/uncertainty lock out restart |
| Fact/Inference; stopService | Public; ordinary caller with component access, AMS rejects isolated caller | Component lookup, public path has no instanceName; not an arbitrary isolated-PID selector | Clears started need; active auto-create binding prevents teardown; no unconditional kill | True means service found/requested; not dead; remaining bindings can retain/recreate |
| Fact/Inference; killBackgroundProcesses / deprecated restartPackage alias | Public, KILL_BACKGROUND_PROCESSES (or legacy permission); ordinary own-package restriction | Package/app-ID and importance filters; not per named worker; isolated UID does not match owner's app ID merely by package | If eligible, system removal/kill; cannot assume active bound worker eligible | Void; no selected-tree receipt; restart permitted by service policy |
| Fact/Inference; Process.killProcess / native kill / pidfd signal | Public signal wrapper / native syscall; sender credentials, capabilities and SELinux apply | Specific process only; owning APK does not grant cross-isolated-UID SIGKILL | Authorized SIGKILL cannot be caught; ordinary manager cross-UID authority not established; no descendant scope | Signal attempt is not wait/reap or tree-empty; numeric identity reuse and pidfd authority distinct |
| Fact/Inference; isolated-not-needed OOM branch | Internal system_server policy; indirectly reachable via ordinary lifecycle requests | Framework ProcessRecord, isolated UID, no services/custom entry point | Actual primary kill plus system group cleanup; callback refusal does not veto predicate | System scheduling/flags govern trigger; no app receipt; another bind can create a new record |
| Fact/Inference; ANR, memory/background/phantom policy | Internal system policy, configuration and sometimes UI decisions | System chooses eligible process(es), not manager-selected epoch | Actual kill paths exist; group scope depends on path; no universal wall-clock/aggregate quota | No ordinary-app complete-teardown contract; manager can also be killed |
| Unsupported; killUid / forceStopPackage | Hidden/system-facing, KILL_UID / FORCE_STOP_PACKAGES checks in AMS; not ordinary production authority | UID or package, not per-epoch public handle | Privileged system kill paths exist; not an authorized PDVA mechanism | Even privileged acceptance is not transferred-capability revocation; user Settings interaction is external recovery, not an app API |
| Unsupported; Process.killProcessGroup / native libprocessgroup | Hidden API/native internal library; cgroup and signal permissions still required | UID/PID cgroup internal identity | System authority works; loading/calling library does not delegate it | Native return exists internally but caller access is not established; root/shell/ADB/OEM remedies excluded |
| Fact/Inference; Binder death / ServiceConnection | Public observation interfaces, scoped to accessible objects | Endpoint, not authenticated descendant-set handle | Do not initiate kill; worker CLEAN and serviceDoneExecuting are weaker cooperative reports | No descendant enumeration, cgroup-empty or external-capability proof; disconnect can leave binding for reconnection |

**Fact:** AMS `killBackgroundProcesses` (4309–4365) uses `SERVICE_ADJ` and own-app-ID
checks; `ProcessList.killPackageProcessesLSP` (3190–3280) checks actual process
app ID, package dependencies and PCC exceptions. Ordinary package-name membership
alone is insufficient. AMS `killUid` (9389 onward) and `forceStopPackage` (4479
onward) enforce their privileged permissions. No permissions are added here.

**Fact/Inference — residual-authority rule:** termination releases references of
processes that actually exit. Closing management's FD does not close transferred
or duplicated FDs; a mapping can retain a file independently of an FD; external
recipients can retain data/handles/Binder references. Binder death describes an
endpoint, not cleanup of every native descendant or recipient. Revoking future
broker epochs cannot erase previously copied bytes. The original ledger's
`fs/file.c`, `mm/mmap.c`, isolated-app FD policy and
[containment analysis](gate-0-worker-containment.md#threat-and-lifetime-model)
anchor these facts. Complete cgroup emptiness would still not certify global
capability revocation. No table row requires forbidden authority unless marked
Unsupported; none supplies a complete ordinary-app contract.

## Adversarial lifecycle and research state model

**Fact:** manager process death reaches AMS application cleanup →
`ActiveServices.killServicesLocked` (7797 onward), which removes that client's
connections through the same removal path. This is outside the worker, unlike
the harness's worker-owned owner-Binder death callback. A dying worker can have
services scheduled for restart when restart is allowed and bindings/started need
remain (7935–7970). `bringDownServiceLocked` removes restart/pending state.
**Inference:** losing the only manager binding is a credible independent cleanup
trigger; merely starting a new manager does not certify what happened to the old
worker. Fresh instance names avoid accidental binding reuse, not old-resource
revocation. Simultaneous instances require separate identity and uncertainty state.

**Hypothesis — research model only:** maintain per-instance epoch and a durable
uncertainty marker before granting capabilities. The following states describe
what a future controller may conclude; they do not modify or validate Session.java.
`LOCKOUT` is terminal for this experiment, including after manager restart.

| Transition | Controlling authority / preconditions | Observation actually certified; required next state |
|---|---|---|
| Unused → Reserved → Active | Trusted manager durably records fresh epoch, then binds/delegates; framework grants binding | Binding and authenticated endpoint identity only; a failed persistence/bind/handoff enters LOCKOUT |
| Active → ReleaseRequested | Manager rejects future epoch operations and calls unbind; stop separately clears started need if applicable | Local policy closure/request handling, not process death |
| ReleaseRequested → ServiceUnneeded | system_server removes last auto-create connection; no started need/pending launch; removes last hosted running-service record | Internal bookkeeping, generally not a public receipt; another remaining binding prevents this transition |
| ServiceUnneeded → KillRequested | System OOM pass sees running isolated record, no services, no custom entry point, no pending-attach exclusion | Internal signal/group-cleanup request; hostile onDestroy cannot veto this predicate; scheduling not bounded here |
| Any live state → EndpointDead | Kernel/Binder endpoint death, independently received by retained observer | That endpoint's death only; descendants, outstanding cleanup and delegated references remain Unknown |
| KillRequested → GroupAttempt → GroupEmptyInternal or FailedInternal | system kill handler + kernel/libprocessgroup, correct UID/PID cgroup and membership | Native path-specific population/removal result; handler discards return; manager receives no such certificate |
| Any uncertain live/releasing/dead state → LOCKOUT | Trusted manager policy on timeout, lost observation, ambiguous identity, partial cleanup or persistence failure | Unknown is preserved; no automatic rebind, epoch reuse or resource reuse |
| Manager dies → restarted manager in LOCKOUT | System removes old client bindings; restarted manager reads durable uncertainty | Old cleanup not proven by new process, absent local session or new UID/PID; no automatic retry |
| GroupEmptyInternal → VerifiedRevocation | Would require trusted externally accessible identity-bound completion AND closure of all delegated authority | **Unknown/unimplemented edge**; no reviewed public observation enables it |

**Inference:** native blocking, an ignored destroy message or fabricated CLEAN
cannot promote state to VerifiedRevocation. A native crash or direct-parent death
can leave a descendant until actual system cleanup; a detached descendant remains
subject to cgroup membership, not ordinary parent reaping. Queue delay, cgroup
write/read/removal errors and exhausted CPU/memory/Binder resources can delay or
lose observations. Bound and executing service importance, background limits and
user interaction change scheduling, not what evidence certifies. App force-stop
through external UI is not a programmatic per-instance receipt and may require
separate recovery authorization. No restart edge is allowed from uncertainty.

## Falsifiable checks and decision

**Observation:** no synthetic lifecycle test is offered as proof of Android
enforcement. The following are explicit source counterexample checks, not executed
Android scenarios. They reject a claim by checking its missing assumption.

| False claim / negative control | Source witness and reason to reject |
|---|---|
| Unbind returned, so worker/tree exited | Public void path discards internal boolean; internal path removes connection; queued group cleanup has separate result |
| Destroy callback must return before any independent kill | Remove-running-service occurs before scheduleStop; OOM predicate counts running, not executing services |
| Binder death certifies all descendants exited | LoadedApk.doDeath identifies one Binder; group cleanup queued separately; no descendant-set/population receipt |
| Manager restart certifies old cleanup | killServices removes connections; restarted manager is not a join on KillHandler and receives no native result |
| Worker CLEAN/serviceDoneExecuting is authoritative | Worker invokes report; arbitrary native compromise controls it; neither carries trusted cgroup observation |
| Same package grants SIGKILL to isolated UID | Distinct allocated UID; kernel credential/security checks still apply, package string supplies no signal privilege |
| cgroup kill attempt proves completion | Signal write and cgroup.events/removal stages differ; native failures exist and KillHandler ignores boolean |
| Manager close revokes every FD/mapping | Reference-counted duplicates/transfers and independent VMA reference survive that close |
| Missing onServiceDisconnected after unbind proves stuck worker | forgetServiceDispatcher removes its death monitor before unbind; absence of this callback is not evidence of liveness |

**Hypothesis:** a dedicated never-started, non-shared, normal-zygote isolated
service with one manager-owned auto-create binding is a credible **termination
trigger research candidate**. Combining it with independently installed,
irreversible process-creation restrictions might simplify descendant accounting.
That combination still needs trusted setup before compromise, all-thread/ABI
coverage, no preexisting descendants, installed Android authority and a trustworthy
completion observation. PR #18's Linux success supplies none of those Android
conclusions. No production lifetime strategy is accepted.

| Class; decision question | Answer / next evidence |
|---|---|
| Fact; what genuinely exists? | Independent isolated-not-needed kill, process-death group cleanup, cgroup.kill or scan fallback, internal population/removal checks, conditional ANR/phantom/resource kills |
| Fact/Inference; what can an ordinary app initiate? | Its legitimate binds/unbinds and eligible stop/background requests; it can cause eligibility but does not own the system kill queue, cgroup or acknowledgement |
| Inference; what resists worker compromise? | System-owned bookkeeping/kill and kernel restrictions, under exact predicates; worker callbacks/timers/replies do not |
| Fact/Unknown; what can be verified? | Source chain, public return semantics, one endpoint death and scoped historical CI; no complete app-observable tree termination or external FD/mapping/data revocation |
| Hypothesis; worth pursuing? | Yes, extend the normal last-binding → post-removal trim trace to exceptional paths and observation access. No, not yet as a shippable complete hostile-worker lifetime contract |
| Unknown; source-resolvable gaps | Close pending-launch, callback-error, manager-death and concurrent replacement interleavings; audit complete Binder authority available to hostile isolated code, cgroup migration policy, UID/PID reuse and restart/error paths; search for a legitimate trusted completion interface with exact caller/return proof |
| Unknown; later physical-only gaps | Actual stock user-build flags/policy/hierarchy, noncooperative destruction and descendant behavior, manager crash/restart, error/exhaustion latency and observation reliability on the declared OEM/ABI matrix |
| Hypothesis; falsifiers | A supported path retains worker indefinitely after last binding with no independent trigger; descendant escapes intended cgroup coverage; ordinary-app restriction installation fails; stale/false endpoint identity accepted; cleanup errors permit restart; transferred writable authority persists where revocation is required |
| Unsupported; forced exits | STOP dependent integration if kill/observation contract cannot close. NARROW only with Tony's explicit approval of reduced scope. REDESIGN only with a separate owner-approved ADR; root/shell/ADB, hidden bypasses, privileged supervisor or cooperative-only security are not silent remedies |

**Inference:** device testing can falsify a proposed mechanism on a build; it cannot
manufacture a public completion API missing from the reviewed call chain. First
resolve the source questions that are actually source-resolvable. Later physical
evidence needs separately authorized bounded synthetic probes and independent
observations; no phone, ADB, physical device, Codex Cloud, QEMU or guest is used here.

## Validation and publication scope

**Observation:** this is original evidence plus source-ledger/index updates only.
No worker, launcher, manager, runtime dependency, workflow, security architecture,
host VPN or previous PR #12–18 control changes. Source references retain upstream
file notices; no referenced implementation is redistributed in this PR.
**Observation:** foundation validation passed: 96 files, 54 Markdown files,
54 requirements, two ADRs. Repository regression suite: 138 tests, OK, four
pre-existing Windows skips (134 executed passes). Harness manifest/source
authority validation passed. Markdown targets, immutable source identities,
file modes, text-only inventory, public-data hygiene and whitespace were reviewed.
No new Android build or Linux process execution was needed for this documentation
change; historical exact-main CI is separately identified above. New-PR hosted CI is
**pending/unobserved at publication**; preserve existing checks and stop after one
immediate PR identity/native association verification, without polling.
