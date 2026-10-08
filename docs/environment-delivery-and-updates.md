# Proposed environment delivery and updates contract

**Design proposal, 2026-10-08.** Governed by **PROPOSED**
[ADR-0002](decisions/ADR-0002-signed-environment-delivery-and-compatibility.md), pending
Tony's explicit approval after review of the final text. The mandatory conditions
below describe the proposed contract if adopted; they do not add or amend the
[requirements register](requirements.md) before approval.

No downloader, catalog parser/verifier, UI, app self-update or image is implemented.
No production engine, signing algorithm/key, wire schema or image layout is selected.
Gate 0 remains **Unresolved**; A–G remain **Not reached**. The ordinary-app/full-guest
and one controlled Android 17 / API 37 direction in
[ADR-0001](decisions/ADR-0001-full-interactive-virtual-android-direction.md) is intact.
This document is the single detailed proposal; the ADR records decision authority,
[image lifecycle](guest-image-lifecycle.md) retains release qualification areas,
and [UX](ux.md) retains the wider virtual-phone experience.

## Separate identities and management authority

| Identity | Purpose and limit |
|---|---|
| PDVA APK version | Host application release (`versionName`/`versionCode`); useful for distribution and optional prerequisite constraints, insufficient as compatibility proof. |
| Host runtime ABI/protocol | Controlled, stable identifiers for the runtime interfaces implemented by this exact installed build. Never infer them from an APK version string. |
| Virtual hardware/device contract | Versioned device/interface capabilities that the runtime actually supports; separate from host CPU ABI and guest Android API. |
| Guest Android major line | Initially Android 17 / API 37 only; choosing a maintenance build does not authorize another major line. |
| Guest image build/version and schema | Exact immutable OS/build identity and image-format contract; a newer build can remain Android 17. |
| Persistent userdata schema | Mutable per-instance state and its supported migrations; OS compatibility does not imply userdata or snapshot compatibility. |

Trusted local capabilities come from the installed PDVA runtime and protected
management configuration. Remote metadata describes required capabilities; it
cannot grant missing interfaces or redefine the local runtime as compatible.
Management owns provisioning, verification, policy and activation outside hostile
guest authority. Guest apps, guest Android permissions and guest requests cannot
approve releases, replace trust anchors or acquire signing/update secrets.
The [enforcing boundary](security-boundaries.md) and verifier TCB remain unproven.

## Host package and first-run provisioning

Investigate a relatively small ordinary Android APK separate from the potentially
large controlled environment. Actual APK/image sizes, compression behavior, free
space margins and performance budgets are Unknown. Package size is a goal to
measure, not a numerical promise.

If no approved environment is installed, PDVA management offers
**"Download Android 17 Virtual Environment"**. The user starts provisioning.
Before consent, show the exact build/line, authenticated download byte count,
estimated installed and peak storage requirements, network/metered-network choice,
and available space. Download size derives from verified metadata, not an
unauthenticated asset label; storage estimation also needs the qualified layout,
staging, migration, userdata and recovery-retention costs. If required information
is missing or untrustworthy, do not start the image download.

Provide progress, pause/cancel where safe, retry/resume, and an explicit decision
before a large or metered transfer. Discovery does not authorize payload download
or installation. Cancellation cannot delete the active environment or userdata.
Space checks and bounded resource use continue during transfer and staging, not
only before download. Do not invent image sizes or storage budgets in this proposal.

## Transport and signed metadata

GitHub Releases is the preferred early distribution candidate, not a proven
permanent production hosting commitment. A future release could carry a signed
environment manifest/catalog and image parts; this PR publishes none.
GitHub is **untrusted transport**, never the root of image trust. Repository ownership,
release tags, HTTPS, asset names or GitHub's global latest endpoint do not authorize
an image. Another transport must preserve the same acceptance contract.

[GitHub's official release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas),
independently checked on **2026-10-08**, documents assets strictly **under 2 GiB**,
up to **1,000 assets per release**, and no total release-size or bandwidth limit.
This is the documented constraint at review time, not a PDVA availability,
throughput or perpetual capacity guarantee. Recheck current constraints and measured
hosting behavior before delivery qualification.

A large image may need independently verified chunks, bounded retries and resumable
recovery. Resume state must bind to the exact authenticated manifest/image/part
identity; changed content invalidates affected partial bytes. Verify each completed
part and the complete reconstructed artifact against authenticated metadata before
acceptance. Neither a range response nor an ETag is cryptographic proof. The signed
layout must bound output size as well as transfer size; chunking, unpacking and
reassembly must not introduce path traversal or unbounded decompression/storage.

`AndroidManifest.xml` describes an Android APK and its Android components and
permissions. It is distinct from PDVA's proposed remotely delivered signed
environment metadata. "Catalog" here means authenticated discovery/policy metadata;
"environment manifest" means authenticated metadata for one exact image. They may
be separate signed objects or a combined design; their relationship is unresolved.
Any split design must authenticate the binding between catalog policy and manifest.

### Metadata information to qualify

The following is an information model, **not a finalized format or JSON schema**.
There are no example signatures, production keys or fabricated artifact hashes.
Unknown mandatory schema/semantics must cause rejection, not permissive parsing.

| Information | Proposed coverage |
|---|---|
| Schema and signature identity | Metadata schema/version, object identity, authorized signing identity/role, covered content and authenticated catalog-to-manifest binding. Signature identities refer to locally authorized trust, not keys trusted merely because metadata includes them. |
| Environment identity | Controlled environment/line identity, guest Android major and API, exact image build/version and schema, selected stable/release channel where applicable. A channel is authenticated policy, not a global latest alias. |
| Runtime compatibility | Required host runtime ABI/protocol identifiers, host CPU ABI where needed, virtual hardware/device interfaces and supported capabilities. Match against trusted local declarations. |
| Optional APK prerequisites | Minimum/allowed app releases only where genuinely needed for management behavior or fixes; these supplement runtime/device compatibility, never replace it. |
| Payload identities | Exact manifest/image identity, cryptographic hashes, ordered part identities/hashes and sizes, complete-artifact identity, bounded reconstructed/installed size. Hash and signature algorithms await review. |
| Storage requirement | Required free storage for the qualified installation/update path, including staging, migration, userdata and retention; local estimates/reservations account for actual state and pressure. |
| Support and authorization | Supported, deprecated or revoked disposition; authenticated release ordering, policy/revocation epochs and channel eligibility; support/end-of-life policy. Deprecation is not automatic revocation or permanent permission. |
| State transitions | Allowed source/target image and userdata schemas, migration paths, rollback restrictions, snapshot/config/runtime compatibility and required policy epoch reauthorization. |
| Freshness and key lifecycle | Issuance/version/expiry, freshness rules, replay/freeze/rollback protection, authorized key rotation and compromise/recovery policy. Time and durable-state assumptions must be explicit. |
| Provenance | Immutable source/build reference, AOSP/kernel/patch/configuration/ABI/toolchain identity and linkage to reviewed rights, reproducibility and adoption records. A provenance locator is not proof of a completed review. |
| Distribution locators | Approved URLs or release/asset identities, permitted redirects/mirrors and bounded fetch behavior, authenticated as locators for exact expected content. A locator cannot authorize substitute bytes. |

### Trust, freshness and recovery

Bootstrap trust must be independently authorized with the PDVA application/management
release, outside hostile guest control. Metadata publication and signing roles,
key custody, review authority and recovery owner require a separate operational
design; do not store private signing material in the guest or public repository.
Rotation/recovery needs authenticated authorization from already trusted authority,
with a reviewed response to a lost or compromised root. Hosting or a new signature
from an unrecognized key cannot repair trust by itself. No algorithm, production
key, threshold scheme or metadata framework is selected here.

Propose protected management records of accepted metadata versions/policy epochs
and exact image identities to detect rollback and replay. Consistently signed
bindings should prevent mixing policy, manifests and chunks from different releases.
Signatures alone do not establish freshness: a host can freeze delivery at an old
validly signed release. Define expiry, trusted-time assumptions, bounded offline
use and authenticated freshness before claiming freeze resistance. App downgrade,
backup/restore, reinstall, clock rollback or lost local state must not silently
reset anti-rollback protection; durable-state and trust-recovery mechanisms remain
Unknown. Until the required authorization can be established, fail closed with
the unresolved reason.

Expired metadata, unauthorized/expired/revoked signing identity, compromised image,
and unavailable transport need distinct failure explanations. A separately
qualified recovery authority/path may be needed; a signature exception or an
older vulnerable image is not recovery. Parser limits, validation order and key
management are security-critical TCB work needing provenance and adversarial review.

## Resolve the newest permitted compatible image

An older PDVA resolves the newest **permitted compatible** image for its approved
line/channel and actual capabilities. It never blindly follows the newest GitHub
release. Proposed resolver order:

1. Authenticate metadata, its bindings, schema, freshness and policy authority.
2. Restrict candidates to the controlled Android 17 line and selected authorized
   channel; apply support, revocation and anti-rollback policy.
3. Match required runtime/protocol, hardware/device, image schema and applicable
   APK prerequisites against trusted local capabilities. Unknown support is failure.
4. For updates/restores, require a qualified path from the actual current image,
   userdata and snapshot/config/policy state. A missing migration is incompatibility.
5. Choose the newest remaining candidate using authenticated release ordering,
   with deterministic selection rules still to be specified. Recheck before acting.

Illustratively, PDVA 1.x and PDVA 2.x may select different maintenance builds within
Android 17 because their implemented runtime/device contracts differ. These labels
are hypothetical, not released versions or a compatibility matrix. An authenticated
newer image requiring a new interface may be explained to the user, but its payload
cannot be downloaded/activated by the older runtime. Catalog metadata retrieval
for that explanation is separate from image download.

No permitted compatible candidate means a specific management outcome, not fallback
to global latest, arbitrary image import or an unverified previous release.
An optional newer feature/build remains optional for an authorized current image;
a prerequisite update is mandatory only to use the desired incompatible environment.
If policy revokes the current environment, continued use is a separate safe-failure
question, not an optional-upgrade promise.

## Acceptance at each lifecycle transition

**An environment must be supported by the installed PDVA runtime before download,
installation, update, restore or boot.** Authentication, current authorization and
compatibility are mandatory regardless of discovery preferences. Manual import,
user override, cached bytes, old metadata or rollback cannot waive them. Arbitrary
guest-image import is outside initial scope; even a future official-image local
recovery path would have to use the identical acceptance rules.

| Transition | Proposed required checks |
|---|---|
| Before image download or resume | Authenticate catalog/manifest and current policy, prove compatibility and transition eligibility, bind exact payload identity, obtain user consent and check storage/network constraints. Revalidate resumed parts; do not accept a stale session's decision. |
| Before installation or update staging | Revalidate authorization/compatibility and complete image/part integrity. Enforce layout/output bounds, space and the qualified source-to-target userdata transition. Staging is not activation. |
| Before activation | Revalidate against the installed app/runtime and current authenticated policy. Commit only the exact verified image plus compatible userdata/config generation atomically; concurrent app/policy/image changes invalidate the prior decision. |
| Before boot | Check selected immutable image identity/integrity, current permitted status, runtime/device/image/userdata compatibility and policy. A previously successful boot is not permanent authorization. |
| Before restore or rollback | Also check snapshot engine/runtime/image/config/schema identities, state integrity/confidentiality, allowed migration/rollback path and policy epoch. Reauthorize capabilities; do not revive stale tokens, credentials or permissions. |
| After APK upgrade/downgrade or recovery | Re-evaluate the installed environment and saved state against the actual resulting runtime capabilities and trust/policy state before the next activation, restore or boot. APK installation alone proves none of these. |

Prevent time-of-check/time-of-use gaps: bind the acceptance decision to exact
metadata, payload and state generations, keep verified bytes protected from
mutation, and coordinate activation with policy/runtime changes. The future
mechanism must make verification and use refer to the same bytes/state, including
a change while a guest is running. Gate B/F evidence must establish that hostile
guest/storage changes cannot bypass this; no locking, handle or engine design is
selected here. Failure returns to identifiable management with a concrete reason.

## Separate app and environment update discovery

Proposed preferences:

- **"Check for PDVA updates automatically"**
- **"Check for environment updates automatically"**

These control discovery cadence only. Defaults and cadence are unresolved;
manual checks remain available. Disabling discovery never disables authentication,
compatibility, revocation/freshness policy or transition checks. Explain that a
mandatory acceptance check may still need policy metadata and can block use when
authorization cannot be established. Discovery is not automatic payload installation.

| Automatic discovery preferences | Proposed behavior |
|---|---|
| Both enabled | Independently discover app releases and authorized compatible environment updates; obtain consent for downloads/changes. |
| App disabled, environment enabled | Check the environment catalog. If a desired authenticated environment requires a newer PDVA, a narrow contextual lookup may identify the prerequisite app update and its appropriate distribution action. Keep the app preference disabled. |
| App enabled, environment disabled | Discover PDVA updates; do not enable routine environment discovery. Revalidate installed environment/state if the app changes. |
| Both disabled | No routine update discovery; allow manual checks and retain mandatory verification/authorization at lifecycle transitions. Offline permission is not inferred from these settings. |

When a desired environment needs newer PDVA, do not download or activate it.
Explain **"Update PDVA to use this environment"**, offer the distribution-aware
app-update action and **"Not Now"**, and retain the current supported environment
where safe. Do not automatically install a PDVA update without user consent or
silently enable automatic app checking. Once the app has actually been updated,
resolve and revalidate again; the prompt is not proof that prerequisites were met.

For GitHub-distributed APKs, investigate a separately authenticated signed app-release
catalog and qualified APK signing/source correspondence. No self-update or sideload
installation is implemented. For Play-distributed builds, use Play's supported
app-update mechanism subject to its distribution requirements, rather than assuming
an APK replacement authority. [Android's official in-app updates guide](https://developer.android.com/guide/playcore/in-app-updates),
checked on **2026-10-08**, describes user update flows handled with Google Play.
Eligibility, app signing continuity and any remote guest-delivery/store policy need
separate current review. Do not claim Play distribution is approved, every store
shares installation authority, or PDVA controls users' independent store preferences.

## Maintenance, persistent state and safe failure

The controlled guest major line stays Android 17; investigate supported security
and maintenance image builds within it. Staying on Android 17 does not mean staying
on an old vulnerable build. No automatic major Android upgrade is proposed.
An Android 17/18/19 chooser is **DEFERRED**, requiring its own owner-approved ADR,
requirements revision, maintenance/security policy and qualification of each line.
No ROM marketplace or arbitrary community-image selection is introduced.

| Lifecycle/risk | Proposed treatment and unresolved evidence |
|---|---|
| Immutable OS versus userdata | Verify immutable guest OS/boot components independently of mutable per-instance userdata. Do not grant the guest write authority over management trust or active OS identity; qualified layout/enforcement is Unknown. |
| Update and migration | Qualify exact source/target image and userdata schemas, preserve authorized Persona/policy state, stage a consistent recoverable state and commit image plus data together. An Android OS build change is not proof of safe data migration. |
| Rollback and retention | Retain the last known compatible image with its matched recoverable userdata generation where storage permits. Reuse only if current policy still authorizes both. Never pair old OS with newly migrated data by guess, or bypass vulnerability/revocation policy to recover. Retention is not indefinite permission. |
| Snapshots | Bind runtime/engine, devices/config, image, userdata schema and policy epoch; authenticate state and protect confidentiality. Reject unsupported restores and reauthorize capabilities. Define stale credential handling and security effects of rewinding guest state. |
| Interruption and atomic activation | Resume verified parts for the exact manifest; isolate incomplete staging. Power loss, cancellation, process death or partial migration must not expose a half-installed active generation. Transaction/recovery mechanics remain unselected. |
| Disk exhaustion/corruption | Account for peak staging/retention needs, bound work, detect tamper/truncation and fail safely. Offer qualified repair/redownload or explicit data reset with data-loss consent where appropriate; never silently erase userdata or fall back to host-data/network access. |
| Unsupported/end-of-life images or apps | Warn clearly with available supported paths and maintenance limits. Old apps are not perpetually supportable; user preference for an old guest is not a security assurance. Define deprecated-use windows, restrictions and end-of-support disposition before shipment. |
| Revocation or compromise | Reject a known revoked image/key at acceptance transitions, prevent further activation/restore/boot, and safely stop/quarantine an affected running environment under a qualified response. Protect recoverable data; offer only authorized recovery. Emergency policy delivery and running-guest response latency remain Unknown. |
| Hosting unavailable/compromised | Report transport failure, retry within bounds or use approved alternative locators for the same authenticated bytes. No signature/compatibility bypass, trust-root replacement or silent global-latest fallback. Host compromise can withhold updates even when it cannot forge an accepted image. |
| Offline startup | A cached signature proves neither current non-revocation nor freshness. Define bounded offline authorization, expiry, trusted-time and durable-state assumptions. Use cached state only if all required authorization/integrity/compatibility checks can be established under that qualified policy; otherwise block boot/restore and label the unresolved reason. No assurance of detecting an unseen offline revocation. |
| Maintenance and rights | Assign a named release/signing/vulnerability/recovery owner, support window, monitoring and security-update response before shipment. Complete source/build/provenance and redistribution review. No proprietary Google package redistribution without established rights; AOSP feasibility and Play/GMS remain separate gates. |

## Proposed management UX

Messages and actions below are concise proposals, not implemented UI or support
claims. Show identity, authenticated byte counts and estimated storage when known;
never substitute invented values. Keep management identifiable and accessible even
when the guest fails or spoofs an update screen.

| State | Proposed message | Proposed action/meaning |
|---|---|---|
| Environment not installed | "Android 17 environment is not installed." | Offer "Download Android 17 Virtual Environment" after authenticated eligibility details; no automatic transfer. |
| Compatible environment ready to download | "A compatible Android 17 environment is ready." | Show build, verified download size, storage estimate and network controls; explicit Download or Not Now. |
| Download in progress | "Downloading Android 17 environment…" | Show bounded progress, pause/cancel where safe; active environment remains separate. |
| Interrupted/resumable download | "Download interrupted. Resume after checking the saved parts." | Revalidate metadata, compatibility and part identities before Resume; retry from scratch if recovery is invalid. |
| Image verification failed | "Environment verification failed. It cannot be installed." | Reject/quarantine affected bytes, explain the failure and offer qualified retry; no override. |
| Environment installed/current | "Installed environment is current under the last verified policy." | Show image build and policy-check time; distinguish stale/unknown policy and compatibility from security assurance. |
| Compatible environment update available | "A compatible Android 17 update is available." | Explain maintenance/security purpose, size and migration effect; user initiates it. If current policy blocks use, show the separate mandatory reason. |
| Environment requires newer PDVA | "Update PDVA to use this environment." | Appropriate app-update action or Not Now; no unsupported image download, and retain current environment only where safe. |
| PDVA app update available | "A PDVA update is available." | Distribution-aware user-consented action; distinguish optional release from an environment prerequisite. |
| Image revoked/unsupported | "This image is revoked" or "This image is no longer supported." | State the specific policy outcome; revoked images cannot run. For unsupported images show policy restrictions and supported recovery/update paths. |
| Insufficient storage | "Not enough storage for this operation." | Show qualified required/available space and peak estimate; offer cleanup guidance without deleting userdata implicitly. |
| No network / metadata unavailable | "Cannot check environment policy right now." | Retry/Not Now; identify whether transfer failed or authorization is unresolved. Offline boot depends on qualified policy, not this dismissal. |

## Requirement traceability and evidence

All identifiers below refer to existing obligations in the unchanged register.
This proposal records prospective elaboration, not new definitions or satisfaction.

| Existing requirement(s) | Relation to this proposal and needed evidence |
|---|---|
| `PDVA-REQ-005` | Preserve one controlled image line and excluded import/chooser scope. Compatible Android 17 maintenance builds are distinct from additional major lines. |
| `PDVA-REQ-008` | ADR-0002 needs Tony's explicit approval of final text. Requirements revisions and any multiple-line decision remain separately reviewable under [governance](governance.md). |
| `PDVA-REQ-012` | Management trust, policy and signing/update authority stay outside hostile guest authority; Gate B/F must prove actual separation and authorization. |
| `PDVA-REQ-034` | Authenticate exact source/build/artifact identity, signatures and rights before image trust/shipment; metadata references must bind to the reviewed release record. |
| `PDVA-REQ-035` | Qualify update, migration, rollback, snapshots, interruption/corruption recovery, vulnerability response and a named maintenance owner at F/G. |
| `PDVA-REQ-036` | Catalog/verifier/signing tools, image components and future delivery dependencies need immutable provenance, dependency/TCB review and explicit adoption; a design document adopts none. |
| `PDVA-REQ-013`, `PDVA-REQ-015` | Narrow authorized management interfaces and explicit image/snapshot enforcement/evidence owners; signature and compatibility checks do not prove boundary security. |
| `PDVA-REQ-028`, `PDVA-REQ-029`, `PDVA-REQ-030`, `PDVA-REQ-033` | Guest Google objectives, rights and certification stay independent of AOSP/core feasibility and host-app distribution. No proprietary redistribution authority follows from transport choice. |
| `PDVA-REQ-039`, `PDVA-REQ-040`, `PDVA-REQ-041`, `PDVA-REQ-043` | Label proposal/Unknowns honestly; capture exact builds/policy/procedure and adversarial controls. Green repository checks and compatible boot are not image security or gate evidence. |
| `PDVA-REQ-046`, `PDVA-REQ-047` | Management-owned provisioning/status, clear escape, interruptions, death and restoration UX need Gate C/G evidence. No UI is supplied here. |
| `PDVA-REQ-048`, `PDVA-REQ-054` | Public documentation contains no private data/keys; immediate technical progression stays Gate 0 research. This proposal does not authorize complete-guest implementation. |

The [current harness evidence](evidence/gate-0-isolated-worker-harness.md) has no
physical or guest delivery outcome. [Gate 0 source/candidate research](evidence/gate-0-userspace-vmm-candidate.md)
is a hypothesis, including store-neutral image transport, not engine adoption or
verification evidence. Use [acceptance criteria](acceptance-evidence-criteria.md)
and [testing](testing.md) for later evidence; Gate F/G shipment qualification remains
unreached. Future tests should falsify at least:

- Bad/expired/revoked signatures, unknown schema, mixed-release objects, chunk
  tamper/truncation, replay/freeze, clock rollback and lost anti-rollback state.
- Old/new APK runtimes and device/image schemas, unsupported migrations and
  missing capabilities at every acceptance transition, including concurrent changes.
- Both discovery preferences independently, contextual prerequisite lookup,
  Not Now and cancelled downloads without preference changes or silent installation.
- Interrupted/resumed transfer and activation, space exhaustion, corruption,
  userdata migration/rollback pairing, snapshots and policy epoch reauthorization.
- Known revocation of active/retained images, offline expired/unknown authorization,
  compromised/unavailable hosting and safe recovery without accepting substitutes.
- Management escape, honest status/reason messages, guest attempts to change trust
  or spoof approval, and source/rights/signing/maintenance ownership failures.

If ADR-0002 is accepted, propose a separate reviewed requirements revision for
stable capability contracts, transition acceptance and anti-bypass rules, discovery
preferences/consent, metadata freshness/revocation/offline recovery, and provisioning
UX with testable evidence criteria. No new requirement IDs are allocated here.
Schema/algorithms/keys, engine/layout/storage budgets, offline time/state protection,
support windows, store/hosting qualification and migration implementation remain
unresolved, as recorded in the ADR. Documentation approval does not resolve them.
