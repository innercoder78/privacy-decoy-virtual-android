# Companion diagnostic source controls

## Gradle installation-level precedence — 2026-11-16

**Runtime Observation:** installation `gradle.properties` selected OFF or LENIENT
when the trusted CLI selection was absent. With `--dependency-verification=strict`
present, both files selected STRICT and the deliberately incorrect dependency
checksum was rejected. **Production-boundary Observation:** the unchanged bootstrap
rejected each altered installation copy before its execution call. These are
separate results; the disposable runtime invocation does not grant production
admission to a modified distribution.

This extends the [existing Gradle runtime record](gate-0-gradle-strict-runtime.md),
specifically PR #64's installation-level **NOT RUN** row. Its ten historical
project/user-home controls and PR #59's synthetic integrity experiments were not
repeated as new runtime evidence. The existing regression suite was run unchanged.
Traceability: PDVA-REQ-010, 036–042, 048, 051 and 054.

### Exact baseline, publication boundary and tools

Canonical live main was `4c2ebd5177172ac2d20ca4383a50fdd17e083283`, agreed by
`git ls-remote origin refs/heads/main`, `git fetch origin main` and
`git rev-parse origin/main`. PR #79 was merged; all-open-PR search returned zero,
so open heads/bases/diffs/files/modes/checks/jobs/logs/reviews/comments/threads
were an empty set. Exact-main [Foundation run 43909808438](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43909808438)
and [Android run 43909808482](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43909808482)
completed successfully. Foundation job 133448319171, Windows job 133448319892 and
Android job 133448319297, their steps and completed logs were inspected. This is
base evidence, not new-PR CI. GitHub Status reported All Systems Operational,
updated `2026-11-16T20:54:41.478Z`; repository API reported push/admin rights.
Reviewed PR #59/#64 diffs and empty discussions, relevant bootstrap history,
requirements, four ADRs, source controls, workflows and tool/dependency adoption
records. Existing main, worktrees, branches, ignored assets and private evidence
were preserved in place; a separate exact-base worktree held this research.

The source checker admits only its enumerated review files outside the exact
companion delta. Actual prospective one-newline edits to the existing Gradle
runner and Gradle evidence file were rejected with **protected-checks** and
**protected-governance**, respectively. These were in-memory candidate snapshots;
neither protected file was edited. Consequently this public change is docs-only,
in this existing reviewable evidence record and the evidence index, linking the
historical Gradle record. No new script admission, historical pin update, source
exception, workflow change or protected-source policy decision is introduced.

Windows x86_64 desktop execution used existing CPython **3.12.14**, Gradle
**9.6.0** and Eclipse Adoptium Temurin **17.0.21+9** (runtime Java **17.0.21**).
The existing archive matched the unchanged bootstrap pin; the production validator
accepted the full original extracted tree against that same archive snapshot.
Both copies matched before deliberate mutation. Complete original distribution,
archive and JDK file-content/type/size/mtime observations were captured before and
compared after the experiment. Production verification XML was compared unchanged.
No tool download, installation, upgrade, dependency or binary adoption occurred.
Private paths, inventories, raw receipts, generated artifact hashes and logs are
not published. All inputs and local observations remain **UNTRUSTED**.

### Source evidence and binary correspondence limits

Fresh immutable source reads at Gradle revision
`3f750f03d77e42327c5f9fcb9992110088330a32` confirm the
[previously documented conversion path](gate-0-gradle-strict-precedence.md#exact-upstream-source-observations):
`LayoutToPropertiesConverter` loads recognized installation properties before
project and user-home properties; `BuildOptionBackedConverter` applies properties
before CLI; `EnumBuildOption` applies a present CLI enum to the same target;
`DependencyVerificationModeOption` binds the property and CLI mode selectors.
`StartParameterResolutionOverride` selects no verification for OFF, whereas
`ChecksumAndSignatureVerificationOverride` logs fatal checksum errors in LENIENT
and throws the verification exception in STRICT.

Fresh `javap -p -c` inspection of the four precedence classes in the
archive-matched installation confirmed those conversion calls, ordering and mode
setter. Its embedded build receipt identifies 9.6.0 and the same source revision.
This corroborates the scoped source explanation; a vendor self-report and matching
bytecode behavior are **not independent source-to-binary reconstruction**. That
qualification remains Unknown and cannot be admitted as passed. The bootstrap and
fixture source bytes used locally matched the exact base Git blobs. No altered
production source or claimed rebuilt Gradle binary supplied the observation.

### Disposable procedure and exact invocation

Two fresh, explicitly UNTRUSTED copies of the complete installed distribution and
pinned archive were created in ignored private research storage. Only each copy's
new root `gradle.properties` was deliberately added, containing exactly one line:
`org.gradle.dependency.verification=off` or
`org.gradle.dependency.verification=lenient`. Original installation and archive
were never changed. Each case received a fresh project, Gradle user home, HOME and
temporary directory; neither project nor user home contained `gradle.properties`.

The runner reused PR #64's exact Groovy `BUILD` and POM constants and deterministic
resource-only JAR recipe, confirming correspondence with that historical fixture.
The local file Maven repository exposed only the invented nontransitive dependency
`org.pdva.fixture:sample:1.0`. POM metadata verification stayed enabled and correct;
only the JAR's expected SHA-256 was 64 zeroes. No real production dependency or
metadata was substituted. Correct-checksum/project/user-home runtime controls were
not rerun; their prior observations remain historical, not new desktop results.

The pinned Windows launcher uses Java `-jar` on its CLI JAR. The probe invoked
that exact entrypoint directly, avoiding shell argument interpretation. For each
case, the private receipt retained this argument vector with resolved paths:

```text
<existing-jdk>/bin/java.exe -Xmx64m -Xms64m -Dorg.gradle.appname=gradle
  -jar <untrusted-copy>/lib/gradle-gradle-cli-main-9.6.0.jar
  -p <fixture-project> --no-daemon -g <fixture-gradle-home>
  --dependency-verification=strict --offline --console=plain --stacktrace
  --no-build-cache --no-configuration-cache --max-workers=1 --no-watch-fs
  -Duser.home=<fixture-home> -Djava.io.tmpdir=<fixture-tmp>
  -Porg.gradle.dependency.verification.console=verbose resolveFixture
```

The child environment was an explicit allowlist: selected JAVA_HOME/PATH,
SystemRoot/WINDIR, isolated HOME/USERPROFILE/GRADLE_USER_HOME, TEMP/TMP and isolated
APPDATA/LOCALAPPDATA. No real Gradle home, SDK, Android project, injection variable,
credential or inherited user cache was supplied. Each invocation had a 90-second
wait bound and timeout tree-termination handler; no timeout occurred, so timeout
cleanup effectiveness was not tested. Offline is a Gradle option, not independently
observed network isolation or an administrative sandbox.

Within each pair the second command removed **only** the literal trusted STRICT
argument. It retained its own case-local cache and identical inputs; no cache was
imported or swapped. Prior generated receipt and report directory were moved aside
inside that case, so they could not satisfy later assertions. The task ran anew;
FROM-CACHE, UP-TO-DATE, SKIPPED and NO-SOURCE markers were rejected. Fresh receipts
recorded actual mode, offline state, Gradle/JDK/vendor and resolved artifact bytes
or exception causes. Fixture input bytes and the complete disposable tool/archive
snapshot were checked after every invocation.

### Actual outcomes and falsifiers

Four invocations completed **18:44:26–18:45:33 America/Fortaleza** on 2026-11-16
(21:44:26–21:45:33 UTC). All reported 9.6.0, Java 17.0.21, Eclipse Adoptium and
offline true. No generic exit or build-failure message alone counted as evidence.

| Installation property | Trusted STRICT | Actual mode / exit | Observed dependency behavior |
|---|---|---|---|
| OFF | Present | STRICT / 1 | Unresolved; actual verification exception in receipt cause chain and stack; fresh HTML report and console identify expected/actual checksum mismatch |
| OFF | Removed only | OFF / 0 | Exact generated JAR resolved; no verification failure or report |
| LENIENT | Present | STRICT / 1 | Same specific checksum rejection and fresh report |
| LENIENT | Removed only | LENIENT / 0 | Exact generated JAR resolved; mismatch printed and a fresh HTML report generated |

Both STRICT failures contained
`org.gradle.api.internal.artifacts.verification.exceptions.DependencyVerificationException`.
The report parser required the artifact name and exact expected/actual checksum
pair, and successful resolution required the generated artifact's exact name and
hash. Missing artifacts, parser errors, task not reached, wrong mode, incomplete
receipt, stale output, input drift and timeout could not count as successful
controls. The strict-mode/unresolved assertion failed on both token-removal
observations, demonstrating that the changed command exercised the intended guard.

Separately, unchanged production `main()` was called with its ROOT and user home
redirected only to each disposable tree, a forbidden-download trap and a mocked
execution sentinel. Each pristine copy reached the sentinel once (positive
control). Each added property caused **Unexpected installed distribution entry**
and zero execution calls (negative control), repeated after runtime. Removing only
`validate_installation` in memory made the same rejection assertion fail exactly
with **installed-entry rejection missing** and reached one trapped launch still
carrying STRICT. No mutant launched Gradle; production source was never changed or
bypassed. Actual precedence execution above is the separately authorized isolated
research invocation, not a successful production-bootstrap admission.

Initial sandbox Git network/metadata access and private-directory creation/write
attempts failed. Scoped approved retries succeeded; the initial probe stopped at
its private receipt write before creating execution copies or launching Gradle.
Those infrastructure failures are not runtime passes. No security setting changed.

### Validation, preservation and remaining blockers

Existing offline checks passed: **38** Gradle distribution/startup/verification
tests (including existing removals), **16** installed-tools tests, repository
**148 passed / four existing Windows skips**, readiness **28**, offline image
**45**, frame copy **4**, and harness validation. Existing source, metadata,
signed/unsigned receipt, SDK and cache-integrity fixtures/removals passed, including
60 source negatives/removals and eight cache-integrity pairs. Historical source
baseline and exact README transition recomputation passed. Foundation validated
183 files, 112 Markdown files, 54 requirements and four ADRs. Final working-tree
source admission, full diff, regular 100644 modes, links, whitespace and public-data
review passed; exact committed-head admission is checked separately before
publication. No new JVM diagnostic, Android CLI, APK assembly,
signing, device/USB/ADB, native activation or VM execution was performed.

Only original task-authored Markdown in two existing review files is published.
Existing Gradle Apache-2.0/bundled notices, Temurin GPLv2/Classpath-exception and
CPython PSF research-tool terms remain applicable; no upstream code or tool
binary is redistributed. Maintenance remains with the repository owner. Source
pins, dependency metadata, automatic workflows, diagnostic application,
signed/unsigned comparison logic and execution lock are unchanged. Foundation
applies to this docs-only PR; existing Android and QEMU path filters do not select
these two files. New-PR CI remains **UNOBSERVED**, not waived.

The runtime falsifier is resolved for these exact inputs. Independent source/toolchain
authentication, administrative independence, Windows-incident disposition,
designated reviewers, private signing custody, independent signature verification,
genuine complete signed-byte equality, backup/recovery, transfer and exact Samsung
approval remain separate blockers. No hostile-build-code, same-user-race,
build-system isolation, signed reproducibility or phone-readiness claim follows.
Historical SDK cache observations and their failed combined SDK-stability result
remain unchanged; all fifteen signed-byte failures remain failures.
**Gate 0 Unresolved; Gates A–G Not reached.** ADR-0003 expires no later than
**December 8, 2026**, subject to earlier conditions. Independent private backup
remains **UNVERIFIED**; private evidence durability remains **UNPRESERVED**.

**Current update:** the [exact README integration correction](#exact-readme-integration-correction--2026-11-11)
adds only the reviewed documentation transition to source admission; updated-head
CI remains unverified at publication. The [fresh unsigned pair experiment](#fresh-unsigned-pair-experiment--2026-11-11)
records exact original-byte equality and a separate failed SDK-directory stability
assertion. The [authorized implementation and unsigned packaging evidence](#active-option-b-and-unsigned-packaging--2026-11-10)
below supersedes the earlier unchanged-active-state statements for this separate
diagnostic only. The following original source-control record is retained as history.

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

Direct observations on Windows with bundled CPython 3.12.14
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
New-head hosted checks are **UNOBSERVED at publication**, not passing. PR publication is not
merge into canonical main or independent private preservation.

## Active Option B and unsigned packaging — 2026-11-10

The owner explicitly authorized the exact three-line companion-only metadata
change, existing source/package control updates, local development validation and
unchanged automatic CI. This resolves implementation/development-build restrictions
for this task only; it is not approval of an installable physical-test artifact.
No new policy proposal, signing, key operation, installation or phone test occurred.
ADR-0003 retains its **2026-12-08 maximum expiration and earlier stop conditions**.

### Exact implementation and source binding

Verified main/base: `44a2d1cc2c914c4d23f3733b3625a9e589d75874` (PR #74 merged).
Implementation commit: `1db535da7feb4271745055c1059bf0a091f7741f`.
Its complete Android Git tree is `a844105b1373ef121401718e1c5d08cf1d6ca3ce`;
verifier blob is `623eeddec60cd3b784e65e7693ffa70619ba86b7`.
The sole Android delta inserts `dependenciesInfo { includeInApk = false }` on
exactly three lines immediately after `compileSdk 37`. Complete module source
SHA-256: `2f5594ab82be8d669cbdeafc211275a62de2608466b0e6b66628cf2e859d26f6`.
These are public source identities, not private artifact fingerprints.

The default source verifier now checks the actual working module against the
existing exact proposal bytes. It no longer replaces baseline bytes in memory
before checking the positive state. `SOURCE_BASE`, `BASE_BUILD`, all seven
protected groups and their exact-byte receipts, the three review-file exceptions,
and all 60 existing negatives/detector-removal controls remain intact. Missing,
duplicate, true/reversed, misplaced and bundle-broadened settings fail
`exact-companion-delta`; host/root/global changes fail their protected groups.
All manifest, Java, cleanup, attempt, variant, null-signing, host, execution-lock,
workflow, requirement, ADR and historical signed-failure files remain byte-identical.

The existing `--apk` path additionally checks the standard diagnostic release
output location, rejects a signing-block marker and dependency metadata ZIP
entries, and rejects generated SDK payload/text-report directories, including
stale directories. It checks that the inspected original APK bytes did not change.
It permits ordinary dependency-report intermediates. It does not authenticate
build execution, provenance or freshness by itself: those require the separately
recorded fresh build below. Six specific synthetic negatives cover the marker,
three prohibited ZIP names/prefixes and both SDK output directories. The marker
fixture is only a disposable ZIP parser control, not a signed APK or signature
verification. No genuine APK contents were rewritten, stripped or normalized.

### Actual unsigned development build

A fresh ignored source export from the verified base received the exact module
delta and the then-current verifier. Its module build directory did not exist.
All exported tracked Android source/configuration bytes were compared after the
build with the implementation commit above and matched. The verifier subsequently
received the package controls; it is not a Gradle input. The final verifier was
run from the primary checkout against the resulting original APK, both before
and after the report control. Documentation changes are not build inputs.

Used the existing Windows x86_64 installation, bundled CPython **3.12.14**,
Temurin **17.0.21+9**, Gradle **9.6.0**, AGP **9.4.0**, SDK **37.0 revision 2,
extension 22, preview 0**, Build Tools **36.0.0**. The existing Gradle distribution
ZIP and Maven artifact/metadata cache were copied into new isolated stores;
no previous module outputs, init scripts or user properties were copied. The
unchanged bootstrap verified distribution bytes/installation and forced STRICT
dependency verification. Execution was offline with build cache disabled. No new
dependency/tool download, SDK-manager operation, signing or native harness build
was performed locally. Existing inputs remain independently **UNTRUSTED**.

From the isolated export, with task-local Gradle/Android homes and the existing
JDK/SDK selected only in the child environment:

```text
python android/build.py --offline --configure-on-demand --no-build-cache :memory-diagnostic:assembleRelease :memory-diagnostic:diagnosticTest :memory-diagnostic:lintRelease
python android/build.py --offline --configure-on-demand --no-build-cache :memory-diagnostic:collectReleaseDependencies :memory-diagnostic:tasks --all
```

| Direct observation | Result and limit |
|---|---|
| Fresh assembly/JVM/lint invocation | Exit 0, BUILD SUCCESSFUL, **45 actionable tasks / 45 executed**; only diagnostic project configured; no harness task or FROM-CACHE output. APK timestamp followed invocation start. |
| Actual unsigned APK | **16,036 bytes**; existing packaged manifest/API/version, extraction rules, DEX, permission/native/assets and v1/signing-block absence checks passed. Original bytes were preserved throughout inspection. |
| Opt-out during assembly | No `collectReleaseDependencies` or `sdkReleaseDependencyData` execution; no ordinary report, encrypted payload or SDK text report output. This contrasts with the [historical retained-policy build](gate-0-diagnostic-dependency-metadata.md), which generated the 97-byte report and 185-byte encrypted payload. That historical build is not a new matched independent pair. |
| Explicit ordinary-report control | Second invocation exit 0, **2 tasks executed**; `collectReleaseDependencies` generated a **97-byte** report; `tasks --all` contained no `sdkReleaseDependencyData` task. No encrypted SDK output or SDK text report appeared; complete original APK bytes still matched their pre-control bytes. Final package checks passed with that ordinary report present. |
| Warnings and skips | Release lint: **0 errors, 5 SetTextI18n warnings** in unchanged Java. Existing builtInKotlin/useAndroidX deprecation and analytics-initialization warnings remained. Gradle reported incompatibility of deprecated features with Gradle 10. `lintVitalReportRelease`/`lintVitalRelease` were SKIPPED while the explicitly requested full `lintRelease` completed; skips are not separate passes. |

The predicted development-output effect was observed. An ordinary dependency
report is distinct from the encrypted payload and from signing-block pair
`0x504b4453`. Both old and new unsigned APKs lack signing blocks because signing
is null: that absence alone does **not** demonstrate the effect of Option B at
the signed stage. Signed-stage absence, signature validity, independent builds
and complete signed-byte equality remain **NOT RUN / Unknown**. No comparator
was weakened and none of the fifteen historical failures was reclassified.

### Local controls, preflight and publication

Final source checks passed **60 specific negatives and 60 detector-removal
assertion failures across five detector bodies**, isolated Git CLI integration,
exact historical-baseline recomputation and committed implementation admission.
Six new unsigned-metadata fixture negatives passed. Diagnostic desktop execution
passed **190 JVM assertions**, the compiled cleanup-removal rejection, actual
Activity bytecode initiation/recreation controls with framework doubles, and
compilation of all production Java against the existing API-37 SDK JAR.
The unchanged execution-lock test passed **600 denials in three JVMs and three
compiled mutant rejections**. These are not Android runtime/physical results.

Repository validators passed: **183 files, 112 Markdown files, 54 requirements,
four ADRs**, and harness manifest authority. Repository regression: **152 tests,
148 passed / four existing Windows skips**. Desktop readiness, offline-image,
frame-copy and Gradle-distribution regressions passed **28, 45, 4 and 38 tests**.
Installed-tools initially ran 16 with one error: disposable Windows junction
creation exceeded the unchanged ten-second timeout in the sandbox. The identical
suite with scoped execution access passed **all 16**; original failure retained,
no timeout/test/security-setting change. Linux-specific controls were not run
locally and remain the unchanged automatic workflow's responsibility.

Live connector and REST agreed on main; connector search and paginated REST found
**zero open PRs**, so all requested open heads/bases/diffs/files/checks/jobs/logs/
reviews/comments/threads were an empty set. PR #74 merge identity was reverified.
Exact-main [Foundation run 42921763930](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42921763930)
had successful foundation **130198110721** and Windows **130198109983** jobs;
[Android run 42921764026](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42921764026)
job **130198109902** succeeded. Check/job/step records and completed logs were
retrieved and inspected; these are baseline results, not new-head CI evidence.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) snapshot updated
`2026-11-10T21:34:20.716Z` reported All Systems Operational, no incidents.
An initial sandbox REST socket denial was resolved with scoped execution access.

Reviewed requirements, ADRs, governance, provenance/catalog/adoption/dependency
records, diagnostic/incident/independent-chain and signed-byte evidence, relevant
history and all three workflows. No tracked binary-extension matches were found.
The initially clean primary checkout, six existing worktrees/branches, ignored
assets and private evidence were preserved; no stashes existed. The final diff
is exactly four regular 100644 text files: module, verifier, this record and index.
Full diff, exact source boundary, whitespace, links, dependency/license and privacy
review completed. No new upstream code, dependency, license grant or binary is
adopted. Python additions use only the standard library. Existing license/rights
records do not supply new independent clearance.

Foundation and Android workflows select this change unchanged; QEMU filters do
not. Automatic CI may run normally. New-head checks remain **UNOBSERVED at
publication**. No APK, raw log, private path, receipt or signing material is public.

Falsifiers remain any source/protected-byte drift, metadata output appearing in
a fresh admitted build, prohibited package content/signing block, ineffective
negative control, missing build/source correspondence, or a later signed-stage
contradiction. Do not delete stale outputs to manufacture a pass: preserve them
and use a separately initialized build for a new scoped observation.
Independent source/toolchain authentication, Windows-incident disposition,
qualified signing custody, two genuinely independent signed builds, strict
complete signed-byte equality, independent artifact review, private backup and
transfer, and separate exact-artifact Samsung approval remain required.
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**
**Independent backup UNVERIFIED; private evidence UNPRESERVED.**

## SDK cache-integrity adversarial experiment — 2026-11-16

**Runtime Observation: a generated cache can become an invalidation input and
postpone discovery of changed SDK inputs by an already-loaded manager.** With
changed XML contents but preserved modification times, the pinned library's deep
`needsUpdate` returned `false`; `RepoManagerImpl.reloadLocalIfNeeded` retained the
old package description without reading XML. Direct `getPackages` and forced
refresh exposed the change. A separate cold Java process also exposed it. This is
not a persistent replacement package database or demonstrated APK-build exploit.

**Runtime Observation: the existing full-tree inspector rejected the changed
input and pre-existing state.** The result argues against treating a matching
`.knownPackages` filename, MD5, timestamp or locally supplied witness as integrity
or freshness proof. No mandatory SDK-stability rule, source pin, protected build
configuration, metadata policy, signer/unsigned qualification, host source,
execution lock or one-attempt behavior changes.

### Hypothesis and exact experimental boundary

PR #78 established writer attribution for one new library invocation and noted
that later reads were possible. It did not execute these stale-read/manager
falsifiers. This extends that record rather than repeating its writer survey.
Hypothesis: an unchanged path digest can coexist with changed input bytes, and a
cache-dependent refresh decision can preserve stale in-memory package information.
Falsifiers for the scoped explanation and inspector boundary: deep invalidation
always detects those mutations; manager reload reads
and reports changed XML; direct discovery also remains stale; or the full-tree
inspector accepts the changed original input. Each has a concrete observation below.

Fact/Source: canonical base is `2bd1fc1376e2c13733eddb8c1e3652a7cf628843`, PR #78's
merge. Reused the exact repository **32.4.0**, sdklib **32.4.0**, Temurin
**17.0.21+9**, CPython **3.12.14** and Windows x86_64 environment identified in the
[preceding investigation](#sdk-generated-state-investigation--2026-11-15).
Rehashed all **130** existing classpath JARs against unchanged verification metadata
by group/name/version/artifact; rechecked the retained source archive's recorded
SHA-256 and exact extracted Kotlin bytes. Fresh `javap -p -c` output confirms the
read/compare/time and manager-invalidation paths. Reinspected the original genuine
JFR write event without modifying it. No installation, download, dependency
substitution or source-to-binary trust promotion. Everything remains **UNTRUSTED**.

Original disposable Java probes used actual `LocalRepoLoaderImpl` and
`RepoManagerImpl`, `AndroidSdkHandler.getAllModules()`, null fallback loaders,
empty remote source providers and null downloader/settings. No Gradle invocation,
APK assembly, Android CLI, native payload or VM execution occurred. Initial small
trees contained two original minimal generic-schema XML fixtures, not SDK binaries;
their observed library behavior is real, but their contents are fixtures. A second
experiment copied all original installed `build-tools/36.0.0`,
`platforms/android-37.0` and `licenses` inputs into a fresh disposable tree and used
their actual XML. The installed SDK and retained PR #77/#78 evidence were read-only.
All mutation, hard-link, recording and compiler output stayed in new disposable
workspace directories. Private raw captures, paths, hashes and probe files are
not published; independent backup remains **UNVERIFIED**.

### Read and refresh paths, derived from exact source and bytecode

- `needsUpdate(last, false)` checks cache existence and whether its modification
  time is greater than `last`; it does not read cache or XML contents.
- `needsUpdate(last, true)` short-circuits on that same time check. Otherwise it
  traverses candidate package directories, hashes their sorted absolute paths,
  compares latest XML modification time with cache modification time, then reads
  cache bytes only when XML is not newer. Equal path hashes return `false`.
  A mismatch/newer XML writes a path hash and returns `true`, including when the
  attempted write fails. Neither XML contents nor package payloads enter the hash.
- `getPackages` collects and parses XML afresh; it does not consume cached package
  entries. Nonempty discovery writes the path hash. Corrupted XML may be omitted
  with a warning; the hash still describes candidate directories, not parse success.
- `LocalLoadTask.doLoad` reuses the manager's existing package objects when its
  expiration has not elapsed and shallow invalidation is false. Deep
  `reloadLocalIfNeeded` resets the last-refresh time only if deep invalidation is
  true, then uses the normal default-expiration load path. Explicit expiration
  zero forces discovery. This call graph alone is source evidence; the observations
  below separately establish actual effects.

### Bounded observations and controls

Each of **15** small-tree scenarios had a fresh root. Except the missing-cache
case, a real manager first loaded the two packages. The probe then applied exactly
that scenario's mutation. It recorded, in order: shallow `needsUpdate(last,false)`,
ordinary manager load with **600,000 ms** expiration, deep `needsUpdate(last,true)`,
manager `reloadLocalIfNeeded`, direct loader `getPackages`, and manager load with
expiration **0**. `last` was captured immediately after initial load. The missing
case recorded only both invalidation decisions and direct discovery. Thus **86**
separately recorded phases completed, with genuine return values/package names,
warning/error counts and JFR events. Later phases are sequential: deep repair and
direct discovery may rewrite the cache; they are not independent snapshots of the
original mutation. An independent fresh tree supplies each scenario.

| Condition | Observed shallow / deep decisions | Observed manager and direct discovery |
|---|---|---|
| Missing cache | `true` / `true`; no file created by these calls | Direct discovery returned two packages and wrote 16 bytes |
| Valid pre-existing cache | `false` / `false` | Ordinary/deep reload retained correct packages; direct discovery read XML and returned both |
| XML changed, XML time explicitly newer than cache | `false` / `true` | Ordinary load remained old; deep reload and direct discovery reported changed description |
| XML changed, original XML modification time restored | `false` / `false` | Ordinary and deep reload retained old description with zero XML reads; direct and forced discovery reported changed description |
| Package directory replaced at same path, XML time restored | `false` / `false` | Old description survived deep reload; direct discovery reported replacement |
| Added package directory, original cache retained | `false` / `true` | Ordinary load missed addition; deep reload/direct discovery enumerated three packages |
| Deleted package directory, original cache retained | `false` / `true` | Ordinary load retained deleted package; deep reload/direct discovery enumerated one |
| Empty / seven-byte / incorrect 16-byte cache, original cache time restored | `false` / `true` for each | Ordinary load reused objects; deep check repaired cache and reload/direct discovery returned correct packages; no injected package entries |
| Same bytes and modification time in a replacement cache file | `false` / `false` | Library did not reject substitution; direct discovery still parsed XML |
| Changed XML with cache timestamp 60 seconds in future | `true` initially | Ordinary manager load discovered change; this was not a successful concealment control. It rewrote the cache before the subsequent deep call |
| Incorrect cache with an in-tree hard-link alias | `false` / `true` | Deep/direct writes also changed the alias; no library link rejection |
| Directory substituted for cache, old cache time restored | `false` / `true` | Discovery returned packages despite unsuccessful cache I/O; no successful cache write event or warning; deep invalidation remained required |
| Truncated XML with original XML time restored | `false` / `false` | Deep reload retained old package without warning; direct/forced discovery omitted it and emitted one warning |

All ordinary small-tree loads except the future-cache control recorded zero XML
reads. No phase reported an error callback or escaped exception; truncated-XML
direct/forced parsing produced the two noted warning observations. Cache-directory
I/O is swallowed by the library's inspected IOException paths, not evidence that
the filesystem operation succeeded.

Two further independent small trees tested deliberate **recomputed cache bytes**:
after initial manager load, add a third package or remove the second, compute the
new path digest, write it to the cache, and restore the cache timestamp. The added
XML timestamp was set equal to that cache time. Both deep checks returned `false`;
deep reload retained the original two-package list, with cache reads and zero XML
reads. Direct discovery returned respectively three and one packages. This is
ordinary recomputation of an unauthenticated digest, **not an MD5 collision attack**.
It requires write authority over those disposable inputs/state and suitable times.

The **full copied SDK** baseline contained **11,556 files / 2,899 directories**.
After initial discovery, changed only the build-tools XML display-name and restored
its original modification time. Deep invalidation returned `false`; deep reload
still reported `Android SDK Build-Tools 36`; direct discovery reported the injected
description. The path digest remained identical. A complete fresh scan found only
that original XML changed plus the generated cache addition; every other original
entry retained its inspected properties. `inspect_sdk_generation(before,root,{})`
rejected **`sdk-input-changed`** before considering a witness. `sdk_capture` on the
post-operation tree rejected **`sdk-preexisting-state`**. A separate fresh Java
process with a new manager and that existing cache read the XML and returned the
changed description: **no cold-start concealment observed**.

### Actual JFR correspondence and negative observations

Enabled `jdk.FileRead` and `jdk.FileWrite` at zero threshold with stack traces;
used JFR stack depth **128**, workspace-local temporary storage, and process
timeouts (240 seconds for the matrix, 120 for follow-ups, 60 for cold initialization). Separate recordings
surrounded each library phase, excluding fixture mutation. Records were read with
`RecordingFile`; selected recordings were independently exported with
`jfr print --json --stack-depth 128`. All observed SDK event stacks were untruncated.

Timestamp-preserved deep checks and stale deep reloads each recorded **two cache
read events totaling 16 bytes**, zero XML reads and zero writes. The complete
retained stacks include this library path (an excerpt, not a complete stack):

```text
Files.readAllBytes
CancellableFileIo.readAllBytes
LocalRepoLoaderImpl.updateKnownPackageHashFileIfNecessary
LocalRepoLoaderImpl.needsUpdate
```

The reload recording additionally includes `RepoManagerImpl.reloadLocalIfNeeded`.
Direct discovery's XML-read stacks include `SchemaModuleUtil.unmarshal`,
`parsePackage`, `parsePackages`, `getPackages`; writes include `writeHashFile`.
The small two-package fixture normally produced **14 XML-read events** and one
cache write; the full SDK direct/cold discovery produced **64 XML-read events**
and one cache write. Event counts include low-level/EOF operations and are not
counts of logical files. Shallow checks produced no file-content events, consistent
with metadata-only inspection. These negative observations do not prove absence
of filesystem metadata queries, races, other native I/O or malicious host activity.

Actual hard-link behavior was safely observed wholly inside a disposable tree.
A Windows symlink creation attempt failed with privilege-not-held (**1314**);
no privilege/security-setting change was attempted. Real symlink traversal,
junctions, concurrent writers, clock rollback, timestamp-resolution collisions,
oversized-cache exhaustion, default-expiration wall-clock waiting, remote refresh,
fallback-loader behavior and APK-build impact remain **NOT RUN / Unknown**.

### Inspector regressions, implications and next proof

Only additive tests change in the existing checker. Every pre-existing function
and admission detector remains source-identical (main only calls the added suite).
Eight new specific negative/removal pairs cover valid/empty/truncated/wrong cache
bytes and a directory already present at capture, timestamp-preserved XML and
hidden-input byte mutations, and same-byte cache replacement identity. Real
filesystem controls also require that path-digest bytes stay equal. Separate
manifest controls isolate changed SHA-256 from timestamp/identity differences.
Each AST detector removal must accept and make the original rejection assertion
fail with its exact message; arbitrary exceptions do not count. These are Python
fixtures, not substitute library-runtime evidence. Existing full-tree enumeration,
link rejection, writer/witness checks and permanent no-admission result stay intact.

Inference: immutable-input versus generated-state classification must depend on
when and how state is consumed. A later cache read makes the generated file part
of discovery's control inputs. Equal hashes or observed writes cannot prove fresh
XML/payload discovery, authenticated origin, safe administration or absence of
substitution. **Unsupported:** this cache alone is a secure trust boundary, a
matching digest authenticates SDK contents, or the experiment qualifies an APK.

The next proof must independently authenticate source/tool acquisition and
administration; bind full original-input inventories to a protected pre-operation
baseline; specify fresh-state creation, reuse/invalidation/expiration, concurrent
write handling and link/identity policy; and independently witness actual reads,
refresh and outputs. A prospective design must keep pre-existing/suspicious state
fail-closed and prove that every original input remains checked, including payload
and metadata that package discovery does not read. Locally consistent forged
baselines/witnesses still cannot authenticate themselves. Any admission relaxation
requires a separate reviewed **ADR-0003 amendment, Tony's explicit approval and
the applicable designated independent reviews**; none is proposed as implemented.

Validation: diagnostic source/signed/unsigned/README suites and the existing 36 SDK
negative/removal pairs pass, as do the eight added pairs. Diagnostic JVM validation
passes **190 assertions**, cleanup-removal rejection, Activity controls and API-37
compilation. Execution-lock validation passes **600 denials / three JVMs / three
rejected mutants**. Exact historical source baseline and README transition pass.
Repository tests pass **148 with four existing Windows skips**; readiness/image/
frame/Gradle-distribution/installed-tools pass **28/45/4/38/16**. Foundation/harness
validation passes. Linux/native runtime and a new real Gradle STRICT run were not
performed locally; successful baseline CI is separate. No new APK build.

Read-only reinspection again confirmed PR #77's **complete original unsigned-APK
equality** and genuine **`unsigned-execution-state` failure**. No historical input
record, APK or PR #78 observation was repaired or reclassified. All fifteen
historical signed-byte failures remain failures.

### Remote preflight, publication and authority

Live `ls-remote`, fetch, `origin/main` and REST canonical main agreed on the base
above. PR #78 is merged. Connector and REST open-PR inventories were empty, so all
requested open heads/bases/diffs/files/modes/checks/jobs/logs/reviews/comments/threads
were an empty set. Exact-base [Foundation run 43802260146](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43802260146)
passed foundation **133085024344** and Windows **133085024656**;
[Android run 43802260121](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43802260121)
passed **133085024042**. Completed step records and full job logs were retrieved and
examined. [GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
**Partially Degraded Service**, update `2026-11-16T15:46:44.983Z`; the required reads
and fetch nevertheless completed. Initial sandbox network/ref-write denials were
resolved with scoped access. Initial log retrieval refused terminal escape
sequences; a separate retrieval retained complete logs privately. No failed
retrieval was counted as evidence. No library experiment failed its observation
assertions; the unavailable symlink control is explicitly retained above. A later
stdin-driven nested-class bytecode export encountered a local permission error;
the same read-only disassembly succeeded from a saved workspace script. No library
experiment was repeated or inferred from that failed export.

Reviewed governing requirements/ADRs, existing provenance/dependency/license and
incident records, source controls and workflows. Existing local main, six prior
worktrees, branches, ignored assets and retained evidence remain preserved; no
stash existed. The research branch uses a separate worktree at verified main.
Three existing regular **100644 text files** change: checker, companion evidence,
index. No dependency, upstream code, binary, license grant, private path/hash,
raw capture, receipt, signing material or personal information is published.
Existing Apache-2.0 library, Temurin GPLv2/Classpath Exception, SDK terms and mixed
transitive-license limitations remain; no independent rights clearance is inferred.
Automatic CI is unchanged: Foundation and Android select these files; QEMU does
not. New-head CI is **UNOBSERVED at publication**.

Independent authentication/administration, Windows-incident disposition, designated
reviewers, private signing custody, genuine signed builds, complete signed-byte
equality, independent signature verification, backup, transfer and exact Samsung
approval remain required. **Gate 0 Unresolved; Gates A–G Not reached.** ADR-0003
expires no later than **December 8, 2026**, subject to earlier stop conditions.
**Private backup UNVERIFIED; private evidence UNPRESERVED.**

## SDK generated-state investigation — 2026-11-15

**Result: generated package-discovery state, for the specifically observed event.**
The exact repository library used with AGP 9.4.0 writes `.knownPackages` during
local package discovery. A fresh isolated invocation directly observed its writer
stack. This does **not** identify the historical process that wrote either PR #77
file: those executions have no retained file-write stack. Their matching contents,
absence in the saved prebuild inventories and presence afterward support the
same mechanism as an **inference**, not retroactive process attribution.

The original complete-original-APK equality remains PASSED for `f272de8` only.
The original `sdk_unchanged=False` records, `unsigned-execution-state` rejection
and historical nonzero combined CLI result remain FAILED and unmodified. No new
APK build, signed or unsigned, was necessary or performed. This experiment is a
library invocation, **not** another Gradle execution or APK reproducibility run.

### Hypothesis, identities and source evidence

Hypothesis: this pinned library creates a package-location cache after discovering
the two existing XML-described packages; creating it need not change any original
SDK input. Falsifiers: another observed writer, an absent/truncated/unexpected
stack, unexpected state bytes/mode, a pre-existing or substituted state file, or
any changed/deleted original entry or additional entry. A filename match or a
16-byte length alone is insufficient. Promoting this observation to authenticated
tool or artifact admission would independently falsify the authority boundary.

Reviewed existing AGP **9.4.0**, Gradle **9.6.0**, Temurin **17.0.21+9**, Platform
**37.0** and Build Tools **36.0.0**, on local Windows x86_64 with CPython **3.12.14**.
All remain **UNTRUSTED**. The pinned public component
`com.android.tools:repository:32.4.0` has JAR SHA-256
`9fd419f3307be633aaf7b02b52832521c1300d4bf9058cee83bb11139990a7f9`, matching existing
verification metadata and the retained build cache. Supporting
`com.android.tools:sdklib:32.4.0` has JAR SHA-256
`d0bbe0e03155a7bdd9bac03567b6b26797f81a778f55d5eadc3e71e7a0a27434`.
All **130** JARs on the experiment's classpath were checked against the unchanged
strict metadata by component group/name/version/artifact and SHA-256, both before
the initial invocation and the continuation. No unlisted JAR was admitted. This
checks existing pins, not independent acquisition or source-to-binary provenance.

Retrieved Google's exact
[repository 32.4.0 source archive](https://dl.google.com/dl/android/maven2/com/android/tools/repository/32.4.0/repository-32.4.0-sources.jar)
privately; public archive SHA-256:
`770b35ee75031185ffe53637b98bc400494b2837bf6ab8731f798bb5208bb7a4`.
`com/android/repository/impl/manager/LocalRepoLoaderImpl.kt` describes and implements
the cache. `getPackages` collects candidate directories, parses their packages
and, when the resulting package map is nonempty, calls `writeHashFile`.
`getKnownPackagesHashFile(true)` creates the file; `Files.write` writes the buffer.
`getLocalPackagesHash` hashes the sorted absolute package-directory strings encoded
as UTF-8 with **MD5**. It hashes neither SDK tool bytes nor package XML contents.
`needsUpdate` can later read this cache; a deep check can update it. Thus generated
state can become an input to later discovery. It is not universally irrelevant
or harmless, and its MD5 is not used as the SDK integrity digest.

`javap -p -c` on the exact pinned binary confirms the calls to the hash function,
`writeHashFile`, `Files.createFile` and `Files.write`. Source/bytecode agreement
and the runtime stack below support this narrow mechanism, not a full library
reconstruction. The upstream algorithm skips some metadata/cache directories;
**the Python SDK inspector does not inherit those exclusions**.

### Actual procedure and observed writer

Created one new private SDK tree by copying only `build-tools/36.0.0`,
`platforms/android-37.0` and `licenses` from the existing installed SDK, preserving
the installation and both previous experiment trees. Captured the complete tree
before invocation using `sdk_capture` in the existing
[diagnostic checker](../../.github/scripts/test-memory-diagnostic.py). The capture
contains **11,556 regular files and 2,899 directories including the root**.
No `.knownPackages` existed. Saved the private baseline exclusively; never derived
or repaired it from post-operation data.

Compiled an original disposable Java `WriterProbe` against the checked classpath
with the existing JDK. Its complete operative sequence was:

1. Assert `.knownPackages` absent. Construct `LocalRepoLoaderImpl(root,
   new HashSet<>(AndroidSdkHandler.getAllModules()))` without a fallback loader.
2. Call `needsUpdate(0, true)` and require `true` with the file still absent.
3. Start a JDK Flight Recorder `Recording`, enabling `jdk.FileWrite` with threshold
   zero and stack traces. Call `getPackages` with a `ProgressIndicatorAdapter`
   that rejects package warnings/errors. Require exactly `build-tools;36.0.0`
   and `platforms;android-37.0`, and a newly present 16-byte state file.
4. Stop and dump the recording privately. The Java process exits zero. Export
   events using `jfr print --json --stack-depth 64 --events jdk.FileWrite`.
5. Require exactly one event, its path equal to this SDK's `.knownPackages`,
   `bytesWritten=16`, an untruncated stack and the exact stack below. Bind that
   observation to the private process interval, repository JAR identity and the
   recorded post-event state-file identity/content/mode. Run the separate
   `inspect_sdk_generation(before, root, witness)` API against a fresh full scan.

Observed event stack, top to bottom:

```text
sun.nio.ch.FileChannelImpl.write
java.nio.channels.Channels.writeFullyImpl
java.nio.channels.Channels.writeFully
java.nio.channels.Channels$1.write
java.nio.file.Files.write
com.android.repository.impl.manager.LocalRepoLoaderImpl.writeHashFile
com.android.repository.impl.manager.LocalRepoLoaderImpl.getPackages
WriterProbe.main
```

**Direct result:** exactly one added regular file, `.knownPackages`; no original
file bytes, modes, identities, timestamps or link counts changed; no original
directory disappeared or changed identity/mode/link count; no other addition.
The generated file matched the independently computed path-derived 16-byte digest
and the witnessed file identity. The API returned `original_inputs_unchanged=True`,
`generated_state_observed=True`, **`whole_sdk_unchanged=False`**, `trust=UNTRUSTED`
and **`artifact_admission=False`**. Root directory timestamps necessarily reflect
the addition; directory timestamps are checked for scan races, not treated as
immutable input bytes. File timestamps are compared in addition to content/mode.

Read-only reinspection of the old SDKs found their 16-byte files match the digest
for their own distinct absolute roots. The retained original APK bytes still
compare equal, and unchanged execution records still raise exactly
`unsigned-execution-state`. These reads neither rebuild nor relabel the pair.
PR #77's original inventory stored file hashes, **not modes or empty directories**;
historical mode/directory invariance and historical write-time process attribution
remain **Unknown**. The new complete inventory cannot backfill those facts.

### Inspector contract, controls and failures

The additive standard-library API is experiment-specific and read-only after
capture. Call `sdk_capture(absolute_root)` before an isolated operation, retain
that private return value, collect the separate local file-write observation above,
then call `inspect_sdk_generation(before, root, witness)`. Its result is a bounded
consistency observation, never an APK-verifier input. Private persisted JSON must
be read without duplicate keys and restore entry arrays to tuples before use;
`sdk_baseline` validates the exact schema, root, time, UNTRUSTED label, entry types,
parents and case aliases. An invented or edited internally consistent local
baseline/witness is not authenticated by these checks.

The scanner enumerates every entry recursively, including hidden files, licenses,
empty directories and root. It reuses `android/build.py` ancestor, no-follow and
descriptor-identity reads. Symlinks, hard links, Windows reparse points and special
files are refused rather than omitted/followed. Complete original file SHA-256,
size, host mode, device/inode, link count and timestamps are compared; directories
retain type/mode/device/inode/link count. Membership detects additions/deletions.
No directory or file class is ignored. Pre-existing generated state is rejected.
Only the one expected addition can pass, and only with the correct bytes, ordinary
file mode, exact pinned writer, observed stack, process interval, successful exit
and matching witnessed state identity. Missing/malformed/substituted/unknown state
fails closed. The observed path digest is not a replacement for full-tree SHA-256.

Default source tests include a positive synthetic observation and **36** specific
negative/removal pairs for input deletion, bytes/size/mode/identity changes, hidden
or other additions, missing/pre-existing state, invalid baselines, missing/wrong
witnesses, wrong writers/pins/stacks, bad event intervals and malformed/substituted
state. Each real rejection must be `SdkStateRejection` with its expected code.
The actual detector body is removed through AST substitution, must accept the
same case, and must cause the original negative assertion to fail with the exact
expected message. Overlapping checks are tested individually rather than disabled
together. A real input-file mutation also fails fresh inspection; replacing the
live scan with cached data admits it and breaks that same negative assertion.
Real malformed-state and hard-link controls pass. Windows reparse-stat injection
exercises the actual scanner rejection; no claim of a real Windows symlink test.
The suite uses a real symlink on POSIX when run there; new-head POSIX execution is
UNOBSERVED at publication.

Failures retained, not counted as successful controls:

- Initial sandbox GitHub access and branch-ref creation were denied; scoped
  execution access completed those authorized operations.
- Web-tool retrieval of the source archive failed; direct HTTPS retrieval from
  the same exact Google Maven URL succeeded. The source download is research,
  not a new build dependency or authenticated upstream receipt.
- The first detector-removal run encountered another valid downstream rejection;
  the revised test separately checks full-inspector rejection and effective removal
  of its specific layer. A malformed fixture intended as 16 bytes was actually
  17; its size rejection was correct, and the fixture was corrected to test content.
- Initial Java/JFR startup failed with access denied to the ambient temporary
  directory, before `getPackages`. The complete SDK still matched the original
  baseline. A separate continuation used a new workspace-local JFR temporary
  directory and succeeded. Original failure logs and baseline were preserved.
- The first JFR JSON display used the printer's default five-frame limit. Reading
  the same recording with `--stack-depth 64` revealed the full eight-frame stack;
  no library operation or build was repeated for that display correction.

### Preflight, validation, provenance and authority

Live main remained `2c64fc1f5a873474c9beba1402c3b11ea6e6eed2`; PR #77 is merged.
Connector and REST open-PR inventories were empty, so open heads/bases/diffs/files/
modes/checks/jobs/logs/reviews/comments/threads were an empty set. Post-merge
[Foundation run 43790692955](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43790692955)
passed foundation **133048187097** and Windows **133048186838**; post-merge
[Android run 43790693722](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43790693722)
passed **133048189531**. Exact checkout, job/step records and completed logs were
inspected. The Android log records 45 diagnostic tasks, ten real offline STRICT
controls and execution-lock mutations. These are existing baseline CI observations,
not newly requested local builds. GitHub Status reported All Systems Operational,
page update `2026-11-16T00:09:19.907Z` (UTC).

Local validation passed the unchanged historical source-baseline and exact README
transition audits; existing 60 source and 60 signed-structure negative/removal
pairs, 11 README pairs, 24 unsigned pairs, eight file/CLI/admission negatives and
six metadata negatives. Diagnostic JVM: 190 assertions, cleanup-removal and Activity
bytecode controls, API-37 compilation. Execution lock: 600 denials, three JVMs and
three mutants. Repository regression: 148 passed with four existing Windows skips
(152 total). Readiness/image/frame/Gradle-distribution/installed-tools: 28/45/4/38/16
passed. Foundation/harness validation: 183 files, 112 Markdown files, 54 requirements,
four ADRs. Linux/native/real-Gradle/device regressions were not run locally.

The three-file change extends only this existing checker, focused record and index.
Protected-source pins, reviewed-file scope, complete-byte comparator, signed verifier
and its permanent independent-authority rejection, unsigned combined verifier,
active metadata policy, host source, one-attempt behavior, execution lock and every
workflow remain unchanged. Existing Foundation and Android workflows select the
change normally; QEMU filters do not. Full diff/modes/public-data hygiene, source
admission, requirements/ADRs, prior experiment procedure, provenance/dependency and
license records were reviewed. No binary, upstream code, dependency or license grant
is added. New Python/fixture code is original; existing filesystem helpers are
reused. The downloaded source carries Apache-2.0 notices and stays private. JDK
GPLv2/Classpath Exception, SDK terms, transitive notices and the existing
185-component/322-artifact ledger retain their limits. Build-tool maintainers retain
maintenance responsibility; library upgrades invalidate this exact-event contract.

This is not an atomic filesystem snapshot, an independent authority or protection
against a compromised host/concurrent same-user writer. Changed-and-restored bytes
between scans can escape observation. Host `st_mode` does not cover Windows ACLs,
alternate data streams, owners, xattrs or every permission semantic. JFR and the
local witness can be forged on an untrusted host; consistent records cannot prove
independent execution. Dependency/classpath pin checks do not clear TOFU or the
Windows incident. The direct library call identifies this new event's writer;
it does not establish which Gradle/AGP caller performed the historical writes.

Any proposal to substitute this distinction for mandatory whole-SDK stability or
artifact admission needs explicit project-owner approval of an **ADR-0003 amendment
to the companion qualification/evidence contract**, assessed under **ADR-0004
Option A**, with PDVA-REQ-036, 039–042 and 054 traced and designated independent
provisioning/security/build reviewers. No such admission change is implemented.
Independent provisioning, Windows-incident disposition, reviewers, qualified signer
custody, genuine signed builds, strict complete signed-byte equality, independent
signature verification, authenticated receipts, private backup and exact-artifact
Samsung approval remain separate prerequisites. All fifteen signed-byte failures
remain failures. No signing, keys, device/ADB/USB, installation, native activation,
VM execution, privilege or environment-security changes occurred.

**Gate 0 Unresolved; Gates A–G Not reached. ADR-0003's December 8, 2026 deadline
and earlier termination conditions remain binding. Independent backup UNVERIFIED;
private evidence UNPRESERVED.** Public implementation preservation does not back up
the private records. Next proof is independent review of this exact input/state
contract and qualified custody/provisioning evidence; the historical writer and
missing historical modes cannot be manufactured. New-head CI is UNOBSERVED.

## Exact README integration correction — 2026-11-11

This is a revision of **existing draft PR #77**, on explicit owner instruction,
not another PR or another APK experiment. **Local integrated-source validation
passed; applicable new-head hosted checks are UNVERIFIED at publication.** The
earlier integration-blocker text records the original publication state. This
section supplies the precise source correction without declaring successful CI
integration or readiness for merge. Gate 0 remains Unresolved; Gates A–G Not reached.

### Reviewed transition and unchanged historical baseline

Live main was `7bbdec67825d4c88d8789d3db643f3bc97ee777f`; existing PR head was
`5cc2104f725901bafc01c80c86f5cd8e76303116`. The intervening main commit changes
**only README.md**, regular 100644, with three added and 47 removed lines. It
clarifies nonroot operation, shortens the introduction and retains experimental
uncertainty. No Android, dependency, requirement, ADR, security or workflow file
changes. Task review of that complete commit does not constitute independent
supply-chain or security qualification.

Main was merged into the existing branch without rewriting history:
`afab19926dbc04081cd12ae249918bae7f6f5f05`, with parents `5cc2104` and `7bbdec6`.
README.md matches main exactly; it was not reverted, rewritten or added to the
three-file review exemption. Existing branches/worktrees/stashes/ignored assets
and private records were preserved; the initial checkout was clean, with six
registered worktrees and no stash.

The [checker](../../.github/scripts/test-memory-diagnostic.py) keeps `SOURCE_BASE`,
the complete historical `PROTECTED` mapping, `protected_evidence`, source modes,
module byte fixtures, `REVIEWED_FILES` and the existing historical recomputation
procedure unchanged. The new immutable transition pins identify the exact README
commit, parent and whole README SHA-256, plus the **complete 109-file governance
count/digest obtained from the historical baseline with only that README replaced**.
All other protected groups retain their original expected count/digest.

During admission, the new governance digest is selected only for that exact README
hash. Every governance path and complete file body still participates in the
length-delimited digest. No path is removed, normalized, wildcarded or generally
exempted. A different README fails; an unrelated governance/security/requirement/
ADR change still fails even with the correct README. The original historical
state remains admissible for explicitly inspecting the old source commit; the
default integrated-source regression additionally requires the exact updated
README in the actual working tree. Existing 100644 mode enforcement is unchanged.

The additive, read-only `--verify-readme-update` audit loads the immutable baseline,
the exact reviewed parent and commit. It verifies parent identity, equal file
inventories, a README-only byte/mode difference, the parent's original README,
the pinned new README, and the recomputed complete protected evidence. It also
checks both historical-parent and updated-commit admission. Missing Git objects
fail rather than fetching or deriving replacement pins. Shallow normal CI uses
the fixed pins and current source tests; it needs no historical fetch or workflow
change. These public source fingerprints are review evidence, not authentication.

### Actual tests and preserved experiment outcomes

Windows x86_64, existing bundled CPython 3.12.14 and Temurin 17.0.21+9 with API-37
compile stubs; all remain UNTRUSTED. No dependency or tool was installed/upgraded.
The actual procedures, using the existing interpreter, included:

```text
python .github/scripts/test-memory-diagnostic.py
python .github/scripts/test-memory-diagnostic.py --verify-source-baseline
python .github/scripts/test-memory-diagnostic.py --verify-readme-update
python .github/scripts/test-memory-diagnostic.py --check-source-ref HEAD
python .github/scripts/test-memory-diagnostic.py --check-source-ref f272de8207586ee2ec84412f6057ea580f0d0611
python .github/scripts/test-memory-diagnostic.py --java-home <existing-JDK> --android-jar <existing-API-37-JAR>
python .github/scripts/test-execution-lock.py --android-jar <existing-API-37-JAR>
```

- Accepted the exact README update in the integrated working source, actual Git
  transition audit and isolated Git CLI. Historical baseline recomputation and
  old experimental source admission passed independently; no old receipt changed.
- **11 new negatives and 11 effective AST detector-removal assertion failures**:
  altered, missing, renamed or executable README; changed governance, requirements,
  ADR, security boundaries, host configuration, execution lock or dependency pins.
  A one-byte newline addition is enough to reject each content mutation. Detector
  deletion must admit that same bad fixture, making the negative assertion fail;
  arbitrary exceptions do not count.
- All existing **60 source negatives / 60 removal assertions** ran on the integrated
  source, as did **60 signed-structure negatives / 60 removal assertions**, eight
  file/CLI/admission negatives, six unsigned metadata negatives and the previous
  **24 unsigned observation negatives / 24 removal assertions**. The signed
  authority rejection and final fail-closed admission boundary are unchanged.
- Diagnostic JVM: **190 assertions**, cleanup-removal rejection, Activity bytecode
  controls and API-37 compilation passed. Execution lock: **600 denials in three
  JVMs and three rejected mutants**. No Android runtime result is claimed.
- Foundation/harness validation passed: **183 files, 112 Markdown files, 54
  requirements, four ADRs**. Repository regression: **152 tests, 148 passed and four
  existing Windows skips**. Readiness, offline-image, frame-copy, Gradle-distribution
  and installed-tools suites passed **28, 45, 4, 38 and 16** tests respectively.
  Linux/native/real-Gradle runtime and device controls were not rerun locally.

The first new mode-removal control failed because a redundant 100644 condition
in the proposed digest selector still rejected its fixture after deletion of the
existing mode detector. The selector was corrected to leave modes to the original
mode detector. The unchanged mode rule and its effective removal control then
passed. This initial test failure is retained; no source mode was relaxed.

Read-only inspection rechecked both retained original APK identities and whole
bytes against the original private execution records. **Original unsigned equality
remains PASSED for `f272de8` only**, and the original **combined SDK-state result
remains FAILED** at `unsigned-execution-state` because `.knownPackages` was added.
The corrected source verifier still reproduces that failure. No artifact or private
record was rewritten, no build rerun occurred, and neither build is relabeled as
originating from `7bbdec6` or the integrated PR. No signing or device operations.

### Live preflight and publication boundary

Connector/REST and fetched refs agreed on the exact head/base above. PR #77 was
the only open PR and remained a draft. Full diff, three changed regular-file modes,
check/job/step records and completed logs were reviewed; reviews, comments and
review threads were empty. Main's real Foundation failure remains recorded:
[run 43071019706](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43071019706),
foundation **130698583492 failed** at `protected-governance`, Windows
**130698584073 passed**. No Android run existed for that README-only change.

PR #77's old-head [Foundation run 43071905566](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43071905566)
passed foundation **130701737955** and Windows **130701737401**;
[Android run 43071905616](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43071905616)
passed **130701737689**. Their checkout logs identify **`5cc2104`**, which did not
contain the concurrent README edit. Those successes cannot verify the integrated
source or retroactively turn main's failure into a pass.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json), update
`2026-11-11T17:54:12.114Z`, reported All Systems Operational, no incidents.

Requirements, ADR decisions, acceptance/provenance/dependency records, source
protection, relevant history and all workflows were rechecked. The revision adds
original standard-library Python only, with no dependency, binary, license grant
or new rights claim. The final PR diff against current main remains exactly the
existing checker and two focused evidence files, all 100644; README.md, Android,
configuration, requirements, ADRs and workflow files match current main. Full diff,
historical pins, source admission, modes, links, whitespace and public-data hygiene
are checked before push. No private paths, artifacts, inventories or hashes are
published; the new hashes identify public source only.

Foundation and Android already check out the exact PR head and call this checker;
the merged ancestry now makes their next normal runs exercise integrated source.
Triggers, check requirements and failure propagation remain unchanged; QEMU filters
do not select this change. **Applicable new-head checks are UNVERIFIED at push;
successful integration is not claimed.**

**Publication resumed 2026-11-15, America/Fortaleza.** The interruption left the
merge commit and three uncommitted correction/evidence files intact; no push had
occurred. On resume, main remained `7bbdec6` and PR #77 remained the sole open PR,
draft at `5cc2104`, with empty comments/review threads and the same three completed
successful old-head checks. Completed implementation/JVM/regression work was
retained without rerunning the APK experiment or repeating those suites. Final
source admission, unchanged historical pins/signed functions, exact README bytes,
main ancestry, three-file scope, privacy, documentation and whitespace were
rechecked. GitHub Status reported All Systems Operational at snapshot
`2026-11-16T00:09:19.907Z`. Those pre-push observations are not new-head CI evidence.

All independent authentication/administration, Windows-incident disposition,
reviewer, signing-custody, signed-byte equality, backup, transfer and exact phone
approval requirements remain separate. ADR-0003's December 8, 2026 deadline and
earlier termination conditions remain binding. **Physical testing NOT READY;
independent backup UNVERIFIED; private evidence UNPRESERVED.**

## Strict signed-APK prequalification — 2026-11-10

Scope: the separate Android 17 memory diagnostic under PDVA-REQ-036–043, 048,
051 and 054. Verified main/base `e0e088e27d435e999cc339e52ad23bd7cf25cee5`.
Implementation commit `052f4a6338f49d63d572560bd47af120137d11ab` adds read-only
controls and disposable synthetic tests to the existing
[diagnostic checker](../../.github/scripts/test-memory-diagnostic.py), Git blob
`4037439e602f5a73551a14f522f47d3783972d59`. The unchanged Android tree is
`a844105b1373ef121401718e1c5d08cf1d6ca3ce`; these are public source identities.
This is a **partial implementation with an explicit hard blocker**, not a
completed end-to-end qualification service. **Real signed-APK admission remains
NOT RUN / Unknown.** No qualified signed companion pair was available or created.

### Executable controls and supported limits

The new `--signed-pair` route reads two original files, rejects aliases of the
same file, checks regular-file identity and bounded sizes, and requires direct
equality of **every original byte**. No hashes-only equality decision, ignored
regions, normalization, repacking, metadata removal, timestamp adjustment or
signature/ciphertext copying exists. A separate re-read control rejects changed
content and same-byte replacement with a different file identity. These are
point-in-time checks under qualified administration, not a hostile-filesystem
atomicity guarantee. The actual CLI exits nonzero with a sanitized reason and
cannot produce a qualification success.

The conventional ZIP profile requires contiguous local records, a bounded APK
signing block, an exact central directory and final uncommented EOCD. It rejects
prefixes, trailing data, ZIP64, multi-disk, encryption/data descriptors, duplicate
names/extras, contradictory local/central fields, unsupported methods/attributes,
bad CRCs and excessive expansion. Stored and complete raw-deflate streams are
supported. Only the narrowly checked Android alignment extra is recognized.
ZIP metadata participates in the original-byte comparison without modification.

The signing-block parser checks both size fields, bounded length-prefixed fields,
unique pair IDs, one v2 signer/certificate and matching unique algorithm lists.
It specifically rejects **dependency-metadata pair `0x504b4453`**, unknown pairs,
nonzero padding, unknown algorithms, extra signed fields and all attributes.
The deliberately narrow supported structural profile is v2 with RSA PKCS1/SHA-256
or ECDSA/SHA-256 and optional zero verity padding. v1/v3/v3.1/v4, rotation and the
historical extra empty signed-data field are unsupported. No signing configuration
was selected or changed to fit this profile. A future qualified pair outside it
must fail pending independent review, never be rewritten into compatibility.
Parsing a certificate or signature-shaped field is **not cryptographic verification**.

Package checks reuse the existing manifest/API/version/release/extraction policy
and add an exact permitted ZIP inventory and one uses-sdk element. Native libraries,
assets, extra DEX, v1 signatures, dependency payload entries, unauthorized permissions
and extra components are excluded. The existing DEX capability screen is retained.
It is not a DEX verifier, resource-table reference resolver or proof of compiled
one-attempt semantics. Those require authenticated source-to-build correspondence;
the original source controls and JVM tests remain necessary and unchanged.

Optional `--build-receipts` reads a private, size-bounded JSON claim packet with
duplicate-key rejection. Exactly two records must bind the whole APK bytes, the
length-delimited full source/mode snapshot and matching input/tool/signer identities.
Build, checkout, output, dependency-home, execution, operator and retained-artifact
identities must differ. Missing fields, contradictory hashes, copied/stale claims,
non-fresh claims, future execution, expired records and mismatched inputs reject.
Identity fields are opaque 64-hex digests of private evidence; their syntax and
inequality do **not** establish the underlying events or independence. The maximum
receipt expiry is conservatively **2026-12-08 00:00 UTC**, with a calendar assertion;
ADR-0003's earlier termination conditions still apply and are not automated here.

### Hard blocker: authenticated authority and real signatures

`qualified_authority` always rejects with
`independent-qualification-authority-unavailable`. There is no caller trust hash,
approval boolean, environment bypass, self-reported verified-signature flag or
test-runner callback that can enable admission. Even a complete internally
consistent synthetic receipt packet fails this boundary through the real CLI.
This preserves the existing [UNTRUSTED installed-tool disposition](gate-0-installed-jdk-sdk-integrity.md)
and [unqualified independent chain](gate-0-independent-linux-build.md).

The staged SDK integration specifies verification only, individually for each
original: `verify --verbose --print-certs --min-sdk-version 37 --max-sdk-version 37 -Werr`.
Its output parser requires successful exit, no stderr/warnings, verified v2 only,
exactly one signer, and the authorized certificate matching the parsed original.
However, **the integration is unreachable without a separately implemented and
reviewed authority adapter** supplying authenticated SDK/JDK identity, sanitized
execution environment, signer authorization and independently authenticated
evidence. Final admission also remains explicitly unimplemented, preventing a
future adapter addition alone from silently enabling qualification. No SDK signature
verification was executed here. Output-parser fixtures are not valid/invalid
cryptographic signature experiments. Real altered-signature and wrong-signer
verification remain **NOT RUN**, not passed by fixture text.

The next required real proof is a designated independent review packet that
authenticates source, OS/administration, complete tools/dependencies and verifier,
disposes of the Windows incident or qualifies a replacement chain, and establishes
dedicated private signing custody and recoverable independent retention. That
packet must define an authenticated receipt authority, freshness/revocation and
source/artifact binding suitable for a reviewed adapter and final admission.
Only after separate build/signing authorization may two genuinely fresh builds,
their independently retained originals, actual signature controls and strict
complete-byte equality supply the real qualification evidence. Backup/recovery,
artifact review, transfer approval and exact Samsung installation approval remain
mandatory subsequent boundaries. No such proof or approval is inferred here.

### Historical logic review and provenance

Read the historical comparator and signing reader at
`18697fd8c32450d96e0c134acb7e9724bd2f65c7`, referenced by the unchanged
[fifteen-failure record](gate-0-apk-reproducibility.md). Retained concepts are
bounded little-endian framing, matching block lengths, duplicate rejection and
original-file comparison. The old native inventory, build orchestration, shared
development signer, summary-object equality and unsigned positive fixtures were
not restored as admission. Unknown pair/algorithm acceptance and the historical
extra-field compatibility exception were deliberately not inherited.
The current [AOSP v2 format](https://source.android.com/docs/security/features/apksigning/v2)
and [SDK verification interface](https://developer.android.com/tools/apksigner)
were consulted for field ordering and verification arguments; no upstream code was
copied. This task's source review is not the designated independent approval.
Original task-authored Python uses only the standard library; existing PSF/SDK/JDK
and toolchain rights records remain applicable, with no new dependency, binary,
license grant or distribution claim. Maintainer remains the repository owner.

### Actual local validation and falsifiers

Windows x86_64, bundled CPython 3.12.14, existing Temurin 17.0.21+9 and API-37
compile JAR. No Gradle/unsigned packaging research was repeated. Commands used
the selected existing Python/JDK paths privately; public equivalents:

```text
python .github/scripts/test-memory-diagnostic.py
python .github/scripts/test-memory-diagnostic.py --verify-source-baseline
python .github/scripts/test-memory-diagnostic.py --check-source-ref HEAD
python .github/scripts/test-memory-diagnostic.py --java-home <existing-JDK> --android-jar <existing-API-37-JAR>
python .github/scripts/test-execution-lock.py --android-jar <existing-API-37-JAR>
python .github/scripts/validate-foundation.py
python .github/scripts/validate-harness.py
python .github/scripts/test-repository-validation.py
python .github/scripts/test-desktop-readiness.py
python .github/scripts/test-offline-image-inspect.py
python .github/scripts/test-frame-copy.py
python .github/scripts/test-gradle-distribution.py
python .github/scripts/test-installed-tools.py
git diff --check
```

- New controls: **60 specific synthetic negatives and 60 assertion failures after
  actual AST detector-body removal across eight functions**, plus **eight** file,
  real CLI and admission negatives. Each mutant must complete on the defective
  input, then the negative assertion must fail because rejection disappeared;
  arbitrary exceptions, timeouts and wrong rejection reasons do not count.
- Positive controls: stored/deflated synthetic ZIP/signing framing, exact original
  byte equality, policy parsing, consistent receipt syntax and SDK-output parsing.
  All binary fixtures are disposable and visibly labeled synthetic; none is a
  valid signed, independently built or installable APK. They never pass admission.
- Existing controls: **60 source negatives / 60 detector-removal assertions**,
  six unsigned metadata negatives, isolated Git CLI and exact historical baseline
  recomputation passed. No protected inventory or trust digest was regenerated.
- Diagnostic JVM: **190 assertions**, compiled cleanup-removal rejection, actual
  Activity bytecode with desktop framework doubles, and all Java compilation
  against API 37 passed. Execution lock: **600 denials in three JVMs and three
  rejected mutants**. Android runtime remains untested.
- Foundation/harness validators passed: **183 files, 112 Markdown files, 54
  requirements, four ADRs**. Repository regression: **152 tests, 148 passed / four
  existing Windows skips**. Readiness, offline-image, frame and Gradle-distribution
  suites passed **28, 45, 4 and 38** tests respectively.
- Installed-tools: first run **16 tests, one error**, the unchanged disposable
  Windows junction creation exceeded its ten-second sandbox timeout. The identical
  suite with scoped execution access passed **16/16**. No timeout/security change.
- First new run rejected its positive synthetic file due to Windows path/handle
  ctime differences. Corrected by comparing ctime within the handle and using
  file ID/size/mtime plus complete bytes across path reads. Final review also caught
  and corrected a one-day error in the proposed expiry literal; the new calendar
  assertion and over-limit receipt negative pass. Neither issue is concealed as
  a successful initial run.

Falsifiers include acceptance of any byte change, metadata pair, malformed or
unsupported structure; wrong package/release/API; protected-source drift; missing,
stale, copied or contradictory receipts; replacement after inspection; a negative
surviving its detector deletion; or any fixture/self-reported evidence causing
admission. Resource/DEX semantic interpretation, cryptographic negatives, authentic
receipt verification, real build independence and real signed equality are unrun.

### Live preflight, final scope and publication

Live GitHub main and local Git agreed on the base above. PR #75 was reverified
merged from `eb03768c80af8a9a2df26b6168037b045e9fd0e7` against
`44a2d1cc2c914c4d23f3733b3625a9e589d75874`. Connector search and REST returned
**zero open PRs**: all requested open heads/bases/diffs/files/modes/checks/jobs/logs/
reviews/comments/threads were an empty set. The commit-workflow connector returned
no runs; REST supplied the actual push-run results. An initial CLI socket denial
was resolved with scoped execution access.
Exact-main [Foundation run 42925839071](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42925839071)
passed foundation job **130211960231** and Windows job **130211959792**;
[Android run 42925839106](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42925839106)
job **130211959920** passed. Check/job/step metadata and completed logs were
retrieved; relevant checkout, test, build and inspection results were examined.
These are baseline receipts, not this PR's CI. [GitHub Status](https://www.githubstatus.com/api/v2/status.json)
reported All Systems Operational, update `2026-11-10T23:36:07.008Z`.

Read governing requirements/ADRs, acceptance/provenance, diagnostic and incident
records, independent-chain/tool-integrity evidence, adoption/dependency catalog,
source history and all three workflows. Six registered worktrees and their branches,
ignored/private assets and the initially clean checkout were preserved; no stashes
existed. No tracked APK/JAR/AAR/SO/EXE/DLL was found. Private artifact inventories
were not exhaustively inspected or authenticated. No APK, private hash/path,
receipt, signing data or personal identifier is published.

Final scope is three existing regular **100644** text files: the diagnostic
checker, this evidence and its index. They were already the exact three explicit
review files. `SOURCE_BASE`, `BASE_BUILD`, `PROPOSED_BUILD`, `PROTECTED` and
`REVIEWED_FILES` remain unchanged; every other tracked file is unchanged.
Complete diff/mode/source/privacy review and whitespace/link validation were
performed. No metadata setting, signing configuration, source authority, requirement,
workflow, execution lock or one-attempt Java code changed. Foundation and Android
remain automatically applicable; QEMU filters do not select this change.
Linux/native controls were not run locally. No keys, signing, physical-test
artifacts, private transfer, phone/ADB/USB, native activation or VM execution.

New-head CI is **UNOBSERVED at publication**. All fifteen historical
signed-byte failures remain failures. ADR-0003 expires no later than **2026-12-08**,
subject to earlier termination. **Gate 0 Unresolved; Gates A–G Not reached; physical
testing NOT READY. Independent backup UNVERIFIED; private evidence UNPRESERVED.**

### Publication continuation — 2026-11-11

Publication was deferred and subsequently resumed on the existing implementation.

## Fresh unsigned pair experiment — 2026-11-11

**Direct observation: complete original unsigned APK equality PASSED.** Two fresh,
separately executed release builds each produced **16,036 bytes**, and the existing
`original_pair` / `exact_original_bytes` control compared every original byte
directly. No normalization, repackaging, ignored regions, signature processing or
comparison exception was used. Both original files remain locally retained.
This is **bounded unsigned-development reproducibility only** on one untrusted
Windows administration/toolchain, not independently authenticated builders,
signed reproducibility, supply-chain qualification or Samsung readiness.

**Separate result: the combined observation route FAILED** with
`unsigned-execution-state`: both SDK directory inventories gained `.knownPackages`.
No original SDK file changed or disappeared. The whole-directory-unchanged claim
is false and remains false; its check, records and nonzero CLI result were not
weakened or converted into success. This does not alter the separately measured
original-byte equality. No claim that all environment state stayed unchanged is
supported. Independent provenance and administration remain **Unknown**.

Scope: PDVA-REQ-036–043, 048, 051 and 054. **Gate 0 Unresolved; Gates A–G Not reached;
physical testing NOT READY — STOP.** This new experiment is neither the earlier
single-build packaging research nor a rerun of the fifteen signed-byte failures.

### Exact source, inputs and execution

Both exports contain all **183** regular source files from reviewed canonical main
`f272de8207586ee2ec84412f6057ea580f0d0611`, the PR #76 merge. The Android tree remains
`a844105b1373ef121401718e1c5d08cf1d6ca3ce`. Each export was initialized separately
from exact Git blob bytes/modes, with exclusive new directories and files; no
working-tree edits were substituted. All exported source bytes matched before
and after each build. The new comparison code runs from this PR against those
unchanged main-source artifacts; it was not injected into either build export.

Environment: Windows x86_64, existing bundled CPython
**3.12.14**, Temurin **17.0.21+9**, Gradle **9.6.0**, AGP **9.4.0**, SDK Platform
**37.0** and Build Tools **36.0.0**. Everything is explicitly **UNTRUSTED**.
Existing exact pins and verification metadata remain unchanged; no installation,
upgrade, replacement tooling or dependency-policy change occurred. Existing
source/provenance, adoption and dependency ledgers remain controlling, including
TOFU and unresolved Windows-incident limitations. No independent rights or
security clearance is inferred from a successful build.

Each side had different source, Gradle home, SDK (`ANDROID_HOME` and
`ANDROID_SDK_ROOT`), Android user home, temporary directory, project build directory
and APK output path. Only original installed SDK inputs, the existing pinned
Gradle distribution archive, and the existing `modules-2` dependency-input cache
were copied separately from their common input sources. No APK, task output,
transformed dependency cache, project cache or configuration cache was copied
between builders. JDK and OS administration were shared. Prebuild JDK/SDK/dependency
regular-file inventories matched across sides; private inventories and paths are
not published. SDK postbuild inventory differences were recorded as above.

Each source export used the unchanged bootstrap, which supplies
`--no-daemon --dependency-verification=strict`, with these exact additional options:

```text
python android/build.py --offline --configure-on-demand --no-build-cache \
  --no-configuration-cache --rerun-tasks --console=plain \
  :memory-diagnostic:assembleRelease :memory-diagnostic:diagnosticTest \
  :memory-diagnostic:lintRelease
```

| Observation | Build A | Build B |
|---|---|---|
| Initial project build and project cache | Absent | Absent |
| Real Gradle result | Exit 0, 1m 32s | Exit 0, 1m 34s |
| Actionable tasks | 45 executed of 45 | 45 executed of 45 |
| Original APK | 16,036 bytes; new file identity and generation time within execution interval | 16,036 bytes; distinct file identity and generation time within its own execution interval |
| Source correspondence | All exact reviewed source bytes preserved | All exact reviewed source bytes preserved |
| SDK directory stability | FAILED: added `.knownPackages`; no original input changed/deleted | FAILED: same added filename; no original input changed/deleted |

Private process IDs, start/finish times, absent-output checks, exact commands,
input inventories, task logs and original output identities support **observed
separate local execution**. Neither build returned cached compilation, DEX or
packaging output. The three empty lifecycle tasks `preBuild`, `preReleaseBuild`
and `generateReleaseAssets` displayed `UP-TO-DATE`; they are not counted among the
45 actionable tasks. Native/Java-resource tasks with no source displayed
`NO-SOURCE`. AGP skipped `lintVitalReportRelease` / `lintVitalRelease` while the
requested full `lintAnalyzeRelease`, `lintReportRelease` and `lintRelease` ran.
These statuses are retained; no task was excluded or altered. Gradle emitted its
configuration-on-demand and deprecation notices. Local records cannot prove
absence of malicious host activity or authenticate their own independence.

### Inspection, controls and real failures

Both originals passed the existing unsigned package/manifest/API/version/release,
DEX capability, extraction-rule, native/asset/permission/signature inventory and
metadata-output controls. The exact package inventory/DEX checks were also reused
from `signed_package`; that function is a content screen, not signing or signature
verification. Source inspection confirms the diagnostic-only Option B setting,
null signing configurations and unchanged host metadata policy. Neither original
was repaired or rewritten. No encrypted SDK dependency output or APK signing block
was found. The DEX/resource screens are not proof of runtime semantics or an
independently authenticated source-to-binary reconstruction.

The existing allowlisted checker adds `--unsigned-pair`, `--unsigned-source-ref`
and `--unsigned-executions`. It reuses original-file identity/complete-byte equality,
source protection, package inspection, duplicate-key/size-bounded JSON reading
and final original re-read controls. It checks local record contradictions,
disjoint workspace/home paths, output/time/identity correspondence, exact exported
source and executed essential tasks. Private records and logs remain **claims**;
consistent forged records cannot establish independence or authority. No signing
function, permanent `qualified_authority` rejection or final admission boundary
was changed. The route reports equality before the later checks, so a failed
combined observation cannot obscure the raw byte result.

- Real positive controls: the two separately generated original APKs passed direct
  equality; both packages, source exports and essential task logs passed their
  individual checks. Before/after file identity and original-byte checks passed.
- Four disposable copies derived from the actual APK were rejected: a one-byte
  mutation, changed ZIP timestamp metadata, truncation, and appended data. Each
  failed `original_pair` with `original-bytes-differ`. The same original supplied
  twice failed `same-original-file`. None is a third genuine build.
- Synthetic copies of the local claim records exercised swapped/stale outputs and
  shared SDK/Gradle/Android-home claims. They never replaced real records. Swapping
  the genuine outputs was rejected by execution-time correspondence first.
  Added native inventory, invalid DEX and missing exported source were rejected;
  actual AST removal of the source-correspondence detector made its negative
  assertion fail. Original APKs stayed unchanged throughout.
- Permanent default regression additions: **16 execution-record negatives, six
  task-log negatives and two source-export negatives**, with **24 effective AST
  detector-removal assertion failures** across three detector bodies. Arbitrary
  exceptions do not count. Existing byte/ZIP/package mutation controls are reused.
- The genuine combined route and actual CLI **failed**, as required, on the
  unchanged false SDK-stability records. No successful end-to-end combined receipt
  is claimed. Signed qualification, actual signature negatives and Android runtime
  execution remain **NOT RUN / Unknown**.

Two private control-driver issues are retained: its initial filename shadowed
Python's `inspect` module; a later swapped-output assertion expected the artifact
identity reason but encountered the earlier valid time rejection. Separate
continuation scripts corrected the driver/import and expected reason, preserving
the original failure logs, records, sources and artifacts. Neither issue caused
a rebuild or changed the equality standard. The normal `python` app alias was
unavailable; the existing bundled interpreter was used without installation.
A redundant, inefficient read-only SDK inventory scan was stopped; the completed
per-file comparison above supplies the recorded finding. An initial ad hoc privacy
pattern matched HTTPS syntax; the corrected drive-prefix boundary check passed.

### Regressions, publication and next proof

The final diagnostic suite passed all existing **60 source negatives / 60 removal
assertions**, **60 signed-structure negatives / 60 removal assertions**, **eight
file/CLI/admission negatives**, six unsigned metadata negatives, the isolated Git
CLI controls, and the 24 new negative/removal pairs. Exact historical source-baseline
recomputation and exact-main source admission passed without regenerating any
protected digest. Diagnostic JVM validation passed **190 assertions**, compiled
cleanup-removal rejection, Activity bytecode controls and API-37 compilation.
Execution-lock validation passed **600 denials in three JVMs and three mutants**.

Foundation/harness validators passed: **183 files, 112 Markdown files, 54 requirements,
four ADRs**. Repository regression passed **148 of 152 tests with four existing
Windows skips**. Desktop-readiness, offline-image, frame-copy, Gradle-distribution
and installed-tools suites passed **28, 45, 4, 38 and 16** tests respectively.
Installed-tools needed no retry in this experiment. Linux/native runtime controls,
real Linux STRICT fixture suite, host APK rebuilding and device packaging controls
were not run locally; existing baseline/automatic workflow evidence is separate.

Live REST main agreed with local Git; connector and paginated REST open-PR inventories
were empty, so requested open heads/bases/diffs/files/checks/jobs/logs/reviews/comments/
threads were an empty set. PR #76's merge identity was reverified.
[Foundation run 43066504275](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43066504275)
passed foundation job **130682759507** and Windows job **130682759031**;
[Android run 43066504286](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43066504286)
passed job **130682760367**. Completed job/step records and logs were retrieved and
inspected. [GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
All Systems Operational, update `2026-11-11T16:59:11.503Z`. Initial sandbox network
and branch-write restrictions were resolved with scoped execution access.

**Pre-publication main advance:** a final live check found main at
`7bbdec67825d4c88d8789d3db643f3bc97ee777f`, a concurrent README-only commit after
the reviewed build base. The exact intervening diff was read; no build source
changed. It is preserved without rebasing, overwriting the README or regenerating
the protected governance digest. The new main fails the existing source admission
with `protected-governance`, reproduced locally.
[Its Foundation run 43071019706](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43071019706)
completed with foundation job **130698583492 failed** and Windows job
**130698584073 successful**; completed logs confirm that source-protection failure.
No Android run was listed for this README-only change. Open PRs were still an empty
set. The earlier three successful jobs apply only to `f272de8`, not the new main.
This PR retains the exact tested parent and is **not ready for integration into
the advanced main** until its protected-source discrepancy is separately reviewed
and resolved. No check bypass or baseline update is supplied here. The measured
pair remains an experiment of `f272de8`, never a claimed build of `7bbdec6`.

Reviewed requirements, ADRs, source controls, provenance/adoption/dependency records,
relevant incident/independent-chain/history evidence and all workflows. The six
existing worktrees, branches, ignored/private outputs and initially clean checkout
were preserved; no stash existed. Only the existing checker, this evidence record
and index change, as regular **100644** text. No new dependency, third-party code,
binary or license grant. Full diff, source admission, modes, links, whitespace and
public-data hygiene are reviewed before publication. Foundation and Android select
the change unchanged; QEMU filters do not. New-head CI is **UNOBSERVED at publication**.

The next necessary proof remains independently authenticated source/tools/OS and
administration, designated reviewers, Windows-incident disposition or a qualified
replacement chain, private signing custody and an authenticated receipt authority.
Future signed work requires separate authorization, genuine signed original-byte
equality and real signature controls; this unsigned result supplies none of them.
Independent backup, recoverable evidence, artifact transfer and exact Samsung
approval remain separate. The SDK-directory failure would require a separately
reviewed input-versus-generated-state contract before any different combined
stability assertion; this PR does not implement that change or waive the failure.
All fifteen historical signed-byte failures remain failures. ADR-0003's
**December 8, 2026 deadline and earlier termination conditions remain binding**.
**Independent backup UNVERIFIED; private evidence UNPRESERVED.**

## Main branch governance enforcement audit — 2026-11-17

The following dated entries describe the earlier three-method policy. The
[current disposition](#merge-only-policy-evidence) supersedes their proposed configuration and test plan.

**Outcome: missing main protection confirmed at this snapshot; one unapproved
correction proposed.** Windows x86_64; read-only remote
investigation and documentation. Scope: PDVA-REQ-008, 036–042, 048, 050–051, 054.
This extends the earlier protection Unknown and README-transition evidence here;
it does not rewrite their historical dispositions.

### Identity, permissions and effective enforcement

`git ls-remote origin refs/heads/main`, `git fetch origin main`,
`git rev-parse origin/main` and live branch metadata agreed on
`e79d74b7b5724d6326793810c479a3204f7739ab`, merged PR #80. An isolated worktree
started there. Existing files, branches, worktrees, stashes, ignored outputs and
private evidence were preserved. No applicable AGENTS.md was found. The complete
open-PR collection returned `[]` twice before publication: open heads/bases,
complete diffs/files/modes, checks/jobs/logs, reviews/comments/threads were an
empty set. No existing intended PR was omitted or duplicated.

**API Facts**, 2026-11-17; detailed response dated 03:17:49 UTC:

| Read-only endpoint | Observed result |
|---|---|
| [Repository](https://api.github.com/repos/innercoder78/privacy-decoy-virtual-android) | Public, owner type `User`, default `main`, not archived/disabled. Existing local CLI credential reports repository admin/push/pull permissions. No access was added. |
| [Main](https://api.github.com/repos/innercoder78/privacy-decoy-virtual-android/branches/main) | `protected=false`, `protection.enabled=false`, required-status enforcement `off`, empty contexts/checks. Metadata is not an enforcement test. |
| [Detailed protection](https://api.github.com/repos/innercoder78/privacy-decoy-virtual-android/branches/main/protection), connector | 403 `Resource not accessible by integration`: **Unknown for that credential**, not proof of absence. |
| Same endpoint, authenticated local CLI | 404 with explicit `Branch not protected`. Successful admin-capable repository access and branch metadata corroborate current classic-protection absence; this is not an unexplained inaccessible-resource 404. |
| [Rulesets including parents](https://api.github.com/repos/innercoder78/privacy-decoy-virtual-android/rulesets?includes_parents=true&per_page=100) | 200 `[]` through both connector and local CLI, no further page. |
| [Effective main rules](https://api.github.com/repos/innercoder78/privacy-decoy-virtual-android/rules/branches/main?per_page=100) | Local CLI `[]`. Connector's URL allowlist rejected this endpoint; that was a tool limitation, not a GitHub permissions response. |
| Collaborators, all affiliations, page size 100 | Only the owner with role admin returned; no second eligible reviewer observed. |

Initial sandbox network/keyring/metadata-write failures were resolved by scoped
command execution, not by changing GitHub credentials or settings. **No additional
read-only access is needed.** If this CLI access becomes unavailable, the minimum
replacement for the detailed endpoint is repository-scoped Administration: read,
plus metadata, per [API permissions](https://docs.github.com/en/rest/branches/branch-protection#get-branch-protection).
No token, confidential path or private receipt is published.

**Upstream Documentation:** the [effective-rules API](https://docs.github.com/en/rest/repos/rules#get-rules-for-a-branch)
returns active branch rules at every level, including organization rules; it
excludes disabled/evaluate-only rules. The parent-inclusive collection complements
that view. This repository has a user owner, not an organization owner.
[Rulesets are available for public repositories on GitHub Free](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets).
The paid account tier is **Unknown**; no paid-plan assumption is necessary for
the branch ruleset below. Push rulesets are not proposed.

**Inference:** neither classic protection nor active branch rules currently
requires PRs, approvals, current-head review, stale-approval dismissal, CI or
force-push prevention on main. There is no returned protection/bypass policy to
inventory: absent gates, not a discovered named bypass, are the issue. Authorized
writers can update main without those gates. Main is the default branch, so its
[separate default-branch deletion restriction](https://docs.github.com/en/pull-requests/how-tos/commit-changes/managing-branches-within-your-repository#deleting-a-branch) must not be confused with a missing
protection deletion rule. No successful deletion or force-push test is claimed.
Owner administration and repository deletion remain separate powers.

### Runtime and historical evidence

**GitHub Runtime Observation:** exact-main
[Foundation run 43966161213](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43966161213)
completed successfully on `push`. Jobs `foundation` **133646042440** and
`offline-image-windows` **133646042879** had successful substantive steps. Completed
logs were retrieved and inspected, including Linux control receipts and Windows
45/4/38/16-test suites. Check runs identify exact main and producer `github-actions`,
app ID **15368**. Legacy status `pending` had **zero contexts**, not another running
check. No Android/QEMU run was listed for that SHA; absence is not success.
Initial log output rejected terminal formatting; a read-only retry stripped it
before inspection. No dispatch or rerun occurred.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational, page update `2026-11-17T02:39:29.774Z`; this is a snapshot only.

**Repository/API Facts:** [README commit 7bbdec6](https://github.com/innercoder78/privacy-decoy-virtual-android/commit/7bbdec67825d4c88d8789d3db643f3bc97ee777f)
has one parent `f272de8207586ee2ec84412f6057ea580f0d0611`; complete diff changes only
README.md, 3 additions/47 deletions, regular 100644 mode unchanged. Committer is
GitHub `web-flow`; associated PR collection returned `[]`. Main's first-parent
history contains it between PR #76 and PR #77. Together these corroborate the
owner-supplied web-editor direct-main history. One parent alone could be a squash
merge; web-flow alone does not establish a direct push or unauthorized action.

Fresh [run 43071019706](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/43071019706)
metadata identifies `push` at that README SHA. Foundation **130698583492 failed**;
Windows **130698584073 succeeded**. Retrieved Foundation log confirms
`SourceRejection: protected-governance`. **Inference:** the source checker detected
the discrepancy after the commit reached main; that push-triggered check did not
prevent this update. Historical protection settings, intent and use of any bypass
remain **Unknown**. Current settings cannot establish the historical settings.
The subsequent exact README integration correction did not erase that failure.

Live merged PR metadata #76–80 targets main, with merge SHAs `f272de8`, `2c64fc1`,
`2bd1fc1`, `4c2ebd5`, `e79d74b`, matching local history. Each submitted-review
collection returned `[]`. Merges and green jobs do
not prove that GitHub required either. No experimental enforcement test was run.

### Workflow applicability and evidence limitations

All three definitions were inspected at exact main:

| Workflow and check context | Applicability |
|---|---|
| [Foundation](../../.github/workflows/foundation.yml): `foundation`, `offline-image-windows` | All ordinary PRs, main pushes; no path filter or job-level skip condition. Both are suitable universal baseline required contexts. |
| [Android](../../.github/workflows/android-harness.yml): `android` | PR/main push paths: `android/**`, `.github/**`, `.gitignore`, `.gitattributes`, `docs/evidence/gate-0-isolated-worker*`, `docs/source-provenance-policy.md`, `docs/source-reference-catalog.md`. Includes APK builds; none run by this task. |
| [QEMU](../../.github/workflows/qemu-android-research.yml): `cross-build` | PR only: its own workflow and `.github/scripts/qemu-android-research.py`, `kernel-fd-research.py`, `arm64-boot-plan-research.py`, `startup-order-research.py`. Cancel-in-progress enabled. |

This evidence record and index select only Foundation/Windows. README and most
governance/evidence edits do not select specialized jobs, but can fail Foundation
source admission. Android/workflow edits select Android; the enumerated QEMU
scripts select both specialized workflows. Security policy and reviewable evidence
still need semantic review. Protected digests do not authenticate their checker.

**Upstream Documentation:** [required-check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
distinguishes a path-skipped workflow (required check may stay pending) from a
skipped job; GitHub accepts success/skipped/neutral conclusions for required
checks. Results must cover the latest applicable SHA; head and test-merge results
have distinct handling. Thus globally requiring Android/QEMU would strand
out-of-filter documentation PRs. Requiring only the universal checks leaves
specialized-job enforcement dependent on review. A green label is not proof of
substantive execution or security.

A settings-only rule cannot enforce PDVA's stronger predicate: applicable jobs
actually executed expected substantive steps on intended source and succeeded.
Missing, skipped, neutral, cancelled, timed-out, zero-step, failed and pending
outcomes remain non-success evidence. The eligible reviewer must inspect complete
diffs, applicability, exact checkout SHA, producer, steps and logs; withhold
approval/merge when an applicable job is absent or inconclusive. Unselected jobs
are not applicable, never relabeled passes. Existing workflows remain unchanged.

A later machine-enforced solution would require a separately authorized,
always-triggered admission check from a trusted producer. It must enumerate the
complete diff without truncation, apply a reviewed path/dependency policy, verify
exact-source jobs and expected substantive steps, reject missing/wrong-source or
non-success results, and explicitly report non-applicable suites. Counting steps
or trusting names alone is insufficient. Changes to that policy/checker must not
let an unreviewed PR certify itself. Shared security-sensitive inputs also need
coverage. This is a precise future design obligation, **not an implemented check
or part of the settings-only proposal**; separate approval and adversarial tests
are necessary. No dummy successes, weakened filters or CI suppression proposed.

### Historical one-approval proposal

PR #81 proposed one required GitHub approval. The later interim decision selected zero.

Create one **active branch ruleset**, name `main-review-and-ci`, include exactly
`refs/heads/main`, no exclusions and **empty bypass actors**, with:

1. Required PR; **one approving review**, stale approvals dismissed on changes,
   approval of most recent reviewable push required, review conversations resolved.
2. Required contexts **`foundation`**, **`offline-image-windows`**, each bound to
   GitHub Actions integration **15368**; strict up-to-date checking enabled.
3. Force pushes blocked; branch deletion restricted. Do not restrict all updates
   (which would require bypass for normal merges). Retain existing merge methods;
   no new signing, linear-history or deployment requirement.

These settings are supported by [GitHub rules documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).
This is a minimal baseline correction, **not complete automatic enforcement of
PDVA evidence**. Specialized jobs retain the review obligation above. Producer
binding rejects other apps' same-name checks, not malicious edits within a
PR-controlled Actions workflow. Strict up-to-date checking does not turn the
existing explicit PR-head checkout into synthetic-merge-tree testing.

The proposed latest-push approval would block a PR without an eligible approval.
Ruleset mutation requires Administration: write. This proposal was never activated.

[Classic branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
exempts administrators by default unless configured otherwise. The proposed
ruleset has no bypass actors, including no admin exception. An authorized owner
can still edit/disable it; it does not resist malicious administration. Review
dismissal remains a trust risk: dismissing objections is not substantive approval.

The proposed recovery path required verified restoration of the exact settings.
No standing bypass, force push or deletion exception was proposed.

**Proposed validation, NOT RUN:** after separate authorization, read back all
settings; use an explicitly authorized disposable branch with equivalent rules
for positive/negative documentation and in-filter cases, direct-update/force-push/
deletion rejection, missing/stale/latest-pusher approval, wrong app/SHA, and
missing/failed/cancelled/timed-out/skipped/neutral/zero-step checks. Record GitHub's
skipped/neutral acceptance as a strict-evidence limitation, not test success.
Confirm successful valid cases too. No such tests or administration changes were
performed here, and no destructive test against main is proposed.

### Falsifiers and preserved boundary

A successful authorized read showing active applicable protection would falsify
this snapshot's absence conclusion and require reassessment, not redundant rules.
A changed reviewer inventory changes the activation prerequisite. Workflow trigger,
job-name, producer or checkout changes invalidate the applicability proposal until
reviewed. Historical settings/associated-PR evidence may refine the direct-main
inference. Actual adversarial enforcement remains **Unknown**; an unauthorized
bypass claim is not supported. **Unsupported product scope** is separate: no
engine, privileged execution or production isolation is adopted here.

Reviewed [governance](../governance.md), [source policy](../source-provenance-policy.md),
[acceptance criteria](../acceptance-evidence-criteria.md), requirements, all ADRs,
Gate 0 criteria, security boundary inventory and relevant history. Public source
and source checkers do not themselves enforce admission to main. Missing server
gates weaken prevention of unreviewed source/evidence changes; they do not imply
hostile Android guest access to GitHub, nor does branch protection contain a guest.
The diagnostic execution lock, source protections and complete guest/host boundary
remain intact. ADR-0004 Option A and ADR-0003's existing bounded decisions remain.

Original analysis only, in this record and its index; no upstream code, dependency,
binary or license grant. No workflow, source pin, requirement, ADR, secret or
administration changes; no APK/build/signing, keys, phone/ADB, VM or installation.
Local checks and committed-source admission are recorded before publication.
New-PR hosted results remain **UNOBSERVED**. **Gate 0 Unresolved; Gates A–G Not reached. Independent build/signing
qualification and physical testing remain blocked.** Existing private evidence
and backup gaps are not resolved by this public record.

### Local validation of this evidence change

Existing bundled Python: Foundation validator **PASS**, 183 files, 112 Markdown,
54 requirements, four ADRs; includes local file-link checks (not fragment checks).
Unchanged diagnostic source suite **PASS**, including exact-source admission,
60 source negatives/removals, 11 README-transition negatives/removals and existing
synthetic signed/unsigned, SDK-state and cache-integrity controls. These are source
and fixture results, not signed qualification or Android runtime evidence.
Full two-file diff, regular 100644 modes, whitespace, new section/index anchor,
public-data/provenance review and exact committed-head admission are checked for
publication. The initial evidence-file write was denied by sandbox permissions;
scoped retry succeeded without changing security settings. No failure is counted
as a pass. No additional tests or workflow changes were needed for Markdown.

## Owner-approved interim main protection — 2026-11-17

**Owner decision: APPROVED INTERIM DIRECTION. Stage 1: document, verify and
prepare only. Activation NOT AUTHORIZED UNTIL RESOLVED: mandatory ADR/source
admission is blocked below. No protection is enabled by this record.**
Approved on 2026-11-17. Scope: repository governance,
PDVA-REQ-008, 036–042, 048, 050–051 and 054; no product or gate advancement.

The interim decision selected required PRs and universal CI with zero mandatory
GitHub approvals. Production activation remained pending.

### Fresh remote preflight and historical reconciliation

**Repository/API facts:** `git ls-remote origin refs/heads/main`, `git fetch
origin main`, `git rev-parse origin/main` and live branch metadata agreed on
`6b59d9469017bfb3fc490164edb127c2e0701b54`. Work started at that commit in a
separate local worktree; local main was not synchronized, reset or rebased.
The paginated open-PR endpoint returned `[]`, corroborated by connector search:
all open heads/bases, full diffs/files/modes, checks/jobs/logs, reviews/comments
and threads were an empty set. No applicable repository AGENTS.md was found.

[PR #81](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/81)
is merged into main: base `e79d74b7b5724d6326793810c479a3204f7739ab`, head
`31348cb82cd2027d1601fafb271f2a3101762b60`, merge commit equal to verified main.
Its complete diff has 248 additions and no deletions in this record and index;
both remain mode 100644. Submitted reviews, issue comments, review comments
and review threads returned empty collections. The earlier audit remains historical evidence;
its one-approval proposal was not activated or implicitly accepted by merge.

Authenticated read-only API observations reproduced its configuration findings:

| Surface | Current observation |
|---|---|
| Repository and permissions | Public, user-owned, default main; connected account reports admin/maintain/push/pull. Local CLI can read the detailed protection endpoint. No permission grant made. |
| Main and classic protection | `protected=false`, protection disabled, status enforcement off with empty checks/contexts; detailed endpoint returns explicit 404 `Branch not protected`. |
| Parent-inclusive rulesets and effective main rules | Both paginated collections return `[]`; no existing ruleset or bypass list to modify. |
| Collaborators | Only `innercoder78`, role admin. No qualified independent approving collaborator is established. |
| Repository merge methods | Merge, squash and rebase all enabled; auto-merge disabled. Preserve these settings. |

These are point-in-time reads, not enforcement experiments. Repository admin
permission is not proof that the particular credential can successfully create
this exact ruleset. Mutation capability and server acceptance remain **Unknown**.
Initial sandbox network/Git-metadata restrictions were resolved by scoped
execution; no host privilege or security-setting change was performed.

**GitHub runtime observation:** post-merge
[Foundation run 44010607205](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44010607205)
is completed/success on `push` at exact verified main. Jobs `foundation`
**133796452914** and `offline-image-windows` **133796452690** have successful
substantive steps. Retrieved completed logs show Foundation source validation,
152 repository tests, companion source/negative/removal controls, native 7/1
controls, modeled bootstrap, Linux lifetime, seccomp and revocation receipts;
Windows shows the 45/4/38/16-test suites. Initial CLI log output refused terminal
escapes; retrieval with escape stripping enabled inspection. These are existing
baseline receipts, not new-head tests or product-security qualification.
Exact-main check runs identify contexts `foundation` and `offline-image-windows`,
producer slug `github-actions`, app ID **15368**. No Android/QEMU run was returned
for this SHA; those jobs were not selected, not successful executions.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational, page update `2026-11-17T02:39:29.774Z`; snapshot only.

Requirements, governance, ADRs, acceptance/gate criteria, source policy/catalog,
relevant evidence and history were reviewed. All three workflow definitions match
verified main. Existing reviewed checkout pin
`3d3c42e5aac5ba805825da76410c181273ba90b1` and dependency inventories are unchanged.
No source adoption, new dependency, binary, redistribution right or private
evidence is introduced. This is an original analysis extension, not a new survey.

### Exact interim settings prepared for separate authorization

**Documentation basis, checked 2026-11-17:** GitHub's
[rules reference](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
documents PR requirements without mandatory approval and public-repository
ruleset availability, including GitHub Free. The paid account tier is Unknown
and is not assumed. The
[REST rules schema](https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset)
defines the fields below and requires Administration: write for creation.
These establish documented semantics, **not acceptance of this combination on
this repository**. The live settings UI was not exercised; exact UI availability,
saved normalization and enforcement require the authorized Stage 2 test/readback.

| Setting / API field | Prepared value and boundary |
|---|---|
| Name, target, intended enforcement | `main-review-and-ci`, `branch`, `active` only after Stage 2 approval/tests. Nothing submitted now. |
| `conditions.ref_name` | `include: ["refs/heads/main"]`, `exclude: []`; no wildcard or default-branch token. |
| `bypass_actors` | `[]`, including no administrator, repository-role, app or emergency standing bypass. |
| `pull_request.required_approving_review_count` | `0`; require a PR, with no mandatory independent GitHub approval in the interim. |
| Other PR parameters | `dismiss_stale_reviews_on_push: false`, `require_code_owner_review: false`, `require_last_push_approval: false`, `required_review_thread_resolution: false`. No required teams/reviewers or additional approval rule. Manual review must still resolve objections. |
| PR allowed merge methods | Preserve `merge`, `squash`, `rebase`; do not alter repository methods. |
| `required_status_checks.required_status_checks` | Exactly `{context: "foundation", integration_id: 15368}` and `{context: "offline-image-windows", integration_id: 15368}`, subject to fresh producer verification and server readback. No silent fallback to any-source checks. |
| `strict_required_status_checks_policy` | `true`; PR must be current with base. `do_not_enforce_on_create: false`; no creation exemption. |
| Additional rule types | `non_fast_forward` and `deletion` only: block force pushes and restrict deletion. |
| Excluded rules | No `update` (Restrict updates), creation restriction, signing, deployment, linear history, merge queue or extra approval requirement. |

This table is a reviewable specification, not an executable administration
request. In the UI, verify the PR checkbox remains enabled when the approval
count is zero and last-push/code-owner approval options are off. Check all
defaults and newly introduced options against this specification. In particular,
GitHub documents the extra unattributed-Copilot approval default as ineffective
at zero approvals; it must not introduce an additional approval here. Any
unsupported field, hidden default or rejected combination is **STOP/Unknown**,
not permission to improvise a bypass or stronger/weaker settings.

The expected benefit is a server-side PR/CI barrier before ordinary main
updates, plus protection against force pushes and deletion. Current absence of
protection is not evidence of unauthorized activity. Default-branch deletion
restrictions are separate from the proposed explicit deletion rule.

### Check semantics and remaining risks

[GitHub check semantics](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
accept skipped/neutral as well as success and distinguish head from test-merge
results. PDVA must not call skipped, neutral, cancelled, timed-out, missing,
pending, failed, zero-step or unverifiable work a successful security check.
Path-filtered Android and QEMU remain conditional; do not globally require them
or call non-applicability execution success. Only the universal Foundation and
Windows jobs apply to these two evidence files. The earlier workflow table
remains current. No workflow or filter is changed.

Binding to app 15368 attributes the producer, not an immutable workflow or trusted
checker. A PR can modify a same-app workflow/checker; manual full-diff review is
still essential. Strict freshness does not convert the workflows' explicit
PR-head checkout into testing a synthetic merge tree. The owner can still edit
rules through administration; no-bypass does not remove that power. Compromised
owner credentials, mistakes, CI outages and unverified specialized obligations
remain risks. This interim policy enforces neither independent review nor every
specialized CI/evidence requirement and warrants no full-repository-security claim.

The selected configuration required universal CI with zero mandatory approvals.
Standing bypass and globally required path-filtered jobs were excluded.

### Mandatory ADR and immutable source-admission blocker

**Governance interpretation:** this material repository evidence-enforcement
decision must have a new PDVA ADR under [governance](../governance.md) and the
owner's Stage 1 instruction. The next sequential candidate is
`docs/decisions/ADR-0005-interim-main-branch-protection.md`. Its final ADR would
need the owner/date, selected scope/settings, alternatives, affected obligations,
consequences, preserved/invalidated evidence, tests and recovery requirements.
No accepted ADR-0005 exists; this evidence extension is not a substitute.

**Source observation:** unchanged
[source checker](../../.github/scripts/test-memory-diagnostic.py) pins
`SOURCE_BASE=69a7165043e1e7fc565a9ff10f044adc4874c595`. `REVIEWED_FILES` contains
only that checker, this evidence record and its index. `protected_group` assigns
other documentation to governance; `protected_evidence` hashes the sorted exact
paths and bytes and counts files. `check_protected_source` permits only the
original governance pin or the exact reviewed README transition. Neither allows
another ADR: original count 109/hash
`384c3a4289c41a25e00a5a90f5eaee5f5a8b7208438fe8de099ad359cb57c45c`;
README-transition count 109/hash
`27162b9af9a45f36a674d76895817ea37285f6ef38487332325f0127f11400ab`.

**Local runtime observation:** loaded the unchanged checker using standard-library
`runpy`, read the exact-main snapshot with `committed_source('HEAD')`, and called
`verify_companion_delta(snapshot, (SOURCE_BASE, PROTECTED.copy()))`: **PASS**.
Added only the candidate ADR path at mode 100644 to an in-memory copy, with bytes
`b'# ADR-0005: Interim main branch protection\n\nOwner direction selected 2026-11-17; activation blocked.\n'`.
The governance count became 110/hash
`3301f6b70ca16b313b74eddef38848fc4f733aef8a75c6e0d6e959c712ff7838`;
the same unmodified verifier raised **`SourceRejection: protected-governance`**.
Rechecking the original snapshot passed. No ADR file, baseline, allowlist or
checker was changed; this is a local source-admission witness, not a GitHub test
or a complete proposed ADR. Adding any ordinary sequential ADR changes the pinned
inventory; changing its prose cannot preserve the 109-file count.

**Disposition: activation NOT AUTHORIZED UNTIL RESOLVED.** Do not weaken, bypass,
repin or silently amend source protections to admit ADR-0005. A separately
reviewed, explicitly authorized resolution must preserve historical invariants
and satisfy ADR admission/approval before Stage 2. No resolution is presumed or
implemented here. Passing this evidence-only diff does not satisfy that blocker.
The earlier unapproved proposal is superseded as direction only; old empirical
failures and original source receipts are not invalidated or relabeled.

### Historical disposable test plan

The earlier plan covered configuration readback, PR merges, direct updates,
force pushes, deletion, check provenance and freshness, and recovery. Stage 1
did not execute those tests. Subsequent outcomes and outstanding gaps appear
in the [disposable test results](#merge-only-policy-evidence).

### Stage 1 validation and preserved boundaries

The publication is limited to this existing record and index, regular Markdown
mode 100644. Source/foundation validation, historical-pin recomputation, complete
diff/mode/link/privacy review and exact committed-head admission are required
before publication. Local results are recorded below. Hosted results for the
new PR remain **UNOBSERVED**.

ADR-0004 Option A, ADR-0003's bounded decisions/deadline, all fifteen historical
signed-byte failures, diagnostic execution lock and source safeguards remain
unchanged. No Android CLI, APK build/signing, signing keys, device/USB/ADB access,
VM execution, tool installation, host privilege or system-security changes.
No GitHub administration, visibility, collaborator, merge-method or workflow
changes. **Gate 0 Unresolved; Gates A–G Not reached. Independent build/signing
qualification and phone testing remain blocked.** This governance work establishes
neither Android isolation nor product feasibility; existing private-evidence and
independent-backup gaps remain unresolved.

**Local validation results:** existing bundled Python on Windows x86_64;
`validate-foundation.py` **PASS** (183 files, 112 Markdown, 54 requirements,
four ADRs). Unchanged `test-memory-diagnostic.py` **PASS**, including 60 source
negatives/removals, 11 README-transition negatives/removals and existing synthetic
package, unsigned/signed-claim, SDK-state and cache-integrity controls. Separate
`--verify-source-baseline` and `--verify-readme-update` recomputation **PASS**.
Both evidence files' local links and heading fragments resolve. Complete diff,
100644 modes, whitespace, exact two-file scope and public-data/provenance review
passed. No new dependency or binary; protected files remain byte-identical to
verified main. These source/fixture results do not qualify signed artifacts or
establish Android execution. Final committed-head source admission is a required
publication check, reported with the PR; this text does not predict hosted CI.

## Consolidated ADR-0005 source admission — 2026-11-17

**Repository implementation prepared for review; administration NOT EXECUTED.**
The exact ADR addition resolved the historical Stage 1 source-admission blocker.
The rejected-proposal receipt remains reproducible. This transition changed
repository source only.

### Fresh baseline and applicability

Live remote main, fetched origin/main and the isolated worktree agreed on
`e8923e315b603227db4b42c9036c184aed28b6fa`. PR #82 is merged; connected search
and REST both returned zero open PRs, so requested open-PR heads/bases/full
diffs/files/modes/checks/jobs/logs/reviews/comments/threads form an empty set.
Local primary main and origin/main were stale before fetch; existing worktrees,
branches, dirty/untracked and ignored outputs and private records were preserved.
Initial sandbox network/Git metadata operations failed; narrowly scoped approved
Git operations succeeded without security-setting changes.

Exact-main [Foundation run 44012740354](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44012740354)
reported successful `foundation` job 133803359427 and `offline-image-windows`
job 133803359774. Their completed logs show substantive validation and controls,
including 45 image, four frame-copy, 38 Gradle and 16 installed-tools tests on
Windows. Check-run producer was freshly confirmed as GitHub Actions app **15368**.
The live ruleset list and effective-main-rule list were empty; merge, squash and
rebase repository settings were all true. GitHub Status reported All Systems
Operational, page update `2026-11-17T15:19:18.141Z`. These are baseline observations,
not results for this PR. Existing protection/authority must be freshly read again
before any subsequent administration.

The existing three workflow definitions were inspected. This checker change
selects universal Foundation/Windows **and Android** via `.github/**`; QEMU's
explicit path filters do not select it. Android job execution is an applicable
hosted review requirement; it was not locally run or manually dispatched. Local
Android CLI/build/signing/device/VM operations remain prohibited. No workflow,
filter, job name, checkout pin or dependency changed. New-PR CI is UNOBSERVED at
publication.

### Exact admission and immutable history

The original `SOURCE_BASE`, `PROTECTED`, `REVIEWED_FILES`, README transition
constants, `protected_evidence`, `check_protected_source` and
`verify_companion_delta` remain unchanged. Historical governance remains count
109 with SHA-256 `384c3a4289c41a25e00a5a90f5eaee5f5a8b7208438fe8de099ad359cb57c45c`;
its exact README transition remains count 109 with
`27162b9af9a45f36a674d76895817ea37285f6ef38487332325f0127f11400ab`.
No digest is recalculated to conceal the new file or any earlier failure.

The separate `verify_current_source` requires the fixed ADR path, mode 100644
and SHA-256 `78e108ca2b5b4ca2660f5b7d101622fd890d1e5cefcf4576beff1bc225a0de87`,
and the exact reviewed README. Only after hashing the exact ADR separately does
it project the remaining snapshot through the unchanged historical protections.
All other governance paths/counts/bytes remain pinned; no wildcard or caller
allowlist exists. Deleting the ADR fails current admission rather than selecting
an older contract. Default tests, source-ref CLI and signed/unsigned source
prechecks use current admission; historical audit entrypoints remain separate.
No signing/package/SDK qualification detector or execution-lock source changed.

`--verify-adr-update` reads immutable prior main and authenticates its checker
against SHA-256 `f31fc60389e9096db8a330d96a5018646874857342ab1423bfeaad45791b7412`.
It recomputes the historical baseline/README transition and compares the whole
prior/current source delta to exactly the new ADR plus the same three original
review files. It executes the immutable prior checker on prior and new snapshots:
prior passes; new ADR fails `protected-governance`. Current admission rejects
old-source replay. It also reproduces Stage 1's exact rejected placeholder and
its recorded count/hash; that placeholder still fails both policies. Original
README replay fails current admission, and removal of the current-README detector
makes that exact negative assertion fail. Missing immutable objects cannot pass
this explicit audit; shallow CI uses the reviewed pins and claims no fresh Git
history recomputation.

The original three review files remain a manual review boundary, not self-proving
authorization. Candidate Python can lie if a reviewer approves a malicious
checker; neither hashes nor app identity eliminate that risk. All changed bytes
must be reviewed independently. Future governance changes need a new exact,
reviewed immutable transition and negative/removal evidence, never rebaselining
historical pins. The ADR defines that maintenance process.

### Actual controls and remaining limits

The current-state suite exercises 123 specific negative cases with effective
detector-removal failures: modified/substituted/deleted ADR, extra governance/ADR,
every existing protected governance file and representatives of all seven
protected groups, plus missing/wrong/candidate-derived baseline identities.
Additional controls cover rename, executable/symlink/gitlink/directory modes,
README deletion/change, prior identity/checker substitution, real directory and
hardlink fixtures and their detector removals. Overlapping mode checks are tested
individually without disabling a second control to manufacture acceptance.
Windows reparse-parent handling uses a synthetic lstat fixture; real Windows
symlink creation is NOT RUN (no privilege changes). POSIX symlink control remains
in the suite for applicable hosted execution, not claimed as a local result.

The historical 60 source negatives/removals and 11 README negatives/removals still
pass on their explicitly historical projection, after whole current admission.
A separate assertion proves that historical admission rejects the new ADR, so
these passing historical fixtures cannot conceal that rejection. Existing
metadata, signed/unsigned receipt/package, SDK-state and cache-integrity tests
also pass. These fixtures do not qualify any real APK, toolchain or signing chain.

All fifteen signed-byte failures remain failures; failed SDK-state qualification
is not repaired. Independent build/signing custody, private backup and physical
readiness remain blocked. Gate 0 Unresolved; Gates A–G Not reached. No Android
CLI, APK signing/key operations, device/ADB/USB, VM execution, installation,
confidential publication or new binary/dependency adoption occurred. This change
is original standard-library Python and governance prose, with existing reviewed
dependencies and provenance unchanged. No product-security obligation is relaxed.

Local validation used existing bundled CPython 3.12.14 on Windows: foundation
184 files / 113 Markdown / 54 requirements / five ADRs; repository regression
152 tests (148 passed, four existing Windows skips); harness validator; readiness
28; offline image 45; frame copy four; Gradle distribution/startup/verification
38; installed tools 16. Historical baseline, README and ADR transition audits
passed. The full memory-diagnostic source/fixture suite passed. Linux-only native
host controls and Android jobs are NOT RUN locally; applicable hosted results
require review after publication. No native compiler/tool installation occurred.

Final review verifies unchanged historical constants and detector functions,
exact prefix preservation of this prior evidence record, four-file scope, regular
100644 modes, UTF-8 text, local links, ruleset JSON and whitespace. An initial
ad hoc Markdown-link scan incorrectly treated a Python call as a link; limiting
that scan to Markdown fixes the review script. Foundation caught Windows-default
encoding in the new evidence suffix; the suffix was corrected to UTF-8 without
changing any historical bytes, then validation rerun. Neither initial failure
counts as a successful check. Exact committed-head source admission is checked
before publication; hosted results are not predicted.

## ADR-0005 incident and enforcement evidence, 2026-11-18

The [immutable prior record](https://github.com/innercoder78/privacy-decoy-virtual-android/blob/2e820f5d0ee8319eb428b6e25081479a0fb5c064/docs/evidence/gate-0-companion-source-controls.md#adr-0005-incident-and-enforcement-evidence-2026-11-18) preserves the original incident and validation receipts.
All three November 17 disposable merges were unauthorized. Each had zero
GitHub reviews. Their technical observations and failed activation qualification
stand as originally recorded. The historical table below describes that exercise.

| PR and method | Time UTC | Exact final head | Result on disposable target |
|---|---|---|---|
| [84, merge](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/84) | 23:17:04 | `0648dda7672c2f1443fd55c656e5f08adb80f8d5` | `752413f5b50d68d46e3793685716f8b7baeddfd9` |
| [85, squash](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/85) | 23:19:20 | `ccddfa2c90a3e0bc5145aaf604c10b3d46535a2c` | `9ccc1a2fdeea42dcc21474cde2c75aec36908d15` |
| [86, rebase](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/86) | 23:21:12 | `1f1c7681451c054eef323773937326064f4922fb` | `429a7ef0cde629c30fe8c4896e52bb3d8b93f56a` |

The target began at production main `2a15f06f2f89711857ff08721f6dd39fe77b2a2c`.
The first result has main and #84's final head as parents. Each subsequent
result has the preceding result as its sole parent. The refreshed #85 head
has its original head and #84's result as parents. The final target is six
commits ahead of main. Its cumulative diff adds 19 lines to this record and
six to the evidence index, with zero deletions and both modes 100644. The
individual PRs added 13, six and six lines respectively. No incident merge
advanced production main.

### Actions execution on the disposable heads

**VERIFIED FACT.** GitHub check runs identify Actions app 15368. Downloaded
job logs identify each checkout and the executed tests. Job IDs below are in
Foundation / offline-image-windows order. Both succeeded except where shown.

| PR and state | Commit (final heads above) | Job IDs |
|---|---|---|
| 84, broken link | `108eecce15e943876c504f331eccbd75043b2374` | 134442259265 **failure** / 134442258934 success |
| 84, intermediate repair | `9f107e1b3c3288ee56212cfcabd83ddb9181a932` | 134443239961 / 134443240197 |
| 84, final repair | `0648dda` | 134443546476 / 134443546025 |
| 85, original base | `6cfa4e3e3d13c19cd74df305fc25f3446742f15d` | 134443541126 / 134443541316 |
| 85, refreshed | `ccddfa2` | 134444771556 / 134444771115 |
| 86, final | `1f1c768` | 134445787363 / 134445787720 |

Foundation diagnosed the deliberate missing target
`adr0005-deliberately-missing-control.md`. Successful Foundation jobs ran
repository regression (152 tests) and the seven native positive controls.
Windows logged suites of 45, 4, 38 and 16 tests. The intermediate repair
altered historical punctuation despite green jobs. The final repair restored
the historical prefix. Android and QEMU workflow filters excluded these
evidence-only PRs.

### Enforcement and recovery

**RUNTIME OBSERVATION.** The following results come from original local
command outputs and API responses, correlated with the historical action
sequence. The deleted rule cannot be queried retrospectively. The receipts
are owner-held local records without independent timestamp attestation.

| Disposable operation | Observed response and scope |
|---|---|
| Unassociated update from original main to the broken-link head | GH013 required a PR and expected two checks. Separate ref lookup still returned original main. Missing checks were part of a combined rejection. A missing-only PR rejection remains UNKNOWN. |
| Forced update to `e8923e315b603227db4b42c9036c184aed28b6fa` and branch deletion | Separate GH013 responses expressly rejected force-push and deletion. Ref lookups after each still returned original main. |
| Failed #84 and pending #86 | HTTP 405 named failing Foundation on the initial #84 head. On #86 the response named two checks in progress. Their target bases remained original main and the #85 result respectively. |
| Stale #85 | After #84 advanced the target, the old head had two successful jobs. GitHub reported it behind, four behind and one ahead in compare. The exact-head request returned 405 expecting two checks and the target remained at the #84 result. Strict freshness is the supported explanation (INFERENCE). The response itself did not name the stale-base rule. |
| Fresh, corrected heads | All three methods updated the target under restored protection with zero approvals. The merge events establish mechanical compatibility. The mandatory authorized positive test FAILED for every method. |
| Configuration and recovery | Independent GET readbacks matched every requested field of the ADR body with the disposable name/ref substituted. Four effective rules were present, bypass actors empty, caller bypass reported never. Control-ref and main lookups returned empty. Admin PUT disabled the exact rule, GET confirmed disabled and effective rules were empty. PUT restored it. The restored and final GET bodies matched the intended fields and all four effective rules returned. The required reviewed post-restore merge remains unsatisfied. |

## Merge-only policy evidence

**Proven under the earlier three-method configuration.** Ruleset 27524027
targets only `codex/adr0005-ownerreview-test-20261118`. The November 18
readback showed active enforcement, empty bypass actors, strict required checks
from app 15368, deletion and non-fast-forward restrictions, and all three merge
methods enabled. The target's effective rules matched. No repository or inherited
ruleset applied to main. Effective main rules were empty and the classic main
protection endpoint returned branch not protected.

| Reviewed PR | Tested head (second parent) | Merge result | Foundation / Windows job IDs |
|---|---|---|---|
| [88](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/88) | `e57e5b044864c672d47493ed8307d58af0c3e157` | `77f8ba43be86392eefdc307188caa6e2294d6559` | 134608080467 / 134608079889 |
| [89](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/89) | `f39ee3e431e112fb9c74f14c14f451b09ec0f707` | `8226525bb8fc85126e8debeb9d844eec46dfa8c6` | 134615483152 / 134615483553 |

GitHub ruleset history records versions 58322128 (active), 58322165 (disabled)
and 58322171 (active again at 05:45:51 UTC), each allowing three methods.
PR #88 merged at 05:57:01 UTC after restoration.

The first parent of #88 was main at `2e820f5d0ee8319eb428b6e25081479a0fb5c064`.
The first parent of #89 was #88's result. Both results were ordinary two-parent
merge commits. The original squash intention for #89 has no bearing on its result.
In each pair, both Actions jobs from app 15368 succeeded on the exact head.
Foundation ran repository and native controls. Windows logged 45 offline-image,
4 frame-copy, 38 Gradle distribution and 16 installed-tools tests. The changes
were evidence-only. Android and QEMU filters excluded both PRs.

**Partially supported.** The earlier three-method trials demonstrated rejection of
direct updates, force pushes, deletion, failed and pending checks. Administrative
disable/restore readbacks and the later reviewed post-restoration merge support
recovery for the three-method configuration. The November 17 unauthorized
results cannot supply authorization evidence. Missing checks occurred in a
combined rejection. Missing-only enforcement remains Unknown.

**Inference.** Strict freshness explains the stale-head refusal for #85. The
response named expected checks without identifying the stale-base rule. A
reviewed stale-to-refreshed merge sequence remains unproven.

**Unknown.** Wrong producer and wrong SHA were each unexercised. Cancelled,
timed-out, skipped, neutral and zero-step cases each lack an adversarial
observation. A skipped or neutral conclusion can satisfy GitHub status semantics.
Substantive execution and checkout identity require inspection of the logs.

**Not run and blocking activation.** Exact merge-only configuration acceptance,
stored and effective readbacks, method exclusion, legitimate post-restoration
merge and recovery with that exact setting remain unverified. The prior evidence
can support unchanged controls. It cannot close these configuration-specific
gaps. Mandatory Unknowns require resolution and separate authorization
before activation. Squash/rebase qualification is retired. No further method-test
PRs are required by this policy.

All fifteen historical signed-byte failures and failed SDK-state qualification
stand. Gate 0 remains Unresolved and Gates A-G remain Not reached.

### Source transition and validation

The prior canonical tree at `2e820f5d0ee8319eb428b6e25081479a0fb5c064`
pins the previous checker and ADR independently of the proposed tree. Run
`test-memory-diagnostic.py --verify-merge-policy-update` with full history to
recompute the older audits, execute the original checker's negative controls,
and verify rejection in both directions. The new ADR has the same exact path
and mode 100644. Its SHA-256 is
`eb2e6ab7bad2ae4ebf3065251d9d96e5f515f6bccba0183b982acecb389831ca`.
The normal source checks use reviewed pins in shallow checkouts. The ADR digest does
not authenticate the checker or evidence files.

Windows validation covered Foundation, the harness, memory/source admission,
repository regression (152 tests, four existing skips), desktop readiness (28),
offline image (45), frame copy (4), Gradle distribution (38) and installed tools
(16). The first installed-tools run timed out creating a temporary junction.
All 16 passed on the host retry. Linux native and Android build jobs were unrun
locally. The checker change selects Foundation, Windows and Android CI. QEMU's
path filters exclude it. On PR #90 head `fea3ddb48619c6ab76a4ef0301ab1014624ec369`, all three
applicable Actions jobs succeeded. Foundation (134624310608) recorded 152
repository tests and seven native positive controls. Windows (134624311027)
ran suites of 45, 4, 38 and 16 tests. Android (134624310552) recorded a successful
build. Each log identified that head. The revised head has separate CI results.

### Regular merge under the exact disposable rule

At 18:00:56 UTC on November 18, 2026, [PR #91](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/91)
advanced the disposable target to [merge commit c10be8d](https://github.com/innercoder78/privacy-decoy-virtual-android/commit/c10be8d9a4341547d25bfd1a077cb9b381cdd4a5).
GitHub's commit object gives these parents in order:

1. `8226525bb8fc85126e8debeb9d844eec46dfa8c6`, the PR base and #89 result.
2. `cdba30ce138b0efb06e5f77370e96c1a33b6738f`, the original and final PR head.

The head was one commit directly on that base. Its only change appended 69 lines
to `docs/evidence/gate-0-companion-source-controls.md`, mode 100644 on both sides.
The PR had zero submitted GitHub reviews, comments or review threads. The
approved rule requires zero GitHub approvals.

The [pull_request workflow run](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44364422551)
completed successfully. Each required check run named the second parent as its
head SHA and GitHub Actions (app 15368) as its producer. Both checkout logs
recorded that exact commit. All listed job steps completed successfully.

| Required check | Execution on the tested head |
|---|---|
| [foundation](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44364422551/job/135014209282) | The log printed the checked-out HEAD, 152 repository tests, seven native wait controls and the expected assertion failure. The bootstrap, Linux worker lifetime, seccomp and revocation steps also completed. |
| [offline-image-windows](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44364422551/job/135014208847) | The Windows log recorded 45 offline-image, 4 frame-copy, 38 Gradle distribution and 16 installed-tools tests. |

#### Activation assessment after PR #91

| Condition | Classification | Evidence and scope |
|---|---|---|
| Exact configuration and applicability | PROVEN | [Ruleset 27524027](https://github.com/innercoder78/privacy-decoy-virtual-android/rules/27524027), version 58434939, was active before the merge. Its stored rules match the ADR with the disposable name and sole target ref substituted. Excludes and bypass actors are empty, caller bypass is `never`, and the target's effective endpoint returned all four matching rules from this ID. The sibling control had no effective rules. |
| Regular merge with current base | PROVEN | The two ordered parents match the original base and tested head. #88 and #89 used the earlier three-method configuration. #91 closes the positive regular-merge case for the singleton configuration. |
| Squash and rebase exclusion | PROVEN in stored and effective configuration; runtime refusals NOT RUN | Both readbacks allowed exactly `["merge"]`. The ADR retires qualification of the other merge paths. No runtime refusal is claimed or required as a separate method trial. |
| Required producer and exact SHA | PROVEN for #91; wrong producer and wrong SHA each UNKNOWN | Both contexts bind app 15368. Both jobs checked out and exercised the exact head. A green context alone cannot authenticate the workflow contents or prove execution on the resulting merge tree. |
| Missing checks | PARTIALLY SUPPORTED | Earlier GH013 named both missing checks and the missing PR. Isolated missing-check refusal remains UNKNOWN. |
| Failing and pending checks | PARTIALLY SUPPORTED for each | Earlier HTTP 405 responses named the failing Foundation job on #84 and the in-progress checks on #86. The check rule parameters persisted across the method change. |
| Strict base freshness | PROVEN in configuration; stale-refusal attribution INFERENCE | The strict flag is true. The old #85 head was behind with two green jobs. Its refusal named expected checks without identifying the stale-base condition. |
| Refreshed-head recovery | PARTIALLY SUPPORTED | The refreshed #85 head passed both jobs and merged in the earlier unauthorized exercise. #91 started current. A reviewed stale-to-refreshed sequence remains unobserved. |
| Cancelled, timed-out, skipped, neutral and zero-step jobs | NOT RUN for each; isolated outcomes UNKNOWN | Neither #91 job exercised any of these cases. Skipped and neutral conclusions can satisfy status semantics. The logs establish substantive execution for #91 only. |
| Direct update, force push and deletion | PARTIALLY SUPPORTED for each | The earlier GH013 receipts and unchanged refs document three refusals. Current effective rules retain the same restrictions. Those historical local receipts lack independent timestamp attestation. |
| Administrative recovery with the singleton setting | PARTIALLY SUPPORTED; exact cycle NOT RUN | History versions 58322128, 58322165 and 58322171 show active, disabled and active with three methods throughout. Version 58434939 changed the method array while active. #88 followed the earlier restore. #91 followed the method change. Neither supplies a merge after restoration of the singleton setting. |
| Independent observation and implementation limits | PARTIALLY SUPPORTED | GitHub exposes the merge object, per-version settings, job identities and substantive output. No separately controlled administrative recovery route or independent witness to the earlier local refusals is established. Empty bypass actors do not prevent an administrator editing the rule. |
| Production applicability | PROVEN at preflight | Main was `53fd5ff9df0de3210902cf20dbc825438df08645`. The listing including inherited rulesets returned only the disposable rule, effective main rules were empty, main reported `protected: false`, and the classic endpoint returned HTTP 404, “Branch not protected.” |

**Production activation remains BLOCKED.** The [approved ADR](../decisions/ADR-0005-interim-main-branch-protection.md)
points to this record for outstanding activation conditions. The outstanding
configuration-specific condition is verified recovery followed by a qualifying
regular merge under the restored singleton rule. The approved policy does not
make each unobserved status conclusion, isolated refusal, or independent GitHub
approval a separate activation test. The earlier unauthorized merges and failed
qualifications retain their recorded outcomes.

The minimum additional proof is a disposable recovery receipt under separate
authorization: capture the singleton rule, observe it disabled and absent from
the target's effective rules, then observe the same singleton body restored and
effective with the control ref still clear. Correlate that restoration with the
next authorized regular merge, its exact-head jobs and its ordered parents.
A changed method array, lost binding, unexpected scope or merge predating the
restore leaves the condition open. Existing #91 receipts already close ordinary
merge qualification. Production activation requires separate owner authorization.

Gate 0 remains Unresolved. Gates A-G remain Not reached. This evidence covers
repository governance only.

### Qualification after restoration

**A. TECHNICALLY READY FOR SEPARATE OWNER AUTHORIZATION.** PR #91 established
the regular merge under the merge-only rule. [PR #93](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/93)
merged into the disposable branch after GitHub recorded restoration of the
rule. GitHub records the merge time, ordered parents and check execution.
It shows zero submitted reviews,
comments or review threads on either PR. Production activation requires a
separate owner decision.

| Stored configuration | Independent GitHub ruleset history, UTC |
|---|---|
| PROVEN, initial | Version 58434939 was active before #91. |
| PROVEN, disabled | Version 58492991 at 00:26:53 on November 19 changed only enforcement in the stored state. |
| PROVEN, restored | Version 58493015 at 00:27:04 restored the initial state field for field. All three version bodies were retrieved for this assessment. |

**PROVEN, policy and current scope.** The stored [ruleset](https://github.com/innercoder78/privacy-decoy-virtual-android/rules/27524027)
matches the [ADR body](../decisions/ADR-0005-interim-main-branch-protection.md)
with only the name and sole included branch replaced. The four effective
rules on the target carry this ID and the same parameters. Exclusions and
bypass actors are empty. Caller bypass is `never`. A PR is required and
allows only regular merges. Required approvals are zero, required reviewers
are empty, and all five review flags are false. The two required contexts
are `foundation` and `offline-image-windows`, both from app 15368. Strict
freshness is enabled and `do_not_enforce_on_create` is false. Deletion and
non-fast-forward updates are restricted.

**PARTIALLY SUPPORTED, effective state during recovery.** The receipt committed
in #93 records four, zero and four effective rules across the three stages.
It records the disposable tip at the #91 result throughout, and the two
controls unchanged and unprotected at every stage. Those point-in-time
branch reads come from one administrative account. The historical version
bodies independently establish the stored settings. Current branch reads
confirm the endpoints after the merge.

**PROVEN, production and sibling controls at preflight.** The listing including
inherited rulesets returned only the disposable rule. The repository had zero
classic protection rules. Main at `c53676b009062df4140fb3107e16f3e1433e0cb1`
and sibling `codex/adr0005-ownerreview-test-20261118-pr1` at
`e57e5b044864c672d47493ed8307d58af0c3e157` each reported unprotected with
empty effective rules. The target alone reported protected. Classic protection
returned HTTP 404, “Branch not protected,” for all three branches.

**PROVEN, post-restoration regular merge and substantive execution.** GitHub
recorded #93 merged at 00:37:31 UTC on November 19. The disposable target
points to [fb0b070](https://github.com/innercoder78/privacy-decoy-virtual-android/commit/fb0b070b7e086eb83a3142738855e5d49e635e62).
Its ordered parents are the exact PR base and head:

1. `c10be8d9a4341547d25bfd1a077cb9b381cdd4a5`, the #91 merge result.
2. `e21a1795baf20e41c36d0c73379586f41b46b2ef`, one commit directly on that base.

The head and result have identical trees. The sole change appended 41 lines
to this evidence file, mode 100644 on both sides. Both check runs reported
success from Actions app 15368 on the second parent. Both checkout logs
identified that SHA. All listed job steps succeeded.

| Required check on #93 | Observed execution |
|---|---|
| [foundation](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44429571456/job/135243156656) | The log recorded 152 repository tests and the native positive and negative controls. The bootstrap, Linux worker lifetime, seccomp and revocation steps completed. |
| [offline-image-windows](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44429571456/job/135243156041) | The log recorded 45 offline-image, 4 frame-copy, 38 Gradle distribution and 16 installed-tools tests. |

The condition classifications in the #91 assessment continue to apply to
the earlier enforcement trials. Direct updates, force pushes, deletion,
missing, failed and pending checks, and refreshed-head recovery remain
PARTIALLY SUPPORTED. Attribution of the stale refusal to strict freshness
remains INFERENCE. Isolated missing-check, wrong-producer and wrong-SHA
outcomes remain UNKNOWN. Cancelled, timed-out, skipped, neutral, zero-step
and alternate-method refusal trials remain NOT RUN. The approved contract
requires the singleton method in stored and effective configuration. The
remaining unknowns are documented enforcement limits. None requires a
further disposable trial for activation under the approved ADR.

Changed paths determine whether the Android and QEMU workflows apply.
A workflow change can retain both the required check name and the producing
app. The checkout log identifies the tested commit, and test output shows
which checks ran. GitHub can accept skipped or neutral conclusions even when
no tests ran. Administrators retain settings authority even with an
empty bypass list. The historical unauthorized merges, fifteen signed-byte
failures and failed SDK-state qualification retain their original outcomes.
Gate 0 remains Unresolved. Gates A-G remain Not reached.

### Production activation on main

GitHub created [ruleset 27600511](https://github.com/innercoder78/privacy-decoy-virtual-android/rules/27600511)
active at 2026-11-19 01:25:23 UTC. The request body came directly from the
[approved ADR-0005 at the activation commit](https://github.com/innercoder78/privacy-decoy-virtual-android/blob/886ae75681a7c66ee0bc0b240c67d8e7134cfade/docs/decisions/ADR-0005-interim-main-branch-protection.md).
The remote main ref, fetched commit and branch API agreed on
`886ae75681a7c66ee0bc0b240c67d8e7134cfade`, the merge of #94.

**Direct observations.** Preflight found zero open PRs. Main reported
`protected: false`, with no effective rules. The listing including inherited
rulesets contained only 27524027. GitHub Status reported normal operation.
Both required checks on the main commit succeeded under GitHub Actions app
15368. The [Foundation log](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44432993043/job/135254766352)
identified the exact checkout, 152 repository tests and seven native positive
controls. The [Windows log](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/44432993043/job/135254766775)
identified the same checkout and suites of 45, 4, 38 and 16 tests.

Independent GETs of the stored rule, main's effective rules and the branch
returned the following results after creation.

| Readback | Observed result |
|---|---|
| Stored scope | `main-review-and-ci`, target `branch`, enforcement `active`. Sole include `refs/heads/main`, empty exclusions and bypass actors. Caller bypass was `never`. |
| Effective source | Exactly four rules, all from repository ruleset 27600511. Each rule and its parameters matched the stored configuration and the ADR. |
| Pull request | Only `merge` allowed. Required approvals 0, required reviewers empty. Stale-review dismissal, code-owner review, last-push approval, thread resolution and extra approval for unattributed changes all false. |
| Required checks | `foundation` and `offline-image-windows`, each with integration ID 15368. Strict freshness true, `do_not_enforce_on_create` false. |
| Ref restrictions | `non_fast_forward` and `deletion`, each without parameters. |
| Main | Branch GET returned `protected: true`. The remote SHA stayed at the #94 merge. Classic protection still returned HTTP 404, “Branch not protected.” The branch summary's classic status-check list was empty. The ruleset checks appeared in the effective rules endpoint. |
| Repository controls | Regular, squash and rebase merge options each remained enabled repository-wide. The listing including inherited rulesets contained exactly 27524027 and 27600511. |
| Disposable target | Ruleset 27524027 retained its complete stored configuration and update timestamp. Its sole target, `codex/adr0005-ownerreview-test-20261118`, retained all four effective rules from that ID alone. |
| Sibling control | `codex/adr0005-ownerreview-test-20261118-pr1` remained at `e57e5b044864c672d47493ed8307d58af0c3e157`, unprotected with zero effective rules. |

**Historical qualification.** The [restoration record](#qualification-after-restoration)
documents disposable enforcement trials. Preflight re-read versions 58434939,
58492991 and 58493015 (active, disabled, active), and confirmed the subsequent
#93 regular merge time and its two ordered parents. The authenticated repository
permission read showed administrative access. Future maintenance depends on
continued authorized settings access. A separately controlled recovery account
remains unverified.

**Inference and unknowns.** The readbacks establish the configured policy.
Production push, deletion, merge, refusal and recovery trials were unrun.
Runtime outcomes for those operations on main remain unknown. CI depends on
the workflow, checkout and actual job execution. A matching check name and app
alone cannot establish which tests ran. Administrators retain authority to edit
the ruleset. The historical limitations above still apply.

This activation concerns repository governance. Android feasibility, isolation
and VM security remain unverified. Gate 0 remains Unresolved. Gates A-G remain
Not reached.

### Disposable branch retirement

GitHub accepted the deletion of `codex/adr0005-ownerreview-test-20261118`
with an exact-ref lease on its original tip,
`fb0b070b7e086eb83a3142738855e5d49e635e62`. Before deletion, ruleset
27524027 applied only to this ref. Its enforcement changed from active to
disabled. A separate read confirmed all other settings matched, and the
branch reported unprotected with zero effective rules. The ruleset remains
available as a historical record.

After deletion, Git's remote head listing and GitHub's matching-refs API
both omitted the exact ref. Every other remote head retained its preflight
SHA, including the similarly named PR branch. GitHub listed zero open PRs.
These checks establish removal of the comparison source. The browser banner
was not inspected.

The [qualification record](#qualification-after-restoration) and
[production activation record](#production-activation-on-main) remain on
main. The disposable history adds eight commits beyond its common ancestor
with main. The heads and merge commits of PRs #88, #89, #91 and #93 account
for all eight. Their only changed file was this technical evidence document.
An independent restoration reproduced the original tip and its full reachable
object set, including the original commits, ordered parents and trees.
Git's strict object integrity check passed.

Main remained at `92fd3f52aab0804d19e2067ef1be2271baaa7a9b` and reported
protected after deletion. The complete stored response for active ruleset
27600511 matched preflight. All four effective rules matched ADR-0005:
regular-merge-only pull requests, required status checks, non-fast-forward
protection and deletion protection. Both `foundation` and
`offline-image-windows` required GitHub Actions integration 15368 and strict
freshness. The bypass list remained empty.

Production enforcement trials and Android and VM tests were unrun for this
retirement. The earlier qualification limits still apply. Gate 0 remains
Unresolved. Gates A-G remain Not reached.

## Android 17 security-branch lifecycle comparison

**NO NEW QUALIFYING AUTHORITY EVIDENCE.** On 2026-11-20, the Android 17 security
branch differed from the previously reviewed release in ActivityManagerService.
Its single changed line in that file affects creator tokens for nested intents.
It provides no completion receipt for an isolated worker. **Gate 0 Unresolved.
Gates A–G Not reached. Dependent implementation STOP.**

### Question and baseline

Can this framework change give an ordinary installed manager independent proof
of teardown after manager death, including descendants and retained authority?
PDVA main resolved remotely and after fetch to
`3ef791c33205eb58b323c5b539fc468f74eda2b5` (merged PR #96). The open PR list
was empty. GitHub Status reported All Systems Operational. The acceptance boundary
comes from [ADR-0004 Option A](../decisions/ADR-0004-gate-0-owner-disposition.md)
and the [roadmap](../roadmap.md). The earlier [platform authority](gate-0-platform-authority.md)
and [integrated decision](gate-0-integrated-feasibility-decision.md) delimit the
ordinary-app and complete-guest requirements.

### Reproducible source comparison

An exact-ref query against AOSP `platform/frameworks/base` returned
`android17-release` and peeled tag `android-17.0.0_r1` at the prior commit
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`. The separately named
`android17-security-release` resolved to `3433336c6477a3b33a6ccb880cd8b06d99139370`.
The comparison uses these two endpoints without assuming a particular OEM build
or patch level. The following Gitiles directory entries had identical Git blob
IDs at both immutable commits. The first three files are in
`services/core/java/com/android/server/am/`.

| File | Git blob at both revisions |
|---|---|
| ActiveServices.java | `32c6f6f031c86d02e75df7474af213ac451ea1df` |
| ProcessRecord.java | `da58696a735690bc9374436662a3a4f3d32762fd` |
| ProcessList.java | `d8e2cfaae0671d20740f11da8698eace47e925d4` |
| core/java/android/os/Process.java | `00dd71b722675356b923decfeb2db3085fab03b3` |
| core/api/current.txt | `572012ca464337b2c65ed83e68a711811d639e61` |

For the differing file, decode each Gitiles TEXT response, hash the bytes and
diff the complete source lines. SHA-256 was
`17923170a97fb001c3892ab4e0d71f9e249f9ea0b427a7aaf29916aae5208797` at release and
`d61d3962392cc4e3d8ffab66eb9c6782d988d2a030b3b53b1dbe48716d2d898b` at the security head.
At line 21101, when an intent lacks an explicit component, the security version
uses a null target for its same-creator comparison. Previously it used the intent's
package field. A package-only match therefore no longer skips creator-token
handling on that basis. Lines 21077–21120 place this decision inside the
flag-guarded handling of nested intents using the Binder caller UID.
[Release source](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActivityManagerService.java#21101)
and [security-branch source](https://android.googlesource.com/platform/frameworks/base/+/3433336c6477a3b33a6ccb880cd8b06d99139370/services/core/java/com/android/server/am/ActivityManagerService.java#21101).

### Ordinary-app authority and decision

An ordinary app can bind its own non-exported isolated service without a special
grant. The manager retains its app UID and app domain. The worker has a distinct
isolated UID and domain. The changed code runs in system_server and uses caller
identity to attribute an intent. It grants the caller no signal or cgroup
permission, SELinux transition, ownership of the worker's descendants, or Binder
operation for joining cleanup. In the identical ProcessList source, lines 799–810
discard the group-kill result and lines 1689–1699 schedule the operation.
[Security-branch ProcessList](https://android.googlesource.com/platform/frameworks/base/+/3433336c6477a3b33a6ccb880cd8b06d99139370/services/core/java/com/android/server/am/ProcessList.java#799).

After manager death, the changed method neither enumerates surviving processes
nor revokes a retained descriptor, mapping or delegated handle. Whether a given
holder survives on a device remains unmeasured. Unbind, Binder death and process
exit history still supply no independent observation that every holder lost access.
Restart, crash, restore or loss of manager state supplies no fresh enrollment or
authenticated result for the prior worker. The prior
[lifetime trace](gate-0-android-lifetime-authority.md),
[lifecycle exceptions](gate-0-android-lifecycle-exceptions.md),
[revocation](gate-0-capability-revocation.md),
[restore](gate-0-managed-restore-lifetime.md) and
[process history](gate-0-process-history-reconciliation.md) records give the
underlying counterexamples.

**Falsifier.** A completion claim fails if a surviving holder can still use a
previously delegated descriptor after the enforcer reports that the old worker
and its authority are gone. Loss of the observer leaves completion Unknown.
This delta exposes no such result to test. Reopening requires a concrete
ordinary-app-accessible independent enforcer that accounts for descendants and
retained grants across manager loss and can establish a trustworthy fresh boundary.

Only the named framework sources and API signature were compared. Kernel,
SELinux, other framework files, OEM correspondence and device behavior were
outside this comparison. No upstream code was adopted and no Android, native
worker or VM experiment was run. This scoped negative justifies no follow-up
execution or change to the accepted decision.

## Android 17 SELinux worker cleanup authority

Does the Android 17 security release give an ordinary installed app on a stock,
nonrooted user build a new way to enforce and verify isolated-worker cleanup?
This comparison covers the SELinux source excluded from the preceding framework
record. Both annotated tags resolved in AOSP `platform/system/sepolicy`.

| Release tag | Peeled commit | Root tree |
|---|---|---|
| `android-17.0.0_r1` | [`e066568e98d86db31a9346d30977f3632fa7073c`](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/) | `f0e857a84958d5472dee9187c54f7b4f191a415a` |
| `android-security-17.0.0_r3` | [`895c7f4dcaa61fbe3155c0c273db63cbda9cd1ac`](https://android.googlesource.com/platform/system/sepolicy/+/895c7f4dcaa61fbe3155c0c273db63cbda9cd1ac/) | `0461cbd56064556d0091ec76f062c59083244fb3` |

Resolve the tags with `git ls-remote`, fetch both, then run
`git diff-tree -r --no-renames --no-abbrev <release> <security>` without a path
filter. Inspect the full patch for every changed blob. The tree comparison found
exactly three modified paths, all mode 100644 on both sides. Each lost the rule
`allow SUBJECT block_device:dir search;`. The table supplies the literal subject
and the before/after Git blob IDs. Each retained its adjacent read permission for
`apex_dm_device:blk_file`. Only the system_app hunk also replaced a two-line
comment about parent-directory search and device reads with a one-line comment
about device-mapped block files.

| Changed path | Subject and authority class | Release blob | Security blob |
|---|---|---|---|
| `private/crosvm.te` | `crosvm_domain`, VM monitor domains | `7e8006850114d97eea6ba4da49f565889b33afb2` | `a9d90ed20f4010e04b6339c50d05c71687b96bb8` |
| `private/priv_app_all.te` | `priv_app_all`, privileged app domains | `49cbc8fc1e0858b19e8e9bee1ccc39cf38db0f03` | `cf4b0e6085f501dd63a750238cfc430bf23a54d4` |
| `private/system_app.te` | `system_app`, system app domain | `00a41baaf53d7a47c83fa9018555d9b3352bc90a` | `d78a59c0908ffedbd261bde8951ea4c5bf24a206` |

**Falsifying observation for each row.** The only executable policy edit in
each blob deletes a directory-search allow for the named subject. None adds an
operation, changes domain membership or identifies a process or retained grant.
Whether another rule supplies equivalent directory access on a particular build
is Unknown.

The ordinary manager and its worker keep distinct domain assignments.
`private/seapp_contexts` maps the ordinary target-SDK 37 app to `untrusted_app`
and the ordinary isolated service to `isolated_app`. Its older target-SDK
mappings also retain identical bytes. `private/isolated_app.te` still applies
`app_domain` and `isolated_app_domain`. The signal neverallow in
`private/app.te` still restricts signals from app domains to the specified
non-app domains, with explicit exclusions. Its target set does not decide
app-to-isolated-worker signaling. The same file retains its procfs restrictions
for non-app process entries. The explicit `getpgid sigkill signal` allow on
`appdomain:process` in `private/system_server.te` still names system_server as
caller. The tree and hunk comparison found no change to process signals, cgroup
control, procfs, pidfd, process observation or relevant neverallows, and no new
enforcement grant even to system_server.
[Domain mappings](https://android.googlesource.com/platform/system/sepolicy/+/895c7f4dcaa61fbe3155c0c273db63cbda9cd1ac/private/seapp_contexts#183),
[app restrictions](https://android.googlesource.com/platform/system/sepolicy/+/895c7f4dcaa61fbe3155c0c273db63cbda9cd1ac/private/app.te#654),
[system-server signal rule](https://android.googlesource.com/platform/system/sepolicy/+/895c7f4dcaa61fbe3155c0c273db63cbda9cd1ac/private/system_server.te#198).

**NO NEW QUALIFYING AUTHORITY EVIDENCE.** A permitted signal or a framework
group-kill request gives the manager no new observation that every descendant
exited. None of the changes establishes that every holder lost a retained FD,
mapping or delegated handle. None returns an independent completion result
that a restarted manager can authenticate after losing its prior state. A
surviving descendant or holder after reported success would falsify a cleanup
claim. A result available only to a privileged caller, or recoverable only
from lost manager state, also fails the ordinary-app criterion.

No Gate 0 blocker moves. ADR-0004 Option A remains accepted, Gate 0 Unresolved,
Gates A–G Not reached, and physical testing **NOT READY — STOP**. Effective
policy on a particular production build and runtime behavior remain Unknown.
No policy compilation, APK, emulator, VM, physical-device test or Linux lifetime
experiment was run. This source comparison establishes neither guest feasibility
nor universal impossibility. No further investigation of this snapshot is
justified without a concrete new falsifier involving an ordinary-app-accessible
enforcer that covers descendants and retained grants across manager loss.

## Disposable SDK copy and source immutability

At `9f610ffc5e9e56faff129ae625405ac2658e7cfe`, can a same-account
filesystem copy plus full source scans before and after copying establish an
immutable SDK input for the Java diagnostic? **Failed on a synthetic Windows
fixture.** The existing scanner observes points in time. The bootstrap's file
checks and Gradle dependency verification supply no write boundary around the
original SDK for the duration of copying or execution.

Two disposable trials used the existing `sdk_capture` and `sdk_scan`, two
synthetic package roots with regular `package.xml` files, an empty licenses
directory, and Python `shutil.copytree` into a previously absent sibling.

1. Both copied files matched their originals and had different file identities.
   A write in the copy left the full source inventory equal. Creating a file
   under source licenses made the inventories differ. Removing that fixture
   file made them equal again. The copying account had write access throughout.
2. Capture the source inventory and the platform package.xml timestamps. Write
   the seven bytes `changed` over `fixture`; the live inventory differs. Copy
   the entire tree, then put back `fixture` and set the original access and
   modification timestamps with `os.utime(ns=...)`. The final full source
   inventory equaled the initial one, while the copy retained `changed`.
   Comparing copied file digests to the initial capture would catch this copy
   mismatch. It would still leave the transient source write in trial 1
   undetected by endpoint comparisons.

**Decision.** Reject this implementation for build validation. Every entry,
including generated state, stays in its respective full inventory. A subsequent
discovery operation consumes existing generated state as input and needs evidence
binding that exact state to the preceding operation. These trials did not run
discovery, test redirection defenses, exercise output freshness or establish
independent provenance. No installed SDK, Gradle build, APK or device was used.
PR #77's unsigned-byte equality passed and its complete SDK assertion failed.

**Next proof.** Before any build, use an independently administered immutable
source snapshot with authenticated inventory. Under the actual disposable worker
identity, demonstrate denied write, create, rename, delete and metadata changes
through every accessible source path, including redirected paths. Verify the
fresh copy against that inventory before use, including package metadata and
empty directories. Record source and copy identities separately. Each later
operation still needs its complete input state, fresh outputs and exact admitted
source and packaging correspondence. A synthetic copy supplies no Windows
incident resolution, signing custody, signed-byte reproducibility, independent
evidence preservation or device authorization. Gate 0 remains Unresolved and
Gates A-G remain Not reached.

## One-attempt Java diagnostic policy

**Draft for ADR-0006 · PROPOSED · NOT APPROVED · 2026-11-23.** ADR-0006 is
unregistered. The next number is available, but adding the decision file
triggered `protected-governance` in the source-admission test. Formal registration
requires separate owner authorization for a reviewed change admitting that
exact decision path and text, its validation, and any hosted operations the
change would trigger. That transition is outside this proposal. Publication,
merge and registration each confer no operational approval.

### Decision and scope

Recommend allowing the owner to rely on one inspected development artifact for
one observation of mapping admission. Independent reproduction adds assurance
against a compromised or divergent build. Its cost is disproportionate here
only if the owner accepts that missing assurance and every control below holds.
The alternative is to retain the existing qualification contract and STOP.

Bind the exception to commit `b84af1c7764298b06bc8b356c38b3ef9fd8f0db3`,
tree `0dfc367c4c87defe7d468946bf3e7cf477cc0282`, and one privately designated
compatible stock Android 17 device. The [module](../../android/memory-diagnostic/build.gradle)
defines only the enabled release of `org.pdva.memorydiagnostic`, version 1
(`0.1-diagnostic`), compile/min/target 37, non-debuggable, with no configured
signer or runtime dependency. Its companion-only APK metadata exclusion is
already in source. The [manifest](../../android/memory-diagnostic/src/main/AndroidManifest.xml)
declares one launcher and zero permissions.

In the [Java implementation](../../android/memory-diagnostic/src/main/java/org/pdva/memorydiagnostic/Experiment.java),
one user press disables the button and requires a successful synchronous
preference commit before allocation. One memfd backs one 4 or 16 KiB page with
separate shared RW and RX views. No RWX view, access to mapping contents,
network operation, JNI, payload, subprocess or guest execution occurs in source.
RX and RW unmapping and descriptor close are attempted independently for acquired
resources. Unexpected faults and incomplete cleanup yield Unknown. There is no
automatic retry. Durability assumes intact app data.

### Which obligations would change

Under [ADR-0003](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md)
the companion's preparation scope still requires independent administration,
full toolchain qualification, qualified signing custody and two independently
built complete signed originals with identical bytes. The table identifies the
three proposed exceptions and the evidence the owner would provide for this attempt.

| Existing requirement proposed for exception | Evidence the owner would still have to produce |
|---|---|
| Independently administered build and independent qualification of the complete toolchain | Identify the fresh worker and exact inputs, verify available authenticated pins, document provenance gaps and demonstrate the SDK write boundary in step 2. |
| Independently qualified signing custody and independent artifact verifier | Keep the dedicated key privately, demonstrate custody and recovery, and verify the signer, signature, tamper rejection and delivered bytes in steps 3 and 4. |
| Two independently built complete signed originals with identical bytes | Trace one original from the reviewed tree to the installed candidate. The second build and signed-byte equality remain unproven. |

Record each exception as **proposed** until explicitly adopted, then as
**waived for this attempt / unproven**. Policy review evaluates those tradeoffs.
It supplies neither independent build evidence nor security certification.
Preserve all fifteen historical signed-byte failures, the failed complete SDK assertion and every
negative receipt. Any observed new mismatch is a failure and stops the attempt.
No normalized comparison, comparator change or substitution of an unsigned pass.

This is a limited disposition of the development-tool adoption evidence under
PDVA-REQ-036 and the companion qualification packet. Rights, provenance
accounting, source controls, independent policy review, private preservation
and truthful reporting under PDVA-REQ-008, PDVA-REQ-039 through PDVA-REQ-041
and PDVA-REQ-051 remain mandatory. Production host Option A retains metadata
and strict signed-byte equality. [ADR-0004 Option A](../decisions/ADR-0004-gate-0-owner-disposition.md)
retains the complete interactive Android 17 virtual phone in an ordinary
user-installed app on a stock nonrooted host. All production isolation,
provenance, signing and distribution requirements and the native harness lock
remain mandatory. No other variant, device, recipient, release, guest or
follow-on attempt qualifies. Gate 0 remains **Unresolved**. Gates A-G remain
**Not reached**.

### Authorization and evidence, in order

1. **Owner decision after independent review.** YES means “I accept the
   listed residual risks and authorize only an offline, read-only assessment
   of the proposed build inputs and custody plan for this exact source.”
   NO means “Retain current qualification and STOP.” Record the dated decision,
   reviewed proposal revision, scope and deadline privately, with a technical
   disposition in the decision register before implementation. Silence, an open
   PR, a merge or a passing check supplies no authority to build or test.
2. **Before a build.** Verify the clean source and tree, applicable real checks,
   exact-ref source admission and RWX/permission negative controls. Record tool
   versions, origin, available authenticated hashes, rights and unresolved trust
   assumptions for OS, JDK, SDK 37, Build Tools 36.0.0, Gradle, AGP, full
   dependency closure, packager, signer and verifier. Retain strict dependency
   verification. Exclude the unresolved incident environment and its caches,
   keys and tools. The owner may administer a fresh worker under the proposed
   exception. Under its actual build identity, demonstrate that the authenticated
   SDK snapshot rejects writes, creation, rename, deletion and metadata changes
   through every accessible path. Match the disposable copy to the full inventory
   and bind generated state between operations. Endpoint scans failed to prove
   immutability. Verify a restore from a separate encrypted private backup.
   **First build remains blocked.** The policy decision and formal registration
   are outstanding. This proposal supplies no incident-separated worker or input
   receipts, SDK write-denial proof, backup restore receipt, or build authorization.
   The owner must record the evidence above, resolve discrepancies, and expressly
   authorize one unsigned release build against that exact source and input set.
3. **Before signing.** Bind the original unsigned digest and fresh output to
   that build. Require passing desktop behavior/cleanup tests, release lint,
   and inspection of the entire merged and packaged manifest, DEX, resources,
   components and archive inventory. Match the reviewed launcher, SDK/version,
   extraction exclusions and non-debuggable flags. Reject added permissions,
   networking, code, components, dependencies, native libraries, assets or
   unexpected metadata. Record build limitations. Require explicit approval of
   the unsigned digest, method and diagnostic-only key operation. Use a fresh
   protected private key with owner-only access, encrypted storage and recovery,
   separate from debug, host and production identities. Keep secrets offline
   from public infrastructure. Sign privately outside the unchanged module.
4. **Before transfer or installation.** Verify the original signed APK using
   pinned signature tools, expected certificate and approved signing schemes.
   Require rejection of a tampered disposable copy and account for every
   difference from the inspected unsigned archive by the signing operation.
   Reinspect the final package and bind its whole-file SHA-256 to the source,
   inputs, unsigned digest and signer. Privately verify stock nonrooted production
   user configuration, exact API 37, ARM64 support, 64-bit app-process support,
   supported page size, ordinary installer access and no previous attempt or
   ambiguous installation history. An Android version alone is insufficient.
   Obtain explicit authorization naming the final digest, signer, private route,
   single recipient, designated device and shorter execution window. Compare
   whole-file digest at receipt before normal installation. Any mismatch,
   protection warning requiring bypass, or unverifiable prerequisite means STOP.
5. **Before pressing.** Confirm authorization is current, identity and installer
   receipts match, the ordinary launcher shows Ready, and the owner has explicitly
   authorized one press for this artifact in this window. Leave platform and OEM
   protections active. The app rechecks API, ABI, actual process bitness and
   page size before allocation. Consume the private authorization on first press,
   including denial, interruption or lost output. Never clear data or reinstall
   to recover an attempt.
6. **Close and withdraw.** Privately transcribe only the outcome, operation,
   bounded errno and corresponding cleanup fields. Accept a positive observation
   only for Admitted with Complete cleanup. Preserve Unsupported, Denied or
   ResourceFailure as observed. Interruption, unresponsiveness, inconsistent
   results or uncertain cleanup mean Unknown and STOP. Record uncertainty even
   if normal uninstall succeeds. Restore the original per-source installer
   permission, verify removal, retire delivery copies and disable further key use.
   Keep originals, failures, authorizations and cleanup receipts encrypted with
   access limited to authorized custodians. Before any build agree a retention
   deadline, verified backup, deletion owner and withdrawal procedure. At expiry
   revoke access and document authorized disposal or unresolved cleanup.

**Residual risk accepted only on YES.** One administrator and one build can
produce and sign the same unintended bytes. Hashes and signature checks detect
substitution but cannot prove benign tools, complete source correspondence or
freedom from key compromise. The owner bears custody, withdrawal and recovery
responsibility. Framework or kernel faults, a blocked synchronous call, state
loss and loss of the displayed result remain possible. A successful attempt
establishes only the bounded observation on that device. Hostile-worker
containment and full-guest feasibility require their own evidence.

**Separate proposed term.** Start only on dated explicit acceptance. End at the
earliest of first press, withdrawal by owner or reviewer, failed mandatory check,
unexpected behavior, loss of custody, change of source/tools/artifact/device/
recipient, or 00:00 on 2026-12-08 in America/Fortaleza. Closure obligations
survive termination. The earlier companion-only Option B ends under its own
terms no later than December 8, 2026 in America/Fortaleza. No renewal, inherited
authority or later signing/install/press permission follows from either term.

Technical provenance is the exact source above, the
[existing diagnostic qualification packet](gate-0-java-memory-diagnostic.md),
the [failed equality record](gate-0-apk-reproducibility.md), and the SDK copy
falsifier immediately above. These are repository observations and retained
evidence. All proposed artifact and device checks are prospective.

## ADR-0006 build worker assessment

**Inference — STOP before the SDK experiment.** On 2026-11-23 the available
Windows session supplied no identifiable fresh worker with a known build
identity and evidence excluding the incident host's tools, caches and keys.

**Fact/Source — source and controls.** Remote main, fetched main and the
evidence checkout agreed at `02b8545af3415cb99af0af0e9c90a5c3ae5f75b9`.
[ADR-0006](../decisions/ADR-0006-one-attempt-java-memory-diagnostic.md)
binds the diagnostic to `b84af1c7764298b06bc8b356c38b3ef9fd8f0db3`.
Git resolved its tree to `0dfc367c4c87defe7d468946bf3e7cf477cc0282`.
The Android subtree had no diff against main. Both main workflows succeeded.
There were zero open PRs at preflight. Effective main rules required a PR,
strict foundation and offline-image-windows checks, and blocked deletion and
non-fast-forward updates. The classic protection endpoint returned 404.

**Runtime Observation — source admission.** The registered checker with
`--check-source-ref` rejected the ADR-bound pre-registration commit with
`exact-diagnostic-adr`. The same checker accepted the fetched registration
commit. The former lacks the registered ADR. Identical Android files do not
resolve the choice of an authorized full build tree. Preserve both outcomes
for owner disposition before any build. Foundation validation passed under the
worktree owner after Git rejected cross-account access to the evidence checkout.

**Runtime Observation — desktop.** A token inspection identified a local
offline sandbox account at medium integrity, with no Administrators group in
the reported token. Executable lookup resolved Java in the host installation.
The JDK release file reported Eclipse Adoptium 17.0.21. Installed SDK package
properties reported platform API 37.0 revision 2 and Build Tools 36.0.0.
Neither SDK environment variable selected an installation in this process.
No standalone Gradle command resolved. The host compute service was stopped,
and the process query returned no matching running VM worker. Private evidence
and archive directory names were visible. Their contents were left untouched.

**Unknown — worker and inputs.** No prospective Gradle launcher, build token,
provisioning record or cache isolation was identified. The observed shell can
read host tools on the desktop associated with the [unresolved Windows incident](gate-0-native-host-antivirus.md).
A different account name or checkout cannot establish exclusion of affected
state. The service and process checks cannot rule out an offline or remote worker.

**Fact/Source — tool identity.** The bootstrap pins Gradle 9.6.0 and its
distribution digest. The project pins AGP 9.4.0 and carries strict dependency
verification metadata. [Earlier installation checks](gate-0-installed-jdk-sdk-integrity.md)
and [diagnostic checks](gate-0-java-memory-diagnostic.md) cover specific
installations and executions. **Unknown:** authenticated OS, JDK, full SDK,
packager, verifier and complete dependency/cache correspondence on a fresh
worker. Package labels and a locally generated inventory cannot authenticate it.

**Runtime Observation — controls withheld.** No SDK copy, ACL change, alias
or write probe, backup restore, local build, signing or device operation ran.
**Unknown:** denial of content writes, creation, rename, deletion and metadata
changes by the actual build identity across every accessible path. Full
disposable-copy correspondence and separation of generated state are also
unverified. Any successful mutation of the protected fixture would falsify
enforcement. An unexamined alias or failed writable control would leave it
unknown. Neither endpoint hashes nor Android app permissions test Windows
access control. The [prior SDK experiment](gate-0-companion-source-controls.md)
already records the failed SDK-state assertion.

**Unknown — custody.** No verified restore from a separate encrypted backup
or agreed retention deadline, deletion owner and withdrawal procedure was
established for this attempt. Directory presence proves only their existence.

**Inference — next operation.** The owner must first designate one existing
candidate worker and explicitly authorize an offline, read-only inspection
of its provisioning record, intended Gradle identity, mounted inputs and cache
origins. Evidence of shared incident tools, keys or caches rejects that
candidate. Without such a worker the first unsigned build remains blocked.
Any later fixture probe and the build each require separate authority.

## PROPOSED decision on the first unsigned diagnostic build

**Recommendation for ADR-0007.** Retain the ADR-0006 worker and SDK requirements
(Path A). Amend only the source-identity clause as specified below. Path B would
accept an unknown build environment for an APK destined for a personal phone.
The available checks cannot establish enough about that APK to recommend B.
The first unsigned build remains blocked. This assessment, its publication,
successful checks and merge confer no authority. A material evidence-gate
change requires independent policy review, explicit owner approval and separate
registration under [project governance](../governance.md).

### Which source would be eligible?

| Identity | Proposed binding and acceptance test |
| --- | --- |
| Reviewed application | Preserve ADR-0006 commit `b84af1c7764298b06bc8b356c38b3ef9fd8f0db3`, full tree `0dfc367c4c87defe7d468946bf3e7cf477cc0282`, as the source of the approved bytes. Only the Java 17 release of `org.pdva.memorydiagnostic`, version code 1, version name `0.1-diagnostic`, min/target/compile API 37, is in scope. |
| Registered checkout | Approve exactly commit `381ab85afacde557346a80b887841e7f49eef05c`, tree `192748380b2c14ec2f24bb42d1e40410a03bc2db`, as the sole prospective build checkout. Both commits contain the same entire `android/` tree `a844105b1373ef121401718e1c5d08cf1d6ca3ce`. The complete delta modifies the source checker, adds ADR-0006, and updates this companion document and the evidence index. All four paths are regular files. Review those exact blobs and modes. Exclude every later commit, including the proposal and any registration commit. |
| Admission | The registered checker rejects the older full tree at `exact-diagnostic-adr` because registration came later. Preserve that rejection. Require the unchanged registered checker to admit the exact proposed checkout. Passing that check cannot select a build ref or approve an exception. |
| Actual build and output | Before invocation verify the clean exported inputs against the pinned tree, including modes, absence of overlays, untracked inputs and ambient build configuration. Privately bind the actual launcher identity, tool and dependency inventory, command, variant and fresh output to that checkout. Afterward retain the original unsigned bytes and whole-file digest. A Git tree identifies neither the executed tools nor the resulting APK. |

### Cost and consequence of the two paths

**Path A.** The owner needs one freshly provisioned worker with an evidenced
boundary from the unresolved incident. This could be an existing separate
machine with verifiable history. If none is available, the owner would have to
provide separate hardware, storage for protected inputs and writable scratch,
and separate encrypted backup capacity. A VM on the incident host supplies
no such separation by itself. No suitable machine, purchase price, license
fee or time estimate is established. The concrete administration cost is a fresh
OS and restricted build account, provisioning JDK 17, SDK 37, Build Tools
36.0.0, Gradle 9.6.0, AGP 9.4.0 and the strict dependency closure from recorded
origins, verifying available authenticated digests and rights, and excluding
incident tools, credentials and caches. Keep a protected SDK master under a
different administrative identity. Expose only read-only SDK inputs to Gradle
and direct generated state to separately inventoried writable storage. The
owner must document and verify that arrangement and restore the private backup.

**Path B, evaluated and declined.** Waiving incident separation, a known
execution identity and proven SDK immutability would also leave exact input
correspondence during execution unknown. A compromised compiler or packager
could replace a method body, inject a component or add permissions. A compromised
inspector could report the expected inventory for different bytes. Even with
the reviewed manifest and no network permission, substituted code could act
at launch, abuse accessible platform interfaces, corrupt the result or trigger
a framework or kernel flaw on the personal phone. A signer exposed to the
worker could leak its key or sign a substituted file. A dedicated key limits
reuse across projects but cannot make malicious code safe.

The repository supplies pinned Gradle and AGP versions, strict dependency
metadata, source and negative controls, and package inspection logic. They
address specific errors. Hashes can detect a changed file after binding;
successful CI, class names and a clean packaged manifest cannot authenticate
the tool that emitted or inspected a method body. A verifier outside the
suspect environment, reviewed DEX behavior, an isolated signer and authenticated
private delivery would reduce specific risks. Their availability and custody
for this candidate are unverified. Even all four would leave a single build
without independent signed-byte correspondence. There is no defensible
environment waiver on the present evidence. If A cannot be provisioned, STOP.

### Owner decision and order of operations

1. **YES** means approve only the two exact source bindings above for this one
   release, retain all ADR-0006 build conditions, and record the dated decision
   against this reviewed revision after independent policy review. **NO** means
   retain the existing source contract and STOP. Registration needs separate
   authority. Neither answer authorizes a build. The next preparatory action
   on YES is to designate one candidate worker and authorize read-only review
   of its provisioning, actual Gradle identity, mounted inputs and cache origins.
2. Require evidence excluding incident state. Only on a genuinely new boundary
   and separate fixture authorization, demonstrate under the actual build token
   denial of writes, creation, rename, deletion and metadata changes on every
   accessible SDK path, with a working writable control. Verify complete input
   correspondence and account for generated state between operations. Shared
   suspect inputs, an unexamined alias, a successful mutation or an unexplained
   difference stops qualification. Preserve the prior failed SDK assertion and
   all fifteen historical signed-byte failures. Do not repeat same-account probes.
3. Before a build require passing exact-ref admission, applicable checks and
   RWX/permission negatives, complete input receipts and a verified restore
   from a separate encrypted private backup. Agree the retention deadline,
   deletion owner and withdrawal procedure. Then obtain separate owner authority
   for one unsigned release build naming the exact checkout, inputs and worker.
   No such worker, recovery receipt or build authority is established here.
4. Before separate signing approval, require passing desktop behavior/cleanup
   tests and release lint. Inspect the merged and packaged manifests, DEX code,
   resources and full archive against the reviewed source. Require the single
   launcher, zero permissions, expected extraction rules and release flags.
   Reject unexplained code, components, libraries, assets or metadata. Bind the
   approved unsigned digest to one fresh, owner-controlled diagnostic-only key,
   with private encrypted recovery and no build-worker access to key material.
5. Verify expected certificate and schemes, account for signing-only changes,
   reinspect the final APK and require rejection of a tampered copy. Obtain
   separate transfer approval for its whole-file digest and one private
   recipient. Match the received bytes before separate installation approval
   for one privately designated compatible stock Android 17 device. Require
   the ADR-0006 compatibility and prior-attempt checks and ordinary installation
   with protections active. One further explicit authorization permits one press.
6. Terminate at first press, withdrawal by owner or reviewer, failed mandatory
   check, unexpected behavior, loss of custody, source/tool/artifact/device/
   recipient change, or **00:00 on 2026-12-08 in America/Fortaleza**, whichever
   comes first. Companion-only Option B retains its own earlier stops.
   Interruption consumes the attempt. Follow ADR-0006 closure even after
   termination, including removal, installer-setting restoration, key retirement
   and private evidence retention and disposal. Uncertain cleanup means Unknown.

ADR-0006's three existing concessions remain recorded as unproven. Production
isolation, signing, provenance, supply chain and distribution retain their full
requirements. ADR-0004 Option A still requires the complete interactive Android
17 virtual phone inside an ordinary stock nonrooted user-installed app. The
native harness stays execution-locked. Even Admitted with Complete cleanup
establishes only bounded memory mapping. Gate 0 remains **Unresolved** and
Gates A-G remain **Not reached**.

## Owner disposition on diagnostic source identity

On 2026-11-23 the owner approved both exact identities in the proposal above
and separately authorized registration and ordinary hosted CI.
[ADR-0007](../decisions/ADR-0007-diagnostic-source-binding.md) records the
decision and its expiry. The first unsigned build remains STOP pending the
separate worker, evidence, recovery and authorization specified above.

Local source-only validation replayed the immutable ADR-0006 checker. It
admitted the exact prospective checkout and rejected the reviewed application
commit at `exact-diagnostic-adr`. The registration checker requires the exact
ADR-0007 path, text and regular mode. Its separate `--check-prospective-checkout`
check pins the commit, full tree and Android subtree. Foundation and local
Markdown link validation, harness manifest validation, historical source audits,
diagnostic negatives and detector-removal checks passed. Repository validation
ran 152 tests with four Windows skips. No worker qualification or physical
candidate build ran. Hosted results are outside this local evidence.

## Diagnostic worker availability

On 2026-11-23 the owner reported that no suitable computer or separately
provisioned environment was available for inspection. **STOP before the first
unsigned diagnostic build.** This finding concerns the one-attempt diagnostic.
Gate 0 remains **Unresolved** and Gates A-G remain **Not reached**.

No worker was inspected or provisioned. Incident separation, the account that
would actually run Gradle, denial of writes to original SDK inputs, the location
of writable generated files, authenticated tool inputs and recovery from a
separate encrypted private backup all remain unverified. No write probe,
restore, build, signing, transfer, installation or phone operation ran.
The fifteen historical signed-byte failures and failed SDK-state assertion
retain their recorded outcomes. The native harness remains execution-locked.

Reopen worker assessment only if the owner designates a candidate and authorizes
a read-only review before the exception ends. Start with its setup history and
whether it shares tools, caches, keys or credentials with the affected system.
Shared incident state or an unexplained source of build inputs blocks qualification.
Keep supporting records in private owner custody. ADR-0006 and ADR-0007 retain
their earlier termination conditions and the deadline of 00:00 on 2026-12-08
in America/Fortaleza.
