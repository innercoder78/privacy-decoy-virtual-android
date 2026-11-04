# Gate 0: first-attempt filesystem links

Date: **2026-11-04, America/Fortaleza**. Verified base/main:
`1a49bc2f495cee543d505b6d2ae8846ef467a1a6` (merged PR #54).
Scope: PDVA-REQ-010–013, 036–043, 048, 051 and 054.
**Gate 0 Unresolved. Physical readiness NOT READY — STOP.**

## Disposition

**Normal Linux symlink rejection verified at `2f1301606cad0fe4e69351f5daf7c3bc48c5ccef`;
the NOFOLLOW_LINKS mutation execution remains Unknown/STOP.** The continuation
below records exact-head CI evidence and adds the mandatory mutation runner.
Production code and all 15 existing Java fixtures are unchanged by this follow-up.

**Original Windows finding:** Real
Windows directory junctions exposed a narrow admission gap: the installed JDK
reports a junction as both `isDirectory()` and `isOther()` under
`NOFOLLOW_LINKS`. PR #54 tested only the first flag. Junctions substituted for
each of `files`, `cache`, and `code_cache` authorized a reservation in actual
disposable fixtures. This is a desktop provider observation, not evidence of an
Android exploit or Android junction semantics.

The narrow correction rejects entries classified as symbolic links or `other`,
in addition to non-directories. All three corrected junction cases passed the
same committed rejection/preservation oracle used by the new symlink tests.
Removing only `|| attributes.isOther()` in a separately compiled disposable
copy made all three cases fail with `AssertionError: filesystem alias admitted`.
Compilation errors and unsupported fixture creation did not count as successful
negative controls. No other production behavior is changed.

**Original Windows symbolic-link execution was unsupported.** Java creation failed with
the Windows required-privilege error, both within and outside the sandbox.
No privileges or security settings were changed. The final JVM run compiles,
passes the existing 217 guard assertions, then exits nonzero at the first real
symlink creation. The subsequent 71 protocol/report assertions are not reached.
This is an unsupported local case and an incomplete suite, never a pass.

## Proposition and limits

For stable, fixture-owned roots supplied consistently as `data` and its `files`
child, an enumerated entry named `files`, `cache`, or `code_cache` that is a
symbolic link or a provider-marked directory alias must not authorize research.
Denial must precede marker creation, sync callbacks and caller-side delegation;
existing names, object types, link destinations and regular-file bytes must remain
unchanged. The original positive and permanent failure-lockout controls remain.

The [previous residual-state evidence](gate-0-first-attempt-residual-admission.md)
and [one-way guard evidence](gate-0-one-way-research-attempt.md) retain their
scope. The new oracle counts delegation only when `reserve()` returns true.
[Session](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java)
independently returns before allocation/bind/INIT on denial. No actual Android
delegation, directory fsync, device or payload runs in these JVM tests.

The supplied root and its ancestors remain trusted preconditions. Root/ancestor
aliases, inconsistent caller-supplied `files`, bind mounts, provider aliases not
identified by these attributes, concurrent adversarial replacement, inode/owner
authentication, rollback and authenticated state loss are **not established**.
`NOFOLLOW_LINKS` on one attribute lookup is not race-proof traversal. No claim
of independent freshness, recovery, hostile-worker containment or cleanup follows.
Snapshots compare object classifications, symlink targets and bytes, not all
filesystem metadata or historical identity. No timestamp-based authority is used.

## Committed real-symlink matrix

[ResearchAttemptTest](../../android/gate0-harness/src/test/java/org/pdva/gate0/ResearchAttemptTest.java)
adds 15 cases: each of the three allowed names against five target shapes.

| Target | Fixture construction | Original Windows result | Linux at `2f13016` |
|---|---|---|---|
| Empty directory outside the admission fixture | Separate disposable fixture's empty `files` | First creation unsupported; later cases not reached | Three names passed |
| Directory with synthetic residual evidence | Separate fixture, `evidence` containing `prior attempt` | Not reached | Three names passed |
| Regular file | Separate fixture, synthetic evidence bytes | Not reached | Three names passed |
| Dangling path | Nonexistent child of separate disposable fixture | Not reached | Three names passed |
| Internal directory alias | `files` points to empty `cache`; cache names point to empty `files` | Not reached | Three names passed |

No target is real application/private data. Snapshots explicitly avoid traversing
symbolic links and `other` entries; external targets are inspected through their
separately owned fixture roots. Cleanup walks only disposable symlink fixtures
without FOLLOW_LINKS and deletes links themselves. Junction fixtures used locally
are retained under ignored build output, not recursively removed.

Each completed symlink case must prove zero delegation/syncs, no marker, equal
before/after snapshots, rejection by a fresh guard, and permanent same-guard
lockout after fixture-only link removal. No exception-to-skip handling exists.
An unsupported filesystem or privilege error fails the task. The test does not
weaken existing assertions or alter the original fixture implementation.

The empty-directory cases are the discriminating symlink negative control:
in a disposable source copy remove the `NOFOLLOW_LINKS` argument from the entry
attribute lookup. Following an empty directory link then admits the attempt and
must fail the `filesystem alias admitted` assertion. File/residual/dangling cases
also exercise denial but are not alone proof that no-follow handling matters.
**This symlink mutant has not executed successfully here; its result is Unknown.**

## Actual junction controls and reproduction

Environment: Windows x86_64; retained Temurin **17.0.20.1+1** and PowerShell;
Python **3.12.14** for repository checks. No new dependencies. The actual JVM
guard and committed `rejectedAlias` oracle are compiled using `javac -Xlint:all`.
For each name, a fresh ignored fixture contains `data`, `target`, and an adjacent
regular `evidence` file with `synthetic evidence`. Create empty `data/files`
unless `files` itself is the alias; create a real PowerShell directory junction
at `data/<name>` pointing to `target`. All paths belong to this disposable fixture.

| Variant | files | cache | code_cache |
|---|---|---|---|
| Actual base guard, before correction | Admitted; rejection assertion failed | Admitted; rejection assertion failed | Admitted; rejection assertion failed |
| Corrected actual guard, shared committed oracle | Denied; preservation passed | Denied; preservation passed | Denied; preservation passed |
| Disposable mutant removing only `isOther()` rejection | Expected admission AssertionError | Expected admission AssertionError | Expected admission AssertionError |

Each variant uses newly created directories; never reuse an admitted fixture
whose marker would mask the defect. Baseline and mutant fixtures retain their
markers. Corrected cases have none, no sync calls, intact empty targets and
unchanged synthetic evidence. Junction identity is checked with `Files.isSameFile`
before and after. The final corrected/mutant run was repeated after the snapshot
helper was changed to avoid traversing `other` entries; all six outcomes held.

Minimal equivalent JVM driver, saved only in a new ignored output directory:

```java
package org.pdva.gate0;
import java.nio.file.*;
public class AliasWitness {
    public static void main(String[] args) throws Exception {
        Path root = Path.of(args[0]), data = root.resolve("data");
        Path alias = data.resolve(args[1]), target = root.resolve("target");
        if (!Files.isSameFile(alias, target)) throw new AssertionError("not an alias");
        ResearchAttemptTest.rejectedAlias(data, data.resolve("files"), target);
        if (!Files.isSameFile(alias, target)) throw new AssertionError("alias changed");
        try (var paths = Files.list(target)) {
            if (paths.findAny().isPresent()) throw new AssertionError("target changed");
        }
        if (!Files.readString(root.resolve("evidence")).equals("synthetic evidence"))
            throw new AssertionError("evidence changed");
    }
}
```

Compile that driver with the actual `ResearchAttempt.java` and
`ResearchAttemptTest.java` to a new output directory, then run
`java -cp <classes> org.pdva.gate0.AliasWitness <fixture-root> <name>`.
PowerShell fixture creation uses `New-Item -ItemType Directory` and
`New-Item -ItemType Junction -Path <fixture-root>/data/<name> -Target <fixture-root>/target`.
Use `Set-Content -NoNewline` for the synthetic evidence. For the negative control,
copy the production source, require exactly one ` || attributes.isOther()` anchor,
remove it, compile with the unchanged tests/driver, and require nonzero Java exit
with the specific `java.lang.AssertionError: filesystem alias admitted` diagnostic.
Do not accept compilation failure, timeout, fixture error or another exception.

## Initial publication validation, Linux gap and preflight (historical)

- Direct `javac -Xlint:all` for the six JVM sources: passed without diagnostics.
  Full final JVM execution: **failed/unsupported at symlink creation**, after
  217 existing guard assertions. No full-suite or protocol/report pass claimed.
- All main and instrumentation Java compiled against retained API-37 `android.jar`
  and release `R.jar`, without diagnostics. This is not Android lint, resource
  rebuilding, signed APK correspondence or physical qualification.
- Foundation and harness validators passed. Repository suite: **149 total,
  145 passed, four existing Windows skips**. Desktop-readiness **28**, offline-image
  **45**, frame-copy **4** passed. Skips are not passes.
- New Gradle APK builds, Android lint and compiled-policy checks: **NOT RUN locally**
  under the existing Windows host qualification limitation. No native Windows
  research executable, phone, ADB, emulator, VM, guest or APK installation ran.

At initial publication, the unchanged [Android workflow](../../.github/workflows/android-harness.yml)
uses Ubuntu 24.04 and runs the existing `:gate0-harness:protocolTest` task, which
already includes this test file. Creating this PR matches its Android path filter.
It has PR/main-push triggers, no workflow dispatch. New-head Linux execution,
the 15-case symlink matrix and the symlink mutant were **UNOBSERVED / Unknown / STOP**.
Publication is not execution evidence. The instruction to stop after native PR
attachment precludes polling to collect a new-head result; no workflow is changed
to work around that instruction. Reopening requires independent exact-head Linux
logs and an actual discriminating symlink-mutant failure, plus required build/lint
results. This PR does not close the originally untested symlink control.

Live main matched the stated base. Search and REST open-PR collections were empty,
so there were no open head/base diffs, jobs, reviews or threads to inspect. PR #54's
complete four-file diff and metadata were reviewed; comments, reviews and threads
were empty. Relevant merged guard/residual/history, requirements, ADRs, governance,
acceptance criteria, gates, all three workflows, build pins, dependency inventory,
provenance and modes were inspected. ADR-0001 remains Accepted; ADR-0002/0003 remain
Proposed, with only Option A approved. All fifteen failed APK equality pairs remain.

Exact-base [Android run 41859393543](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41859393543)
and [foundation run 41859393384](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41859393384)
succeeded. Actual job metadata/steps/logs were inspected for Android `126676695092`,
foundation `126676695883`, and Windows `126676695033`. Android logs include 217
guard/71 protocol assertions and successful build/lint; these are **base-only**
results, not this change's qualification. QEMU is filtered, not passed.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) at preflight reported
Actions partial outage, degraded webhooks/Pages, incident `xr3myzj7ms51` (summary
updated 2026-11-04 16:17 UTC). No CI fault is inferred from this status alone.

Initial sandbox branch/output/network denials and unavailable PATH Python/Java
were resolved with scoped authorization and retained development tools. Actual
Windows symlink privilege failure persisted and remains a failure.
An initial evidence link used the wrong workflow filename; foundation validation
rejected it, and the link was corrected to the existing `android-harness.yml`.
JDK SHA-256 identities match the [previous guard record](gate-0-first-attempt-residual-admission.md):
java `1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406`,
javac `9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549`.

## Continuation: exact-head Linux verification and mandatory mutation control

On 2026-11-04, the owner authorized continuation of **existing PR #55 only**,
including the smallest additional Ubuntu CI control, one final commit/push, then
attachment verification and STOP. The live main remained
`1a49bc2f495cee543d505b6d2ae8846ef467a1a6`; PR #55's exact head remained
`2f1301606cad0fe4e69351f5daf7c3bc48c5ccef`. It was the only open PR in search
and REST collections. Complete diff/files/modes/commit, check metadata and all
three jobs' actual logs were inspected. Comments, reviews and threads were empty.

**Direct CI-log observation:** [Android run 41871456921](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41871456921),
job `126719350567`, checked out that exact head on Ubuntu 24.04 runner image
`20261025.353`, Temurin **17.0.21+9**. The 16:51:38 UTC output explicitly reports
217 guard assertions, 15 real symlink cases, and 71 protocol/report assertions
passed. Build of debug/release/instrumentation APKs and `lintDebug` completed
successfully. Packaged-policy tests: five passed; the malformed-APK negative
control's `Unknown chunk type` diagnostic did not represent a failed job.

[Foundation run 41871456198](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41871456198)
also checked out that exact head. Foundation job `126719347391` (Ubuntu image
`20261101.360`) and Windows job `126719346644` passed. Repository, receipt, image,
frame-copy and existing Linux controls remain separately scoped evidence.
These logs establish normal Linux fixture execution, **not mutant detection**.
QEMU remained filtered. [GitHub Status](https://www.githubstatus.com/api/v2/summary.json)
reported all systems operational, no incidents (summary updated 18:36:25 UTC).
The earlier outage and unsupported Windows attempts above remain historical facts.

### Executable control and acceptance rule

The new original PDVA standard-library script
[test-research-attempt-mutation.py](../../.github/scripts/test-research-attempt-mutation.py)
runs in a mandatory step of the existing Ubuntu Android job **after** the unchanged
build/lint/normal JVM step. Existing native/package/policy validations remain
mandatory. No continue-on-error, skip, suppressed assertion, dependency, permission,
signing, runtime architecture or production/test-Java change is introduced.
The foundation allowlist adds exactly this text script; its binary restrictions
are unchanged. Three runner regression methods join the existing repository suite.

Run `python3 .github/scripts/test-research-attempt-mutation.py` with JDK 17 selected
through `JAVA_HOME` (as the existing CI step does). It copies the six applicable
production/test Java files byte-for-byte into a new temporary normal directory,
compiles with `javac -Xlint:all`, and requires successful execution plus all three
normal-suite completion lines and empty stderr. A failing normal test aborts
before mutant compilation and cannot become expected-failure success.

Then a separate temporary directory receives the same sources/tests, except that
the single uniquely matched `Files.readAttributes(entry, BasicFileAttributes.class,
LinkOption.NOFOLLOW_LINKS)` call is changed to its following-links overload.
The replacement preserves every byte outside that lookup, including line endings;
missing/duplicate anchors fail. Neither `isOther()` rejection nor tests are changed.
Both compilations must succeed independently (60-second timeout); each JVM run has
a 30-second timeout and its own test-owned `java.io.tmpdir`.

The unchanged `ProtocolTest` entry point executes the existing guard controls then
the symlink matrix. Its first case is `files` linked to a separately owned empty
directory. Source inspection predicts admission by the mutant and rejection by
the existing shared oracle. **This prediction is not an executed mutant result.**
The runner requires exit **1**, exactly the existing 217-assertion completion line
on stdout, and the exact uncaught `java.lang.AssertionError: filesystem alias admitted`
header followed only by the expected `rejectedAlias → symlinks → run → ProtocolTest.main`
stack frames. Other exits, missing output, fixture/privilege errors, cleanup errors,
timeouts, compilation failures and unrelated exceptions fail the runner.
Only after exact validation does the runner print the observed mutant stack trace.
Original source bytes are rechecked in `finally`; successful cleanup and that
preservation check precede the only mutant-success message:
`PASS: NOFOLLOW_LINKS mutant rejected by filesystem alias admitted`.

### Continuation validation and remaining STOP

The three new Python tests passed locally, covering unique/exact LF and CRLF
mutation, precise versus invalid modeled subprocess outcomes, and mandatory
failure propagation for normal execution, compilation and timeouts. These are
**modeled runner tests**, not real Linux symlink/mutant evidence. The full repository
suite passed **148 of 152 tests, four existing Windows skips**. Foundation and
harness validators passed. Production and applicable Java tests are byte-identical
to the verified `2f13016` source. Full Gradle/APK/lint runs were not repeated locally.

Actual local invocation of the new runner compiled the normal sources but failed
with nonzero normal-JVM exit on Windows; it did not reach mutant compilation or
print mutant success. The earlier required-privilege symlink failure remains an
unsupported Windows result. A separate disposable local check compiled the actual
mutant with unchanged tests successfully, then observed exit 1 after the 217 guard
assertions and a `FileSystemException` at `createSymbolicLink`. The real runner's
result classifier rejected that outcome; it was **not** the required admission
assertion and is not a successful mutation control. Both original and mutant
compilations are verified locally; Linux mutant execution is still unverified.
No local Linux execution environment was used; no VM,
guest, device, ADB, installation or security-setting change was attempted.

**Mutation result at this update: Unknown/STOP, pending actual Ubuntu execution.**
The one authorized final push will schedule the existing workflow with the new
mandatory step. New-head CI results are not known before that push, and polling
after publication/attachment is prohibited. Independent follow-up must confirm
exact new-head successful normal build/lint/JVM results and the precise runner
success message; earlier head results cannot establish this new runner executed.
No additional production defect was demonstrated in this continuation.

## Preservation and exclusions (initial publication and continuation)

Original PDVA Java/test/documentation only; no copied upstream implementation,
license change, runtime dependency, binary, permission, native code, manifest,
build pin modification. The initial four regular text files (100644) received
full diff, whitespace, local-link and public-data review before commit. The
continuation adds only the documented mandatory CI step, original Python runner,
runner regression tests, exact source allowlist entry and evidence/index updates;
the same complete-diff/privacy/mode/link checks apply.
No credentials, signing assets, private paths, incident samples or raw private
logs are published. No applicable AGENTS.md was found. Original tracked checkout
was clean, one worktree, no stashes; existing branches and ignored assets remain.
Local synthetic fixtures are retained separately from existing evidence. Independent
backup of private assets is not newly attested; the private recovery gap remains.

The [Malwarebytes incident](gate-0-native-host-antivirus.md) remains **unresolved
and deferred**; the owner's folder exclusion is not clearance. Security settings
were not changed. Exactly one evidence PR is to be published, natively attached
to the requesting chat and verified once, then STOP without CI/review/comment/bot/
mergeability polling. Association failure requires repair of that same PR under
[governance](../governance.md), never a duplicate.
