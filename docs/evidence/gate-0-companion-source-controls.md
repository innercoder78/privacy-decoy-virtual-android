# Companion diagnostic source controls

**Current update:** the [authorized implementation and unsigned packaging evidence](#active-option-b-and-unsigned-packaging--2026-11-10)
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
publication**. Publish one PR, attach it natively to the originating chat, verify
association once, then STOP without polling CI/reviews/comments/bots/badges or
mergeability. No APK, raw log, private path, receipt or signing material is public.

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

Publish exactly one PR, attach to the originating Codex chat, verify that association
once, then stop without polling new-head CI, reviews, comments, bots, badges or
mergeability. New-head CI is **UNOBSERVED at publication**. All fifteen historical
signed-byte failures remain failures. ADR-0003 expires no later than **2026-12-08**,
subject to earlier termination. **Gate 0 Unresolved; Gates A–G Not reached; physical
testing NOT READY. Independent backup UNVERIFIED; private evidence UNPRESERVED.**
