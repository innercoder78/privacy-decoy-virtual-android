# Android 17 boot and HAL dependency closure

**2026-10-19, America/Fortaleza. Gate 0 Unresolved; Gates A–G Not reached.**
ADR-0001 Accepted; ADR-0002 Proposed. Windows desktop source research only.
No engine, guest configuration, dependency or security redesign is adopted.
The [source ledger](gate-0-android17-boot-hal-sources.md) supplies immutable
identities, retrieval hashes, preflight and validation receipts. Source IDs below
refer to that ledger. This narrows [PR #23's assessment](gate-0-complete-android.md);
it does not repeat the general graphics/virtualization survey.

## Decision and new evidence

**CONTINUE SOURCE RESEARCH; STOP unchanged Cuttlefish import and dependent guest
construction.** There is a concrete mechanism hypothesis worth investigating,
but no closed ordinary-app-compatible Android 17 product configuration yet.
Three source findings change the next investigation:

1. **ARM64 defaults already select guest-local nonsecure key services.**
   `flags.cc` selects `oemlock,guest_keymint_insecure,guest_gatekeeper_insecure`
   for non-RISC-V targets. `BootconfigArgsFromConfig` selects the corresponding
   KeyMint/Gatekeeper APEXes. Their actual implementations register guest Binder
   services and run software implementations locally. Thus `/dev/hvc4` and
   `/dev/hvc11` existing in QEMU's console layout do **not** prove that remote
   Gatekeeper/KeyMint are the active ARM64 clients. [F1, F2, H1–H4]
2. **A real userspace vsock backend exists, but the reference QEMU launcher does
   not select it.** Pinned QEMU's `vhost-user-vsock` realizes a USER backend with
   a required chardev. The separately pinned AOSP `vhost-device-vsock` implements
   virtqueues, guest memory access and Unix-stream peers. Cuttlefish's shared
   socket library and a tombstone receiver caller support the Unix transport.
   However, `--vhost_user_vsock=true` checks for crosvm, while the Linux QEMU
   launch still appends kernel `vhost-vsock`. Its AOSP backend build is
   `rust_binary_host`, not a reviewed Android app binary. This closes the
   existence question, **not** Android integration, client closure or authority.
   [Q1–Q2, V1–V11, F1, C1]
3. **The kernel has a source lead beyond its build ID.** `kernel_version.mk`
   names `6.12.74-android16-6-g3ec022196c4e-ab15076761-4k`; the embedded revision
   resolves to `kernel/common` commit
   `3ec022196c4e9d5c1434599cdda63f622dd6f586`. Its Makefile identifies 6.12.74.
   This is a source-version correspondence, not proof of the exact configuration,
   toolchain, module ABI or binary reproduction. The Android 17 product selecting
   an android16-named kernel is not itself a mismatch. [K1–K4]

The local key services explicitly describe themselves as nonsecure/test
implementations; their source documents secure-environment requirements for real
devices. Retaining the reference setting in a research comparison is not approval
to ship it, assert hardware-backed protection, satisfy compatibility requirements,
or weaken guest security. Whether a qualifying guest security implementation can
be provided under PDVA's constraints remains blocking. A change to required
security guarantees would require Tony's explicit approval and an ADR; it is not
made here. [H1–H4; existing requirements 029–037]

## Precisely bounded configurations

**R — unchanged negative reference:** Android 17 r1
`aosp_cf_arm64_phone`, `PRODUCT_DEVICE=vsoc_arm64`, nonprotected Android boot,
QEMU VM manager on Linux, no caller override of the relevant launcher defaults,
and no separately supplied product-output bootloader. Host architecture matters:
compatible ARM64 takes the KVM branch; a noncompatible host takes the emulation
branch. Graphics `auto` is host-sensitive, so no single renderer is invented for
R. This is a source selection, not an observed launch or a claimed built `user`
artifact. No fully resolved release-config/build manifest exists in this review.

**H — narrow source-supported mechanism hypothesis:** the same phone and guest
framework contracts, explicit ARM virt/TCG, guest SwiftShader/plain virtio GPU,
matching composer and multitouch, ordinary virtio block/RNG/consoles, SLIRP
networking, and QEMU userspace-vsock paired with the pinned Rust backend and
matching Unix-service clients. Preserve AVB, encrypted storage, enforcing guest
SELinux, required services and separate host management authority. Preserve the
reference guest-local key-service selection only as a disclosed research fact;
its production security acceptability remains Unknown. Retain the selected sensor
protocol and provide a source-reviewed simulator, rather than deleting sensors.

H is **not a runnable command line or an accepted product**. It requires changes
to the reference launcher and new Android backend/build/transport review. No
existing artifact implements H. In particular, the PDVA cross-build explicitly
disables SLIRP and pixman/OpenGL; it cannot be relabeled as this configuration.
Do not move the VMM/backends into management or widen host authority to make H
work. [C1, F1–F3, Q1–Q3, V1–V10; existing cross-build recipe]

## Exact boot spine and preserved security inputs

The product includes core-64-bit/generic-system, handheld and telephony
system_ext, AOSP product, shared phone vendor, Virtualization product packages,
and ARM64 bootloader makefile. `vsoc_arm64/BoardConfig.mk` selects ARMv8-A,
arm64-v8a plus secondary ARM ABI and includes shared board, Bluetooth, camera,
GNSS, graphics, identity, reboot escrow, sensors, SwiftShader, telephony,
vibrator and conditional nonautomotive virgl board files. These includes are
not proof that every corresponding host backend is active. [C2–C5, C8]

For this phone, shared BoardConfig defaults to kernel 6.12 and ARM64. Kernel and
system modules come from `kernel/prebuilts/6.12/arm64`; virtual-device modules
come from the separate pinned common-modules prebuilt tree. First-stage module
selection names failover, nd_virtio, net_failover, virtio_dma_buf, virtio-gpu,
virtio_input, virtio_net and virtio-rng, plus block/console/PCI/vsock transport
from the system prebuilt directory. Wildcard Wi-Fi and PCI/vsock dependency
modules are configuration-dependent; remaining modules populate vendor/system
DLKM. The 16-KiB developer option also selects separate mainline/16k inputs;
`PRODUCT_MAX_PAGE_SIZE_SUPPORTED=16384` does not make those inputs identical to
the inspected 4-KiB kernel. This review does not close the alternate 16-KiB chain.
Guest Binder is a guest-kernel facility; the board requests `binder.impl=rust`
and the kernel prebuilt tree lists `rust_binder.ko`. No host Binder device is
passed through. Built-in/module configuration and full ABI closure remain
unverified. [C2–C4, K1–K4 and kernel tree inventory]

`vsoc_arm64/bootloader.mk` saying the product does not build a single bootloader
does not remove firmware. QEMU default setup first looks for the product-output
`bootloader`, then `etc/bootloader_aarch64/bootloader.qemu`; ARM QEMU consumes it
through `-bios`. The prebuilt module maps that path to `qemu_aarch64/u-boot.bin`.
U-Boot environment generation selects `run bootcmd_android`. The source mapping,
configuration and reproducible build for that exact firmware are **Unknown**.
The inspected prebuilt directory contains `System.map` and `u-boot.bin`, not a
resolved source manifest. No firmware payload was downloaded. [C1, C5, F1, B1, B2]

Boot header v4 and init_boot header v4 are selected; generic ramdisk is moved to
the 8-MiB init_boot partition. Vendor_boot carries the vendor ramdisk/module
inputs and bootconfig. `BOARD_INCLUDE_DTB_IN_BOOTIMG=true` is set; this alone
does not identify the final DTB consumed by the firmware or prove agreement with
QEMU's generated virt hardware description. The existing raw-Image reservation
control does not admit this firmware/ramdisk/DTB path. Persistent bootconfig
assembly reads built-in vendor_boot arguments, merges runtime settings and adds
an AVB hash footer. The persistent composite disk has U-Boot environment,
vbmeta and conditional bootconfig inputs. These are required dependencies, not
optional strings that can be omitted for a theoretical boot. [C2, B2–B5]

AVB is enabled with chained system, boot, init_boot, vendor_dlkm and system_dlkm
metadata and rollback-index locations. The reference uses public test signing
material; that is not PDVA release signing. Dynamic super groups contain
system/product/system_ext/system_dlkm and vendor/odm/vendor_dlkm/odm_dlkm.
Fstab requires logical first-stage mounts, slot selection and AVB, then metadata
and encrypted userdata. For the explicit f2fs/HCTR2 branch, source substitutions
select inlinecrypt, AES-256-XTS/HCTR2 file encryption, metadata key storage,
compression and filesystem checkpointing. Other filesystem selections require
their own exact generated fstab. `nofail` on product/system_ext for image mixing
does not make the phone UI/framework supplied there optional. [C2, C6, B6–B8]

First-stage init/module loading and mounted system/vendor/APEX must lead to
servicemanager, guest Binder, ART/APEX availability, Zygote and SystemServer;
guest display/input/app services must then operate. PR #23's immutable
system/core and frameworks sources remain the evidence for that spine. The
new APEX selectors refine which key services it starts; they do not replace
APEX verification, VINTF agreement, guest SELinux policy or initialization order.
F2 labels the Gatekeeper property assignment as preemptive for runtime selection;
the assignment and available APEX are observed, but actual activation in a built
image is not. No complete generated VINTF manifest or framework boot is claimed.

## Falsifiable comparison matrix

S = source observation; I = inference; H = hypothesis; U = Unknown.
“Required” means required for the stated selected path, not every Android device.
Positive tests below are acceptance criteria for later evidence, **not results**.
Every row inherits the rights/adoption conditions in the ledger; none is accepted
where source/build correspondence or redistribution rights remain missing.

| Critical dependency and selection | R versus H; authority/API/ABI/SELinux and TCB consequences | Positive evidence required; explicit negative falsifier |
|---|---|---|
| CPU/accelerator — required [C1] | S: compatible Linux host selects KVM; H explicitly uses TCG and must select CPU/GIC coherently. I: software emulation need not open KVM; host ARM64/Bionic execution, strict W^X, signals, page size and isolated policy remain U. QEMU translator/device model enters hostile-code TCB. | Exact selected machine/device objects and legitimate Android execution; reject any KVM open or executable-memory fallback. Changing only accelerator cannot clear vsock or any other row. |
| Firmware/DTB/boot headers — required [C2, C5, F1, B1–B5] | S: ARM `-bios` U-Boot; v4 boot/init_boot/vendor_boot, DTB and persistent config. H retains the verified boot contract. Ordinary app can own verified bytes, but current generic pathname loading/firmware dispatch is not bounded FD admission. Firmware is guest boot trust base; loader parsing is host TCB. | Match firmware source/config/toolchain, DTB and each signed ramdisk/partition to exact resources; missing firmware, DTB provenance, ramdisk or AVB input rejects closure. Direct Linux boot is not a substitute. |
| Kernel and modules — required, 16k branch conditional [C2–C4, K1–K4] | S: 4k version identifies a full kernel source commit; module tree separately pinned. H still needs generated config, toolchain and module ABI correspondence including Binder/DRM/virtio/filesystems. Guest kernel authority is emulated guest authority. GPL and module/source obligations remain. | Exact reproducible manifest/config and module dependency/load inventory; a build ID, abbreviated revision alone, missing module or mismatched ABI is insufficient. Do not infer 16k closure from max-page-size setting. |
| AVB/logical disks/metadata/userdata — required [C2, C6, B3–B8] | S: encrypted fstab and chained vbmeta; normal block path exists with vhost-user-block default false. H retains those guest services, app-owned storage and explicit resource delegation. Block/AVB/filesystem parsers, signing owner and disk lifecycle enter the trust analysis. No raw host disk authority. | Matching generated fstab, slots, super layout, encryption/key HAL and authentic signing inputs; reject disabled AVB/encryption, missing metadata or pretending public test keys are release trust. |
| Binder/APEX/ART/Zygote/SystemServer — required [PR #23 A1–A4; F2, H1–H4] | S: guest framework and local service registration; H needs full guest ABI, linker, APEX/VINTF/init/SELinux agreement. No host framework proxy replaces these. Mixed AOSP licenses and guest trust base remain to resolve. | Exact generated service/manifest/init closure followed eventually by real app execution; boot-complete text, a shell or a missing declared HAL is not acceptance. |
| KeyMint/Gatekeeper — required service contracts; remote choice conditional [F1–F2, H1–H6] | S: ARM64 defaults select rust_nonsecure and gatekeeper.nonsecure, not the remote FIFO clients. Local KeyMint runs its TA in-process; Gatekeeper registers software Binder services and SharedSecret. H has a real local implementation, but security/compatibility suitability remains U and blocking. No host TEE claim. Crypto/APEX dependencies and key-state protection require review. | Resolve selected VINTF/APEX and required security guarantees without weakening them; reject service deletion, claiming hardware-backed attestation, or adopting test-only security as a qualifying product. Remote selection additionally requires its actual host peer. |
| Host/guest vsock — required by R launch, consumers partly conditional [C1, F1, Q1–Q2, V1–V10] | S: kernel vhost is unconditional in Linux QEMU launch. H pairs QEMU USER backend with actual Rust Unix-stream implementation; library and tombstone caller have transport support. Not all service clients reviewed; launcher rejects explicit true for QEMU. Shared RAM, AF_UNIX/SCM_RIGHTS, epoll/eventfd, process lifetime and isolated-app policy remain U. Backend sees guest RAM and becomes hostile-input TCB; host build is not Android adoption. | Review exact Android build/FD transport plus every selected caller; reject `/dev/vhost-vsock`, unexplained AF_VSOCK host sockets, a backend name without implementation, or an unmodified QEMU launcher claimed to use it. |
| Networking — required capability; TAP/vhost-net conditional [C1, F3, Q3] | S: default TAP, vhost-net false; explicit SLIRP emits QEMU user netdevs. H has a source-supported userspace mechanism but PDVA build disables it. libslirp version/transitive rights, DNS, route/VPN behavior and isolated-worker delegation are U. Ordinary-app networking does not grant TAP or raw host network devices. | Pin/review libslirp and host-authorized transport, then independent route evidence under existing Gate D rules; reject TAP, physical-route bypass, or accepting hard-coded reference DNS as VPN-safe. No production networking broker adopted. |
| Sensors — required by selected product; custom package conditional [S1–S6] | S: multihal opens guest hvc18/19, fatal on missing descriptors/raw-terminal setup; real simulator receives corresponding host FDs and WebRTC/control input. H must retain coherent synthetic sensor protocol and policy. No genuine host sensor permission follows. Transport/parser/helper lifetime enters TCB; Android port/dependencies U. | Close simulator, goldfish sub-HAL, channel protocol and authorized transport; missing endpoints, removing HAL while keeping features, or silent real-sensor fallback rejects closure. Desktop source can resolve this before phone work. |
| Block/RNG/console/input/shared RAM — required mechanisms, extra devices conditional [C1–C2] | S: ordinary virtio block default; virtio RNG; console port ordering; file-backed shared RAM; vhost-user switches/rotary even alongside mouse/keyboard. pmem/pstore branches depend on architecture/files. H must replace ambient paths with admitted resources and match all retained clients; no general file broker. Sharing guest RAM with a helper expands the hostile resource/lifetime boundary. | Exact device/FD/port inventory including helper peers; reject assuming all vhost is kernel vhost, assuming all vhost-user is authority-free, or closing manager FDs as proof of mapping revocation. |
| Graphics/multitouch/phone UI — required [C1, F4; PR #23 C7–C11, Q2–Q5] | S: explicit GuestSwiftshader branch uses plain virtio GPU and guest software graphics; automatic graphics selection is host-dependent. H requires matching composer, minigbm/DRM, scanout and multitouch/IME/rotation. Existing binary has no qualified display adapter. Host app-window presentation is plausible; direct isolated GPU/input device authority is not assumed. | Real compatible device/buffer/event contracts and eventual interactive app frames; headless boot, mouse-only input, a screenshot or synthetic frame cannot satisfy this row. |
| Audio, camera, radio and other selected services — required where product/requirements demand; endpoint choices conditional [C3, C7, F2] | S: phone inherits broad features; QEMU declares AC97 with `driver=none`; confirmation UI boot flag is zero for QEMU; camera/lights/modem ports are conditional. Those facts neither prove working audio nor permit deleting mandatory features. H's complete service-client/dependency closure remains U. | A retained-service inventory with exact backend for audio and every required feature; reject treating disabled host output as working audio, or a configurable package hook as an implemented replacement. |
| Provenance, rights and containment — required for both [ledger; existing containment/revocation records] | S: source licenses and pins identify references only. Firmware/modules and new backend/build closures are incomplete. H also inherits unresolved whole-tree completion, FD/mapping revocation and manager-loss behavior. No architectural adoption or approved supervisor follows from this table. | Complete corresponding-source/rights and authority review, then independently observable bounded lifecycle; missing rights, opaque required input, retained hostile authority or restart during uncertainty rejects acceptance. |

The deliberately invalid controls are therefore rejected by identifiable source
witnesses: TCG plus kernel vhost; missing firmware/ramdisk/module/partition/AVB;
headless-as-interactive; a named backend without its clients/build; and unresolved
source/redistribution rights. This is a manual source audit. No executable oracle
was added: a test asserting this hand-authored matrix would add no independent
evidence. A later checker would need actual pinned selected build/config inputs.

## Smallest next work and phone-test decision

1. **Worth pursuing?** Yes, H's userspace-vsock + Unix peers, ordinary block,
   software graphics and guest-local service mechanisms warrant bounded research.
   No, the evidence does not identify a complete qualifying app-compatible phone
   configuration. R remains a negative baseline even under TCG.
2. **Blocking dependencies:** exact U-Boot source/build/AVB/DTB correspondence;
   kernel/config/toolchain and module ABI closure; qualifying key-service security;
   all retained host clients and Android backend builds; audio/interactive-device
   closure; ordinary-app memory/network/lifetime authority; redistribution rights.
   The **next desktop question** is the exact source/configuration/build manifest
   for `bootloader_qemu_aarch64` at B1, including `bootcmd_android` and the DTB,
   boot/init_boot/vendor_boot and persistent-vbmeta contract. This is upstream
   source/build research, not a reason to acquire or boot an image.
3. **Smallest next experiment:** a source-correspondence check for that firmware.
   Positive: an immutable upstream build record maps the selected prebuilt to a
   complete source revision, patches/configuration and toolchain, and its reviewed
   Android boot path accounts for every required signed input and DTB. Negative:
   the record maps another binary/configuration, requires an unavailable input or
   prohibited authority, or the source path cannot implement the selected boot
   contract. Missing/inaccessible records are **Unknown**, never a pass. Stop
   firmware-dependent construction until this is resolved. Do not infer that the
   entire candidate is impossible solely because one metadata lookup failed.
4. **Narrow eventual Galaxy S25+ falsifier:** the existing fixed, trusted native
   launch control can independently test packaged ARM64 dynamic-PIE execution
   from the isolated service on Tony's stock user build. After separate physical
   authorization and the existing provenance/security-incident prerequisites,
   require the exact 40-byte result, expected exit 42, specified identity/domain/
   capability/FD fields and direct-child reap with no timeout or uncertainty.
   Executable/linker denial, wrong identity/record/status, signal, timeout or
   uncertain cleanup fails or leaves Unknown according to the existing protocol.
   No retries around uncertainty and no policy/security weakening. See the
   [native launch record](gate-0-isolated-native-launch.md) and
   [integration prerequisites](gate-0-qemu-worker-integration.md).
5. **Phone testing now?** No new phone test is justified by this boot/HAL slice.
   The trusted native-launch probe has an independently interpretable narrow
   question, but cannot answer firmware, vsock-client or guest-security closure.
   These desktop questions still prevent interpreting any proposed complete-guest
   launch as evidence for H. No new backend is ready for an Android authority
   experiment. Continue source research; do not request redesign approval merely
   to bypass unresolved dependencies. If closure demands a material security or
   architecture change, stop and present that concrete ADR for Tony's approval.

No phone connection, ADB, APK installation, guest execution/image acquisition,
new guest build, QEMU integration, tool installation, privileged authority,
proprietary Google binary, host VPN, SDK/permission or security-policy change
was performed. A native launch, Linux boot or successful cross-build would not
pass Gate 0. New-PR hosted CI remains **pending/unobserved at publication**;
the ledger records only checks actually observed before publication.
