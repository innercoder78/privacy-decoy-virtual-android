# Governance

PDVA has its own requirements and ADR sequence. The owner explicitly selected
the direction in [ADR-0001](decisions/ADR-0001-full-interactive-virtual-android-direction.md).
Acceptance selects an investigation, not an engine, feasibility, or a security
claim. The [requirements register](requirements.md) is the canonical obligation
set; topic documents explain those obligations. Evidence records observations
and cannot silently amend requirements.

Pending decisions include
[ADR-0003: host APK dependency metadata and reproducibility evidence](decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md).
It is a documentation-only proposal; no signing, CI or acceptance change is approved.

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

## Research preservation

Every research task MUST create or update exactly **one intended public-safe
evidence PR**, including positive, negative, failed, Unknown, STOP, source-only
and no-code outcomes. Record a substantive disposition, provenance, actual
validation, limits and reopening condition, cross-referenced from the
[evidence index](evidence/README.md). Reuse the intended PR after interruption;
do not create duplicate or content-free PRs, fabricate evidence or manipulate CI
to obtain a pass. A PR is not canonical until merged and independently verified
on main with the applicable checks distinguished from filtered/unrun workflows.

Private-sensitive details MUST remain in separately backed-up owner-controlled
private evidence; publish only a generic safe disposition. Ignored local storage
is not proof of independent backup. If private durability cannot be verified,
record a private recovery gap without exposing the material or its metadata.

On a hard publication or required association failure, STOP, report the precise
failure and mark the task **UNPRESERVED pending recovery PR or association
repair**, identifying any PR that already exists. Never create a duplicate to
repair association or imply that failure erased an existing GitHub record.
Completed chats may be archived after their durable disposition is verified, or
knowingly archived with a documented UNPRESERVED gap; keeping old no-PR chats
open is not a substitute for recovery. This rule governs preservation only and
does not change architecture approval, research authority or gate criteria.
