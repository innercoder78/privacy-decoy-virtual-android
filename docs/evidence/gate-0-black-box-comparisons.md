# Gate 0 black-box comparison plan

**2026-10-07. Documentary review only; no product installed or tested.**
Gate 0: **Unresolved**. A–G: **Not reached**. These products are behavior/UX
references, not selected engines, source dependencies or security evidence.

## Virtual Master: established metadata and limits

Treat Virtual Master as **CLOSED-SOURCE / BLACK-BOX** for this investigation.
The [Google Play listing](https://play.google.com/store/apps/details?id=com.clone.android.dual.space)
identifies package `com.clone.android.dual.space`, title Virtual Master - Android
Clone and publisher Eden Technology HongKong Limited. At retrieval it displayed
an October 1, 2026 update and release notes about crashes in Android 11/12 virtual
machines. These are live distribution metadata, not an immutable APK identity.
The [publisher site](https://www.virtualmaster.app/) is a product/download reference.
No APK hash, extracted manifest, ROM content, source revision or physical run was
obtained here; effective permissions and kernel implementation are **Unknown**.

**Upstream claims:** the Play description advertises local Android environments,
background running and Vulkan. Its FAQ describes first-run image provisioning and
faster later starts, with illustrative image/storage sizes. Its privacy/isolation
marketing is not accepted as evidence. Old FAQ Android versions and newer release
notes are not reconciled into a verified guest-version inventory.

**Inference limit:** current public evidence does **not** establish whether the
primary boundary is a distinct guest kernel. A VM label, root toggle, boot animation,
Android version or changed `uname` text cannot establish it. No product behavior
was directly observed by this review. User-observation hypotheses below are future
questions; they are not invented reports attributed to Tony or anyone else.

## Lawful observational checklist

For a future study, use a legitimately obtained release on a synthetic test device
and record package/version, artifact hash if lawfully obtainable, distribution
channel, test date and public host build/ABI. Observe documented UI/exports and
legitimately accessible manifests/release notes only. Do not bypass DRM, access
controls, account restrictions or unpack proprietary code beyond authorized lawful
observation. Do not redistribute APKs/ROMs or publish private captures in this PR.

Each row starts **Unknown / unobserved**. A future record must distinguish direct
observation, vendor statement, inference and unresolved conflicting evidence.

| Study surface | Reproducible question / observation to collect | Current result |
|---|---|---|
| ROM/download package and provisioning | What legally visible package/file structure, download phases, authenticated transport and first-run storage changes exist? Record visible facts; image format/signature verification remains Unknown without inspectable evidence. | Unknown |
| Host versus guest kernel | Compare legitimately visible kernel/build/uptime/boot observations and source provenance if available. Treat reported strings as potentially mediated; independent-kernel enforcement cannot be inferred from them alone. | Unknown |
| Boot | Cold start, boot animation, time to usable launcher, first versus subsequent boot, offline restart and failure/recovery behavior. | Unknown |
| System and data | What observable system/userdata persistence, partition presentation and read/write behavior differ? Does repair preserve data? | Unknown |
| Storage footprint | App, downloaded image, per-instance userdata, temporary/update staging and post-reset footprint; measure with synthetic data. | Unknown |
| Reset/factory reset/new device | Which synthetic apps/settings/identities persist, reset or rotate? Distinguish a fresh instance from a factory reset and account/server-side state. | Unknown |
| Root/su | Does normal operation expose usable su, a root daemon, Magisk or ADB root? Do not enable host privilege to make a reference fit PDVA. | Unknown |
| Carrier and location | Compare synthetic guest-visible carrier/SIM/location configuration, native/app/system observations and denial behavior; never use real host GPS as an unnoticed fallback. | Unknown |
| Locale/language/timezone | Change each via documented controls and record consistency, restart persistence and cross-app/system results. | Unknown |
| Camera/microphone | With each host permission denied/granted/revoked, which guest capability works and is capture visible? Record background and restart behavior using synthetic scenes/audio. | Unknown |
| Display/GPU | Observable resolution/density/refresh, software/accelerated options, graphics compatibility and resource cost; no inference about driver isolation. | Unknown |
| Keyboard/input/rotation | Touch coordinates, hardware/software keyboard, IME, clipboard boundaries, resize/rotation, accessibility and safe return to management. | Unknown |
| Network/DNS/VPN | Attribute producers; independently observe TCP/UDP, DNS, IPv4/6 and VPN loss/change/exclusions with controlled endpoints. VPN icon or connectivity does not prove routing. | Unknown |
| Notifications/background | Notification projection/actions, foreground indicators, screen-off, suspend/resume, host process death, restart and normal memory pressure. | Unknown |
| Android upgrades | Is an update an in-place migration, new instance or download? Observe synthetic userdata preservation, failed update, rollback and old image behavior. | Unknown |
| Host permission mapping | Build a permission-by-capability matrix, one documented grant/revoke at a time, including storage/network-related settings. Separate declared permission, granted permission and observed operation. | Unknown |

Study results may motivate PDVA provisioning, reset, display/input, device-data,
networking and upgrade UX. They cannot replace PDVA's source-built isolated-worker
experiment or authorize exposing host facts then attempting to conceal them in
guest API hooks. Any behavior requiring ADB/root/helper authority is labeled and
excluded from PDVA production evidence, even if useful as a comparison.

## VMOS, VPhoneOS and similar products

[VMOS product descriptions](https://app.vmos.com/) advertise an independent local
Android space, background operation and root features.
[VPhoneOS's site](https://vphoneos.com/) advertises virtual Android and guest Magisk
features. These are **upstream marketing claims**, not a reviewed kernel boundary,
rights assessment, safe implementation or PDVA compatibility result. Source,
exact artifact, effective authority and independently enforced boundary remain
**Unknown** for this record. Retain these and analogous products as black-box
comparisons unless independently inspectable implementation evidence is obtained.

Use the same checklist and evidence labels for each product/version; never transfer
an observation between products or assume a brand denotes one implementation.
No proprietary code, image or binary is imported. The inspectable shared-kernel
and WASM alternatives are separately classified in the
[source ledger](gate-0-userspace-vmm-sources.md).
