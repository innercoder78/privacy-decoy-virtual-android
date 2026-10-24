# Gate 0: Android 17 Memory Limiter and isolated-worker resources

Review: **2026-10-24, America/Fortaleza; Windows x86_64; desktop source research.**
**Gate 0 Unresolved; Gates A–G Not reached. ADR-0001 Accepted; ADR-0002 Proposed.**
Scope: ordinary installed-app authority, PDVA-REQ-002–006, 009–015, 036–045,
048 and 054. No engine, guest, new memory manager or production design is adopted.

## Result and evidence boundary

**Source finding:** an ordinary isolated service is not automatically exempt from
Memory Limiter. Its own framework process record, actual isolated UID and PID
feed the limiter; its own computed process state selects the limit. The traced
normal binding calculation transforms a TOP client's contribution into BOUND_TOP,
which receives the visible class. Foreground-service and bound-foreground-service
states receive the nonvisible class. Thus neither “all workers are nonvisible”
nor “a foreground manager gives every worker TOP and its budget” is supported.

**New correspondence blocker:** live Android 17 r1 and `android17-release` resolve
to the same framework commit, but that commit does **not** implement the current
website's system-partition, bounded-interval configuration contract. The website
also disallows app allowlists, while the release Java contains a specific platform
service exemption. Preserve both observations; do not substitute another branch,
declare r1 compliant/noncompliant from this limited review, or claim installed
OEM behavior. **STOP the inference from current documented tiers to active r1
or device limits.** The worker's conditional source classification is established;
its effective installed numeric limit remains **UNKNOWN**.

This extends the resource gap in [worker containment](gate-0-worker-containment.md),
not its lifetime/security conclusion. Read with the existing
[platform authority](gate-0-platform-authority.md),
[userspace sources](gate-0-userspace-vmm-sources.md),
[harness](gate-0-isolated-worker-harness.md),
[native launch](gate-0-isolated-native-launch.md),
[lifetime](gate-0-android-lifetime-authority.md),
[exceptions](gate-0-android-lifecycle-exceptions.md),
[revocation](gate-0-capability-revocation.md),
[complete guest](gate-0-complete-android.md),
[fixture proposal](gate-0-isolated-qemu-proof.md) and
[recovery](gate-0-research-recovery.md) records. Source facts below are not device
observations; conditional implications and hypothetical quantities are labeled.

## Live baseline and procedure

GitHub main metadata and `git ls-remote` independently agreed on
`555ec23aa6691ba54a8074a114a5bcda04135e12`. PR #34 is merged at that SHA, with
head `bec9b98f7d457196179d32d00ae0b673e9191da1`; the local prior head and main
have identical trees. The all-open-PR query returned zero, so there were no open
heads/bases, diffs/files, checks/jobs/logs, reviews/comments/threads to reconcile.
[Exact-main run 40067616976](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40067616976)
and its foundation job `120794059919` and offline-image-windows job
`120794059683` succeeded. Both existing job logs were retrieved and inspected;
their checkout identity is the exact baseline. These are prior hosted controls,
not this investigation's Android tests. GitHub Status reported All Systems
Operational. Foundation applies to these Markdown changes; Android and QEMU
workflow path filters do not select them. Unrun workflows are not passes.

Requirements, both ADRs, governance, gates, acceptance/provenance rules, evidence
index and required prior records were reviewed. History, dependency/native
inventories, workflows and tracked modes were inspected. Initial tracked tree
was clean; one worktree, no stashes, all 127 tracked files mode `100644`.
Existing branches and ignored assets were preserved. No applicable AGENTS.md was
found. The historical repository remains read-only. This branch starts at main.

Procedure: resolve release refs through public Gitiles commit JSON; retrieve
selected files at the full SHA with `?format=TEXT`; base64-decode without newline
rewriting; inspect the named methods, callers and XML schema. Compare official
current documentation and CDD separately. Follow UID/PID registration, service
binding, process-state notification, JNI attribute lookup and kernel accounting.
Use existing local Python for repository checks. No upstream code was executed.
Initial sandbox network requests failed; approved public HTTPS/Git operations
succeeded. Web-reader JSON failures were retrieval limitations, not upstream
absence. Old guessed OomAdjuster/ProcessStateRecord paths and guessed test-data
directories returned 404; actual `am/psc` implementation and XSD were located.
No test XML fixture or installed OEM XML was obtained; the release Markdown XML
is an illustrative example, not a deployed configuration.

## Immutable sources and release mismatch

Framework **F = `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`**, tree
`908a2ce43657451526181a33ee94fc688add3117`, independently resolved from both
`refs/tags/android-17.0.0_r1` and `refs/heads/android17-release`.
System/core **C = `545d2487e38192a2ce25040897ced877cf6b4f53`**, independently
resolved from `refs/tags/android-17.0.0_r1`. These are reference release identities,
not an OEM build manifest. Full immutable file links and selected byte receipts
appear below. Linux v6.12 is a semantic reference, not an asserted host kernel.

| Topic | F source observation | Current official documentation / limit |
|---|---|---|
| Configuration location | `MemoryLimiter.CONFIG_PATH` is `/vendor/etc/memory-limiter-config.xml` | [Memory Limiter website](https://source.android.com/docs/core/perf/memory-limiter), updated 2026-10-20 UTC, specifies `/system/etc/memory-limiter-config.xml` |
| Tier selection | `getConfiguration` chooses greatest eligible minimum, inclusive; no maximum field in XSD or selection code | Website uses inclusive floor/exclusive ceiling, including `maximumAllowedMemTotal` |
| Numeric values | Release Markdown illustrates 8192/4096/4096/4096 MiB at minimum 14336 MiB and 6144/3072/3072/3072 at minimum 10240 MiB. Java test default is 4096/2048/2048/2048 MiB and explicitly not production-qualified | Current five-tier table below differs; no equality to r1 XML or installed policy established |
| Enablement | Feature enable flag, system-server context, existing valid matching XML; missing/unmatched configuration disables; invalid/unreadable present XML throws. JNI additionally needs usable cgroup attributes | Website specifies cgroup v2 plus memory controller. Installed flags, controller activation and configuration remain UNKNOWN |
| Exemptions | UID readiness check excludes values below 10000; configured on-device sandboxed inference package enters `mExemptList`. Ordinary isolated UID is not an exemption | Website rejects app allowlists; [CDD 8.6 C-0-1](https://source.android.com/docs/compatibility/17/android-17-cdd#86_app_memory_limits) prohibits bypass methods/allowlists/policies. This is an OEM obligation, not permission for PDVA to use a source exception |
| Cached state | Leaves memory.high unchanged, requests unlimited swap | Website describes freezing and maximal reclaim. Do not infer a fresh visible allowance or guaranteed residency |

The CDD describes limits per individual app process across its allocations; it
does not give PDVA an allocation reservation, an isolated-worker exemption or a
sum-of-process-budgets guarantee. The website's general no-allowlist statement
and its developer ignore/manual commands must be read in their separate
production versus diagnostic scopes. None was run or proposed as a remedy.

## Enforcement trace

1. **Identity:** `ActiveServices.bringUpServiceLocked` uses isolated creation;
   `ProcessList.newProcessRecordLocked` allocates the isolated UID.
   `addProcessNameLocked` creates/finds `UidRecord(proc.uid)` and calls
   `ProcessRecord.setUidRecord`. That forwards the actual UID and package to
   `MemoryLimiter.Limiter.setUid`; `ProcessRecord.setPid` forwards the PID.
   This is not the manager's UID or a package-wide pooled allowance.
2. **State:** `ProcessStateController` constructs `OomAdjusterImpl`.
   Its connection computation and `computeServiceHostOomAdjLSP` examine the
   client's state and binding flags. A normal TOP contribution becomes BOUND_TOP;
   the host takes the more important applicable contribution. Pending attach,
   other connections, activities and lifecycle inputs matter. `BIND_WAIVE_PRIORITY`
   skips this normal promotion; `BIND_NOT_FOREGROUND` and
   `BIND_IMPORTANT_BACKGROUND` can lower its propagated state. Scheduling-group
   priority, OOM adjustment and process state are distinct quantities.
   `BIND_IMPORTANT` or `BIND_ADJUST_WITH_ACTIVITY` is not a memory-budget API.
3. **Notification:** `OomAdjuster` applies state and calls its AMS callback;
   `ActivityManagerService.OomAdjusterCallback.onProcStateUpdated` calls
   `ProcessRecord.onProcStateUpdated`, then the per-process limiter. A changed
   limit class is queued to the handler and JNI `configureLimit`, not atomically
   granted by the binding call. Backgrounding can remove the visible-class
   contribution. Unbinding or manager death removes connections and causes
   lifecycle/OOM recomputation; exact final state and teardown timing are UNKNOWN.
   The separate experimental `ProcStateController` has TODO evaluation methods
   at F; it is not used here as evidence of a completed alternative algorithm.
4. **Cgroup:** JNI asks `CgroupGetAttributePathForProcess("MemEvents", uid, pid)`.
   C's task profiles map this to memory-controller `memory.events`.
   `ProfileAttribute::GetPathForProcess` builds the v2 UID/PID path; for app UIDs
   the default root yields `/sys/fs/cgroup/apps/uid_<uid>/pid_<pid>`.
   `createProcessGroupInternal` makes system-owned directories, activates
   controllers as applicable and writes the initial PID to `cgroup.procs`.
   This is a memory-accounting group, not necessarily the similarly named CPU
   scheduling group. Controller configuration is optional in C's JSON and OEM
   overrides/creation variants require actual build correspondence.
5. **Enforcement:** JNI writes `memory.high` and `memory.swap.max`, watches
   `memory.events` with inotify and polls qualifying targets. Missing paths skip
   the current application attempt; writes can fail. Monitor and swap-monitor
   flags and runtime disable-limits/disable-kill switches affect behavior.
   Java names/comments mentioning swap.high do not change the actual native
   swap.max pathname. Generated flag values for an installed build were not
   established. Source presence alone is not proof of successful enforcement.

The normal state map is visible for TOP, BOUND_TOP, IMPORTANT_FOREGROUND and
TOP_SLEEPING; nonvisible for FOREGROUND_SERVICE, BOUND_FOREGROUND_SERVICE,
IMPORTANT_BACKGROUND, TRANSIENT_BACKGROUND, BACKUP, SERVICE, RECEIVER,
HEAVY_WEIGHT, HOME and LAST_ACTIVITY. PERSISTENT/PERSISTENT_UI are unrestricted
in this map, not states an ordinary app may assume. Cached states keep the old
high threshold and release the swap restriction. UNKNOWN/NONEXISTENT do not
supply a new usable limit. These mappings are independently corroborated by F
Java and the official state table; their runtime input remains device-specific.

### Accounting, descendants and termination

**Kernel source semantics:** memory.high induces reclaim/throttling and can be
exceeded; crossing it alone does not invoke the kernel OOM killer. memory.max is
a different hard memory control. memory.swap.max restricts swap-out capacity;
it is neither extra DRAM nor guaranteed available swap. Global pressure, LMKD,
kernel OOM, allocation-specific failure and Android lifecycle kills are separate
failure paths. Java heap limits are separate again.

At F, native `MemoryStat.anonMetric` is **anon + shmem**; the polled combined
metric adds `memory.swap.current`. The configured combined threshold is high
plus swap. After a high event, source can add a **100 MiB** high margin and uses
**10 MiB** hysteresis for returning to event monitoring. A qualifying combined
overage causes the Java callback to release limits and queue a kill request
after **30 seconds**, optionally triggering profiling. Runtime kill-disable and
profiling flags matter; this is not an unconditional exact-deadline termination
guarantee, nor a public tree-empty acknowledgement. The native metric and
event/poll conditions are more precise than interpreting “over high = killed.”

Forked descendants inherit cgroup membership; ordinary exec/setsid does not
grant migration authority. Consequently a native child remaining in the worker's
group contributes to that group's accounting; it does not acquire a fresh
MemoryLimiter allowance merely by having another PID. This is a **conditional
source implication**, not a measured hostile-descendant result. No reviewed
ordinary-app authority delegates cgroup migration or quota modification. Existing
containment evidence separately covers system cleanup and phantom-process policy;
do not turn memory accounting into proven lifetime containment.

Memory charges attach to backing pages and can be shared across processes;
moving a process does not move its existing charges. Group usage is not RSS/PSS
summation. Guest RAM reservation, committed/resident guest pages, TCG code and
metadata, shared backing, file cache, device buffers and manager rendering need
separate accounting. Two virtual aliases of one TCG backing object are not two
unique physical allocations. A shared mapping's size does not identify which
group bears all its charges. A host memory limiter does not inspect guest
process identities inside a hypothetical emulated Android system.

## PDVA role-to-enforcement matrix

Every runtime row is **NOT RUN**. “Visible” below means the limiter's state class,
not merely that the APK displays pixels somewhere.

| Role | Identity and accounting | State / transitions and applicable limit | Remaining falsifier |
|---|---|---|---|
| A. Visible manager | Ordinary app UID, own framework PID/group; owns its UI allocations | Actual TOP maps to visible. Leaving foreground can change class; cached retains prior high. No guarantee of survival | Exact installed state/config/charges and global-pressure behavior |
| B. Bound isolated worker | Separate allocated isolated UID and PID; own framework group. Current `Session` uses application context, `bindIsolatedService`, only `BIND_AUTO_CREATE`, unique instance; manifest has isolatedProcess true | On traced normal completed binding with TOP manager, BOUND_TOP contribution gives visible class, not TOP. Manager background/death or unbind removes that premise; other state inputs decide outcome | Actual state and high/swap values across those transitions; no installed numeric limit established |
| C. Trusted isolated diagnostic, dormant | Diagnostic is not a privileged exemption. An executable launched by the worker inherits its UID/group; a separately framework-created isolated service would have its own record | Trust label does not select a class. Child follows hosting group's limits; separate service must establish its own state | No activation, new service, exemption or separate budget inferred from dormant code |
| D. Potential hostile native descendant | Same inherited UID/group unless an independently authorized migration occurs; native child is not automatically a new AMS app-process record | Shared group pressure/charges follow parent group's settings; detached POSIX session does not supply another allowance | Actual membership, shared-page charges, migration denial and cleanup remain physical UNKNOWN; no stress/fork-bomb test |
| E. Later separate guest backend | Hypothetical only; identity, launch mechanism, bindings and authority unselected | Framework-created service follows its own state; native descendant shares inherited group. Neither topology proves aggregate capacity | Need an explicit permitted topology and resource demand before assigning a number; no backend construction authorized |

For every role, effective ordinary-app budget observation is unresolved at runtime.
The current website explicitly supplies no assigned-limit runtime query API.
`ActivityManager.getMemoryClass/getLargeMemoryClass` describes the Java heap,
not this cgroup allowance; `MemoryInfo` is not a per-worker reservation. Native
proc/cgroup reads depend on actual DAC/SELinux/mount access and trustworthy
incarnation identification. No hidden API, shell dependency or readable-path
assumption is promoted into a shippable budget observer. Manager death also ends
its own observer; missing worker data is UNKNOWN, not evidence of free memory.

## Documentation-scoped resource envelope

All quantities below are **MiB**, with 1 MiB = 2^20 bytes and 1 GiB = 1024 MiB.
MemTotal is kernel-available physical RAM after carve-outs, not advertised RAM.
These are the current official website's five tiers, **not measured or proven
installed/r1 defaults**. Swap visible/nonvisible values happen to match per row.

| MemTotal interval (MiB) | Visible high | Nonvisible high | Visible swap.max | Nonvisible swap.max |
|---|---:|---:|---:|---:|
| [3200, 4800) | 2048 (2 GiB) | 1024 (1 GiB) | 1024 | 1024 |
| [4800, 6800) | 4096 (4 GiB) | 2048 (2 GiB) | 2048 | 2048 |
| [6800, 9216) | 5120 (5 GiB) | 3072 (3 GiB) | 3072 | 3072 |
| [9216, 14336) | 8192 (8 GiB) | 4096 (4 GiB) | 4096 | 4096 |
| [14336, 18432) | 10240 (10 GiB) | 5120 (5 GiB) | 5120 | 5120 |

The website describes no limiter limits outside those intervals. That does not
remove LMKD/global memory pressure or prove a bypass opportunity, and the r1
minimum-only matcher does not independently establish those outside-range rules.

Let **W** be a hypothetical worker cgroup resident charge relevant to high,
**M** the manager's corresponding charge, and **A+S** the native combined metric.
These are distinct, currently unmeasured quantities. For a policy row, compute
`headroom = selected_high - W`; negative headroom identifies reclaim/throttling
pressure, not automatic allocation failure. Compare A+S to the separately
configured combined threshold only where F's monitored algorithm applies.

| Documented tier interval | A=TOP / B=BOUND_TOP: separate high thresholds (M, W), MiB | A=TOP / B=nonvisible, MiB | Hypothetical W=3072 MiB: visible / nonvisible headroom |
|---|---|---|---|
| [3200, 4800) | (2048, 2048) | (2048, 1024) | -1024 / -2048 |
| [4800, 6800) | (4096, 4096) | (4096, 2048) | 1024 / -1024 |
| [6800, 9216) | (5120, 5120) | (5120, 3072) | 2048 / 0 |
| [9216, 14336) | (8192, 8192) | (8192, 4096) | 5120 / 1024 |
| [14336, 18432) | (10240, 10240) | (10240, 5120) | 7168 / 2048 |

The 3072 MiB value is an **arbitrary arithmetic witness**, not full-Android demand,
measurement or recommended budget. Reproduce each cell by subtracting 3072 from
the preceding tier's high value. Parentheses are independent thresholds, **not
additive reservations**. All roles compete with the OS and other apps; shared
pages must be counted once where appropriate. Meeting a threshold is insufficient
for latency, residency or a whole-system fit claim.

The earlier Linux fixture proposes 256 MiB guest RAM, 64 MiB TCG cache and a
768 MiB worker RSS/PSS ceiling. It is explicitly NOT RUN and is not Android 17.
RSS and PSS are separate metrics, neither equal to memory.current or anon+shmem
plus swap. Its small numbers cannot establish full-guest capacity. Full Android
working set, translator overhead, guest device state, graphics and host management
remain **not measured**. No minimum full-Android RAM figure is invented here.

## Independent negative controls and outcome

These are source counterexamples, **not executed Android tests**:

| Unsupported claim | Independent reason for rejection |
|---|---|
| Foreground service always gets visible limits | F state map explicitly assigns FOREGROUND_SERVICE and BOUND_FOREGROUND_SERVICE nonvisible |
| Top activity guarantees every worker TOP | Binding calculation maps TOP contribution to BOUND_TOP, with flag/connection/attach conditions; state is evaluated per process |
| Isolated UID is exempt | ProcessList registers the actual isolated UID; limiter readiness tests application UID threshold, not “isolated means exempt” |
| Large Java heap raises native cgroup budget | Heap APIs and the XML/procstate-driven JNI limit path are different mechanisms; no such link established |
| memory.high is a hard RSS ceiling | Kernel contract is throttle/reclaim; native accounting and later kill path are separate |
| One allowance proves whole PDVA residency | Thresholds reserve no physical pages or swap; separate processes still compete for shared device resources |
| Debugger/shell/exemption proves production feasibility | Diagnostic policy changes do not establish ordinary-app authority; CDD bypass prohibition and PDVA requirements exclude that remedy |

**Disposition: constrained, not globally falsified.** The ordinary-app/full-guest
hypothesis has no measured requirement to compare against an authenticated active
policy. A configuration whose required nonreclaimable working set exceeds its
actual nonvisible envelope may fail its declared latency/residency contract, but
the table alone cannot establish that failure. Visible management cannot be used
as a permanent allowance premise for a worker after its binding state changes.

**Smallest new proof:** an exact stock-build correspondence receipt joining the
shipped limiter/configuration, effective flags/controller hierarchy and worker
state transitions to independently observed effective high/swap and memory
charges. It must discriminate BOUND_TOP from nonvisible and account for inherited
native children without changing policy. This is a proof requirement, **not an
authorized phone procedure**. Physical acquisition/observation is NOT RUN and
must stop here; no repeat generic source survey, phone request, workload stress,
APK installation, ADB, privileged command, guest build or integration follows.
Any later workload feasibility proof separately needs preregistered measured
resource/latency requirements and the unresolved containment/provenance gates.

## Reproduction receipts, validation and preservation

Reference-only review: AOSP implementation/schema files retain their Apache-2.0
notices; kernel documentation retains its source terms. No upstream implementation,
binary, dependency, license grant or runtime is imported. Public text contains no
private identifiers, machine paths, local artifact hashes, Persona material,
credentials or raw logs. Temporary local receipts are not an independently
backed-up private archive; independent private retention remains unverified.

The following links identify the reviewed source paths; selected SHA-256 values
cover decoded upstream public bytes, not private machine artifacts. Existing
framework/source receipts are also cross-referenced by the
[containment ledger](gate-0-worker-containment-sources.md).

Kernel reference: [Linux v6.12 cgroup-v2 documentation](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/Documentation/admin-guide/cgroup-v2.rst),
sections Organizing Processes and Threads, Memory Interface Files and Memory
Ownership. The immutable content was checked against the retrieved v6.12 text.
For reproduction, inspect the complete methods named above, not only string
matches. Relevant F anchors include MemoryLimiter lines 574–608, 921–943 and
1081–1183; OomAdjusterImpl 1884–2186; OomAdjuster 2438–2456;
ProcessRecord 695–734 and 1621–1626; AMS 20438–20467; JNI 298–328,
441–548 and 841–851. Line anchors supplement immutable identities, not runtime proof.

Local checks used existing Python **3.12.14**:

| Check | Observed result |
|---|---|
| `validate-foundation.py` | PASS: 128 files, 77 Markdown files, 54 requirements, two ADRs; local file links and modes included |
| `validate-harness.py` | PASS, source/manifest authority only |
| `test-repository-validation.py` | 141 total; 137 passed, four existing Windows/platform skips |
| `test-desktop-readiness.py` | 27 passed |
| `test-offline-image-inspect.py` | 45 passed, synthetic inputs only |
| Whitespace and review | `git diff --check` passed; complete two-file change reviewed for modes, source claims, links, dependencies and public-data hygiene |

No new tests or dependencies were needed for this documentation change. Skips
are not passes. No native Android, diagnostic, guest, VM engine or phone test ran;
no installed memory limiter or physical resource measurement was performed.
New hosted CI is **pending/unobserved at publication**. This single evidence PR
is pending independent review and merge; publication ends after one immediate
PR identity/head/base check and one native conversation-association verification.

| Immutable public source | Decoded SHA-256 |
|---|---|
| [services/core/java/com/android/server/am/MemoryLimiter.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/MemoryLimiter.java) | `6713fd65cfc4bab10069734d09b2fb46c884c27ec0fee76f553295a31f733dc0` |
| [services/core/java/com/android/server/am/MemoryLimiter.md](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/MemoryLimiter.md) | `ab6da0575c1a0118f0f0dab5b49f4dc146c1ce589d07632bd4ca590a45443d59` |
| [services/core/jni/com_android_server_am_MemoryLimiter.cpp](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/jni/com_android_server_am_MemoryLimiter.cpp) | `974c668c3d9a1e5e76bc58a5643e8e7b53070c1edadce9ef089c045040e9a569` |
| [services/core/xsd/memory-limiter-config/memory-limiter-config.xsd](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/xsd/memory-limiter-config/memory-limiter-config.xsd) | `993f23da0119481d3340a5c89a90d16967ed0012b6dc65f6d9fb894eeb44aa50` |
| [services/core/java/com/android/server/am/psc/OomAdjuster.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/psc/OomAdjuster.java) | `3e64883feb5dff1c259005cb509cd76fc68148960b1416079cf5f70d9bdfa337` |
| [services/core/java/com/android/server/am/psc/OomAdjusterImpl.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/psc/OomAdjusterImpl.java) | `3e160836e33f383e93aa2f09e270868ee9ed934607a9dcd688e88501af1d9676` |
| [services/core/java/com/android/server/am/psc/ProcessStateController.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/psc/ProcessStateController.java) | `51d5b0a0da21cada2a1925c675700f820102f02a5d7d4ae094a57df103f83925` |
| [services/core/java/com/android/server/am/psc/ProcStateController.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/psc/ProcStateController.java) | `e2c846c2f823f88558367b7e9a590a14abc4cc0fdefbfbf77dfdd47facc05e49` |
| [services/core/java/com/android/server/am/ProcessRecord.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessRecord.java) | `f4f07c1ba18fe28c66664c7300b9e5d22d5136358b136d3562aab401b0d616a0` |
| [services/core/java/com/android/server/am/ProcessList.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessList.java) | `96bfea0a32f822a04e46a16279100d5fdc718b909999df4962f2bd15c8ac55fc` |
| [services/core/java/com/android/server/am/ActiveServices.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActiveServices.java) | `bd27258e4fd4bacec2924fdd6366166104f5961c6600945ae2aedb0163aca7db` |
| [services/core/java/com/android/server/am/ActivityManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActivityManagerService.java) | `17923170a97fb001c3892ab4e0d71f9e249f9ea0b427a7aaf29916aae5208797` |
| [core/java/android/app/ActivityManager.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ActivityManager.java) | `b77a98e9aad8110436048ded1c86f36515fba9ac406703eaf21f297acfb7af02` |
| [libprocessgroup/processgroup.cpp](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/libprocessgroup/processgroup.cpp) | `61825c2354e9472b0f08ddd20bdcf415d27910e9549bc5f3744b7293b2d1d0ab` |
| [libprocessgroup/task_profiles.cpp](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/libprocessgroup/task_profiles.cpp) | `410c070bd06c3497f4f1784e4f387aeed45e1b4c5bc17c5b10ade3c75a5a6256` |
| [libprocessgroup/profiles/task_profiles.json](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/libprocessgroup/profiles/task_profiles.json) | `c7395e2366edc0292c8d8ecb2b19d9e71cf1ac451fe34c30d6029a9eba72f6dc` |
| [libprocessgroup/profiles/cgroups.json](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/libprocessgroup/profiles/cgroups.json) | `ab2ed667ff45958843fb0c6ee953a5512def0ae87470c4358aa9576a6a4b2e22` |
