# Ambient Gradle configuration admission: STOP

Date: **2026-11-05, America/Fortaleza**. Examined live main:
`4494d03b991c3728af668a4238a95d923dedb1c7`, tree
`676a3d77d6e4da195c6436b161718dcf36174b93` (merged PR #59).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**

## Decision and exact scope

**The bootstrap admission gap is reproduced; correction is NOT implemented.**
A verified synthetic distribution reaches the mocked launcher while an external
Gradle user home, JVM-option environment variables and an explicit initialization
script argument remain admitted. The real Gradle implementation supplies the
source-level connection from that input to initialization-script processing.
No actual Gradle/JVM execution or Android build occurred. This is not evidence
that any real installation is compromised, nor an executed Gradle exploit.

STOP at qualification of the configuration/input-admission contract. The
repository has no independently qualified external configuration/cache manifest
or provisioning authority for either supported build host. The existing
[independent build assessment](gate-0-independent-linux-build.md) explicitly
leaves these inputs and administrative custody unqualified. A check that accepts
their current contents, their absence, or a newly created directory would not
establish the requested provenance. A mandatory qualified-input check without
any qualifying configuration would block the currently documented build route.
This record does not assert that a future narrow correction is impossible.

The task permits a precisely evidenced STOP when the property cannot be supplied
within approved behavior. No new trust authority, cache admission exception,
signing-home change or provisioning qualification is silently selected here.
The narrower technical option of blocking known init filenames alone remains
possible, but does not satisfy the requested equivalent-configuration coverage.

Traceability: PDVA-REQ-010, 036–042, 048, 051 and 054; see
[requirements](../requirements.md), [source policy](../source-provenance-policy.md)
and [evidence criteria](../acceptance-evidence-criteria.md). No requirement changes.

## Preflight and preservation

GitHub's live main commit API confirmed the exact SHA above. Open-PR search
returned zero: no open heads/bases/diffs/files/checks/jobs/logs/reviews/comments/
threads existed to inspect. Merged PR #59's record and full diff were retrieved;
its parent is `e0e9f4fbbeb9687ff28af0bf13cafae2dd878dda`. Local history, all three
workflows, bootstrap, Gradle settings/properties/module, requirements, three ADRs,
provenance/acceptance policy, adoption/dependency records and the preceding
installed-integrity and independent-build evidence informed this review.
No new CI result is inferred from historical evidence.

[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported `none`,
All Systems Operational, page updated `2026-11-05T19:24:39.232Z`.
The checkout was clean on the same main, with one worktree and no stashes.
No private host configuration, user Gradle cache, signing material or confidential
evidence was opened. Existing assets and Git state are preserved. Only disposable
invented test fixtures were created and cleaned by their existing test helper.
No sandbox permission or Windows security setting was changed.

## Version-specific source and input trace

The upstream `v9.6.0` commit API resolved to
`3f750f03d77e42327c5f9fcb9992110088330a32`. Source references below identify that
revision, not the moving current manual. Initial versioned manual requests were
inaccessible through the web tool; direct HTTPS was denied by local socket policy.
Old source paths returned 404. Repository directory discovery then located the
relocated implementation and versioned documentation through the GitHub connector.
The retrieved current manual identified **9.8.2** and was not substituted for 9.6.0.

- [StartParameter](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/StartParameter.java):
  `getAllInitScripts()` starts with explicit init scripts, then appends scripts
  discovered in the user home and distribution. Its verification mode starts STRICT.
- [UserHomeInitScriptFinder](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/UserHomeInitScriptFinder.java)
  resolves a root `init` script and searches `init.d` beneath the selected user home.
  [DirectoryInitScriptFinder](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/DirectoryInitScriptFinder.java)
  uses the script resolver and sorts directory discoveries.
- [InitScriptHandler](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/subprojects/core/src/main/java/org/gradle/initialization/InitScriptHandler.java)
  obtains that complete list, loads each file and passes it to the script processor.
- [DefaultGradlePropertiesLoader](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/subprojects/core/src/main/java/org/gradle/initialization/properties/DefaultGradlePropertiesLoader.java)
  reads installation/user-home properties and exposes system, environment and
  command-line project-property sources.
- [9.6.0 build-environment documentation source](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/documentation/docs/src/docs/userguide/reference/runtime-configuration/build_environment.adoc)
  specifies user-home properties ahead of project/installation properties, the
  default user-home `.gradle` location, system-property home override, project
  environment properties, client JVM options and separate daemon JVM selection.
- [StartParameterBuildOptions](https://github.com/gradle/gradle/blob/3f750f03d77e42327c5f9fcb9992110088330a32/platforms/core-runtime/start-parameter/src/main/java/org/gradle/initialization/StartParameterBuildOptions.java)
  includes initialization scripts, included builds, project-cache directory,
  configuration/build caches and dependency-verification write/mode options.

These are source observations, not a binary-to-source reconstruction. The complete
launcher/JVM/AGP input closure and every alias/precedence interaction are not
qualified by this inspection. In particular, JVM-owned option variables require
the selected JDK's own authoritative behavior and separate runtime controls.

| Input | Actual bootstrap contract at examined main | Trust consequence |
|---|---|---|
| Distribution | Pinned 9.6.0 ZIP and PR #59's complete installed-tree check | Changed installation entries fail; external configuration is outside this tree. |
| Invocation | Absolute selected `bin/gradle` or `bin/gradle.bat`, `-p ROOT`, `--no-daemon`, then every caller argument; no explicit `env` or `cwd` | Caller arguments and process environment reach the launcher; no admission policy intervenes. |
| User home/init | No explicit home selection or initialization-script admission | `GRADLE_USER_HOME`, defaults and overrides can select inputs outside reviewed source. Distribution init files remain covered by PR #59. |
| Properties/JVM | Repository properties request `-Xmx2g`, UTF-8 and two Android settings; no environment scrub | User properties, `JAVA_OPTS`, `GRADLE_OPTS`, JVM-owned options and `ORG_GRADLE_PROJECT_*` are not rejected. `--no-daemon` is not configuration isolation. |
| JDK/SDK | README requires JDK 17, `JAVA_HOME` and `ANDROID_HOME`; workflow selects runner JDK and SDK | Selection is explicitly expected, but path selection alone is not authenticated installed-tool provenance. Ignored `local.properties` is another configuration surface requiring an explicit policy. |
| Caches | No bootstrap cache inventory/admission; project `.gradle`, user-home caches and output reuse remain external state | Dependency artifact hashes do not constitute a complete manifest of configuration, compiled scripts, transformed artifacts or task outputs. No cache contents were inspected. |
| Arguments | All `sys.argv[1:]` are forwarded, including init/home/project/property/cache/verification switches | No reviewed task/option allowlist; normal-build prohibition on verification-write mode is documentation, not bootstrap enforcement. |
| Dependency/source baseline | Reviewed settings, AGP 9.4.0, verification XML and dependency inventory | Preserved; initial cache/TOFU provenance limitations from the existing ledger remain. |

## Reproducible harmless bootstrap witness

Run the following Python from the repository root using Python 3.11+ with
assertions enabled. It reuses the existing synthetic-distribution helper and
patches only the fixture root/pin, process environment, argv and final launch.
**No Gradle, shell launcher, JAR or init script is executed.** Environment values
are invented and cleared within the patch, so no private host data is read.
Fixture cleanup affects only the helper's newly created temporary directory.

```python
import importlib.util
import os
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "controls", ".github/scripts/test-gradle-distribution.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
t = m.DistributionTests()
t.setUp()
try:
    external = t.root / "external-home"
    external.mkdir()
    init = external / "init.gradle"
    init.write_text("println 'PDVA_SYNTHETIC_INIT'\n", encoding="utf-8")
    props = external / "gradle.properties"
    props.write_text("org.gradle.jvmargs=-Dpdva.fixture=true\n", encoding="utf-8")
    env = {"GRADLE_USER_HOME": str(external),
           "ORG_GRADLE_PROJECT_pdvaFixture": "true"}
    for name in ("GRADLE_OPTS", "JAVA_OPTS", "JAVA_TOOL_OPTIONS",
                 "JDK_JAVA_OPTIONS", "_JAVA_OPTIONS"):
        env[name] = "-Dpdva.fixture=true"
    before = {p.name: p.read_bytes() for p in external.iterdir()}
    with patch.dict(os.environ, env, clear=True), patch.object(
            m.b.sys, "argv", ["build.py", "help", "--init-script", str(init)]), \
            patch.object(m.b.subprocess, "call", return_value=17) as launch:
        assert m.b.main() == 17
        launch.assert_called_once()
        assert launch.call_args.kwargs.get("env") is None
        assert launch.call_args.args[0][-2:] == ["--init-script", str(init)]
        assert all(os.environ[k] == v for k, v in env.items())
    assert before == {p.name: p.read_bytes() for p in external.iterdir()}
    print("PASS: ambient inputs admitted; launch mocked")
    (t.home / "lib/test.jar").write_bytes(b"changed")
    with patch.dict(os.environ, env, clear=True), patch.object(
            m.b.subprocess, "call") as launch:
        try:
            m.b.main()
        except RuntimeError as error:
            assert str(error) == "Installed distribution content mismatch"
        else:
            raise AssertionError("Expected distribution rejection")
        launch.assert_not_called()
    assert before == {p.name: p.read_bytes() for p in external.iterdir()}
    print("PASS: changed distribution rejected; external fixtures preserved")
finally:
    t.doCleanups()
```

Observed on Windows x64 with existing bundled CPython **3.12.14**: both controls
passed. The synthetic pin is intentionally replaced by the helper; this does not
claim an authentic Gradle archive was executed. The first control falsifies
bootstrap rejection of ambient configuration; the second separates that gap from
distribution tampering. It does not prove init-script execution on Windows or Linux.

## Rejected minimum corrections and next proof

| Candidate | Why it does not meet this task's full property |
|---|---|
| Deny known init filenames and option variables | Useful subset, but cannot qualify unknown alternate configuration, cache inputs, project-local properties, JVM selection or unrestricted arguments. Filename absence is not input provenance. |
| Set a new empty user home and clear the environment | Prevents some ambient discovery, but freshness is not qualification; inherited project caches and tool/plugin inputs remain. Changing the JVM/Android user home also requires preserving signer/SDK behavior explicitly. |
| Hash the existing user home and admit that manifest | Self-attests unknown input; creates no reviewed provenance. A mutable cache cannot become trusted merely because its current bytes were hashed. |
| Require independently approved complete configuration/cache receipts now | Fail-closed behavior is feasible, but no qualifying receipt exists for the documented Windows/Linux routes. Enforcing it now blocks those routes instead of preserving supported builds. |

Next proof: identify a reviewed provisioner/maintainer and approve a minimal input
contract: explicit JDK/SDK selectors; exact allowed tasks/options; configuration
file identities and permitted absence; environment allowlist including OS launch
requirements; explicit user-home, project-cache and output-state ownership;
cache admission/regeneration provenance; and preservation of signing identity.
No migration, deletion or automatic repair of existing private state may be part
of that contract. Missing, ambiguous, substituted or unqualified inputs must fail
before the distribution launch, with public-safe errors.

Then qualify harmless real 9.6.0 runs against an empty standalone fixture project
on Windows and Linux, without Android tasks. Require positive JDK/SDK-selection
controls and negative init/root/init.d, properties, JVM-option, argument override,
missing receipt, substitution and preservation controls. Remove only the new
admission guard and require the same rejection assertion to fail with a recorded
mocked invocation. **That new-protection mutation was not performed here because
there is no new protection.** The existing distribution mutation is separate.

Filesystem checks alone cannot prevent a same-user/administrator writer changing
configuration after validation and before JVM consumption. Quiescent storage,
controlled process environment and independently qualified administrative custody
remain preconditions, not properties established by this record.

## Actual validation and publication limits

Existing unchanged suites ran locally: Gradle distribution **20 passed**, including
its installed-validation-removal mutation and real Windows junction rejection;
repository regressions **148 passed / four existing Windows skips (152 total)**;
desktop readiness **28 passed**; offline image **45 passed**; frame copy **four
passed**. Harness source-manifest validation passed. No test suppression or
failure reclassification was introduced. Real Gradle execution, Linux runtime
controls, JVM/Android builds, signing and physical tests remain **unobserved**.
The excluded CLI product, native security investigation, QEMU experiments and
stopped APK experiment were not invoked or reopened.

Final foundation validation passed: **159 files, 100 Markdown files, 54
requirements and three ADRs**. The exact fenced reproduction was extracted and
executed successfully. Both complete changed texts, local links, public-data
hygiene and whitespace were reviewed; publication uses regular `100644` files.

This evidence and its index are the only changes: original task-authored Markdown
and a standard-library reproduction snippet; no upstream implementation copied,
new dependency, binary, license adoption, mode or workflow change. Upstream sources
are references, not adopted code. Gradle version/pin, all dependency metadata,
PR #56's unconditional execution lock, ADR-0003 Option A, strict whole-signed-APK
equality and all fifteen historical failures remain intact. The wider host,
supply chain, signing custody and phone-test blockers remain unresolved.

Foundation applies to every PR. These two documentation paths do not match the
Android or QEMU workflow filters. No filters were changed to obtain that outcome.
The new PR's CI/reviews/mergeability are deliberately unobserved: publish one
focused evidence PR, attach it to the current chat, verify that association once,
then stop. This record cannot qualify the build chain or authorize physical work.
