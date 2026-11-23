# ADR-0007: Exact source binding for the one-attempt Java diagnostic

**Accepted on 2026-11-23.** The owner answered YES to the two source identities
and separately answered YES to registration, the minimum source-admission
changes and tests, and their ordinary hosted CI. Those workflows may build
existing unsigned research artifacts.

This decision adopts Path A and the complete
[reviewed proposal](https://github.com/innercoder78/privacy-decoy-virtual-android/blob/c1ca4e18636b1432adae7ad9c068415bce40f8a8/docs/evidence/gate-0-companion-source-controls.md#proposed-decision-on-the-first-unsigned-diagnostic-build).
It amends only the source binding for the companion evidence under PDVA-REQ-036
in [ADR-0006](ADR-0006-one-attempt-java-memory-diagnostic.md).

| Role | Commit | Full tree |
| --- | --- | --- |
| Reviewed diagnostic application bytes | `b84af1c7764298b06bc8b356c38b3ef9fd8f0db3` | `0dfc367c4c87defe7d468946bf3e7cf477cc0282` |
| Sole prospective build checkout | `381ab85afacde557346a80b887841e7f49eef05c` | `192748380b2c14ec2f24bb42d1e40410a03bc2db` |

Both contain the complete `android/` tree `a844105b1373ef121401718e1c5d08cf1d6ca3ce`.
The registered ADR-0006 checker must continue to reject the reviewed commit at
`exact-diagnostic-adr` and admit the prospective checkout. Later commits,
including this registration and subsequent main revisions, are ineligible.
Scope is the Java 17 release of `org.pdva.memorydiagnostic`, version code 1,
version name `0.1-diagnostic`, min/target/compile API 37.

The owner retained incident separation and SDK enforcement. Path B's environment
waiver would leave the executing tools and their outputs insufficiently known.
The first unsigned build remains **STOP**. It requires a demonstrably separate
worker, known actual Gradle execution identity, authenticated inputs and
applicable provenance, proven SDK write denial under that identity, complete
input and generated-state correspondence, a verified restore from separate
encrypted backup, agreed retention, withdrawal and deletion arrangements, and
separate explicit authorization. The worker remains unidentified. Hosted CI
provides no physical candidate approval. Signing, transfer, installation and a
physical attempt each require their own authorization.

ADR-0006's three concessions, all fifteen signed-byte failures, the failed
SDK-state assertion, and the native harness execution lock retain their prior
dispositions. PDVA-REQ-008, PDVA-REQ-039 through PDVA-REQ-041 and PDVA-REQ-051
remain mandatory. ADR-0004 Option A and all production security requirements
continue. Gate 0 remains **Unresolved** and Gates A–G remain **Not reached**.

All earlier termination triggers and closure obligations in ADR-0006 apply.
The exception expires no later than 00:00 on 2026-12-08 in America/Fortaleza.
