# Bounded Gradle startup-configuration protection

Date: **2026-11-06, America/Fortaleza**. Base:
`aed83c975e7834bdbe68f4791cca15aac85c79e5` (merged PR #60).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**

## Result and boundary

Implemented a narrow admission guard in [build.py](../../android/build.py).
This supersedes the no-correction disposition only for the bounded subset in
[PR #60's evidence](gate-0-gradle-ambient-configuration.md); its observations and
broader provenance gaps remain historical evidence. The guard runs before any
download, distribution preparation or `subprocess.call`. It fails with a generic
error that contains no input values, private paths or filesystem exception details.
It is not a sandbox, a complete configuration allowlist or provenance attestation.

The exact fenced PR #60 reproduction was extracted and executed against unchanged
current main with bundled CPython 3.12.14 on Windows x64. Both original controls
passed: ambient inputs reached the mocked launch; changed installed distribution
bytes were rejected. No script, Gradle, JVM or Android code executed in that witness.

## Version-specific contract and policy

Sources below were inspected at Gradle 9.6.0 revision
`3f750f03d77e42327c5f9fcb9992110088330a32`; these are source observations, not
binary-to-source reconstruction or new upstream code adoption.

- [StartParameterBuildOptions](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/StartParameterBuildOptions.java)
  registers `init-script`/`I` and `include-build`.
- [BuildLayoutParametersBuildOptions](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/initialization/BuildLayoutParametersBuildOptions.java)
  registers `gradle-user-home`/`g` and `project-dir`/`p`.
- [CommandLineParser](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/cli/src/main/java/org/gradle/cli/CommandLineParser.java)
  accepts registered names with one or two dashes, equals values, attached short
  values and short clusters. Matching only the usual long spelling is insufficient.
- [BuildLayoutParameters](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/build-discovery/src/main/java/org/gradle/initialization/BuildLayoutParameters.java)
  selects home from `gradle.user.home`, `GRADLE_USER_HOME`, then Java's user home.
  [BuildLayoutConverter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/launcher/src/main/java/org/gradle/launcher/cli/converter/BuildLayoutConverter.java)
  applies command-line layout after system properties.
- [UserHomeInitScriptFinder](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/UserHomeInitScriptFinder.java)
  and [DirectoryInitScriptFinder](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/DirectoryInitScriptFinder.java)
  establish root init-script and `init.d` discovery.
  [ScriptingLanguages](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/build-discovery/src/main/java/org/gradle/internal/scripts/ScriptingLanguages.java)
  registers `.gradle`, `.gradle.kts` and `.gradle.dcl`; all three root names are
  refused, without assuming that declarative init execution succeeds.
- [Unix launcher template](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/jvm/plugins-application/src/main/resources/org/gradle/api/internal/plugins/unixStartScript.txt)
  and [Windows launcher template](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/jvm/plugins-application/src/main/resources/org/gradle/api/internal/plugins/windowsStartScript.txt)
  consume option environment variables and select Java through `JAVA_HOME`.
  [Java 17 launcher](https://docs.oracle.com/en/java/javase/17/docs/specs/man/java.html)
  documents `JDK_JAVA_OPTIONS`; [JVM option injection](https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/envvars002.html)
  documents `JAVA_TOOL_OPTIONS`. `_JAVA_OPTIONS` is conservatively refused as an
  implementation-specific injection surface, not asserted portable to all JVMs.

Initial guessed build-layout paths returned 404; directory discovery found the
versioned locations above. A recursive-tree request failed in transport; no claim
depends on that incomplete response.

| Input | Implemented disposition |
|---|---|
| Explicit init, alternate home/project and included build | Reject `--init-script`/`-I`, `--gradle-user-home`/`-g`, `--project-dir`/`-p`, `--include-build`; include single-dash long names, double-dash short names, equals and attached short values. Reject missing values, truncated long names and ambiguous short clusters. Scan even after `--` conservatively. |
| Startup properties | Reject `gradle.user.home`, `user.home`, `user.dir`, `gradle.home`, `org.gradle.jvmargs`, including `systemProp.` counterparts, through `-D`/`--system-prop`, `-P`/`--project-prop` and selected `ORG_GRADLE_PROJECT_*` keys. Reserved keys are case-folded to refuse Windows casing ambiguity. Other properties remain unqualified. |
| JVM option environment | Refuse any nonempty `JAVA_OPTS`, `GRADLE_OPTS`, `JAVA_TOOL_OPTIONS`, `JDK_JAVA_OPTIONS`, `_JAVA_OPTIONS`, including whitespace and malformed quoting. Do not parse, clear or silently ignore requested options. Empty values are accepted. |
| Automatic init | Accept absolute `GRADLE_USER_HOME`, otherwise Python's home plus `.gradle`; explicitly pass that same path as `-g`. Reject relative/empty/dot-dot paths, symlink/reparse ancestors, unexpected types or inspection errors. Perform only ancestor metadata and four named `lstat` queries: `init.gradle`, `init.gradle.kts`, `init.gradle.dcl`, `init.d`. Any present entry is refused, even an empty directory or dangling link. No enumeration or content read. |
| Argument ambiguity | Reject empty arguments and embedded double quotes, CR, LF or NUL; on Windows also reject `%!^&\|<>` shell expansion/metacharacters in arguments and the selected Gradle home. This conservative policy does not qualify the Windows shell or arbitrary environment. |
| Distribution | Existing exact ZIP SHA-256, manifest, installed-content/type checking and both launchers remain unchanged. Distribution-owned init entries remain covered by that manifest. |

The environment is snapshotted and forwarded explicitly. No environment variable
is scrubbed. The user home is not replaced by an empty home; signing identity and
JVM `user.home` are not changed. No home/cache/credential creation, migration,
deletion, repair, reset or permission change is performed by the guard.
An existing empty `init.d`, linked home, injected JVM flags or overridden startup
root is intentionally outside the admitted route. The user must resolve that
configuration through review; the bootstrap supplies no bypass or silent repair.

## Tests actually completed

The existing [offline suite](../../.github/scripts/test-gradle-distribution.py)
contains all new controls and remains in both Windows and Linux foundation jobs.
Every Gradle launch is mocked; fixtures are invented and disposable. Test setup
now isolates environment and argv so it cannot inspect the operator's real home.

| Validation | Observed result on Windows |
|---|---|
| Exact original main witness | Both original controls passed before implementation. |
| Extended distribution/startup suite | 28 tests passed, including all 20 existing integrity controls. |
| Positive admission | Documented five Android task arguments, help, offline, logging, ordinary project/system properties, excluded task values, JDK/SDK environment and `org.gradle.java.home` selection reach the mocked boundary unchanged. Default and explicit homes are bound. |
| Negative admission | Aliases/overrides, injected environment, known automatic entries, inaccessible/ambiguous homes and real Windows home junction refused; launch never called. Synthetic properties/cache bytes and timestamps preserved. |
| Guard-removal mutation | Patch only `admit_startup` to a no-op. PR #60 fixture's exact RuntimeError rejection assertion fails with `RuntimeError not raised`; one mocked launch is observed with the init argument and environment. Restoring the guard rejects the same fixture. |
| Existing integrity mutation | Removing only installed-tree validation still produces its expected rejection-assertion failure with mocked invocation. |
| Repository regressions | 148 passed; four existing Windows skips (152 total). Skips are not passes. |
| Harness source-manifest validation | Passed. |
| Desktop readiness / offline image / frame copy | 28 / 45 / four passed. |

The first new suite run failed on Windows environment-key casing and an incorrectly
nested mutation mock. Both were corrected before the successful run; no assertion
was suppressed. Readiness/image tests initially hit sandbox fixture-directory
access failures. Unchanged suites passed on an approved execution retry, without
changing sandbox configuration or Windows security settings.

No real Gradle fixture run on Windows or Linux, Linux runtime control, Android
build/JVM/lint run, signing, native research, phone/USB/ADB, VM or guest execution
was performed. Real host compatibility remains unobserved; positive mock admission
does not establish a successful build. The optional real-run extension was not
used: this task stays at the synthetic launch boundary and versioned source
contract, without claiming independently qualified host/tool provisioning.

## Remaining gaps and next prerequisite

Project and user `gradle.properties`, ignored `local.properties`, arbitrary project
properties, non-reserved system properties, caches/compiled scripts/transforms/task
outputs, daemon configuration, verification-mode overrides and other environment
inputs remain unqualified. This guard does not establish provenance for those
inputs or claim that init-filename absence establishes all configuration integrity.
The complete JDK/SDK/toolchain, OS/shell, trusted Python/bootstrap source, private
signing custody and administrative control remain prerequisites. Same-user or
administrator mutation after checks can race consumption; controlled quiescent
storage is assumed. Direct Gradle invocation bypasses this bootstrap policy.

The next concrete physical-test prerequisite remains an owner-appointed independent
provisioning custodian and reviewer producing authenticated immutable acquisition
and installed-file manifests, configuration/cache custody, administrative
independence, permitted SDK acquisition/rights and private signing custody.
A genuinely new method must address the signed-byte blocker before another APK
experiment. This narrow correction supplies one control; it does not qualify that
packet, independent provisioning, supply chain or physical readiness.

PR #56's unconditional execution lock, the separate Java diagnostic NO-GO,
ADR-0003 Option A, dependency metadata, strict whole-signed-APK equality and all
fifteen historical failures remain unchanged. No excluded CLI was invoked.

## Preflight, provenance and publication

Live main was verified through GitHub and fetched at the base above. Open-PR
search returned zero, so there were no open heads/bases/diffs/files/checks/jobs/
logs/reviews/comments/threads to inspect. PR #60's metadata and complete diff,
local history, requirements, ADRs, acceptance/provenance/adoption/dependency
records, bootstrap/build sources and all three workflow applicability rules were
reviewed. GitHub Status reported All Systems Operational, updated
`2026-11-06T05:29:38.400Z`. No new CI success is inferred.

The original checkout had two uncommitted evidence files; both were preserved
unchanged. Work used a separate branch/worktree based on exact live main. Existing
branches, stashes, ignored assets and private evidence were not reset or cleaned.
Only synthetic user-home data was inspected in tests.

Changes are original standard-library Python and documentation, with no copied
upstream implementation, new dependency, binary, license adoption, Gradle version/
pin change, build metadata change or workflow change. Foundation and Android
workflows apply to these paths; QEMU workflow does not. The existing Android
workflow may schedule its normal builds automatically; no manual dispatch or
companion APK build is requested. Publication ends with one native PR attachment
check; new CI, reviews, bots and mergeability remain unobserved.

Traceability: PDVA-REQ-010, 036–042, 048, 051, 054. No requirements or gates changed.

Final foundation validation: 160 files, 101 Markdown files, 54 requirements and
three ADRs. Five changed regular text files; complete diff, local links, modes,
dependency/provenance preservation, privacy and whitespace reviewed before commit.
