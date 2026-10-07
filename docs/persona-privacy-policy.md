# Persona and privacy policy

These are deliberately re-adopted PDVA semantics, defined by
[PDVA requirements](requirements.md), not inherited predecessor requirements.
No implementation or surface coverage is established.

| Mode | Required meaning |
|---|---|
| Real | Explicit, scoped, visible genuine-data disclosure through a controlled PDVA path. It is never unrestricted passthrough or an enforcement failure. |
| Decoy | Deliberate synthetic values within a defined coherent Persona and scope. No genuine fallback when generation fails. |
| Empty | A deliberate empty result where valid and unambiguous for that surface; not a fabricated success for an operation that requires data. |
| Deny | Explicit refusal with honest failure semantics and no side-channel genuine disclosure through an alternate path. |

A guest Android permission never automatically grants corresponding host personal
data. Host permission and PDVA disclosure authorization are separate checks.
Never silently fall back to host GPS, including fused/SDK/native alternatives.
Unsupported or unresolved integrations stay blocked from genuine disclosure;
policy failure, absent data and corruption do not select Real.

Persona values should remain coherent and stable until deliberate change, reset
or rotation. Research must define scope (instance/app/session as appropriate),
cross-surface relationships, persistent storage, atomic changes and revocation.
Master state stays outside hostile guest authority; expose only necessary outputs.
Resetting a Persona does not erase remote observations or sessions.

Potential surfaces include region, locale, language, timezone, virtual location,
carrier, SIM/telephony metadata, selected Android/device descriptors, build
descriptors, display characteristics, Android identifiers, network metadata and
related guest-visible state. Each needs a surface-specific mode contract and tests
across Java, native, SDK, cached and lifecycle paths. This list is a research
inventory, not a promise of universal spoofing or coverage.

Reported identity is not physical hardware identity. Changing descriptors cannot
create matching hardware-backed attestation or new APIs/ABI capabilities. Persona
geography and public network geography are separate; changing a virtual location
does not change public IP. [Networking](networking.md) and
[Google compatibility](google-compatibility.md) retain independent limitations.
