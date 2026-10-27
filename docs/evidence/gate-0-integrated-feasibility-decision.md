# Gate 0: integrated Android 17 feasibility decision

Review: **2026-10-26–27, America/Fortaleza; Windows x86_64; source/configuration
and existing CI receipts only. Gate 0 Unresolved; Gates A–G Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No engine is selected.

**R: STOP as an unchanged ordinary-app full-phone candidate. H: no assembled,
coherent configuration established; dependent construction remains blocked.**
The new check below connects an actual successful Android QEMU build's generated
configuration to the required device graph. It rejects that artifact as H's
device provider before graphics, service correctness or performance can qualify
it. It does not establish product-wide impossibility or authorize a replacement.

## Baseline and scope

Live main was `6a2d64bea7f8638a9d29a59c27eeaf16c9090768`, merging PR #43.
The open-PR collection returned **zero**; inspection of all open heads/bases,
diffs/files, checks/jobs/logs, reviews/comments/threads therefore had an empty
set. Relevant local history and the complete PR #43 merge diff were inspected.
Its EOF finding is **partially confirmed source control flow**, not execution
of authentic upstream C++ or demonstrated memory exhaustion; it is not reopened.

Baseline [foundation run 40422222840](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40422222840)
completed successfully. Both actual job logs identify that main: foundation
`121919170065`, Windows `121919170364`. They contain existing repository/native
controls; Windows records 45 image and four frame tests. They are not full-guest
evidence. [GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
All Systems Operational, page update `2026-10-26T21:59:23.005Z`. This is a
preflight snapshot, not a statement about this PR's hosted checks.

Initial local main was the preceding merge, clean, with one registered worktree,
no stashes and 136 tracked regular `100644` files. Branches and ignored research,
Gradle/CMake/tool/source assets were inventoried and preserved. No applicable
AGENTS.md supplied additional instructions. Fetch and branch creation used the
required sandbox approvals. No destructive Git operation occurred. An ignored
checkpoint retains completed stages, source receipts and the next safe step;
it is **not independently backed-up evidence**. No private backup is re-attested.

The governing requirements, architecture, gates, acceptance criteria, security
boundaries, threat model, Persona policy, networking, provenance, testing,
roadmap, governance and both ADRs remain unchanged. Native/build/dependency,
license, binary and mode inventories retain their existing research-only scope.
This record reconciles the actual findings linked below, rather than adopting
the evidence index's summaries as proof. It changes only documentation.

## Two evidence subjects

**R** is the previously selected Android 17 r1 `aosp_cf_arm64_phone`,
`PRODUCT_DEVICE=vsoc_arm64`, nonprotected Android boot, Linux Cuttlefish QEMU
manager, default relevant product/launcher choices, and no product-output
bootloader override. Cuttlefish is `283645aacf6cdb56cc31a9362f54d412dbc132a1`.
Its ARM firmware is the QEMU U-Boot target, source
`3fe9647575890b846172e546201eff7614c8cb59`, prebuilt snapshot
`36f427b7c46682cfcdb2e61eee6893acbfb2a606`; documentary build 15108624 is not
local binary reproduction. Compatible Linux hosts choose KVM; the other branch
emulates. Graphics auto is host-sensitive. R has no proven generated release/user
build in PDVA. This uncertainty does not erase its unconditional Linux vhost edge.

**H** denotes only the previously researched software mechanisms: pinned QEMU
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, ARM virt/explicit TCG;
guest_swiftshader/ANGLE/Pastel, ranchu GuestFrameComposer and plain virtio GPU;
software multitouch/keyboard; ordinary virtual block/RNG/consoles; userspace
vsock and matching peers; software sound and userspace networking. These are
comparison hypotheses, **not jointly selected, built, integrated or installed**.
The Rust backend pin is `28233ae213b24a9a35f25e9e49bcadee2bf93821`;
its existing host executable is not an Android app backend. Missing adapters,
source variants, peers and protected state remain missing. No command line can
be inferred by combining favorable rows from the separate investigations.

The guest remains a complete normally unrooted Android 17/API 37 phone with
one controlled image. Guest init, Binder, DRM, ALSA and HAL capabilities are
guest authority; they are not requests for host root, host Binder passthrough,
host GPU or host sound-device access. Conversely, QEMU's host device opens and
native helpers cannot be relabeled guest authority. Neither a Linux boot nor
headless Android, a profile/container, app virtualization or UI simulation meets
the objective. No product/security requirement is removed.

## New independent configuration check

**Question:** does the actual successful cross-build, rather than a hand-authored
capability list or declared minikconf control, select the devices needed by H?

Retrieved the original successful [run 38095872712, job 114341523528](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38095872712/job/114341523528),
source head `379822d7f1b56e8f6d0f06a2476d4f9387f80ae7`. Its recorded output is
66,991,384 bytes, SHA-256
`30e259f29a2cd7418bd674a1fb640f0608e9e571632e0ee2a4d06439bbdcab24`,
Android API-30 ARM64 dynamic PIE, NDK r28c, direct dependencies libc/libm/libz.
This is a **CI log receipt**, not a freshly downloaded/hashed executable, and
predates the strict TCG allocator adaptations. No claim transfers its identity
to later patched builds or a JNI library. The [cross-build](gate-0-qemu-android-linux-crossbuild.md)
and [integration record](gate-0-qemu-worker-integration.md) retain that distinction.
Comparison with the current recipe confirms the same ARM_VIRT-only device seed,
disabled default devices/features, pixman, slirp and modules, and empty audio
driver list. That correspondence does not assign the old binary's hash to the
current recipe or substitute for a newly generated configuration.

Reproduction: retrieve that exact job log; locate `CONFIG
aarch64-softmmu-config-devices.mak sha256=` at 23:43:09 UTC. Remove only each
GitHub timestamp prefix from the following file-content lines, retaining LF and
the terminal newline, stopping before `CONFIG config-host.mak`. SHA-256 of the
reconstructed file **matches the runner's printed digest**:
`825dab0bfb4a4ae9c7533caed2c2b6f3f2e359c43d8c89a9fb2fd895973e79b4`.
It has **42 enabled symbols**, unlike the earlier explicitly declared 41-symbol
control. The later `COMPILED DEVICE CONFIGURATION` section repeats generated
header digest `573eacc74636f51a1e834ea2df4632bf0a3b4a993c709bd5217ccf52fb4b493b`.
The job reaches its cross-build completion marker. A missing/truncated section
or digest mismatch would make this check Unknown, not an absence result.

| Actual successful-build selection | Required source edge / result |
|---|---|
| ARM_VIRT, PCI, PCI_EXPRESS, VIRTIO, VIRTIO_MMIO present | CPU/machine and generic bus infrastructure exist. PCI core is **not** VIRTIO_PCI; MMIO does not instantiate absent leaf devices. Positive control against claiming all PCI/virtio absent. |
| VIRTIO_PCI absent | QEMU virtio Meson adds `virtio-pci.c` and its complete PCI wrapper source set only under this symbol. The selected phone's PCI device graph cannot be supplied unchanged. |
| VIRTIO_BLK, VIRTIO_RNG, VIRTIO_SERIAL absent | Block/RNG implementations and serial PCI wrapper have explicit gates. The reference requires virtio disks, RNG and a serial PCI controller. Generic block helpers or a compiled serial-bus helper do not establish those device types. |
| VIRTIO_GPU, VIRTIO_INPUT, VIRTIO_SND, VIRTIO_NET, VHOST_USER_VSOCK absent | Missing required H display/input and proposed sound/network/vsock selections. The prior source records specify their contracts; this is now a corresponding **generated-build** negative for this artifact. |
| config-host.h undefines PIXMAN, SLIRP, VHOST_USER; configure disables modules | Independent dependency gates also fail. An absent device is not repaired by a plugin/module at runtime. A Rust backend existing elsewhere cannot supply QEMU's omitted front end. |

Fresh immutable QEMU Meson/Kconfig reads below establish the block, RNG, PCI,
userspace-vsock and GPU gates. Fresh decoded Cuttlefish source matches its prior
hash: serial PCI lines 523–526, virtio disks 711–718, RNG 763–766, Linux kernel
vhost 878–882. This extends the earlier graphics/input declared-selection result
to actual generated build evidence and to the earlier boot/storage/service bus
dependencies. No new minikconf run, compilation, target execution, object-code
disassembly or synthetic acceptance oracle is claimed.

| Fresh immutable file | SHA-256 of retrieved source text |
|---|---|
| [Cuttlefish qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` |
| [QEMU hw/virtio/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/meson.build) | `26ee116a285af2cc7afd82b2360ac54f679e809a04233ff5799248cc7daad01e` |
| [QEMU hw/virtio/Kconfig](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/Kconfig) | `931dafedf7b6869847e7b97cc720357ce6af1ffd6c1518092333c9fd03753bc7` |
| [QEMU hw/block/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/block/meson.build) | `d9ff53ef07f0ef25691a9f22cc8559fa39f50f377ea2da79846c6fa4d4d21463` |
| [QEMU hw/display/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/display/meson.build) | `36fb16a74d50369756313baaecee09b687139effa5bfa3aed03e2e61025e6abd` |

Gitiles TEXT was base64-decoded without newline conversion; QEMU raw text was
read at the exact commit. Initial sandbox network denial supplied no source
evidence; the approved retry supplied the matching Cuttlefish bytes. These are
references, not imported implementation. Existing source receipts supply the
remaining matrix edges; no new full source survey is claimed.

## Necessary-condition matrix

M = mandatory for the stated selection/requirement; C = conditional on a named
option. **Supported** means only the explicitly named source/build fact;
**Contradicted** rejects that exact pairing; **Conditional** is an unselected
alternative; **Unknown** is missing evidence; **Not Run** is execution status.
All R/H Android runtime edges are Not Run. Each row names the first missing
dependency and a concrete falsifier; no source implementation alone satisfies
an integrated edge. Linked records contain exact revisions and companion ledgers.

| Edge; exact selection and receipt | Required authority / mandatory status | Built/integrated state and disposition | First missing dependency; concrete falsifier |
|---|---|---|---|
| A1 native launch: isolated service, packaged ARM64 dynamic PIE; [launch](gate-0-isolated-native-launch.md), [integration](gate-0-qemu-worker-integration.md) | M ordinary installed-app UID/SELinux/seccomp/linker; no shell grant | Small trusted payload built/packaging inspected; QEMU separately cross-built, not integrated. Android **Unknown / Not Run** | Installed extraction/exec/linker authority. Fixed payload denied or wrong UID/domain rejects that executable route; JNI remains a distinct unproved route. |
| A2 translation memory/ABI/page size: explicit TCG split-wx; [strict TCG](gate-0-tcg-executable-memory.md) | M ordinary memfd, RW/RX aliases, signals/threads; host 4/16-KiB distinct from guest pages | Source adaptation and controls exist; original build above is older. Runtime **Unknown** | Exact patched build plus installed executable-memory/cache behavior. Required RWX/temp-path fallback or RX denial falsifies the strict selection. ELF alignment alone cannot satisfy it. |
| A3 background/lifetime/resources: dedicated isolated worker; [lifetime](gate-0-android-lifetime-authority.md), [containment](gate-0-worker-containment.md) | M ordinary binding and system-owned lifecycle; no app cgroup delegation | Source shows isolated-not-needed kill and system cgroup cleanup, not app-visible completion. **Unknown** | Independent enrollment/completion across manager loss. Unbind success or Binder death accepted despite surviving authority falsifies cleanup; working-set/latency budgets remain unmeasured. |
| B CPU/machine: R compatible-host KVM, otherwise emulation; H ARM virt/TCG | R KVM C on compatible Linux host and prohibited for ordinary app; H software translation M, no intrinsic KVM | TCG/ARM virt cross-build **Supported**; new device check **Contradicted** for unchanged artifact | Matching selected leaf devices/transport. Missing VIRTIO_PCI already rejects borrowing R's PCI graph into that build. No runtime performance inference. |
| C1 firmware/DTB/disks: ARM `-bios`, QEMU DTB, boot/init_boot/vendor_boot v4, bootconfig, super, metadata/userdata; [boot/HAL](gate-0-android17-boot-hal.md), [U-Boot](gate-0-android17-uboot.md) | M guest boot authority; host needs bounded authenticated resource admission, not host root | Source lineage improved; no PDVA image/firmware loader integration. **Unknown**; current virtio disk pairing **Contradicted** | Complete source/config/module ABI, actual DTB and admitted signed resources. Missing init_boot, disk/console device or kernel module rejects closure; raw Linux boot is insufficient. |
| C2 AVB/encryption/key services: R guest-local nonsecure KeyMint/Gatekeeper; OEM-lock still external | M required trust/encryption; remote key HALs C, not inferred from unused console slots | R test keys/fresh unlocked state/non-OP-TEE zero/no-op rollback: **Contradicted** as release trust. H **Unknown** | Independent protected state/enforcement, not merely a signed message to hostile emulated RAM. Zero/reset rollback or bypassable boot admission falsifies it; [handoff STOP](gate-0-keystore-boot-handoff.md) remains. |
| D init/SELinux/servicemanager/APEX/ART/Zygote/system_server/SurfaceFlinger/SystemUI/Settings/package installation; [complete guest](gate-0-complete-android.md), [sources](gate-0-complete-android-sources.md) | M guest-local privileged system components, normally unrooted user experience | Source include/startup spine **Supported**; generated release, VINTF/APEX/linker graph and execution **Unknown** | One exact product/release/user configuration matching kernel and HALs. Missing mandatory service or inability to install/launch a real guest app rejects full-guest qualification. |
| E1 graphics: H explicit guest_swiftshader, auto→ranchu, Pastel→GuestFrameComposer, minigbm, plain virtio-gpu-pci; [graphics](gate-0-android17-software-graphics.md), [config](gate-0-android17-graphics-config-closure.md) | M guest DRM/KMS/buffers/fences; host worker need not access GPU | H current device build **Contradicted**; alternative pairing **Conditional** | Generated textproto takes precedence over android-info; installed kernel/module correspondence missing. RGBA with the inspected fixed-XRGB non-blob dumb resource rejects color correspondence; BGRA is not an adopted repair. |
| E2 host display: bounded CPU pixels into app-owned window; [display boundary](gate-0-host-display-boundary.md) | M ordinary own-window presentation; separate trusted manager | Four desktop copy controls exist, no guest listener/adapter. **Conditional / Unknown** | Bounded receiver and independent ownership/coherence contract. Retained writable alias or an unchanged counter cannot certify a coherent frame; bounded hostile pixels may still tear. Stale epoch rejects current-session acceptance. |
| E3 touch/keyboard/navigation/IME: R mouse+keyboard; H software multitouch; [input](gate-0-android17-input-compatibility.md) | M own-window events, guest virtual input; no host input injection | R complete touch **Contradicted**; H source recognition **Conditional**, build/bridge absent | Installed device/display association and loss/cancel state. Mouse-only, absent virtio-input, lost final release or raw keycode claimed as composed text rejects closure. |
| F1 sensors: selected AIDL multihal/HIDL sub-HAL over hvc18/19; [sensors](gate-0-android17-sensor-service-closure.md) | M under unchanged phone; custom package C, not selected; no real host sensor grant intrinsic | Host-only simulator and ambient FIFOs; H Android peer absent. R unchanged app pairing **Contradicted** | Matching confined peer/build/handshake and all advertised reports. Missing control/data reply or no-value sentinel reported as valid sensor output rejects it. |
| F2 audio: selected AIDL primary/ALSA 0/0; R AC97/none; H virtio-sound; [audio](gate-0-android17-audio-service-closure.md) | M playback; Real capture separately authorized and C; guest ALSA not host `/dev/snd` | R output **Contradicted** (discarded); H device/PCM/AudioTrack adapter **Conditional**, not built | Actual driver/card/PCM and bounded host receiver, plus model provenance. Frame-count progress with discarded output falsifies playback; a separate reference socket does not connect AC97. |
| F3 radio: selected Goldfish AIDL/AtChannel→modem_simulator; [radio](gate-0-android17-radio-service-closure.md) | M default telephony selection; removal override C, not adopted; guest NET_ADMIN is not host privilege | Synthetic protocol source exists; peer has platform-device variant, not qualified app build. Bounded unchanged pairing **Contradicted**; H **Unknown** | App build plus bidirectional backend and bounded state/EOF behavior. Unserved guest-to-host port rejects closure. PR #43 adds no runtime exhaustion proof; real calls/SMS are not supplied by synthetic success. |
| F4 power/time, GNSS/camera, lights and other selected clients; [boot/HAL](gate-0-android17-boot-hal.md), [communication](gate-0-userspace-communication.md) | M retained product contracts; particular external camera/lights/other endpoints C by exact flags | CPU/timer source exists; exhaustive active-client/generated service closure **Unknown** | Exact init/VINTF/feature and selected peer inventory. An enabled mandatory client without its peer rejects closure; an unused optional port is not a mandatory host privilege. No host GPS/camera/timezone passthrough is authorized. |
| G vsock/endpoints: R kernel vhost; H USER device+Rust backend/Unix peers; [endpoints](gate-0-backend-endpoints.md) | R M host vhost device; H M delegated connected streams, SCM_RIGHTS and dedicated RW guest RAM | R **Contradicted**; H source mechanisms **Supported**, unchanged host-only entrypoint/late pathname contract **Contradicted** | Android-target entrypoint and both transport directions. Guest-to-host dynamic pathname connect cannot consume a preopened stream unchanged. Read-only guest RAM cannot satisfy backend RW mapping; manager/Persona backing must never be shared. |
| H hostile worker/descendants/files/Binder/IPC/memory/Persona/revocation; [containment](gate-0-worker-containment.md), [revocation](gate-0-capability-revocation.md), [recovery](gate-0-research-recovery.md) | M independently enforced host boundary outside hostile guest/engine/peers | Linux controls and source witnesses only; Android enforcement **Unknown** | Exact pre-exposure authority, quotas, enrollment and completion/recovery. Surviving raw FD/map, protected-state access, ignored manager loss or uncertain-history restart falsifies qualification. Closing manager FDs does not revoke copies. |
| I egress: guest→PDVA backend→ordinary host network; [network contract](../networking.md) | M networking; required external-VPN behavior separately M when policy requires; no host VPN slot | R default TAP is not ordinary-app authority; H SLIRP source exists but actual build disables it. **Conditional / Unknown** | Qualified userspace producer/backend first; then independent VPN routing/loss proof. Missing SLIRP rejects this build pairing; silent physical fallback rejects required routing regardless of guest network success. |
| J source/image/distribution: exact manifests, kernels/modules, firmware, audio models, native/build dependencies; [provenance](../source-provenance-policy.md), [U-Boot ledger](gate-0-android17-uboot-sources.md) | M rights/build correspondence, controlled signing and maintained image; not a privilege grant | Partial source/build receipts, no controlled full guest or complete rights package. **Unknown** | Missing required corresponding source/license/model or uncontrolled image trust rejects adoption. Public firmware digest is not locally verified bytes; reference keys are not release identity. |

## Smallest failure set and Gate 0 decision table

For R, **one edge suffices**: Linux QEMU launch unconditionally selects kernel
vhost-vsock. The [pinned QEMU implementation](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/vhost-vsock.c)
opens host `/dev/vhost-vsock` unless supplied a suitable vhost FD; the FD merely
delegates the same required kernel authority. This is a host backend, not the
guest's AF_VSOCK syscall. No ordinary-app grant/delegator is established. R is
a Linux reference deployment, not an Android-app recipe. Switching accelerator
alone leaves this necessary edge intact. Compatible-host KVM is a second,
conditional prohibited edge, not a reason to claim every R host uses KVM.
The [platform](gate-0-platform-authority.md) and [communication](gate-0-userspace-communication.md)
records establish the access-class distinction. No restricted AVF route is substituted.

Audio-none and mouse-only input independently reject unchanged complete interaction;
release trust and peer contracts add separate STOPs. None is needed to enlarge
the minimal authority failure set. H is not disproved by those R failures:
userspace vsock, software graphics and virtual input are real source mechanisms.
But **H's first missing construction condition is one actual coherent selected
build/device/backend graph**. The new check falsifies using the existing successful
binary to supply it. Independent ordinary-app execution is the first unmeasured
host-authority proposition, not a consequence of a successful link.

| Decision axis | R: unchanged reference | H: software-only hypothesis |
|---|---|---|
| Full-phone ordinary-app candidate | **Candidate STOP**; mandatory host vhost edge already fails the authority contract | **Missing evidence / dependent construction blocked**; collection of hypotheses, not an assembled configuration; product-wide impossibility **not established** |
| Prohibited authority | Kernel vhost; KVM on compatible Linux hosts; default TAP setup. No privilege or preopened privileged FD is authorized | None proved intrinsic to TCG/software devices. Borrowing R's kernel backends, direct isolated GPU/sound access or privileged cleanup would violate scope |
| Remaining ordinary-app Unknowns | Not repaired by source-compatible guest services | Isolated native load/exec, strict TCG RW/RX behavior, ABI/page sizes, FD/Unix/RAM transfers, threads/seccomp, background/resource/lifetime authority |
| Remaining full-guest Unknowns | Generated image and runtime absent despite reference source | Matching devices/build, protected boot state, kernel/modules, generated graphics/HAL/APEX graph, every mandatory peer, real UI/input/audio/app operation and budgets |
| Security/TCB obligations | Reference signing, helpers and cooperative replies do not enforce PDVA policy | Hostile engine/backend/peers, descendants, parsers, Binder/FD/mapping authority, quotas, trusted enrollment/Persona/master state, revocation and recovery remain unqualified |
| Can desktop decide first issue? | Yes: necessary authority contradiction is already source-supported | Yes for current-build/device correspondence: **new check rejects it**. No existing combined selection is available to validate; another generic survey/cross-build cannot manufacture one |
| Is phone now the smallest authority falsifier? | Unnecessary to reject R | **Yes for the separate narrow installed native-launch proposition**, after existing prerequisites; **no** as a remedy for missing full-guest construction or an unconditional ready-to-run decision |
| Owner decision | Do not implement/import unchanged R | Continue only with explicit bounded research decisions; material product, guest configuration or trust-owner redesign requires Tony's approval and an ADR before dependent implementation |

## One smallest next proof, with readiness limits

**The next independent execution-authority proof is the already prepared limited
physical native-launch control**, not another graphics/radio survey or a VM boot.
Desktop research cannot decide whether an ordinary non-debuggable app on the
declared stock ARM64 user build can extract and execute the fixed packaged PIE
from its isolated worker with the expected identity and direct-child reap.
Use the [existing protocol and acceptance conditions](gate-0-qemu-worker-integration.md#single-smallest-next-experiment-and-stop-conditions),
without substituting QEMU or expanding implementation. Positive: expected
40-byte result, exit 42, required identity/domain/FD observations and known
direct-child reap. Negative: validly observed extraction/exec/linker denial,
wrong authority, malformed result or failed cleanup; lost observation remains
Unknown and locks out retry. This can reject the **executable launch subroute**,
not all H/JNI alternatives, and a positive proves neither TCG nor containment.

**Necessary for that empirical question does not mean ready or authorized.**
Only Tony can authorize physical work. Exact artifact/source/provenance review,
applicable [security-incident prerequisites](gate-0-native-host-antivirus.md),
fresh-attempt enrollment, independent observation and durable uncertainty lockout
still apply. The [recovered enrollment/recovery gaps](gate-0-diagnostic-recovery.md)
are not cleared here; no dormant diagnostic activation, restart over uncertainty,
automatic reboot inference or retry workaround is proposed. If prerequisites
cannot be established, the experiment stays blocked. No phone is scheduled or used.

For the **complete H configuration**, no additional execution expansion is needed
to falsify the claim that it already exists: the generated device mismatch above
does so now. No new source-backed protected boot-state/enforcement replacement
has been supplied either. More desktop work becomes discriminating only with a
concrete new configuration or enforcing mechanism and its correspondence inputs;
repeating inventories cannot supply them. A phone result cannot select missing
components or waive those blockers. This is a stopping boundary, not a queue of
unapproved ports or builds.

Owner decisions before dependent implementation would include changing the guest
device/product selection, enabling/reviewing additional QEMU dependencies/devices,
replacing host-only/pathname backend entrypoints, choosing exec versus library
integration, and assigning any new trusted broker/boot-state enforcement owner.
Source review/build adoption needs its scoped authorization; material architecture,
security-boundary or product changes require explicit Tony approval and an ADR.
No removal of sensors, telephony, audio, verification, encryption or enforcing
guest SELinux is selected. If no acceptable concrete candidate can be offered,
**STOP / owner-approved NARROW / owner-approved REDESIGN** remains the decision;
there is no evidence here excluding every possible product-wide alternative.

## Licensing, privacy, validation and preservation

QEMU GPL/file-specific terms, U-Boot/kernel corresponding-source obligations,
GLib/PCRE2/libffi/libfdt and other existing build dependencies retain their
reviewed limits. Guest ANGLE/SwiftShader/LLVM/minigbm/ranchu and Rust/Cuttlefish
peer dependencies need full transitive qualification; audio models and firmware
metadata do not confer source completeness or redistribution rights. No binary,
model, new dependency, signing identity or source implementation is adopted.
Controlled image signing/lifecycle remains unresolved; ADR-0002 is not accepted.

Management, policy and Persona master state must remain beyond hostile guest,
QEMU, native worker and peer authority. Real is explicitly scoped visible
disclosure; Decoy/Empty/Deny never fall back to genuine host data. Guest permission
is not host authorization. No host VPN-slot use, real identifiers, private logs,
keys or confidential machine paths are published. No parser or cooperating peer
is accepted as enforcement after its compromise.

Actually performed: live read-only preflight; merged-evidence reconciliation;
five fresh immutable source reads/hashes; exact historical CI generated-config
reconstruction/hash comparison and source-gate comparison. Local checks passed:
foundation validation (137 files, 85 Markdown, 54 requirements, two ADRs), harness
validation, repository validation (141 tests: 137 pass, four existing Windows
skips), desktop readiness (27), offline image (45), and frame copy (four).
These checks validate documentation and existing controls, not full-phone
feasibility. Final review covers the complete two-file diff, relative links and
anchors, UTF-8, whitespace, regular file modes, source correspondence, public
privacy, unchanged licenses/dependencies and unchanged workflow applicability.

**Not Run:** new QEMU/backend/native compilation, Linux native/process suites
locally, guest-image build, Android/TCG/VM/emulator execution, boot, phone/USB/ADB,
APK installation, radio EOF runtime, audio/input/graphics runtime, physical
containment, networking/VPN or performance tests. No test policy or CI is changed.
Foundation applies to this two-Markdown-file change; Android and QEMU workflows
are path-filtered out, not passing results. New-head hosted checks remain
**unobserved until independent review**. Publication requires exactly one PR,
native association and one identity/association verification, then STOP without
polling CI/bots/reviews/mergeability. A publication/association failure is
**UNPRESERVED pending recovery PR or association repair**, reusing any existing PR.
