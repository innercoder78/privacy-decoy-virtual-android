# Threat model

**Design baseline; no implemented or verified boundary.**

Assets include genuine host personal data and files, host services and device
authority, PDVA management/policy state, Persona master state, credentials,
management tokens, signing/update secrets, guest-image signing material, image
integrity, snapshot consistency and other guest instances. Availability matters
when resource pressure or recovery could trigger unsafe fallback.

Every guest app, SDK, native library, dynamic component, subprocess and guest-native
path is adversarial. Attackers may collude with other apps and remote servers,
exploit the guest kernel/framework, emit malformed virtual-device or bridge
messages, race revocation, retain descriptors, exhaust resources, tamper with
guest-controlled state and trigger death/restart/update/restore. Treat guest input
as hostile even when its package is signed or installed through Play.

The conceptual trust chain is host Android → PDVA management/control plane →
explicit guest/host boundary → guest Android → hostile applications. The guest
platform is part of guest functionality; do not assume it protects the host after
guest compromise. The TCB is unresolved and must include all components capable
of breaching the required host boundary: CPU execution, device models, host
kernel/drivers, bridges, supervisor, policy stores and image/update verification.

| Attack | Required investigation |
|---|---|
| Guest-native code issues syscalls, probes host files/properties/proc/sys | Identify whether instructions and syscalls are guest-only; test host observations independently. |
| Malformed device/broker traffic or inherited Binder/FD/shared memory | Enumerate every interface, parser, handle and deputy; test cross-instance authorization and lifetime. |
| Guest compromises VMM/backend process | Determine that process's host files, credentials, management and network authority; VM nomenclature is insufficient. |
| Guest requests real data using a granted guest permission | Verify separate PDVA Real disclosure; negative modes must not become genuine fallback. |
| Guest spoofs management UI or abuses IME/clipboard/notifications | Separate management identity and input, make disclosure visible and retain safe escape. |
| VPN changes while packets are pending | Independent packet capture, producer attribution and fail-closed race/loss tests. |
| Image/update/snapshot tampering or rollback | Authenticate inputs, enforce version policy and invalidate stale capabilities before restore. |
| CPU/memory/disk/IPC exhaustion, process death | Bounded resources and safe shutdown/recovery without policy reset or leaked genuine data. |

Assumption: the stock host boot chain, OS/kernel and hardware are not already
compromised. Exact supported devices are unknown. A fully compromised host,
malicious hardware, unrestricted forensic owner, and compromise of remote services
are outside this model; those exclusions do not excuse a guest-to-host escape or
misleading claims. No promise is made of anonymity, remote-history deletion or
matching physical hardware attestation.

Mandatory protection that remains Unknown cannot support a protected-production
claim. Required but unverified routing fails closed. Corrupt or missing Persona
state must not silently disclose host values. Recovery must reauthorize bridges;
authentication does not replace per-operation authorization. The
[boundary matrix](security-boundaries.md), [privacy policy](persona-privacy-policy.md)
and [testing plan](testing.md) define the review inventory. Physical stock release
evidence and independent security review are mandatory before strong claims.
