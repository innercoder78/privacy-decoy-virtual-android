# Gate 0: one-way research-attempt reservation

Date: **2026-10-29, America/Fortaleza**. Scope: PDVA-REQ-002–003, 009–015,
035–043, 047–048 and 054. **Gate 0 Unresolved; Gates A–G Not reached. Physical
native-launch readiness NOT READY — STOP.** ADR-0001 Accepted; ADR-0002 Proposed.
This corrects the original research harness, not production lifecycle/recovery.
No device experiment is authorized or performed.

## Baseline, live preflight and provenance

Live main and local HEAD agreed on **`6d0d5b7f0df93c0cf08289987cdf46155da64a05`**,
tree `dd90e3df7e82744049540ab52e289f656579221f`. PR #48 is merged, head
`c97e571994c235b26b28333398426be2de7fb619`, into that exact main. Recent merges
#45–48 and original harness/native-launch history were inspected. The baseline
Session and MainActivity bytes are the same original sources identified in the
[readiness audit](gate-0-native-launch-readiness-audit.md#exact-source-and-analysis-procedure).
Use `git show <baseline>:<path>` for the original and this PR's exact committed
files for the corrected source. New Java/tests/evidence are original PDVA work,
maintained by the repository owner; no upstream implementation was copied.

Both connected GitHub search and the paginated-capable REST open-PR collection
returned **zero**. Thus open heads/bases, complete diffs/files/modes, checks,
jobs/logs, reviews/comments/threads and dependencies were an empty set. No open
PR needed reuse. Read-only Git networking initially failed in the sandbox;
an approved retry independently verified main and exact-commit push workflows.

Exact-main [foundation run 40827813161](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40827813161)
and [Android run 40827812985](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40827812985)
completed successfully. All three jobs and their step metadata/logs were inspected:
foundation `123294789002`, Windows offline controls `123294788693`, Android
`123294787897`. Logs identify the exact baseline checkout. These are baseline
receipts, not results for this change. QEMU's path filter does not apply.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational, no incidents, page update `2026-10-29T05:25:25.715Z`.

Initial checkout: 142 tracked files, clean, one worktree, no stashes. Local
branches and ignored research/build/toolchain/cache/APK assets were inventoried
and preserved. No applicable AGENTS.md was found. No reset, clean, restore,
stash pop, force push or private incident-record modification occurred. The
single new branch required the ordinary sandbox Git-metadata escalation.
Read requirements, gates, acceptance criteria, governance, threat model,
security boundaries, roadmap, both ADRs, provenance/adoption/dependency records,
Android source/UI/tests/build instructions and all three workflows.

Required prior evidence remains applicable: [readiness](gate-0-native-launch-readiness-audit.md),
[lifetime authority](gate-0-android-lifetime-authority.md),
[diagnostic recovery](gate-0-diagnostic-recovery.md),
[process histories](gate-0-process-history-reconciliation.md),
[managed restore](gate-0-managed-restore-lifetime.md),
[capability revocation](gate-0-capability-revocation.md),
[host incident](gate-0-native-host-antivirus.md) and
[packaged policy](gate-0-packaged-extraction-rules.md). No broad lifecycle,
clock, process-history, cgroup or Binder survey is repeated.

## Actual correction and conditional first-use predicate

**Source observation:** [Session](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java)
uses one static [ResearchAttempt](../../android/gate0-harness/src/main/java/org/pdva/gate0/ResearchAttempt.java).
Its synchronized reserve method latches the process before inspecting storage.
Directory enumeration errors fail closed; no `exists()==false` shortcut treats
an access failure as absence. Any `shared_prefs` entry in the application-data
directory denies admission without loading or modifying preferences. This includes
the old `launch_lifetime.xml` containing `uncertain_child=false`, true, a wrong
type, malformed/empty XML, only a backup, or even an empty preference directory.
The old false value can mean a completed earlier launch; it is never migrated.
Any entry in the private files directory also denies admission, including prior
synthetic objects and a zero-length, malformed, wrong-type or complete marker.

Only an enumerably empty private files directory and absent preference directory
qualify **under the explicit assumption that these are intact fresh app data,
with no prior attempt, lost state, restore, rollback or concurrent replacement**.
Absence does not authenticate that assumption. A completely erased/rolled-back
state is indistinguishable from the qualifying empty state; this code cannot
detect it. Unestablished freshness remains a physical-readiness blocker, not a
reason to describe an actual installation as safe to run. Partial/residual state
is conservatively denied, including benign residue. There is no reset, migration,
repair, clear button, alternate unguarded entry or reinstall recommendation.

The guard exclusively creates `files/research-attempt-reserved-v1`, writes the
fixed `RESERVED` record, forces file content/metadata, closes it, then synchronizes
the files directory and its application-data parent. Every operation must succeed
before returning true. Directory synchronization uses public Android `Os.open`,
`fstat`/`S_ISDIR`, `fsync` and `close`; failures, including close failure, deny.
[CREATE_NEW](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/StandardOpenOption.html#CREATE_NEW)
provides exclusive creation without truncating an existing entry;
[Android Os](https://developer.android.com/reference/android/system/Os) provides
the public synchronization calls. These contracts are not storage-failure or
OEM durability measurements. No hidden constant, privileged call or permission
is used. The existing extraction exclusions cover the files domain, without
becoming independent preservation or freshness authority.

**Source observation:** reservation precedes synthetic file creation, native
allocation, the sole isolated bind, INIT capability transfer, RUN and every
LAUNCH request, including protocol negative controls. Failed reservation returns
a bounded UNKNOWN lockout report with no bind. No path deletes the marker or
resets the process latch. The marker is never parsed as a cleanup receipt.
Honest successful direct-child wait, CLEAN, Binder death, STOP, unbind, timeout,
self-termination, cancellation and manager restart cannot reopen intact state.
New UUIDs remain request labels, not admission authority.

MainActivity has two mutually exclusive single-attempt choices (normal or worker
self-death), Stop and explicit sanitized clipboard export. Both choices use the
same guard. Its loop and death-then-normal-session sequence are removed.
Development instrumentation, the only other Session.run caller, now requests at
most one guarded session; its Activity lifecycle hooks do not start another.
All Java call sites were inventoried. There is one isolated bind and one INIT
issuance in Session, no alternate service-start/retry mechanism. A second or late
connection callback is not adopted; disconnect/binding death cancels continuation.
Framework-internal process restart scheduling is not controlled or proved absent.

## Before/after admission transitions

| Event/state | Original source | Corrected source and limit |
|---|---|---|
| Absent key / empty local state | Defaults false; bind and INIT precede durable marker | Conditional fresh-data predicate only; exclusive marker and all syncs before bind. Absence is not authenticated freshness. |
| Existing uncertain_child=false | Eligible if ACTIVE is fresh/cleared | Denied without reading or rewriting old preferences. |
| Existing true / wrong type / malformed data | True blocks; typed read may throw; parser ambiguity not independently rejected | Any preference directory, marker or files residue blocks; access errors deny. |
| Two calls in one manager | ACTIVE excludes temporarily | One static synchronized latch; at most one successful reservation; no reset. |
| Reservation write/sync/close fails | Only late LAUNCH commit checked | No bind or INIT; retain partial evidence and process latch. |
| INIT before child launch / lost INIT reply | No durable attempt; initialized flag may stay false | Already reserved; mark INIT attempted before IPC; best-effort STOP with any known endpoint. |
| Honest child completion / worker CLEAN | Clears uncertain_child before worker/resource closure | Reservation stays; reported_clean is UNKNOWN worker self-report, never independent success. |
| Binder death or new Session/UUID | Can release ACTIVE; restart makes it fresh | Never clears reservation; replacement callback never supplies new authority. |
| Stop/cancellation/timeout/bind failure | Local guard depends on endpoint/late child marker | Reservation persists if admission occurred; cancellation before admission binds nothing. |
| Manager restart with intact reservation | False or missing key can admit | Marker/residue denies, even with a new process latch. |
| Entire state loss or rollback to empty | Unsafe freshness inference possible | Outside intact-state guarantee; still indistinguishable locally. No recovery or readiness claim. |

## Exception, cancellation and cleanup audit

**Source trace, not Android scheduling evidence:**

- Read/commit errors: the latch is taken before enumeration. Exceptions and
  partial write/force/directory-sync/close failure deny. Partial files are retained.
  A failure before creation has no durable marker and delegated nothing; a later
  process cannot infer prior history from absence. No arbitrary-interruption
  persistence theorem is claimed.
- Multiple UI clicks: Activity rejects concurrent UI work; recreated Activities
  and instrumentation still meet the same static guard. A second process object
  after restart meets the marker. No UI loop continues after completion/failure.
- Cancel before admission returns without reservation/bind. Cancel racing with or
  following admission consumes the attempt. Rechecks precede resource work/bind;
  request() refuses cancelled operations except STOP. A race after a check can
  still enter a call; it remains covered by the retained reservation.
- Bind false/throw/timeout, null callback or lost callback retains the marker.
  Binding is marked attempted before the call; best-effort unbind is attempted
  even after a false return or throw, including without a worker. Unbind failure
  is reported UNKNOWN; no retry follows and no independent closure is claimed. Late/replacement
  callbacks are ignored/cancelled; they do not initiate another INIT.
- Manager death before INIT or during its transfer leaves already synchronized
  reservation under intact-state assumptions. `finally` is not promised after
  process death. A partial/lost INIT reply no longer suppresses a possible STOP.
- Lost RUN/LAUNCH response, malformed length/fields/trailing bytes, valid result
  or reported CLEAN all leave admission closed. INIT and LAUNCH reply decoding
  recycle their Parcel even on parsing failure. Native/protocol negative controls
  remain; the same-worker repeated-LAUNCH rejection probe does not reserve anew.
- STOP and post-STOP-check failures are reported UNKNOWN. Unbind, local memory
  release, each FD close, unmap and shared-memory close are independently guarded
  so one cleanup exception does not skip later local cleanup. A timed-out or
  blocked synchronous Binder transaction is not independently cancellable here;
  STOP itself can block. This is a remaining harness availability/cleanup gap.
- Synthetic native control memory is released only if INIT was never attempted.
  Once its address may have escaped, it is retained until manager process exit,
  even after worker return/death. FD close/unmap remain local reference releases,
  not revocation of worker/descendant/external references or copied bytes.
- Binder death records one endpoint event; worker_reaped remains UNKNOWN. The
  manager never treats it, its own death, lease expiry or worker self-kill as
  group death, descendant reap, external FD/map revocation or data erasure.

The reservation only restricts subsequent manager admissions. It does not
constrain hostile work inside the first admitted worker or independently identify
all framework/descendant instances. No new supervisor, service, engine, guest,
Persona policy, networking policy, permission or dependency is introduced.

## Falsifiable validation of this source

Environment: Windows x86_64; existing bundled CPython 3.12.14 and reviewed Temurin
17.0.20.1+1. Java executable SHA-256
`1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406`;
javac `9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549`.
Retained Gradle ZIP matches pin
`bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01`.
Existing AGP 9.4.0, SDK 37, NDK r28c and 185-component/322-artifact dependency
pins/licenses remain unchanged; they are not independently rebuilt or incident-cleared.

- Actual ResearchAttempt.java compiled and ran with real temporary directories:
  **68 assertions**. Covers first conditional success then denial, new guard with
  intact reservation, eight concurrent callers, old false/true/string/int markers,
  malformed/empty XML, empty/backup-only/wrong-type preference directory, corrupt
  or wrong-type new marker, old synthetic residue, missing/non-directory roots,
  both directory-sync failure boundaries and thrown access exception. Original
  evidence bytes are checked unchanged. Directory-sync callbacks are injected;
  these JVM controls do not execute Android fsync or simulate power loss.
- Existing actual Protocol/Report/LaunchResult controls plus self-report-label
  assertions: **71 assertions**. The existing protocolTest Gradle target includes
  the guard suite; no dependency or workflow change is required.
- Three focused Python source-bound tests inspect the actual Session/UI/guard/
  instrumentation, ordering and all call sites. **16 injected source mutants**
  must be rejected, including bypassed admission, missing denial return,
  clear-on-CLEAN, ACTIVE release, skipped partial-INIT STOP, unsafe unbind,
  replacement endpoint, ignored cancellation, UI repetition, permissive legacy/file state, nonexclusive
  creation, omitted file/parent sync and instrumentation death/rebind. These are
  narrow structural contracts, not a Java parser or Android execution.
- All main Java and instrumentation sources compile against existing API-37 SDK
  stubs with `javac -Xlint:all`, with no diagnostics. Uses retained generated R
  symbols (resource names unchanged), not a new resource build or APK. Initial
  compile failed because O_DIRECTORY is not in the public SDK; corrected to
  O_RDONLY plus public fstat/S_ISDIR. No hidden API workaround was introduced.
- Four disposable copies of actual ResearchAttempt.java were separately compiled
  with the unchanged real JVM test suite. Bypassing legacy evidence, bypassing
  marker/residue inspection, admitting failed synchronization and permitting
  in-process retry after failed reads each produced the required specific guard
  AssertionError. Compilation errors, timeout or unrelated failure did not count.
- Foundation validation passed: **145 files, 90 Markdown files, 54 requirements,
  two ADRs**. Repository suite: **149 tests, 145 passed, four existing Windows
  platform skips**. Offline receipt suite: **28 passed**; offline image suite:
  **45 passed**; frame-copy suite: **four passed**. Harness manifest/extraction
  source validation passed. Whitespace and local Markdown links passed.

Initial source-mutant test run had three test-harness errors because removed
anchors raised ValueError before explicit assertions; corrected anchor assertions
now reject those mutants specifically. An initial sandbox Python edit was denied
without changing the file; changes used the supported patch tool. Failed attempts
are not passing results. Initial sandbox receipt/image suite runs stalled in
fixture setup and were interrupted; approved fixture-access runs passed. No
stalled run is counted as a pass.

Reproduction uses the existing JDK and SDK, with a new ignored output directory:
compile Protocol, Report, LaunchResult, ResearchAttempt, ProtocolTest and
ResearchAttemptTest using `javac -d <output>` and run
`java -cp <output> org.pdva.gate0.ProtocolTest`. Compile all main Java plus
HarnessInstrumentation with `javac -Xlint:all`, API-37 android.jar and the retained
R.jar on the classpath. Python commands from the repository root:

```text
python .github/scripts/validate-foundation.py
python .github/scripts/validate-harness.py
python .github/scripts/test-repository-validation.py
python .github/scripts/test-desktop-readiness.py
python .github/scripts/test-offline-image-inspect.py
python .github/scripts/test-frame-copy.py
git diff --check
```

Full Gradle debug/release/instrumentation APK builds and Android lint: **NOT RUN**
locally under the unresolved Windows host-security/build qualification limitation.
Direct JVM compilation is not Android lint. Retained APKs/builds are preserved
and do **not** correspond to the newly changed Java/UI; no historical APK or CI
receipt is claimed as proof of these bytes. Native controls, Android native launch,
phone/USB/ADB/emulator/guest execution, incident samples and security-software
changes: **NOT RUN**. Existing foundation/native, APK/resource, offline receipt
and Android build/lint workflows remain intact. Foundation and Android filters
apply to this PR; QEMU does not. New-head hosted results are **unobserved at
publication** and must be reviewed independently later, without polling here.

## Remaining proof and preservation limits

The smallest genuinely new independent proof remains an ordinary-app-accessible
current-attempt enrollment/inventory and scope-complete closure witness that is
sound through the manager-death/INIT cut and state-loss/restore uncertainty.
It must account for every worker/descendant and delegated resource independently
of worker self-report; disclosed copies require separate treatment. Repeating
these local guard tests, adding a UUID, or observing one Binder death cannot
supply that proof. No recovery transition is implemented.

Incident clearance, source/build/signing qualification for physical execution,
external observation/revocation and full interactive Android feasibility remain
separate blockers. A more conservative harness is not an enforcing security
boundary, complete cleanup proof, Gate 0 pass or phone-test authorization.

Final review covers all intended source/tests/docs, exact regular 100644 modes,
unchanged permissions/native sources/dependency pins/workflows, local links,
whitespace and public-data hygiene. No generated binary, signing material,
private path, incident record/sample, sensitive ID, Persona data or raw private
log is published. New ignored validation outputs are local, not independently
backed up; prior private-evidence recovery gaps remain unverified.

Publish exactly one focused PR, natively attach it, verify conversation metadata
once, then stop without polling CI/reviews/comments/status/bots/mergeability.
Association failure means **UNPRESERVED pending association repair of the same
PR**, not permission to create a duplicate or denial that the GitHub record exists.
