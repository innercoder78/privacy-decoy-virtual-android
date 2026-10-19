# Evidence-gated roadmap

Planning baseline: **2026-10-19, America/Fortaleza**, through merged
[PR #24](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/24),
canonical main `8ed024150019a0c9d07fc66e2463ced755d589c0`.
**Gate 0 is Unresolved; Gates A–G are Not reached.** The
[gate definitions](feasibility-gates.md), [requirements](requirements.md),
[governance](governance.md), [evidence criteria](acceptance-evidence-criteria.md)
and [source policy](source-provenance-policy.md) govern progression. New repository
evidence overrides this planning snapshot and any PR estimate.

Tony's provisional preference is **approximately 40–60 additional focused PRs
from the post-PR-24 baseline, including this roadmap PR**. This is a planning
target, not a deadline, engineering guarantee, approval to weaken requirements,
or authorization for dependent implementation. Security, efficiency, performance,
maintainability and functional quality take precedence over the count.

## Current evidence and its limits

| Already established, for the recorded scope | What remains unestablished |
|---|---|
| An [Android research harness](../android/README.md), source-built native launch control, manifest/packaging inspection and build/JVM/lint controls exist. | Stock-phone release-equivalent execution, ordinary-app lifecycle authority and supported-host scope. Synthetic frames and probes are not a virtual phone. |
| An [Android-targeted QEMU ARM64 dynamic-PIE cross-build](evidence/gate-0-qemu-android-linux-crossbuild.md) succeeded in the recorded experiment; the [integration review](evidence/gate-0-qemu-worker-integration.md) identifies its exact artifact and restrictions. | QEMU execution on Android, full Android 17 boot, a production engine selection or Gate 0 pass. QEMU is not integrated into the APK. |
| [Strict TCG memory](evidence/gate-0-tcg-executable-memory.md), [kernel snapshot](evidence/gate-0-kernel-fd-snapshot.md), [ARM64 reservation](evidence/gate-0-arm64-boot-plan.md) and [startup ordering](evidence/gate-0-startup-resource-order.md) research provide bounded source/build controls and counterexamples. | End-to-end resource admission, firmware/DTB caller integration, Android JIT authority and acceptable device memory/performance. A reservation helper is not an exclusive boot path. |
| Desktop Linux [process lifetime](evidence/gate-0-linux-worker-lifetime.md), [surviving-grandchild](evidence/gate-0-surviving-grandchild.md), [seccomp](evidence/gate-0-seccomp-process-control.md) and [mapping/mediated-revocation](evidence/gate-0-linux-mediated-revocation.md) controls have actual hosted receipts. | Containment after arbitrary native worker compromise on Android; independently observed whole-scope cleanup, resource revocation and isolation. Linux controls do not supply ordinary-app Android authority. |
| [PR #23's complete Android 17 assessment](evidence/gate-0-complete-android.md) and [PR #24's boot/HAL closure](evidence/gate-0-android17-boot-hal.md) trace source-based boot, device, software graphics, input and service contracts. | A closed, reproducible ordinary-app-compatible guest product, complete virtual-phone GUI/touch integration or any observed PDVA guest boot. |
| Immutable references, hashes and known compatibility gaps are recorded in the [PR #23 ledger](evidence/gate-0-complete-android-sources.md) and [PR #24 ledger](evidence/gate-0-android17-boot-hal-sources.md). | Complete kernel/module/firmware correspondence, all Android backend/client builds, acceptable guest key-service security and redistribution closure. A source identity is not artifact qualification. |

VPN routing, Google Play compatibility and complete Persona implementation are
also **not established**. There is no acceptable-performance or stock-phone
runtime-feasibility result. [Containment](evidence/gate-0-worker-containment.md),
[Android lifetime authority](evidence/gate-0-android-lifetime-authority.md),
[exceptional lifecycle](evidence/gate-0-android-lifecycle-exceptions.md) and
[retained-capability research](evidence/gate-0-capability-revocation.md) remain
blocking inputs, not implemented security guarantees.

The live preflight found PR #24 merged from head
`c54e5d6f003f5cc0d6c2a86d167d607d3686c436`, base
`24ddb82ab1b3a6b4bb4a07b5dcee1a7269700838`, with the merge equal to the baseline
above; its complete change is three documentation files, 454 additions. No PRs
were open. Exact-main [foundation run 39300145968](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39300145968),
[job 118222904027](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39300145968/job/118222904027),
passed with actual receipts for foundation/harness validation, 141 repository
tests, seven native wait controls and the injected assertion control, four Linux
lifetime cases/four mutants, four seccomp cases, and ten revocation cases/ten
semantic mutants with cleanup. Older publication-time pending statements in
those research records remain historical. Only foundation ran on this exact-main
push; Android and QEMU path filters did not select this documentation change.
Zero legacy commit-status contexts do not constitute another pending job.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational at preflight. CI success and source research are not product
proof or gate decisions.

## Provisional allocation, not an implementation queue

These ranges allocate reviewable changes by purpose. Their lower endpoints total
**40** and upper endpoints total **60**; they are not independent confidence
intervals or a prediction of how many discoveries remain. Count each PR once by
its primary purpose, even when it helps several gates. The first row includes
this roadmap PR and any narrowly authorized physical evidence work during Gate 0.

| Work area | Provisional additional PRs | Dependency and intended evidence |
|---|---|---|
| Remaining Gate 0 feasibility and planning | 8–12 | Firmware/build/security-input closure, kernel/modules, backend/client and ordinary-app authority/lifecycle falsification; reviewed candidate disposition. Includes this PR. |
| Conditional Android 17 guest implementation | 6–9 | Only after reviewed Gate 0 pass, explicit engine/architecture decision where needed and scoped adoption review: reproducible guest and complete framework/service/device operation. |
| Enforcing security boundary and Persona controls | 8–12 | Gate B authority, hostile-worker containment, trusted management, narrow brokers, revocation and surface-specific Real/Decoy/Empty/Deny evidence. |
| Interactive graphics/input and performance | 6–9 | Matching guest display/input stack, real interaction, lifecycle and declared CPU/RAM/latency/thermal/battery budgets; Gates A/C scope. |
| Networking and VPN-route verification | 4–6 | Authorized transport, producer/protocol attribution and independent loss/change/leak controls; Gate D scope. |
| Controlled image signing, delivery and lifecycle | 4–6 | Provenance before use; reviewed signing/update/recovery contracts and Gate F evidence. ADR-0002-dependent design remains conditional on acceptance. |
| Integration, adversarial testing and private prototype qualification | 4–6 | Exact integrated build, failure/regression evidence, bounded private-device cohort and explicit acceptance/Unknowns. |
| **Total** | **40–60** | **Conditional planning envelope toward the first private testable prototype.** |

Later production/security/device-matrix qualification and separately qualified
Google services/Play goals are **not promised within this envelope**. Their
requirements remain in force; this separates acceptance scopes, not permission to
discard obligations. A private AOSP-based prototype can test core functionality
without proprietary Google software and without claiming Gate E success.

Do not enlarge PRs to fit the total, schedule filler, or hold a useful falsifying
experiment until an allocation is consumed. Prefer focused changes with independent
review and meaningful controls. Re-estimate after each material discovery and
gate decision. If Gate 0 fails, requires major redesign or shows that 40–60 is
unrealistic, evidence takes precedence: stop dependent work and revise the plan.

## Milestones and dependencies

The milestones below define future acceptance evidence, **not achieved results**.
No PR number, elapsed count or successful CI run authorizes a successor. Research
that does not depend on an unresolved fact may continue; implementation must stop
at that dependency. Every milestone inherits exact-build/source provenance,
synthetic data, public-data review and the evidence fields in the acceptance
criteria. A changed engine, image, dependency, host policy or bridge invalidates
affected evidence until revalidated. **STOP** is immediate for the affected path;
**NARROW** or material **REDESIGN** needs Tony's explicit decision and a reviewed
PDVA ADR, including affected requirements and invalidated evidence.

### 1. Close the remaining Gate 0 feasibility questions

- **Goal:** establish whether a concrete legitimately shippable ordinary-app
  candidate can support the complete interactive guest with a defensible
  prospective boundary; otherwise record the scoped failure or Unknown.
- **Predecessor:** current requirements, ADR-0001 Accepted and source/adoption
  review for each bounded experiment. No engine is selected by this roadmap.
- **Acceptance evidence:** reviewed exact source/build/device/backend inventory,
  legitimate execution/authority proof, constraints and remaining A/B questions,
  followed by an explicit scoped Gate 0 disposition under the gate definitions.
  Resolve the PR #24 blockers below; a tiny Linux boot is insufficient.
- **Negative/failure controls:** reject unchanged Cuttlefish import with kernel
  vhost despite TCG, unexplained host services, missing signed boot inputs, opaque
  required firmware, nonsecure reference keys treated as product security, and
  teardown accepted solely on worker reports or management FD closure.
- **Remaining Unknowns:** Android execution, strict executable memory, memory and
  lifetime limits; complete service-client/build closure, guest security and
  corresponding-source/rights; independent whole-scope cleanup and revocation.
- **STOP/NARROW/REDESIGN trigger:** a required mechanism needs prohibited authority,
  cannot meet the security contract or lacks legitimate source/distribution
  closure. Missing evidence stays Unknown and blocks dependent construction;
  one failed candidate or lookup does not prove all alternatives impossible.
- **Does not prove:** full guest boot, usability, enforced production isolation,
  VPN behavior, Play compatibility or qualified device support.

PR #24 specifically leaves a **real but unadopted userspace-vsock mechanism**:
QEMU's USER backend and the pinned Rust backend exist, but the reference QEMU
launcher still selects kernel vhost and the Rust build is host-targeted. All
retained Android backend/client, FD-sharing, syscall, SELinux and lifetime
contracts remain unresolved. The kernel lead resolves to
`3ec022196c4e9d5c1434599cdda63f622dd6f586`; it does not close exact config,
toolchain, module sources/ABI or reproducible binary correspondence. ARM64's
guest-local KeyMint/Gatekeeper defaults are explicitly nonsecure reference
services, not an acceptable-security result. Ordinary-app execution and lifecycle
authority are still unverified. The authoritative details and immutable pins
remain in [PR #24's assessment](evidence/gate-0-android17-boot-hal.md) and
[source ledger](evidence/gate-0-android17-boot-hal-sources.md).

**Next focused desktop technical experiment:** investigate the selected QEMU
ARM64 firmware lineage, `bootloader_qemu_aarch64` / `qemu_aarch64/u-boot.bin`,
at the recorded Cuttlefish-prebuilts revision. Seek an immutable mapping to exact
U-Boot source, patches, configuration, toolchain and build inputs; trace
`bootcmd_android`, the final DTB and the actual boot/init_boot/vendor_boot,
persistent bootconfig/vbmeta, AVB and signed-partition dependency contract.
Positive evidence must correspond to that selected firmware, not a similarly
named crosvm binary. A different configuration, unavailable mandatory input or
unsupported boot contract falsifies that path; missing records remain Unknown.
Do not omit AVB, encryption or DTB dependencies to make a demo boot. Keep
firmware-dependent construction stopped until closure. This priority can change
only when newer evidence supersedes it; this roadmap runs no firmware experiment.

### 2. First narrow physical experiment: isolated native-launch authority

- **Goal:** answer the prepared [native-launch control's](evidence/gate-0-isolated-native-launch.md#next-bounded-physical-experiment)
  precise stock-phone question: can an ordinary release-equivalent app's isolated
  service execute the fixed packaged ARM64 dynamic PIE with the specified identity
  and direct-child cleanup? Desktop evidence cannot settle installed OEM policy.
- **Predecessor:** Tony's separate explicit authorization before any phone use,
  reviewed exact source/package hashes and build provenance, existing
  [integration prerequisites](evidence/gate-0-qemu-worker-integration.md#single-smallest-next-experiment-and-stop-conditions)
  and applicable [security-incident prerequisites](evidence/gate-0-native-host-antivirus.md).
  This can supply a Gate 0 input before Gate 0 passes; it is not Gate A work.
- **Acceptance evidence:** one bounded normal launch on a genuine stock nonrooted
  production `user` phone, non-debuggable release-equivalent APK, no special grants,
  expected 40-byte record and exit 42, required identity/domain/capability/FD fields,
  and known direct-child reap with no timeout or lost reply. Distinguish
  worker-reported observations from independent observations.
- **Negative/failure controls:** packaging/linker/exec denial, wrong identity or
  result, malformed record, signal, timeout and cleanup uncertainty must not count
  as success. **Pass** requires all acceptance fields above; **fail** means an
  observed denial or contradictory result for the exact proposition; **Unknown**
  means missing or inconclusive evidence. **Cleanup-lockout** means uncertain
  cleanup or a lost reply persistently blocks repeats, including across restart,
  regardless of any earlier positive field. No clearing state or retries around
  lockout; timeout does not establish successful teardown.
- **Remaining Unknowns:** physical launch is NOT RUN; device execution policy and
  cleanup results remain Unknown. The trusted child is not an arbitrary hostile
  descendant tree, and its reap is not an independent whole-scope completion API.
- **STOP/NARROW/REDESIGN trigger:** denied required authority or any unresolved
  cleanup/security event stops the exact dependent experiment. Do not lower SDK,
  move execution into management or change phone/security policy to obtain success.
- **Does not prove:** Gate 0 pass, TCG execution, Linux/Android guest boot,
  post-compromise containment, full resource revocation or acceptable performance.

Prefer useful desktop work first, currently the firmware question above. Do not
delay a necessary falsifying physical experiment merely to consume PRs. A later
physical task must provide novice-friendly **Windows 10 and Samsung** instructions:
ordinary installation, exact variant/hash checks, normal launch, outcome reading,
stop/lockout handling and rollback/uninstallation. Development-only ADB may be
included only if Tony explicitly authorizes it; it grants no production authority
and must be disconnected for normal acceptance execution. Rollback must not erase
evidence or bypass cleanup lockout. Use synthetic data and sanitized reviewed
records; keep host/Persona information, accounts, identifiers, keys, raw captures
and private local paths out of public GitHub. No phone use is authorized here.

### 3. Conditional complete Android 17 guest foundation

- **Goal:** implement one reproducible normally unrooted Android 17/API 37 image
  and matching virtual devices, progressing from boot to real framework/app and
  guest display operation. Serial, headless, GUI and full interaction are distinct
  observations, as defined in [PR #23](evidence/gate-0-complete-android.md).
- **Predecessor:** reviewed Gate 0 pass for the exact candidate, resolution of
  construction-blocking authority/security/provenance gaps, explicit Tony-approved
  engine/material-architecture ADR where required, and scoped source adoption.
- **Acceptance evidence:** complete source/build manifest and artifact identity;
  firmware/kernel/modules, AVB/encryption, init/APEX/VINTF/SELinux and active HAL
  agreement; SystemServer, Zygote, package manager, Activities, launcher/System UI,
  WebView, storage and required services operating without proprietary Google
  software. Full Gate A acceptance also needs the interaction work below.
- **Negative/failure controls:** missing/corrupt boot input or module, wrong ABI,
  rejected verification, missing service/backend, crash/restart and storage
  interruption; boot-complete text or a Linux shell cannot satisfy the milestone.
- **Remaining Unknowns:** complete guest build/device closure, qualifying key
  services, audio/backend integration, resource budgets and all runtime outcomes.
- **STOP/NARROW/REDESIGN trigger:** a required service depends on prohibited host
  authority, unavailable rights/source or weakened verification/security; stop
  affected guest work and return to the prerequisite decision.
- **Does not prove:** complete interaction by itself, host containment, Persona
  enforcement, safe VPN routing, Play support or device-matrix qualification.

### 4. Enforcing boundary, lifecycle and Persona controls

- **Goal:** establish Gate B evidence for actual enforcing authorities and narrow
  brokers, with management/Persona master state and secrets outside hostile guest
  and worker authority; implement surface-specific Real/Decoy/Empty/Deny controls.
- **Predecessor:** reviewed Gate 0 candidate/authority decision and scoped adoption;
  exact guest/device interfaces as they become available. Prospective containment
  and lifetime blockers must be resolved before dependent guest integration, not
  postponed until after a demonstrator exists.
- **Acceptance evidence:** [boundary inventory](security-boundaries.md) and TCB,
  independent host sentinels, native/syscall/escape and malformed-interface probes,
  cross-instance/caller/epoch authorization, manager death and descendant cleanup,
  retained/transferred handle and in-flight revocation tests. Persona evidence
  covers each declared surface, coherence, persistence/reset/rotation, cached and
  native paths, explicit scoped Real disclosure and no host-GPS fallback.
- **Negative/failure controls:** compromise the worker in the test model; retain
  mappings/FDs, forge/replay requests, kill management, corrupt policy and attempt
  restart during uncertainty. Independent positive controls must expose real
  unauthorized effects when deliberately enabled; absent observations are Unknown.
- **Remaining Unknowns:** independently acknowledged Android whole-scope completion,
  revocable ownership, remaining host attack surface and full Persona coverage.
  Revoking future access cannot erase previously copied/disclosed bytes.
- **STOP/NARROW/REDESIGN trigger:** retained hostile authority, exposed master state,
  uncontrolled disclosure, genuine-data fallback or accepted restart without known
  cleanup. Do not replace enforcement with cooperative shutdown or host hooking.
- **Does not prove:** usability/performance, networking, image lifecycle, universal
  Persona identity or production isolation without independent security review.

### 5. First full interactive guest demonstration and measured usability

- **Goal:** show a real complete guest responding to touch, then qualify useful
  graphics/input and lifecycle behavior against declared Gate A/C scope.
- **Predecessor:** milestone 3's real guest stack and the reviewed boundary,
  resource/lifetime controls needed to run it safely from milestone 4; exact
  graphics/input source adoption and separate authorization for physical tests.
- **Acceptance evidence:** actual guest-rendered launcher and app frames through
  composer/renderer/virtual display/host presentation; touch/multitouch, IME text
  composition, navigation, rotation, audio, storage and normal app lifecycle.
  Preserve safe escape to management. Declare startup/frame/input-latency,
  CPU/RAM/storage, thermal and battery budgets before measuring release-equivalent
  stock devices, including pressure, interruption, suspend/resume and recovery.
- **Negative/failure controls:** stale/malformed/oversized frames and events,
  cancellation/stuck touches, rotated coordinates, queue pressure, process death,
  low memory, backgrounding and lost presentation. Static screenshots, synthetic
  frames, mouse-only input and raw keycodes are insufficient.
- **Remaining Unknowns:** matching graphics/device/buffer/fence contracts, nested
  software-rendering cost, tolerable latency, OEM behavior and physical resource fit.
- **STOP/NARROW/REDESIGN trigger:** unusable interaction, exceeded budgets, unsafe
  recovery or a required direct host GPU/input privilege. Revisit the candidate
  rather than silently removing required functionality or security.
- **Does not prove:** a private qualified prototype, complete Gate B/D/F evidence,
  production readiness, Play compatibility or support on untested phones.

### 6. Networking and external-VPN route evidence

- **Goal:** qualify Gate D's approved host path and active external VPN where
  applicable, including proven loss/change behavior and no silent physical egress.
- **Predecessor:** reviewed ordinary-app transport/backend and its enforcing
  authority, milestone 4's broker/lifetime controls and real guest producers from
  milestone 3. No host VPN-slot takeover is authorized.
- **Acceptance evidence:** [network contract](networking.md) coverage for Java/native
  TCP, UDP, DNS, IPv4/IPv6, WebView, QUIC/Cronet, guest services and secondary/
  background processes; identify each actual socket producer and independently
  observe packets through required routes during VPN loss/reconnect/provider and
  full/split/excluded-policy changes, queued I/O and process death.
- **Negative/failure controls:** intentional leak-positive controls, bypass attempts,
  stale handles, resolver failure and route uncertainty; a VPN icon/callback or
  application timeout cannot establish fail-closed packet behavior.
- **Remaining Unknowns:** backend/client closure, DNS, allowed ordinary-app route
  enforcement, provider behavior and race-free loss handling.
- **STOP/NARROW/REDESIGN trigger:** uncontrolled physical fallback or unverifiable
  required routing; block traffic and dependent claims. Any changed VPN authority
  requires Tony's explicit decision and reviewed ADR.
- **Does not prove:** universal anonymity, Persona/public-IP geography agreement,
  Google compatibility or every VPN/provider/device combination.

### 7. Controlled image signing, delivery and lifecycle

- **Goal:** qualify Gate F provenance, authenticated image acceptance and safe
  maintenance for the single controlled Android 17 line.
- **Predecessor:** provenance/rights before every adoption, reviewed guest/runtime
  identity and milestone 4's protected management authority. ADR-0002 remains
  **Proposed**: its separate-delivery design needs Tony's explicit acceptance of
  the final text, reviewed requirement changes and scoped implementation approval.
- **Acceptance evidence:** [image lifecycle](guest-image-lifecycle.md) source/build
  correspondence, hashes, signing/key custody, authentication and compatibility
  at boot/install/update/restore, atomic migration, rollback/snapshots, revocation,
  corruption/interruption recovery and named vulnerability/maintenance ownership.
  If adopted, apply the [delivery contract](environment-delivery-and-updates.md)
  without treating hosting identity or user consent as image trust.
- **Negative/failure controls:** altered/truncated image or metadata, wrong signer,
  stale/revoked/incompatible versions, downgrade, stale snapshot capabilities,
  storage exhaustion and interrupted download/update/migration; recovery must not
  accept unverified state or reintroduce host-data/network fallback.
- **Remaining Unknowns:** exact firmware/module correspondence, signing and trust
  contracts, storage budgets, migration formats, support ownership and delivery
  choices. Proposed ADR text is not implementation evidence.
- **STOP/NARROW/REDESIGN trigger:** missing rights/source, unverifiable trust chain,
  unsafe restore/update or ownerless security maintenance; block affected use.
- **Does not prove:** escape resistance, Play/GMS redistribution rights, accepted
  ADR-0002, arbitrary ROM import or a guest-major version chooser.

### 8. First private testable PDVA prototype

- **Goal:** provide a deliberately bounded private cohort with an installable,
  interactive, integrated PDVA build and reproducible tests of its declared scope.
  This is the 40–60 planning target, distinct from the first demonstration.
- **Predecessor:** reviewed exact-scope acceptance from milestones 3–7, including
  applicable A/B/C/D/F evidence and all mandatory protections for the offered
  functions; Tony's explicit physical/private-test authorization. Unresolved
  mandatory protection blocks qualification, even if the GUI works.
- **Acceptance evidence:** one identified host APK/guest/dependency build, controlled
  provisioning and rollback, declared stock-device cohort and measured budgets,
  coherent Persona controls, enforced guest/host separation, verified networking
  and integrated adversarial/failure/regression results. Provide novice-friendly
  installation, interaction, stop, cleanup and recovery instructions; record
  supported scope, excluded claims and every remaining Unknown explicitly.
- **Negative/failure controls:** combine hostile guest/native behavior, malformed
  brokers, VPN loss, manager/worker death, retained resources, exhaustion,
  tampered image/snapshot and interrupted recovery; use independent observers
  and positive controls, with no security/cleanup bypass to continue testing.
- **Remaining Unknowns:** integration defects, real-session endurance, broader
  devices/providers, maintenance scale and independently qualified security.
- **STOP/NARROW/REDESIGN trigger:** any required isolation, disclosure, routing,
  cleanup or image-integrity condition fails; suspend the affected prototype
  capability and revalidate its prerequisites before resuming.
- **Does not prove:** production readiness, a complete Gate G device matrix,
  independently reviewed production isolation, Google services/Play qualification,
  certification or universal app compatibility. Private status does not waive
  requirements or turn missing evidence into a pass.

### 9. Later production/security/device-matrix qualification

- **Goal:** qualify supported release scope, independent security review and Gate G
  across a declared stock nonrooted host/OEM/ABI/version matrix.
- **Predecessor:** accepted integrated prototype evidence, maintained exact builds,
  resolved production-blocking Unknowns and a separately reviewed qualification plan.
- **Acceptance evidence:** independent security findings and verified remediation,
  matrix-based release-equivalent boundary, graphics, lifecycle, networking,
  performance/endurance and recovery results, reproducible supply chain and
  operational vulnerability/update/support ownership.
- **Negative/failure controls:** escape/native attacks, OEM/policy differences,
  thermal/resource limits, host updates, VPN changes, signer compromise and
  failed recovery across the declared support matrix.
- **Remaining Unknowns:** cost and size of the matrix, security findings, changing
  host policies and long-term maintenance. No PR budget or release date is known.
- **STOP/NARROW/REDESIGN trigger:** uncovered critical failure or unmaintainable
  support obligation; restrict claims and stop release for affected scope, with
  owner-approved ADR review for material narrowing/redesign.
- **Does not prove:** support outside tested scope or Google/Play certification.

### 10. Separately qualified Google services and Play goals

- **Goal:** evaluate the [Google compatibility objectives](google-compatibility.md)
  independently from core AOSP feasibility and qualify Gate E for exact scope.
- **Predecessor:** viable complete guest and required security/lifecycle evidence,
  current authoritative rights/acquisition review and explicit approval of any
  proposed material architecture/scope change. Source/rights research may proceed
  earlier without adopting proprietary packages.
- **Acceptance evidence:** separate technical, redistribution-rights, user-local
  acquisition, certification and integrity dispositions; authorized test accounts,
  genuine Play sign-in/search/install/update behavior and honest compatible or
  rejected app outcomes for exact builds.
- **Negative/failure controls:** unavailable services, rejected account/installation,
  updates, integrity/certification and incompatible apps; sideloaded APKs are not
  Play-installed. Synthetic descriptors cannot supply physical attestation.
- **Remaining Unknowns:** legitimate acquisition/distribution, certification,
  service maintenance and app-specific integrity acceptance; no allocation is
  guaranteed inside the private-prototype budget.
- **STOP/NARROW/REDESIGN trigger:** absent rights or a path requiring certification,
  attestation, licensing, certificate, DRM or anti-tamper bypass; stop that path
  and record the honest limitation without weakening controls.
- **Does not prove:** universal banking/payment/DRM compatibility, retail-device
  identity or a right to redistribute proprietary Google binaries.

## Product boundaries and authorization

[ADR-0001](decisions/ADR-0001-full-interactive-virtual-android-direction.md) remains
**Accepted**. [ADR-0002](decisions/ADR-0002-signed-environment-delivery-and-compatibility.md)
remains **Proposed**, pending Tony's explicit final-text decision. This roadmap
does not select an engine, accept an architecture, alter requirements or approve
any dependent implementation. Each future proposal needs its own scope, adoption,
evidence and owner decisions where governance requires them.

- Ordinary installed Android app on a stock nonrooted production host; no root,
  privileged/system/platform-signed, shell/production ADB, OEM-only, custom-kernel
  or development-only production authority.
- Complete interactive Android 17/API 37 guest, normally unrooted, with one
  controlled image line. No simulated phone, profiles, containers, in-host hooks
  or Microdroid substitution for the required full guest.
- Genuine guest/host separation and narrow authorized brokers; management and
  Persona master state remain outside hostile guest authority. Real means
  explicit scoped visible disclosure; Decoy, Empty and Deny retain their defined
  semantics. No silent genuine-data or host-GPS fallback.
- Approved host network paths and active external VPN where applicable, with
  independently proven loss/change behavior. No host `VpnService` or host VPN-slot
  takeover without Tony's explicit approval and a reviewed ADR.
- Separately gated Google services/Play goals, no attestation/certification or
  other security-control bypass, and no proprietary Google binary redistribution
  without established rights.

**STOP, NARROW and REDESIGN remain real exits.** Neither the planning range nor a
PR merge substitutes for Tony's explicit decision and a reviewed ADR on a material
change. Historical Privacy-Decoy remains read-only reference, not an inherited
architecture, result set or implementation queue.
