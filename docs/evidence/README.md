# Evidence index

Evidence describes exact observations and limitations; it does not redefine
requirements. Use the terminology and record fields in
[acceptance criteria](../acceptance-evidence-criteria.md).

| Record | Role and scope |
|---|---|
| [Gate 0 platform authority](gate-0-platform-authority.md) | Independently retrieved current and Android 17 AOSP/source documentation; candidate access findings and explicit Unknowns. Gate 0: Unresolved. |
| [User-space VMM source research](gate-0-userspace-vmm-sources.md) | Immutable QEMU/Android packaging and isolation evidence, alternative ranking inputs, licenses/limits and exact-base repository preflight. |
| [Candidate architecture hypotheses](gate-0-userspace-vmm-candidate.md) | Isolated worker, capabilities, Persona/guest management, network/graphics and store-neutral signed image; no engine selected. |
| [Next physical proof](gate-0-isolated-qemu-proof.md) | Exact falsifiable isolated-QEMU authority experiment using a tiny Linux fixture. NOT RUN; even success is not Gate 0 Passed. |
| [Black-box comparison plan](gate-0-black-box-comparisons.md) | Virtual Master/VMOS/VPhoneOS metadata versus claims and an unobserved behavior checklist; no kernel-security inference. |
| [Bootstrap repository preflight](bootstrap-preflight.md) | Starting Git/GitHub structure, authority and binary/dependency observations; not runtime evidence. |

No VM or Android runtime has been executed in this bootstrap. There is no direct
PDVA guest boot, isolation, VPN-route or physical-device evidence. Historical
experiments remain under [historical reference](../reference/privacy-decoy-history/README.md).
