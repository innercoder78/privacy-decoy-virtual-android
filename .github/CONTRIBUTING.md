# Contributing to PDVA

Read the [requirements](../docs/requirements.md),
[governance](../docs/governance.md), [gates](../docs/feasibility-gates.md) and
[evidence criteria](../docs/acceptance-evidence-criteria.md) first. The repository
is a foundation, not a VM implementation. Next technical work remains Gate 0
research. No engine or production isolation is selected or proven.

Keep root entries limited to `.github/`, `android/`, `docs/`, `.editorconfig`,
`.gitattributes`, `.gitignore` and `README.md`. New root entries need a reviewed
explicit purpose. No license, build system, wrapper, guest image or binary should
be added merely by convention. Code adoption needs
[provenance review](../docs/source-provenance-policy.md); a reference is not adoption.

Treat all GitHub surfaces as public. Never commit secrets, signing material,
private accounts, host identifiers, Persona secrets, confidential local paths,
raw sensitive captures or proprietary software without established rights.
Ignore rules are convenience, not review exemptions. Intentionally adding ignored
artifacts still requires review, and bootstrap validation rejects tracked binaries.

Preserve unrelated work, branches, worktrees and stashes. Historical Privacy Decoy
is read-only: use exact-SHA reads and read-only remote queries without fetching
into it. Never import its history or silently reuse its architecture/numbering.

Before a commit:

1. Run `python .github/scripts/validate-foundation.py` and `git diff --check`.
2. Inspect every changed file and the full diff from the exact verified base,
   including new files, modes, binaries, dependencies and public-data hygiene.
3. Verify local Markdown targets, historical notices and requirement/ADR IDs.
4. Check claims against evidence: Gate 0 stays Unresolved unless reviewed new
   evidence establishes a complete scoped result; documentation is not a pass.
5. Verify no VM/Android runtime/image/engine slipped into bootstrap scope and no
   historical checkout file changed.

The standard-library validator checks tracked and non-ignored new files and is
deliberately conservative: bootstrap files are text Markdown, the foundation
Python validator, workflow YAML and named repository configuration. Expanding
that scope needs review. It is not a Markdown specification parser, secret
scanner, security audit or feasibility test.

CI checks all PRs without path filtering, using read-only permissions and a short
timeout. Future expensive Android/VM suites must be path-aware. Check
[GitHub Status](https://www.githubstatus.com/) and actual job/step evidence before
diagnosing code failures; runner, infrastructure, quota/billing or zero-step
failures are separate outcomes. Do not weaken or rerun checks just to obtain green.
