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

## Identity coverage and platform semantics

This clarifies PDVA-REQ-009–021, 022–027, 031–032 and 039–043; it adopts no
architecture or implementation. The protection obligation is separation: real
host identifiers must not reach adversarial guest apps or guest-native code through
unapproved interfaces. Changing a guest API string is not evidence of that boundary.
Any Real disclosure needs explicit scoped authorization, visible behavior and
independently reviewed enforcement. No host IMEI passthrough is authorized here.

**Platform fact (official documentation checked 2026-10-24):** Android 10 introduced
restrictions on persistent identifiers. `READ_PHONE_STATE` alone does not authorize
an ordinary Android 17 app to read IMEI. The historical overview is not a substitute
for each current method's contract. Do not assume ordinary social-media apps can
read the host IMEI, or possess privileged permissions or carrier roles.
[Android 10 privacy changes](https://developer.android.com/about/versions/10/privacy/changes#non-resettable-device-ids).

**Platform fact:** `getImei(int)` permits specified privileged, managed-device,
carrier, default-SMS-role or `USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER` callers. Without
an applicable exception, target SDK 29+ throws `SecurityException`; target SDK
28 or lower with `READ_PHONE_STATE` receives null, otherwise an exception.
Unavailable IMEI returns null. `getMeid` is deprecated since API 36; the current
reference specifies null on Android 25Q2+ in its restricted-caller behavior and
separately describes older CDMA feature/permission failures. Do not copy the IMEI
exception table to MEID or assume CDMA support. Record OS, method/overload, target
SDK, feature declarations, permissions, role and carrier privileges separately.
[TelephonyManager](https://developer.android.com/reference/android/telephony/TelephonyManager#getImei(int)),
[MEID](https://developer.android.com/reference/android/telephony/TelephonyManager#getMeid()).

**Platform fact:** Modern `ANDROID_ID` is scoped to signing key, user and device;
factory reset or signing-key changes can change it. Instant Apps have their own
installation/clear lifecycle. A global arbitrary value shared by every app is not
correct Android ID behavior. Per-app separation must respect signing-key sharing,
not invent a package-only scope or promise rotation on every restart.
[Settings.Secure](https://developer.android.com/reference/android/provider/Settings.Secure#ANDROID_ID).

**Platform fact:** `SubscriptionManager.getPhoneNumber(int)` requires
`READ_PHONE_NUMBERS`, privileged phone-state access or carrier privileges; absent
data produces an empty string, missing permission a security exception, absent
subscription feature an unsupported-operation exception, and unavailable telephony
process an illegal-state exception. Number formatting/correctness is not guaranteed.
[SubscriptionManager](https://developer.android.com/reference/android/telephony/SubscriptionManager#getPhoneNumber(int)).
Neither a displayed number nor a synthetic carrier establishes a working line,
cellular service, calling, SMS reception or successful phone verification.

## Identity-surface contract matrix

The four modes above apply separately to every row; there is no universal spoofed
identifier. Each future surface record must specify the requested mode, exact API
behavior, authorized source, scope/lifetime, consistency, persistence, absent or
unsupported outcome, independent test, failure/rollback and current evidence.
Decoy uses approved synthetic guest state only where platform semantics support it;
Empty and Deny use the method's appropriate absence/refusal behavior. An unavailable
telephony implementation may require absence or denial rather than an invented
physical identifier. Unsupported output never selects Real.

All rows are **Unknown** for enforcement and **Not tested** for PDVA runtime.
Candidate authorities are review obligations under the existing
[boundary inventory](security-boundaries.md), not selected implementations.

| Separately scoped surface | Authorized source, scope and consistency to specify | Enforcement authority to identify / independent validation |
|---|---|---|
| IMEI, MEID; IMSI, ICCID | Guest telephony state only when legitimately supported; otherwise method-specific absence/denial. Separate equipment, subscriber, SIM, slot and subscription lifetimes; no host radio source by default. | Guest service permission/role checks plus the actual host boundary; compare Java, Binder, native and file/property paths under each caller class. |
| Android ID | Guest platform identity scoped by signing key/user/guest device; stable across ordinary restarts. Explicit reset, signing-key and restore semantics; no host ID seed. | Guest settings authority plus protected instance state; independently compare same/different signing keys, users and guest instances. |
| Phone number, operator/carrier display, MCC/MNC | Declared guest subscription state; validate display-name/code relationships, number structure and subscription count without claiming real service. | Telephony/subscription services and phone-feature declarations; compare APIs, callbacks, settings and unsupported-feature behavior. |
| SIM country and network country | Distinct subscription and network observations; roaming can legitimately differ. Persona geography must describe intentional differences rather than force equality. | Guest telephony/radio interfaces and boundary; test absent SIM/network, multi-subscription and changed-state cases. |
| Manufacturer, model, build, serial and hardware descriptors | Controlled guest build/capabilities or explicitly supported Persona fields; never imply a certified handset or invent absent APIs/ABI. | Guest build/property/filesystem authorities plus host isolation; compare framework, native libraries, properties, files and reported features. |
| Language, locale, region, timezone | Persistent guest/Persona settings with declared app/user overrides and geographic relationships; not an automatic host-settings mirror. | Guest settings/configuration and protected Persona policy; compare Java/native/WebView and lifecycle observations. |
| Virtual GPS/location | Explicit virtual location source for Decoy; valid absence/refusal for Empty/Deny. Real requires separately authorized disclosure. | Reviewed location boundary and every provider/SDK/native path; force mechanism failure and manager loss and prove no host-GPS fallback. |
| Other identifiers and fingerprints | Separately inventory advertising/app-set/install IDs, accounts/tokens, Wi-Fi/Bluetooth identifiers, sensors, display, fonts, graphics/audio/timing, cookies and browser storage. Define each scope/reset independently. | Relevant guest services, storage and every integration/backend; test alternate APIs, caches, cross-app and cross-instance correlation with synthetic fixtures. |
| Network metadata | Host routing and public IP geography are separate from GPS, SIM/network country and locale/timezone; include DNS, WebRTC and active external host VPN policy. | Actual socket producer and routing authority; independent endpoint/packet observations under [networking](networking.md), including VPN loss. |

For every row, preserve authorized state across ordinary restart; deliberate change,
rotation, update, restore and reset require a defined coherent transition. On missing,
corrupt, stale or partially migrated state, keep genuine disclosure blocked, report
failure and prevent rollback from restoring revoked authorization. Exact safe output
and recovery behavior must be defined per method before support is claimed. These
are acceptance obligations, not evidence that persistence or revocation exists.

Ordinary browser web APIs do not simply expose hardware IMEI. Browser/WebView
fingerprinting and native bridges are separate surfaces: configuration, rendering,
storage and network observations can correlate visits and accounts. A bridge with
native authority needs its own review. The [W3C fingerprinting guidance](https://www.w3.org/TR/2025/NOTE-fingerprinting-guidance-20250925/)
describes correlation risks; it is not evidence of PDVA protection.

No Persona guarantees unlinkable social-media accounts, successful phone verification,
unobservable automation, retail-handset certification, Play Integrity success,
hardware-backed attestation, universal financial/social-media/DRM compatibility,
or concealment of server-side account history and network correlations. Reset cannot
erase information already observed remotely. No hooks, package rewriting, host system
interception, hidden permissions, integrity/licensing/attestation/anti-tamper bypass,
or host VPN takeover is authorized. Future evidence uses synthetic fixtures and
structural descriptions only; do not collect or publish user-real identifiers,
locations, account data, fingerprints or Persona secrets.
