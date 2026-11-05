# First physical native-launch test: owner readiness procedure

Prepared **2026-11-03, America/Fortaleza**, against main
`074e3e83a67f656ad5b94edcd445f3761f1e340d`, tree
`b52d86d03c181ba44c49cf9a07cd8c6bccac2c62`.
**NOT READY — STOP. This is offline preparation, not permission to test.**
**2026-11-04 correction:** the [research execution lock](gate-0-research-execution-lock.md)
removes the buttons described below and denies both modes before reservation.
This historical conditional procedure cannot enable the current APK. Future
execution requires a separately reviewed, owner-approved code change after the
readiness prerequisites are satisfied; no current activation mechanism exists.
Gate 0 remains **Unresolved**; Gates A–G **Not reached**.
Scope: PDVA-REQ-002–003, 008–015, 036–045, 047–048 and 054.

Tony can use this procedure to collect the missing evidence and obtain a scoped
decision. Do not connect a phone, initialize Android CLI, build/sign an APK,
install, open the harness or press a test button now. Every device-facing step
below is **NOT AUTHORIZED UNTIL THE READINESS GATE IS CLEARED**, followed by
Tony's separate explicit testing authorization. No security-setting change,
ADB, credential acquisition or privileged access is included.

This operational handoff supplements the [readiness audit](gate-0-native-launch-readiness-audit.md),
not another lifecycle survey. Apply its findings together with the later
[one-way guard correction](gate-0-one-way-research-attempt.md): PR #49 supersedes
the old late marker, clear-on-CLEAN and multi-cycle behavior. It does not supply
independent freshness or recovery. All [requirements](../requirements.md),
[governance](../governance.md), [acceptance criteria](../acceptance-evidence-criteria.md)
and [roadmap prerequisites](../roadmap.md) remain in force. ADR-0001 is Accepted;
ADR-0002/0003 are Proposed, with only ADR-0003 Option A approved.

## 1. Identify the one experiment

The first proposed test is one normal request in **PDVA Gate 0 research**,
package `org.pdva.gate0`, using a qualified non-debuggable release-equivalent APK
on Tony's stock, nonrooted Samsung Android 17/API 37 production `user` phone.
The current button is **Request one research attempt**. The separate
**Request one worker-death attempt** is not this experiment.

The existing [native-launch control](gate-0-isolated-native-launch.md) attempts
installer-extracted ARM64 dynamic PIE `lib/arm64-v8a/libpdva_launch.so` through
the isolated worker's fixed `fork`/`execve` path. The trusted, non-forking payload
writes exactly 40 bytes containing result 42 and intentionally exits **42**.
Its `.so` suffix is an extraction convention, not JNI loading. There is no VM,
QEMU, kernel/rootfs, Android guest, emulator or simulated physical substitute.

The normal request also executes the existing synthetic substrate/protocol
probes before LAUNCH, including generated-code and process-authority probes.
It is not a standalone arithmetic-only app. Qualification and authorization must
cover that complete existing path. Do not remove probes, invoke a private entry,
lower target SDK or move execution into management to make the test pass.
Use the fixed [integration acceptance scope](gate-0-qemu-worker-integration.md#single-smallest-next-experiment-and-stop-conditions).

## 2. Assemble the prerequisite packet without device work

Tony owns collection and the final authorization. A build maintainer supplies
artifact evidence; a reviewer independent of its production checks it. A vendor
or qualified security analyst supplies incident disposition. An independently
qualified observer/recovery mechanism must supply runtime evidence; **none is
identified or qualified here**. Naming a person does not create platform authority.
Unassigned responsibility is itself a blocker.

For each row, retain privately: evidence ID/location, exact revision/artifact and
scope, evidence producer, independent reviewer, date, observed result, limitations,
falsifier result and decision. A completed form or signature is not proof.
**Verified** means only the stated observed/source scope; **Unknown** means missing
or inconclusive proof; **Failed** means a contradicted proposition; **Blocked**
means a prerequisite forbids dependent work; **Not run** means no execution.

| Mandatory prerequisite | Current evidence and state | Required evidence and responsible party | Falsifier / stop trigger |
|---|---|---|---|
| Complete attempt enrollment before delegation | **Verified source only:** PR #49 reserves before allocation/bind/INIT and retains the marker. **Unknown/Blocked:** independent complete enrollment through manager loss. | Maintainer and independent reviewer: exact-source contract binding every pending bind, worker, child and delegated resource to an enrolled attempt, including lost INIT reply and callback races; identify a legitimately available independent authority. | Any issued authority without enrollment, or restart admission with an unaccounted attempt. |
| Freshness and state loss | **Unknown/Blocked.** Empty files and absent preferences are a conditional first-use assumption, not authenticated fresh state. [Process histories](gate-0-process-history-reconciliation.md) cannot supply a complete census; [managed restore](gate-0-managed-restore-lifetime.md) narrows particular restore routes without proving universal freshness. | Independent reviewer: exact installed-build, state-loss/restore and no-prior-attempt proof, with failure semantics and applicability. Tony retains prior-attempt history; his recollection alone cannot satisfy it. | Missing, stale, corrupt, rolled-back or conflicting history; treating absence, a new UUID or reinstall as proof. |
| Independent observation | **Blocked:** no qualified ordinary-app observation procedure for this attempt and complete authority scope. | Observer provider and independent reviewer: concrete authority/access class, identities, observation points and retained receipts; qualification showing it detects a known event and rejects missing, forged, stale and wrong-attempt evidence, including manager death. | Reliance solely on worker JSON, Binder death, PID disappearance, diagnostic history, callback, timeout or observer silence. |
| Cleanup and recovery | **Unknown/Blocked.** Direct-child wait is worker-reported; worker/descendant/reference closure is unproved. No recovery transition exists. | Observer/recovery provider: independently established direct-child reap plus complete worker, descendant, FD/mapping and external-holder disposition; pre-agreed safe response to unavailable closure. Treat already disclosed copies separately. | Lost reply, partial cleanup, unaccounted holder or an alleged recovery based only on force-stop/reboot/uninstall. |
| Permanent attempt lockout | **Verified source condition:** intact PR #49 state never reopens, even after success. **Unknown:** device durability and state-loss resistance. | Maintainer/reviewer: exact-source and independently qualified persistence/continuation evidence across relevant failures. Keep a separate owner-controlled uncertainty record; it is operational evidence, not a replacement enforcer. | Clear/delete/repair marker, app-data reset, restore, alternate journal, update/reinstall or repeat to evade uncertainty. |
| Host antivirus and binary provenance | **Blocked:** [two quarantined Windows controls](gate-0-native-host-antivirus.md) have no qualified malicious/false-positive verdict or exact executable ancestry. Later Linux CI does not resolve them. | Tony obtains vendor or qualified analyst disposition covering both recorded detection hashes, rule/version, source/construction and executable correspondence; analyst defines any remaining execution restrictions and qualifies the intended build environment. Owner separately approves any private sharing. | Unresolved applicable finding, new detection, missing provenance, or reliance on a clean scan/source review/green CI as clearance. No sample restoration or exclusions. |
| Exact source and build chain | **Verified repository identity** above; historical pinned build ledger exists. **Unknown/Blocked:** qualifying current source-to-APK correspondence and environment trust. | Build maintainer supplies full source/tree, reviewed diff, tool versions and hashes, package revisions, commands, build logs, dependency/native inventory, adoption/rights and independent review. Apply [existing adoption limits](gate-0-isolated-worker-adoption.md). | Dirty/substituted input, stale APK, missing tool identity, changed dependency or unexplained output. A source SHA typed into a receipt is insufficient. |
| Reproducibility and signing | **Failed:** fifteen historical whole-signed-APK equality pairs. **Unknown/Blocked:** current qualifying artifact and key provenance. Release currently uses a development key. | Maintainer/reviewer must satisfy approved [ADR-0003 Option A](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md), retain failures and independently qualify exact signer/custody and release-equivalent scope. No qualifying route is established here. | Treating matching ZIP/native content, a valid signature or a retained identical copy as whole-APK reproducibility. Do not repeat the stopped experiment or adopt D1/D2. |
| APK/native/package identity | Historical retained APK inspection is **Verified for those old bytes only**, not current installation clearance. Current qualified APK **Unknown**. | Maintainer: exact APK SHA-256, signer certificate SHA-256/schemes, non-debuggable release manifest, compiled extraction policy, all three native-entry hashes and matching original build outputs. Reuse existing validators below. | Wrong variant, unexpected signer, missing/extra native entry, mismatch, unknown resource format or source drift. |
| Ordinary-app host and hardware | **Verified source:** no requested permissions, isolated non-exported service, target/compile 37, research minSdk 30, ARM64 payload. **Not run/Unknown:** Samsung applicability, installed ABI/page size/linker/seccomp/SELinux, memory/storage/thermal fit. | Reviewer prepares non-sensitive model/build/patch/One UI, production/nonrooted, ARM64 and page-size evidence requirements and conservative resource/observation limits before separate device authorization. x86_64 is not a launch substitute. | Need for root/shell/OEM grants, a different SDK/policy, unexpected ABI/domain/capabilities, unknown prerequisites or no justified limits. ELF 16-KiB alignment alone is not compatibility. |
| Installation path and artifact continuity | **Unknown/Blocked:** no approved transfer/installer route for this phone. | Tony and reviewer specify ordinary transfer, independent identity checks across transfer and installation, and an already permitted installer route without changing security policy. APK filename/app label alone cannot bind installed bytes. | Auto Blocker/Play Protect/admin/source restriction, override prompt, changed file or inability to establish installed identity. |
| Evidence retention and failure reporting | **Unknown/Blocked:** independent private backup is not attested; in-app report is memory-only until copied. | Tony and reviewer verify owner-controlled independent backup and retrieval of packet/observations, pre-arrange capture through manager death, and name failure recipient/storage. Public output is a separately reviewed redacted summary. | Sole ignored local copy, clipboard/screenshot loss, unsanitized upload, absent observer receipt or interrupted retention. |
| Separate test authorization | **Not given; Blocked.** This request authorizes preparation and one evidence PR. | After all rows are independently satisfied, Tony explicitly authorizes the exact source/APK, device scope, normal one-attempt path, observers, limits and recovery instructions. | General enthusiasm, PR merge, checkmarks, CI, elapsed time or silence interpreted as permission. |

**Action now:** collect incident disposition and a concrete independently
reviewable enrollment/freshness/observation/recovery contract first. These are
separate blockers. Stop build qualification at unresolved incident/provenance
dependencies; stop phone preparation at unresolved authority/artifact conditions.
If no ordinary-app authority can meet the contract, retain STOP and return the
specific failure to Tony for the existing governance decision. Do not invent a
supervisor or reopen stopped general surveys to fill the table.

## 3. Reuse the offline tools; do not build another readiness validator

| Existing tool/evidence | Reusable function | Limit or actual gap |
|---|---|---|
| [Foundation validator](../../.github/scripts/validate-foundation.py) and [regressions](../../.github/scripts/test-repository-validation.py) | Repository roots, text/binary hygiene, requirements and local links; rejection controls. | No physical permission, secret-safety guarantee or artifact clearance. |
| [Harness validator](../../.github/scripts/validate-harness.py) | Source/merged manifest; with a qualified APK/analyzer, actual package authority, three-entry native/ELF inventory and compiled extraction policy. | No signature verification, full source reconstruction, installed execution or recovery proof. |
| [Packaged-policy controls](../../.github/scripts/test-packaged-rules.py) | Existing real compiled policy mutations from PR #48. | Requires qualified SDK tools/artifacts; not rerun or replaced with synthetic results here. |
| [Desktop readiness journal](../../.github/scripts/desktop-readiness.py) and [procedure](gate-0-desktop-readiness.md) | Source/APK/native-output correspondence and append-only offline dispatch/result records; conservative interrupted-operation handling. | No phone dispatch or cleanup-clear API, independent authenticity/anti-rollback, external backup or Android lockout enforcement. COMPLETED means offline inspection only. |
| [One-way guard and tests](gate-0-one-way-research-attempt.md) | Existing reservation and malformed/prior-state rejection controls. | Intact fresh data assumption; tests do not establish independent Android enrollment/freshness. |
| [Offline image inspector](../../.github/scripts/offline-image-inspect.py) and frame-copy tests | Existing bounded byte/receipt and copy controls. | No guest image is needed for this experiment; do not introduce image inspection as a substitute prerequisite or execute an image. |
| SDK apksigner | Independent signature-format verification of an identified APK with qualified tool bytes. | Signer authenticity/custody, source correspondence, equality and safety remain separate. |

The gaps are missing qualified authorities and evidence, not a missing checklist
parser. Retained APKs and old receipts remain historical. PR #49 explicitly notes
that earlier local APKs predate its Java/UI change; do not relabel them as current.
PR #50's experimental comparator is historical and unadopted, not a current tool
to restore or run. No validator is added by this procedure.

## 4. Windows 10 preparation for a later cleared build

**Future only: do not run build/signing or artifact-qualification commands until
the applicable incident/environment prerequisites are independently cleared and
the work is separately authorized. These steps do not authorize a phone.**

1. The reviewer supplies the exact approved commit, qualified APK and build
   receipt, expected APK hash and signer fingerprint through an authenticated
   owner-controlled channel. Keep originals and logs private with a verified
   independent backup. Do not use a random download, debug APK, instrumentation
   APK or the old locally retained release just because its filename matches.
2. In File Explorer, open the reviewed repository folder, then open PowerShell
   there. Use the existing qualified Python/JDK/SDK paths supplied by the build
   maintainer. A missing tool means STOP; this procedure installs nothing and
   does not initialize Android CLI. The [existing build instructions](../../android/README.md#build)
   identify the pinned build tasks. A maintainer must qualify their exact outputs;
   Tony should not repeat builds to pursue equality or generate a different key.
3. Read `git rev-parse HEAD` and `git status --short`. Compare with the packet;
   do not reset, clean, stash or overwrite unrelated work. The source, APK and
   native outputs must be from the same reviewed build, with independently
   established correspondence rather than merely the current checkout's name.
4. With the qualified release file at the standard output location, these are
   the existing offline checks. The maintainer must supply validated environment
   paths before use; commands are not evidence until actually executed:

   ```powershell
   $testApk = 'android/gate0-harness/build/outputs/apk/release/gate0-harness-release.apk'
   Get-FileHash -Algorithm SHA256 -LiteralPath $testApk
   & "$env:ANDROID_HOME/build-tools/36.0.0/apksigner.bat" verify --verbose --print-certs $testApk
   if ($LASTEXITCODE -ne 0) { throw 'STOP: APK signature verification failed' }
   python .github/scripts/validate-harness.py --variant release --apk $testApk --apkanalyzer "$env:ANDROID_HOME/cmdline-tools/22.0/bin/apkanalyzer.bat"
   if ($LASTEXITCODE -ne 0) { throw 'STOP: package inspection failed' }
   ```

   Compare the hash and certificate SHA-256 with the independently approved
   packet, not values copied from this same command run. Record verifier/tool
   identities and schemes. Keep certificate details and diagnostic paths private.
   [Android's apksigner reference](https://developer.android.com/tools/apksigner)
   documents verification; signature validity alone does not approve the signer
   or authenticate the source. Follow the existing desktop-journal procedure
   only for an explicitly authorized offline inspection and original native-output
   mappings. An UNKNOWN journal must not be repaired or replaced to retry.
5. Reviewer checks the compiled package: `org.pdva.gate0`, non-debuggable release,
   no permissions, expected components/extraction policy, target 37 and the exact
   ARM64 executable plus ARM64/x86_64 JNI inventory. Recheck file identity after
   inspection. Any mismatch or unresolved Option A condition returns NO-GO.

## 5. GO/NO-GO decision before touching the phone

The independent reviewer evaluates every matrix row against its actual supporting
evidence, not a total score. A row can become satisfied only for its exact scope;
historical or synthetic evidence cannot satisfy a physical or independent claim.
All mandatory technical pre-test rows must be satisfied; the final authorization
row is evaluated separately after that technical decision. Expected experimental outcomes
(whether this exact phone permits exec, for example) remain **Not run** until the
authorized experiment; their observation and failure-handling prerequisites must
already be qualified. This distinction does not waive independent cleanup.

Record **NO-GO** for any Failed, Unknown, Blocked, missing, stale, conflicting or
unreviewed prerequisite. Identify the row, owner, missing receipt and reopening
condition. No approval can transform absent technical evidence into proof.
**Current decision: NO-GO / NOT READY — STOP.**

Only after independently satisfying every mandatory prerequisite may the reviewer
record a scoped readiness decision. Tony must then separately authorize one test
against the exact packet. Bind that authorization to source/tree, APK/native and
signer identities, host scope, normal button, independent observation procedure,
resource/time limits, evidence destination and safe recovery instructions.
Any relevant source, artifact, host-policy or observer change invalidates the
decision pending re-review. This document supplies no GO receipt.

## 6. Samsung test-day instructions — NOT AUTHORIZED UNTIL THE READINESS GATE IS CLEARED

These are conditional operator steps, **not presently executable instructions**.
The qualified packet must first supply the missing observer, installed-artifact
identity method, justified observation deadline/resource limits and recovery
actions. Blank fields mean STOP; Tony must not improvise them.

1. With the separately authorized reviewer, confirm the approved model, Android
   build/patch/One UI, stock production state, ARM64/page-size applicability and
   resource conditions using the packet's ordinary-access method. A Samsung
   **Settings → About phone → Software information** view may help identify the
   build; labels vary, and that view alone does not prove all host prerequisites.
   Do not capture serial numbers, IMEI, Android ID, accounts or notifications.
   Do not enable Developer options, USB debugging or special grants.
2. Start the qualified independent evidence capture **before** installation or
   any attempt-related action. Verify evidence retention and freshness using its
   approved procedure. Missing observation or prior/ambiguous app state means STOP;
   do not clear data, uninstall/reinstall or restore a backup to obtain admission.
3. Transfer only the approved APK through the reviewed ordinary route; verify
   continuity to the approved hash/signature and installed package using the
   qualified method. With an already permitted installer, open that exact file
   (for a file-based route, in **My Files**), review the ordinary install prompt
   and choose **Install** only if it matches the packet. If it asks to enable
   unknown sources, bypass a warning or change a security setting, cancel and
   STOP. Do not switch to ADB, another store or a privileged installer.
   [Samsung documents Auto Blocker installation restrictions](https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/system-security/samsung-auto-blocker/).
   Actual applicability is an exact-device prerequisite, not a reason to disable
   protection. No installation attempt or policy check was made here.
4. Choose **Done** after installation. Confirm the installed-artifact receipt
   with the reviewer before opening **PDVA Gate 0 research** from the app list.
   Check the expected title and current one-attempt UI against the exact reviewed
   source. Old multi-cycle buttons, an unexpected permission request, or a
   lockout means STOP. The app's built-in NOT READY warning is not a clearance
   display; this procedure does not alter it or claim it grants permission.
5. Only with the observer ready and the separate exact-scope authorization,
   tap **Request one research attempt** once. Do not tap the worker-death button,
   rotate/background as a fault injection, or retry. The normal request includes
   its existing protocol rejection checks; no second physical attempt is added.
6. Read each field with the reviewer. If a report is available, use **Copy
   sanitized JSON** only into the approved private evidence destination. The
   button name is not a privacy review; clipboard history/sync and screenshots
   are not durable or automatically public-safe. If capture cannot be completed
   without changing settings or exposing personal information, STOP and record
   the evidence gap. Do not rerun to recover a missing report.

## 7. Read the result, stop, and preserve evidence

The reviewer keeps worker/payload self-report separate from independent receipts.
The positive launch proposition needs successful creation/exec, exact valid
40-byte/result-42 output, exit 42, matching direct-child reap, no signal/timeout
or kill/cleanup error; child PID distinct from worker, same worker UID/eUID,
expected isolated domain, zero effective capabilities and zero unexpected FDs.
Record seccomp and linker observations with their limitations. Missing inventory
is Unknown. `EACCES`/`EPERM` alone does not identify SELinux as the cause.
See the actual [LaunchResult fields](../../android/gate0-harness/src/main/java/org/pdva/gate0/LaunchResult.java).

`launch_cleanup=reported_clean` is **worker report only**;
`worker_reaped=not_measured` remains Unknown. A valid-looking JSON report, green
row, exit 42 or Binder death cannot establish independent completion or whole-scope
closure. Preserve the UI's conservative labels even if separate evidence later
supports a narrowly reviewed launch result. No result establishes hostile-worker
containment, TCG, guest boot, Gate 0 pass or production readiness.

On any alert, denial, malformed/partial report, unexpected identity/authority,
signal, timeout, lost reply, crash, observation failure, exceeded limit or cleanup
uncertainty: **STOP the experiment and permanently prohibit repeats**. If responsive,
tap **Stop** once to request cooperative cancellation; it does not interrupt every
synchronous Binder call or certify teardown. Do not wait indefinitely or use a
deadline as proof of death. Follow only the already qualified safety response;
if it cannot establish closure, record **cleanup UNKNOWN / LOCKOUT** and escalate
to the designated reviewer. No automated recovery or clearing step exists here.

Record distinct outcomes: **Not run** only when evidence establishes that the
specified operation was never dispatched (missing replies do not establish this);
**Failed for exact scope** for an independently attributable denial/contradiction;
**Unknown** for missing/inconclusive evidence; and **cleanup lockout** independently
of any positive launch fields. A successful trusted-child observation also consumes
the reservation permanently. Do not press again to demonstrate lockout.

Preserve original source/build/APK identities, authorization, sequence/timestamps,
observer receipts, output, errors, stop action and unresolved scope privately.
Verify the independent backup is retrievable and hash-identical before reporting
durability. A hash alone does not prove authenticity or completeness. No private
incident samples are needed in this packet. Publish only a reviewed summary with
safe model/build/ABI context, relevant hashes, procedure, falsifier, actual outcome
and limitations; exclude keys, identifiers, private paths, accounts and Persona data.

Uninstallation is removal, not proven cleanup or a reset authorization. Only after
evidence preservation and independently established applicable closure, and if the
separately approved recovery plan permits it, use **Settings → Apps → PDVA Gate 0
research → Uninstall**. If closure is uncertain, do not erase state to pursue a
retry; retain lockout and obtain the qualified recovery disposition. Apparent reboot,
force-stop, uninstall success or a new installation never clears this record.

## Preparation evidence and validation

Live GitHub main matched the baseline above. Connector search and the REST
open-PR collection returned zero; open heads/bases, complete diffs/files,
checks/jobs/logs, reviews/comments/threads were therefore an empty set. No matching
PR needed reuse. Inspected merged PRs #45–52 with exact head/base/merge identities,
their retained findings, current source/UI, requirements/ADRs, provenance/dependency
records and all workflows. Initial checkout was clean, one worktree, no stashes;
existing branches and ignored outputs were preserved. No repository/ancestor
AGENTS.md was found. This adds only original procedural text and an index link;
no implementation, dependency, workflow, signing policy or requirement changes.

Exact-main [foundation run 41711642174](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41711642174)
completed successfully. Jobs `126180930580` and `126180931146`, steps and actual
logs were inspected: 149 repository, 28 journal, 45 image and four frame tests
on Linux, plus existing native controls; Windows logged 45 image and four frame
tests. These are historical hosted receipts, not new local native runs or incident
clearance. The legacy status had zero contexts despite its `pending` label.
The commit-workflow connector returned no runs; the exact-SHA REST collection
supplied the run above. Android/QEMU path filters did not apply to that main
documentation change and do not apply to this two-file change; foundation does.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational, page update `2026-11-04T01:24:27.247Z` (November 3 locally).

Local validation used existing Python 3.11.4 on Windows:

| Check actually completed | Result and limit |
|---|---|
| Foundation validator | PASS: 148 files, 93 Markdown files, 54 requirements, three ADRs; local file links and repository hygiene. |
| Harness validator without APK arguments | PASS: source and available merged manifests; no fresh APK or signature qualification. |
| Repository regressions | 149 total: 145 passed, four existing Windows skips (native C control and POSIX symlink/mode cases). |
| Desktop-readiness regressions | 28 passed; offline journal/fixture evidence only. |
| Offline-image regressions | 45 passed; synthetic byte/receipt fixtures, no image execution. |
| Frame-copy regressions | Four passed; desktop mapping/copy behavior only. |
| Documentation review | Complete two-file change, local links/anchors, UTF-8, regular 100644 modes, whitespace, evidence claims, privacy and provenance checked. |

The first sandbox journal/image suite attempts stalled at fixture setup and were
interrupted without a result. Approved reruns of the unchanged suites with fixture
access completed as listed; interrupted runs are not passes. No skip/assertion or
validation policy was changed. Existing ignored evidence was not deleted.
All 24 local links/anchors in the procedure and new index entry resolved. An
initial ad hoc privacy-pattern check incorrectly matched HTTPS URL suffixes as
drive paths; the corrected boundary-aware check passed, followed by manual review.

No fresh APK,
signature, compiled-policy, JVM/lint, native/process, Android/emulator/VM/guest,
phone/ADB, security or performance experiment is claimed. The WindowsApps Python
alias was unavailable; existing NDK-bundled Python 3.11.4 is used for offline
checks. Initial sandbox Git networking failed; live GitHub connector reads
established main. Neither failure is counted as a passing check. No private
incident material was read and no private backup is newly attested.

Publication preserves one evidence PR, followed by native attachment to the
requesting chat and one association check, then STOP without polling checks,
reviews, bots or mergeability. New-head CI is unobserved at publication. A failure
to publish or attach requires recovery of the same work/PR, never a duplicate.
