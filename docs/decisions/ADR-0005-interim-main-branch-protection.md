# ADR-0005: Interim main branch protection

**Approved policy revision, 2026-11-18. Production enforcement pending.**

Updates to main require a pull request. Regular merge commits are the only
permitted merge method. Squash and rebase merges are disallowed.

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

The rule requires current-base results for both `foundation` and
`offline-image-windows` from GitHub Actions app 15368. It blocks branch
deletion and force pushes, has no bypass actors, and requires zero GitHub
approvals under the interim configuration.

The [enforcement evidence](../evidence/gate-0-companion-source-controls.md#merge-only-policy-evidence)
records the tested configuration and outstanding activation conditions.
