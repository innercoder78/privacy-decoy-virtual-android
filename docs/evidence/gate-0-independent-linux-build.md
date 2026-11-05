# Independent Linux build-and-signing qualification: NO-GO

Date: **2026-11-05, America/Fortaleza**. Exact reviewed main:
`9d4ae689866327a3b25680de19f1975157a1e76b`, tree
`72dbca0ba8bbe60dc97cb8714b6843d8ae06dfd9` (merged PR #57).
**Gate 0 Unresolved; Gates A–G Not reached. Physical readiness NOT READY — STOP.**

## Objective, hypothesis and decision

Qualify one replacement chain for the separate
[Java-only diagnostic](gate-0-java-memory-feasibility.md), without depending on
the affected Windows installation. This record does not repeat the API survey
or reopen the deferred security incident.

**H-independent:** a separately provisioned Linux environment, acquiring reviewed
source and tools directly from authenticated upstreams, can demonstrate that no
Windows tool, cache, executable path, credential or signing asset is an input,
while retaining dependency metadata, signing policy and whole-signed-APK equality.

The concrete candidate examined is the existing GitHub-hosted Ubuntu 24.04
infrastructure, with independently acquired, immutable tool inputs and a
separately qualified owner-controlled private signing/verification endpoint.
**Not qualified.** Existing hosted receipts establish remote execution of
identified repository checks, not a complete independent build/signing chain.
Missing provenance and credential/custody proof prevents a GO. A clean Linux
machine could remove local binary/cache dependencies in principle; its freshness
does not prove upstream binaries safe, repository authority independent, or strict
APK reproducibility. No Linux environment was newly provisioned in this task.

Traceability: PDVA-REQ-008, 010, 012, 036–042, 048, 051 and 054;
[requirements](../requirements.md), [source policy](../source-provenance-policy.md),
[acceptance criteria](../acceptance-evidence-criteria.md) and
[governance](../governance.md). No requirement or adoption decision changes.

## Live inspection and actual observations

GitHub's commit and recursive-tree APIs confirmed the main/tree above. PR search
returned zero open PRs: there were no open heads/bases/full diffs/files/checks/
jobs/logs/reviews/comments/threads to reconcile. The complete merged PR #57 diff
contains only its evidence and index; reviews, issue comments and review threads
were empty. Its parent is `78c4d550a81ef5e96940a4fafac18a5d983665f2`.
All executable/configuration inputs therefore remain those of PR #56.

The exact-main [foundation run 41958604871](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41958604871)
has two successful jobs: Linux `127019344771` and Windows `127019344509`.
Job steps and logs were retrieved. Linux logs show 152 repository tests, 28
readiness, 45 offline-image and four frame-copy tests passing, plus the existing
host controls and their negative controls. Windows logs show 45 and four passing.
These are historical baseline observations, not tests of this new evidence PR.

The latest inspected [Android run 41954841886](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41954841886),
job `127007154179`, belongs to PR #56's main SHA, **not** PR #57's main SHA.
Its successful steps/logs record assembly, protocol/lint, symlink mutation,
600 execution-lock denials, three rejected lock mutants and five packaged-policy
tests. Reading these receipts did not invoke any Android tool. No old APK was
downloaded or treated as a companion artifact.

Both inspected Linux jobs report image `ubuntu-24.04`, version
`20261025.353.1`; the Android job reports Temurin `17.0.21+9`.
The runner provisioning agent reports commit
`21505ad2541d5be6135ed84fc33697146cf75b8e`.
These are provider-reported run identities, **not** an immutable VM image digest,
hardware attestation or independently reconstructed toolchain.

[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) returned Actions
**degraded_performance**, incident `t89g2q1800fr`, investigating delayed/erroring
workflow starts (page updated `2026-11-05T16:52:52.715Z`).
This is an infrastructure observation, not a validation failure or permission to
count an absent run as passing. Local Git fetch failed on read-only Git metadata;
local GitHub CLI reads failed on socket policy. Connector reads succeeded. These
local access failures are distinct from the service incident; no security or
sandbox setting was changed.

Inspected sources: all three workflow definitions, build bootstrap/settings/
properties/module configuration, verification metadata, dependency/adoption
ledgers, ADR-0003 and its fifteen-failure history, requirements, governance,
provenance and acceptance rules. No private incident material was opened.

## Exact chain inventory and missing independent evidence

| Input / authority | Actual inspection | Qualification gap |
|---|---|---|
| Reviewed source and checkout | Main/tree above; official checkout `3d3c42e5aac5ba805825da76410c181273ba90b1`; exact event SHA; read-only contents; credentials not persisted | Independently approve source/tree/workflow and repository authority from a clean administrative endpoint. Git hashes bind bytes, not trustworthy authorship. |
| Linux host | Workflow selects `ubuntu-24.04`; observed image version above | Label moves. No immutable image digest, complete host package closure, provider attestation or independent provisioning receipt supplied. Container pinning alone would leave host/runner trust unresolved. |
| JDK | `JAVA_HOME_17_X64` selects runner installation; observed Temurin 17.0.21+9 | No fresh Linux archive digest/signature and trusted signer-root receipt qualified here. Existing Windows JDK checksum does not qualify Linux. |
| Gradle | 9.6.0 binary ZIP pinned to SHA-256 `bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01` in build.py | Existing pin is a repository observation. Fresh upstream checksum retrieval was not completed; archive endpoint could not be rendered by the web tool. Extracted directory is reused without rehashing its contents; archive checking alone does not bind an already extracted installation. |
| SDK platform | Requested `platforms;android-37.0`; prior ledger identifies revision 2 / extension 22 | Package name is not immutable archive identity. No newly acquired Linux SDK manifest/archive digest, complete installed-file manifest or rights receipt. The PR #57 stub hash is signature-surface evidence only. |
| Build tools | `build-tools;36.0.0`; AGP aapt2 `9.4.0-15978811` has classifier pins | Build-tools distribution and all executable/JAR inputs need independent acquisition identities. SDK aapt2 is not interchangeable evidence for AGP's Maven-selected aapt2. |
| AGP and Maven closure | AGP 9.4.0; XML contains 185 components / 322 artifacts with SHA-256, metadata verification enabled, signature verification disabled; official Google/Maven Central/plugin repositories configured | Ledger explicitly records some initial hashes from local cache/TOFU. Reacquire and independently authenticate complete Linux closure, including POMs/plugins/native classifiers; no new checksums generated from suspect caches. Existing inventory does not establish companion-specific completeness. |
| Build mode | Current module release is non-debuggable but uses `signingConfigs.debug`; debug and instrumentation variants also exist | This is a research signer, not qualified private companion custody. Separate Java-only module/configuration and release-equivalent inventory remain unimplemented. No native graph may be inherited. |
| Signing and verifier | No private signer or independent artifact verifier qualified | New isolated key custody, approved signing behavior, independent verifier identity, backup and transfer authorization missing. No existing Windows key may be reused. |
| Other tools | Git, Python, shell, OS libraries, TLS roots, runner agent and archive extractors participate in acquisition/build | Complete versions/hashes/licenses/security maintenance are not pinned by the workflow. NDK/CMake/JNI/payload tools are excluded from the companion, not silently counted as Java prerequisites. |

The bootstrap verifies a ZIP on every use but trusts an existing extracted Gradle
directory. This is a concrete source-level counterexample to “all executed tool
bytes are verified.” It is not evidence that any installation was altered.
Fresh extraction plus a verified installed-file manifest is a new falsifiable
qualification method; no cached-directory mutation or executable was run here.

## Acquisition, rights and maintenance boundary

[GitHub's runner contract](https://docs.github.com/en/actions/concepts/runners/github-hosted-runners)
describes new hosted machines for standard non-single-CPU jobs.
[Runner image documentation](https://github.com/actions/runner-images) identifies
moving image releases and included software. These upstream descriptions support
investigating separation from local disks; they do not establish absence of
provider compromise. This task did not start a runner or VM.

Android CLI is permanently excluded. The inspected Android workflow calls SDK
command-line installation/inspection tools and builds the native harness; it is
not an authorized ready-made route and was not dispatched. No CLI workaround or
renaming is proposed. For the same Linux candidate, a clean provisioning
custodian could evaluate the official
[Android Studio graphical SDK Manager](https://developer.android.com/studio/intro/update#sdk-manager)
as the acquisition step, recording exact packages, dependencies and license
acceptance before sealing the input set. This adds Studio/JBR and provisioning
trust to the inventory. Its exact version/digest and ability to supply the pinned
SDK without forbidden tools are **unverified**, not an approved installer recipe.
No copying of Windows SDK files or license-acceptance records is permitted.

[Adoptium's official Linux distribution](https://adoptium.net/installation/linux/)
provides an acquisition authority for JDKs, not a prequalified Linux archive here.
[Gradle checksum guidance](https://gradle.org/release-checksums/) supports comparing
distribution identities. The current checksum page did not expose the existing
pin in the retrieved text, and the exact checksum endpoint returned an unsupported
content-type; neither proves a mismatch. Versioned 9.6.0 verification documentation
was inaccessible to the web tool. Current
[dependency-verification documentation](https://docs.gradle.org/current/userguide/dependency_verification.html)
is conceptual guidance, not proof of the pinned version or executed closure.

Existing adoption records list JDK GPLv2 with Classpath Exception, Gradle/AGP
Apache-2.0, checkout MIT and mixed transitive licenses. POM declarations do not
audit bundled files. [Android SDK terms](https://developer.android.com/studio/terms)
and package notices require a competent custodian's acceptance/review; acquiring
tools does not establish redistribution rights. No tool archive, SDK image,
license file, APK, key or third-party implementation is added to GitHub.
The owner maintains the adopted research tools; the proposed new chain still needs
an assigned provisioning custodian, security reviewer and signing custodian.
They must track upstream advisories, archive exact provenance privately where
permitted, review every changed digest and invalidate affected evidence on update.
No current vulnerability clearance or source-to-binary reconstruction is claimed.

## Conditional private procedure, not executed or qualified

1. Owner designates an independently administered Linux provisioning endpoint and
   independent reviewer. They authenticate upstream releases and the exact GitHub
   source/tree from that endpoint, without using Windows credentials, remote
   sessions, files, caches or executable paths. Separately establish repository
   and workflow control; this chat's publication credential is not proof of that.
2. Custodian supplies a signed input manifest covering OS/runner, JDK, SDK,
   build tools, Gradle, AGP and all transitive binaries/metadata/licenses. Use
   empty homes, fresh extraction, an explicit tool path and isolated workspaces;
   reject inherited Gradle init scripts, Maven settings, shared caches and
   automatic SDK/dependency downloads after the reviewed acquisition stage.
   No APK assembly/signing is admitted at this qualification stage.
3. Independent reviewer checks the manifest and the controls below. A separate
   private signing endpoint must be provisioned and assessed independently too.
   Generate a dedicated research key there only after signing policy approval;
   never import a Windows/debug/production key or expose it to PR code. Record
   custody, access, encrypted backup/recovery and signer certificate privately.
   A new key is not generated or a signing-policy change authorized by this record.
4. Only after source/environment/security and an authorized reproducibility
   method are qualified may two separately initialized builds/signing operations
   be considered. Use the same approved signer and unchanged signing behavior,
   preserve original full outputs and verify signatures, certificate, manifest,
   DEX/native inventory, dependency metadata and exact whole signed bytes using
   a separately qualified verifier. No randomness change or normalization.
5. Keep every APK, signer record and confidential receipt in owner-controlled
   authenticated private storage outside public GitHub surfaces. No public
   Actions artifact, release, issue attachment, log dump or build scan. A future
   private transfer must authenticate both endpoints, encrypt transit/storage,
   restrict recipients, bind source/workflow/input/output identities and compare
   complete hashes at the recipient. Confirm backup and retention before cleanup.
   Secret masking is insufficient; GitHub's
   [security reference](https://docs.github.com/en/actions/reference/security/secure-use)
   warns redaction is not guaranteed. No private storage endpoint or access
   control has been demonstrated here.
6. Recipient verifies the packet independently before any later physical approval.
   This task performs no phone connection, ADB, USB, installation or execution.
   Owner approval and independent review remain required even after desktop
   qualification; a PR merge is not authorization.

The procedure defines obligations, not a verified private delivery service.
No existing signing material, private identifiers or confidential evidence was
read or transferred.

## Controls and precise falsifiers

| Property | Positive control required | Negative control required | Actual status |
|---|---|---|---|
| Source/input binding | Reviewer-approved full tree and manifest match independent acquisition | Change source SHA, workflow SHA, one tool byte or one manifest entry; reject before use | Exact repository identity inspected; acquisition controls NOT RUN |
| Extracted tool integrity | Fresh verified extraction and complete file manifest agree | Alter extracted Gradle script while leaving ZIP intact; admission must reject | Source inspection shows current bootstrap lacks this check; mutation NOT RUN |
| Complete dependency closure | Empty-home resolution matches reviewed graph; subsequent offline resolution has no new inputs | Remove a POM/classifier, inject init script, change artifact or enable undeclared repository; fail closed | Existing XML counted; independent Linux controls NOT RUN |
| Windows independence | Independent custodian verifies no imports, mounts, cached state or reused credentials/keys | Offer a harmless marked Windows-cache fixture or unapproved credential source; reject it | No imports performed by this task; full administrative chain Unknown |
| Private signing/transfer | Approved signer and recipient recover exact original fixture bytes over authorized private route | Wrong signer, substituted artifact, altered metadata, unauthorized recipient or leaked log fixture must block | Procedure only; no keys/APKs/transfer tests |
| Strict equality | Comparator accepts identical disposable fixture; later authorized genuine pair meets whole-byte assertion | Any byte change, append/truncation or metadata-only difference fails | Fifteen historical real failures retained; no new experiment |
| Receipt completeness | All mandatory steps bound to current source/run/attempt are observed | Missing, skipped, cancelled, timed-out, infrastructure-blocked or stale receipt remains blocking | Baseline jobs distinguished from new PR's unobserved checks |

Fixtures would establish only detector behavior. They cannot demonstrate
independent provisioning, genuine APK reproducibility, malware absence or phone
safety. No proposed control is represented as executed. The new falsifier targets
build-input independence and installed-tool integrity; it does **not** resolve
AGP's encrypted-metadata signed-byte blocker. Consequently this task does not
repeat any stopped APK experiment.

## Validation, preservation and next proof

Only this evidence and its index entry are proposed against exact main; regular
100644 text, no binaries, dependencies, workflow changes, trigger changes,
assertion changes, signing changes or new implementation. Original execution lock
and [ADR-0003 Option A](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md)
remain intact. All fifteen historical failures remain failures.

Local validation is evidence-document hygiene only, using existing Windows Python,
not an independent Linux qualification. Foundation validation passed with 156
files, 98 Markdown files, 54 requirements and three ADRs; harness source-manifest
validation passed. Repository regressions: 152 tests, 148 passed and four existing
Windows skips (not passes). Complete diff, local links, whitespace, text modes,
rights/provenance statements and public-data hygiene were reviewed. Git tree
comparison confirmed the only baseline changes since local main were the two
PR #57 documents; XML counting confirmed 185 components / 322 artifacts.
New PR CI is unobserved at the
required publication stop; foundation applies, unchanged Android and QEMU path
filters do not select this documentation-only change.

Initial checkout was clean, on older main, with one worktree and no stashes.
Existing branches, ignored assets and private records remain preserved.
The two PR #57 documentation files are synchronized from exact live main locally
for validation; publication uses the exact remote base tree, not the stale local
commit. No exhaustive ignored/private inventory or independent private backup is
claimed. GitHub APIs create the evidence commit because local Git metadata is
read-only; no permissions change is requested.

**Next proof and responsible parties:** the owner must appoint an independent
Linux provisioning custodian and reviewer to supply the missing immutable
acquisition/installed-file manifest and administrative-independence receipt,
including a CLI-free SDK acquisition demonstration, rights and private custody.
The reviewer must also identify a genuinely new method capable of resolving the
strict signed-byte blocker before any repeat artifact experiment. Without both,
the shortest legitimate next action is qualification evidence, not an APK build.
After those prerequisites, independent review can admit implementation of the
already described separate bounded Java diagnostic and its cleanup/error controls.
No new API or architecture survey is needed.

**Outcome: independent route NOT QUALIFIED; companion artifact NO-GO.**
Gate 0 remains Unresolved; Gates A–G remain Not reached.
Physical readiness remains **NOT READY — STOP**.
Publish exactly one evidence PR, attach it to this chat, verify association once,
then stop without polling CI, reviews, comments, bots or mergeability.
