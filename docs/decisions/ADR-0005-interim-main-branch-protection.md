# ADR-0005: Interim main branch protection

**Date: 2026-11-17, America/Fortaleza. Owner: Tony.**
**Status: APPROVED INTERIM DIRECTION; final technical implementation pending
review. GitHub enforcement NOT ACTIVATED.**

Authority is Tony's explicit 2026-11-17 decision, preserved in
[PR #82](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/82),
and his subsequent instruction to complete the ADR, bounded source admission,
security tests and activation procedure together in one substantive PR. This
authorizes repository preparation and publication. It does not invent approval
of previously unreviewed implementation bytes or authorize administration.
After successful review and merge, the next operation is separately authorized
GitHub enforcement testing and activation; no additional planning PR is required.

## Decision and scope

Require PRs and genuine universal Foundation/Windows checks before main updates,
strict current-base checks, non-fast-forward protection and deletion restriction,
with no bypass actors, including administrators. Require **zero independent
GitHub approvals for now**, because no eligible independent reviewer is available.
Preserve ordinary authorized PR merges and all three existing merge methods.
Complete ChatGPT review remains mandatory before every merge. That obligation
is manual and is not enforced by the approval count.

This addresses repository governance only. Traceability: PDVA-REQ-008, 010,
036–043, 048–051 and 054 in the [requirements](../requirements.md), together with
[governance](../governance.md), [source policy](../source-provenance-policy.md)
and [evidence criteria](../acceptance-evidence-criteria.md). No requirement is
relaxed. The full interactive Android 17/API 37 phone in an ordinary stock
nonrooted user-installed app remains the goal. Gate 0 is Unresolved; Gates A–G
are Not reached. Containment, revocation, privacy, Persona, networking/VPN,
guest completeness and host authority obligations are unchanged.

## Exact configuration for subsequent authorized administration

The following is the complete intended create-ruleset body, not an instruction
to submit it during this PR. The
[GitHub REST schema](https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset)
was checked on 2026-11-17. Use the documented API version `2026-03-10` and
`Accept: application/vnd.github+json` on the subsequent operation. Creation
requires Administration: write. Exact server acceptance, defaults and normalized
readback remain NOT TESTED until the disposable-branch procedure below.

```json
{
  "name": "main-review-and-ci",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {
    "ref_name": {"include": ["refs/heads/main"], "exclude": []}
  },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "allowed_merge_methods": ["merge", "squash", "rebase"],
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_approving_review_count": 0,
        "required_review_thread_resolution": false,
        "require_extra_approval_for_unattributed_changes": false,
        "required_reviewers": []
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "required_status_checks": [
          {"context": "foundation", "integration_id": 15368},
          {"context": "offline-image-windows", "integration_id": 15368}
        ],
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false
      }
    },
    {"type": "non_fast_forward"},
    {"type": "deletion"}
  ]
}
```

App 15368 was freshly observed as `github-actions` on both exact-main check
runs. Reconfirm at activation. Do not substitute any-source status checks.
Explicit values avoid reliance on defaults for approvals, freshness, branch
creation or bypass. No dismissal restriction is requested; inspect any server
defaults, including newly introduced fields, for equivalent behavior. A rejected
field, unsupported combination or conflicting default means STOP/Unknown;
do not silently drop fields or improvise another configuration.

Do not add Restrict updates (`update`), mandatory reviewers, code-owner or
last-push approval, signing, deployments, creation restrictions, linear history
or merge queues. `update` with no bypass can block legitimate merges. Existing
repository merge/squash/rebase availability must remain unchanged.

## Enforcement limits and review obligations

Before every merge, ChatGPT reviews exact head/base, every changed byte and mode,
dependencies/provenance, workflows and applicability, check producer and checkout
identity, actual job steps/logs and meaningful execution evidence. Changed heads
or bases require renewed review. Android and QEMU jobs remain required when
their existing filters apply; universal statuses do not replace specialized
obligations. Skipped, cancelled, neutral, missing, failed, timed-out, pending,
zero-step or unverifiable jobs are never PDVA successful execution evidence.

[GitHub status-check behavior](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
can accept skipped/neutral conclusions. The app binding identifies a producer,
not immutable workflow code. A same-app modified workflow can emit misleading
success; complete manual review must detect it. Strict freshness does not change
the existing PR-head checkout into synthetic merge-tree testing. Do not insert
dummy checks, weaken filters, disable controls or rerun failures merely for green.

Residual risks include sole-owner error/credential compromise, unenforced manual
review, same-app workflow changes, infrastructure outages and administrative
settings changes. No standing bypass does not remove an administrator's ability
to edit rules. This is no claim of independent review, product isolation or
comprehensive repository security.

## Bounded source admission and historical evidence

The checker retains `SOURCE_BASE=69a7165043e1e7fc565a9ff10f044adc4874c595`, all
original inventories/hashes, and the exact immutable README transition. Its
historical verifier remains independently callable and still rejects this ADR
as an extra governance file. The current-state verifier requires this exact ADR
path, regular mode 100644 and reviewed SHA-256, then applies the unchanged
historical source contract to the remaining snapshot, requiring the reviewed
README state. It accepts no candidate-selected baseline or allowlist.

The immutable prior state is canonical main
`e8923e315b603227db4b42c9036c184aed28b6fa`. An explicit offline audit recomputes
its historical contract and unchanged checker digest, verifies the original
baseline and README objects, and checks that current differences are only this
ADR and the original three enumerated review files. Shallow CI uses reviewed
constants; absence of old Git objects is not evidence that the audit ran.
The three pre-existing review files still require full independent diff review;
they cannot certify their own approval. This source checker is a review boundary,
not authentication of the local machine, reviewer, toolchain or candidate verifier.

Current admission cannot fall back to historical acceptance when the ADR is
missing, and old source replay cannot satisfy current admission. Tests retain
historical rejection controls separately from current positives and test exact
rejection reasons plus effective detector removal. Links/nonregular files,
changed ADR bytes, added/renamed/deleted governance, protected source mutations
and forged baseline receipts must fail.

Future governance edits require another explicit reviewed transition: immutable
prior source, exact proposed path/mode/bytes, historical recomputation, preserved
old rejection tests and new negative/removal controls. Never change a historical
digest, accept candidate-generated pins or introduce a wildcard exemption.

All fifteen historical signed-byte failures remain failures. Failed SDK-state
qualification remains failed; independent build/signing custody and physical
readiness remain blocked. No historical evidence is invalidated or repaired.
The [evidence record](../evidence/gate-0-companion-source-controls.md#consolidated-adr-0005-source-admission--2026-11-17)
records actual local validation separately from proposed GitHub experiments.

## Single activation and recovery procedure — NOT EXECUTED

1. After review and merge, obtain separate Tony authorization for named disposable
   branches/ruleset/test PRs, actors, permitted test operations, cleanup, recovery
   and eventual main activation. Record approval of final technical details; a
   merge alone does not establish unstated owner consent. Reverify live main,
   open PRs, all parent/effective/classic protection, admin authority, merge
   methods and genuine recent jobs/app identity. Export old configuration and
   exact refs to public-safe evidence. Drift or missing evidence stops activation.
2. Create the authorized disposable target before applying the exact body above,
   differing only in approved name and target. POST to
   `/repos/innercoder78/privacy-decoy-virtual-android/rulesets`; save its returned
   ID. GET `/repos/innercoder78/privacy-decoy-virtual-android/rulesets/{id}` with
   sufficient authority to see bypass actors and GET
   `/repos/innercoder78/privacy-decoy-virtual-android/rules/branches/{branch}`.
   Compare every normalized field and effective rule. Verify an unrelated control
   branch is outside scope. Rejection or unexpected settings mean STOP/Unknown.
3. On that disposable target demonstrate actual authorized zero-approval PR
   merging with fresh base, genuine required checks/app and substantive logs,
   after complete ChatGPT review. Exercise merge, squash and rebase separately
   within authorization; untested methods remain Unknown. No badge substitutes
   for a completed legitimate merge and observed resulting target OID.
4. Against the disposable target only, attempt authorized unassociated direct
   updates, non-fast-forward updates and deletion; record actor, attempted
   old/new OIDs, rejection response and unchanged target. Exercise missing,
   pending and failed required checks and stale-base PRs. Advance the base via
   a compliant PR, then prove a stale PR is blocked and a legitimate refreshed
   head with fresh checks can merge. Account for GitHub's PR-associated local
   merge routes; do not falsely claim every Git transport update is forbidden.
5. Test wrong-producer/wrong-SHA, cancelled/timed-out, skipped/neutral and zero-step
   cases only with authorized safe fixtures. Never impersonate Actions, grant
   extra app privileges or modify production workflows to manufacture results.
   Unavailable fixtures are Unknown; any mandatory enforcement gap blocks
   activation. GitHub's documented skipped/neutral limitation remains an explicit
   manual-review obligation, not a passing security control.
6. Before activation, rehearse recovery on the disposable rule: confirm the
   authorized administrator can GET and PATCH that exact rule through the ruleset
   API independently of branch merging; exercise only the approved disable/restore
   change, read back both states and repeat the positive PR test. Preserve topic
   branches and evidence. Prefer reviewed repair PRs for CI/configuration issues.
   No working recovery path means STOP before main activation.
7. Review results and Unknowns with Tony. Only successful required tests and
   explicit final authorization permit creation of the single exact main rule.
   Never run destructive enforcement probes against main. Read back its ID,
   bypass list, exact target and effective rules; compare parent/classic settings
   and merge methods. Record timestamps, actor, old/new configuration and tests.
   Halt merges on disagreement. Clean up disposable resources only as authorized.
8. If legitimate work later blocks, preserve topic work, inspect real CI/logs and
   settings, and use a compliant reviewed repair PR when possible. Emergency main
   disablement/relaxation requires separate Tony approval naming the exact rule,
   old/new body, reason, duration, reviewer, restoration and verification plan.
   It is never automatic and never a standing bypass. Restore and read back the
   approved configuration before resuming merges. If the required recovery review
   or administrative route is unavailable, remain stopped.

## Alternatives and upgrade conditions

Waiting without protection leaves the observed prevention gap. Mandatory
independent approval now would block sole-owner work without a qualified reviewer.
Standing bypass or Restrict updates plus bypass defeats the selected protection.
Globally requiring path-filtered Android/QEMU risks deadlock and is not selected.

Move to independently enforced review when a named trusted qualified reviewer
can approve owner-authored/latest-owner-pushed changes, with separately authorized
access and explicit Tony approval of stronger settings. Test those settings and
recovery before activation, record the transition and retain this interim history.
Revisit earlier on compromised authority, unsafe allowed updates, invalid source
admission or an inability to sustain genuine checks/manual review. None of these
conditions licenses weakening Android product security.
