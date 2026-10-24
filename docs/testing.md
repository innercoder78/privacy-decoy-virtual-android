# Testing and validation

Functionality/compatibility and security/enforcement have separate results.
Booting Android, launching an app, successful graphics or a green harness does not
prove isolation. [Acceptance criteria](acceptance-evidence-criteria.md) govern all
claims. This bootstrap runs only foundation validation and no VM experiment.

| Future test family | Required approach |
|---|---|
| Guest functionality | Complete Android component/lifecycle, WebView, services and ordinary app behavior for the exact image; independently test without proprietary Google packages. |
| Escape and native containment | Host filesystem/properties, `/proc`, `/sys`, native code, direct syscalls, guest kernel compromise scenarios and hostile workloads; independently observe host sentinels. |
| Authority transfer | Binder reachability, shared memory, device passthrough, inherited/duplicated descriptors/handles, guest/host IPC and confused deputies. |
| Management | Malformed broker messages, caller/instance authorization, replay, stale tokens, revocation, cross-instance and management-state probes. |
| Network | Bypass, protocols/producers and VPN loss/change from [networking](networking.md); independent packet observation with positive controls, not just API return values. |
| Image/state | Image tampering, signing failure, downgrade, snapshot corruption, incompatible versions, interrupted migration/update and recovery. |
| Resource/lifecycle | CPU/memory/disk/IPC exhaustion, process death, restart, restoration, thermal/battery load and background restrictions without fail-open behavior. |
| UX/integration | Display/input/IME/audio, rotation, interruptions, accessibility, clipboard and file disclosure, safe escape and genuine-data revocation. |

Test matrices must identify host Android/build type/OEM/device/ABI, guest/engine
and dependency revisions, exact artifacts, policy and relevant external services.
Use synthetic fixtures, protected host sentinels and adversarial positive/negative
controls. An absent path or inconclusive observer is Unknown, not access denied.
Emulator and development tooling results remain research only. Strong production
isolation claims require stock non-rooted physical release-equivalent tests and
independent security review across the declared supported matrix.

Never put real private accounts, host identifiers, Persona secrets, credentials,
signing material or raw sensitive captures into public evidence. Redact before
upload and retain enough safe metadata to reproduce the conclusion.

## Future Persona identity and leakage acceptance

This elaborates PDVA-REQ-009–021 and 039–043 without adding requirements or
authorizing implementation. Apply the [identity-surface matrix](persona-privacy-policy.md#identity-surface-contract-matrix)
to each method and overload, not just each UI field. All tests below are
**Not tested**; mandatory identity protection remains **Unknown**.

Every test receipt must name the requested Real/Decoy/Empty/Deny mode, guest OS/API,
target SDK, permissions/roles/features, authorized data source, instance/user/app
scope and lifetime, expected cross-surface consistency, persisted state, exact
absence/unsupported/error result, enforcing authority/TCB, independent observer,
failure and rollback behavior, and actual evidence status. Use the official API
citations in the policy to derive expectations; do not make a handwritten success
table into an enforcement oracle. A guest permission does not authorize host data.

| Leakage/coherence family | Independent acceptance approach and falsifier |
|---|---|
| IMEI/MEID/IMSI/ICCID and caller classes | Exercise ordinary callers with/without relevant permissions and applicable target SDKs; separately test only legitimately available privileged/role/carrier cases. Verify method-specific null/empty/exception/unsupported behavior. Falsify on unapproved host data or privilege assumptions, not on honest unavailability. |
| Phone/carrier/subscriptions | Compare display name with MCC/MNC, SIM versus network country including roaming, subscription count/slot mappings and feature declarations. Check number formatting separately from SMS/calling capability; a displayed number is never a verification success. |
| Android ID and separation | Use controlled same-key and different-key test apps, separate users and guest instances. Verify platform scope, restart stability and deliberate reset/key-change behavior; do not require distinct IDs for every same-key package. No host ID seed or universal shared ID. |
| Geography and network | Independently compare Persona GPS, SIM/network country, locale/timezone and explicit overrides. Observe public-IP, DNS and WebRTC metadata separately; changing GPS/carrier must not be reported as changing public IP. Exercise required external-VPN routing and loss under the networking contract. |
| Alternate access paths | For every surface probe Java/framework/SDK APIs, direct Binder/system services, native libraries/direct syscalls, guest files/properties, browser/WebView/native bridges, callbacks and cached values. A changed Java return value with an unapproved alternate path is failure. |
| Unauthorized authority | Probe inherited/duplicated/transferred descriptors and handles, process/service access, shared memory and management interfaces. Include hostile guest, device-model and backend execution; identify what still enforces separation after guest or worker compromise. UI switches and hooks are not enforcement authorities. |
| Persistence and change | Exercise restart, update, restore, deliberate change/rotation/reset, multiple apps and instances, stale caches and in-flight requests. Observe atomic consistency and revoked-authority rejection; restoring a snapshot must not silently restore Real disclosure. Remote observers may retain prior data. |
| Failure and recovery | Inject unavailable APIs, missing/corrupt state, failed virtual location, denied permission, service death, manager loss and interrupted migration/rollback. Require declared errors and blocked genuine disclosure; never fall back to host GPS or another Real source. |

Use synthetic host sentinels in a separately approved fixture, never genuine host
identifiers or user data. Establish that each observer detects an intentionally
exposed synthetic sentinel in a controlled positive case, then detects refusal in
the negative case; an absent/broken observer yields Unknown. Attribute observations
to the actual caller, source and authority, with independently controlled observations
outside guest self-report. No positive control may weaken a production boundary.
Record unimplemented interfaces and unrun cases explicitly. No such fixture, app,
guest, phone, hook or interception mechanism is implemented by this documentation.
Only later stock non-rooted release-equivalent evidence and independent security
review can support scoped host-identity protection claims.

## Foundation validation

Desktop-only preparation has a [short procedure and evidence schema](evidence/gate-0-desktop-readiness.md).
Run `python .github/scripts/test-desktop-readiness.py` for its deterministic
standard-library interruption, writer-lock, corruption, identity and retry controls.
Private journals remain under ignored build storage; they are not Android cleanup evidence.

Run `python .github/scripts/validate-foundation.py` at repository root and
`git diff --check`. The validator checks tracked and non-ignored new files so it
also works before staging. It verifies roots, local Markdown file targets,
bootstrap text/binary/signing hygiene, requirement definitions/numbering and
historical notices. It does not fetch external links, parse arbitrary Markdown,
validate every anchor, discover every secret, prove license compliance or assess
security claims. Human review must inspect every changed file and the exact-base
diff, modes, source/provenance, scope and assertions.

The lightweight workflow checks every PR so unexpected root files cannot evade
path filters. Future expensive Android/VM suites must be path-aware without hiding
unclassified changes. Check GitHub Status and actual job/step logs before labeling
failures: distinguish code defects from service, runner, billing/quota and zero-step
failures. Never weaken or rerun a check solely to obtain green status.
