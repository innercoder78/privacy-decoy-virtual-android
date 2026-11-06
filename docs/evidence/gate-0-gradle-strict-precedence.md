# Fixed Gradle STRICT selection over property-file modes

Date: **2026-11-06, America/Fortaleza**. Base main:
`a3d9394b6f8b42894f739c1ef3cb9716828d09ee` (merged PR #62).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**
Traceability: PDVA-REQ-010, 036–042, 048, 051, 054.

## Result and boundary

[The bootstrap](../../android/build.py) now supplies the literal
`--dependency-verification=strict` after its trusted project/home selectors and
before every caller token. The existing admission guard continues rejecting
caller verification selection (including STRICT), metadata writing, key operations
and reserved properties before directory creation, download, preparation or launch.
No configuration value is used to construct or select the internal mode.

**Source-backed inference:** valid OFF/LENIENT property-file mode values cannot
weaken this CLI selection in the pinned Gradle conversion path. The fixed token
is parsed before any caller task or `--`; admitted ordinary property values cannot
replace it. This is bounded to the reviewed bootstrap, parser and mode-conversion
contract, not arbitrary hostile build code or a modified bootstrap/JVM/shell.

**Direct observation:** synthetic launches carry the fixed option in the expected
position and preserve caller arguments and fixture bytes. **Real Gradle mode
selection and dependency rejection: NOT RUN.** The offline tests do not execute
Gradle, parse its property files or establish actual JVM enforcement. No Python
simulation is presented as an independent test of Gradle precedence.

## Exact upstream source observations

All links identify Gradle **9.6.0**, immutable revision
`3f750f03d77e42327c5f9fcb9992110088330a32`, inspected during this task.

1. [LayoutToPropertiesConverter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/LayoutToPropertiesConverter.java)
   loads recognized build-option properties from installation, build-root and
   user-home `gradle.properties`, then JVM/requested system properties. Thus a
   recognized file value can replace the initial STRICT default in PR #62.
   [InitialPropertiesConverter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/InitialPropertiesConverter.java)
   collects requested system properties. The separate
   [project-property loader](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/subprojects/core/src/main/java/org/gradle/initialization/properties/DefaultGradlePropertiesLoader.java)
   does not make every project-property spelling a proven mode override.
2. [StartParameterConverter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/StartParameterConverter.java)
   passes the property map and parsed CLI to the build-options converter and
   enables mixed tasks/options. [BuildOptionBackedConverter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/BuildOptionBackedConverter.java)
   applies environment, properties, then command-line options to the same target.
3. `DependencyVerificationModeOption` in
   [StartParameterBuildOptions](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/StartParameterBuildOptions.java)
   binds `org.gradle.dependency.verification` and CLI `dependency-verification`/`F`
   to `setDependencyVerificationMode`.
   [EnumBuildOption](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/build-option/src/main/java/org/gradle/internal/buildoption/EnumBuildOption.java)
   applies a present CLI enum even when a property already set the target. Invalid
   enum property values can fail during property conversion; they are not a proven
   successful weakening and this change does not sanitize arbitrary Gradle logs.
4. [CommandLineParser](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/cli/src/main/java/org/gradle/cli/CommandLineParser.java)
   accepts the double-dash equals form and treats `--` as ending options. Putting
   the trusted token after caller tokens would be wrong; this implementation
   places it first relative to them. Repeated argument-taking options are rejected
   by this parser, but the bootstrap independently rejects caller mode options.
5. [StartParameterResolutionOverride](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/software/dependency-management/src/main/java/org/gradle/api/internal/artifacts/ivyservice/ivyresolve/StartParameterResolutionOverride.java)
   selects no verification for OFF or absent metadata; write/export selects the
   writer before normal verification. Otherwise it passes the selected mode to
   the verifier. Existing metadata and write/key guards therefore remain essential.

The raw-source web fetch initially failed; the exact files were successfully
retrieved through the GitHub connector. Source inspection is not binary/source
correspondence or a real Gradle experiment.

## Executed controls

Windows x64, existing bundled CPython 3.12.14, standard library only.
Run `.github/scripts/test-gradle-distribution.py` with that interpreter:
**38 tests passed, zero skips**, including the three added tests.

| Control | Observed result and limit |
|---|---|
| Fixed STRICT / caller ordering | Exact launch slot and one occurrence asserted; caller tail and environment unchanged for no arguments, help, leading `--`, task followed by `--`, ordinary properties/offline and all five documented Android tasks. Mock only. |
| Property files | OFF, LENIENT and STRICT at each of project, user and synthetic installation locations (nine cases) retain the fixed CLI. Installation fixtures are included in the pinned synthetic ZIP, not inserted into an existing install. This verifies launch construction/preservation, not Gradle property loading. |
| Preservation | Property files, synthetic distribution files, copied real verification XML and invented private evidence retain bytes and modification timestamps. No real property, cache or signing file is edited/read by these new fixtures. |
| Trusted-option mutation | Compile a source copy with only the single literal option removed; replace only main's code, retaining fixture globals and admission/integrity guards. The same positive launch assertion fails specifically with `trusted STRICT option missing`; the mocked call occurred once. Restoring main passes again. No generic exception counts. |
| Existing PR #62 controls | Caller OFF/LENIENT/STRICT, aliases, reserved properties/environment forms, metadata/key operations and attempts after `--` remain rejected; early rejection prevents creation/download/preparation/invocation and excludes synthetic private values from guard errors. Its helper-removal mutation still detects the intended regression. |
| Existing PR #59 / #61 mutations | Installed-validation removal and startup-guard removal still trigger their exact rejection-assertion failures and observe mocked unsafe invocations. |
| Repository regression suite | 152 total: 148 passed, four existing Windows skips. |
| Frame copy / harness source manifest | Four passed / passed. |
| Desktop readiness / offline image | 28 / 45 passed on the unchanged-suite approved retry. |

The first command could not start the Windows Python app alias; it was replaced
with the existing bundled interpreter, with no installation. Readiness/image tests
initially failed on sandbox fixture-directory access (28/22 errors respectively);
those failed attempts are infrastructure failures, not successful validation.
An approved retry passed the unchanged suites without changing security settings.

Real standalone Gradle precedence, positive checksum acceptance and negative
checksum rejection remain **NOT RUN**: no independently qualified JDK/configuration/
cache execution contract was established, as recorded in the
[ambient-input prerequisite](gate-0-gradle-ambient-configuration.md).
The strongest exercised boundary here is the mocked bootstrap launch combined
with exact source inspection. A future qualified disposable non-Android fixture
must observe the selected mode for OFF/LENIENT files, verify known-good and
deliberately mismatched local dependency checksums, and remove only the fixed
option to show those same files restore weakened behavior. Do not treat today's
mutation as that runtime experiment.

## Preflight, unchanged protections and publication

Live fetched main matched the base above. GitHub all-open-PR search returned zero;
there were no open heads/bases/diffs/files/checks/jobs/logs/reviews/comments/threads
to inspect. Merged PRs #59–62, relevant history, requirements, ADRs, evidence,
provenance, dependency inventory and workflows were reviewed. Repository API
reported push/admin rights. [GitHub Status](https://www.githubstatus.com/)
reported All Systems Operational, updated `2026-11-06T14:29:25.854Z`.
The dirty primary checkout and both earlier worktrees were preserved; this work
uses a new isolated branch from fetched main. No stash or ignored asset was reset.
Private backup durability remains unverified; existing private evidence is retained.

All 161 base tracked files have regular `100644` modes; no tracked binary suffix
was found in the inventory. Changes are original task-authored Python/Markdown;
upstream code is referenced, not copied/adopted. No package, tool, binary, workflow,
dependency/version pin, signing change or license adoption is introduced.
The owner retains maintenance responsibility. Metadata SHA-256 remains
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.

Foundation Windows/Linux jobs already run the offline bootstrap suite. Android
workflow filters apply; QEMU filters do not. Local Android builds/JVM/lint/APK
checks and Linux/native research are NOT RUN under this task's exclusions and
unqualified toolchain; they are not passes. CI rules are unchanged and new PR CI
is deliberately unobserved after publication, not waived.

STRICT selection does not authenticate property files, caches, other build inputs,
the environment or signing custody. Modified scripts/plugins, direct Gradle,
host/JDK/SDK/shell trust, same-user races and administrative custody remain outside
the claim. Existing startup and distribution protections remain necessary.
PR #56's unconditional execution lock and ADR-0003 Option A retain dependency
metadata, strict whole-signed-APK equality and all fifteen historical failures.

Next Java-only diagnostic prerequisite: owner-appointed independent provisioning
custodian/reviewer, authenticated acquisition and installed-input manifests,
configuration/cache and private signing custody, administrative independence and
permitted CLI-free SDK acquisition/rights. A genuinely new method must address
the signed-byte blocker before another artifact experiment. No diagnostic was
implemented, assembled or signed; no phone, USB, ADB, guest or VM was used.

Publish exactly one PR, attach that PR to this chat, check association once, then
STOP without polling CI, reviews, comments, bots or mergeability.

Final local foundation validation passed: **162 files, 103 Markdown files,
54 requirements and three ADRs**. Complete five-file diff, links, regular text
modes, whitespace, unchanged metadata/dependencies, provenance and public-safe
content were reviewed. No private host path or configuration value is published.
