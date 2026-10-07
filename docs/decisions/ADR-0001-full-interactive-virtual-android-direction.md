# ADR-0001: Full interactive virtual Android direction

**Status: Accepted.** **Date: 2026-10-07.**
**Authority:** explicit project-owner instruction for PDVA's initial foundation.

## Context and decision

PDVA will investigate a complete interactive virtual Android guest as its product
direction rather than making hostile applications execute primarily against host
Android with a growing mediation layer. It is a new Android-only product lineage.
The initial guest is Android 17 / API 37, normally unrooted, from one controlled
supported image line. Arbitrary ROM import and a guest-version chooser are out of
initial scope.

No VM engine is selected. Feasibility is not established. The actual enforcement
boundary is unresolved. The word "virtual" supplies no security evidence and
does not establish superiority over other architectures.

## Constraints and consequences

[Gate 0](../feasibility-gates.md) must pass before a production VM architecture
can be claimed or complete-guest implementation begins. The normal host is a
stock non-rooted device running an ordinary distributable third-party app, without
host root, Magisk, Xposed, LSPosed, custom ROM, patched kernel, privileged/system
installation, platform signing, production ADB, userdebug/eng builds or OEM-only
integration. A permission obtained for development is not production authority.

App virtualization, Binder proxying alone, APK/DEX rewriting, Java/native hooking,
namespace tricks and similar in-host execution cannot silently become the primary
security boundary. A failure of this direction requires STOP, owner-approved
NARROW, or a new owner-approved REDESIGN ADR. It does not authorize weakening the
boundary to preserve a schedule.

PDVA management/control-plane state must remain outside hostile guest authority.
The intended immersive phone experience must retain a reliable route to PDVA
management and respect ordinary-app host System UI limitations. PDVA does not
occupy the host VPN slot or implement a production host `VpnService` under this
decision. Google Play remains a compatibility objective, independently gated.

## Evidence and alternatives

[Gate 0 evidence](../evidence/gate-0-platform-authority.md) excludes several
restricted platform paths for the ordinary installed-app category in the
inspected sources. User-space emulation and other legitimate mechanisms remain
Unknown; no engine is adopted. Gate 0 is **Unresolved**.

[Privacy Decoy findings](../reference/privacy-decoy-history/negative-findings.md)
remain historical evidence, not PDVA authority or VM-isolation evidence. Its
transformation-first direction is not inherited. Neither its scoped failures nor
its incomplete Phase II establishes a result for PDVA. This ADR accepts only the
owner's direction and foundation; no runtime or image is added.
