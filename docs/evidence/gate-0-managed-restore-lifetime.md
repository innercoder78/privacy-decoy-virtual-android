# Gate 0: managed application-data restore and isolated-worker lifetime

Review: **2026-10-28, America/Fortaleza; desktop/source-only, Windows x86_64.**
**Result: the examined backup paths do not establish a way to restore the old
private E1 journal under the current harness contract. They also do not establish
an independent all-worker termination boundary.** Physical native-launch readiness
remains **NOT READY — STOP**. Gate 0 **Unresolved**; Gates A–G **Not reached**.
ADR-0001 remains Accepted and ADR-0002 Proposed. Scope: PDVA-REQ-002–003, 008–015,
035–037, 039–045, 048 and 054. No recovery mechanism is adopted.

## Objective, baseline and preflight

Determine whether a legitimate Android-managed restore can replace earlier
manager/enrollment state while an already launched isolated worker retains
authority. Specifically, [REC-05](gate-0-diagnostic-recovery.md#rec-05--valid-e1-inference-stale-inventory)
assumes authentic E1 state returns after E2 enrollment/launch, E2 remains live,
and the restarted manager mistakes E1 for complete inventory before admitting E3.
That conditional counterexample remains valid. This record tests its restoration
premise against concrete source paths, not the already rejected process histories.

Before edits, live GitHub main and an independent `git ls-remote` both returned
`f793061f2656a2bd1fc26cca0a126825234dc74d`, the PR #46 merge. Local main matched.
Relevant merge and harness/validator history were inspected. The live open-PR
search returned **zero**, so all open heads/bases, complete diffs/files/modes,
checks/jobs/logs, reviews/comments/threads and PR dependencies were an empty set.
No existing intended PR required reuse. The initial tracked checkout was clean:
139 files, one registered worktree, no stashes. Local/remote branches and ignored
research, cache and build assets were inventoried and preserved. No applicable
AGENTS.md was found. No reset, clean, restore, stash pop or force push occurred.
Sandbox Git networking and branch creation initially failed; approved retries
verified main and created the single evidence branch. Failures are not successes.

[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational, page update `2026-10-29T00:32:07.685Z` (still October 28 in
the review timezone). Contribution instructions and all three workflows were
read. Foundation applies to this record and its index entry; Android substrate
and QEMU research path filters do not select them. Filtered jobs are not passes.
No new-PR CI result is inferred from historical receipts.

Requirements, architecture, governance, acceptance criteria, threat model,
security boundaries, feasibility gates, roadmap, provenance policy and both ADRs
were consulted. Inputs include [process-history reconciliation](gate-0-process-history-reconciliation.md),
[native-launch readiness](gate-0-native-launch-readiness-audit.md),
[diagnostic recovery](gate-0-diagnostic-recovery.md),
[Android lifetime authority](gate-0-android-lifetime-authority.md),
[capability revocation](gate-0-capability-revocation.md) and the
[native-host incident](gate-0-native-host-antivirus.md). Existing dependency and
artifact provenance records were reviewed, not re-attested as trusted builds.
No dependency, binary, manifest, packaging, permission, lifecycle control, CI,
security policy or production source changes.

## Evidence classes and actual harness correspondence

**FACT** means directly observed pinned-source behavior, not execution on every
Android 17 device. **INFERENCE** requires the stated source predicates.
**HYPOTHESIS** is plausible but unestablished; **UNKNOWN** lacks sufficient
evidence; **CONTRADICTED** names an explicit source witness against a proposition.
All reachability below is source analysis. No Android restore was executed.

At the baseline, the [manifest](../../android/gate0-harness/src/main/AndroidManifest.xml)
sets `allowBackup=false`, `fullBackupContent=false` and
`dataExtractionRules=@xml/data_extraction_rules`. There is no custom backup agent,
shared UID, privileged permission or platform signing. The dedicated worker is
non-exported, isolated, named `:gate0_worker`, with `useAppZygote=false`.
Compile/target SDK is 37; research minSdk is 30, not a qualified host-support floor.

Both sections of the [extraction rules](../../android/gate0-harness/src/main/res/xml/data_extraction_rules.xml)
exclude `path="."` for `root`, `file`, `database`, `sharedpref`, `external`,
`device_root`, `device_file`, `device_database` and `device_sharedpref`.
Session's actual durable state is the private `launch_lifetime` SharedPreferences
key `uncertain_child`, not an implemented E1/E2/E3 journal. Its files and preference
are covered by these private-domain exclusions. The CE/DE root exclusions also
cover ordinary nested private files. REC-05's complete journal is a model premise.

The original [packaged-authority validator](../../.github/scripts/validate-harness.py)
checks disabled backup/fullBackupContent, permissions, components, release
debuggability, packaged SDK/extraction settings and native inventory. **It does
not check `dataExtractionRules` or decode/validate its compiled XML contents.**
A validator pass alone therefore does not authenticate the D2D exclusion resource.
This investigation checks source correspondence, not a freshly installed APK.
The readiness audit's retained-artifact observation is historical evidence.

## Concrete eligibility matrix

Source abbreviations refer to the immutable ledger below: BER (BackupEligibilityRules),
PUR (PerformUnifiedRestoreTask), FRE (FullRestoreEngine), UBM (UserBackupManagerService),
BAC (BackupAgentConnectionManager), AMS (ActivityManagerService), PL (ProcessList).

| Mode and authorizing component | Pinned predicates and actual PDVA applicability | E1-file replacement disposition |
|---|---|---|
| Ordinary cloud backup / transport restore; system BackupManager and selected transport under user backup/setup policy | BER `isAppBackupAllowed` CLOUD returns the manifest allow-backup bit. PUR accept-set filtering applies eligibility; TarBackupReader `chooseRestorePolicy` rechecks installed-package permission, signatures and version for full streams. A historical backup from an earlier eligible version does not waive the current check. | **FACT / INFERENCE: excluded** for this installed configuration. Stop this pathway; no kill-order proof is needed to reject this particular restore route. |
| D2D migration; system restore session and transport-selected destination | BER `IGNORE_ALLOW_BACKUP_IN_D2D` is enabled since target S and overridable; for a non-system app it can ignore `allowBackup=false`. FullBackup selects the present `device-transfer` XML section. Default BackupAgent rejects excluded destinations before `FullBackup.restoreFile` opens them. | **FACT:** package-level eligibility can exist. **INFERENCE:** these excluded private E1 files are not restored by this default-agent path with the declared resource. `allowBackup=false` alone is **CONTRADICTED** as a D2D exclusion. |
| Automatic restore after install/reinstall; PackageManager → UBM `restoreAtInstall` | UBM accepts only system UID, requires a dataset, transport and auto-restore, then enqueues a filtered restore. `getEligibilityRulesForRestoreAtInstall` distinguishes ancestral D2D from cloud. InstallPackageHelper `restoreAndPostInstall` requests restore for a new install or an update still marked pending restore. | **INFERENCE:** inherits cloud exclusion or D2D file exclusions; installation is not an alternate unrestricted importer. A genuinely fresh target has no earlier target-local E2, but that premise must not be silently applied to replacement/reinstall/deferred restore. |
| Supported app-specific request | Public `BackupManager.requestRestore(observer)` delegates to the overload whose body logs deprecation and returns `-1` (335–371). | **FACT: unavailable** on this pin. Old documentation/comments about restoring without killing the caller do not establish a working ordinary-app API. Stop this candidate. |
| Internal single-package restore session | ActiveRestoreSession `restorePackage` allows BACKUP or matching target UID; UBM's session permission logic also has an own-package exception. PUR's single-target accept set differs from its filtered set. The public session wrapper is hidden/SystemApi, and the public request above is disabled. Full-stream tar policy still checks eligibility; key/value restore rejects an absent custom agent. | **FACT:** internal plumbing exists. **CONTRADICTED:** its existence supplies a supported public ordinary-app operation. Hidden Binder entry points are not adopted. Current harness cannot acquire arbitrary private-file restoration from this exception. |
| Routine package replacement/update | InstallPackageHelper normally preserves app data; a pending-restore update can enter BackupManager as above. PackageFreezer distinguishes asynchronous kill, wait variants and a no-op freezer. | **INFERENCE:** an update alone is not an E1 snapshot source or whole-resource certificate. Do not assume every update restores or every update synchronously ends isolated authority. |
| System package rollback with userdata snapshots | InstallPackageHelper calls RollbackManager for rollback/downgrade flags. RollbackManagerServiceImpl `enableRollbackAllowed` requires an installer with MANAGE_ROLLBACKS and a module/allowlisted target, or TEST_MANAGE_ROLLBACKS. `commitRollback` enforces management authority; snapshot/restore entry is system-only. | **FACT:** separate from backup exclusions. **INFERENCE:** unavailable under the ordinary, non-module, non-allowlisted harness installation model. OEM allowlisting or test privilege is a separate assumption, not a PDVA production grant. Stop before claiming installd or rollback ordering for such an installation. |
| Framework CE/DE migration in AppDataHelper `maybeMigrateAppDataLIF` | Requires a system package, non-file-encrypted storage and the platform migration configuration. | **FACT / INFERENCE:** this specific storage migration is inapplicable to the ordinary harness. It is not an old-journal restore API. Stop this pathway. |
| Cross-platform transfer branch present in this pin | BER requires allowBackup plus cross-platform configuration; FRE requires matching platform-specific configuration. Harness has neither opt-in. | **FACT / INFERENCE:** excluded. No external transfer implementation is needed for this negative. |
| ADB/debug restore, arbitrary privileged filesystem restore, OEM-specific migration | ADB has distinct debug/privilege eligibility in BER. Proprietary transports/OEM file-copy implementations are not identified by this framework pin. | **Excluded access class / UNKNOWN implementation**, respectively. No shell/root grant, hidden API or unauthorized manager-file access enters the ordinary-app model. No universal assertion about every OEM restore follows. |

The official [Auto Backup guidance](https://developer.android.com/identity/data/autobackup)
also warns that some manufacturers permit D2D despite disabled backup and describes
install-time restore. It is mutable contextual guidance, not the source of a
completed-kill invariant. Actual destination classification, compatibility overrides,
feature flags, compiled resources and OEM transport correspondence remain UNKNOWN.
Normal transfer to another device does not move the source device's live process
into the destination kernel; E2 must be target-local for the specific overlap.

## Positive exclusion witness and its destructive limit

**FACT:** ActivityThread `getBackupAgentName` selects FullBackupAgent when no custom
agent is declared for full backup/restore. FullBackupAgent inherits file restoration
from BackupAgent. FullBackup `parseSchemeForBackupDestination` (648–689) selects
the applicable new XML section before legacy fallback. Thus `fullBackupContent=false`
is not an additional unconditional veto when that new section is present.
`isFullRestoreEnabled` returns true for the new scheme; individual exclusions
still apply. D2D's legacy-config compatibility override does not erase a present
new `device-transfer` section in this method.

**FACT:** FullBackup canonicalizes the domain/path exclusions; `root` and
`device_root` map to the CE and DE data directories. BackupAgent
`isFileEligibleForRestore` (1037–1105) checks exclusions before includes and passes
a null destination for rejection. BackupUtils `isFileSpecifiedInPathList` tests
files beneath an existing excluded directory by path components. With ordinary
accessible private data roots, `launch_lifetime.xml` is rejected even if an older
authentic stream contains it. `FullBackup.restoreFile` consumes rejected bytes
without opening a destination. A permitted non-excluded file would instead reach
FileOutputStream: the code is not a stub that rejects everything.

**Important scoped limit, source inference:** exclusion from restored file writes
does **not** promise preservation of existing state. FRE (436–486) can clear app
data before creating the default agent, before that agent evaluates an individual
file's XML exclusion. FRE's coarse `isRestorableFile` returns true for D2D; it is
not the XML exclusion check. Given a valid accepted D2D stream that reaches this
branch, clear-before-reject can remove current state even though no E1 file is
restored. A stream produced solely by this unchanged all-excluded configuration
is not evidence that such private-file input exists. Prior eligible backups or a
different supported dataset require their own provenance/reachability predicates.
This is a **conditional state-erasure concern**, not a demonstrated REC-05 replay.
Worker survival across that clear remains UNKNOWN.

## Restore ordering and exact authority

The following ordering describes eligible paths, including counterfactual eligible
apps, to avoid confusing the scoped exclusions with a universal cleanup boundary.
It does not silently make the excluded PDVA E1 file eligible.

1. **Initiation and eligibility.** System BackupManager/PackageManager and the
   selected transport choose the restore dataset and operation. Restore-set/session
   operations have privileged controls; own-package internal exceptions are noted
   above. BER explicitly separates stopped-state checks used for backup from
   restore eligibility: being stopped is not a universal restore prerequisite.
   Its optional skip-already-launched-app filter depends on feature/transport flags
   and exempts custom-agent apps. It is not an unconditional no-live-worker rule.
2. **Before default full restore.** FRE conditionally calls
   `clearApplicationDataBeforeRestore` once per package; custom-agent apps normally
   skip clearing unless the system force-clear list selects them. UBM
   `clearApplicationDataSynchronous` (1614–1673) checks the clear-data flag, asks AMS
   to clear, and uses a 30-second timeout. It returns void after timeout or
   interruption; FRE then marks the package cleared and proceeds to bind. A
   completed cleanup success predicate is not required by this caller.
3. **What that clear requests.** AMS (4235–4273) calls `forceStopPackageLocked`,
   arranges the data observer and asks PackageManager to clear data. AppDataHelper
   `clearAppDataLeafLIF` delegates deletion to Installer. The observer describes
   data-clear completion; it is not a cgroup-empty or capability-revocation receipt.
   AMS force-stop first uses PL package-process selection and also brings down
   package services. PL (3232–3277) filters actual process app IDs, with dependency
   and PCC exceptions. A distinct isolated UID does not match the ordinary app ID
   merely because the APK/package name is the same. Service teardown and independent
   isolated-not-needed cleanup remain separate paths; their previous
   [lifetime analysis](gate-0-android-lifetime-authority.md#3-independent-isolated-not-needed-kill-with-scheduling-qualifications)
   is reused, not reinvestigated. **Do not infer that force-stop never affects
   isolated workers; do not infer that its package pass directly synchronously
   kills every isolated instance either.**
4. **Binding and visibility.** BAC `bindToAgentSynchronous` waits for agent attachment,
   not every previous process exit. AMS `bindBackupAgent` clears package stopped
   state and reuses an existing matching process or starts one. A live agent
   thread receives `scheduleCreateBackupAgent`; the path itself has no universal
   pre-bind force-stop. For an accepted file, BackupAgent/FullBackup writes into
   the destination tree file by file, with FileOutputStream before restore-finished
   callbacks. There is no whole-directory atomic E1/E2 journal transaction in this
   code. The normal install callback sequence follows restore, but
   InstallPackageHelper explicitly closes its freezer before BackupManager restore
   (918–926). That sequencing is not an all-lifetime exclusion lock.
5. **Initialization and concurrent work.** Restricted backup mode is conditional:
   BAC (368–414) checks operation type, feature flag, manifest property, target-SDK
   compatibility and transport decisions. Key/value mode is unrestricted; target
   37 is not an unconditional restricted-mode guarantee. The source therefore
   does not establish universal exclusion of app initialization/concurrent code
   until all restored state is complete. Actual PDVA replacement-worker creation
   during restore is **UNKNOWN**, not inferred merely from absence of this proof.
6. **After restoration.** PUR `keyValueAgentCleanup` (1481–1486, also used for full
   streams) calls BAC `unbindAgent`, allowing kill only if `mTargetPackage == null`.
   BAC kills only when allowed and its restricted-mode/unknown-connection or
   restore-with-FLAG_KILL_AFTER_RESTORE condition holds; core UIDs are exempt.
   AMS `killApplicationProcess` (4763–4788) looks up the one process name/backup
   agent UID and asks its application thread to `scheduleSuicide`. This is a
   post-write, process-specific request, not a pre-write SIGKILL of all isolated
   services, native descendants or resource holders. The legacy internal
   single-target no-kill branch is real; the disabled public API makes it an
   invalid ordinary-app example. No inference of successful hostile execution
   is needed to contradict **kill-after-restore implies pre-restore completion**.
7. **Interrupted/failed restore.** FullBackup can encounter short input after
   opening/writing a destination; write errors can delete the partial file.
   PUR's full-stream failure path aborts transport and calls conditional
   `clearApplicationDataAfterRestoreFailure` (1280–1304); key/value error cleanup
   can also clear. UBM applies the target-version/failed-restore clear flag and
   the same bounded wait. Skip/error install paths can finish installation without
   successful data restoration. No whole-state rollback transaction, all-worker
   completion or safe-admission receipt is established by these callbacks.

**Exact enforcement distinctions:** BackupManager eligibility is system policy;
the default BackupAgent's XML check runs in the trusted app's restore process,
not the isolated worker. PackageManager/Installer own authorized private-data
operations; ordinary apps do not acquire arbitrary access to manager-private files.
AMS/PL own process records and can invoke kernel signalling/group cleanup. PL
`removeProcessLocked` removes name mappings and calls `killLocked`, then handles
death bookkeeping; record removal is not independent completed exit observation.
ProcessRecord `killLocked` signals the primary PID and calls group cleanup. Even
its non-async branch sends a group signal before queuing PL group cleanup; it is
not an application-visible resource-closure certificate.

The existing pinned [group-cleanup chain](gate-0-android-lifetime-authority.md#4-system-owned-kill-and-the-lost-completion-result)
identifies system cgroup authority, conditional native completion/error checks
and discarded results. It can target native descendants remaining in the selected
group, not an unselected isolated UID's separate group. No new kernel/cgroup survey
is necessary. Completed exit, removed framework record, cleanup request, native
cleanup return and independently established group emptiness remain distinct.
Even established emptiness does not revoke transferred external references or
destroy disclosed copies; the [capability analysis](gate-0-capability-revocation.md)
still applies. No system-server-origin operation is promoted into global closure.

## REC-05 falsification matrix

“Not established” means neither demonstrated reachable overlap nor proof of
impossibility. A potentially surviving E2 is not automatically an unrecorded E2:
the state-loss/replacement predicate must also hold.

| Specific fault model | Class and source-grounded disposition | Live, unrecorded E2 / E3 conclusion |
|---|---|---|
| Current contract forbids the relevant cloud restore or rejects the D2D private file | **FACT:** predicates above. **INFERENCE:** authentic older E1 journal cannot be installed by these examined branches. | REC-05's exact restore premise is **CONTRADICTED for these branches**. This does not independently prove no E2 or authorize E3. |
| Eligible restore independently completes termination of every relevant worker and authority before replacement | **INFERENCE under explicit stronger premise:** the same live E2 cannot span that boundary. **UNKNOWN:** a complete applicable invariant satisfying it was not established here. | Exact live-E2 counterexample excluded if that premise is proved. Transferred authority/data require separate scope; no platform kill request substitutes. |
| Eligible restore exposes old data before relevant termination completes | **FACT:** file writes precede conditional post-restore teardown; pre-clear has a timeout-and-continue branch. **HYPOTHESIS:** a concrete permitted path plus surviving E2 realizes overlap. | REC-05 remains conditionally valid. Actual harness private-file eligibility is excluded above; this control-flow finding alone is not an ordinary-app exploit or a demonstrated E2 survivor. |
| Restore requests only agent/main-process death while isolated E2 may remain | **FACT:** post-restore AMS targets process name/agent UID and schedules suicide. **UNKNOWN:** other framework/service cleanup timing. | The request alone does not eliminate E2. Actual live, unrecorded E2 still requires a reachable state-replacement event and survival; neither is fabricated. |
| Interrupted, failed or incomplete restore; or clear-before-file-exclusion | **FACT:** bounded clear, incremental writes and failure clearing. **INFERENCE:** missing/partial state is not complete current inventory. | Not necessarily authentic E1 restoration. **UNKNOWN** whether E2 overlaps on a concrete installed build; state erasure must remain a separate admission fault. |
| Package update/reinstall treated as full cleanup | **FACT:** pending-restore, rollback eligibility and freezer variants differ. **CONTRADICTED:** update event or callback alone is a global closure certificate. | No E1 source from routine update alone. Fresh install without target-local E2 excludes that overlap by premise; reinstall with retained/uncertain authority is not proved clean. Qualified system rollback is outside the stated installation predicates. |
| Ordinary manager death, no restoration | **FACT:** Session ACTIVE is volatile; INIT precedes durable launch marking; marker clear precedes worker closure. See readiness audit. | **INFERENCE:** enrollment/admission gaps do not require backup restore. **UNKNOWN:** old-worker survival through independent cleanup. This investigation does not resolve REC-03 or prove E2 persists. |
| Journal corruption/incomplete persistence, no valid restore event | **FACT:** original missing key defaults false; successful commit ordering is explicit. **UNKNOWN:** concrete storage failure/corruption outcome; arbitrary loss of committed data is not asserted. | Distinct fault model, not evidence of Android-managed E1 restore. Do not substitute corrupt/missing state for proof that all earlier work ended. |

## Disposition and smallest remaining proof

**Narrowed:** stock-framework cloud restore and the default-agent D2D private-file
route do not instantiate REC-05 under the unchanged declared configuration.
**Rejected:** disabled public requestRestore as a live-restore example;
allowBackup alone as a universal D2D veto; post-restore kill as an atomic pre-restore
termination barrier; ordinary package update as an all-resource certificate.
**Still conditional/UNKNOWN:** OEM-specific paths, installed resource/flag
correspondence, state-clearing effects, concrete manager-death/isolated-worker
overlap, all native descendants, resource closure and external capability holders.
An authorized module/allowlisted system rollback is a separate fault assumption;
its framework snapshot calls do not consult the backup XML, but this does not
grant such restoration to the ordinary harness.

The proposed **universal pre-restore all-authority completion invariant is not
established**. The precise falsifier would be a permitted identified path that
exposes restored older protected state before complete relevant termination.
The reviewed control flow decisively rejects using conditional kill-after-restore
as that proof; no synthetic lifecycle model is needed. It does not demonstrate
that the exact current-contract E1/E2/E3 sequence is reachable on stock Android.
Stop this focused investigation without expanding excluded pathways.

The smallest genuinely new proof for the restore question is correspondence of a
specific supported host's restore destination, default-agent implementation and
compiled exclusion resource, or an identified permitted bypass with exact source
and installation predicates. A bypass claim must then establish state visibility
relative to **completed** relevant termination, including isolated identities and
remaining capability scope. Absent such a bypass, do not assert arbitrary rollback.
For overall recovery, the independent manager-death enrollment and closure blockers
remain; eliminating one restore premise supplies no universal current-worker
inventory and does not permit replacement or physical launch. No new privilege,
supervisor, remote freshness dependency or cleanup bypass is proposed.

## Validation and preservation

Executed with the existing bundled Python 3.12 interpreter; no dependencies were
installed and no validation assertions or skip rules changed:

| Check | Actual result and scope |
|---|---|
| Foundation validator | **PASS:** 140 files, 88 Markdown files, 54 requirements, two ADRs; repository hygiene and local Markdown targets. |
| Harness source/available merged-manifest validator | **PASS**, not fresh packaged extraction-resource or runtime verification. |
| Repository validation regressions | **137 PASS, four existing platform SKIP**, 141 total. |
| Desktop-readiness regressions | **27 PASS**. Synthetic journal/inspection controls, not Android recovery. |
| Offline-image inspection regressions | **45 PASS**. Synthetic byte/receipt controls; no image execution. |
| Frame-copy regressions | **4 PASS**. No Android rendering or worker-lifetime result. |
| Source correspondence | **PASS:** 22 decoded upstream SHA-256 identities and Apache-2.0 notices; six local LF-normalized files match baseline Git blobs. |
| Record review | Local links and anchors checked; full intended change, immutable source identities, whitespace, regular text modes and public-data hygiene reviewed. |
| Android/JVM build, native controls, restore fault injection, synthetic REC-05 model | **NOT RUN** in this investigation. No native/Android result inherited from historical evidence. |

Initial sandbox runs of desktop-readiness and offline-image suites stalled during
their first fixture setup and were interrupted without a result. Approved reruns
of the unchanged suites with access to their ignored fixture directories completed
as listed. Those interrupted attempts are not passes. A denied scripted ledger
append was replaced with the normal patch tool; all resulting hashes were checked.

No Android, phone, USB, ADB, emulator, guest, native launch or security-sensitive
Windows executable is
run. No APK rebuild, install or new native binary is required for this two-file
documentation change. No synthetic E1/E2/E3 model is run. Source-order conclusions
are not runtime test passes. Hosted checks remain unobserved at publication.

Only original analysis and the evidence-index entry are published. Upstream text
is reference-only temporary material; no source/binary redistribution or runtime
adoption occurs. Temporary reference files are locally retained without verified
independent backup. No private incident backup is re-attested. Public changes and
PR text exclude personal paths, credentials, signing material, private checkpoints,
incident samples, Persona data and third-party comparisons.

Publication uses exactly one branch and PR, followed by native chat attachment
and one identity/association verification, then STOP without polling CI, reviews,
comments, checks or mergeability. A publication/association failure must be reported
as **UNPRESERVED pending recovery of the same branch/PR/association**, never repaired
with a duplicate PR. Independent review and merge remain separate.

## Immutable source ledger and reproduction

All fresh upstream files below are from `platform/frameworks/base` commit
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`, the project's existing Android 17
reference pin. No additional backup repository/revision was necessary. It is a
per-project source reference, not a complete release manifest or authentication
of a particular installed OEM build. The previously recorded system/core cleanup
pin is reused only through the linked lifetime evidence, not newly retrieved.

Retrieve each immutable URL with `?format=TEXT`, base64-decode to bytes without
newline conversion, then SHA-256 hash and compare. Read the named methods and
callers, not just symbol matches. For example, Python standard-library
`base64.b64decode(urllib.request.urlopen(url).read())` followed by
`hashlib.sha256(data).hexdigest()` reproduces the identities. All retrieved files
carry Apache-2.0 notices, checked here; this grants no blanket license to adopt
unreviewed dependencies. The first BAC lookup under `backup/internal/` returned
404; the correct sibling path below succeeded. BackupUtils had one transient 503
before successful retrieval. A web-renderer failure was not counted as a source read.

| Immutable framework file | SHA-256 of decoded bytes |
|---|---|
| [core/java/android/app/backup/BackupAgent.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/backup/BackupAgent.java) | `6ea8e0c2ce954eb167c2f1235b6d81216544c37f56a3787234c88db4b5c88fc6` |
| [core/java/android/app/backup/BackupManager.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/backup/BackupManager.java) | `16c386e11a00cf5bbca843c0e64730312acb8ef5397fd2a847c5d684feb5d7fb` |
| [core/java/android/app/backup/BackupUtils.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/backup/BackupUtils.java) | `4698eee24de91a556821ca5c0c659db3e40bc29892ea136b5769cf0cc14b1925` |
| [core/java/android/app/backup/FullBackup.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/backup/FullBackup.java) | `ec60723acc6e2df5713e6a744763cad9515a843e739cb973438687520f85af73` |
| [core/java/android/app/backup/FullBackupAgent.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/backup/FullBackupAgent.java) | `02f765240f315663b0acf6036b90381091678b0ea989c51e79dedb33d812d952` |
| [core/java/android/app/ActivityThread.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ActivityThread.java) | `2d7bd7d9a9978258776a98ffe60589585a215688da303da7c71be7af961dc210` |
| [services/backup/java/com/android/server/backup/BackupAgentConnectionManager.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/backup/java/com/android/server/backup/BackupAgentConnectionManager.java) | `a3c16ed4d24f8c0f352b9a2f1911ca38eb6519671f1ff2b2b7df229d1762a409` |
| [services/backup/java/com/android/server/backup/UserBackupManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/backup/java/com/android/server/backup/UserBackupManagerService.java) | `a737879d82bce2d1fc47afd3f012e34fc1aad9c0aab5b0dbf075202ab57e4f3d` |
| [services/backup/java/com/android/server/backup/utils/BackupEligibilityRules.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/backup/java/com/android/server/backup/utils/BackupEligibilityRules.java) | `c69649be1d592d422ceeddc16a154cac19eac31e129daaae303821dc2f374bc4` |
| [services/backup/java/com/android/server/backup/utils/TarBackupReader.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/backup/java/com/android/server/backup/utils/TarBackupReader.java) | `69caf795d884b736fedb7525d8c576215b879602705dfad3ed78fb1f69769477` |
| [services/backup/java/com/android/server/backup/restore/ActiveRestoreSession.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/backup/java/com/android/server/backup/restore/ActiveRestoreSession.java) | `11d6d6de0cd122cdeecebfa6ef6f53043e49500430d0c371b214856705e106d6` |
| [services/backup/java/com/android/server/backup/restore/FullRestoreEngine.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/backup/java/com/android/server/backup/restore/FullRestoreEngine.java) | `5f3fca55395de25b192e7e2828966073d434413570ac252de16c4a7f1fcb0f03` |
| [services/backup/java/com/android/server/backup/restore/PerformUnifiedRestoreTask.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/backup/java/com/android/server/backup/restore/PerformUnifiedRestoreTask.java) | `020336574dd1212a6e35daa45cd4197a43c8079a3181d00b07c7b6c99d2c00ae` |
| [services/core/java/com/android/server/am/ActivityManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActivityManagerService.java) | `17923170a97fb001c3892ab4e0d71f9e249f9ea0b427a7aaf29916aae5208797` |
| [services/core/java/com/android/server/am/ProcessList.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessList.java) | `96bfea0a32f822a04e46a16279100d5fdc718b909999df4962f2bd15c8ac55fc` |
| [services/core/java/com/android/server/am/ProcessRecord.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessRecord.java) | `f4f07c1ba18fe28c66664c7300b9e5d22d5136358b136d3562aab401b0d616a0` |
| [services/core/java/com/android/server/pm/AppDataHelper.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/pm/AppDataHelper.java) | `e2a204f325e99013ba300238eed58f4741cacceba34c4d5df58f54d7e1aba5ca` |
| [services/core/java/com/android/server/pm/InstallPackageHelper.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/pm/InstallPackageHelper.java) | `00a61a16e9a209f8c8be39bb997f63e3a7235c1214faab9a56157e619f1104ee` |
| [services/core/java/com/android/server/pm/PackageFreezer.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/pm/PackageFreezer.java) | `ebb73a0f5ae8b23646a15ebf338a44616d4f729e2c8f9643917d78a811393c20` |
| [services/core/java/com/android/server/rollback/AppDataRollbackHelper.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/rollback/AppDataRollbackHelper.java) | `88661c1e2e6f3da6e1b2433aaff777d21e98fd6bf9de1297fce2a9a49f0aa89c` |
| [services/core/java/com/android/server/rollback/Rollback.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/rollback/Rollback.java) | `164e05c94af53b5fd3eb5a3b3a9f9c914afa8b5d5123c4b2ddacc8ba05b9fe98` |
| [services/core/java/com/android/server/rollback/RollbackManagerServiceImpl.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/rollback/RollbackManagerServiceImpl.java) | `de61660579d2b44ce2706bd4aab14daa1906a72f54abed1d46ba26f0a52b8161` |

Local identities use baseline Git blobs (LF bytes). All six working files,
normalized from CRLF to LF, matched those blobs.

| PDVA source at the baseline | SHA-256 |
|---|---|
| [android/gate0-harness/src/main/AndroidManifest.xml](../../android/gate0-harness/src/main/AndroidManifest.xml) | `c9cdc91cb4889ee4c433934145d0c864bea17b0811e89fd1d3567d31e2d9f62c` |
| [android/gate0-harness/src/main/res/xml/data_extraction_rules.xml](../../android/gate0-harness/src/main/res/xml/data_extraction_rules.xml) | `b0e88f2e1ffb1c8de5783db430a938f0bb86987ded7aca3b5cf77590247ae09d` |
| [android/gate0-harness/src/main/java/org/pdva/gate0/Session.java](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java) | `78ec8a68f5efb801a006042106603377be6d5bd800718c798a483d8157516cba` |
| [android/gate0-harness/src/main/java/org/pdva/gate0/WorkerService.java](../../android/gate0-harness/src/main/java/org/pdva/gate0/WorkerService.java) | `48e52e6861621dda2caa5a5a1d127122559ee9b1efadb10c0c671c26c61bf101` |
| [.github/scripts/validate-harness.py](../../.github/scripts/validate-harness.py) | `f9557746c1061e20dbf2f3c7c39c6c4165e87f10aabd6c35365fdecb75d70bf1` |
| [android/gate0-harness/build.gradle](../../android/gate0-harness/build.gradle) | `fbd7ab15c643cc966427c362a1e7c950c13755487eb14b7d6387d45a5fb58017` |
