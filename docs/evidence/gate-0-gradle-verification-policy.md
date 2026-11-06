# Bounded Gradle dependency-verification policy guard

Date: **2026-11-06, America/Fortaleza**. Base main:
`cf3e1fb89ab24f4c0d8db502fbe104e39306e18d` (merged PR #61).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**

## Result and exact boundary

[The bootstrap](../../android/build.py) now rejects caller selection of dependency
verification mode, metadata writing and verification key refresh/export during
startup admission, before distribution directory creation, download, preparation
or invocation. Even an explicit `strict` selection is refused: normal builds use
the reviewed default and existing metadata, not an alternate caller policy.
Refusals disclose no argument values, environment values or private input paths.
This closes the identified explicit-input gap at the synthetic launch boundary;
it does not qualify every configuration source, cache, host or supply chain.

PR #59 validates installed distribution bytes against the pinned ZIP; PR #60
records ambient-input admission and its wider qualification STOP; PR #61 rejects
known startup injection but explicitly leaves verification-mode overrides open.
Their controls and limits remain applicable. The new helper is called from the
existing argument/property admission paths, without a new configuration framework.

## Immutable upstream source contract

All Gradle references below were inspected at **9.6.0** revision
`3f750f03d77e42327c5f9fcb9992110088330a32`. These are source observations, not
executed Gradle exploits or binary-to-source reconstruction.

- [StartParameterBuildOptions](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/StartParameterBuildOptions.java)
  registers `dependency-verification`/`F` and the property
  `org.gradle.dependency.verification`; `write-verification-metadata`/`M` takes a
  comma-separated checksum list. `refresh-keys` and `export-keys` are enabled-only
  boolean options, with no short aliases or configuration properties registered.
- [StartParameter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/StartParameter.java)
  initializes STRICT. [EnumBuildOption](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/build-option/src/main/java/org/gradle/internal/buildoption/EnumBuildOption.java)
  reads the configuration property and CLI value, accepting enum case variants.
- [Resolution override](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/StartParameterResolutionOverride.java)
  selects no verification for OFF; a nonempty checksum-write list or export request
  selects the verification-file writer before the ordinary verification branch.
  [Checksum verifier](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/verification/ChecksumAndSignatureVerificationOverride.java)
  logs and clears failures in LENIENT mode rather than failing as STRICT does.
  [Signature service factory](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/verification/signatures/DefaultSignatureVerificationServiceFactory.java)
  propagates refresh to key/signature caches. Refresh is a verification-state
  mutation surface, not independently proven to disable this checksum-only policy.
- [CommandLineParser](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/cli/src/main/java/org/gradle/cli/CommandLineParser.java)
  accepts registered names with either dash count, double-dash equals values,
  short `-F=off`/`-M=sha256` and attached `-Foff`/`-Msha256`. Single-dash long
  names take separate values. Single-dash long equals forms are not asserted
  supported; the policy conservatively refuses them. Short clusters containing
  argument-taking aliases fail argument completion in this parser; they are
  refused as ambiguous, not described as proven successful aliases. Truncated
  names, malformed/missing values and guarded tokens after `--` are also refused
  conservatively. No invented short alias for refresh/export is claimed.
- [Initial properties](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/InitialPropertiesConverter.java)
  and [layout properties](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/LayoutToPropertiesConverter.java)
  carry requested `-D` values into build-option properties, overriding file values.
  [Start parameter conversion](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/StartParameterConverter.java)
  applies those properties and CLI options; project properties are a separate map.
  [Project-property loader](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/subprojects/core/src/main/java/org/gradle/initialization/properties/DefaultGradlePropertiesLoader.java)
  exposes environment, system-project and command-line project sources. Accordingly
  `-P` and `ORG_GRADLE_PROJECT_*` reservations are defensive policy, not a claim
  that every such spelling directly changes StartParameter verification mode.

The reserved key, its `systemProp.` and `org.gradle.project.` counterparts are
rejected through `-D`/`--system-prop`, `-P`/`--project-prop`, their alternate dash
forms and `ORG_GRADLE_PROJECT_*`, including empty values and case ambiguity.
Other properties and `-Dorg.gradle.java.home` remain admitted. Values inside
ordinary `-D`, `-P` and `-x` attached arguments are not searched for mode aliases.

Existing metadata enables metadata checks and disables signature checks, with
185 components / 322 hashed artifacts in the dependency inventory. Its SHA-256 is
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.
That file, Gradle 9.6.0/distribution pin, AGP 9.4.0, dependency inventory, settings
and build configuration are unchanged. No bootstrap option forces a new mode over
unexamined property files; those remain an explicit limitation.

## Executed controls and compatibility

Existing Windows x64 CPython **3.12.14**, standard library only. All Gradle launches
are mocked; fixture data is invented. The tracked verification XML is copied into
the temporary fixture, never modified in the repository.

| Control | Observed result |
|---|---|
| Distribution/startup/verification suite | 34 tests passed in the full run, then the added early-creation/privacy test passed separately: 35 distinct tests, zero skips. |
| Mode and metadata options | Off, lenient, strict, case variants, aliases, attached/equals/separate values, write options, refresh/export, missing/malformed values and ambiguous clusters refused. |
| Reserved properties | System, project and environment forms, prefixes, case ambiguity, empty/missing values refused. |
| Preservation and ordering | Each matrix refusal preserves XML/private fixture/archive bytes and file timestamps; download, preparation and subprocess mocks remain uncalled. A nonexistent root remains absent. Error traceback excludes the injected private marker. |
| Positive admission | Each of the five documented Android tasks, their combined invocation, help, ordinary properties, logging/offline, refresh-dependencies and JDK/SDK selectors reach the mocked boundary. |
| New removal mutation | Disable only `admit_verification_input`; the exact same RuntimeError rejection assertion for `-Foff` fails with `RuntimeError not raised`, and exactly one mocked invocation carrying `-Foff` is observed. Restoring it rejects again. |
| Existing mutations | PR #59 installed-validation removal and PR #61 startup-admission removal still detect their intended regression and observe mocked unsafe invocation. |
| Repository regressions | 148 passed, four existing Windows skips (152 total); skips are not passes. |
| Harness source-manifest / frame copy | Passed / four passed. |
| Desktop readiness / offline image | 28 / 45 passed on the unchanged-suite retry. |

Commands: `.github/scripts/test-gradle-distribution.py`,
`test-repository-validation.py`, `validate-harness.py`, `test-desktop-readiness.py`,
`test-offline-image-inspect.py`, `test-frame-copy.py` and `validate-foundation.py`,
all run using the existing Python interpreter; whitespace checked with `git diff --check`.
Readiness/image tests initially encountered sandbox fixture-directory access errors;
these failed attempts are not passes. An approved execution retry passed both
unchanged suites; neither sandbox configuration nor Windows security was changed.

Native Linux execution and real Gradle/JVM/Android builds are **unobserved**, not
passes. No permitted native Linux execution environment was established in this
Windows session; no VM/guest route was used. The existing foundation workflow
already runs this same suite on Windows and Linux. The unchanged Android workflow
matches these paths and retains ordinary build/security checks; QEMU filters do
not match. Mock admission supports argument compatibility, not real-build success.

## Preflight, provenance and remaining prerequisites

Live GitHub main and fetched main matched the exact base above. All-open-PR search
returned zero; there were no open heads/bases/diffs/files/checks/jobs/workflows/logs/
reviews/comments/threads to inspect. Merged PRs #59–61, their diffs, relevant local
history, requirements, three ADRs, evidence, provenance/adoption/dependency records,
source and all workflow applicability rules were reviewed. GitHub Status reported
All Systems Operational, updated `2026-11-06T14:29:25.854Z`.

The old main checkout's two dirty evidence files and existing startup worktree
were preserved. A new branch/worktree isolates this change from live main.
No existing private files, cache, signing identity, ignored assets or stashes were
deleted, repaired, migrated or reset. No security or sandbox settings changed.

Original task-authored Python and Markdown only; no upstream code copied, new
package, binary, license adoption, dependency pin, workflow or mode change.
Maintenance remains with the repository owner. Traceability: PDVA-REQ-010,
036–042, 048, 051, 054. Source inspection does not qualify installed tool provenance.

Residual limits: project/user/installation property files, ignored local settings,
other properties/environment inputs, cached scripts/transforms/task outputs,
direct Gradle invocation, modified bootstrap, host/JDK/SDK/shell, administrative
custody and same-user races remain outside the bounded claim. A property file can
still select a verification mode; this task adds no property-file admission or
cache qualification. Controlled source and quiescent storage remain prerequisites.

The next Java-only phone-test prerequisite remains an owner-appointed independent
provisioning custodian and reviewer providing authenticated acquisition/installed
manifests, configuration/cache and private signing custody, administrative
independence and permitted SDK acquisition/rights. A genuinely new method must
address the signed-byte blocker before another artifact experiment. No separate
diagnostic was built or signed. PR #56's unconditional execution lock, ADR-0003
Option A, dependency metadata, strict whole-signed-APK equality and all fifteen
historical failures are preserved. No gate or physical readiness advances.

Publication is one focused PR, followed by native chat attachment and exactly one
association check, then STOP. New CI, reviews, comments, bots and mergeability
remain unobserved at that stop; no complete build-chain qualification is claimed.

Final foundation validation passed: **161 files, 102 Markdown files, 54 requirements
and three ADRs**. Full five-file diff, local links, regular text modes, whitespace,
unchanged dependency/metadata identities, source provenance and public-data hygiene
were reviewed. No binary or private path is included in the publication.
