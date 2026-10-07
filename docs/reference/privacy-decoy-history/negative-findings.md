# Preserved negative findings

> **Historical / non-normative for PDVA.** Origin: [innercoder78/Privacy-Decoy](https://github.com/innercoder78/Privacy-Decoy).
> Exact authoritative predecessor main: `5320b3b44b38df4b8f3361ecbcb530386ff195e9` (verified 2026-10-07).
> Original scope: stock non-rooted host-app virtualization/mediation research,
> including Phase I admission-gated and post-AG1 boundaries and incomplete
> Phase II transformation-first mediation; individual experiment scope is narrower.
> PDVA must revalidate every conclusion before relying on it.
> App virtualization/mediation evidence is **not VM-isolation evidence**.

## Phase I closeout

[Comparative synthesis](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-comparative-synthesis.md)
selected **C. NO CREDIBLE BOUNDARY** under the predecessor's original contract.
This was a scoped synthesis, not universal impossibility. The
[owner handoff](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-owner-handoff.md) later records
acceptance of the old-contract STOP and authorization of contract redesign.

## AG-1 direct-loader failure

[AG-1 closeout](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/ag1-feasibility-closeout.md) preserves failure
of the tested trusted-helper executable-code mediation hypothesis. Previously
unadmitted DEX executed through the direct `InMemoryDexClassLoader` path without
the mandatory helper authorization. Loader construction, class resolution,
initialization and execution in that tested path falsified the hypothesis.
Bounded admission/bootstrap/helper successes did not repair the bypass. This was
not an escape from Android's UID sandbox and is not evidence of a VM escape.

## Managed-profile genuine-state limitations

[Managed-profile S1](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/pr8-managed-profile-boundary.md)
reports falsification for its Persona requirements at tested head
`69f0352510a55d92dcf4a408aa524cc0532788f9`: seven mandatory Build surfaces matched
the parent environment in both tenants. Storage/UID separation did not replace
genuine platform identity. The follow-up networking work remained blocked.
This does not invalidate all managed-profile security properties or establish
anything about a full guest's isolation.

## VPN-loss physical egress

[Historical network evidence](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/pr5-network-feasibility.md)
uses API 35 Google APIs x86_64 debug research. The implementation run at
`b87b2682ba6085bef2edab4e99aea74568fdb6d7` recorded physical packets after
non-lockdown VPN loss even when the operation returned timeout. Later scoped
results retained this known gap; tested no-fallback depended on external Android
lockdown. Callback/snapshot detection was not proof of no packets. Protocol,
producer and physical-release gaps remained. The particular broker and external
VPN fixture do not become PDVA architecture.

## Incomplete Phase II and PDVA limit

[ADR-0010](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0010-select-transformation-first-hybrid-privacy-mediation.md)
selected transformation-first hybrid mediation.
[ADR-0012](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0012-suspend-active-development-and-establish-pdva-successor.md)
and [project status](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/project-status.md) state Stage 2 maintenance
completed; Stage 3 and later stages remained unfinished. No production privacy
boundary was proven. Suspension did not establish that Phase II was technically
disproven or universally impossible.

These architecture-specific results neither prove nor disprove PDVA's full-guest
product direction. They motivate independently falsifiable tests and honest
Unknown handling. No historical success or failure passes PDVA Gate 0 or Gate B.
