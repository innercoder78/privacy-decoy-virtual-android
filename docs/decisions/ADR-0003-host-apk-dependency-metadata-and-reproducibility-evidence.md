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
