# ADR-0003: Host APK dependency metadata and reproducibility evidence

**Status: PROPOSED.** **Date: 2026-10-30, America/Fortaleza.**
**Owner: project owner. Option A approved: 2026-10-30.**
**Full ADR acceptance: pending explicit approval of its final text.**
The owner's explicit instruction in the existing PDVA conversation approves only
Option A. The remaining proposal stays PROPOSED; documenting, committing or merging
it does not accept the entire ADR or authorize implementation changes.

## Context and verified scope

The [existing PR #50 investigation](../evidence/gate-0-apk-reproducibility.md#dependency-info-observation-and-policy-proposal)
now localizes the remaining whole-APK mismatch to dependency-info signing-block
value `0x504b4453`. At diagnostic head
`b51d59d5c94f610bc04fba8d8808694f2d68e027`,
[run 40989682770](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40989682770)
and [run 40989678262](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40989678262)
each completed two genuine independent builds of candidate SOURCE
`aa517dfdfe2b72986d67ad65f7f1b34d8494118b`, TREE
`5965f746c6093c2bb86a99f3b4f361b6c315798c`.

**Direct observations from hosted logs:** within each pair, native objects,
unstripped/stripped libraries and build IDs match, as do every ZIP entry and its
contents, local records, central directory and EOCD. The v2 block, including
RSA-PKCS1-v1_5-SHA256 signatures, certificate/public key and signed data, matches;
verity padding matches. The 185-byte dependency-info value differs. Both complete
81,312-byte APK hashes differ and both Android jobs fail the strict assertion.
External apksigner verifies each original; each altered-signature copy is rejected.
Foundation and Windows checks passed. These scoped successes do not pass Android CI.

**Upstream documentation:** Android's
[dependency information for Play Console](https://developer.android.com/build/dependencies#dependency-info)
describes dependency metadata used for SDK/dependency issue reporting, recommends
retaining it, and describes compression, encryption and release signing-block
storage. Reviewed on 2026-10-30. The existing research record identifies pinned
AGP/apksig/Signflinger 9.4.0 sources and hashes; Signflinger inserts dependency
information separately from the v2 block.

**Inference and Unknown:** matching v2 signatures alongside a different metadata
value explains why signature validity cannot imply complete file equality.
The [bounded source investigation](../evidence/gate-0-apk-reproducibility.md#dependency-metadata-encryption-source-investigation)
establishes that the pinned AGP/Tink path uses P-256 ECIES, HKDF-SHA256 and
AES-128-GCM, with a fresh ephemeral key pair and 12-byte IV on each encryption.
No supported deterministic-retention mode was found for that configuration.
Actual historical plaintext equality, individual random values and exact runtime
causal isolation remain **Unknown**; source review is not a reconstruction of
those ciphertexts. Stop attempts to force equality through deterministic randomness
or ciphertext reuse. No universal impossibility claim for future schemes follows.

## Proposed decision and scope

**Selected direction: Option A, approved by the project owner on 2026-10-30.**
Retain dependency metadata in PDVA host APKs, preserve the existing strict
whole-signed-APK reproducibility requirement, and retain all observed failures
and unresolved limitations. Complete signed-byte equality remains unestablished.
Preserve the maintenance/reporting benefit while investigating honestly.
This proposal authorizes no build, signing, comparator, workflow or acceptance
change. **Current failing Android CI blocks merging PR #50 under existing rules.**
Neither this ADR nor passing documentation checks is a merge waiver.

These are separate evidence questions, not interchangeable definitions:

| Claim | Required evidence and present limit |
|---|---|
| Exact source/build-input identity | Record source/tree, configuration, dependency verification and actual tool inventories for independent builds. The measured inputs match; this is not proof that every environmental or random input is controlled. |
| Whole signed-APK byte identity | Compare both complete original signed artifacts, with the same signer within the pair. ANY real byte difference fails. Current pairs fail; no exclusion or normalized hash qualifies. |
| APK application-content identity | Explicitly enumerate all ZIP entry bytes, inventory/order/metadata and relevant native outputs. These match for the observed pairs. This limited result excludes no bytes from the separate whole-APK assertion and proves no runtime behavior. |
| Cryptographic signature validity | Qualified external verification of each artifact plus altered-signature rejection. Valid signatures authenticate the scheme's covered content; see the [AOSP v2 format](https://source.android.com/docs/security/features/apksigning/v2). Do not equate validity with equality of all signing-block pairs. |
| Signing-key identity and custody | Certificate/key fingerprints establish the observed signer, not exclusive custody, production authorization, rotation or recovery. The harness uses a development identity, shared within each pair; identities differ across runs. Production custody is unqualified. |
| Dependency provenance and maintenance | Immutable references, inventory/hashes, file-level licenses/rights, security history and assigned update ownership remain necessary. Encrypted metadata and Play feedback do not replace this review or prove vulnerability absence. |
| Security and distribution readiness | Require the applicable gates, rights, signing operations and physical/adversarial evidence. Neither content agreement nor valid signatures establishes safety, release readiness or supply-chain trust. |

## Alternatives considered

| Alternative | Benefits, costs and disposition |
|---|---|
| A. Preserve metadata and unresolved strict signed-byte claim | **Approved policy choice, 2026-10-30.** Retains upstream-recommended reporting and all evidence integrity. Leaves applicable CI failed and PR #50 blocked; no promise of a future byte-equality solution. Full ADR acceptance remains pending. |
| B. Disable metadata for a narrowly defined development-only artifact | Could isolate the metadata contribution, but success is unproved and cannot describe the metadata-bearing artifact. Requires separate owner approval of exact variant, audience, non-distribution controls, maintenance tradeoff, original-artifact comparison and positive/negative evidence. No configuration change is authorized here. |
| C. Disable metadata for distributed artifacts | **Not recommended.** Sacrifices the reporting channel to pursue a byte claim, with maintenance and distribution implications. Would require explicit distribution/security policy review and compensating evidence; no claimed equality benefit until measured. |
| D. Define a separate artifact-correspondence evidence contract | Could give useful positive evidence for source, application content and signatures despite a negative whole-byte result. Must name every covered/excluded field and limitation, retain raw artifact identities and the strict result, and have its own falsifiers. Cannot rename limited equivalence as complete reproducibility or silently replace required checks. Requires separate owner-approved contract and implementation review. |

**Options B, C and D remain unapproved.** A and a future separately approved D
could coexist. B or C would produce a different artifact policy, not repair the
historical comparisons. No alternative
permits stripping, copying, normalizing or replacing metadata/signatures to make
the original pair appear equal.

## Honest evidence and future CI reporting

This is a proposed reporting design only; existing CI is unchanged. A future
report could carry independent, explicitly scoped results for input identity,
ZIP/application-content correspondence, external signature verification, signer
identity and complete signed bytes, each bound to source, tools, both artifact
hashes, run/job IDs and controls. Positive results need actual completed checks;
negative results retain the violated assertion and evidence; missing execution,
unsupported structures or insufficient attribution are Unknown, never success.

The whole-byte assertion must remain a real failure whenever any bytes differ.
Malformed structures, changed signer, failed signature verification, changed
required inputs/content, or ineffective controls must fail their applicable checks.
A successful comparison test that detects an injected difference is a positive
*test-control* result, not a successful comparison of the genuine APK pair.

Separately labelled content/signature results can legitimately be positive when
their full stated scope passes, even alongside a negative byte result. A report
may explain all three states without changing the failed job's conclusion.
No continue-on-error, suppressed exit, skipped/path-filtered experiment, expected
failure conversion or passing umbrella status may hide an applicable failure.
Unknown cannot satisfy a required assertion. Any future change to which contract
is required for merging needs explicit owner approval and a separately reviewed
requirements/check transition; historical failures must remain failures.

## PROPOSED Option D contract: additive research correspondence

**Status: PROPOSED; Option D is not approved or implemented.** This section is the
decision-ready contract, dated 2026-10-30. Recommend **D1: additive, per-property
research reporting with the existing whole-byte assertion and merge block intact**.
It relies on the [existing evidence](../evidence/gate-0-apk-reproducibility.md), not
a new APK experiment or a new definition of reproducibility. Approval of Option A
does not approve this reporting contract.

### Evidence envelope and independence

Each proposed report must identify its schema/contract revision, experiment/run/job,
diagnostic source SHA, tested candidate SOURCE/TREE, build variant and ABI scope,
tool versions and actual inventories, dependency-verification/configuration hashes,
verifier identity, and both original complete APK sizes and SHA-256 values. Attach
per-result procedure, coverage, control outcomes, evidence links, limitations and
the emitting tool's exit status. A report is not a cryptographic attestation.

Build A and B must come from separate fresh checkouts/output and dependency homes,
with caches disabled and the same authorized signer within the pair. Bind every
measurement and verifier invocation to its original artifact hash; recheck identity
around measurement. Never substitute a mutation fixture, copy of A, retained APK
or imported JSON claim for independently built B. Distinct paths and matching
hashes alone cannot prove independence: retain build execution and source/input
records. The current pairs share a hosted runner/toolchain and trust domain;
they do not demonstrate independently operated builders or compiler diversity.

The following proposed result names are report labels, not new requirement IDs.
All positive results require an admitted envelope and completed controls. Builders
can recompute these properties when they possess both original artifacts and the
necessary inputs/intermediates; current public logs alone permit review, not a
fresh cryptographic verification or reconstruction of unavailable artifacts.

### Property coverage, existing evidence and required controls

| Proposed result | Exact comparison / demonstrated scope | Required positive and negative controls before reporting a positive result |
|---|---|---|
| `INPUT_CORRESPONDENCE` | Exact source/tree, configuration, resolved dependency inventories/verification policy and actual qualified tool inventories match. Demonstrated for the recorded pairs. Does not cover entropy, every environment input, source-to-tool-binary reconstruction or key custody. | Positive: recompute both complete inventories from the actual builds. Negative: changed source, tool/dependency/configuration hash, omitted field, stale receipt and reused build output must prevent a positive result. Same-path and copied-artifact controls cannot substitute for fresh-build evidence. |
| `APPLICATION_CONTENT_CORRESPONDENCE` | All ZIP entries: names/count/order, uncompressed bytes, recorded metadata including times/flags/compression/attributes/extra/comments/offsets; separately compare raw local-record, central-directory and EOCD regions. No DEX/resource/native exclusions. Demonstrated within recorded pairs. Covers these enumerated regions, not the signing block or runtime semantics. | Positive: validated identity fixture plus recomputation over both genuine APKs. Negative: mutate DEX/resource/native payload, add/remove/reorder an entry, change ZIP metadata/raw region or introduce duplicate/truncated entries. Each mutation must fail the affected result; metadata-only changes must not be described as changed application payload. |
| `NATIVE_OUTPUT_CORRESPONDENCE` | For both JNI ABIs, exact object, unstripped and stripped library hashes, section inventories/build IDs, and stripped-to-packaged bytes; inventory the separate ARM64 launch payload. Demonstrated for current measured scope, not every platform or native toolchain. | Positive: actual object/library inventory and packaged correspondence, with mapped replay controls. Negative: change an object, code/debug/build-ID section or packaged native byte; omit an ABI/output; remove a required mapping or security flag. No section normalization. Missing intermediates yield Unknown, not a source-to-native claim. |
| `SIGNATURE_VALIDITY` | Qualified external apksigner verifies each original APK under the required scheme policy. Demonstrated v2 validity; structural parsing alone is insufficient. This authenticates scheme-covered content, not every outer metadata pair or provenance. | Positive: both original verifier successes with exact artifact/tool identities. Negative: existing disposable altered-signature controls must cause the expected cryptographic rejection, not a missing-tool/parse/infrastructure error. Missing output, false scheme result or failed control prevents a positive result. |
| `SIGNER_AND_V2_CORRESPONDENCE` | Separately compare certificate/public-key identities, scheme set, algorithm IDs, complete v2 block, signed data/digests/attributes and signature bytes. Demonstrated same signer and RSA-PKCS1-v1_5 signature bytes within current pairs; not production authorization/custody or cross-run identity. | Positive: bounded parse bound to each externally verified leaf certificate and compare all listed fields. Negative: different signer/scheme/algorithm/signature, duplicate or missing mandatory record, malformed prefix or forbidden trailing bytes must fail the relevant comparison/admission. A valid differently signed APK may pass validity while failing signer correspondence. |
| `SIGNING_BLOCK_INVENTORY` | Inventory every outer ID/value pair, offsets/sizes/hashes and padding without ignoring unknown pairs. Current v2 and padding match; dependency-info `0x504b4453` differs. Report each field's equality explicitly; no overall signing-block-equality success is available. Plaintext equivalence and individual historical random inputs remain Unknown. | Positive: complete bounded inventory tied to originals and expected identities. Negative: changed/extra/missing/duplicate pair, changed padding, malformed size or unsupported interpretation must be detected. A dependency-info-only change must be reported as different; never infer plaintext equality from size, source pins or valid v2 signatures. Unknown IDs stay opaque and cannot earn semantic validation. |
| `WHOLE_SIGNED_APK_EQUALITY` | Both complete original signed files, including all signing metadata, must meet the unchanged strict comparator and signer policy. Repeated genuine result: **FAIL**. No reduced, normalized or unsigned digest may replace this result. | Positive test control: equal disposable fixture admitted by the comparator, labelled fixture-only. Negative: any real byte mutation, append/truncation or artifact/report substitution must reject equality. Genuine success requires two independent real signed builds satisfying the unchanged check; the positive fixture proves no such result. |

Existing synthetic and hosted controls support parts of this matrix, but the
future reporter's envelope binding, every per-result mutation mapping and complete
fail-closed behavior have **not** been qualified as a new D contract. They require
implementation review and tests after approval. No control is claimed executed
merely because it is specified here; no new build is needed to decide this proposal.

### Fail-closed result and reporting rules

Each result carries `PASS_FOR_SCOPE`, `FAIL` or `UNKNOWN`, an explicit scope and
reason, plus `evidence_admission=VALID` or `REJECTED`. These are proposed labels.
Malformed, duplicate, inconsistent, truncated or substituted evidence is REJECTED
and fails evidence admission; missing/unsupported/unexecuted proof is UNKNOWN.
UNKNOWN or REJECTED never satisfies a mandatory assertion. A failed verifier is
FAIL for validity; an unavailable verifier makes validity UNKNOWN and fails the
mandatory verification prerequisite. A control that fails to detect its injected
defect invalidates the associated positive claim. Do not retain an aggregate pass
when prerequisites or controls are missing.

Recompute from originals rather than trusting imported result booleans. Reject
ambiguous schema versions, mismatched artifact/tool identities and stale run links.
Bounds and parser policy remain fail-closed; no inferred field identities, silent
discard or accepted arbitrary padding. Do not manufacture missing artifacts from
logs. Privately retained inputs require authorized custody and access; public
reports contain reviewed hashes and bounded facts, not keys, private paths or raw
sensitive reports. Hash correspondence relies on the stated hash assumptions and
trusted tools; neither it nor this envelope supplies supply-chain attestation.

A future summary for the observed kind of pair would read: research build A/B
completed; measured input/application/native correspondence PASS_FOR_SCOPE;
signature validity and signer/v2 correspondence PASS_FOR_SCOPE; dependency-info
values DIFFERENT; metadata plaintext correspondence UNKNOWN; whole signed APK
equality FAIL; mandatory Android outcome FAIL; merge BLOCKED; release readiness
NOT ESTABLISHED. This is an illustrative report, not executed D implementation.
No umbrella "reproducible", "secure" or "ready" status is permitted.

Research findings answer a bounded question and preserve negative outcomes.
Release/distribution requirements need their own approved artifact, custody,
provenance, rights, maintenance and gate evidence; this research contract cannot
satisfy them. Mandatory signature, APK policy, native protection and provenance
checks remain mandatory regardless of a content match. Whole-byte reproducibility
and limited correspondence are distinct results, and neither passes Gate 0.

### Smallest alternatives, requirements and merge consequences

| Alternative | Approval and requirements effect | PR #50 consequence and risk |
|---|---|---|
| Retain current reporting under A only | Already selected policy; no Option D implementation. PDVA-REQ-036–041, 048, 051 and 054 continue unchanged. | Honest existing negative evidence is sufficient to retain STOP. PR remains blocked; less structured presentation, no extra implementation trust. |
| **D1 — PROPOSED, recommended: additive report with A intact** | Separately approve the exact envelope, coverage/control matrix and bounded research-only implementation. Elaborates PDVA-REQ-039/040 evidence, 036/037 provenance, 041/042 security limits, 048 privacy and 051 validation. No obligation is waived or marked satisfied; 008/054 governance and approved A remain intact. | Existing strict failure/exit/check and merge blocker remain. No applicability, workflow or merge-rule change is needed for this documentation or inherently required for a supplemental report; any future workflow edit still needs review. Costs: reporter/parser trust and risk of readers mistaking scoped passes for full equality. |
| D2 — PROPOSED for decision comparison only, not recommended here: make limited correspondence sufficient for research merging | This would change the current required merge contract and cannot preserve A's present whole-byte merge prerequisite intact. Requires explicit reconsideration of that part of A, dated governance disposition under PDVA-REQ-008/054, and separately approved precise research acceptance/required-check revisions. Must reassess 036, 039/040 and 041/042; no implicit supply-chain or security satisfaction. | Cannot be applied to finish PR #50 under existing authorization. Any future legitimate transition must state what obligation changes, why research-only acceptance is adequate, what remains failed, and how every test continues to run with honest outcomes. Making the same applicable failed assertion green, hiding/removing it or merely relabelling the job is not legitimate. No such transition is designed or authorized by this proposal. |

PDVA-REQ-034/035 concern guest-image supply chain/lifecycle and are **not** host-APK
merge waivers. PDVA-REQ-050's foundation scope and its existing reviewed Android
research extension are not broadened here. All alternatives leave production
security boundaries and guest obligations untouched. The exact current host
whole-byte/merge obligation comes from approved Option A and existing experiment
acceptance, not an invented claim that the register expressly mandates identical
host APKs under PDVA-REQ-034. The register is unchanged; a future material policy
revision must preserve stable IDs and traceability rather than silently edit history.

**Merge answer:** completing and publishing this research proposal does not require
a CI-rule change; merging PR #50 while the applicable strict assertion fails
cannot be achieved under A's current rules. D1 does not solve that blocker. No
approved secure deterministic configuration has been established to satisfy the
existing condition. A decision to revise a merge obligation is a separate owner
policy decision, not a technical fix justified by a negative experiment.

**Minimum next owner decision, still pending:** explicitly approve or reject D1's
exact scope, envelope, result meanings and control matrix, and separately authorize
its bounded implementation with A's strict failure and merge block preserved.
Full ADR acceptance needs explicit final-text approval; approving D1 alone must
not be recorded as accepting unrelated portions. If the owner instead seeks a
merge-rule transition, require a separate explicit decision identifying the exact
part of A being reconsidered and the replacement obligations before implementation.
This request to prepare the proposal approves none of those choices.

### Research-only merge decision: STOP under current authority

**Recommendation, 2026-10-30:** retain A and the negative research on OPEN PR #50;
D1 remains the recommended additive reporting direction, subject to approval.
There is no merge path that both preserves A's current merge prerequisite and
accepts this failed pair. D2 is a policy amendment for owner consideration, not
a reproducibility fix or an authorized implementation. The following narrows
the decision without replacing the contract/control matrix above.

| Question | Honest outcome and consequence |
|---|---|
| Are the two complete original signed APKs identical? | No for the observed pairs. The strict assertion and its nonzero failure remain genuine, including when only encrypted dependency metadata differs. |
| Does the comparator correctly detect differences? | Passed controls support that bounded tool behavior. Identical fixtures must pass and mutations must fail; this says nothing positive about equality of the real pair. An unexpected exception is not successful difference detection. |
| Is the negative research worth preserving? | Yes: it records a falsified equality claim and a source-established randomized encryption mechanism, with historical plaintext/random values Unknown. Preservation is already required; it does not authorize merge. |
| Which CI obligations must succeed? | Every applicable foundation/Windows, build/JVM/lint, APK policy, native/security, signing, provenance and comparator-control obligation. Today the combined Android job also requires strict equality and genuinely fails. |
| Is the research production-qualified? | No. Content/v2 agreement, valid development signatures and accepted research records cannot qualify releases, key custody, supply-chain reconstruction, containment or any gate. |

**Exact D2 policy change for a separate decision:** allow preservation-only
merging of this reviewed PR's negative research despite its visible strict
whole-signed-APK equality failure, conditional on independent review of the
complete PR and successful mandatory controls. This would replace **only A's
requirement that this equality assertion succeed before this research PR merges**.
It would retain metadata, the unchanged complete-byte assertion and every failure,
and would grant no release, adoption, device or production qualification. It
would not make limited correspondence sufficient by itself. This conflicts with
an approved part of A; it cannot be described as implementing A unchanged.
No such exception is approved here, and no general exception for future PRs is
proposed. PR #50 also contains earlier comparator, CMake and workflow changes;
calling this revision documentation-only does not exempt that accumulated code
from review or validation.

**Checks and controls before any separately authorized implementation:** an
independent reviewer must map every existing job/step and obligation to its
enforced outcome, using the envelope and positive/negative controls above.
The current combined Android job cannot simply become optional: that would
also waive its security/build failures. Any future separation must demonstrate
that each security, signature, input/provenance, malformed-evidence and control
failure still blocks merging; missing, skipped, stale or Unknown mandatory
evidence must also block. Review exact-head binding, permissions, triggers,
dependencies between jobs and enforcement, not just check names. Preserve
applicable test execution and coverage; moving code cannot drop a check or turn
a prerequisite failure into an accepted negative experiment.

The real comparison must still execute when applicable and report failure for
different bytes. Reject catching that failure as an expected-success result,
continue-on-error, suppressed exits, a green replacement/umbrella status,
retained/synthetic APK substitution, renamed conclusions, or applicability changes
that hide the experiment. A future explicitly approved policy could permit a
merge **with a visible failed research assertion**, never report all checks passed.
A separately passing evidence-integrity control must prove its own stated scope;
it cannot replace or certify the failed equality assertion. No workflow/check
arrangement or enforcement transition has been implemented or qualified here.

**Owner decision required:** explicitly approve or reject this narrowly scoped
D2 exception, identifying the superseded A merge clause and the exact final
research acceptance text. Approval must separately name the mandatory control
and required-check mapping and authorize its implementation/review before any
change; a general wish to preserve research, D1 approval or PR merge is insufficient.
Full ADR acceptance remains a separate final-text decision. Until those decisions
and qualification are complete, **STOP: PR #50 stays blocked**. Failure of any
mandatory control, unreviewed code/provenance, missing approval or misleading
reporting must continue blocking even under a future D2 exception.

Affected policy: A's host research merge prerequisite and its governance/check
mapping under PDVA-REQ-008/054; evidence obligations 039/040 and validation 051.
Review 036/037 supply-chain adoption, 041/042 security limits and 048 privacy as
non-waivable prerequisites; 034/035 guest release obligations and 050's existing
scope remain unchanged. No requirement is satisfied, weakened or superseded by
this proposal. The governance preservation duty requires a substantive PR, not
automatic merging of a failed applicable check.

Risks/falsifiers: an optional combined job, omitted prerequisite, stale receipt,
green summary concealing failure, or acceptance of an injected security/control
failure rejects the proposed arrangement. Opaque metadata semantics and mutable
runner trust remain unresolved. A new difference outside the documented metadata
scope invalidates that pair's scoped explanation and requires review. Reopen
technical experimentation only for a new falsifier; unchanged repeat builds do
not resolve this policy decision. GitHub merge-button availability is not owner
authority, and a research merge would not advance Gate 0 or production work.

#### D2 enforcement design assessment — 2026-10-31

**Disposition B: STOP.** The smallest candidate is a separation of mandatory
controls from the still-failing equality assertion, but a required-check list
alone cannot enforce the requested failure semantics. No qualified independent
enforcer exists in this repository. This is a concrete rejected minimum and a
bounded qualification plan, not a claim that every future design is impossible.
The owner authorized investigation/design only; A, D1/D2 and ADR status are unchanged.

The mapping below covers every step in the existing
[Android workflow](../../.github/workflows/android-harness.yml), including generated
runner steps. M1 and M2 are proposed obligation groups, not installed check names.
Every mapped control remains mandatory independently of equality's result.

| Existing step | Precise obligation and proposed mandatory destination |
|---|---|
| Set up job | M1: qualified Ubuntu runner, successful initialization and recorded infrastructure identity; a zero-step run is not evidence. |
| Check out exact reviewed source | M1: immutable official checkout pin, exact PR head, complete historical source availability, no persisted credentials and no destructive checkout. |
| Repository and manifest hygiene | M1: foundation roots/links/requirements/binary/privacy rules, manifest authority validation and head whitespace. |
| Select runner JDK and install pinned Android packages | M1: JDK selection, executable SDK tools, requested platform/build-tools/NDK/CMake and recorded versions/hashes. Package IDs alone do not pin mutable runner bytes; M2 adds exact qualification/inventories. |
| Build both variants and exercise protocol | M1: debug/release/test APK compilation, JVM protocol tests and debug lint through the existing hash-verified Gradle bootstrap and strict dependency verification. No Android runtime execution is implied. |
| Cross-build and inspect dormant seccomp bootstrap without executing it | M1: native cross-compilation and static bootstrap controls; preserves the no-execution boundary. |
| Inspect release APK authority and native inventory | M1: release/debug compiled APK policy, packaged extraction-rule negative controls, expected native inventory/protections and recorded source/tool/APK hashes. |
| Record offline release artifact correspondence privately | M1: exact-head/artifact-bound journal init/prepare/inspect, native-to-packaged correspondence and private evidence handling. A receipt is not physical readiness. |
| Exercise independent APK comparison failure controls | M1: all existing comparator/parser/mapping controls; fixture equality and rejected mutations test the tool, not genuine build equality. |
| Build exact reviewed candidate twice: qualification/build portion | M2: hosted-Linux restriction, exact JDK/package revisions and full tool hashes; pinned SOURCE/TREE; fresh separate worktrees/dependency homes, disabled caches, both successful builds and unchanged tool installation. |
| Same step: signing/native/provenance portion | M2: external apksigner verification of both originals, bounded parser/certificate binding, altered-signature rejection, APK/ELF inspection, mapped compiler replay and unmapped negative controls, strip/build-ID/packaged-byte consistency, complete matching input inventories and same signer/schemes. |
| Same step: comparison portion | M2 must independently validate the result binding, same signer and the narrow metadata-only difference scope from both originals. The separate research assertion R still compares complete original signed bytes, rejects ANY difference and exits nonzero. No parser/input/signature exception qualifies as R's expected scientific outcome. |
| Post checkout / Complete job | M1/M2: verify terminal execution and cleanup outcomes; successful runner finalization cannot override a prior failure. Cancellation or missing terminal evidence blocks. |

Existing `foundation` and `offline-image-windows` also remain required in any
candidate mapping. Preserve foundation repository/comparator/receipt/image/frame
tests, harness validation, native wait/assertion controls, modeled bootstrap,
Linux lifetime/seccomp/revocation controls and whitespace; preserve Windows
image/frame controls. Their success cannot compensate for any M1/M2 failure.

**Smallest candidate and rejection:** require those two existing jobs plus M1
and M2; let only R remain visibly failed and non-blocking under a PR-50-only
owner exception. This needs a future reviewed separation inside the current
monolithic script, not merely moving its last workflow step. Original APKs must
stay bound to the same fresh pair across M2/R with identity rechecks; job separation
adds transfer, retention, signing-material and substitution risks. No artifact
upload or new dependency is authorized. The existing script cannot currently
emit independently enforced M2 success and R failure; its common exit 1 also
represents genuine build/security/parser errors. Classifying that exit or STOP
message as acceptable, or replaying retained APKs, is rejected.

**Independent platform assessment:** GitHub accepts `success`, `skipped` and
`neutral` for required checks; a conditional skip can therefore satisfy protection.
A dependency-skipped job may not block. Filtered workflows instead leave required
checks pending. Required checks bind to the current head or test-merge commit;
merge queues need their own event coverage. These are documented semantics,
not newly tested PDVA enforcement. See
[required-check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
and [conditional jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions),
reviewed 2026-10-31. Requiring R would block its genuine failure; making R optional
does not require its execution or distinguish a scientific mismatch from a crash.

| Outcome | Required decision; gap in the minimum candidate |
|---|---|
| Mandatory failure, timeout, cancellation or action-required result | Block; never neutralize or retry merely for green. Verify actual protection enforcement, not just a red icon. |
| Missing, queued, in-progress or Unknown mandatory evidence | Block; no receipt or job name can substitute for completed checks. |
| Skipped/neutral job or skipped required step inside a successful job | Block despite GitHub's accepted job conclusions; requires independent execution/coverage validation absent from a simple required-check list. |
| Old head/base, wrong source/tree, wrong run attempt or stale/cross-run artifacts | Block; bind diagnostic head, build candidate, base, workflow identity and both artifact hashes separately. A historical candidate build does not validate current-head code. |
| R missing, skipped, timed out, cancelled or crashed before a complete comparison | Block; an optional R alone cannot enforce this condition. Generic exit 1 is insufficient. |
| M1/M2 actually succeed and R completes with only the documented metadata difference | Retain R FAILED. Only a separately approved, qualified D2 policy could permit research preservation; no all-green or reproducible claim. |
| New content/native/signer/v2/padding difference, or unexpected genuine equality | Stop this narrow exception for review; preserve the actual result. Equality for one pair would not erase previous failures. |

Closing the gaps would require an independent, trusted execution/evidence
validator with its own substantive controls, plus enforced review of workflow
integrity. It must not be a wrapper translating R failure into success. Merely
adding `always()` does not prove coverage or prevent its own skip/cancellation.
No such validator, trusted source or permissions/adoption decision is qualified.
An external check producer would add a new trust/maintenance obligation, not a
free workaround. GitHub supports expected-app binding, unique check names and
admin protection, but the Actions app identity alone does not identify an immutable
workflow. See [branch protections](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
Live main has no classic protection or active rulesets; project policy still
blocks. Future controls must include administrators, prevent direct-push/bypass
routes and enforce current reviews. A malicious rules administrator remains a
trust limit. No settings were changed, and no manual merge bypass is proposed.

**Independent qualification plan, not executed:** a reviewer other than the
implementer must first trace each row to exact code/checks and approve provenance,
permissions and artifact handling. Before production-repository enforcement,
use an owner-authorized isolated test setting to demonstrate actual merge denial
for each injected M1/M2 failure; missing/skipped/neutral checks and steps; timeout,
cancellation and unavailable runner; wrong SHA/base/attempt/producer; duplicate
check names, forged receipts, replaced APKs and changed workflow/trigger. Include
direct push/admin bypass, stale approvals, base updates and a non-#50 PR to prove
the exception cannot escape its scope. No such setting or test is authorized now.
Positive controls must demonstrate genuine mandatory execution and authentic
completed comparison evidence; only the separately approved exception may admit
a still-red R. Reuse the contract's byte/signature/parser mutations without
substituting fixtures for independent builds. Verify R remains visibly FAILED
in the checks UI/API and logs. An enforcer outage must block, not default success.
This qualification tests new enforcement falsifiers; it is not permission to
repeat the unchanged APK experiment. Missing proof in any row means STOP.

**Proposed replacement owner text, NOT APPROVED and NOT EFFECTIVE:** "For PR #50
only, at a separately reviewed final head/base and approved enforcement revision,
I amend only Option A's equality-before-research-merge prerequisite. Preservation
may proceed with the complete signed-APK assertion visibly FAILED for the reviewed
dependency-info-only mismatch, only after every mapped mandatory control actually
executes successfully, independent qualification proves fail-closed enforcement,
and the complete accumulated PR receives current independent review. Metadata,
strict byte comparison, all historical failures and production/security/release
obligations remain unchanged. No other PR or failed/Unknown mandatory protection
is excepted. Missing qualification keeps the merge blocked. This approves neither
the whole ADR nor merging now; implementation scope and enforcement changes need
separate explicit authorization."

This is the exact proposed conflict with A, not an accepted amendment. It affects
the already mapped 008/054 governance, 039/040 evidence and 051 validation policy;
036/037, 041/042, 048, guest 034/035 and existing 050 scope remain intact. Full
ADR acceptance and D1/D2 remain unapproved. The ten-file accumulated PR includes
615 lines of comparator/diagnostics, 537 test lines, validator allowlisting,
workflow history/trigger/control additions and four CMake debug-map lines, as well
as documentation. Earlier path-mapping/parser evidence supports their bounded
behavior, not enforcement separation or source-to-binary supply-chain qualification.
Do not remove the branch-specific trigger to hide failure. Whole-PR review must
cover these changes, retained security flags, parser bounds and source pins.
No production adoption, gate advancement or native-launch readiness follows.

## Acceptance criteria, residual risks and falsifiers

Before any implementation, require all of the following:

1. Record the owner's dated acceptance, rejection or requested revision of this
   exact ADR; identify selected alternatives, artifact scope and remaining Unknowns.
   The recorded approval of A alone retains the present check and merge block.
   B, C or D needs its own explicit scope and implementation authorization;
   no implicit CI waiver.
2. For D, approve the precise evidence schema, field coverage/exclusions, failure
   and Unknown semantics, reviewer responsibility and relationship to merge rules.
   For B/C, approve exact variants/distribution boundaries and the maintenance loss.
   Review any affected requirement change with stable IDs and preserved history.
3. Preserve two genuine independent build directories/dependency homes, recorded
   source/tool/configuration identities, same signer within each pair, original
   complete APK hashes and external verification. Retain all historical failures.
4. Demonstrate positive controls and negative mutations for covered content,
   metadata, signatures, signer identity, malformed/truncated structures and
   incomplete/substituted evidence. A metadata-only mutation must still fail the
   whole-byte assertion even if separately scoped content checks pass. Neither
   synthetic fixtures nor retained identical APK copies replace real builds.
5. Review privacy, dependencies, licenses, security protections and required
   coverage; define a repeatable qualified hosted experiment and stop conditions.
   No production key, device execution or distribution is authorized by this ADR.

Falsifiers: any additional changed field invalidates the metadata-only explanation
for that pair; input drift invalidates its same-input premise; an ineffective
signature/content mutation control invalidates the associated positive evidence;
disagreement between parser and qualified verifier requires STOP and investigation.
A genuinely equal independent pair would establish equality for that pair only,
not rewrite earlier failures or prove universal determinism. A controlled experiment
that contradicts an encryption hypothesis requires revising that hypothesis.

Residual risks include mutable hosted infrastructure, incomplete control of
environmental inputs, dependence on pinned parsers/verifiers, opaque metadata
semantics, unavailable original unsigned signing inputs, and unqualified production
key custody. Metadata retention does not guarantee Play detects every dependency
issue; independent provenance, vulnerability response and maintenance remain needed.
No secure/reproducible upstream binary reconstruction is asserted.

## Requirements, host/guest boundary and owner disposition

This proposal interprets evidence questions under [governance](../governance.md),
[source policy](../source-provenance-policy.md) and
[acceptance criteria](../acceptance-evidence-criteria.md). Related obligations are
PDVA-REQ-036 and PDVA-REQ-037 (provenance), PDVA-REQ-039 through PDVA-REQ-042
(evidence/security), PDVA-REQ-048 (privacy), PDVA-REQ-051 (validation) and
PDVA-REQ-054 (gated progress); PDVA-REQ-034 and PDVA-REQ-035 remain separate guest
image/lifecycle obligations. The requirements register is unchanged and no
obligation is marked satisfied or superseded.

Host APK dependency metadata is build/distribution information. It neither adds
Google Play to the future guest nor supplies Google software rights, guest Play
compatibility, certification or attestation. The independently gated
[Google compatibility objective](../google-compatibility.md), ADR-0001's runtime
direction and ADR-0002's proposed delivery scope remain unchanged. No VM engine,
guest architecture or product boundary is selected or modified.

**Owner disposition, 2026-10-30:** Option A is explicitly approved, as recorded
above. This is approval of that specific policy choice, not acceptance of this
entire ADR. No approval is granted to disable metadata, modify signing behavior
or algorithms, ignore/normalize/exclude differing bytes, weaken/suppress/skip CI
failures, change merge requirements, adopt B/C/D, claim whole-APK reproducibility
or merge PR #50.

**Still pending:** explicit approval of the final ADR text and any separately
scoped implementation. A future Option D evidence contract and any change to
required CI/merge criteria each need separate explicit owner approval. B and C
also remain unapproved. Status stays PROPOSED for all unapproved portions;
metadata remains enabled, strict CI remains applicable and PR #50 stays OPEN
and blocked. No failed assertion is reclassified as a pass.

Gate 0 **Unresolved**; Gates A-G **Not reached**. Windows native-host security
incident remains unresolved. Physical native-launch readiness **NOT READY — STOP**.
No phone, USB, ADB, emulator, guest execution or antivirus bypass is authorized.
