# Historical reuse classification

> **Historical / non-normative for PDVA.** Origin: [innercoder78/Privacy-Decoy](https://github.com/innercoder78/Privacy-Decoy).
> Exact authoritative predecessor main: `5320b3b44b38df4b8f3361ecbcb530386ff195e9` (verified 2026-10-07).
> Original scope: stock non-rooted host-app virtualization/mediation research,
> including Phase I admission-gated and post-AG1 boundaries and incomplete
> Phase II transformation-first mediation; individual experiment scope is narrower.
> PDVA must revalidate every conclusion before relying on it.
> App virtualization/mediation evidence is **not VM-isolation evidence**.

No source, scaffold, fixture, binary or Git history is copied by this bootstrap.
Classifications describe prospective treatment, not an adoption approval.

| Material / concept | Classification | PDVA treatment |
|---|---|---|
| Threat-model methodology, evidence discipline, conservative Unknown handling and compatibility/security separation | reusable after generalization | Reframe around guest/host authority and PDVA gates; do not inherit old coverage claims. |
| Source/provenance discipline, public-repository hygiene, CI principles and adversarial testing methodology | reusable after generalization | New PDVA policies and lightweight CI; independently verify action pins and sources. |
| Real / Decoy / Empty / Deny and coherent stable Persona semantics | reusable after generalization | Deliberately re-adopt as PDVA-REQ-016–021; translate surfaces and enforcement to a full guest. |
| Networking methodology, producer attribution, independent packets, VPN-loss tests and no-silent-fallback discipline | reusable after generalization | Apply to a future guest/host backend; do not import old broker routing assumptions. |
| Java/native probes, controlled fixtures and artifact/network analyzers | reusable after architectural rewrite | Possible future reuse only after architectural and file-level provenance review; adapt observers to guest/host boundaries. No copy now. |
| Minimal Android app, Gradle/build and test scaffolding | reusable after architectural rewrite | Host minimum/ABI/build needs depend on Gate 0; no Gradle/wrapper/app added now. |
| Particular historical broker implementation and external test VpnService | historical reference only | Neither is PDVA networking architecture; fixture is test-only and not production VPN authorization. |
| AG-1 evidence, candidate analyses, Phase I/II ADRs, old roadmaps/requirements and C. NO CREDIBLE BOUNDARY | historical reference only | Preserve scope and immutable links; no PDVA gate credit. |
| Old PD-REQ numbering, ADR numbering and Fully/Partially mediated vocabulary | historical reference only | New PDVA IDs, ADRs and evidence/gate terminology. |
| Transformation-first runtime, host app virtualization, Binder proxying, APK/DEX rewriting and Java/native hooks as primary boundary | incompatible | Cannot silently become PDVA's selected primary isolation boundary. |
| Restriction against a full guest Android | obsolete; incompatible | Obsolete for the successor and incompatible with the explicitly selected full-guest direction. |
| Old implementation sequencing, emulator-first phase permissions and old runtime build jobs | unnecessary | Not needed for foundation and not authorization for PDVA implementation. |
| Unmodified runtime/artifact adoption | reusable as-is: none selected | No predecessor implementation is approved for verbatim adoption. Immutable citation is reference, not code reuse. |

“Reusable as-is” would require evidence of unchanged fitness and provenance.
“After generalization” preserves a method while changing scope. “After architectural
rewrite” requires redesigned code/contracts. “Historical reference only” confers
no forward authority. “Obsolete” means superseded for PDVA; “incompatible” conflicts
with its contract; “unnecessary” supplies no current need. All seven categories
are available without forcing a nonempty code-adoption category.

The [historical index](README.md) identifies exact sources. Current
[requirements](../../requirements.md) and [source policy](../../source-provenance-policy.md)
control any later reuse.
