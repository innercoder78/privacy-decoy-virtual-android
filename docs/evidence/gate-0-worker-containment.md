# Gate 0: non-cooperative worker and descendant containment

Review: **2026-10-16, America/Fortaleza. Source evidence; new Linux process
controls NOT RUN.** Gate 0 remains **Unresolved**. Gates A–G remain **Not reached**.
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No production VM engine is
selected. No phone, ADB, guest execution or QEMU/APK integration occurred.

**Finding:** no complete ordinary-app containment and revocation path has been
established for arbitrary native compromise of PDVA's isolated worker. Android
does have system-owned cgroup cleanup of app processes and their descendants;
it would be incorrect to claim that the framework only kills a service PID.
However, that source mechanism is not a public PDVA-controlled, bounded,
independently acknowledged tree-termination API. Existing cooperative harness
cleanup and direct-child reap results do not fill that gap. This is a blocker
to claiming a defensible hostile-worker lifetime boundary, not proof that every
possible ordinary-app implementation is impossible.

This record refines the [integration review](gate-0-qemu-worker-integration.md),
[native launch control](gate-0-isolated-native-launch.md) and
[isolated-worker harness](gate-0-isolated-worker-harness.md), under the existing
[requirements](../requirements.md), [boundaries](../security-boundaries.md),
[gates](../feasibility-gates.md) and [provenance policy](../source-provenance-policy.md).
It changes no production source, dependency, workflow, requirement or ADR.

## Independent preflight

Canonical main was `99b11b6c4aaff42a25f99b33e712dde52dfe2fdc`, as expected.
Open PR inventory was empty. [PR #14](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/14)
was merged at `2026-10-16T05:34:52Z`, head
`bfb68228a8dff04656d1ead331937317eca51347`, base
`15086b1c6b4a5bcfe14bbca1c416079c9bf378e5`, merge equal to current main.
The complete seven-file, 506-insertion merged change was inspected. Its tree
equals the source-head tree. Reviews, conversation comments, inline comments
and review threads were empty; there were no unresolved threads.

PR #14's [foundation](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38855763140),
[Android](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38855763091)
and [cross-build](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38855763112)
checks succeeded. The cross-build log checked out the exact PR head and recorded
all 13 startup cases and three mutants with their intended exit codes, followed
by cross-build completion. These are earlier hosted Linux/configuration and
build results, **not descendant-containment tests**. Exact-main foundation and
Android checks also succeeded. Combined commit status had zero contexts; its
aggregate `pending` was not an additional pending check. All three registered
workflows were active; their pins, permissions, path filters and checks were
read. GitHub Status reported All Systems Operational, page timestamp
`2026-10-16T03:19:25.204Z`. Main was not branch-protected; this research does not
claim server-enforced required checks or alter repository settings.

Local worktree was clean at the PR #14 head; one registered worktree, no stashes.
Existing branches and ignored build/dependency/research trees were inventoried
and preserved. The new branch starts at verified main. Tracked modes were all
regular `100644`. The dependency ledger, Gradle verification metadata, native
source inventory and antivirus incident record were inspected. Retained binaries
were not re-executed or newly attested. Historical Privacy-Decoy was not modified.

## Evidence scope and exact sources

The [immutable source ledger](gate-0-worker-containment-sources.md) supplies
repository revisions, paths, source links and SHA-256s for the reviewed bytes.
The AOSP revisions were resolved independently from `android17-release`, then
files fetched by commit, not by a moving branch. They are reference snapshots,
not a pinned OEM release manifest or evidence of installed policy. Linux v6.12
is a semantic reference, not an assertion about any Android device's kernel.
Official documentation was read on the review date and is separately mutable.

Evidence classes here: **S** = source/documentation fact, **I** = inference,
**U** = unproved Android/runtime behavior, **P** = proposed unrun control.
There are **zero new executed Linux process scenarios** in this PR.

## Threat and lifetime model

Assume arbitrary native code execution in the worker, including direct syscalls,
altered handlers, fabricated replies, duplicated FDs and attempts to fork/exec.
Do not assume compromise of the host kernel, system_server or management. Their
correct enforcement, installed configuration and every delegated interface remain
part of the prospective TCB. QEMU's argument restrictions cannot constrain code
that has already escaped into the QEMU host process.

Management and the isolated service are different UIDs. The service is created
through Android's zygote/framework path; it is not management's Linux child.
A native child of the service is its direct child; grandchildren need not remain
its waitable children after reparenting. Parentage, process group, session,
cgroup, UID, SELinux domain, Binder object and PDVA epoch are distinct identities.

A fork inherits references to open files and mappings; exec retains descriptors
without close-on-exec, while replacing the address space. A duplicated descriptor
is another reference, not a fresh authorization query to management. A file-backed
mapping has its own reference and can outlive descriptor close. Termination drops
the terminating process's references, not references in survivors or recipients.
Previously disclosed/copied bytes cannot be recalled. An epoch can reject future
broker operations; it cannot revoke raw FDs, shared mappings or copied data.
See Linux `fs/file.c` (`dup_fd`, `close_fd`), `mm/mmap.c` (`get_file` for VMAs),
and the isolated-app policy explicitly permitting use of received file/socket FDs.

## Android source findings

### Creation and baseline authority

**S:** `ActiveServices.bringUpServiceLocked` chooses isolated process creation;
`ProcessList.newProcessRecordLocked` allocates an isolated UID. The normal zygote
specialization calls `createProcessGroup` while privileged and installs the app
seccomp filter. `ProcessList` handles group creation for app/webview-zygote paths.
PDVA's current manifest does not use an app zygote or shared isolated process.
The [service documentation](https://developer.android.com/guide/topics/manifest/service-element#isolated)
describes isolated execution without the application's own permissions.

**S:** `isolated_app_all.te` forbids opening app-data files but permits defined
operations on already-open files received over IPC, including mapping. Ordinary
`isolated_app.te` permits use of received TCP/UDP sockets; creating those sockets
is separately forbidden. `domain.te` grants self fork and signal permissions.
Thus isolated does not mean no descendants or no capabilities. UID/DAC, SELinux,
seccomp and per-object authority must all permit an operation; an allow rule
alone is not proof that the syscall succeeds on a stock device.

**S:** Bionic's app policy inputs include `SYSCALLS.TXT`, common/app allowlists
and common/app blocklists. The inspected lists admit clone/clone3, execve,
setsid/setpgid, prctl, wait4/waitid and pidfd operations at the syscall-number
layer for the relevant architectures. The generator subtracts blocklists and
adds allowlists. This is not a no-fork policy. **U:** generated/installed filters,
argument restrictions elsewhere, ABI/kernel support, labels and permissions.
The existence of a Bionic wrapper does not establish signal or ptrace authority.

### Framework cleanup is stronger than POSIX process-group cleanup

**S:** `ProcessRecord.killLocked` signals the main PID and calls
`killProcessGroupIfNecessaryLocked`. `ActivityManagerService.appDiedLocked`
also invokes group cleanup on the applicable process-death path. The ordinary
`ProcessList.killProcessGroup` path queues work on a system kill handler.
These paths are outside compromised worker code.

**S:** `libprocessgroup.sendSignalToProcessGroup` uses the UID/PID cgroup. For
SIGKILL, where available, it writes `1` to `cgroup.kill` and also signals the
original POSIX process group. Otherwise it reads `cgroup.procs` and signals
member processes/groups. `KillProcessGroup` reads `cgroup.events`, retries
signaling/removal, and has a default deadline of 2200 ms. It can log still-populated
groups and return errors. That deadline bounds this routine's attempt, not a
public guarantee that every process has finished exiting within 2200 ms.

**S/I:** Linux cgroup membership is inherited on fork; exec and setsid do not
themselves move a task to another cgroup. Linux's `cgroup.kill` handles concurrent
forks and migrations as documented in the pinned cgroup-v2 source. A detached
grandchild is therefore a counterexample to plain process-group killing, **not**
automatically a counterexample to Android cgroup killing. The fallback member
scan is a distinct path; it must not inherit atomic tree-kill claims.

**S:** cgroup configuration and creation are system-owned. The general SELinux
cgroup write grants exclude appdomain; no reviewed rule/API delegates a private
kill/quota cgroup to PDVA. `Process.killProcessGroup` and
`sendSignalToProcessGroup` are hidden framework methods. Calling a similarly
named native function would not grant cgroup write or cross-UID signal authority.
**U:** full compiled OEM policy, actual hierarchy, kernel support, migration
protection, failure propagation and completion observation on supported builds.

**S:** `PhantomProcessList` discovers native descendants through cgroup membership,
tracks death observations and trims excess/stale processes; `PhantomProcessRecord`
has killed/zombie timeout states and invokes process/group killing. This is
additional system lifecycle policy, not a PDVA-owned descendant registry or a
promise of immediate termination. It cannot be replaced by trusting child PIDs
reported by a compromised worker.

### Public requests and management death

**S:** `Process.killProcess` is a signal wrapper subject to kernel restrictions.
Linux `check_kill_permission` checks credentials/capability and the security hook;
ordinary management does not acquire cross-isolated-UID kill authority because
it owns the APK. pidfd signaling still checks authority. A pidfd stabilizes an
identified target; it neither adds descendants nor grants CAP_KILL.

**S:** `ActivityManager.killBackgroundProcesses` is a public, permission-gated
request limited to one's own package on recent Android. AMS passes an OOM-adj
threshold to `killPackageProcessesLSP`; that method filters identity/package
and importance before killing. An active bound isolated worker cannot be assumed
eligible. The inspected matching uses app IDs/dependencies, so package ownership
must not be assumed to include every isolated UID. This API returns no tree-empty
receipt and permits restart. `killUid` and `forceStopPackage` require privileged
permissions; root/shell/ADB variants do not satisfy PDVA's production contract.

**S:** `ActiveServices.bringDownServiceLocked` schedules unbind/stop callbacks
and updates lifecycle state. `killServicesLocked` removes the dying client's
service connections. These are real framework actions, but requesting stop or
unbind is not an immediate acknowledged tree kill. The `ServiceConnection`
contract says disconnection commonly follows process death and that the binding
can remain active for reconnection. Neither it nor Binder death enumerates or
certifies the end of native descendants and retained capabilities.

**I/U:** system-owned cgroup tracking can outlive management, but management's
death removes its own timers/observations. The isolated service is a separate
framework process, so a native child's PDEATHSIG tracks its creating worker
thread, not the PDVA manager. Service callbacks that self-terminate are controlled
by compromised code. Exact last-binding removal, service execution/ANR timing,
framework cleanup failure and manager restart reconciliation remain unproved.
Restart must not infer cleanup from a missing local session or reuse a stale PID.

## Enforcement assessment

All rows require Android evidence beyond Linux semantics. No row alone proves
revocation of references held outside the processes it actually terminates.

| Mechanism and owner | Ordinary-app use / compromise resistance | Descendants, manager loss, retained capabilities and gap |
|---|---|---|
| Isolated UID, SELinux, platform seccomp: kernel/system | Legitimate isolated service; restrictions remain after worker compromise if platform enforces them | Constrain inherited authority, not a lifetime lease; remain after manager loss. Passed FDs can remain usable. Exact OEM policy U. |
| STOP/KILL Binder request, onUnbind, owner-death callback, Java lease: worker | Present harness; cooperative only | Hostile native code may ignore/replace logic. No tree proof; manager death callback can be ignored. Raw capabilities survive. |
| `alarm`, PDEATHSIG: calling child plus kernel | Useful fixed-fixture backstops; hostile code can cancel/change them | PDEATHSIG is cleared in a forked child, can be set to zero, and relates to the creating thread. Alarm is not a descendant lease. No manager-death or FD-tree guarantee. |
| waitpid/waitid: kernel child relation | Worker can reap its direct child; manager does not parent the isolated service | Direct-child exit/reap does not establish absence of grandchildren. A subreaper improves orphan observation only where it is an ancestor; not a kill boundary or Android permission grant. |
| SIGKILL/pidfd: kernel credentials and LSM | Cannot be caught, but sender must be authorized; pidfd availability/permissions U | Identity-safe signaling is useful for an owned child, not a process-tree handle. Manager death ends its controller. Waiting for actual exit remains necessary. |
| POSIX group/session kill: authorized sender | Same-UID tests possible on Linux; no new cross-UID authority | setsid/setpgid can change membership. No tree/FD guarantee; stale numeric group identities unsafe. |
| Android cgroup kill: system_server/kernel | System uses it; no reviewed public app-owned control/receipt | Credible inherited-tree cleanup even after detachment, conditional on membership/kernel/path. Independent of manager; trigger, timing, failure acknowledgment and residual capabilities U. |
| Phantom trimming / low-memory and background policy: system | Platform lifecycle, not app-selected containment | No per-instance guaranteed deadline, complete inventory or PDVA resource budget. System may kill manager too. |
| Hard rlimits installed before compromise: kernel | Unprivileged code can lower its hard ceilings; cannot freely raise them again | Real constraints, not all cooperative. CPU/AS/NOFILE generally per process; NPROC is real-UID scoped. Fork multiplies some budgets; sleeping evades CPU deadlines. No wall/tree/total-disk guarantee. |
| Additional irreversible seccomp filter: kernel after trusted setup | Linux no_new_privs path can restrict syscalls without root; AOSP lists seccomp/prctl. Android end-to-end U | Could prohibit creation or constrain it after trusted setup, including exec inheritance. Requires thread synchronization, ABI/flag policy and no preexisting descendants. Does not itself solve termination authority or FD revocation. Not implemented/adopted. |
| Broker epochs and bounded requests: management | Can independently reject future operations if all access goes through trusted broker | No revocation of raw FDs/mappings/copies already issued. Manager restart needs durable session/revocation reasoning. Broker redesign requires separate review/approval. |
| cgroup delegation, namespace supervisor, ptrace, root/shell force-stop | No complete ordinary-production-app route established | Do not import Linux workstation privileges. Same-UID supervisor is not automatically protected from hostile peers; different UID loses ordinary signal authority. |

Linux `PR_SET_PDEATHSIG` source explicitly accepts zero; fork resets the field.
The [manual](https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html)
also documents creating-thread death, setup races and exec credential-transition
exceptions. These observations falsify treating it as an immutable descendant
lease; they do not imply an actually executed escape test in this PR.

Hard limits and seccomp deserve separate treatment from cooperative timers:
once a correctly installed kernel restriction is irreversible to the worker,
arbitrary code cannot simply ignore it. But the current launcher applies its
CPU/core limits only to the fixed executable child, not to the whole isolated
service. It sets PDEATHSIG and an alarm; the arbitrary-code threat model can
change those. Its CLEAN field follows a successful direct-child reap. Its wire
identity/context/FD fields originate in the child. These are scoped synthetic
test observations, never authoritative statements about a hostile descendant tree.
No production correction is made because the existing fixture's stated scope
already distinguishes these limits.

### Resource exhaustion

Bounded startup allocation and PR #13's reservation plan constrain a reviewed
startup path, not allocations/syscalls made after native compromise. Hard
RLIMIT_AS can constrain an individual process's address space, but is not total
tree RAM; RLIMIT_CPU is CPU time, not elapsed time; RLIMIT_FSIZE does not provide
a total storage quota over multiple files. An inherited writable disk FD is
authority beyond a QEMU logical-size check unless an independent mechanism bounds
it. Process/thread counts, Binder queues, mappings, CPU, memory and disk need
separate accounting and exhaustion behavior. No stress/fork-bomb test is proposed.

Android 17 [documents app memory limits](https://developer.android.com/about/versions/17/behavior-changes-all#app-memory-limits).
The pinned `MemoryLimiter.md` and Java implementation describe system-controlled
memory.high/swap policy, state-dependent limits and a delayed kill path (30 s
constant), with vendor configuration and enable/disable conditions. This is not
a universal PDVA-selected hard memory budget or an immediate lease. Descendant
accounting, installed configuration and interactions with isolated UIDs remain U.
The documented ADB adjustment commands are test privileges, not app authority.

## Bounded Linux negative-control specification — NOT RUN

This Windows host has no installed WSL distribution (confirmed outside the
sandbox after an initial access denial); Docker and a host C compiler were not
found on PATH. Windows/NDK compilation would not establish Linux fork/wait
semantics. No Linux runtime was installed, remote job dispatched, Windows native
test substituted or antivirus setting changed. For this environment, safely
executed real Linux controls were not practical. This PR therefore contributes
new exact-source evidence and the following test specification, not unvalidated
process-execution code or passing test results.

A future Linux implementation must have an independent controller outside each
tested subtree, use one private temporary directory, no network, fixed payloads,
at most three descendants, hard CPU/address-space/FD/file/core limits, a short
per-case deadline and a whole-run deadline. Each synthetic descendant must arm
its own independent expiration immediately after fork and again where needed
across exec; timers are not inherited by fork. Never cancel that safety expiration
in a control about canceling a *different* cooperative mechanism. Synthetic
expiration is test safety, not hostile-code containment evidence.

Before releasing any child from a handshake, the controller must own an identity
handle for it, preferably pidfd received/created without a PID-reuse race. A
subreaper can collect orphaned known children on Linux. Cleanup must independently
terminate each registered survivor by verified handle, observe exit and reap all
adopted children; never enumerate/kill arbitrary host PIDs. Plain killpg controls
must keep their owned group leader alive/unreaped through signaling to prevent
reuse. Failure to register identity, expiration, unexpected exit, timeout, missing
output, observation loss or uncertain cleanup fails the case and stops further
adversarial cases. Controller death is a separate safety fault; descendants'
independent expiration still applies. Capture exact statuses and named assertions.

| P: fixed scenario | Positive setup and deliberate false assertion | Required distinguishing observation, then verified cleanup |
|---|---|---|
| Cooperative direct child | Fixed exec returns 42; assert wait/reap records 42 | Exact exit and single reap, not generic nonzero/signal. |
| Unexpected crash | Fixed child raises SIGABRT with core dumps disabled; assert ordinary exit | Exact WIFSIGNALED/SIGABRT rejects ordinary-exit assertion; must not count unrelated crash as success. |
| Ignored TERM / timeout | Child acknowledges installed SIGTERM ignore; assert TERM implies exit | Same pidfd still live after TERM plus bounded challenge reply; controller SIGKILL then exact reap. Timeout alone is not evidence. |
| Parent death with PDEATHSIG | Child arms SIGKILL and acknowledges parent check; kill only owned parent | Positive direct child receives SIGKILL; compare a grandchild whose PR_GET_PDEATHSIG is zero. Grandchild must answer after parent reap. |
| Worker cancels PDEATHSIG | Fixed child clears only PDEATHSIG, leaves separate expiration intact | Parent dies; registered child answers bounded challenge afterward. Reap child via controller, not claimed parent cleanup. |
| Direct reap with surviving grandchild | Known grandchild registers before parent exits 42; assert reap means tree empty | Parent status 42 plus grandchild post-reap response and live identity falsify tree-empty assertion. |
| Detached/double-fork child | Fixed three-process topology; detached child acknowledges new SID/PGID before signal | Old owned group killed, detached known child responds; explicit cleanup. Does not test escaping a cgroup. |
| Duplicate/inherited FD and mapping | One-page synthetic file; duplicate/inherit/map; close sender's copy | Exact synthetic read through surviving handle/mapping rejects universal-revocation assertion; close/unmap and reap. |
| Stale identifier | Reap known child; retain its pidfd, start a separate owned sentinel child | Old pidfd reports exited / signaling yields ESRCH; sentinel remains alive and responsive. No forced PID reuse or signaling numeric stale PID. |
| Manager loss / forged report | Controller survives tested manager; worker sends a false stopped record while remaining alive | Independent handle/challenge contradicts report. Controller cleanup succeeds; loss of observation is failure, never a pass. |

An actual future test runner must also deliberately mutate expected status/output
handling and prove rejection of missing/extra output, an unrelated signal,
timeout and a wrong exit status. These are intended falsifiers, **not observed
negative-control outcomes**. Existing deterministic wait-operation tests do not
exercise these real-process behaviors. Linux host success would still not be
stock Android runtime evidence or proof of the framework's cgroup path.

## Architectural disposition and missing evidence

The credible lead is system-enforced isolated authority plus Android-owned
descendant cgroup cleanup, possibly complemented by restrictions irrevocably
installed before untrusted native work. **No complete supervisor strategy is
established**: PDVA lacks a reviewed ordinary-app control and observation contract
that closes non-cooperative termination, manager death, exhaustion and retained
capabilities together. An extra same-UID helper is not automatically a trusted
external supervisor; an ordinary different-UID manager cannot assume it can kill
the isolated worker. No new helper, filter, broker or engine is selected here.

Before a positive lifetime claim, evidence must establish:

1. Exact supported stock builds: installed UID/domain/filter, cgroup membership
   across fork/exec/detachment, denied migration, and available observation APIs.
2. An ordinary-app trigger for hostile-worker termination, with bounded failure
   handling and independently verifiable completion for all possible descendants.
   Binder death and successful public stop/unbind are insufficient evidence.
3. Management death/restart, loss of the final binding, multiple bindings,
   worker crash, framework failure paths, stale identifiers and no reuse of old
   session resources until revocation is established.
4. Every retained/forwarded FD, mapping and Binder capability; which references
   die with the subtree and which are outside it. Prove future-access rejection
   separately from data already disclosed and from physical resource release.
5. Kernel-enforced process/thread/resource budgets compatible with the selected
   runtime, and fail-closed behavior under bounded exhaustion and observation loss.
6. If considering an additional filter: trusted installation order, all existing
   threads, clone/clone3 and ABI coverage, exec inheritance, no preexisting escaped
   capabilities, Android syscall availability and QEMU compatibility. Separate
   architecture/TCB review is required before adoption.

This blocker prevents promoting QEMU compilation, TCG controls, the PR #12 FD
reader, PR #13 reservation planner or PR #14 startup witness into a containment
claim. Their pins and implementation are preserved. It does not invalidate their
scoped build/parser/startup evidence or close all future user-space alternatives.
Do not weaken the isolation contract, redesign PDVA or begin complete-guest work.
Any material architecture change needs an ADR and Tony's explicit approval.

## Validation and publication boundary

Only research Markdown and its index are changed. Source downloads remain ignored
reference material; no source is compiled/imported, no new runtime or build
dependency is adopted, and no binary/proprietary asset is added. The source ledger
records reference licensing and its limits, not redistribution/adoption approval.

Local Python 3.12.14 validation: foundation checks passed (88 files, 50 Markdown
files, 54 requirements, two ADRs); harness manifest/source authority checks
passed; repository regression suite **138 tests, OK, four existing Windows
skips** (134 executed passes). Markdown targets, requirement/ADR references,
UTF-8 text, prohibited artifact/secret markers, regular file modes and whitespace
were checked. The full three-file change was reviewed against the exact base.
No Android rebuild is claimed for this documentation-only change. New Linux
process controls and all Android physical outcomes remain **NOT RUN / Unknown**.

Hosted CI for this candidate is **pending/unobserved at publication**. After publishing one focused
PR, verify only PR identity/branch/exact head/base if immediately available, then
stop without querying Actions, checks, reviews, comments, bots or mergeability.
