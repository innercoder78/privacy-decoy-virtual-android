# Conceptual architecture

**No engine selected. Feasibility and enforcing boundary unresolved.** This is a
logical responsibility model, not an implementation or deployment diagram.
The [Gate 0 candidate proposal](evidence/gate-0-userspace-vmm-candidate.md) develops
a non-normative QEMU/TCG plus dedicated isolated-UID worker hypothesis with trusted
management outside. Its [physical authority proof](evidence/gate-0-isolated-qemu-proof.md)
is specified but not run; it does not change this document's unresolved boundary.

```text
Host Android (stock, non-rooted, production user build)
  → PDVA host management/control plane
    → explicit guest/host boundary (enforcing authority unresolved)
      → controlled guest Android 17 / API 37 platform
        → potentially hostile guest applications and all their code
```

Host Android supplies only authority available to an ordinary installed app.
PDVA management owns instance lifecycle, security policy, Persona master state,
image/update verification and management credentials. The guest receives only
explicit capabilities and permitted data, never management databases, signing
secrets or unbounded host handles. Other guest instances remain separate protected
assets. Running a guest does not establish this separation.

The guest platform provides normal Android semantics including SystemServer,
Zygote, packages, Activities, launcher/System UI, services, WebView and guest-native
execution. Guest platform components can be attacked by apps; boundary analysis
must examine a compromised guest and malformed virtual-device traffic, not rely
solely on guest Android permissions.

Each bridge (network, display/input, audio, sensors, files, clipboard, notifications,
camera/microphone and management) needs a typed, narrow, authorized interface,
explicit data direction, bounded resource budget, revocation semantics and failure
behavior. This does not select a broker implementation or assume a hypervisor.
Candidate authorities include the host kernel/process sandbox/SELinux, hypervisor,
device model, broker and cryptographic verification, subject to Gate 0 access and
Gate B evidence. A software emulator could expose host-process authority if
compromised; management separation and the emulator/device-model TCB need their
own proof.

Guest permissions authorize guest behavior, not automatic host data disclosure.
Real data crosses only through the [privacy policy](persona-privacy-policy.md).
The desired [network path](networking.md) uses host networking and an external host
VPN where required without PDVA taking the VPN slot. Route verification and
fail-closed enforcement remain unresolved.

Only one controlled image line is intended. Verification precedes guest start and
restore; stale capabilities must not survive snapshots, policy changes or process
death. Exact mechanisms remain Unknown. [Boundary inventory](security-boundaries.md),
[threat model](threat-model.md) and [image lifecycle](guest-image-lifecycle.md) define
the questions a future candidate must answer. Restricted AVF access cannot be
repaired by silently substituting privileged installation or host app hooking.
