# ADR-0004: Gate 0 owner disposition

**Status: PROPOSED. Date: 2026-11-07, America/Fortaleza. Owner: Tony.**
**Choice: not selected. Approval/date: pending Tony's explicit decision.**
Publication or merge does not select either choice, accept another ADR, pass a
gate or authorize implementation. **Gate 0 remains Unresolved; Gates A–G remain
Not reached; physical testing remains NOT READY — STOP.**

## Decision requested

Choose **A: retain the full-phone requirements with dependent implementation
stopped**, or **B: commission a separately reviewed NARROW/REDESIGN proposal**.
B commissions a proposal, not its adoption. Until an explicit decision is recorded,
the existing requirements and immediate execution/implementation stops apply.
These choice labels are local to ADR-0004; ADR-0003's already approved Option A
is a separate, preserved decision.

This frames the [roadmap's outstanding owner question](../roadmap.md), using
the [integrated assessment](../evidence/gate-0-integrated-feasibility-decision.md)
and subsequent merged evidence. It does not replace that assessment, the
[gate criteria](../feasibility-gates.md), or the
[independent-build procedure](../evidence/gate-0-independent-linux-build.md).

## Evidence delta and remaining blockers

Reviewed canonical main: `f73949464a0e75b7d17fc5092f15346f52ccc6bd` (PR #64).
**Inference: the later evidence does not materially change the integrated Gate 0
disposition.** It improves bounded research/build controls, without qualifying a
complete ordinary-app Android 17 phone or independent hostile-worker enforcement.
R denotes the unchanged Cuttlefish reference phone; H denotes the researched
QEMU/TCG software-only mechanisms, not a selected or assembled configuration.

| Merged evidence | Established scope and present consequence |
|---|---|
| [#44 integrated assessment](../evidence/gate-0-integrated-feasibility-decision.md); [#51 authority delta](../evidence/gate-0-platform-authority.md) | Candidate-specific STOP for unchanged reference R: required host kernel-vhost authority is not established for ordinary apps; separate interaction/trust failures remain. The actual cross-built artifact lacks required device selections. Software-only H remains an unassembled hypothesis, not a failed test of every possible alternative. #51 found no qualifying new authority in its bounded review. |
| [#49 reservation](../evidence/gate-0-one-way-research-attempt.md); [#54 residual admission](../evidence/gate-0-first-attempt-residual-admission.md); [#55 links](../evidence/gate-0-first-attempt-links.md) | Observed, bounded admission corrections supersede old late-marker/reopen and filesystem-admission behavior. They do not establish authenticated freshness, independent enrollment, crash/restore recovery or revocation of surviving authority. Desktop filesystem results are not Android lifecycle results. |
| [#50 signed-APK preservation](../evidence/gate-0-apk-reproducibility.md) | Fifteen historical strict signed-byte equality failures remain failures. Later pairs localize differences to encrypted dependency metadata; historical plaintext equality remains Unknown. ADR-0003 Option A preserves metadata and strict equality; D1/D2 remain closed at STOP. |
| [#52 roadmap](../roadmap.md); [#53 physical procedure](../evidence/gate-0-first-physical-test-procedure.md); [#56 execution lock](../evidence/gate-0-research-execution-lock.md) | Owner disposition remains outstanding. The old conditional procedure is not an activation route: #56 unconditionally denies research execution before Session construction/reservation. Its trusted-management accident-prevention control is not hostile-worker containment. |
| [#57 Java memory candidate](../evidence/gate-0-java-memory-feasibility.md); [#58 independent build](../evidence/gate-0-independent-linux-build.md) | Public SDK mapping surface is a candidate, not physical mapping/execution evidence. Companion artifact remains NO-GO; independently administered provisioning, authenticated tool/input acquisition, signing/verifier custody and strict signed-byte qualification remain missing. |
| [#59 installed integrity](../evidence/gate-0-gradle-installed-integrity.md); [#60 ambient configuration](../evidence/gate-0-gradle-ambient-configuration.md); [#61 startup guard](../evidence/gate-0-gradle-startup-protection.md) | #59 corrects #58's specific unchecked extracted-Gradle reuse gap; #61 supersedes #60's no-correction statement only for its bounded startup subset. Whole configuration/cache/host/JDK trust and independent custody remain unqualified. Historical findings are not erased or represented as still-unfixed identical defects. |
| [#62 verification guard](../evidence/gate-0-gradle-verification-policy.md); [#63 fixed STRICT](../evidence/gate-0-gradle-strict-precedence.md); [#64 real runtime controls](../evidence/gate-0-gradle-strict-runtime.md) | Explicit override guards and fixed CLI selection now have ten real hosted Gradle 9.6.0 controls: correct bytes resolve; bad checksums fail despite project/user-home OFF/LENIENT; removing the trusted token restores weakened resolution. This supersedes #63's runtime NOT RUN for that fixture scope only. Installation-property mutation was not run. No APK equality, independent build/signing qualification or Android virtualization result follows. |

The five decisive obligations remain separate; success in one cannot discharge
another. The linked records retain their exact sources, artifacts and controls.

| Blocker and evidence classification | Required new evidence; decisive falsifier of the claimed route |
|---|---|
| Ordinary-app authority for a complete interactive Android 17 guest: R's scoped source/configuration contradictions are established; H's production authority remains Unknown. | A concrete allowed candidate, exact API/permission/device/helper authority and legitimate stock production access under Gate 0. Required root, platform privilege, production ADB, OEM-only grant or restricted VM workload substituted for the full phone rejects the route. |
| Coherent corresponding-source guest/backend/device build: current artifact/device mismatch is verified for that artifact; a complete alternative remains Unknown. | One selected, traceable product/kernel/module/firmware/device/HAL/backend graph, rights and build correspondence, including protected boot-state enforcement. Missing mandatory devices/peers, incompatible generated configuration, opaque critical inputs or rollback state controlled by the hostile worker rejects qualification. Separate favorable source rows are not an assembled system. |
| Independently enforcing hostile-worker containment and revocation: Android enforcement remains Unknown; reservation, Binder death and worker reports cannot supply it. | An enforcing authority outside the hostile worker, pre-exposure scope enrollment, independent whole-scope closure and loss/restore recovery evidence covering descendants, FDs, mappings and delegated resources. Surviving authority, protected-state access, restart over uncertain history or a boot decision the hostile CPU can ignore falsifies the proposed protection. |
| Physical executable-memory, lifecycle and resource feasibility: unmeasured, not a verified universal platform failure. | After separate readiness and owner authorization, exact-scope release-equivalent stock-device evidence for the selected execution strategy, lifetime, page/ABI behavior and declared memory/latency/thermal/battery budgets. Required prohibited fallback, failed cleanup, lost observation or exceeded budgets blocks that route. RX denial rejects the tested mapping strategy, not every interpreter; a mapping success would not prove TCG execution or containment. |
| Independent build/signing custody and strict signed bytes: chain NOT QUALIFIED; fifteen equality failures observed; future compliant resolution Unknown. | The existing independent-build qualification packet, named provisioning/security/signing reviewers, authenticated installed-input and configuration/cache manifests, authorized CLI-free acquisition, private custody/transfer/verification, plus a genuinely new method addressing the signed-byte blocker before any new artifact experiment. Shared unqualified inputs/custody, missing receipts or any whole-signed-APK byte difference rejects qualification. Normalized equality, valid signatures or Gradle success cannot replace it. |

Unsupported assumptions include treating Linux controls as Android authority,
combining H's source mechanisms as an implemented phone, assuming clean hosting
proves independent custody, and treating GUI/boot/checksum success as security.
No universal impossibility, new platform failure or new security claim is made.

## Owner choices and authorization boundaries

| Decision axis | A — retain requirements and stop dependent implementation | B — commission a NARROW/REDESIGN proposal |
|---|---|---|
| What Tony chooses | Keep the complete ordinary-app phone contract and accept the continuing stop while no new qualifying evidence exists. | Assign a proposal author/reviewer to present a concrete changed product/architecture contract for a later explicit decision. No replacement is chosen now. |
| Permitted | Preserve evidence; review genuinely new, exact-scope qualifying inputs under the roadmap and existing provenance rules. An independently useful evidence-only review needs no invented experiment or implementation queue. | Documentation and evidence analysis for the commissioned proposal: requirement-by-requirement changes, alternatives, authority/TCB, excluded capabilities, invalidated evidence, maintenance costs and falsifiable acceptance criteria. |
| Prohibited | Dependent complete-guest/production implementation, adopting unchanged R, treating H as assembled, or reopening blocked execution/build/signing/physical experiments. Repeated surveys or Gradle hardening merely for PR count are not next work. | Implementing the redesign, changing requirements or unlocking execution before separate approval. App virtualization, hooks, profiles, a headless VM or a simulated phone cannot silently become the product or satisfy the original full-phone requirement. |
| Evidence required to proceed | New evidence addressing the actual missing edge and its prior counterexamples, followed by scoped review/authorization. A Gate 0 pass still needs the existing gate criteria; dependent adoption and later gates retain their own prerequisites. Physical/build readiness remains separately blocking. | A coherent proposal showing exactly which obligations change, why the new scope is feasible enough to investigate, the independent enforcement owner, provenance and what prior evidence no longer applies. Tony must explicitly approve final changes through ADR review before implementation; evidence gates must then be re-evaluated for that approved scope. |
| Decisive falsifiers | Any applicable contradiction in the five-blocker table; missing evidence remains blocking Unknown. Failure of one candidate does not prove the entire product impossible. | A proposal that still requires unavailable authority, hides a removed product goal, retains an unsupported boundary claim, lacks corresponding source, relies on cooperative hostile code, or weakens a mandatory protection to claim progress is not approvable as satisfying the existing contract. |
| Next authorized owner action | Record explicit A selection/date and acknowledge the unchanged stop; identify a reviewer only when a genuinely new qualifying input is available. This is not an instruction to manufacture another experiment. | Record explicit B commissioning scope/date, proposal owner and reviewer. Require a separately reviewed final proposal and explicit acceptance/amendment decisions; commissioning alone authorizes no adoption. |
| Requirements / ADRs affected | All [PDVA-REQ-001–054](../requirements.md) remain intact, especially 001–015, 034–045 and 054. ADR-0001 stays Accepted; ADR-0002/0003 stay PROPOSED with only ADR-0003 Option A approved. | No requirement changes now. A future scope departure must trace 001/004/005/007/033/046–047 for full-phone, guest and interaction goals; 002–003/044–045 for host authority/support; 009–027/034–037/042–043 for boundary, privacy, networking and trust; 028–032 for Google goals. Apply 006/008/039–041/054 to approval and evidence. Explicitly amend/supersede affected ADR-0001 provisions; assess ADR-0002 delivery compatibility and ADR-0003 evidence obligations without auto-accepting either. |

Under B, dropping full-phone interaction, Android 17, required services, ordinary
stock-app operation, supported host scope, Persona features or Google objectives
would be an explicit product/requirements change, not an implementation shortcut.
The proposal must identify actual changes and retained obligations, not mark every
requirement optional. Guest device/backend or trust-owner redesign within the
same goals also needs concrete architecture/adoption review.

Under both choices, preserve hostile-code treatment; independent enforcing
authority and honest Unknowns; management/Persona/signing state separation;
narrow revocable interfaces; explicit Real disclosure and Decoy/Empty/Deny;
no genuine-data/GPS fallback; required VPN fail-closed behavior and no host VPN-slot
takeover; source/rights and image trust; no integrity/attestation/DRM bypass;
public-data hygiene and strict evidence. These protections cannot be silently
weakened. ADR-0003 metadata retention, whole-signed-byte equality and all fifteen
failures remain intact; D1/D2 are not reopened.

PR #56's unconditional research execution lock remains unchanged under either
choice. A future activation would require satisfied readiness prerequisites and
a separately reviewed owner-approved code change plus explicit physical-test
authorization; this ADR grants none. Existing independent-build and physical
procedures remain the prerequisite references, not new tasks authorized here.

## Review basis and preservation

Live REST verified main above and all open PRs: **zero**. Therefore open
heads/bases/full diffs/files/checks/jobs/logs/reviews/comments/threads were an
empty set. Merged identities #44 and #49–64 match local first-parent history;
requirements, all three prior ADRs, roadmap, linked evidence, provenance/adoption
and dependency inventories, tracked modes and all three workflows were inspected.
No new source survey or source/binary qualification was performed.

Exact-main [foundation run 42308760896](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42308760896)
and [Android run 42308760908](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42308760908)
had successful check/job/step records; completed logs were retrieved, including
the ten Gradle receipts at main. These are existing baseline observations, not
new experiments or validation of this ADR. Legacy status was pending with zero
contexts, not another running job. QEMU was not selected.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational and no incidents, page update `2026-11-07T04:29:17.751Z`.

Original documentation only; no production source, build, workflow, dependency,
binary, signing or security-policy changes. Existing branches, four worktrees,
ignored assets and private evidence are preserved; no independent private backup
is newly attested. No Android CLI, APK experiment, signing, native execution,
phone/ADB or VM activity was performed for this task. The existing foundation
workflow applies automatically to this documentation PR, including its unchanged
host controls; Android and QEMU path filters do not select these files. No
workflow is manually dispatched or changed, and filtered checks are not passes.

Local standard-library foundation validation passed: **165 files, 105 Markdown
files, 54 requirements, four ADRs**. Full diff, local links, requirement/ADR IDs,
regular text modes, whitespace and public-data review passed. No runtime tests
were needed for these three documentation files. New-head hosted checks remain
UNOBSERVED at publication. Publish exactly one PR, attach it to the current chat,
verify association once, then stop without polling CI/reviews/comments/bots or
mergeability. Association failure must be reported UNVERIFIED and UNPRESERVED
pending association repair, reusing the existing PR under [governance](../governance.md).

**Owner decision remains pending; no implementation is newly authorized.**
