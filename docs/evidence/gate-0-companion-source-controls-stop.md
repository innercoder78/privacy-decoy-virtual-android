# Gate 0 companion source controls publication STOP

On 2026-11-10 in Codex Desktop LOCAL, the owner confirmed STOP for scope
revision. The question was whether the source controls specified in the
[ADR-0003 acceptance record](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md#companion-only-acceptance-and-preparation--recorded-2026-11-10)
could be implemented, tested and published with workflow integration while
retaining the existing checks and prohibiting Android builds. This records a
repository and workflow observation under [PDVA-REQ-008, 038–041 and 054](../requirements.md).

## Verified baseline and conflict

- GitHub's main branch response and the fetched Git ref agreed on
  `907c14c11bb9ff6dcfe12234960b0a0ded2a43dd`. [PR #72](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/72)
  was merged at that commit. The open PR list was empty, so there were no open
  heads, bases, diffs, modes, checks, jobs, logs, reviews, comments or threads
  to inspect. PR #72's merge delta was limited to ADR-0003 and the evidence
  index, both regular 100644 files.
- Exact-main [Foundation run 42862155126](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42862155126)
  reported success for `foundation` (129990854978) and
  `offline-image-windows` (129990854407). Check and job records and completed
  logs were retrieved. The run listing returned no Android or QEMU run for
  that SHA. These observations concern the existing baseline.
- The retrieved [GitHub Status snapshot](https://www.githubstatus.com/api/v2/summary.json),
  updated `2026-11-10T16:39:58.896Z`, reported a Pull Requests major outage
  and an Actions partial outage. Successful reads establish only those requests.
- The [Foundation validator](../../.github/scripts/validate-foundation.py) uses
  an exact-path code allowlist. Adding Python verifier and test scripts requires
  adding their paths to that validator even if placed under `docs/`. The
  validator itself and any workflow integration are under `.github/`.
- The [Android workflow](../../.github/workflows/android-harness.yml) selects
  `.github/**` on PRs and pushes to main. Its job invokes the Android SDK CLI
  and Gradle and assembles harness and unsigned companion APKs. Publishing the
  requested implementation would select that job through either the allowlist
  edit or workflow integration. Under the prior scope, the builds were
  prohibited and existing checks and triggers had to be preserved. The
  conclusion depends on those exact source rules. A later base or path change
  requires a fresh applicability review.

## Disposition and reopening condition

At the previous STOP, implementation and proposed source tests were **NOT RUN**.
No production configuration changed, the three-line module patch stayed
unapplied, and no implementation PR existed. Carry forward the exact-base,
in-memory positive and negative controls and detector-removal tests for a
separate owner decision. The narrow options for that decision are:

1. Authorize local-only verifier preparation and fixture tests in an isolated
   checkout, deferring workflow integration and publication of the code.
2. Separately authorize a future source-control PR and the existing hosted
   operations its exact paths select, subject to the applicable review and
   qualification prerequisites. If those operations remain prohibited, keep
   publication stopped. Reassess the reviewed baseline and acceptance window
   before reopening.

This record adopts neither option. CI bypass, trigger edits, workflow
suppression, relocating code to evade checks and hidden builds are excluded.

The two paths in this documentation change are this record and
`docs/evidence/README.md`. The [Foundation workflow](../../.github/workflows/foundation.yml)
applies normally. Neither path matches the Android or
[QEMU workflow](../../.github/workflows/qemu-android-research.yml) filters.
Local bundled CPython 3.12.14 Foundation validation passed with 182 files,
111 Markdown files, 54 requirements and four ADRs. New-head hosted results
are **Unknown** at publication.
No local build, signing, Android CLI, native/VM or physical test was performed.
This path analysis supplies no packaging, signed-byte, provenance or security proof.

ADR-0003 host Option A and companion-only Option B preparation acceptance,
including the maximum **2026-12-08** expiration in America/Fortaleza and earlier
stop conditions, retain their dispositions. [ADR-0004 Option A](../decisions/ADR-0004-gate-0-owner-disposition.md),
all [fifteen signed-byte failures](gate-0-apk-reproducibility.md), the
[unconditional research execution lock](gate-0-research-execution-lock.md) and
all existing requirements remain in force. **Gate 0 Unresolved.** Independent
reviewers and custodians are **UNASSIGNED**, independent backup **UNVERIFIED**
and private evidence **UNPRESERVED**.
