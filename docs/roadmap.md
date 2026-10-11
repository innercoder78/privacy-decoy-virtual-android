# Evidence-gated roadmap

| Stage | Authorized scope and exit |
|---|---|
| Foundation — this bootstrap | Governance, PDVA requirements, historical classification, platform-authority evidence and cheap validation only. No feasibility result. |
| Immediate next work — Gate 0 research | Review the [source survey](evidence/gate-0-userspace-vmm-sources.md) and [isolated QEMU authority proof](evidence/gate-0-isolated-qemu-proof.md). The next bounded physical step is the smaller [PDVA-owned native executable control](evidence/gate-0-isolated-native-launch.md) in the [substrate harness](evidence/gate-0-isolated-worker-harness.md). The later tiny ARM64 Linux/QEMU experiment remains subject to source/adoption review; QEMU and its guest fixture are not integrated into the APK. A scoped mechanism success is not Gate 0 Passed. No engine selected by this roadmap. |
| Conditional complete-guest work | Only after a reviewed Gate 0 pass, propose Gate A implementation for the approved exact scope. Headless workload guests cannot satisfy it. |
| Conditional qualification | Progress through Gates B–G as foundational evidence allows, with independently tracked security, usability, networking, Google and image-lifecycle outcomes. No calendar promise or giant implementation queue. |

Gate 0 is **Unresolved**; A–G are **Not reached**. The
[gate definitions](feasibility-gates.md) govern progression. A scoped excluded AVF
path does not eliminate user-space alternatives. A failed candidate stops work
dependent on that candidate; it cannot be quietly replaced with in-host hooks or
privileged deployment.

Before QEMU integration, the [isolated native launch control](evidence/gate-0-isolated-native-launch.md)
prepares a smaller PDVA-owned ARM64 executable experiment. It separates JNI,
packaging, exec/linker, identity and cleanup evidence. Its first physical run is
one release-equivalent session on stock Android; uncertain cleanup blocks repeats.
This bounded step adopts no engine and leaves the later QEMU questions unresolved.

Continue useful source research, theory, architecture, provenance, build
integration, static analysis and other non-physical falsification work, including
QEMU research and adoption review, without requiring Tony to connect a phone.
The proposed physical experiment is future work, not a prerequisite for this PR
or every later PR. Physical runtime observations remain **Unknown** and must not
be treated as a substrate pass. Work depending on a physical fact must preserve
that Unknown; stop only at the exact question that genuinely cannot advance
without stock physical-device evidence. ChatGPT will identify future physical
tasks separately. Further adoption and integration still require their own scope
and provenance review; complete-guest progression still requires the reviewed
Gate 0 pass above.

**STOP**, **NARROW** and **REDESIGN** are real exits. Narrowing or material redesign
requires explicit owner approval and a PDVA ADR. No engine, VM execution, guest
image or Android runtime work is authorized in this bootstrap.

## Lifecycle proposal for owner review

[ADR-0002](decisions/ADR-0002-signed-environment-delivery-and-compatibility.md) is
**PROPOSED**, pending Tony's explicit approval of the final text. The
[delivery and updates contract](environment-delivery-and-updates.md) records the
small-host/separate-environment product goals and proposed compatibility,
authentication, discovery and recovery behavior. This is parallel documentation
work, not a Gate 0 result or authorization for guest/downloader implementation.
Immediate technical work remains Gate 0 research; A–G remain Not reached.

If accepted, first review the identified requirements additions, trust/compatibility
contracts, rights and maintenance ownership. Implementation/adoption needs its own
scope and provenance review; complete-guest work still depends on Gate 0. Later
Gate F/G qualification needs tamper, freshness, revocation, compatibility, migration,
snapshot and interruption/recovery evidence for exact builds. A future guest-major
chooser is deferred to a separate owner-approved ADR and requirements revision.
