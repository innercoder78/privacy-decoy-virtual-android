# Privacy Decoy historical reference

> **Historical / non-normative for PDVA.** Origin: [innercoder78/Privacy-Decoy](https://github.com/innercoder78/Privacy-Decoy).
> Exact authoritative predecessor main: `5320b3b44b38df4b8f3361ecbcb530386ff195e9` (verified 2026-10-07).
> Original scope: stock non-rooted host-app virtualization/mediation research,
> including Phase I admission-gated and post-AG1 boundaries and incomplete
> Phase II transformation-first mediation; individual experiment scope is narrower.
> PDVA must revalidate every conclusion before relying on it.
> App virtualization/mediation evidence is **not VM-isolation evidence**.

This area contains concise summaries and immutable links, not copied predecessor
history, normative requirements or an implementation work queue. PDVA is not
Phase III. Its requirements start at PDVA-REQ-001 and its own ADRs at ADR-0001.

The live predecessor main matches the expected suspension merge of PR #39.
The local predecessor checkout remained on its existing suspension branch at
`38ab23fce8e88b66c974afd31f0d33a77c1685d4`; exact-SHA Git object reads supplied
current authoritative content without fetching or changing that checkout.

Phase I ended with **C. NO CREDIBLE BOUNDARY** within its original contract and
AG-1 failed. Phase II selected transformation-first hybrid mediation, completed
Stage 2 maintenance and stopped before Stage 3 and later implementation. No
production privacy boundary was proven. Suspension did not prove Phase II
universally impossible. None of these results proves or disproves PDVA's VM direction.

See [reuse classification](reuse-classification.md) and
[negative findings](negative-findings.md).

## Inspected authority and research index

All links use the exact source SHA above. The documents were inspected for
status, constraints, findings and reuse implications; this was not a fresh audit
or re-execution of their experiments.

### Status and contracts

- [README.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/README.md)
- [docs/project-status.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/project-status.md)
- [docs/requirements.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/requirements.md)
- [docs/threat-model.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/threat-model.md)
- [docs/platform-support.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/platform-support.md)

### Architecture and governance

- [docs/architecture-redesign-study.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/architecture-redesign-study.md)
- [docs/post-ag1-enforcement-boundary-redesign.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/post-ag1-enforcement-boundary-redesign.md)
- [docs/privacy-mediation-redesign-handoff.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/privacy-mediation-redesign-handoff.md)
- [docs/canonical-roadmap-1.0.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/canonical-roadmap-1.0.md)

### Phase II

- [docs/phase-ii-requirements.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/phase-ii-requirements.md)
- [docs/phase-ii-requirements-migration.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/phase-ii-requirements-migration.md)
- [docs/phase-ii-threat-model.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/phase-ii-threat-model.md)
- [docs/phase-ii-acceptance-criteria.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/phase-ii-acceptance-criteria.md)
- [docs/phase-ii-roadmap.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/phase-ii-roadmap.md)
- [docs/open-source-reference-catalog.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/open-source-reference-catalog.md)

### Evidence

- [docs/evidence/ag1-feasibility-closeout.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/ag1-feasibility-closeout.md)
- [docs/evidence/post-ag1-candidate-1-os-process-compartment.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-candidate-1-os-process-compartment.md)
- [docs/evidence/post-ag1-candidate-2-controlled-runtime-lower-boundary.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-candidate-2-controlled-runtime-lower-boundary.md)
- [docs/evidence/post-ag1-candidate-3-constrained-execution-class.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-candidate-3-constrained-execution-class.md)
- [docs/evidence/post-ag1-candidate-4-syscall-binder-boundary.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-candidate-4-syscall-binder-boundary.md)
- [docs/evidence/post-ag1-candidate-5-hybrid-architecture.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-candidate-5-hybrid-architecture.md)
- [docs/evidence/post-ag1-comparative-synthesis.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-comparative-synthesis.md)
- [docs/evidence/post-ag1-owner-handoff.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/post-ag1-owner-handoff.md)
- [docs/evidence/pr5-network-feasibility.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/pr5-network-feasibility.md)
- [docs/evidence/pr8-managed-profile-boundary.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/pr8-managed-profile-boundary.md)
- [docs/evidence/architecture-discovery-synthesis.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/architecture-discovery-synthesis.md)
- [docs/evidence/architecture-discovery-virtualspace-static-falsification.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/architecture-discovery-virtualspace-static-falsification.md)
- [docs/evidence/architecture-discovery-blacks-blackbox-provenance.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/evidence/architecture-discovery-blacks-blackbox-provenance.md)

### Scaffolding and validation

- [.github/CONTRIBUTING.md](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/.github/CONTRIBUTING.md)
- [.github/workflows/android.yml](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/.github/workflows/android.yml)
- [.github/scripts/classify-ci-changes.sh](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/.github/scripts/classify-ci-changes.sh)
- [android/build.gradle.kts](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/build.gradle.kts)
- [android/settings.gradle.kts](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/settings.gradle.kts)
- [android/app](https://github.com/innercoder78/Privacy-Decoy/tree/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/app)
- [android/probe-app](https://github.com/innercoder78/Privacy-Decoy/tree/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/probe-app)
- [android/research-native](https://github.com/innercoder78/Privacy-Decoy/tree/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/research-native)
- [android/test-apps](https://github.com/innercoder78/Privacy-Decoy/tree/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/test-apps)
- [android/tools/artifact-analyzer.py](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/tools/artifact-analyzer.py)
- [android/tools/network-evidence.py](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/android/tools/network-evidence.py)

### ADR lineage (all inspected)

| ADR | Historical role |
|---|---|
| [ADR-0001](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0001-engine-prototype-direction.md) | Prototype only; no production engine. |
| [ADR-0002](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0002-feasibility-stop-gate.md) | REDESIGN; bounded containment and network evidence insufficient. |
| [ADR-0003](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0003-redesign-prototype-direction.md) | Managed-profile S1 and source/provenance S2 dispositions. |
| [ADR-0004](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0004-canonical-audit-reconciliation.md) | Specification/governance reconciliation. |
| [ADR-0005](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0005-canonical-roadmap-source-restoration.md) | Historical roadmap source restoration. |
| [ADR-0006](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0006-redesign-again-architecture-discovery.md) | Bounded discovery and STOP recommendation. |
| [ADR-0007](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0007-admission-gated-controlled-runtime.md) | Admission hypothesis; subsequent AG-1 failure. |
| [ADR-0008](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0008-post-ag1-enforcement-boundary-redesign.md) | Five-candidate lower-boundary investigation. |
| [ADR-0009](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0009-retire-universal-containment-and-authorize-privacy-mediation-redesign.md) | Owner accepts old-contract STOP and authorizes contract redesign. |
| [ADR-0010](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0010-select-transformation-first-hybrid-privacy-mediation.md) | Selects historical Phase II transformation-first hybrid. |
| [ADR-0011](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0011-adopt-emulator-first-phase-ii-development.md) | Research-stage emulator policy; no production physical claim. |
| [ADR-0012](https://github.com/innercoder78/Privacy-Decoy/blob/5320b3b44b38df4b8f3361ecbcb530386ff195e9/docs/decisions/ADR-0012-suspend-active-development-and-establish-pdva-successor.md) | Suspension, Stage 2 final state and separate PDVA lineage. |
