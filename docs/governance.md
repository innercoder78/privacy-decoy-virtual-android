# Governance

PDVA has its own requirements and ADR sequence. The owner explicitly selected
the direction in [ADR-0001](decisions/ADR-0001-full-interactive-virtual-android-direction.md).
Acceptance selects an investigation, not an engine, feasibility, or a security
claim. The [requirements register](requirements.md) is the canonical obligation
set; topic documents explain those obligations. Evidence records observations
and cannot silently amend requirements.

Material changes to product scope, host privileges, guest platform/image policy,
primary boundary, networking contract, or evidence gates require a new PDVA ADR
and explicit project-owner approval. A PR merge alone must not be interpreted as
unstated approval to weaken these contracts. Record the owner decision, date,
alternatives, affected requirements, consequences and invalidated evidence in the
ADR. Requirements keep stable IDs; superseded obligations remain traceable.

Gate decisions require a reviewable evidence record identifying exact scope,
unresolved portions and the reviewer/owner disposition. Passing one candidate's
authority test does not pass complete-guest, usability or security gates. Failed
foundational evidence stops dependent implementation. Allowed outcomes are
**STOP**, evidence-backed **NARROW** with owner approval, or deliberate owner-approved
**REDESIGN** through a new ADR. More hooks or a privileged demo cannot substitute
for the selected contract.

The historical repository is read-only reference. Never import its Git history,
continue its numbering, or treat its roadmaps as a PDVA work queue. Re-adopt useful
concepts through PDVA obligations and revalidate their application.

All GitHub surfaces are public: source, branches, PRs, issues, checks, logs and
artifacts. Contributors must review evidence for sensitive data before upload.
The bootstrap grants no authority to publish production security claims or
redistribute proprietary packages. [Provenance review](source-provenance-policy.md)
precedes adoption, including build and CI dependencies.
