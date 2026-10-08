# Evidence-gated roadmap

| Stage | Authorized scope and exit |
|---|---|
| Foundation — this bootstrap | Governance, PDVA requirements, historical classification, platform-authority evidence and cheap validation only. No feasibility result. |
| Immediate next work — Gate 0 research | Review the [source survey](evidence/gate-0-userspace-vmm-sources.md) and the now-specified [isolated QEMU authority proof](evidence/gate-0-isolated-qemu-proof.md). The next proposed physical experiment is a tiny ARM64 Linux fixture in an isolated worker, subject to source/adoption review; the [pre-QEMU substrate harness](evidence/gate-0-isolated-worker-harness.md) now prepares the Android-side capability test; QEMU and its fixture remain unimplemented. A scoped mechanism success is not Gate 0 Passed. No engine selected by this roadmap. |
| Conditional complete-guest work | Only after a reviewed Gate 0 pass, propose Gate A implementation for the approved exact scope. Headless workload guests cannot satisfy it. |
| Conditional qualification | Progress through Gates B–G as foundational evidence allows, with independently tracked security, usability, networking, Google and image-lifecycle outcomes. No calendar promise or giant implementation queue. |

Gate 0 is **Unresolved**; A–G are **Not reached**. The
[gate definitions](feasibility-gates.md) govern progression. A scoped excluded AVF
path does not eliminate user-space alternatives. A failed candidate stops work
dependent on that candidate; it cannot be quietly replaced with in-host hooks or
privileged deployment.

**STOP**, **NARROW** and **REDESIGN** are real exits. Narrowing or material redesign
requires explicit owner approval and a PDVA ADR. No engine, VM execution, guest
image or Android runtime work is authorized in this bootstrap.
