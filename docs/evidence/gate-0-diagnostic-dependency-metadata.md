# Java diagnostic dependency metadata: generation and signed-stage boundary

Date: **2026-11-07, America/Fortaleza**. Reviewed canonical main:
`00209b30ef61442ffd702ddca632bb1baf0da5d4` (merged PR #67).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**

## Objective and scope

Determine whether the separate, runtime-library-free Java diagnostic generates
nonempty encrypted dependency information under AGP 9.4.0, and whether the normal
supported packaging path would insert it into a legitimately signed release APK.
Task execution alone is insufficient evidence. This is a companion-specific
follow-up to [PR #67](gate-0-java-memory-diagnostic.md), not another API survey.

The owner authorized source/output inspection and, if needed, an isolated unsigned
release build. No signing, keys, metadata opt-out, randomness changes, ciphertext
reuse, normalization, signature copying, installation, Android CLI, device access,
native activation, guest/VM work or new external binary adoption is authorized.
[ADR-0003 Option A](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md),
[ADR-0004 Option A](../decisions/ADR-0004-gate-0-owner-disposition.md), all fifteen
[historical signed-byte failures](gate-0-apk-reproducibility.md), the original
execution lock and full virtual-phone requirements remain intact. Traceability:
PDVA-REQ-006, 008, 010, 012, 036–042, 048, 051 and 054.

## Preflight and source/input identities

Live GitHub commit inspection and Git remote-ref inspection agreed on main above.
Open-PR search returned zero; open heads/bases/full diffs/files/commits/modes/checks/
jobs/logs/reviews/comments/threads were therefore an empty set. PR #67's merged
head is `8aa81a79926e191bdbf18cad5f9cb26155fee1b5`; its implementation/evidence,
two-commit history and empty discussion/review/thread records were inspected.
PR #50's final documentation-only preservation and fifteen failures were retained,
alongside the [independent-chain NO-GO](gate-0-independent-linux-build.md).
Requirements, all four ADRs, governance, provenance/adoption and binary/dependency
inventories, relevant merged history and all three workflows were inspected.

Exact-main [foundation run 42406952686](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42406952686)
had successful Linux job `128506589628` and Windows job `128506589479`.
[Android run 42406952682](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42406952682),
job `128506589577`, also succeeded. Check/job/step records and all three logs were
retrieved. Android logged both diagnostic dependency tasks and successful unsigned
assembly; it did not report their output sizes or signed insertion. Those receipts
are CI observations, not a local experiment or evidence of ciphertext contents.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported all systems
operational, no incidents, page update `2026-11-07T22:47:42.146Z`.

The initially clean primary checkout, four other existing worktrees, branches,
ignored outputs and private evidence were preserved; no stashes existed. The
research uses a new ignored directory and separate source export/cache/output
directories, not an existing worktree's output. No old evidence was deleted,
overwritten or relocated. No Windows incident clearance is claimed.

Official Google Maven source publications were fetched over verified HTTPS and
matched the already retained source identities:

| Publication | SHA-256 |
|---|---|
| [AGP 9.4.0 sources](https://dl.google.com/dl/android/maven2/com/android/tools/build/gradle/9.4.0/gradle-9.4.0-sources.jar) | `d462c399729eb35241208899f937037e40f2f9157a54fa9c455595ed6ceca091` |
| [Builder 9.4.0 sources](https://dl.google.com/dl/android/maven2/com/android/tools/build/builder/9.4.0/builder-9.4.0-sources.jar) | `384e5cfd3aa1292a85145c40f0b4b9f4af6f963c3c93d38ef8c19eff374b159a` |
| [Signflinger 9.4.0 sources](https://dl.google.com/dl/android/maven2/com/android/signflinger/9.4.0/signflinger-9.4.0-sources.jar) | `6ea6551350faf30f27845283e2961eed980228efaa1899f1839303b648ac50bb` |

Relevant task/packager source hashes match the existing
[source ledger](gate-0-apk-reproducibility.md#immutable-sources-and-provenance).
AGP, builder, Signflinger and apksig 9.4.0 and Tink 1.7.0 cached binaries were
separately compared with their tracked verification pins before the build.
This binds inspected release sources and pinned binaries by publication/version;
it is **not** independent source-to-binary reconstruction or security qualification.
The existing 185-component/322-artifact inventory remains unchanged. Sources carry
Apache-2.0 notices; JDK GPLv2/Classpath Exception, SDK terms and transitive notices
retain their existing limits. No upstream source/binary is committed or adopted
anew. Repository owner remains the existing tools' maintenance owner.

## Three distinct stages: pinned-source findings

Paths below are within the source archives above; line numbers refer to those
exact publications, not a moving upstream branch.

1. **Dependency report.** AGP
   `com/android/build/gradle/internal/tasks/PerModuleReportDependenciesTask.kt`
   lines 186–224 serialize runtime-library entries, repositories and a module
   record. Empty library loops do not skip the repository loop or unconditional
   module builder. Lines 263–298 select external runtime AAR/JAR artifacts,
   settings repositories and module name `base`. A dependency-free app is not
   necessarily a zero-byte report. The schema distinguishes `library` (field 1),
   `library_dependencies` (2), `module_dependencies` (3) and `repositories` (4).
2. **Encrypted payload.** `ApplicationTaskManager.kt` lines 220–241 register the
   report for non-debuggable variants and the encryption task for a non-debuggable
   base module when both include-in-APK switches are true. DSL
   `internal/dsl/DependenciesInfoImpl.kt` initializes inclusion to true;
   `options/BooleanOption.kt:148` also defaults APK dependency information to true.
   The diagnostic changes neither setting. `SdkDependencyDataGeneratorTask.kt`
   lines 295–326 read the report, DEFLATE it, encrypt it and write
   `sdkDependencyData.pb`, then emit the human-readable `sdkDependencies.txt`.
   There is no library-count or empty-input early return in this action. Task
   registration/execution is conditional; encryption is not conditional on having
   external runtime libraries once this action runs. Up-to-date tasks need not
   regenerate bytes. The retained Tink analysis establishes randomized encryption;
   this task does not repeat that crypto survey or analyze key/nonce material.
3. **Signing-block insertion.** AGP `tasks/PackageAndroidArtifact.kt` lines
   625–628 connect `SDK_DEPENDENCY_DATA`; lines 931–939 read its bytes and pass them
   to `IncrementalPackagerBuilder.withSigning`. That builder returns immediately
   for null signing configuration (lines 154–161); otherwise it forwards the
   dependency bytes into signing options (line 201). Builder `ApkFlinger.kt`
   lines 99–124 selects ordinary `ZipArchive` without signing options, or
   `SignedApk` with them and `setSdkDependencies`. Signflinger `SignedApk.java`
   lines 245–257 enter the insertion path when v2 or v3 signing is enabled and
   insert the value under `0x504b4453`. `SigningBlockUtils.java` lines 60–68 skip
   null/zero-length values; lines 81–96 insert a nonempty supplied value without
   decrypting or regenerating it. AGP variant `SigningConfigImpl.kt` lines 91–120
   default to v3 off and v2 on for this API-37 scope absent overrides.

**Conditional source conclusion:** a successfully configured normal AGP release
signing path with metadata retained and v2/v3 enabled would include this nonempty
payload. The current module explicitly has `signingConfig null`, so its unsigned
APK does not exercise that branch. Applying an unrelated signing tool later to
the unsigned ZIP is not the same packaging path and is not established to import
the detached intermediate. No alternate signing route is qualified here.

## Actual procedure, controls and observations

Existing safely inspectable intermediates had a 97-byte dependency report and a
185-byte encrypted-output file, plus a text report showing only the base module
and the two configured public Maven repositories. Their original per-file build
correspondence was incomplete; they were not accepted as fresh exact-main proof.

A fresh export of every tracked file from the main SHA above was byte-checked
against `git archive`. Its module output directory did not exist. The existing
Gradle ZIP was copied to a new bootstrap store; only Maven artifact/metadata cache
directories were copied into a separate Gradle home, with no prior task outputs,
init scripts or user-home properties copied. No external binary was downloaded.
The unchanged bootstrap checks the Gradle 9.6.0 ZIP and extracted installation,
admits startup inputs and forces STRICT dependency verification.

The build used verified absolute installed paths for Temurin **17.0.21+9**, SDK
**37.0 / revision 2 / extension 22 / preview 0** and Build Tools **36.0.0** on
Windows x86_64, with existing CPython **3.12.14**. SDK platform JAR identity matched
the public PR #67 pin. Child-process tool/home selection changed no persistent
environment or security setting. The exact source/build/settings/properties and
verification XML were not modified. Invocation, using the absolute Python path:

```text
python <isolated-source>/android/build.py --offline --configure-on-demand --no-build-cache :memory-diagnostic:assembleRelease
```

Retained setup failures: bare Python resolved to an unusable Store alias, so the
existing bundled interpreter was selected. A source-fetch socket denial required
scoped execution approval, with TLS verification retained. The first build stopped
at plugin initialization because Android's inferred user directory was unwritable.
The retry selected a new task-local `ANDROID_USER_HOME`; the first log was retained.
An analytics-initialization warning remained and is not a security qualification.

The retry completed with exit **0**, `BUILD SUCCESSFUL`, **43 actionable tasks,
43 executed**. Only the diagnostic project configured; no harness task executed.
The following are actual local observations, separate from the hosted receipts:

| Observation/control | Result and evidential limit |
|---|---|
| Freshness/source control | Before both attempts the module build directory was absent. After completion every exported tracked file still matched the exact-main archive. Report, payload, text report and APK were regular nonempty files with modification times after the successful invocation started. |
| Producer execution | `collectReleaseDependencies`, `sdkReleaseDependencyData` and `packageRelease` executed without UP-TO-DATE/FROM-CACHE labels; no build-cache restoration occurred. Pre-build lifecycle tasks marked UP-TO-DATE do not stand in for these producers. |
| Actual report | **97 bytes**. A bounded standard-library protobuf wire inspection, checked against the pinned generated schema, found zero library records, zero library-edge records, one `base` module without dependency indices and two Maven repository records matching unchanged settings. The generated text report corroborates that structure. |
| Actual generated payload | **185 bytes**, nonempty and different from the report bytes. Source/input/output correspondence identifies it as the generator's encrypted output, not a decoded/decrypted or independently cryptographically verified payload. No encrypted bytes or digest is published. |
| Empty-library source control | In the exact task source, empty library/edge loops still reach unconditional repository/module serialization and the generator's compress/encrypt/write operation. The real zero-library report plus fresh nonempty output exercises this case without an opt-out or added library fixture. |
| Unsigned-stage contrast | Existing package inspector passed manifest/version/API/DEX/native/signature checks on the fresh APK, including absence of an APK signing block and v1 signatures. This genuine output distinguishes generated metadata from metadata already inserted into a signed container. |
| Retained-output comparison | Fresh and retained report bytes matched; encrypted payload bytes differed. This rejects simple reuse of that retained payload. The old build's incomplete correspondence prevents treating this as a controlled independent encryption or signed-build pair. |

Fresh directory absence, exact output locations, task receipts, source comparison,
timestamps and schema checks jointly guard against stale/unrelated outputs; size
alone would not. Empty-output production, damaged-input execution and actual
signed-stage controls were **NOT RUN**. No fixture supplies the production result.

**Outcome:** this exact diagnostic **does generate nonempty encrypted metadata**
despite having no declared external runtime libraries. It encounters the known
generation mechanism; the normal metadata-retaining AGP signed path would include
the value under the conditions traced above. The signed-artifact obstacle is
therefore **inferred for a future legitimately signed diagnostic**, not a newly
observed signed-byte failure. No genuinely new supported route or successful
whole-signed-APK reproducibility has been demonstrated.

## Limits, falsifiers and next proof

No signed diagnostic was produced or inspected. Genuine signed insertion, a pair
of independent signed builds, whole-signed-APK equality, qualified private custody,
independent verification and Android runtime behavior are **NOT RUN**. No new
randomness experiment, opt-out, signing-policy control or ciphertext reuse was
performed. Source correspondence is not a trusted-host attestation; the existing
Windows security incident and independent-chain NO-GO remain unresolved.

Reopen the bounded conclusion if the exact fresh report is absent/empty, contains
unexpected runtime libraries/repositories, the producer was skipped/restored from
cache, exported source differs, artifact hashes mismatch, or the unchanged normal
packaging path demonstrably omits a supplied nonempty value under v2/v3 signing.
A future AGP/configuration change requires fresh review; a task name, unsigned
byte equality or successful signature alone cannot falsify the signed-byte blocker.

The next proof remains independent qualification under PR #67's existing packet:
reviewed environment/input provenance and security disposition, private signing
custody/verifier, and a genuinely new supported method addressing strict signed
bytes before any separately authorized signed experiment. This research does not
authorize that experiment or any physical attempt, and discovers no new route.

## Retention and publication

Local validation passed: foundation (**177 files, 108 Markdown files, 54
requirements, four ADRs**), harness source-manifest validator, diagnostic source
policy with RWX/INTERNET negative controls, and **152 repository tests: 148 passed,
four existing Windows skips**. Fresh unsigned package inspection passed as above.
These are local executions; Linux-only controls, separate full release lint and
the new PR's hosted jobs were not rerun/observed. Full final text diff, local link
targets, public source identities, provenance, privacy, regular 100644 modes and
whitespace were reviewed. No validation or production code changes are needed.

Owner clarification: no owner-controlled private backup location is established
or verified. Receipts remain locally in the private work area, without public
upload. **Independent backup UNVERIFIED; private evidence UNPRESERVED.** Ignored
storage is not independent backup. No destination is invented; any operation
requiring verified independent private retention remains stopped. Only sanitized
findings and public source/tool identities belong in this evidence PR; no APK,
encrypted bytes, private hashes/paths, keys or raw local logs are published.

Exactly this evidence and its index entry change. Historical failures, lock,
requirements/ADRs, source, dependencies, signing configuration and workflows remain
byte-identical. New-head CI is **UNOBSERVED at publication**; unchanged foundation
applies, Android/QEMU path filters do not select this documentation-only diff.
Filtered/unrun checks are not passes. Publish one PR, attach it natively to the
current chat, verify association once, then stop without polling CI, reviews,
comments, bots, badges or mergeability.
