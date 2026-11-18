# ADR-0005: Interim main branch protection

**Approved policy revision, 2026-11-18. Production enforcement pending.**

Updates to main require a pull request. Only a human maintainer may use GitHub's
regular **Merge pull request** operation. Squash merges, rebase merges and merges
performed by automated agents are prohibited. Zero GitHub approvals remain
required in this interim configuration. A future change to approval requirements
requires a separate decision.

This revision supersedes the three-method decision in the
[previous ADR](https://github.com/innercoder78/privacy-decoy-virtual-android/blob/2e820f5d0ee8319eb428b6e25081479a0fb5c064/docs/decisions/ADR-0005-interim-main-branch-protection.md). Qualification of squash
and rebase merge paths ended with that decision. Repository-wide merge options
are independent of this branch rule.

## Exact configuration for subsequent authorized administration

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
        "allowed_merge_methods": ["merge"],
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

The rule applies only to main, with no bypass actors. The strict check policy
requires results against a current base. An additional restrictive update rule
would interfere with legitimate PR merges. Reconfirm both check contexts and
their GitHub Actions integration ID against genuine runs at activation.

## Evidence required for a merge

Inspect the exact head and base, changed bytes and modes, applicable workflow
definitions, job checkout, producer, steps and logs. Repeat the assessment on
head or base changes. Android and QEMU jobs apply according to their path filters.
Successful execution requires substantive test output. A skipped, neutral,
cancelled, timed-out or empty job provides no such evidence. Same-app workflow
changes can affect what a successful context represents. Strict freshness does
not test a synthetic merge tree when the workflow checks out the PR head.

## Activation and recovery

The [evidence record](../evidence/gate-0-companion-source-controls.md#merge-only-policy-evidence)
identifies completed tests and open conditions. Production activation requires
separate owner authorization after the exact disposable configuration, effective
rules, legitimate merge, enforcement gaps and recovery are assessed. Preserve
refs and export the prior configuration before an authorized change. Independently
read back the stored ruleset including bypass actors, effective rules for the
target and an unrelated ref, and any inherited or classic protections. Compare
each field with the body above. Stop on drift, unavailable mandatory proof or an
unexpected allowed or rejected update.

Recovery requires an independently available administrative read/update route,
verified disable and restoration on a disposable rule, followed by a qualifying
merge. Prefer a reviewed repair PR for CI failures. Emergency production changes
require separate authorization for the exact rule, change, duration and restoration
procedure. Verify restoration before resuming merges. Administrators can edit
rules even when the bypass list is empty.

## Scope

The [requirements](../requirements.md), [governance](../governance.md),
[source policy](../source-provenance-policy.md) and
[evidence criteria](../acceptance-evidence-criteria.md) govern product work.
Gate 0 remains Unresolved. Gates A-G remain Not reached. These repository tests
establish no Android guest, VM, physical-device or ordinary-app authority result.
