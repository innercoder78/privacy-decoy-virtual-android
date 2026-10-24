# Gate 0: Android 17 graphics configuration closure

Review: **2026-10-24, America/Fortaleza; Windows x86_64; source only.**
**Gate 0 Unresolved; Gates A–G Not reached. ADR-0001 Accepted; ADR-0002 Proposed.**
Scope: existing graphics/product/source obligations PDVA-REQ-001–015, 034–045,
047–048, 054; accompanying Persona clarification of 016–027, 031–032 and 039–043.

## Question and disposition

Can the Android 17 / API 37 `aosp_cf_arm64_phone`, explicit
`guest_swiftshader`, `hwcomposer=auto`, ranchu GuestFrameComposer, ANGLE/Pastel
and minigbm establish one matching framebuffer and DRM/atomic-fence contract with
plain QEMU `virtio-gpu-pci` 2D, blob off, no host GL renderer?

**Overall: Unknown because of generated-configuration and installed-kernel/module
correspondence gaps. STOP dependent construction.** This is a research comparison,
not an adopted product, engine, backend or build. The
[previous graphics record](gate-0-android17-software-graphics.md) already rejects
the unchanged PDVA QEMU recipe; it was not rebuilt or reconsidered here.

New source findings narrow the question:

1. The guest textproto takes precedence over android-info; missing BGRA fields
   default false, but a present malformed textproto fails rather than falling back.
   The inspected phone android-info alone implies RGBA, not an observed generated
   or installed value.
2. The prior kernel source lead advertises eight primary-plane formats, including
   ABGR8888 and ARGB8888. However, its **non-blob dumb allocation creates a fixed
   host-XRGB resource**, and QEMU's ordinary scanout uses that resource format.
   A successful AddFB2 or matching advertised format list does not change it.
   On little-endian ARM64, RGBA/ABGR bytes and that BGRX resource disagree on red
   and blue. **Inference: the RGBA + this exact dumb-resource source subcase is
   incompatible with correct color interpretation; STOP that subcase.** This is
   not an observed installed-driver result. Selecting BGRA would require a new
   explicit configuration and complete composer/conversion/fence proof, not a
   claim that changing one flag fixes graphics.
3. Atomic/fence mechanisms exist in the kernel lead, but the composer ignores the
   return from its swapchain wait, and the kernel flush wait is bounded without
   checking its result. Thus even source mechanism presence does not establish
   safe reuse on failure or completion of host presentation.

**Hypothesis:** full interactive Android remains constrained, not globally
falsified. No coherent generated/installed pairing is established here.

## Verified baseline, procedure and preservation

GitHub commit metadata, fetched main and a separate remote-ref query agree on
`4c277816747cc0572050cf4a4d2205a5b7f487e9`, the merge of
[PR #36](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/36).
Connector search and complete REST open-PR inventory both returned zero: there
were no open heads/bases, diffs/files, checks, reviews, comments or threads to
inspect or reuse. Relevant history and all three workflows were read.
[Baseline run 40119814930](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40119814930)
has successful foundation job `120948704443` and offline-image-windows job
`120948704215`; their steps and execution logs were inspected, including exact
checkout SHA and validation results. Android/QEMU workflows are filtered out for
this documentation slice, not additional passes. [GitHub Status](https://www.githubstatus.com/)
reported All Systems Operational during preflight.

Reviewed governance, requirements, architecture, gates, ADRs, acceptance criteria,
provenance/dependency records, all nine requested Persona-related documents and
the prior complete-Android, boot/HAL, graphics and QEMU-integration records/ledgers.
Local branches, one worktree, no stashes, clean tracked state and ignored source,
toolchain/build assets were inventoried. Initial tracked modes were all 100644.
No applicable AGENTS.md was found. The previous branch and ignored assets were
preserved; the historical repository was not modified. A new focused branch starts
at the verified merge. Sandbox Git/network failures were resolved through approved
escalation, not bypassed.

Procedure: read only pinned source; rehash all 36 prior graphics file receipts
against the merged ledger; retrieve bounded additional Gitiles TEXT files, base64
decode raw bytes and SHA-256 them; inspect source predicates and call paths. Read
QEMU from its clean retained Git checkout at the prior pin. Follow format selection,
dumb allocation, PRIME, AddFB2, atomic commit, response fencing and reuse. No
generated graph was substituted with a handwritten capability oracle. The source
environment is a Windows desktop; the candidate guest ABI is little-endian ARM64.
No target build variant, installed artifact or supported physical host is asserted.

The public disposition and immutable links/hashes are the reproducible record.
Ignored convenience copies are not independently backed-up private evidence.
No new private-data evidence was collected; independent backup of pre-existing
private assets was not established or re-attested. Publication/association failure
would leave the task **UNPRESERVED pending recovery PR or association repair**.

## Configuration: four different evidence levels

C, G, M and Q denote the immutable Cuttlefish, goldfish, minigbm and QEMU pins in
the [prior graphics ledger](gate-0-android17-software-graphics.md#source-identities-and-selected-graph).
K denotes kernel/common `3ec022196c4e9d5c1434599cdda63f622dd6f586`, the
[prior boot/HAL source lead](gate-0-android17-boot-hal-sources.md), not proven module
corresponding source. New file receipts are below; prior IDs C2/C4/C7/C10,
G1–G7, M1/M3/M4 and Q3–Q5 identify the reused files.

| Level | Source observation or missing receipt |
|---|---|
| Source default | C `GuestConfig` in `flags.h` initializes `supports_bgra_framebuffers=false`. ARM64 phone product inherits shared phone vendor/graphics configuration. Shared phone android-info has no BGRA key. |
| Explicit selected option | Research fixes guest_swiftshader and auto composer, with no custom property override; this resolves ranchu/Pastel through the previously traced predicates. It does not select a generated textproto or prove its absence. |
| Generated configuration | C `ReadGuestConfig` checks the system-image directory for `cuttlefish-guest-config.txtpb` first. If present, parsing must succeed; `graphics.bgra_framebuffers_supported`, when present, replaces the false default. Only when the file is absent does android-info parsing run; only the literal `supports_bgra_framebuffers=true` selects BGRA. Actual packaged textproto/android-info and emitted bootconfig are **Unknown**. |
| Installed runtime | `instance.set_guest_uses_bgra_framebuffers` feeds QEMU manager's `androidboot.hardware.hwcomposer.display_framebuffer_format`: true emits `bgra`, false `rgba`. Guest init copies `ro.boot.hardware.hwcomposer.display_framebuffer_format` to `ro.vendor.hwcomposer.display_framebuffer_format`; G `GetHostDisplayPixelFormat` selects BGRA_8888 only for `bgra`, otherwise RGBA_8888. Installed properties, init/APEX selection and runtime formats are **Not tested / Unknown**. |

This is precedence, not a merge: a textproto lacking the graphics field does not
inherit android-info's true value. An unavailable generated product directory is
not evidence that its textproto is absent. Exact release/variant, Vulkan support,
mapper release flag, installed ANGLE/Pastel/composer modules, VINTF/init/linker graph
and boot-property provenance remain required, as in PR #36.

**Upstream claim:** G `Common.cpp` explains a historical RGBA kernel patch and
BGRA compatibility. That comment does not identify the installed kernel and is
not a current primary-plane format table. K's actual eight-format table is the
source observation used here.

## Allocator, primary plane and first format falsifier

**Source observation:** GuestFrameComposer creates a DRM swapchain
using `GetHostDisplayPixelFormat`, HW_COMPOSER plus frequent software read/write
usage. M's gralloc helper maps RGBA_8888 to DRM ABGR8888 and BGRA_8888 to DRM
ARGB8888; HW_COMPOSER requests scanout/texture usage. The allocator resolves format
and usage before checking a supported combination. Its real non-3D path strips
BO_USE_SCANOUT for non-XRGB8888 and retains linear CPU/render combinations.
This is not conversion to XRGB and does not authorize scanout by itself.

`virgl_2d_dumb_bo_create` aligns non-R8 dimensions to its tile size and calls
`drv_dumb_bo_create_ex` with BO_QUIRK_DUMB32BPP. The helper sends width, height,
32 bpp and flags zero to CREATE_DUMB, then derives metadata from returned pitch
and the requested format. It sends no requested color FOURCC in that ioctl.
Linear metadata, pitch, offsets, sizes and modifier correspondence matter; a
different tiled/blob path is not interchangeable. PRIME export supplies gralloc
FDs; ranchu imports the first FD with `drmPrimeFDToHandle`, uses handle format,
stride and offset with `drmModeAddFB2`, flags zero, not AddFB2WithModifiers.

K supplies GEM dumb allocation/map and PRIME mechanisms. When resource-UUID
assignment is not supported, its non-blob export path marks UUID state as an error
but can still export a DMA-BUF; a failed assignment when that feature is advertised
is a separate error path.
Import from the same DRM device reuses the GEM object; generic foreign scatter/gather
import ends in `-ENODEV`. Matching allocator/composer DRM device selection is thus
a required correspondence receipt, not a promise of universal DMA-BUF import.

K `virtgpu_plane.c` gives non-cursor planes eight formats and uses atomic helpers.
But K `virtio_gpu_mode_dumb_create` requires 32 bpp and sets
`params.format=virtio_gpu_translate_format(DRM_FORMAT_HOST_XRGB8888)`.
With blobs off this is a resource-create-2D path. On little-endian ARM64 that
translation is VIRTIO_GPU_FORMAT_B8G8R8X8_UNORM. Plane update transfers raw dumb
buffer bytes, then calls ordinary SET_SCANOUT with resource ID and rectangle;
there is no replacement format argument. Q stores the create-2D format in its
pixman image, copies transfer bytes and derives scanout format from that image.

**Inference / conditional falsifier:** RGBA_8888/ABGR8888 memory interpreted as
B8G8R8X8 exchanges red/blue for unequal channels. AddFB2 success cannot repair that
contract. The first exact mismatch is resource creation's fixed color layout,
not absence of ABGR from the plane table. Stop this RGBA + K non-blob dumb subcase;
do not add a host swizzle, select another backend or manufacture a guest build.
BGRA/ARGB channel order aligns with that resource's RGB lanes, but alpha is ignored
and the selected composer's CPU conversion/output, allocation/device identity,
generated configuration and fences still need proof. It is not an approved repair.

## Atomic fences and lifetime

**Source observation:** ranchu requires universal planes, atomic client support
and guest DRM master. DrmDisplay sets OUT_FENCE_PTR for the CRTC and primary-plane
FB/CRTC/geometry properties; it sets IN_FENCE_FD only when supplied. This CPU
composer calls flush with -1 input fence. DrmAtomicRequest commits synchronously
with ALLOW_MODESET, without NONBLOCK. Returned out-fence is duplicated into the
swapchain image; a shared pointer retains the previous DRM buffer, and destruction
removes framebuffers/closes GEM handles and frees allocations.

K declares MODESET/GEM/ATOMIC and syncobj features, but Kconfig can disable
DRM_VIRTIO_GPU_KMS, masking modesetting/atomic support. DRM atomic UAPI obtains
input sync_file fences and creates output sync_files; atomic helpers wait for
input fences and provide event completion, including fake vblank where applicable.
These are source mechanisms, not installed CONFIG_DRM/CONFIG_DRM_VIRTIO_GPU,
KMS, CONFIG_SYNC_FILE, DMA-BUF, PCI or module-load receipts.

For dumb primary updates, K allocates a virtio fence, queues transfer and resource
flush, notifies QEMU and waits up to 50 ms for the flush fence. Q's synchronous
2D handlers finish processing and echo a requested fence ID in the control response;
K's response handler processes that ID and signals dma_fences. This explains a
source-level command-completion bridge, not a physical display presentation fence
or a complete error/lifetime proof for a future asynchronous host listener.

Two concrete limits prevent declaring safe reuse: K ignores the bounded flush
wait result; G `Image::wait` calls sync_wait for 3000 ms and clears its stored FD,
then returns an error on failure, but GuestFrameComposer ignores that return before
accessing the next buffer. **Inference:** presence of waits does not establish
fail-closed timeout/error handling. **Unknown:** installed correspondence, complete
atomic error paths and end-to-end release/host-surface ownership. No fault was run
and no runtime corruption is claimed. Stop at these missing contracts, not a new
fence implementation.

## Kernel correspondence, QEMU build, rights and TCB

The existing kernel provenance identifies prebuilt kernel commit
`318576752b27af3d328e6deb5e6aa29b08f762c9`, build `15076761`, and the K source
lead; virtual-device module prebuilt commit is
`e6673fcbd05e63e6fcc2c2d2cf33246108b73b0c`. Neither a version string nor that
release snapshot proves the selected virtio_gpu module's source/config/ABI.
The bounded K inspection supplies an authoritative source comparison, **not an
authoritative matching installed configuration**. Missing: resolved build manifest,
module source and patches, toolchain/config fragments/final config, module ABI and
installation/load correspondence, and generated guest selection. No unrelated
emulator or generic Linux driver is substituted as installed proof.

| Distinction | Result |
|---|---|
| Q source capability | Pinned plain device supports eight 32-bit protocol formats, transfer/scanout/flush and response fencing. Resource format remains decisive; source capability is not arbitrary guest format conversion. |
| Build selection | GPU/PCI device closure and pixman source gates must be satisfied together. |
| Existing PDVA recipe/binary claim | Rejected unchanged recipe omits required GPU/PCI selection and disables pixman; no new compiled-device inventory or executable result. |
| Potential differently configured build | Conditional on separate dependency/adoption review, exact generated selection and Android link receipts. No new pixman version or dependency selected. |
| Guest/kernel pairing | Unknown installed graph; conditional RGBA/dumb-resource color mismatch above. |
| Stock Android execution | Not tested; ordinary-app authority, TCG, memory/resource/lifecycle containment and display-adapter obligations remain unresolved. |

Reviewed inventory retains QEMU, GLib, PCRE2, libffi, proxy-libintl, GVDB,
dtc/libfdt, keycodemapdb, softfloat/testfloat and existing build tools under prior
research limits. Guest functionality includes ANGLE, SwiftShader/Pastel and LLVM,
minigbm/libdrm, ranchu/libyuv/libsync/Binder plus kernel DRM/DMA-BUF code. This is
not a complete generated dependency graph. C/G Apache notices, M BSD-style notices,
K GPL/file-specific notices and Q GPL/file-specific obligations remain separate;
no blanket AOSP license or binary redistribution approval is inferred.

Host TCB includes Q device/protocol/pixman parsers, worker containment and any future
bounded pixel owner/presenter; guest services cannot alone protect host identity
after guest or backend compromise. No host authority, runtime dependency, binary,
image, proprietary content, build recipe, native source or file mode changes are
introduced. Existing native assets are retained, not executed or newly adopted.

## Controls, execution, limitations and next proof

Source counterchecks, not executable graphics tests: textproto absent versus present
with missing/true field; malformed textproto must not fall back; plane-format list
versus fixed resource format; same-device versus foreign PRIME import; successful
wait versus ignored wait failure. These independently visible branches prevent a
false positive from names, allocation or advertised formats. No synthetic graphics
capability table or runtime success was produced.

Executed: read-only preflight, source fetch/decode/hash and source review, prior
verification of 36 prior file-byte receipts, existing local repository validators. Local validation
results are recorded below after execution. **Not tested:** guest/kernel build,
QEMU rebuild/execution, Android/emulator/phone, color output, scanout/fence runtime,
host graphics adapter, Persona implementation/enforcement or privacy/isolation.
No broad repeated search, full guest construction or alternate renderer was used.

Smallest new independent receipt: the exact product/release/variant's packaged
guest-config textproto (or proven absence plus android-info), emitted bootconfig
and installed module selection, paired with the authoritative matching
virtio_gpu source/build/config/module manifest. It must resolve actual resource
format and atomic/fence behavior, including failure/reuse; another version string
or screenshot cannot do so. If it confirms the RGBA/non-blob fixed-XRGB subcase,
retain STOP. A different configuration needs explicit scope and source proof before
any separately authorized build. Do not continue searches without new correspondence
evidence. Gate 0 and all other boot, source/toolchain, authority and lifetime blockers
are unchanged.

The same PR clarifies existing Persona policy and future acceptance only, with
official Android API citations and explicit Unknown/Not tested labels. It adds
no spoofing feature, host identifier disclosure or architecture decision.

## Local validation and publication receipt

Using the existing NDK-bundled Python 3.11.4, without installation:

- Foundation passed: 130 files, 79 Markdown files, 54 requirements, two ADRs;
  local Markdown targets, numbering, historical notices and hygiene included.
- Harness source/manifest authority validation passed; no APK execution.
- Repository regression: 141 tests, 137 passed, four existing Windows skips.
- Desktop-readiness controls: 27 passed; offline-image controls: 45 passed.
- All 36 prior source-byte receipts matched; 17 fetched file receipts below were
  hashed from decoded source bytes. This validates provenance, not capability.
- Complete four-file diff, links, Markdown table structure, whitespace, privacy,
  regular 100644 file modes and unchanged dependencies/requirements/ADRs reviewed.

Linux-only native runtime controls were not executed locally. Existing skips
remain skips. Foundation/tool controls establish repository structure and tool
behavior, not graphics, Persona enforcement, isolation or any gate pass.

Publish exactly one combined evidence PR, attach it natively and verify identity,
head/base and association once. New hosted CI remains pending/unobserved until
Tony requests independent review; do not poll checks/reviews or merge.

## Additional immutable source-byte receipts

Retrieve each Gitiles link with `?format=TEXT`, decode base64 without newline
conversion, then SHA-256 the bytes. Reused graphics receipts remain in the prior
ledger; all 36 matched locally. K is the source lead only, as qualified above.

| Immutable file | SHA-256 |
|---|---|
| [device/google/cuttlefish: host/commands/assemble_cvd/flags.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags.h) | `72fb96a73d18578287a4baa4aae8b7c933cdbf7e5f4f6e10c64fb992b9b90c68` |
| [device/google/cuttlefish: host/commands/assemble_cvd/flags.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags.cc) | `52ba2555c01639b68dfc348fce73124e4b7afa35d82a93e0b1a58c6c59254de9` |
| [device/google/cuttlefish: shared/phone/android-info.txt](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/android-info.txt) | `78bd68a29bf4f56599ad4b17540996c504ce1ef99aa9c1c0f128882d95607aa8` |
| [device/google/cuttlefish: vsoc_arm64/phone/aosp_cf.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/phone/aosp_cf.mk) | `ba74bdb141f2346a53b516fecb9cda9337c903185cdf7b4603b25a7293c77579` |
| [device/google/cuttlefish: shared/phone/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk) | `69645517941d7013eb798376faeee588cc86f9bfd117dd5eecd27b250b6ad176` |
| [kernel/common: drivers/gpu/drm/virtio/virtgpu_plane.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/virtgpu_plane.c) | `ecb42308522985535f5814b97f87d4dbbb372f9a8350dead5cef14b19bb2bfdd` |
| [kernel/common: drivers/gpu/drm/virtio/virtgpu_display.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/virtgpu_display.c) | `db53dedc7d9b1375a8411f9929b722ba355e844433b5272ea20ce7423d958cd6` |
| [kernel/common: drivers/gpu/drm/virtio/virtgpu_gem.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/virtgpu_gem.c) | `8dde9970960c286cc259f5452fc8c21c140708a879c0f7d48efc93070a58a432` |
| [kernel/common: drivers/gpu/drm/virtio/virtgpu_prime.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/virtgpu_prime.c) | `c6c137fb93d93530b32c9a8dafd51071628029ab63679f9ddbd758a50f194450` |
| [kernel/common: drivers/gpu/drm/virtio/virtgpu_drv.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/virtgpu_drv.c) | `4f3402a82bbb434ca174599810e89378db2a3672492c330cedfb49550a34b0b3` |
| [kernel/common: drivers/gpu/drm/virtio/Kconfig](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/Kconfig) | `f56dcb16709a587e6f549e5e811e8b2a8c2323c6ac26bdd407ac436449d592e7` |
| [kernel/common: drivers/gpu/drm/drm_atomic_uapi.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/drm_atomic_uapi.c) | `79333df7629f2671dcf1c4312b7384ef962a3d4d788482a11520212a304076ae` |
| [platform/external/minigbm: drv_helpers.c](https://android.googlesource.com/platform/external/minigbm/+/ce79bbee67b3e2ea7abb110e1415e9ceceaa6471/drv_helpers.c) | `72bac2bdefc51034425303ff781dd773190db9416c72756594fa2db2ddc8d86d` |
| [platform/external/minigbm: cros_gralloc/cros_gralloc_helpers.cc](https://android.googlesource.com/platform/external/minigbm/+/ce79bbee67b3e2ea7abb110e1415e9ceceaa6471/cros_gralloc/cros_gralloc_helpers.cc) | `2906c8a076cd24854c4d7be8f88b1345d2f85d3f675cbfe2066fb31749cd3632` |
| [kernel/common: drivers/gpu/drm/virtio/virtgpu_vq.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/virtgpu_vq.c) | `ae7c9bab76af9672414dc7fe001259a0cfbc617dc2888445c504c4f96b994be8` |
| [kernel/common: drivers/gpu/drm/virtio/virtgpu_fence.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/virtio/virtgpu_fence.c) | `83199ad3f23fab434eba62d6cc821939fac4d3967f4ebe7f6b4f0fe73da62fb3` |
| [kernel/common: drivers/gpu/drm/drm_atomic_helper.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/gpu/drm/drm_atomic_helper.c) | `b7f4bf0ada9742062dbd2087987a9a481378ee888a97cc739420578b3abdd1c4` |
