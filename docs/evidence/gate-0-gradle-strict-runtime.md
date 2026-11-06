# Real offline Gradle STRICT enforcement experiment

Date: **2026-11-06, America/Fortaleza**. Base main:
`b52b3af22b3d3323f02df2ce0ea6b083e43809c9` (merged PR #63).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**
Traceability: PDVA-REQ-010, 036–042, 048, 051, 054.

## Objective and bounded execution route

Test real Gradle 9.6.0 property-file precedence and dependency checksum rejection,
beyond [PR #63's mocked launch controls](gate-0-gradle-strict-precedence.md).
The [dedicated runner](../../.github/scripts/test-gradle-strict-runtime.py) uses
the existing Linux [Android workflow](../../.github/workflows/android-harness.yml),
after its unchanged build step installed the pinned Gradle distribution. It only
validates the existing ZIP and installed tree with PR #59's implementation; it
does not call download/extraction/preparation or change installed files.

The branch-specific push trigger permits one pre-PR experiment on
`codex/verify-gradle-strict-runtime`. Existing main and PR coverage remains, with
the runtime step mandatory wherever this workflow applies. Foundation does not
gain Gradle/Android execution; QEMU workflow paths do not match. Failure propagates
normally, with no optional check, skip-success conversion, upload or merge-rule
change. The existing 25-minute job bound remains; the fixture step has a 12-minute
bound and each invocation a 90-second process-group timeout. No automatic retry.

This narrowly authorized hosted experiment is not independent build-environment
qualification. The preexisting workflow's ordinary build/package checks remain;
no new signing operation, Java-only diagnostic app, signed-APK pair experiment,
native research route, device, USB, ADB, VM or guest execution is added.

## Exact source expectations

Gradle **9.6.0**, revision `3f750f03d77e42327c5f9fcb9992110088330a32`:

- [LayoutToPropertiesConverter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/LayoutToPropertiesConverter.java)
  loads recognized installation, project and user-home properties.
- [BuildOptionBackedConverter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/BuildOptionBackedConverter.java)
  applies properties before CLI, and
  [EnumBuildOption](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/build-option/src/main/java/org/gradle/internal/buildoption/EnumBuildOption.java)
  applies a present CLI selection to the same target.
- [ChecksumAndSignatureVerificationOverride](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/verification/ChecksumAndSignatureVerificationOverride.java)
  throws `DependencyVerificationException` for fatal STRICT verification failures;
  LENIENT logs and clears them.
- [DependencyVerifier](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/verification/verifier/DependencyVerifier.java)
  compares the recorded artifact checksum against computed bytes.
  [HTML report renderer](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/verification/report/HtmlDependencyVerificationReportRenderer.java)
  renders the expected and actual checksum for that failure.

These immutable sources were retrieved through the GitHub connector. They support
the expected behavior; they do not establish binary/source correspondence.

## Procedure and falsifiers

The runner generates a deterministic resource-only JAR with a manifest and invented
text, plus a minimal POM, in a file-based Maven repository. No Java compilation,
external fixture, plugin, Maven download or new package is needed. The synthetic
Groovy project has one nontransitive dependency and one resolution task. Metadata
checks remain enabled and POM hashes correct; only the JAR's expected SHA-256 is
changed to 64 zeroes in negative cases. Production metadata is never substituted.

Each case starts with fresh project, HOME, Gradle user home and temporary directory
under a disposable fixture. Child environment is an explicit allowlist; no real
user-home configuration, cache, JVM injection or project-property environment is
passed. CI's selected JDK 17 is required. Every invocation uses `--offline`,
`--no-daemon`, disabled build/configuration caches and one worker. These are bounded
fixture controls, not a host/network sandbox or protection against hostile Gradle.

The trusted `--dependency-verification=strict` occupies the same slot as the
production bootstrap, before task tokens. For each property-file case, the second
invocation removes **only that token** from the exact command and keeps the same
fixture input bytes and case-local cache. The previous generated receipt is
removed to prevent stale success. Production bootstrap and its mocked tests stay
unchanged. No production invocation without STRICT is introduced.

The task writes a structured receipt from the real Gradle process with selected
mode, offline state, Gradle/JDK identity and either the resolved JAR's name/hash or
the exception cause types. STRICT rejection requires a failing exit, unresolved
receipt, actual `DependencyVerificationException` in the cause chain and stack,
and both expected and actual JAR checksums in diagnostics and Gradle's HTML
verification report. Success requires exit zero and the exact resolved JAR hash.
LENIENT additionally must report the mismatch while resolving. This combination
distinguishes verification from missing artifacts, parser/network failures and
infrastructure errors; no generic nonzero exit is accepted. Reports from the
preceding STRICT invocation alone cannot satisfy the LENIENT output/receipt checks.

Falsifiers: wrong selected mode; accepted bad bytes with STRICT; rejected good
bytes; missing/mismatched receipts; missing verification cause/report details;
unsuccessful option-removal control; input drift; wrong JDK/version; timeout;
changed production metadata or installed distribution. Any such result fails the
step. All generated inputs are compared after each invocation, and installation
and production metadata are checked again after the complete matrix.

## Observations and input identities

**Actual Gradle precedence and checksum enforcement observed: ten controls passed.**
The completed [branch run 42303663835, attempt 1](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42303663835)
tested exact source `25d88eb85fa29734b81c0db626ebdf2f1deea365` via `push` using
`.github/workflows/android-harness.yml`. Job
[128187497529](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42303663835/job/128187497529)
and every step completed successfully. The full completed job log was retrieved
and the ten individual JSON receipts inspected, not inferred from the green badge.
An earlier log fetch while the job was still running returned BlobNotFound; it
supplied no evidence and was replaced by the completed log retrieval.

The fixture ran **19:20:09–19:21:10 America/Fortaleza** (22:20:09–22:21:10 UTC)
on 2026-11-06. All receipts report Gradle **9.6.0**, Java **17.0.21**, vendor
**Eclipse Adoptium**, offline **true**. Setup reports **Temurin 17.0.21+9**,
Ubuntu **24.04.5**, runner image **ubuntu-24.04 / 20261101.360.1**, Actions runner
**2.338.2**, provisioner **20261028.624**. These are hosted observations, not
independently authenticated provisioning claims. The final evidence-only commit
does not change the runner, workflow or validator tested at that source.

Setup attempt [42303476607](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42303476607)
at `3c87f39c7204bb9e2312965effaa9816e0fae187` was cancelled before the runtime
step: source review found the verbose-report selector requires a project property
(`-P`), not a JVM system property (`-D`). This was a fixture diagnostic correction,
not an enforcement-policy change or an observed Gradle result. The corrected
commit is used for the actual matrix; the cancelled attempt is not a pass.
The completed job metadata confirms cancellation during the ordinary build and
the runtime step **skipped**; no fixture invocation occurred in that attempt.

| Real control | Actual observation |
|---|---|
| Correct JAR/POM, STRICT | STRICT, exit 0; exact JAR hash resolved |
| Incorrect JAR checksum, STRICT | STRICT, exit 1; checksum-specific rejection |
| Project OFF + trusted STRICT / token removed | STRICT, exit 1 / OFF, exit 0 and exact JAR hash |
| Project LENIENT + trusted STRICT / token removed | STRICT, exit 1 / LENIENT, exit 0, mismatch diagnostic and exact JAR hash |
| Disposable user-home OFF + trusted STRICT / token removed | STRICT, exit 1 / OFF, exit 0 and exact JAR hash |
| Disposable user-home LENIENT + trusted STRICT / token removed | STRICT, exit 1 / LENIENT, exit 0, mismatch diagnostic and exact JAR hash |
| Installation-level property files | **NOT RUN**: modifying the installed distribution would violate its integrity boundary |

All five STRICT negative receipts contain the actual
`org.gradle.api.internal.artifacts.verification.exceptions.DependencyVerificationException`
and `resolved: false`. Before emitting each result the runner validated the
exception stack plus expected/actual checksum details in console and HTML reports.
The one good control and four option-removal controls resolved the same JAR hash.
The final marker confirms ten controls and unchanged installation/production XML.
Raw HTML, generated binaries and receipts were not uploaded or committed; the
runner's checks and public-safe structured log entries are the retained evidence.
Their authenticity remains within GitHub-hosted execution trust, not independent
custody. No mock result is classified as a runtime control.

Gradle distribution ZIP SHA-256:
`bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01`.
Production verification XML SHA-256 remains
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.
Observed SHA-256 input identities from that run:

| Input | SHA-256 |
|---|---|
| Generated resource JAR | `1cef7661ff63a175ff1f2ad6dfc8813ded0321b5e17031f24ff1a0c404348be1` |
| Generated POM | `96450aa435ac1f4ff90faedff9be5ddbbfdb831dabb13280ef17565d3944c162` |
| Runtime runner source (committed LF bytes) | `cd417a13ac6b0102cd4a2dede30d90be33bccbec98c5e4fb9a71c490b4a4e0af` |
| Generated Groovy build source | `2b47e2e4bc154d7144e64ffba7a987152d350e3832bccfddb506acf7d8c72cd8` |
| Selected Java launcher | `a2195ae9f8a91b82f53df7e1d1b9a650937ebbabbf67d0240c6378b4fbd9990b` |
| Selected JDK release file | `9568390645661374febde48f3c7a019f21cb116d6e4c627de29c119aa7bd0efc` |

Incorrect expected JAR checksum in all negative cases: 64 zeroes. The source
contains the complete deterministic JAR/POM recipe, project, property files and
metadata template. No production dependency metadata or binary was changed.

## Preflight, provenance and limitations

Live fetched main matches the base above. All-open-PR search returned zero, so
there were no open heads/bases/diffs/files/checks/jobs/logs/reviews/comments/threads
to inspect. Merged PRs #59–63, their diffs/discussions, relevant requirements, three
ADRs, evidence, source/adoption/dependency inventories and workflows were reviewed.
Repository API reports push/admin rights and Actions enabled. GitHub Status
reported All Systems Operational, updated `2026-11-06T22:04:28.197Z`.

The primary checkout began clean; its branch was isolated from main. Three existing
worktrees and all ignored assets/private evidence were preserved; no reset, stash,
cleanup of old fixtures, private-home read or security-setting change occurred.
Initial sandboxed Git fetch/network access failed; the authorized Git operation
succeeded under per-command approval without changing sandbox configuration.

Original task-authored Python/Groovy/Markdown/YAML only, maintained by the repository
owner; no copied upstream code, new dependency/action pin, binary, external fixture,
artifact upload, credentials or private host paths are published. The synthetic
coordinate is invented and disposable, not an adopted Maven dependency. All base
tracked files use regular `100644` modes. The validator allowlist adds only the
exact new runner path; other validation and workflow checks remain intact.

Local Windows x64 CPython **3.12.14**, standard library only: all **38** existing
bootstrap tests passed, including PR #63's option-removal mutation; repository
regressions **148 passed / four existing Windows skips** (152 total). Harness
manifest validation and runner syntax compilation passed. Foundation validation
passed with **164 files, 104 Markdown files, 54 requirements and three ADRs**.
Full five-file diff, modes, links, whitespace, rights, provenance, dependency
preservation and public-data hygiene were reviewed. The production bootstrap,
verification XML, existing bootstrap suite and foundation workflow are byte-for-byte
unchanged in the diff. No local Gradle/Android/JVM execution is claimed.

Existing distribution/startup/verification protections and PR #63's command and
option-removal tests remain intact. PR #56's unconditional research execution lock,
ADR-0003 Option A, metadata, strict whole-signed-APK equality and all fifteen
historical failures remain unchanged. No Gate advances.

Hosted success establishes only this fixture behavior in that recorded run.
Same-user races, host/JDK/shell trust, mutable runner provisioning, general Gradle
configuration/cache authentication, independent administrative custody and secure
signing remain unqualified. Offline dependency resolution is not independently
observed network isolation. JDK file hashes identify inputs, not their trusted
acquisition or whole-installation provenance. Direct/modified Gradle or hostile
build code remains outside the bootstrap claim.

Phone-test prerequisites still require independent provisioning custody/review,
authenticated acquisition and installed-input manifests, configuration/cache and
private signing custody, permitted SDK acquisition/rights, and a genuinely new
method addressing the signed-byte blocker. No phone-test readiness is established.

At publication, new PR CI is **UNOBSERVED**. Publish exactly one PR, attach it
natively to this chat, check association once, then STOP without polling CI,
reviews, comments, bots or mergeability. Next proof is subsequent review of the
new PR's actual checks by the owner/reviewer; it is distinct from this branch run
and does not waive the broader qualification or phone-test blockers.
