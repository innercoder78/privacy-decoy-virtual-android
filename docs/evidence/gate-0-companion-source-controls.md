# Companion diagnostic source controls

Date: **2026-11-10, America/Fortaleza**. Source baseline: canonical main
`69a7165043e1e7fc565a9ff10f044adc4874c595`. Scope: implement the source controls in
[ADR-0003's bounded preparation plan](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md#companion-only-acceptance-and-preparation--recorded-2026-11-10).
Traceability: PDVA-REQ-008, 036–042, 048, 051 and 054.

The owner explicitly authorized this source implementation, local tests and one
public PR, including normal automatic existing CI. That resolves the earlier
[publication STOP](gate-0-companion-source-controls-stop.md) for this task.
The active metadata configuration remains unchanged. The proposed three lines
exist only in disposable in-memory fixtures and isolated test Git blobs. No
workflow is changed or manually dispatched. Host Option A, companion-only
Option B's **2026-12-08** expiration
(or earlier stated condition), ADR-0004 Option A, all fifteen signed-byte failures
and the original execution lock remain intact.

## Implementation and review boundary

The existing allowlisted [diagnostic test](../../.github/scripts/test-memory-diagnostic.py)
now compares the entire proposed Gradle file byte-for-byte with the exact approved
three-line insertion. It never evaluates Gradle. Every other repository file is
protected by length-delimited SHA-256 of sorted public repository paths and exact
Git blob bytes, partitioned for specific rejection reporting. Counts are pinned
too; additions, deletions, renames and unsupported files fail closed. All entries
must be regular 100644 files. Working-copy checks include nonignored new files,
reject symlinks and conflicts, and check POSIX executable bits before staging.
Ignored build outputs and private assets are outside this source-only comparison.

The public receipt is derived from the exact baseline above: 179 protected files
in build (9), checks (30), cleanup (1), diagnostic (7), governance (109), host (22)
and lock (1) groups. The module's complete baseline text is also pinned. The active
Android and GitHub source at that base is unchanged from ADR-0003's proposed
`0d5b9ba11157040b06466cf626581bcf4e7e08f2` source baseline. Public source fingerprints
are comparison evidence, not independent authentication of this host or toolchain.
Missing, incomplete or different baseline receipts reject admission. No candidate
can supply a new accepted baseline. CI's shallow checkout needs no network fetch;
an explicit local procedure recomputes the receipt from actual baseline Git blobs.

Exactly three preparation files require full independent review outside the
protected-content comparison: this record, `docs/evidence/README.md`, and
`.github/scripts/test-memory-diagnostic.py`. They must exist and retain regular
modes. There is no caller-supplied allowlist. Their enumeration does **not** prove
review, make arbitrary edits to the verifier safe, or authorize another scope.
The verifier cannot authenticate its own implementation or human approval.
Any further control/evidence change requires explicit review; all other source
drift rejects. The result is only an exact source-delta check, never operational
admission, an expiry renewal, signing approval or a physical-test artifact.

## Procedures and observed results

Direct observations on Windows in Codex Desktop LOCAL, bundled CPython 3.12.14
and the existing Temurin JDK **17.0.21+9** installation. These are executed controls, not
independent host/tool authentication. From the repository root, use the local
Python executable in place of `python`; `JDK_HOME` below denotes the existing
JDK directory, not a public private-path receipt.

| Exact procedure | Observed outcome |
|---|---|
| `python .github/scripts/test-memory-diagnostic.py` | Exact in-memory proposal accepted; **60 separate negative controls** rejected at their expected source assertion; **60 detector-removal negative assertions failed because the defective input was accepted**. Five actual detector bodies were independently removed through AST compilation. Each mutant also accepted the positive fixture. Arbitrary errors do not count. Existing RWX and INTERNET source controls passed. |
| Same script with `--verify-source-baseline` | Recomputed all 179 protected public Git blobs and regular modes against the exact base; complete original Gradle bytes matched. No remote fetch or candidate-derived replacement baseline. |
| Same script with `--java-home JDK_HOME` | Repeated the final source suite; **190 diagnostic JVM assertions passed**, real compiled cleanup-removal mutant failed the expected behavioral assertion, actual Activity bytecode passed initiation/recreation controls with desktop framework doubles. No Android runtime result. |
| `python .github/scripts/validate-foundation.py` and `python .github/scripts/validate-harness.py` | Passed: **183 files, 112 Markdown files, 54 requirements, four ADRs**; source manifest authority passed. |
| `python .github/scripts/test-repository-validation.py` | **152 tests: 148 passed, four existing Windows skips**. Skips are not passes or Linux/native execution. |
| `python .github/scripts/test-desktop-readiness.py`; `python .github/scripts/test-offline-image-inspect.py`; `python .github/scripts/test-frame-copy.py` | **28, 45 and 4 tests passed**, respectively. Existing synthetic transport/package fixtures retain their limited labels. |
| `python .github/scripts/test-gradle-distribution.py` | **38 tests passed**. This existing suite uses synthetic distributions and mocked Gradle invocations; it supplies no real Gradle/STRICT runtime result. |
| `python .github/scripts/test-installed-tools.py` | Two sandbox attempts each completed 16 tests with **one error**: `test_real_directory_redirection` timed out at the existing ten-second disposable Windows junction creation. The identical full suite with scoped execution access outside the sandbox then **passed all 16 tests**. No test, timeout or system security setting changed. The scoped rerun resolves execution for this run, not independent input authentication. |

The default source suite also performs genuine command-line integration. In a
new temporary Git repository, `git fast-import` creates only synthetic source
objects; the only fixture worktree file is this Python verifier. It runs
`--check-source-ref refs/heads/fixture` against the exact proposal and requires
exit 0 with the source-only receipt. The base commit is deliberately absent.
`--verify-source-baseline` must then fail with Git `rev-parse` exit 128, not
silently adopt the fixture as a baseline. These two subprocess checks passed.
The fixture commits are never pushed; no active Gradle file is edited or evaluated.

Negative coverage includes missing/duplicate/true metadata, wrong DSL location,
root/global/host overrides, added hooks/plugins/dependencies, API/namespace/app/
version/variant drift, enabled debug, release flags, both signing configurations,
bundle opt-out, distribution routes, JNI/native/network/permission additions,
execution-lock removal, each close/RW/RX cleanup removal, attempt reset,
deleted/skipped/filtered checks, suppressed failure, expected-failure conversion,
passing wrapper, added comparator, executable/symlink/gitlink modes, deleted
protected files/module/review files, unsupported new scope and absent/wrong/
incomplete baseline evidence. Every case starts from the passing exact proposal;
its corresponding detector removal must admit that same defective input before
the negative assertion is required to fail. No broad catch converts unrelated
exceptions, compilation errors or timeouts into success.

The first source/baseline run failed because the newly embedded original Gradle
fixture contained one extra blank line. Comparison correctly rejected it. The
fixture was corrected against the Git blob; the actual module was never edited.
Subsequent final source, Git integration, baseline and JVM runs passed as above.

## Live preflight and final review

Read-only Git and paginated REST agreed on the baseline SHA above; connector
search and REST both returned **zero open PRs**, so open heads/bases/full diffs/
files/modes/checks/jobs/logs/reviews/comments/threads were an empty set. PR #73 is
merged. Reviewed relevant local history, ADRs, requirements, acceptance/governance,
diagnostic source and validators, source catalog, adoption/dependency ledger and
all three workflows. The tracked binary-extension scan returned no package/tool
binaries; ignored assets and private inventories were not enumerated or qualified.
No stashes or primary-checkout dirt existed initially; all six existing worktrees
and their branches were preserved, and a new implementation branch was created.

Exact-main [Foundation run 42865094202](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42865094202)
reported success for `foundation` (130001185606) and `offline-image-windows`
(130001185238). Check/job/step metadata and completed logs were retrieved. No
exact-main Android or QEMU run was listed; absence is not a pass. These are
baseline results, not execution of the new source suite. Legacy commit status
has no contexts and is not substituted for these check runs. Live branch protection
returned **404 Branch not protected** and rulesets returned an empty list. No
settings were changed; required-check enforcement and independent review remain
separate qualification obligations, not properties this source verifier proves.

[GitHub Status](https://www.githubstatus.com/api/v2/summary.json), snapshot updated
`2026-11-10T17:29:30.039Z`, reported **Partially Degraded Service**: Pull Requests
degraded, Actions operational. Successful reads establish only those requests.
Initial sandbox Git/REST network failures were resolved with scoped execution
access. No service health, test success or publication result was invented.

The final scope is exactly the existing diagnostic test, this focused record and
its index entry, all regular 100644 text. Full diff, whitespace, public-data
hygiene, baseline fingerprints, provenance/rights, dependency absence and workflow
applicability were inspected. The original test functions and existing checks
remain in place. No validator allowlist, workflow trigger, source pin, metadata
configuration, protected source, requirement, ADR or historical failure record
changes. The extension uses Python's standard library and existing Git/JDK;
review of existing ledgers is not fresh independent rights/security clearance.

## Qualification and preservation limits

Source checks do not prove evaluated AGP packaging, absence of signing-block
metadata, signing, reproducibility, Android security, lifecycle cleanup or device
support. Independent source/build/security reviewers, authenticated provisioning
and inputs, Windows-incident disposition or a qualified replacement chain,
dedicated signing custody/verifier, genuine independent signed builds and strict
complete-byte comparison, private retention/transfer and exact-artifact physical
authorization remain required under ADR-0003. Existing CI builds do not discharge
that qualification packet. No new dependency, third-party source, binary, license
grant, rights clearance or runtime adoption is introduced by this original
standard-library extension.

**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**
**Independent backup UNVERIFIED; private evidence UNPRESERVED.** No private paths,
hashes, inventories, keys, receipts, binaries or APKs are published. Existing
worktrees, branches, ignored assets and private evidence are preserved. No local
Gradle/APK build, Android CLI, signing, key operation, artifact delivery, ADB/USB,
phone installation, native/guest execution or security-setting change is run.

Foundation and Android CI apply through the unchanged workflows; QEMU's existing
path filters do not select this diff. Automatic CI is allowed to run normally.
New-head hosted checks are **UNOBSERVED at publication**, not passing. Publish one
PR, attach it natively to this chat, verify association once and stop without
polling CI, reviews, comments, bots, badges or mergeability. PR publication is not
merge into canonical main or independent private preservation.
