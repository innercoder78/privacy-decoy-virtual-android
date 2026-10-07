# PDVA requirements register

These are PDVA-native obligations, not implementation evidence. All are **Required**;
technical satisfaction is unproven. MUST/MUST NOT are mandatory; SHOULD expresses
a recommendation whose deviation needs documented justification. IDs are consecutive,
permanent and begin at PDVA-REQ-001. Retain superseded IDs with their decision history.

| ID | Family | Obligation | Validation gate |
|---|---|---|---|
| PDVA-REQ-001 | Product | PDVA MUST be Android-only and investigate a complete interactive virtual Android phone presented by an ordinary Android application. | 0, A |
| PDVA-REQ-002 | Host | Normal operation MUST be an ordinary distributable user-installed third-party app on supported stock non-rooted production `user` devices. | 0, G |
| PDVA-REQ-003 | Host | Normal operation MUST NOT require root, Magisk, Xposed, LSPosed, custom host ROM, patched host kernel, privileged/system installation, platform signing, production ADB, userdebug/eng builds or OEM-only integration. | 0, G |
| PDVA-REQ-004 | Guest | The initial guest MUST be Android 17 / API 37 and normally unrooted. | A, F |
| PDVA-REQ-005 | Guest | PDVA MUST own one controlled supported guest-image line; arbitrary ROM import, ROM marketplaces, random community images, other guest operating systems and a version chooser MUST be outside initial scope. | A, F |
| PDVA-REQ-006 | Architecture | This bootstrap MUST NOT select a VM engine or claim feasibility or an established enforcing guest/host boundary. Gate 0 MUST pass before a production VM architecture is claimed or complete-guest implementation begins. | 0 |
| PDVA-REQ-007 | Architecture | In-host app virtualization, Binder proxying alone, APK/DEX rewriting, framework/native hooking, namespace tricks or similar mechanisms MUST NOT silently replace the full-guest primary boundary. | 0, B |
| PDVA-REQ-008 | Governance | Material product or architecture changes MUST have a PDVA ADR and explicit owner approval; foundational failure MUST lead to STOP, approved NARROW or deliberate approved REDESIGN. | All |
| PDVA-REQ-009 | Security | Every guest-installed app, SDK, native library, dynamic component, subprocess and guest-native path MUST be treated as adversarial. | B |
| PDVA-REQ-010 | Security | Every claimed boundary MUST identify its actual enforcing authority, TCB and evidence, or be recorded Unknown/unresolved; the VM label MUST NOT count as evidence. | B |
| PDVA-REQ-011 | Security | The boundary inventory MUST address memory, filesystem, process, native-code and syscall containment; kernel/devices, Binder/services, shared memory, descriptors/handles, virtual devices, escape resistance and exhaustion. | B, G |
| PDVA-REQ-012 | Control plane | Management state, Persona master state, credentials, signing/update secrets, image signing material, tokens, policy, host files and other guest instances MUST remain outside hostile guest authority. | B, F |
| PDVA-REQ-013 | Control plane | Guest/host interfaces MUST be explicit, narrow, least-privilege and authenticated where necessary, with caller/instance authorization, validation, revocation and safe failure. | B |
| PDVA-REQ-014 | Integration | Display/input, audio, clipboard, camera, microphone, sensors, notifications, file/storage sharing and other host integrations MUST have explicit policy and boundary evidence before disclosure. | B, C |
| PDVA-REQ-015 | Security | Network isolation, image integrity and snapshot state MUST have explicit enforcement/evidence owners; mandatory unknown protection MUST NOT be represented as safe. | B, D, F |
| PDVA-REQ-016 | Privacy | Policy modes MUST be Real, Decoy, Empty and Deny, deliberately adopted as PDVA concepts. | B |
| PDVA-REQ-017 | Privacy | Real MUST mean explicit, scoped, visible genuine-data disclosure through a controlled PDVA path, never uncontrolled passthrough or enforcement failure. | B |
| PDVA-REQ-018 | Privacy | Host GPS MUST NOT silently become fallback; a guest Android permission MUST NOT automatically grant corresponding genuine host personal data. | B |
| PDVA-REQ-019 | Persona | Persona values SHOULD be coherent and stable until deliberate change, reset or rotation; scopes and state transitions MUST be explicit. | B, C, F |
| PDVA-REQ-020 | Persona | The design MUST assess region, locale, language, timezone, virtual location, carrier, SIM/telephony metadata, Android/device/build descriptors, display, identifiers and network metadata as potential Persona surfaces. | B, C |
| PDVA-REQ-021 | Persona | Reported identity MUST be distinguished from physical hardware identity and matching hardware-backed attestation; Persona geography MUST be distinguished from public network geography. | B, D, E |
| PDVA-REQ-022 | Network | PDVA MUST NOT occupy the host VPN slot or implement a production host-side VpnService absent a later explicit owner-approved ADR. | D |
| PDVA-REQ-023 | Network | The intended path MUST be guest app → guest Android network → PDVA guest/host backend → host Android network → external host VPN when applicable → Internet; coverage MUST be evidenced, not assumed. | D |
| PDVA-REQ-024 | Network | Guest traffic MUST NOT intentionally bind to physical/underlying networks to bypass a required host VPN. | D |
| PDVA-REQ-025 | Network | Required external-VPN routing that cannot be established or verified MUST fail closed, including change/loss/reconnect, without silent physical egress. | D |
| PDVA-REQ-026 | Network | Evidence MUST cover Java/native TCP, UDP, DNS, IPv4/IPv6, WebView, QUIC/Cronet, guest system services, background/secondary processes, reconnects, provider changes and VPN loss, with producer attribution and independent packets. | D, G |
| PDVA-REQ-027 | Network | A guest VPN MUST be treated separately from external host-VPN inheritance; historical broker/fixture architecture MUST NOT be inherited as PDVA production architecture. | D |
| PDVA-REQ-028 | Google | Guest account sign-in, Play Store search, genuine Play installation, supported updates and compatible app execution MUST be maintained as objectives, not established capabilities. | E |
| PDVA-REQ-029 | Google | Technical feasibility, redistribution rights, user-local acquisition, certification/compatibility and Play Integrity/attestation behavior MUST be evaluated separately. | E |
| PDVA-REQ-030 | Google | Proprietary Google binaries MUST NOT be committed or redistributed without established rights; sideloaded APKs MUST NOT be represented as Play-installed. | E, F |
| PDVA-REQ-031 | Google | PDVA MUST NOT forge or bypass Play Integrity, hardware-backed attestation, certificate validation, licensing, DRM, anti-tamper or similar controls. | E |
| PDVA-REQ-032 | Google | PDVA MUST NOT promise retail-device/Play Protect certification, physical-device integrity or universal banking, payment, DRM or high-integrity app compatibility. | E |
| PDVA-REQ-033 | Guest | Core virtualization feasibility MUST remain independently testable without proprietary Google software. | 0, A |
| PDVA-REQ-034 | Supply chain | Before image trust/shipment, exact source, AOSP/kernel revisions, patches, build/device configuration, ABI, licenses, rights, reproducibility, cryptographic identity and signing/authentication MUST be documented. | F |
| PDVA-REQ-035 | Lifecycle | Guest updates, migration, rollback, snapshot compatibility, corruption recovery, vulnerability response and maintenance ownership MUST be documented and tested before shipment. | F, G |
| PDVA-REQ-036 | Supply chain | Every runtime, VMM, helper, image component, native dependency, build tool and reused source MUST pass immutable upstream, file provenance, license, dependency/native/binary inventory, reproducibility, security-history, TCB and update-ownership review with an explicit adoption decision. | 0, B, F |
| PDVA-REQ-037 | Supply chain | A permissive root license MUST NOT be treated as proof for all bundled files; opaque security-critical binaries MUST NOT enter the TCB merely because a demo works. | B, F |
| PDVA-REQ-038 | Bootstrap | This PR MUST add no VM implementation/execution, engine import, Android runtime, guest/ROM/kernel/VM disk image, proprietary package, opaque runtime, hypervisor binary, AAR, APK, AAB or SO. | Foundation |
| PDVA-REQ-039 | Evidence | Evidence MUST distinguish verified platform fact, repository/source/direct observation, upstream claim, inference, hypothesis, assumption and Unknown; Unsupported and gate states MUST remain separate. | All |
| PDVA-REQ-040 | Evidence | Records MUST identify exact source/ref or artifacts, environment/build/host/device/ABI/date, procedure, observation, limits and supported/excluded conclusions; failed retrieval MUST remain Unknown. | All |
| PDVA-REQ-041 | Evidence | Compatibility, boot, launch, missing leak observations and static absence MUST NOT imply security; documentation MUST NOT pass a gate; no aggregate safety/privacy score may be used. | All |
| PDVA-REQ-042 | Testing | Strong production isolation claims MUST require stock non-rooted physical-device release-equivalent evidence and independent security review. | B, G |
| PDVA-REQ-043 | Testing | Future tests MUST include escapes, host files/properties/proc/sys, native/direct syscalls, Binder, shared memory, passthrough, inherited handles, guest/host IPC, malformed brokers, management authorization, network bypass, image/snapshot tampering, exhaustion, death and recovery. | B–G |
| PDVA-REQ-044 | Platform | Guest baseline MUST be distinguished from host minimum/version/device/OEM/ABI support; host minimum is Unknown and no device support is claimed until evidenced. ARM64 MUST be investigated without implied support. | 0, G |
| PDVA-REQ-045 | Platform | Emulator, Cuttlefish, root, userdebug/eng and development-grant evidence MUST be labeled research and MUST NOT substitute for physical production evidence. | All |
| PDVA-REQ-046 | UX | The immersive virtual-phone experience MUST retain a clear reliable escape to PDVA management and MUST NOT claim host OS replacement or System UI control beyond ordinary-app authority. | C |
| PDVA-REQ-047 | UX | Research MUST address edge-to-edge/bars, touch, IME, sizing/density, rotation, gestures, accessibility, suspend/resume, interruptions, multitasking/PiP, death, background limits and restoration. | C, G |
| PDVA-REQ-048 | Hygiene | All public surfaces MUST exclude secrets, tokens/keys, Google credentials, private accounts, host identifiers, Persona secrets, confidential paths, raw sensitive captures and proprietary software without rights. | All |
| PDVA-REQ-049 | Hygiene | Root entries MUST be limited to .github/, android/, docs/, .editorconfig, .gitattributes, .gitignore and README.md absent a reviewed explicit need; no license/build/wrapper/binary is added by convention. | Foundation |
| PDVA-REQ-050 | CI | Bootstrap CI MUST be cheap standard-library foundation validation, with read-only permissions, a short timeout and reviewed immutable official checkout pin; no Android/VM/Gradle/NDK/emulator suite. | Foundation |
| PDVA-REQ-051 | CI | Validation MUST inspect allowed roots, Markdown file links, disallowed binaries/signing filenames, unique consecutive PDVA requirements, initial ADR numbering and historical provenance notices. | Foundation |
| PDVA-REQ-052 | History | Historical material MUST be classified rather than bulk-copied; predecessor numbering, coverage vocabulary, requirements, ADRs and results MUST remain historical/non-normative for PDVA. | Foundation |
| PDVA-REQ-053 | History | Every historical-reference document MUST state origin, exact authoritative source SHA, original scope, revalidation duty and that app mediation evidence is not VM-isolation evidence. | Foundation |
| PDVA-REQ-054 | Governance | The immediate roadmap MUST remain Gate 0 research; dependent work MUST stop on foundational failure rather than weaken the ordinary-app boundary. | 0–G |

## Family traceability

| Requirement family / IDs | Canonical elaboration | Evidence owner / acceptance |
|---|---|---|
| Product/host/guest/architecture/governance: 001–008, 033, 044–045, 054 | [Governance](governance.md), [ADR-0001](decisions/ADR-0001-full-interactive-virtual-android-direction.md), [architecture](architecture.md), [platform](platform-support.md), [roadmap](roadmap.md) | Gate 0 [authority record](evidence/gate-0-platform-authority.md), then A/G; owner approves changes |
| Security/control plane/integration: 009–015 | [Boundaries](security-boundaries.md), [threat model](threat-model.md) | Gate B interface and TCB evidence; D/F for dependent surfaces |
| Privacy/Persona: 016–021 | [Persona policy](persona-privacy-policy.md) | Gate B policy tests, C coherence, D/E identity limitations, F persistence |
| Network: 022–027 | [Networking](networking.md) | Gate D independent observation; G physical qualification |
| Google: 028–032 | [Google compatibility](google-compatibility.md) | Gate E separately scoped technical/rights/integrity review |
| Supply chain/lifecycle/bootstrap: 034–038 | [Source policy](source-provenance-policy.md), [catalog](source-reference-catalog.md), [image lifecycle](guest-image-lifecycle.md) | Adoption review before use; B/F/G qualification |
| Evidence/testing: 039–043 | [Acceptance criteria](acceptance-evidence-criteria.md), [testing](testing.md) | Each gate reviewer; independent security review before claims |
| UX: 046–047 | [UX](ux.md) | Gate C with physical matrix G |
| Hygiene/CI/history: 048–053 | [Contributing](../.github/CONTRIBUTING.md), [historical index](reference/privacy-decoy-history/README.md), [reuse](reference/privacy-decoy-history/reuse-classification.md) | Foundation validator plus human diff/provenance review; not a technical gate pass |
