# Gate 0: process histories cannot reconcile isolated-worker inventory

Review: **2026-10-28, America/Fortaleza; desktop/source-only, Windows x86_64.**
**Outcome: CONTRADICTED as a complete reconciliation authority; STOP this
candidate for replacement admission. Physical-test readiness: NOT READY — STOP.**
Gate 0 remains **Unresolved**; Gates A–G **Not reached**. ADR-0001 remains
Accepted and ADR-0002 Proposed. No production mechanism is implemented or adopted.
Scope: PDVA-REQ-002–003, 008–015, 035–037, 039–045, 048 and 054.

## Question and decisive new witness

Can an ordinary restarted manager combine `getHistoricalProcessStartReasons()`
(API 35+), `ApplicationStartInfo`, `getHistoricalProcessExitReasons()` (API 30+)
and `ApplicationExitInfo` to account completely for earlier bind/INIT/LAUNCH
attempts, including attempts missing from a restored local journal?

**Source observation:** at the Android 17 framework reference revision below,
`AppStartInfoTracker.addStartInfoLocked` (588–615) returns without storing the
record whenever `UserHandle.isIsolated(raw.getRealUid())` is true. This is an
unconditional isolated-UID exclusion in the inspected method, not merely a
small buffer, a missing permission, or a PID-query mistake. The service-start
caller does reach this tracker; independently named isolated instances still
have isolated real UIDs and are discarded. Requesting all records cannot recover
a record that was never retained.

**Inference:** the proposed pair cannot distinguish “no earlier worker” from
“an earlier isolated worker still exists but has no available start/exit entry.”
A live worker need not yet have any exit event, and its start is excluded here.
This does not prove that a particular worker survives Android's independent
manager-death cleanup; that timing remains UNKNOWN. It proves the histories
cannot certify the missing absence fact. Assuming cleanup already finished
would import the separate authority this candidate was supposed to provide.

The public [ActivityManager contract](https://developer.android.com/reference/android/app/ActivityManager)
also explicitly limits both APIs to recent ring-buffer history. Startup entries
may be incomplete. Zero `maxNum` requests matching retained information; it is
not an unbounded audit or live census. Even a future implementation that retains
isolated starts would still need a completeness/freshness contract.

The existing [exit-history witness](gate-0-android-lifecycle-exceptions.md#exit-history-negative-witness)
already rejects exit-entry-as-completed-kill. This investigation reuses that
disposition, checks its source chain, and adds the specific isolated-start
exclusion and combined-history failure. It does not repeat a broad lifecycle,
clock, boot-counter, journal-authentication or Binder-death survey. No synthetic
state machine is needed to reproduce an explicit source contradiction.

## Live preflight and preservation

GitHub's live main and an independent `git ls-remote` agreed on
`a982c3d5373543a77181a476ec9bd2f6c41dc35d`, the merge of PR #45. Local main
matched exactly. The complete live open-PR search returned **zero**: open
heads/bases, full diffs/files/modes, checks/jobs/logs, reviews/comments/threads
and PR dependencies therefore form an empty set. There is no intended open PR
to reuse. Relevant merge and harness source history were inspected; no merged
record adequately disposes of the isolated-start exclusion and combined candidate.

Initial state: clean tracked checkout, 138 tracked files, one registered worktree,
no stashes. Existing local/remote branches and ignored research/build/cache
directories were inventoried and preserved. No applicable AGENTS.md was found.
No reset, clean, restore, destructive overwrite, stash pop or force push occurred.
Direct sandbox Git networking failed; an approved read-only retry verified main.
No failure is counted as a successful source retrieval.

All three current workflow definitions and contribution/PR instructions were
read at this baseline. Foundation applies to the two proposed Markdown changes;
Android substrate and QEMU research path filters do not select them. Filtered
jobs are not passes. No new-PR CI result is inferred from older evidence.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational, page update `2026-10-28T17:09:26.328Z`.

Requirements, Gate 0, both ADRs, architecture, governance, acceptance criteria,
security boundaries, threat model, provenance policy and roadmap were consulted.
Inputs include the [readiness audit](gate-0-native-launch-readiness-audit.md),
[integrated decision](gate-0-integrated-feasibility-decision.md),
[diagnostic recovery](gate-0-diagnostic-recovery.md),
[Android lifetime authority](gate-0-android-lifetime-authority.md),
[capability revocation](gate-0-capability-revocation.md) and
[native-host incident](gate-0-native-host-antivirus.md). Their independent
security, artifact, enrollment and resource-closure blockers remain in force.

## Exact sources and reproduction

Framework repository: `platform/frameworks/base`, commit
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`, tree
`908a2ce43657451526181a33ee94fc688add3117`. This is the existing
[Android 17 reference pin](gate-0-worker-containment-sources.md), originally
resolved from `android17-release`. Fresh Gitiles commit metadata identifies a
2026-05-21 merge into `26Q2-release`. It is not a complete release manifest or
proof of correspondence to every Android 17 OEM image. API availability is a
host requirement, separate from PDVA's Android 17 guest target and minSdk 30.

All nine files were freshly retrieved by full commit with `?format=TEXT`,
base64-decoded without newline rewriting, and SHA-256 hashed. Table paths are
relative to that framework repository; links are immutable. All carry AOSP
Apache-2.0 source notices. These are reference reads, not imported implementation.

| File | SHA-256 of decoded bytes |
|---|---|
| [core/java/android/app/ActivityManager.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ActivityManager.java) | `b77a98e9aad8110436048ded1c86f36515fba9ac406703eaf21f297acfb7af02` |
| [core/java/android/app/ApplicationStartInfo.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ApplicationStartInfo.java) | `9023b6d211ae06efa50462e5f6938b6624bc62d00899e7eb7f48bd14a7b1baaf` |
| [core/java/android/app/ApplicationExitInfo.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ApplicationExitInfo.java) | `0bc54065c04f2d04f01f831ba7dcc1062f62d47b670caf3a295464dfa1e6e9ba` |
| [services/core/java/com/android/server/am/AppStartInfoTracker.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/AppStartInfoTracker.java) | `1b1539494ef520ca79db7241da94ca4fe943aa0b51d83dea9c4bff67d47dc2cc` |
| [services/core/java/com/android/server/am/AppExitInfoTracker.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/AppExitInfoTracker.java) | `4cb4c46bd10ad51ecc07adc011e14ab22fa58ded7cf5f6754e8144d4da9f3f29` |
| [services/core/java/com/android/server/am/ActivityManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActivityManagerService.java) | `17923170a97fb001c3892ab4e0d71f9e249f9ea0b427a7aaf29916aae5208797` |
| [services/core/java/com/android/server/am/ProcessList.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessList.java) | `96bfea0a32f822a04e46a16279100d5fdc718b909999df4962f2bd15c8ac55fc` |
| [services/core/java/com/android/server/am/ActiveServices.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActiveServices.java) | `bd27258e4fd4bacec2924fdd6366166104f5961c6600945ae2aedb0163aca7db` |
| [services/core/java/com/android/server/am/ProcessRecord.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessRecord.java) | `f4f07c1ba18fe28c66664c7300b9e5d22d5136358b136d3562aab401b0d616a0` |

Reproduce using any HTTPS client: append `?format=TEXT` to each exact URL, decode
base64 into bytes, hash those bytes and compare before reading the methods below.
For example, Python standard-library `urllib.request.urlopen(url).read()`,
`base64.b64decode(...)`, then `hashlib.sha256(decoded).hexdigest()` suffices.
Do not substitute moving branches for missing files. Read full functions and
callers; symbol matches alone do not establish control flow. No AOSP build or
execution is required for the exclusion witness.

The official mutable API pages were read on the review date:
[ActivityManager](https://developer.android.com/reference/android/app/ActivityManager),
[ApplicationStartInfo](https://developer.android.com/reference/android/app/ApplicationStartInfo),
[ApplicationExitInfo](https://developer.android.com/reference/android/app/ApplicationExitInfo).
Their immutable counterparts are in the table. Local original-source inspection
used the exact PDVA baseline, particularly Session.java, WorkerService.java,
LaunchResult.java, AndroidManifest.xml and launch.c; the readiness audit's
source identities/order remain applicable because these files are unchanged.

## Caller, creation, retention and return paths

**Source observations; runtime/OEM behavior is not measured.** AMS below means
ActivityManagerService, AS means ActiveServices, ST means AppStartInfoTracker,
ET means AppExitInfoTracker, PL means ProcessList and PR means ProcessRecord.

| Question | Exact path and finding | Disposition / limit |
|---|---|---|
| Ordinary-app access | ActivityManager's public start wrapper (4598 onward) calls AMS with null package and the caller's user. AMS start (10866 onward) and exit (10974 onward) reject isolated callers and enforce incoming-user/package access. Null package filters caller UID; own-package access needs no DUMP. `enforceDumpPermissionForPackage` (11089 onward) requires DUMP for another UID's package. | **SUPPORTED** for the non-isolated manager's own diagnostic history on the respective SDK levels. Not restricted to userdebug or privileged apps. No hidden API, shell grant or DUMP is proposed. Both APIs cannot be assumed on API 30–34 hosts. |
| Isolated starts | AS `bringUpServiceLocked` calls `handleProcessServiceStart` after a non-null `startProcessLocked` result (6373), before adding pending service state. ST fills a raw record (427–450, 517–538), then `addStartInfoLocked` discards isolated real UIDs (600–602). It also discards records during initial loading. | **CONTRADICTED** as isolated-worker start inventory. A ProcessRecord/start request is not successful service initialization, bind callback, INIT or LAUNCH. Failed/null process creation has no entry on this path. |
| Named instances | AS builds the component class name with the requested instance suffix (5130–5140); `getProcessNameForService` (939–959) derives a distinct name for the normal dedicated isolated case. PL allocates isolated UID and registers its package mapping (3536). | **SUPPORTED** framework name/UID distinction while records exist. Names come from app manifest/manager choice; they are not immortal incarnation certificates. None defeats ST's isolated-UID rejection. |
| Isolated exits | ET `obtainRawRecord` (1080 onward) copies PID, real/package/defining UIDs and process name from ProcessRecord. `addExitInfoLocked` (475–508) maps isolated real UID through `mIsolatedUidRecords` to package UID when mapping exists, then indexes package records. PL registered that mapping; ET's death handler removes it after insertion/update. | **SUPPORTED** conditional inclusion of isolated-process exit diagnostics in the ordinary manager's history. Failure/missing mapping is not repaired by merely knowing the package. This is not guaranteed per bind or per native descendant. |
| Exit versus kill decision | PR `killLocked` calls PL `noteAppKill` before primary signal/group cleanup (1396 onward). ET queues MSG_APP_KILL (312–330); `handleNoteAppKillLocked` (457–472) inserts or updates reason/status/timestamp without awaiting termination. A separate `handleNoteProcessDiedLocked` (402–434) can merge zygote/lmkd information. | **CONTRADICTED**: entry presence implies completed termination. **SUPPORTED**: a system-recorded kill decision exists on this path. More specific real-exit data can support only its identified process event, with provenance/identity qualifications; no generic public complete-cleanup bit is supplied. |
| Retention | ST capacity comes from `config_app_start_info_history_list_size`; insertion evicts oldest retained entries (1197 onward), without testing liveness. Persistence pruning removes records older than 14 days (1345 onward). ET uses `config_app_exit_info_history_list_size` and removes the oldest timestamp when over capacity (1474–1510). | Bounded diagnostics, not complete enrollment. No portable capacity is assumed; configured/OEM resource values are not an app guarantee. |
| Persistence/failure | Both trackers schedule normal persistence after 30 minutes, use AtomicFile and catch storage/load errors. Both skip early records while historical load is incomplete; unreadable files can finish loading with no old records. Package/user removal paths remove records. | Atomic file replacement is not synchronous per-attempt durable enrollment. Framework failure can lose unsaved information. Historical records can survive a restart without describing live state. No claim that framework restart always preserves or always kills workers. |
| Query shape | AMS returns separately queried lists; ST `getStartInfo` maps maxNum=0 to configured history size and filters by UID. ET filters by package/UID/PID and count; AMS also collects native tombstones. | No joint atomic snapshot, completeness watermark, issue sequence or current-membership guarantee. Larger limits, repeated calls and tombstone enrichment do not recover excluded or evicted starts. |

The SELinux boundary remains the existing
[pinned policy review](gate-0-worker-containment-sources.md): ordinary manager
uses framework Binder access; neither API grants cross-UID signalling, direct
system-history-file access or cgroup authority. AMS independently rejects isolated
callers. Installed OEM SELinux policy/flags are UNKNOWN here. No special policy
exception is needed or proposed for the ordinary manager's own public queries.

## Field provenance and identity limits

Android assigns/process-tracks PID, isolated UID, package UID and defining UID;
the trackers copy these from system-owned ProcessRecord/hosting state. Package
and process naming also reflect app declarations and manager-selected instance
names. A system copy of an app-selected name does not authenticate a durable
PDVA epoch or reconstruct a lost enrollment. Multiple live dedicated instances
can have distinct names/PIDs/UIDs, but PID and isolated-UID reuse remain possible.
The records expose no shared non-reusable start-to-exit capability or complete
attempt sequence, and ET itself guards updates for possible PID reuse (516 onward).

Startup state, reason/type, launch intent and available timestamps describe
startup diagnostics. Service reason is selected from service metadata; the intent
is derived from the start request and stripped of extras. Timestamp availability
depends on startup state; fully-drawn reporting depends on an app call. The API
also permits app-defined startup timestamps. Thus system storage does not make
all payload values independent of application behavior. These timestamps are
monotonic nanosecond startup measurements; exit timestamps are wall-clock
milliseconds. They are not interchangeable, a boot attestation or a reliable
cross-restart incarnation join. The pinned API notes older service launch-time
inaccuracy on API 36 and below. No clock research is reopened here.

Exit reason/status can reflect system kill decisions, observed process death,
zygote or lmkd reports; some reasons remain UNKNOWN. Memory samples, descriptions
and trace content are diagnostic context. `getProcessStateSummary()` explicitly
returns bytes provided through the app's `setProcessStateSummary`; it cannot be
an independent cleanup receipt. Similarly, a worker's claimed PID, resource list
or CLEAN response is not upgraded by embedding it in system-maintained data.
No claim is made that the isolated worker can invoke every ordinary-app mutation
API: caller restrictions still apply. Returned app-side object mutation is not
authority to change system-owned ProcessRecord identity.

Process restart can reuse names and later identifiers; app updates do not supply
a new history completeness certificate, and package replacement differs from
uninstall/user removal. Old local journal restoration does not atomically restore
or validate Android's separate diagnostic histories. Repeated/in-progress records,
multiple sources or ambiguous PID matches must not be treated as exactly-once
enrollment or counted as independent corroborating authorities. Specific OEM
update/restore behavior and installed-build correspondence remain UNKNOWN.

## Original PDVA failure-window matrix

The original manager uses a process-local ACTIVE guard, then binds a fresh named
worker, then INIT transfers canary/scratch FDs, shared memory and owner Binder.
Only before valid LAUNCH does it commit `uncertain_child=true`. A consistent
worker-supplied direct-child CLEAN result clears it before STOP and independent
worker termination. `launch.c` waits for its own direct child; this does not make
the manager that child's parent or certify worker/resource closure.

Every row is **source analysis/inference**, not executed Android fault injection.
The independent observer considered throughout is **AMS/ST/ET in system_server**,
with the limited diagnostic authority described above. It is independent of the
worker's reply, but is not an ordinary-app-accessible complete inventory oracle.
“Could remain” means not excluded by these observations; it does not assert an
observed Android leak or indefinite survival.

| Attempt/cut | What that observer can establish | What it cannot establish; could earlier authority remain? | Required fail-closed action |
|---|---|---|---|
| Bind begins; manager dies before worker identity | Possibly later mapped exit/kill diagnostics if a ProcessRecord and reporting path exist. | ST excludes the isolated start. No bind-attempt receipt or guaranteed entry for failed/incomplete starts; worker/pending start could remain unaccounted. | Keep admission closed despite empty histories; do not equate missing callback or entry with no issued attempt. |
| INIT transfers capabilities; manager dies or loses reply before enrollment | Framework process identity in an available exit record; no knowledge of this INIT transaction's committed resources. | INIT/FD transfer is not a history event. Worker may hold references although manager never sets initialized or durably enrolls it. | Preserve uncertainty and block replacement until separate exact-attempt/resource closure is independently established. |
| Valid LAUNCH executes; reply lost | Possible worker exit diagnostics; no guaranteed per-fork/exec native-child enrollment through these APIs. | Child completion, remaining child/tree authority and worker references are not proved. Original intact true marker helps lockout but does not restore missing inventory. | Retain the marker/uncertainty; absence of a child/worker exit entry never permits retry. |
| Direct child completes; worker keeps FDs/maps | A future worker event only; system history does not observe PDVA's direct-child wait predicate as a whole-scope receipt. | Successful child reap leaves worker resources. A child entry, if present, has only child scope. | Require independent worker and retained-capability closure; do not clear admission on child CLEAN. |
| Manager records cleanup before worker termination | ET may record a kill decision, potentially before actual death. | Cleared local marker plus history entry is not completed worker/group/resource cleanup. Earlier authority could remain. | Reject replacement based on apparent clear; retain unresolved closure. |
| Restart with missing, corrupt or rolled-back enrollment | Available retained diagnostic entries only. | No complete inventory/freshness proof. Corruption cannot default to clean; older authentic state can omit issued work. | Treat missing freshness as uncertainty; do not reconstruct “all ended” from the returned subset. |
| REC-05: authentic E1 restored, E2 absent, E3 considered | Any valid E1-specific inference remains about E1; an available E2 exit diagnostic may add limited context. | With E2 live under REC-05's explicit restore fault assumption, ST discards E2's isolated start and E2 need not have an exit entry. Histories fail to reveal the missing attempt. | Deny E3. E1 evidence and the combined histories do not discharge E2. |
| Histories missing, delayed, evicted, duplicated, inaccessible or ambiguously matched | At most the returned records' scoped diagnostics, or an access/error outcome. | No negative membership fact; polling cannot establish completeness, and ambiguous identity cannot clear an attempt. | Fail closed for every such outcome; do not turn count zero, timeout, maxNum=0 or duplicate agreement into absence proof. |
| Manager/worker death, framework restart, unusual service termination or update interrupts observation | A supported source path may later produce a record; prior persisted data may remain. | Every relevant attempt/event, synchronous persistence, all cleanup and snapshot freshness are not guaranteed. | Retain lockout until an independently qualified boundary resolves the uncertainty; restart/update alone is not that boundary. |

REC-05 expressly assumes old authentic storage can return without first ending
E2. This is a fault-model condition, not attribution of manager-storage access to
an isolated attacker or an observed restore exploit. If a concrete restore path
always independently ends all affected authority first, that invariant would be
separate proof. The history APIs supply no such invariant.

## Positive/negative witnesses, TCB and disposition

**Positive source control:** non-isolated eligible starts with loaded storage
continue beyond ST's isolation guard into insertion; the method is not a stub
that always returns no records. ET's isolated-UID-to-package mapping separately
shows that isolated exit diagnostics can be visible. These are reviewed source
branches, not executed Android positive controls.

**Negative witnesses:** isolated-start rejection; load-time omission and bounded
eviction without live-membership preservation; a kill-decision entry preceding
termination; and the existing resource-scope mismatch. These establish the scoped
candidate failure without pretending a desktop model proves Android behavior.

**SUPPORTED, exact limited fact:** the ordinary non-isolated manager can request
its permitted recent diagnostics, and the pinned server can supply system-owned
identity/kill/exit context for qualifying retained records. An independently
qualified actual process-exit observation can support that process's termination.
**CONTRADICTED:** these histories alone completely reconcile issued isolated
attempts or authorize replacement after lost/rolled-back enrollment.
**UNKNOWN:** installed OEM behavior, every crash/restore interleaving, latency,
per-event record delivery and actual resource closure. **STOP** dependent use of
this candidate as a cleanup/admission authority. This is not product-wide
impossibility and does not pass or fail all of Gate 0.

TCB for the limited observations includes the host kernel/Binder credentials,
system_server/AMS/process trackers, package mapping, reporting sources, storage,
installed configuration and manager interpretation. System-server independence
from a hostile worker does not imply completeness. Neither query terminates
anything or enforces descendant/cgroup completion. Neither enumerates inherited
or transferred FDs, mappings, shared-memory aliases, queued Binder references,
external recipients, outstanding operations or copied information. Even actual
worker death cannot revoke all external references or erase disclosed bytes;
the existing capability analysis applies unchanged. No new trusted supervisor,
privilege, security-policy redesign or implementation follows from this result.

**Smallest genuinely new reopening proof:** a supported-host, ordinary-app
contract and exact implementation that accounts for every issued/pending isolated
attempt despite manager-state loss, with non-reusable incarnation identity and
an independently verifiable current completeness boundary before replacement.
It must close the live-but-absent E2 case and retention/restart failures. Merely
removing the isolated-start filter, increasing buffer capacity, adding timestamps
or collecting more successful samples is insufficient. Whole-resource completion
still requires its own independently enforced and observed authority. None is
provided or adopted here; no follow-up implementation is invented.

## Validation, privacy and publication boundary

Executed locally with existing Python 3.12.14, without installing dependencies:

| Check | Actual result and limit |
|---|---|
| Foundation validator | **PASS**: 139 files, 87 Markdown files, 54 requirements, two ADRs; includes local Markdown-link and repository hygiene checks. |
| Harness source/manifest validator | **PASS**; no Android runtime or isolation claim. |
| Repository validation regressions | **PASS** for 137 tests; **SKIP** for four existing platform cases, 141 total. No assertion or skip rule changed. |
| Nine upstream decoded-byte identities and license notices | **PASS**: all nine table hashes match retrieved files, all nine Apache-2.0 notices checked. Identity checks are not runtime tests. |
| Original Session, WorkerService and LaunchResult correspondence | **PASS**: local LF-normalized bytes match exact baseline Git blobs and the prior readiness-audit hashes. |
| Full intended diff, local references, whitespace, modes and public-data review | Two Markdown files only; regular `100644` text, no source/dependency/workflow changes. |
| Android fault injection, phone/emulator/guest/native-launch runs | **NOT RUN**; all installed-build lifecycle/resource outcomes remain **UNKNOWN**. |
| New-PR hosted checks | **NOT RUN locally / unobserved at publication**; no inherited or filtered pass. |

The initial `python` PATH alias could not run; the existing bundled interpreter
completed the checks above. No failed invocation is counted as a test pass.
The candidate is **CONTRADICTED by source**, not an executed Android test FAIL.
Source review is not an Android runtime test. No phone, USB, ADB, APK installation, emulator, guest,
native-launch activation, native binary build or security-policy change occurred.
No dependencies or opaque binaries were added. Synthetic lifecycle/model tests
are **NOT RUN**, deliberately unnecessary for the explicit source falsifier.

Only this original analysis and its evidence-index entry are intended for public
publication. Upstream source remains reference-only temporary text; hashes/links
permit independent retrieval. No confidential paths, machine identifiers,
incident samples, signing material, private data or third-party product comparisons
are included. Existing licensing and security-incident prerequisites remain
unresolved; reference licensing does not constitute runtime adoption or a new
repository distribution license. Temporary source copies are locally retained,
not independently backed up; no private incident backup is re-attested.

Publication is exactly one branch and one evidence PR, followed by native chat
attachment and one association verification, then STOP without polling checks,
jobs, status, reviews or mergeability. New-PR hosted results are unobserved at
publication. A publication/association failure must be reported as UNPRESERVED
pending recovery of that same branch/PR/association; never create a duplicate.
Independent review and merge remain separate from this evidence submission.
