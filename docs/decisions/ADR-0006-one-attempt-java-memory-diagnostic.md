# ADR-0006: One owner-operated Java memory diagnostic attempt

**Accepted by the project owner on 2026-11-23.** The owner approved the
diagnostic-only policy and separately authorized its registration, the minimum
source-admission changes, and the ordinary hosted CI operations they trigger.
Initial operational authority covers offline, read-only preparation only.

This decision adopts the complete [one-attempt policy as reviewed in PR #101](https://github.com/innercoder78/privacy-decoy-virtual-android/blob/2256e3f72b860e65e3e4b41a7a6c3596ac105656/docs/evidence/gate-0-companion-source-controls.md#one-attempt-java-diagnostic-policy),
including its ordered evidence, authorization, withdrawal and closure requirements.
Its source is commit `b84af1c7764298b06bc8b356c38b3ef9fd8f0db3`,
tree `0dfc367c4c87defe7d468946bf3e7cf477cc0282`. Scope is the reviewed
Java-only release of `org.pdva.memorydiagnostic`, one privately designated
compatible stock Android 17 device and one physical attempt.

## Accepted tradeoffs

For this attempt, three obligations are **waived for this attempt / unproven**:

1. Independent build administration and complete independent toolchain qualification.
   The owner must document the fresh worker, exact inputs, provenance gaps and SDK write boundary.
2. Independently qualified signing custody and independent artifact verification.
   The owner must demonstrate private custody and recovery, verify the signer,
   signature and delivered bytes, and confirm rejection of a tampered copy.
3. Two independently built, byte-identical complete signed APKs.
   The owner must trace one original from reviewed source to delivered artifact.

One administrator can build and sign unintended bytes. Hash and signature
checks cannot establish benign tools, complete correspondence or safe custody.
The owner accepts responsibility for recovery and withdrawal and the risks of
framework or kernel faults, blocking, state loss and lost results. Even an
admitted mapping with complete cleanup establishes only the observation on
that device.

## Authority and expiration

Each build, signing, transfer, installation and execution requires separate
authorization. The first unsigned build requires verified exact source and
inputs, passing applicable checks and negative controls, an incident-separated
worker, demonstrated SDK immutability under its build identity, verified
encrypted-backup recovery, and agreed retention, deletion and withdrawal terms.
Ordinary registration CI supplies no physical candidate approval.

The exception ends at the earliest of first press, owner or reviewer withdrawal,
a failed mandatory check, unexpected behavior, loss of custody, a change to
source, tools, artifact, device or recipient, or 00:00 on 2026-12-08 in
America/Fortaleza. Interruption consumes the attempt. Closure obligations
survive termination. Companion-only Option B retains its own earlier termination
rules and December 8 deadline.

Only the specified companion qualification evidence under PDVA-REQ-036 changes.
PDVA-REQ-008, PDVA-REQ-039 through PDVA-REQ-041 and PDVA-REQ-051 remain mandatory.
ADR-0004 Option A retains the full interactive Android 17 virtual phone under
ordinary-app-only host authority. Production source, build, isolation, signing,
distribution and strict signed-byte requirements continue. The native research
harness remains execution-locked. All fifteen historical signed-byte failures,
the failed historical SDK-state assertion and negative receipts retain their
dispositions. Gate 0 remains **Unresolved**. Gates A–G remain **Not reached**.
