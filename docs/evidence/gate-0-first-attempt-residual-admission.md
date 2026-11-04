# Gate 0: residual application-data admission

Date: **2026-11-04, America/Fortaleza**. Base/main:
`8175ec05f65427fa2cdf7c3fc53ee4c824c499a8`, tree
`220802f92b628940cf30151a972d2f051c14239c`. Scope: PDVA-REQ-002–003,
009–015, 036–043, 048, 051 and 054. **Gate 0 Unresolved; Gates A–G Not
reached. Physical readiness NOT READY — STOP.**

## Result and falsifier

**Direct desktop observation:** the actual baseline `ResearchAttempt.reserve()`
returns true with empty `files`, absent `shared_prefs`, and synthetic prior-attempt
evidence in each of five other application-data siblings. Both injected directory
sync callbacks execute and a reservation marker is created. Evidence is preserved.
The preference and private-files negative controls return false without syncing.
This contradicts an unrestricted reading of PR #49's statement that partial/residual
state is conservatively denied. It does not demonstrate an Android prior attempt,
state-loss route, surviving worker, or exploit under intact-state assumptions.

**Falsifier:** a known synthetic residue outside the old two checked locations
must not satisfy the admission predicate. A test increments a stand-in delegation
counter only if the actual guard returns true; the required value is zero.
[Session](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java)
source independently shows that false returns before allocation, bind and INIT.
The counter is not an executed Android delegation or lifecycle simulation.

The correction is conservative rejection, not a new freshness classifier.
Enumerate the application-data root and permit only real directories named
`files`, `cache`, and `code_cache`; require each to be empty before reservation.
`files` must exist for the existing file creation path; cache directories are
optional. Preserve unconditional rejection of `shared_prefs`. Reject other
siblings, non-directory entries, symbolic-link entries, nonempty caches and
enumeration/attribute errors. Do not parse, remove, repair or migrate evidence.
`NOFOLLOW_LINKS` is used for entry attributes; this is not race-proof traversal.

The process latch, `CREATE_NEW`, write loop, file force, close and ordered files/
parent directory sync remain unchanged. All must succeed before admission.
Failed reads/writes/syncs still consume the process attempt; partial marker bytes
remain. No completion, restart with intact marker, CLEAN or cleanup request reopens
admission. No lifecycle ownership, privilege, permission, native source, dependency,
manifest, workflow or production boundary changes.

## Fresh state is a conditional assumption

**Source finding:** Android creates some directories without any PDVA attempt.
It is incorrect to reject every sibling on the theory that directory existence
proves earlier delegation. These immutable Android 17 r1 sources were retrieved
and SHA-256 hashed from decoded Gitiles bytes:

| Input | Revision and SHA-256 | Observed behavior |
|---|---|---|
| [InstalldNativeService.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/cmds/installd/InstalldNativeService.cpp) | Revision `ae266dcb706d083868578cfedce381ef44488a07`; SHA-256 `074e5ce7fedcaa83de576915e3fef21ded70c01cb8b10714bb9f44d60e99dcce` | `createAppDataDirs` prepares the data directory and `cache`/`code_cache` (lines 784–827), including creation without a prior app attempt. This justifies allowing empty cache directories, not arbitrary contents. |
| [ContextImpl.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ContextImpl.java) | Revision `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`; SHA-256 `5c57081e34b69cf9f8882a47fb67c8a58b36ea2c687b756a4ee3f119872515e9` | `getFilesDir`, `getNoBackupFilesDir`, `getDatabasesDir`, `getCacheDir`, and `getCodeCacheDir` ensure the corresponding directories exist. Session calls `getFilesDir` before entering the guard. Calling a directory accessor is not a research attempt. |
| [ActivityThread.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ActivityThread.java) | Same base revision; SHA-256 `2d7bd7d9a9978258776a98ffe60589585a215688da303da7c71be7af961dc210` | `setupGraphicsSupport` configures the application cache as temporary storage and sets up graphics caches using a **device-protected** context; called during non-isolated application binding. Do not misattribute these graphics caches to the credential-protected root scanned by Session. |

The Java/C++ upstream files carry Apache-2.0 notices. They are documentary inputs,
not imported implementation or adopted dependencies. Initial web retrieval failed;
initial shell retrieval was network-denied. Approved read-only Gitiles retrieval
then succeeded, including resolution of release refs to the immutable revisions.

**Supported assumption:** the selected context's app data are intact, with no
prior attempt, restore, rollback, concurrent replacement or adversarial writer;
the root contains empty `files` and optionally empty `cache`/`code_cache` only.
The synthetic positive fixtures establish the Java behavior for this state.
They are not a claim that every fresh Android/OEM installation has this layout
at the time a person presses the button. No complete fresh-install layout is
inferred from these three source files.

Empty `databases`/`no_backup`, other directories (including a platform-specific
entry), and nonempty caches can have benign explanations. They are denied as
**ambiguous/unsupported by this admission predicate**, not declared proof of an
earlier attempt. A legitimate installation with such state can be locked out.
Do not delete that state or retry/reset/reinstall to make it qualify.

**Unknown / STOP:** identifying arbitrary platform-created contents as fresh,
qualifying an OEM layout at first button press, authenticating absence after
erasure/rollback, and covering other storage roots require evidence not supplied
here. The guard examines only the context data root supplied by Session, not all
credential/device-protected, external or system-owned state. No permissive content
allowlist, timestamp, inode, owner, filename or generated identifier is adopted
as historical authority. Stop at conservative denial where the supported predicate
does not hold. Any broader admission needs separate exact-platform evidence and
an independent freshness authority; this work does not invent one.

## Actual desktop fixtures and results

Windows x86_64, installed Temurin `17.0.20.1+1`; actual repository Java compiled
with `javac`. Each case used a new real temporary filesystem directory, an empty
`files` child, and a new guard. Residue was the synthetic text
`SYNTHETIC PRIOR ATTEMPT` in a `prior-attempt.txt` child. Directory sync was an
injected counter, not Android fsync. Fixtures were deleted only by their test owner.
No application state or previous research asset was deleted.

| Fixture | Baseline observation | Corrected regression requirement/result |
|---|---|---|
| Empty `files` only | Admitted, two sync callbacks | Admitted; marker and subsequent lockout checked |
| Empty `files`, `cache`, `code_cache` | Admitted, two sync callbacks | Admitted; both cache directories remain empty; also test either cache separately |
| `unexpected/prior-attempt.txt` | Admitted, two sync callbacks | Denied before sync/marker/delegation |
| `databases/prior-attempt.txt` | Admitted, two sync callbacks | Denied before sync/marker/delegation |
| `no_backup/prior-attempt.txt` | Admitted, two sync callbacks | Denied before sync/marker/delegation |
| `cache/prior-attempt.txt` | Admitted, two sync callbacks | Denied before sync/marker/delegation |
| `code_cache/prior-attempt.txt` | Admitted, two sync callbacks | Denied before sync/marker/delegation |
| `shared_prefs/prior-attempt.txt` | Denied, zero sync callbacks | Existing preference rejection controls retained |
| `files/prior-attempt.txt` | Denied, zero sync callbacks | Existing private-file rejection controls retained |

The new regression matrix additionally tests empty unexpected/databases/no_backup
directories, nested empty directories, and a regular file in place of each of the
five siblings. Every denied case checks zero delegation and sync counters, no
marker, preserved evidence, denial by a new guard under intact residue, and the
same guard's permanent latch even after **fixture-only** removal of the residue.
No production cleanup path is added. Wrong-type files are executed controls;
symbolic-link rejection is a source observation, not a Windows symlink test.

Reproduce the baseline witness by compiling the base version of ResearchAttempt
with a same-package Java caller: for each table row create a fresh temp directory,
create `files` and the listed siblings, write the fixed synthetic residue if any,
then invoke `new ResearchAttempt().reserve(data, files, p -> syncs.incrementAndGet())`.
Assert the exact admission/callback counts above, marker presence iff admitted,
and unchanged residue bytes; close each fixture by walking only its owned tree.
The nine-case witness was executed **before editing production source**. It used
the same original guard blob `47403172edabf56570dbda28032e4b70a04f133d` as live main.
The observation is a known omission, not a passing safety test.

Reproduce corrected tests using existing JDK 17, without Android/native execution:

```text
javac -Xlint:all -d <new-output> <main-java>/Protocol.java <main-java>/Report.java <main-java>/LaunchResult.java <main-java>/ResearchAttempt.java <test-java>/ProtocolTest.java <test-java>/ResearchAttemptTest.java
java -cp <new-output> org.pdva.gate0.ProtocolTest
```

Here main/test Java directories are `android/gate0-harness/src/main/java/org/pdva/gate0`
and `android/gate0-harness/src/test/java/org/pdva/gate0`. The unchanged Gradle
`protocolTest` target includes both suites.

- **Executed:** corrected guard **217 assertions**, protocol/report **71 assertions**.
  All earlier tests remain, including exclusive reservation, concurrent callers,
  permanent lockout, legacy false/true/malformed preferences, nonempty files,
  marker preservation, missing/wrong roots and both failed-sync boundaries.
- **Executed negative controls:** compile the unchanged new guard test suite with
  (1) the original guard, (2) a copy changing the unknown-sibling rejection to
  `continue`, and (3) a copy removing nonempty-cache rejection. Each compiled and
  then failed with the intended `reservation check` AssertionError (14, 14 and
  104 respectively). Compilation errors or unrelated failures were not accepted.
- **Executed:** all main/instrumentation Java compiled with `javac -Xlint:all`
  against retained API-37 stubs and release R symbols, without diagnostics.
  This is not Android lint, resource rebuilding or APK correspondence.
- **Executed:** foundation and harness validators; repository suite **149 total,
  145 passed, four existing Windows skips**; desktop-readiness **28**, offline-image
  **45**, frame-copy **4**, all passed. Skips are not passes. Python **3.12.14**.
- JDK executable hashes match the existing [adoption evidence](gate-0-one-way-research-attempt.md):
  java `1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406`,
  javac `9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549`.

**Not run:** new Gradle/APK builds, Android lint, compiled-policy/APK qualification,
Android fsync/durability, VM/guest/emulator/phone/ADB/APK installation, native Windows
controls or local Linux process suites. Full Android CI remains required for these
Java changes; no workflow or assertion is weakened to compensate. Foundation and
Android workflows apply; QEMU is filtered. New-head hosted results are unobserved
at publication and require independent later review, without polling here.

## Preflight, provenance and preservation

Live main matched the supplied SHA. Connected search and REST open-PR collection
both returned zero; all open heads/bases/diffs/files/checks/jobs/logs/reviews/comments/
threads were therefore an empty set. No matching PR existed. Reviewed merged
PR #45–53 identities, changed-file inventories and relevant evidence: readiness,
process-history rejection, managed-restore limits, packaged-policy correction,
one-way guard, negative APK reproducibility, bounded authority STOP, roadmap and
first-physical-test procedure. PR #49 is the source of the current guard; its
broader residual-state language is narrowed by this record.

Exact-main [foundation run 41765419977](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41765419977)
succeeded. Both job/step metadata and actual logs were inspected: foundation
`126362528662`, Windows `126362528872`. The connector workflow wrapper returned
an empty list; the exact-SHA REST collection supplied this run. Android/QEMU were
filtered, not passes. [GitHub Status](https://www.githubstatus.com/api/v2/summary.json)
reported operational systems and no incidents during preflight.

No applicable AGENTS.md was found. The tracked checkout was clean, one worktree,
no stashes; local main was still at PR #52's merge. Created one branch from fetched
live main without moving existing local branches. Existing ignored tools, APKs,
research, caches and private assets remain. New disposable outputs are ignored;
independent private backup is not newly attested. Initial sandbox fixture-directory
creation failed; an approved scoped creation succeeded. Failures are not passes.

Reviewed requirements, ADRs, governance, acceptance criteria, gates, provenance/
adoption/dependency records, manifest, source/test call paths, contribution rules
and all three workflows. ADR-0001 remains Accepted; ADR-0002/0003 Proposed, only
Option A approved. Preserve all fifteen failed APK equality pairs; no repeat or
D1/D2 adoption. New Java changes/tests are original PDVA work, no copied upstream
implementation. No dependency, binary, signing material, incident sample, sensitive
log or private path is published. Intended files are regular text mode 100644.

The Malwarebytes incident remains **unresolved**. The owner's folder exclusion
is not security clearance; no settings or incident investigation occurred.
Independent enrollment, whole-worker/descendant/resource cleanup, recovery,
anti-rollback, exact build/signing qualification and physical support remain
unestablished. This restriction supplies none of those protections.

Publish one focused PR, attach it natively to the requesting chat and verify the
association once. Then stop without polling CI, reviews, comments, bots or
mergeability. A publication/association failure must be reported as UNPRESERVED
pending repair of that same PR under [governance](../governance.md).
