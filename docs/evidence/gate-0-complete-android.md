# Gate 0: complete interactive Android 17 source feasibility

Review: **2026-10-18, America/Fortaleza; Codex Desktop LOCAL, Windows x86_64.**
Source research only. **Gate 0: Unresolved. Gates A–G: Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. QEMU/TCG is a research
hypothesis, not an adopted engine. No guest, emulator, APK or phone was executed.

**Recommendation: continue-source-research, with STOP on full-guest construction
and integration.** A plausible software-only device path exists in source, but
the inspected Android 17 reference configuration does not close inside an
ordinary app. This is not evidence that all such implementations are impossible.
No redesign is approved or required by a demonstrated universal impossibility.
Any material change still requires Tony's approval and an ADR.

This investigation adds a concrete guest/device contract to the existing
[platform authority](gate-0-platform-authority.md),
[worker integration](gate-0-qemu-worker-integration.md),
[ARM64 reservation](gate-0-arm64-boot-plan.md),
[TCG memory](gate-0-tcg-executable-memory.md) and
[containment](gate-0-worker-containment.md) work. It does not repeat their
experiments. Scope: PDVA-REQ-001–015, 028–045, 047–048 and 054.
Exact sources, hashes, retrieval limitations and preflight are in the
[companion ledger](gate-0-complete-android-sources.md).

## What the new source comparison establishes

**Source observation 1 — a Cuttlefish guest is not just system.img plus virt.**
At Android 17 r1, the ARM64 phone product inherits system, system_ext, product
and vendor definitions. Its shared BoardConfig defaults to kernel line 6.12,
selects first-stage virtio modules, boot header v4, separate init_boot/vendor_boot,
AVB and dynamic partitions. Its fstab requires matching logical partitions,
metadata and encrypted userdata. The QEMU manager's ARM route supplies `-bios`
with a bootloader, not PDVA's restricted raw ARM64 Image path. The product's
`TARGET_NO_BOOTLOADER := true` means it does not build one fixed bootloader;
it does not mean this launcher boots without firmware. [C1–C6, C9]

**Inference:** the existing bounded kernel snapshot/reservation controls cannot
admit this complete boot chain unchanged. A source-built direct-boot alternative
would need an explicitly reviewed ramdisk, bootconfig, partition/AVB, DTB and
module contract. It must not silently disable guest verification, omit required
services or inherit ambient path loading. The exact source/config/toolchain
correspondence for the reference prebuilt kernel remains Unknown: its retrieved
metadata contains build ID `15076761`, not a source revision. No kernel binary
was acquired. [C2, C6, K1; existing ARM64 record]

**Source observation 2 — the reference launcher has host-service dependencies.**
On Linux, Cuttlefish's QEMU manager unconditionally adds
`vhost-vsock-pci-non-transitional`; pinned QEMU realizes that device by opening
`/dev/vhost-vsock` unless supplied a preopened FD, then initializes a **kernel**
vhost backend. It is not a software substitute for that kernel facility. The
launcher also creates keymaster, Gatekeeper, Rust KeyMint and sensors console
endpoints, vhost-user input endpoints and file-backed shared RAM. Compatible
Linux host/guest architectures select KVM. TAP is a conditional networking mode,
not an unconditional requirement. Changing just `-accel` to TCG would leave
these other dependencies. [C1, Q1]

**Inference:** this launcher cannot be imported as an ordinary-app recipe.
Receiving an FD cannot create authority that no permitted ordinary-app component
has. Nor does replacing vhost-vsock with vhost-user automatically implement the
peer service, bound its authority or satisfy its guest clients. Shared device.mk
lists remote and nonsecure KeyMint/Gatekeeper alternatives and conditional Trusty
VM configuration; package inclusion alone does not identify the active APEX/HAL
selection. Source research must resolve those selections and their clients,
rather than assuming every service is mandatory or deleting all endpoints.
Software guest key services would not supply hardware-backed attestation. [C1, C3]

**Source observation 3 — software graphics and touch have identifiable contracts.**
The GuestSwiftshader branch selects guest EGL `angle`, Vulkan `pastel`, gralloc
`minigbm`, a configurable composer with DRM display discovery, and QEMU
`virtio-gpu-pci`. The guest graphics init file copies boot properties into the
HAL-selection properties. Shared graphics configuration includes DRM/ranchu
composer choices and minigbm allocation/mapping. The SwiftShader configuration
explicitly requests guest executable-memory support. These are guest-side
choices, not permission for host TCG or direct host GPU access. [C1, C7, C8, C10]

The reference QEMU input configuration creates mouse and keyboard devices; that
does not establish touchscreen gestures. Pinned QEMU separately implements
virtio multitouch with slots, tracking IDs, absolute coordinates and
`INPUT_PROP_DIRECT`. Android EventHub recognizes multitouch event capabilities.
Cuttlefish's touchscreen configuration also supplies display association and
orientation awareness, but its device name describes a different vhost-user
touchscreen. It cannot be assumed to match QEMU's device automatically. [C1,
C11, Q2, A5]

**Inference:** there is a specific possible software rendering/touch path to
investigate, without direct GPU passthrough or host-wide input injection. There
is no reviewed Android transport or matching image implementing it. The existing
cross-build disables pixman/OpenGL and has no Android display adapter. Its UI
helpers are not a GUI result: QEMU's VNC source set requires pixman, and virtio
GPU source sets name pixman as a dependency. Conversely, QEMU contains a minimal
pixman compatibility header, so absence of external pixman alone is not proof
that all framebuffer operations are impossible. Inspect the actual selected
device objects/link closure before asserting availability. [Q3–Q5; existing
cross-build/integration records]

## Minimum dependency and interface matrix

This is a minimum **contract inventory**, not a proven smallest image or an
exhaustive resolved build graph. S = inspected source; I = inference;
U = Unknown. "Provides" distinguishes upstream source from PDVA's constrained
research artifact. Source IDs resolve in the companion ledger. Rights/TCB column
identifies review obligations; none is an adoption or shipment approval.

| Required component / interfaces | Pinned candidate provides? | Ordinary-app authority and restrictions | Rights, TCB and smallest falsifier / Unknown |
|---|---|---|---|
| Guest ARM64 CPU, exceptions/MMU, timer, interrupt controller, PSCI, virtio PCI/MMIO and DTB | QEMU ARM virt/TCG provides machine mechanisms (existing integration/boot review); no Android CPU/kernel configuration qualified | I: software execution needs no KVM intrinsically; packaged ARM64/Bionic code, signals, threads and JIT must work under actual app policy. API-30 cross-link is not a supported-host minimum | QEMU GPL/file-specific closure; translator/device model is hostile-input TCB. Falsifier: a required guest CPU/device feature absent from the exact compiled machine; host TCG runtime remains U |
| Android-capable kernel, matching modules, first/second-stage init, ramdisk and bootconfig | No Android kernel supplied by QEMU. C2/C6/A1 identify binderfs, virtio modules, mount/APEX and partition requirements; kernel release line is not its source identity | Guest privileged init and guest Binder run within emulated guest authority, not host root/Binder passthrough. Host only supplies validated resources; existing direct-boot admission is incomplete | Kernel GPLv2 plus per-file notices, build tools, modules and firmware provenance. Falsifier: any required module/config/boot input lacks a reproducible matching source identity. K1 does not resolve that gap |
| Complete userspace: Bionic/linker, ART/APEX, servicemanager, Zygote, system_server, framework and package/app services | A1–A4 trace init → app_process64 `--start-system-server` → Zygote/SystemServer service startup; build files include runtime, surfaceflinger, vold and phone UI. QEMU supplies none of this userspace | I: guest syscalls stay on guest kernel; no host hidden API is needed for guest framework itself. Full ABI/APEX/VINTF/SELinux and runtime dependencies must agree; headless survival is not app execution | Mixed AOSP component licenses; guest system is functionality/image trust base, while host isolation must tolerate its compromise. Falsifier: unresolved mandatory HAL/APEX/service or privileged host helper; full resolved graph U |
| Persistent block storage, boot verification, metadata/userdata, entropy and guest key services | C1/C3/C6 expose block/RNG/console mechanisms and guest service alternatives; raw block FD mechanism exists, but whole boot/storage caller integration is absent | Exact file FDs and software devices are plausible; ordinary app can own private files. No general file-open broker, TAP/device grants, raw host key material or imported boot keys. Disk capacity, staging and crash durability U | Guest key services are not certified secure hardware. Block/image/update parsers and trusted resource owner enter TCB. Falsifier: active encryption/KeyMint dependency requires inaccessible host peer or unlicensed component; selected software alternative must be traced |
| SurfaceFlinger, RenderEngine, composer, allocator/mapper, EGL/GLES/Vulkan and guest DRM driver | A6/C7–C10 identify software path; upstream virtio GPU exists. PDVA artifact has no demonstrated matching renderer/device closure | Guest SwiftShader CPU/JIT work is translated by host TCG: nested translation/rendering cost U. Host isolated worker cannot directly use GPU driver under inspected policy. Host app presenting copied pixels in its own UI is plausible, with a bounded validated adapter | ANGLE BSD-style, SwiftShader Apache-2.0, minigbm BSD-style, drm_hwcomposer Apache-2.0 with listed MIT exception; transitive code not audited. Falsifier: mandatory buffer modifier/fence/format/capset unavailable in selected QEMU/guest pair |
| Display output to host app: scanout updates, stride, size, fences/ownership and resize | QEMU display listener hooks exist; current two synthetic 64×64 frames are not guest output | Ordinary app window/Surface can show pixels; it gives no host System UI ownership. Copy bounds, synchronization, queue pressure and stale-instance rejection remain unimplemented; no general QMP/VNC endpoint adopted | Host parser/renderer adapter is additional TCB. Falsifier: no bounded software scanout path compatible with guest composer; screenshots or serial output are inadequate positive controls |
| Touch/multitouch, keyboard, Back/Home/navigation, guest input dispatch | Q2/A5 supply compatible-looking event vocabulary; C1 mouse/keyboard is insufficient; C11 name/display association needs matching | App receives only its own UI events, maps them into guest virtual devices. No host `/dev/input`, uinput or privileged injection needed by hypothesis. Slot tracking, cancellation, coordinates/density/orientation and key layout U | Device emulation plus validating transport/host UI enter TCB. Falsifier: mismatched advertised event bits/device name/display association, or stale release/cancel leaves a stuck contact |
| IME/text editing and rotation | A3 starts input-method/window services; a guest IME package and configuration are still required. A host keyboard keycode path is not Unicode composition | Lowest-extra-interface hypothesis: touch a guest-rendered IME. Host IME composition/selection bridge would need separate policy and protocol; not adopted. Rotation requires guest display/input transforms and configuration, optionally synthetic guest sensor events, not host sensor disclosure | Guest IME licenses/configuration and text privacy; host bridge adds TCB if chosen. Falsifier: app field cannot commit composed text or keep touch aligned after rotation. Keyboard socket existence proves neither |
| Basic virtual phone services: launcher/SystemUI/settings, time, power/battery; audio/network/sensors according to product scope | A4 lists Launcher3QuickStep/SystemUI; C3/C4 include many HALs. C1 has host endpoints and AC97 with `driver=none`; that is not working audio | Real hardware access is not required merely to render a guest phone; absent hardware needs coherent guest service behavior. Audio/network integration is separate, authorized ordinary APIs only. Networking still needs host-VPN evidence; no TAP or production ADB | Each retained HAL/backend/license must be enumerated. Falsifier: UI/startup blocks on removed peer, or required interaction depends on an unavailable bridge. No implied camera, telephony, GMS or Play compatibility |
| RAM/CPU/JIT budget and lifecycle | TCG split-memory research and Linux controls exist; no phone envelope or complete-guest latency measurement | Account for resident guest RAM, TCG code/cache/metadata, renderer buffers, host queues and management overhead; virtual aliases differ from RSS. Android 17 memory limits, LMK/background rules, 4/16-KiB alignment, thermal/battery limits apply; no ADB exemptions | Host OS remains resource authority. Falsifier: required working set/latency exceeds predeclared ordinary-device budget. Kernel boot time or desktop TCG speed is not that evidence |
| Hostile-worker containment, death and capability revocation | Existing source and controlled Linux witnesses only; arbitrary native compromise and Android whole-tree completion remain U | Isolated UID/SELinux is a prospective authority boundary; same-UID app worker is insufficient for management secrets. Revocation cannot erase copied bytes; cooperative exit or manager FD close does not revoke retained mappings | Host kernel/framework, trusted endpoint owners and validation code are TCB. Falsifier: surviving child/retained access after accepted teardown or restart without independent completion; use existing containment/lifetime/revocation records |
| Legitimate image acquisition, build and distribution | No guest image adopted; official source manifest exists but references prebuilts and tag-based project revisions | Source-only custom image is plausible without host privilege. Resolve every project, generated input, kernel/module/bootloader and tool to immutable identities; use a user/release-equivalent guest and controlled signing, not an imported debug demo | No blanket redistribution approval from AOSP name or root license. Falsifier: selected mandatory blob lacks rights/source correspondence or GPL/notice/source obligations cannot be met. GMS licensing/certification remains separate U |

## Candidate feasibility matrix

| Candidate/configuration | Complete guest potential | Ordinary-app fit / disposition |
|---|---|---|
| Pinned QEMU/TCG plus a source-built, explicitly configured complete Android 17 virtual device | Mechanisms plausibly cover CPU, block, software scanout and virtual input; image/HAL/device closure, performance and security unproved | **Continue-source-research only.** No engine selection, no full-guest build/integration |
| Unchanged pinned Cuttlefish QEMU launch/product | Concrete full-phone reference; bootloader, HAL peers and graphics selections identify needed work | **STOP unchanged import.** Kernel vhost/compatible-host KVM and external endpoints are not an ordinary-app contract |
| GuestSwiftshader + plain virtio GPU | Specific source-grounded software-rendering branch; requires full guest graphics stack and transport | Plausible without direct host GPU; **Unknown** resource/usability/device closure. Guest executable memory is not host TCG authority |
| Virgl/gfxstream/rutabaga host graphics route | Requires a different renderer/protocol/capset closure than plain scanout | **Unknown / not adopted.** Existing isolated-worker GPU denial is material; moving renderer authority to management requires security design and owner review |
| AVF/custom VM, direct KVM/system crosvm | Existing platform review establishes restricted access class | **STOP for ordinary-app route** under inspected policy; no hidden grants or Microdroid substitute |
| Android QEMU wrappers; browser/WASM alternatives | Existing survey is packaging/reference evidence, not complete Android 17 proof | No new qualifying full-phone evidence here. Reuse prior findings rather than repeat a vendor survey; no selected fallback |

## Four distinct outcomes

| Outcome | Minimum witness | Does not establish |
|---|---|---|
| Serial/Linux boot | Guest kernel reaches a controlled init/console on the exact machine | Android userspace, framework, GUI or interaction |
| Headless Android boot | Matching init/APEX/ART, Zygote, system_server and required services survive and execute a controlled guest app | SurfaceFlinger output, input or usable phone experience; a boot-complete property alone is insufficient |
| Working Android GUI | Guest-rendered launcher/app frames traverse real compositor, virtual display and host presentation | Touch, IME, rotation, navigation or bounded latency/lifecycle |
| Complete interactive Android phone | Real guest apps respond to touch/gestures, text composition, navigation and rotation; storage and lifecycle behavior meet declared budgets | Host isolation, legitimate distribution, Play certification or attestation compatibility |

None has been observed in PDVA. The existing synthetic harness is not counted in
any row. A normally unrooted guest still needs privileged guest init/system
services; that is distinct from requiring root on the host or giving guest users
a root shell.

## Three most consequential unresolved blockers

1. **A closed, legitimate Android 17 boot/device/HAL bill of materials.**
   Smallest useful evidence now: a fully resolved source-only product/config
   manifest covering kernel + modules + bootloader/ramdisks + AVB/partitions +
   active HAL/APEX choices, with each external endpoint mapped to an allowed
   user-space implementation or a justified guest configuration. Include rights
   and source-to-prebuilt correspondence. One mandatory inaccessible kernel
   device, unavailable host service, or unlicensed/opaque input falsifies that
   exact configuration. Negative control: unchanged C1 must be rejected for
   kernel vhost dependence; merely replacing KVM by TCG must not make it pass.
   This source closure can remove a configuration blocker but cannot prove boot.

2. **An interactive software graphics/input stack within an ordinary-app budget.**
   Smallest evidence now: selected guest composer/gralloc/renderer/DRM and exact
   QEMU device/capset/buffer/fence/event contracts, plus a declared RAM/CPU/frame
   and input-latency budget. A missing required buffer/device feature falsifies
   the proposed pairing without running a guest. Negative controls: mouse-only
   is not multitouch; raw keycodes are not IME composition; a headless build or
   static image is not a GUI. Later, only separately approved bounded ordinary
   device evidence can falsify or support usability and memory/thermal fit;
   desktop results cannot clear it. No arbitrary numerical pass threshold is
   invented here.

3. **Enforcing host authority after arbitrary native worker compromise.**
   Smallest evidence now is the still-missing exact ordinary-app authority and
   independent completion contract identified in the existing containment and
   lifecycle records. It must cover descendants, retained resources, manager
   death and uncertain teardown, not a self-report. A surviving capability or
   accepted restart during uncertainty falsifies the claim. Existing Linux
   mapping/descendant/semantic-mutation controls are useful negative witnesses;
   repeating them does not supply Android authority. Eventual physical proof
   requires separate approval and remains forbidden in this task.

## Acquisition, rights and experiment decision

Basic Android boot does not require acquiring Google services. Investigate an
AOSP-derived controlled image with a resolved manifest and source-built matching
virtual hardware support. Preserve per-file licenses/notices and corresponding
source obligations for kernel/QEMU and other copyleft components; audit graphics
and build transitive dependencies separately. The reference product contains
conditional vendor Widevine and Trusty-related paths: exclude proprietary inputs
from any proposed AOSP-only closure and prove the remaining selected services,
rather than assuming the word AOSP guarantees a binary-free build. [C3, M1, L1–L4]

Official build documentation calls for a substantial Linux build environment;
it is not an instruction to install tools on Tony's Windows computer. Neither an
SDK image nor a public CI download carries an automatically established right
to redistribute the resulting image. No such image was downloaded. Proposed
separate image delivery remains under Proposed ADR-0002; no signing or release
architecture is adopted. GMS/Play acquisition rights, certification, supported
updates and integrity behavior remain separate compatibility work, with no
proprietary binaries or certification/attestation bypass.

**No additional executable desktop experiment is justified in this slice.**
Another serial boot, cross-build or synthetic framebuffer would not discriminate
the newly identified missing product/HAL closure. A source-only dependency
closure review is justified next; do not construct a full guest to answer it.
After that closure, a separately scoped static device/format contract checker
could be useful if it consumes actual selected build outputs and rejects the
negative controls above. A hand-authored list testing itself is not evidence.
Nothing here authorizes renderer/broker changes, engine adoption or Gate A work.

## Validation and limits

Sources were read at immutable IDs, with Gitiles TEXT decoding and SHA-256
records. Five decisive QEMU upstream files were independently byte-compared to
the clean retained Git blobs. Product includes, boot path, vhost realization,
graphics property propagation and input capabilities were traced; no complete
AOSP dependency graph or binary correspondence is claimed. Failed lookups and
the unresolved kernel provenance are retained in the ledger.

Local foundation, repository-regression, harness-authority and whitespace
validation results are recorded in the ledger after execution. No new runtime
test was added; missing Android/guest tests remain **NOT RUN**, not passes.
The PR changes documentation only. The publication's hosted CI is
**pending/unobserved**; preflight successes apply only to the old exact-main SHA.

[C1–C6, C9]: gate-0-complete-android-sources.md
[C2, C6, K1; existing ARM64 record]: gate-0-complete-android-sources.md
[C1, Q1]: gate-0-complete-android-sources.md
[C1, C3]: gate-0-complete-android-sources.md
[C1, C7, C8, C10]: gate-0-complete-android-sources.md
[C1, C11, Q2, A5]: gate-0-complete-android-sources.md
[Q3–Q5; existing cross-build/integration records]: gate-0-complete-android-sources.md
[C3, M1, L1–L4]: gate-0-complete-android-sources.md
