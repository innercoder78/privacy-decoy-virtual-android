# ADR-0002: Signed environment delivery and compatibility

**Status: PROPOSED.** **Date: 2026-10-08.**
**Owner: Tony. Approval: pending explicit approval after review of the final text.**
The request to document this proposal, a green check or a PR merge is not acceptance.
No owner acceptance date or accepted implementation choice is recorded.

## Context

Tony's product goals are a relatively small ordinary Android host APK, explicit
in-app provisioning of a separately delivered controlled environment, compatible
maintenance updates, and separate app/environment update discovery preferences.
These goals guide this proposal; their detailed architecture and enforcement
contract await approval and evidence. No APK/image size or storage budget is known.

[ADR-0001](ADR-0001-full-interactive-virtual-android-direction.md) selects full
interactive guest investigation, Android 17 / API 37 and one controlled image
line. It selects no production VM engine. The current
[isolated-worker harness](../evidence/gate-0-isolated-worker-harness.md) is substrate
research, without a guest runtime or physical results. Gate 0 is **Unresolved**;
Gates A–G are **Not reached**. Remote delivery does not resolve execution authority,
containment, Google compatibility or image qualification.

## Proposed decision and scope

Investigate a separate host APK and controlled guest environment. Use authenticated,
versioned release metadata to select an authorized image compatible with the
installed runtime and approved guest line. GitHub Releases is the preferred early
transport candidate; hosting identity is never the image trust root. Investigate
resumable independently verified parts where image size requires them.

The single detailed proposed contract is
[environment delivery and updates](../environment-delivery-and-updates.md).
It covers catalog trust, capability-based resolution, acceptance transitions,
separate discovery settings, provisioning UX, maintenance, migration and recovery.
Its mandatory acceptance condition, if adopted, is runtime support before download,
installation, update, restore or boot; user settings and alternate byte-delivery
paths cannot waive authentication, authorization or compatibility.

Investigate security and maintenance builds within Android 17 without automatic
major guest upgrades. Distinguish APK versions, runtime/device interfaces, guest
major line, image build and userdata schema. A future Android 17/18/19 chooser is
**DEFERRED**: it would require a separate owner-approved ADR, requirements revision,
maintenance/security policy and qualification of every supported line.

This documentation PR implements no UI, downloader, parser, verifier, self-update,
sideload installer or cryptographic key. It adopts no VM engine, QEMU, image format,
algorithm, dependency, guest binary or release asset, and publishes no release.
It changes no Android source, Gradle configuration, CI or validators. No phone,
ADB, emulator or physical-device work is required to review this proposal.

## Alternatives considered

| Alternative | Assessment in this proposal |
|---|---|
| Bundle the full guest in the host APK | Simpler first-run availability, but couples large payload distribution to APK updates. Package/storage/store feasibility remains Unknown; not the preferred investigation. |
| Separate signed environment via GitHub Releases | Preferred early candidate for the product goals; needs chunking, authenticity, availability, rights and lifecycle qualification. No permanent hosting commitment. |
| Store asset delivery or a dedicated hosting service | Future transport alternatives if policy, reliability or measured scale requires them; preserve the same acceptance contract. No service or store delivery mechanism selected. |
| Always use GitHub's global latest release | Reject as a resolver: chronological recency does not establish runtime, line, userdata or policy compatibility. |
| APK version alone, or user override of verification | Reject as acceptance authority: an app version is not a stable runtime/device interface contract, and user consent cannot authenticate an image. |
| Arbitrary ROM import or multiple guest major lines | Outside initial scope. No marketplace or version chooser is authorized here. |

## Consequences and security boundaries

Separating payloads could reduce host-package size and allow compatible image
maintenance independently of APK release cadence. That benefit is unmeasured.
Costs include first-use network dependence, staging/retention storage, metadata and
verification TCB, signing operations, recovery UX and ongoing support ownership.
Old app versions cannot be assumed perpetually maintainable; staying on a major
Android line does not justify a vulnerable image build.

Management owns catalog trust, acceptance and activation outside hostile guest
authority. Source/build provenance and redistribution rights remain prerequisites;
no proprietary Google packages may be redistributed without established rights.
AOSP feasibility and Play/GMS objectives remain separately gated. Authentication
and compatibility success do not prove containment or pass any feasibility gate.

## Affected requirements and future revisions

The [contract traceability](../environment-delivery-and-updates.md#requirement-traceability-and-evidence)
explicitly maps existing `PDVA-REQ-005`, `PDVA-REQ-008`, `PDVA-REQ-012`,
`PDVA-REQ-034`, `PDVA-REQ-035` and `PDVA-REQ-036`, with related control-plane,
Google, evidence, testing and UX obligations. The requirements register is unchanged;
this proposal adds no normative requirement or claim of satisfaction.

If accepted, a separately reviewed register revision should define delivery and
transition acceptance obligations, stable compatibility identifiers, independent
discovery preferences and consent, metadata freshness/revocation/recovery policy,
and provisioning/lifecycle UX with evidence criteria. Keep existing IDs and their
history. Multiple major lines would need their own later decision, not an implicit
revision of `PDVA-REQ-005` or ADR-0001.

## Unresolved choices and owner disposition

Unresolved: execution engine and qualified runtime/device contract; catalog schema,
signing algorithms, trust anchors, key roles/custody/rotation/recovery; image layout,
part sizes, storage budgets; authenticated ordering and anti-rollback persistence;
trusted time, freshness and offline authorization; migration/snapshot formats;
support periods, revocation response and maintenance owner assignment; app/store
update integration, hosting scale and source/redistribution qualification.

Tony must review the final ADR and linked contract, then explicitly accept, reject
or request revision. Record that disposition and date here before treating the
proposal as an accepted architecture decision. Even acceptance would not grant
implementation/adoption authority or change Gate 0/A–G status; those retain their
own scope, provenance and evidence reviews under [governance](../governance.md).
