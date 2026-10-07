# Gate 0 candidate: isolated user-space full-system emulation

**2026-10-07 — Hypotheses only. Gate 0: Unresolved. A–G: Not reached.**
No production VM engine is selected and no ADR is created. The
[source ledger](gate-0-userspace-vmm-sources.md) records the documentary evidence;
the [physical proof specification](gate-0-isolated-qemu-proof.md) defines the next
experiment. There is no PDVA runtime observation. The architecture below is a
candidate to falsify, not a normative replacement for the
[requirements register](../requirements.md) or [architecture](../architecture.md).

## Ranking and decision boundary

| Rank / role | Candidate | Reason and unresolved obligation |
|---|---|---|
| Lead mechanism hypothesis | Full-system QEMU/TCG aarch64 software emulation under ordinary app authority | Upstream machine support and multiple Android packaging precedents. Actual isolated-process TCG, narrow resources, lifecycle and full Android viability remain Unknown. |
| Lead containment hypothesis | Dedicated Android isolated process/UID with trusted management outside | Documented isolation and AOSP FD/permission policy make a physical test worthwhile. A QEMU compromise must not inherit management authority; all broker and native-host surfaces need evidence. |
| Alternate/fallback research | Draugr/TinyEMU/v86/WASM and other legitimate user-space mechanisms | Independent JIT/process/ISA/complete-guest and provenance questions; no demonstrated advantage sufficient to displace the lead experiment. |
| Guest/device-model references | AOSP Cuttlefish and virtual Android device sources | Useful virtio, HAL, rendering and platform integration concepts; not an ordinary Android app launch/authority solution. |
| Scoped negative routes | Restricted AVF/Microdroid, privileged KVM/platform launch paths | Preserve exact existing exclusions; they do not close user-space alternatives. |
| Unsuitable primary boundary | Shared-kernel namespace/ptrace/Binder/syscall mediation, including inspected RootlessAndroid15VM and VineOS routes | No genuine independent full-system guest kernel; retain technique references without substituting them for PDVA's direction. |
| Behavioral comparisons | Virtual Master, VMOS, VPhoneOS | Black-box UX/lifecycle study only; kernel isolation and security remain Unknown. |

Research ranking is not component adoption. A failed foundational hypothesis stops
its dependent work; owner-approved NARROW or REDESIGN follows existing governance.
A different engine, host privilege, shared management UID or weaker boundary cannot
be silently substituted to keep the experiment green.

## Candidate responsibility and authority model

```text
stock non-rooted host Android: kernel / process / UID / SELinux enforcement
  trusted PDVA management process
    policy, Persona master state, image verification, update/signing authority
    |
    | narrow explicit Binder interface + exact passed FDs/capabilities
    v
  dedicated Android isolated worker (fresh instance and isolated UID)
    source-built QEMU/TCG full-system machine; assumed compromiseable
    |
    v
  controlled Android guest with independent emulated guest kernel
    hostile guest apps, SDKs, native code and potentially compromised guest OS
```

One fresh worker per VM instance is the investigation direction. Separate named
processes with the same app UID are insufficient. Do not share isolated workers
between VM instances or rely on reinitializing QEMU globals safely. Android may
reuse numeric UIDs after process death: authorize a live instance/epoch and Binder
lifetime, not an old UID number alone. Management initialization must not load
Persona databases, credentials or private handles into the isolated worker.

**QEMU/TCG is the machine implementation, not the trusted security boundary.**
A malicious guest can attack its translator and device emulation. Evaluate
arbitrary native code execution inside the worker, including direct host syscalls,
Binder use, passed/inherited handles and resource exhaustion. The intended
post-QEMU containment is Android's host process/UID/SELinux enforcement plus narrow
brokers. This remains unproved and still exposes the host kernel and allowed
services; isolation is not a promise of no host attack surface. Separate guest
kernel execution is necessary for this direction, but by itself does not make
TCG an isolation guarantee. Broker parsers, supervisor, verification and host
kernel/service paths that can breach containment belong in the TCB analysis.

## Minimal theoretical capabilities

| Resource | Candidate delegation | Authority excluded / question to prove |
|---|---|---|
| Guest boot/image/disk | Exact pre-opened FDs; immutable boot/OS read-only, per-instance scratch/userdata writable only where needed | No directory FD, path traversal, arbitrary open request, backing-file discovery or broad management filesystem. Verify kernel/initrd/firmware loaders as well as block storage. |
| Display | Bounded framebuffer/shared-memory handles with fixed dimensions, stride, format, ownership and quotas | No direct GPU passthrough or unrestricted host surface acquisition. Malformed/oversized frames must not compromise the presenter. |
| Input/control | Fixed typed, bounded messages for the specific VM and epoch | No arbitrary shell/exec, generic Binder proxy, unrestricted QMP or worker-selected host operations. |
| Networking | Initially absent; later explicitly delegated socket/network capability only after proof | No assumed ambient unrestricted host network, resolver, physical-network bind or unrestricted listening/forwarding. |
| Host personal/device data | Absent by default; explicit Real-mode brokers only when separately reviewed | No ambient camera, microphone, location, clipboard or external-storage access. A guest permission is not host authority. |
| Management | Only the narrow interface needed for this VM's operation | No Persona master state, signing/update secrets, credentials, policy database, peer image or arbitrary host Binder/service authority. |

FDs and shared-memory mappings are real authority, not harmless numbers. Closing
the management copy does not revoke a worker duplicate or existing mapping.
Investigate broker-enforced epochs and stop/kill/reap for capabilities that cannot
be withdrawn in place. Account for framework-inherited descriptors, logging,
Binder and app startup code rather than claiming an empty process.

## Guest root and Persona design direction

The proposed normal production guest exposes no usable `su`, Magisk,
general-purpose root daemon, root for ordinary apps or production ADB root.
That is distinct from a possible narrowly privileged guest-management component:
a dedicated identity/SELinux domain as appropriate, a fixed typed management
protocol, no arbitrary shell/exec and no APK-accessible "become root" interface.
Its potential tasks include locale, language, timezone, virtual location,
carrier/telephony configuration and controlled guest identity inputs. This
component is unimplemented and its authority/authentication need later review.
A compromised guest component must still not become host management authority.

Prefer Persona as actual guest-visible virtual-device/system state over API-result
rewriting: region, locale, language, timezone, virtual location, carrier,
SIM/telephony metadata, selected device/build/identifier surfaces, and appropriate
display/network metadata. This is a design hypothesis, not a claim of complete
surface coverage. Persona master state remains host-side, with only approved
scoped outputs delivered to a guest. Guest root absence is not the host boundary;
malicious code may compromise the guest OS anyway.

Genuine host facts should not enter guest authority unless an explicit Real-mode
broker authorizes scoped disclosure. PDVA should not expose genuine facts and
then try to hide them from rooted guest apps. Android's host sandbox still permits
some native worker observations of host properties, time, resource behavior and
other metadata; inventory those surfaces and guest-observable channels. Absolute
concealment after arbitrary worker compromise is not established by isolatedProcess.
Do not promise universal spoofing, physical-device identity or attestation
equivalence. Preserve **Real / Decoy / Empty / Deny**, fail-safe missing/corrupt
Persona behavior and **no host-GPS fallback**. Persona geography and public-IP
geography are separate obligations.

## Network and graphics hypotheses

The isolated worker should ideally have no ambient unrestricted network authority.
AOSP's passed-socket allowances motivate investigation of narrow socket/FD
delegation or a separate bounded network broker; they do not demonstrate a working
backend. A socket delegated too broadly can retain real egress authority after a
policy change. SLIRP in Podroid/Linxr/QubeVM does not by itself solve that problem.
Default Linux-fixture experiment: no virtual NIC, no SLIRP, no socket delegation.
Direct socket creation and inherited network handles are still tested from native
worker code. Guest network absence alone cannot show worker network denial.

For later networking, identify every actual socket-producing process/UID and
independently prove external host VPN inheritance. PDVA does not take the host
`VpnService` slot. A required route that cannot be verified fails closed. DNS,
UDP, TCP, IPv4/IPv6, QUIC/Cronet, WebView, background/secondary/system processes,
pending packets and VPN loss/change/reconnect are separate evidence obligations.
The feasibility of ordinary-app race-free enforcement remains Unknown; this
proposal does not relax [the network contract](../networking.md).

Initially avoid direct GPU passthrough. Investigate virtio-gpu/2D or a framebuffer,
with guest software rendering/SwiftShader as a possible first Android compatibility
path and an explicit host presentation broker. Software rendering can still have
large CPU/memory/thermal costs. A Linux test pattern is not Android compositing,
video, Vulkan, WebView or app-graphics compatibility. Accelerated graphics and
additional display/native handles require a separate TCB/security review.

## Controlled guest image and store-neutral transport

The logical artifacts are a PDVA host APK/app and one controlled signed PDVA
Android guest-image line. Transport is not the trust root: PDVA cryptographically
authenticates its approved image before use regardless of how bytes arrive.
No signing algorithm, keys or production verifier is selected in this research.

| Possible transport | Hypothesis / separate constraint |
|---|---|
| Local file for owner/development use | Import only the official signed PDVA image, not arbitrary ROMs. A local file is not automatically trusted. |
| GitHub Releases or similar | Possible early-tester delivery; image authentication remains independent of hosting. |
| Third-party store mechanisms | Evaluate size, update, execution and distribution policies separately. |
| Google Play Asset Delivery | Possible later Play delivery; availability and policy fit require a dedicated review, not an approval claim here. |
| F-Droid | Feasibility independently depends on complete source, build recipes, licenses and redistribution conditions. A historical Limbo recipe does not approve PDVA. |

Investigate immutable OS state separated from persistent userdata, explicit
image/runtime ABI compatibility and a rollback policy. An Android N to N+1 update
may preserve userdata only through tested migration and recovery, including
interrupted updates, incompatible snapshots, policy/Persona state and downgrade
restrictions. Transport changes must not change image acceptance policy. Do not
redistribute Google proprietary binaries without rights; Play/GMS compatibility
and integrity remain a separate Gate E issue.

Initial controlled guest target remains **Android 17 / API 37**. A stable PDVA
virtual-hardware/broker contract should, where feasible, let future Android releases
be image/platform rebases. Migration to Android 18/19 requires explicit tests and
may fail; it is not assumed seamless. No guest-version chooser, arbitrary ROM
import or other guest OS is added as product functionality. The tiny Linux fixture
exists only to test host authority before investing in an Android build.

## Governance and conditional progression

Existing requirements cover these obligations; all mechanism choices here remain
hypotheses. No requirement, ADR, CI rule or gate state is changed. After a scoped
successful isolated-QEMU experiment, the next **proposal** is a controlled Android
17 complete-guest spike: investigate upstream QEMU `virt`, selected virtio devices,
a stable virtual-hardware/broker contract and AOSP/Cuttlefish references.

A tiny Linux pass is not Gate 0 Passed and does not itself authorize complete-guest
implementation. First review a credible path to the complete interactive guest,
shippability/provenance and defensible prospective boundary, then record a scoped
Gate 0 disposition under current governance. Only the required reviewed Gate 0
pass permits Gate A implementation. This PR defines that conditional work; it
implements neither experiment nor Android guest.
