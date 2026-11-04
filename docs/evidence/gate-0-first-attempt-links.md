# Gate 0: first-attempt filesystem links

Date: **2026-11-04, America/Fortaleza**. Verified base/main:
`1a49bc2f495cee543d505b6d2ae8846ef467a1a6` (merged PR #54).
Scope: PDVA-REQ-010–013, 036–043, 048, 051 and 054.
**Gate 0 Unresolved. Physical readiness NOT READY — STOP.**

## Disposition

**Partial direct observation; symlink objective remains Unknown/STOP.** Real
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

**Actual symbolic-link execution is NOT verified.** Java creation failed with
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

| Target | Fixture construction | Actual local result |
|---|---|---|
| Empty directory outside the admission fixture | Separate disposable fixture's empty `files` | First creation unsupported; later cases not reached |
| Directory with synthetic residual evidence | Separate fixture, `evidence` containing `prior attempt` | Not reached |
| Regular file | Separate fixture, synthetic evidence bytes | Not reached |
| Dangling path | Nonexistent child of separate disposable fixture | Not reached |
| Internal directory alias | `files` points to empty `cache`; cache names point to empty `files` | Not reached |

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

## Validation, Linux gap and preflight

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

The unchanged [Android workflow](../../.github/workflows/android-harness.yml)
uses Ubuntu 24.04 and runs the existing `:gate0-harness:protocolTest` task, which
already includes this test file. Creating this PR matches its Android path filter.
It has PR/main-push triggers, no workflow dispatch. New-head Linux execution,
the 15-case symlink matrix and the symlink mutant remain **UNOBSERVED / Unknown / STOP**.
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

## Preservation and exclusions

Original PDVA Java/test/documentation only; no copied upstream implementation,
license change, runtime dependency, binary, permission, native code, manifest,
build pin or workflow modification. Four intended regular text files (100644)
receive full diff, whitespace, local-link and public-data review before commit.
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
