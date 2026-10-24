# Gate 0: Android 17 software graphics and virtual display contract

Review: **2026-10-24, America/Fortaleza; Windows x86_64 desktop; source only.**
**Gate 0 Unresolved; Gates A-G Not reached.** ADR-0001 remains Accepted;
ADR-0002 remains Proposed. QEMU/TCG remains a hypothesis, not an adopted engine.
Scope: PDVA-REQ-001 through PDVA-REQ-015, PDVA-REQ-034 through PDVA-REQ-045,
PDVA-REQ-047, PDVA-REQ-048 and PDVA-REQ-054.

## Disposition and exact candidate

**Overall compatibility: UNKNOWN. STOP the unchanged existing PDVA build pairing:
it does not select the required virtual GPU.** This is a build-contract negative,
not a universal impossibility of software-rendered Android.

The candidate examined is the Android 17 `aosp_cf_arm64_phone` reference product,
explicit `gpu_mode=guest_swiftshader`, QEMU VMM, `hwcomposer=auto`, GPU vhost-user
`auto`, with no custom property overrides; guest ANGLE/Pastel, minigbm and the
resolved **ranchu GuestFrameComposer**, paired with QEMU ARM virt/TCG and plain
`virtio-gpu-pci` (2D, blob off, no GL renderer). A bounded CPU-pixel listener is
only a proposed output mechanism, not an existing PDVA adapter or an alternate
renderer. The reference launcher itself still uses VNC and other forbidden or
unclosed host services; it is not the proposed ordinary-app launcher.

Three new distinctions prevent a false positive or false negative:

1. `hwcomposer=auto` resolves to **ranchu** for this branch. Selecting
   drm_hwcomposer merely because its APEX is packaged would combine different
   configurations. Ranchu selects GuestFrameComposer when `ro.hardware.vulkan`
   is `pastel`, unless explicit noop/client composition overrides take precedence.
2. Minigbm's backend named `virtgpu_virgl` has a genuine **non-3D dumb-buffer
   path**. Its name does not imply a mandatory Virgl renderer/capset. Missing
   cross-domain/blob/context features causes fallback, not automatic failure.
3. Successful allocation is not successful scanout: this 2D allocator strips
   `BO_USE_SCANOUT` for non-XRGB8888 formats; ranchu still imports the resulting
   handle with `drmModeAddFB2` and commits a primary plane. Generated framebuffer
   selection and the exact guest kernel's accepted formats/fences are therefore
   necessary evidence. They have not been closed here.

The first decisive falsifier for the **unchanged PDVA recipe** is earlier:
its all-no-defaults ARM-virt device selection produces neither `VIRTIO_GPU` nor
`VIRTIO_PCI`, and its disabled pixman dependency independently excludes the
plain GPU implementation and PCI wrapper source sets. Stop that pairing; do not
infer that enabling pixman alone repairs it. For a differently configured build
of the same pinned 2D device, the guest kernel/generated graphics graph and actual
link receipt remain UNKNOWN. No replacement build or experiment was attempted.

## Baseline, preservation and method

GitHub commit metadata and `git ls-remote` independently returned main
`05a8a3373ca87c7660ced1c17e5446426ececccf`. [PR #35](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/35)
merged at that SHA, on `2026-10-24T07:11:41Z`, head
`bec2486a604ad514cdaf3d9f7c105a2218cf53eb`. Both connector search and the complete
open-PR REST inventory returned zero. There were consequently no open heads,
bases, files/diffs, checks/jobs/logs, reviews, comments or review threads to inspect
and no intended existing PR to duplicate.

[Exact-main run 40073173100](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40073173100)
completed successfully: foundation `120810815331`, offline-image-windows
`120810815530`. Job steps and execution-log checkout/validation receipts were
inspected; both logs identify the exact main SHA. GitHub Status reported All
Systems Operational. Foundation applies to this documentation change; Android
and QEMU workflows are path-filtered out, not additional passes. An initial
connector workflow query returned an empty result; direct REST with `head_sha`
resolved the run and is the evidence used here.

Requirements, governance, both ADRs, gates, evidence criteria, provenance policy,
index, complete-Android and boot/HAL records and ledgers, integration/cross-build,
VMM, TCG, harness, containment and memory-limiter evidence were reviewed. Their
boot, lifetime, resource, source/toolchain and host-authority gaps are preserved.
History, branches, worktree, stashes, ignored assets, dependencies and modes were
inspected. Initial tracked state was clean, one worktree, no stashes; all 128
tracked entries were regular `100644`. Prior branch and ignored tool/build/source
assets were preserved; prior head and fetched merge had identical trees. No
applicable AGENTS.md was found. Historical repository remained untouched.

Only this document and the index are intended for publication. Local public-source
receipts are convenience research copies, not independently verified durable
backup. Existing private evidence was neither republished nor re-attested; no
owner-controlled independent backup was established in this task. Git preserves
the public disposition after successful publication, not private ignored assets.
Failure to publish would leave this result **UNPRESERVED pending recovery**.

Procedure: independently resolve Android release commit JSON; fetch selected
immutable files through Gitiles `?format=TEXT`; decode base64 without newline
normalization and hash source bytes. QEMU's clean retained checkout and upstream
commit API agree on commit/tree; raw `git show` supplies source-byte receipts.
Trace actual predicates, module definitions and command handlers. Run only the
existing pinned `scripts/minikconf.py` source-selection control and repository
validators. No capability table was turned into a synthetic passing test.

Initial sandbox Git network access failed; authorized escalation succeeded.
Existing NDK Python lacks HTTPS support, so curl retrieved public source and
Python decoded/hashed it. Guessed `graphics_flags.cpp`, `virtio_gpu.c`, graphics
APEX/build paths and old goldfish-opengl/graphics-common release paths returned
404; directory/manifest discovery located `graphics_flags.cc`, `virtgpu.c` and
`device/generic/goldfish/hals/hwc3`. These failures are not evidence of absence.

## Source identities and selected graph

All seven supplied Android project pins were independently re-resolved from
`refs/tags/android-17.0.0_r1` and match the prior ledgers:

| Project | Immutable revision |
|---|---|
| frameworks/base | `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` |
| frameworks/native | `ae266dcb706d083868578cfedce381ef44488a07` |
| device/google/cuttlefish (C) | `283645aacf6cdb56cc31a9362f54d412dbc132a1` |
| external/angle (A) | `1f4500d3906c24de59eec5b9cda17a2ad2a8ba2d` |
| external/swiftshader (S) | `9a22bb9de00f5d8ddf4fc5ba5c2f425c2816e679` |
| external/minigbm (M) | `ce79bbee67b3e2ea7abb110e1415e9ceceaa6471` |
| external/drm_hwcomposer (D; alternative, not selected composer) | `87daba89b05fabc7f1e9316e3f283f19fd0c45cd` |
| device/generic/goldfish (G; newly resolved ranchu provider) | `296e55aa0244e8929e393e00e34471fef2a5d662` |
| QEMU (Q) | `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`; tree `0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de` |

These are reference identities, not adoption, a generated build manifest or
redistributable binary provenance. Sources below identify exact symbols/files;
prior [source ledger](gate-0-complete-android-sources.md) retains framework,
product and license receipts without duplication.

**Selection (source observation).** C `graphics_flags.cc` gives GuestSwiftshader
an empty host-graphics requirement list; explicit mode avoids host-dependent auto
ranking. `SelectGpuVhostUserMode` returns false for GuestSwiftshader with auto.
C `flags.cc` resolves composer auto to ranchu, and `bootconfig_args.cpp` selects
`com.android.hardware.graphics.composer.ranchu` for the composer APEX. This is
stronger evidence than listing both installed composer packages. C QEMU manager
sets EGL `angle`, Vulkan `pastel`, gralloc `minigbm`, DRM display finder, GLES
version 196609 and CPU Vulkan version 1.2. Guest graphics early-init copies boot
values into the corresponding `ro.hardware.*`/`ro.vendor.hwcomposer.*` properties.

**Product/build (source observation with unresolved generated closure).** The
ARM64 phone inherits shared phone graphics and SwiftShader definitions. Shared
device defaults `TARGET_VULKAN_SUPPORT ?= true`; under true, graphics adds
`com.google.cf.vulkan` and SwiftShader sets `cvd.use_vulkan_pastel=true` plus
`PRODUCT_REQUIRES_INSECURE_EXECMEM_FOR_SWIFTSHADER=true`. The Vulkan APEX conditionally
includes `vulkan.pastel` (and also packages `vulkan.ranchu`, which does not select
it at runtime). S `src/Android.bp` defines `vulkan.pastel` using
`libswiftshadervk_llvm`/`libLLVM16_swiftshader`; Android AHardwareBuffer integration
is separate from host WSI compilation. A `Android.bp` defines the ANGLE EGL/GLES
modules and Vulkan backend. No generated installed-files/link graph establishing
all ANGLE modules, release flags or transitive targets for a chosen lunch/release/
user variant was produced. Property selection alone is not that graph.

C graphics packages `com.google.cf.gralloc`, the minigbm allocator service and
`mapper.minigbm`. Its gralloc APEX overrides the standalone allocator; placement
of mapper/linker/VINTF content inside that APEX depends on
`RELEASE_SM_OPEN_DECLARED_PASSTHROUGH_HAL`. Its exact generated value and resulting
installed VINTF/linker graph remain missing. G defines the ranchu composer3 V5
service, APEX, generated init path, and guest system/graphics/drmrpc execution
identity. Its SYS_NICE capability is **inside the guest**, not host app authority.
D's packaged drm_hwcomposer and `vendor.hwc.drm.device=/dev/dri/card0` settings
must not be substituted for ranchu's actual discovery/commit behavior.

**Guest compositor (source observation).** G `Device::getComposer` checks noop,
then client, then `pastel` for GuestFrameComposer, otherwise HostFrameComposer.
The inspected GuestSwiftshader boot branch does not request noop/client. Guest
composition uses libyuv/CPU operations, gralloc mappings and DrmClient; no host
render-control peer is called in that selected path. The service binary still
links shared graphics transport code and includes other composers; absence of an
active host renderer is not absence of that code or a complete transitive audit.
SurfaceFlinger/RenderEngine, app rendering, ANGLE, Pastel, allocator, composer,
libdrm and DMA-BUF handles here execute within the guest. QEMU device emulation,
pixman, memfd surfaces and a future listener execute in the isolated host worker.
Reference launch/configuration and VNC execute on the external reference host.

**First unresolved guest/device contract.** DrmClient opens guest DRM cards,
requires universal planes, atomic modesetting and DRM master, imports PRIME FDs,
uses per-plane stride/offset metadata with `drmModeAddFB2` (flags zero), and issues
atomic primary-plane commits. DrmDisplay requests a CRTC out-fence; in-fence is
added when supplied. GuestFrameComposer flushes its CPU-composed target with -1
input fence; swapchain reuse waits on the previous out-fence. Required kernel
facilities include virtio PCI/GPU DRM, KMS/atomic/primary-plane support, GEM dumb
buffers and mapping, PRIME/DMA-BUF export/import, sync_file/fence handling and
proper guest device permissions. These guest nodes do not authorize host nodes.

Framebuffer selection is not safely inferred from the word SwiftShader. C's
legacy android-info parser tests `supports_bgra_framebuffers=true`; the retrieved
phone text lacks that key, so that input path selects RGBA. A separate proto
path supplies `graphics.bgra_framebuffers_supported`. QEMU manager emits bgra or
rgba accordingly; G `GetHostDisplayPixelFormat` maps these to BGRA_8888 or
RGBA_8888. Its comment explains a historical guest-kernel RGBA patch, which is
an upstream explanation, not proof that the selected module contains it.
M's 2D path permits allocations of more formats than primary scanout and removes
scanout usage for non-XRGB8888. Thus an allocated RGBA/ABGR8888 buffer does **not**
prove that `AddFB2`/plane commit accepts it. Exact generated guest config, selected
kernel/module source/config and format/fence correspondence are missing. The
prior kernel prebuilt/version lead does not close them. No unproved kernel
identity or replacement BGRA configuration is silently selected here.

## Interface and first-falsifier matrix

S = observed source; I = inference; U = unknown. Status applies only to the stated
interface, never boot/usability/security. File IDs resolve in the ledger below.

| Guest-selected component | Required interface / QEMU provider | Build-selection status and result | First independent falsifier | Rights / TCB |
|---|---|---|---|---|
| ANGLE + Pastel | Guest Vulkan/AHardwareBuffer and CPU JIT; QEMU TCG supplies guest CPU, not host Vulkan | S: properties and module definitions; U: generated package/link closure | Missing ANGLE/Pastel target or APEX/linker visibility despite properties | Guest LLVM/SPIR-V/ANGLE dependency closure; host TCG remains hostile-input code |
| Ranchu GuestFrameComposer | Guest CPU composition plus DRM/KMS; Q plain GPU below guest driver | S: auto/APEX/pastel predicates resolved; conditional on generated init/properties | noop/client/HostFrameComposer activated instead, or unavailable mandatory peer | G Apache-style source plus libyuv, Binder, libui, libdrm, libsync and linked transport closure |
| Minigbm allocator/mapper | GETPARAM; cross-domain probe then non-3D fallback; Q plain GPU has no Virgl/cross-domain capsets | **Conditional source match** for 2D, not an obligatory capset mismatch (M1-M3, Q3) | Kernel reports incompatible params, allocator/mapper missing, or required usage cannot resolve | BSD-style minigbm/libdrm and guest handles; no host GBM service inferred |
| Composer target format/stride | PRIME import + AddFB2 + primary plane; Q maps eight 32-bit virtio formats (Q4) | **UNKNOWN** across actual guest kernel; M strips scanout for non-XRGB | Selected target format/modifier rejected by guest kernel even though allocation succeeds | Guest DRM/module provenance; Q dimensions/format/stride/offset parsers |
| Fences and ownership | G atomic out-fence/reuse; Q control response echoes fence ID after CPU commands | **UNKNOWN** kernel translation and complete release semantics; host presentation not implied | Missing OUT_FENCE_PTR/sync support, early reuse, or stale async surface pointer | Guest sync_file and host resource references/queues; no escape proof |
| Required virtio-gpu-pci | Q `virtio-gpu-base.c`, `virtio-gpu.c`, PCI wrapper and pixman | **INCOMPATIBLE with unchanged PDVA recipe**: device closure omits GPU/PCI transport; pixman disabled | Reproduced real Kconfig closure and Meson dependency conditions | Adding pixman would require separate exact pin/license/Android link review; not added |
| CPU-readable output | Q transfer -> pixman image -> scanout surface -> display listener | S: source exists; **conditional**, absent qualified build/adapter | Unsupported format/stride, invalidated ownership or missing listener; VNC is not delegated output | Q GPL/file-specific plus prospective bounded adapter/presenter TCB |
| Resize/cursor/release | Q surface switch/update, cursor callbacks, detach/unref/reset | S: device lifecycle exists; U: guest resize and host adapter semantics | Surface freed while queued, omitted cursor, stale display epoch, missing full redraw | Resource IDs, lifetimes, dirty rectangles and message sizes need independent validation |

### QEMU source versus configured/build evidence

Q plain GPU exposes 2D resource creation/backing attach/detach, transfer, scanout,
flush, unref and a cursor queue. Virgl is advertised only for the corresponding
renderer-enabled flags; blob defaults false, hostmem defaults zero. EDID and other
feature bits depend on base configuration. The simple command dispatcher does
not implement accelerated context/capset operations. Minigbm cross-domain init
requires context-init, cross-domain capset, blob and suitable memory support;
it returns ENOTSUP without them and the backend loop tries `virtgpu_virgl`.
That backend skips capset loading when 3D is absent and uses dumb creation/map.
A capset requirement from gfxstream or cross-domain cannot be borrowed into this
software branch. Nor can those accelerated features be borrowed into plain QEMU.

The repository recipe at the verified baseline writes only `CONFIG_ARM_VIRT=y`,
uses `--without-default-devices`, `--without-default-features`, `--disable-pixman`
and disables OpenGL. Running Q's existing minikconf with the recipe's exact
**declared** external symbols reproduced 41 selected symbols, including VIRTIO
and VIRTIO_MMIO but not VIRTIO_GPU or VIRTIO_PCI. This control is not Meson's
complete detected configuration or a link inventory. Independently, Q's Meson
GPU and PCI-wrapper source sets require pixman; root Meson leaves that dependency
not-found when disabled. `pixman-minimal.h` cannot satisfy those source-set gates.
The prior successful executable receipt therefore supplies no graphical-device
success. No new binary inspection or compilation was performed.

Evidence levels: **A** source exists, **B** a pixman-enabled/device-selected
configuration is expressible in source, **C** required feature is absent from the
unchanged recipe's selection, **D** whole guest/kernel/device matching remains U.
**E** stock-Android execution and **F** hostile-input safety are wholly unverified.
B is not permission to change the recipe or adopt a dependency.

## Potential software-only output, not an adapter implementation

In the non-blob path, Q allocates a pixman image, attaches guest-memory IOV backing,
copies `TRANSFER_TO_HOST_2D` data into the image using its computed row stride,
and wraps a scanout rectangle in a referenced pixman image/DisplaySurface.
`RESOURCE_FLUSH` intersects dirty rectangles with active scanouts and calls
`qemu_console_update`; display listeners receive `dpy_gfx_update`.
`qemu_console_set_surface` invokes `dpy_gfx_switch` and then frees the old surface.
Resize, disable, unref and reset therefore require lifecycle handling, not a
permanent cached pointer. Cursor updates are a separate callback path.

The prospective flow is:

```text
guest app / SurfaceFlinger / ANGLE / Pastel
  -> minigbm + ranchu CPU composition
  -> guest DRM/KMS virtio_gpu + guest memory backing
  -> QEMU 2D copy / pixman scanout surface (isolated worker)
  -> missing bounded CPU snapshot listener / typed instance transport
  -> ordinary PDVA app window presenter
```

This path has no intrinsic host EGL/Vulkan renderer, GPU node, KVM, hostwide screen
ownership or external display-server requirement. Q's POSIX shareable-image
allocator calls `qemu_memfd_alloc`; upstream fallback behavior and PDVA's strict
Android memfd adaptation remain subject to the existing
[TCG record](gate-0-tcg-executable-memory.md). Source allocation is not observed
isolated-process authority or a total memory quota. Blob/udmabuf and GL imports
are not shortcuts adopted here. The reference VNC/QMP endpoints are not approved
output/control interfaces and no listener endpoint was opened.

A future internal listener must copy while QEMU owns stable surface data or retain
appropriate image references and synchronize in QEMU's execution context; a raw
surface pointer cannot safely outlive switch/unref. Reference counting alone does
not prevent concurrent mutation. It must normalize/validate dimensions, format,
byte order, alpha, row stride, crop/dirty rectangles and overflow-checked extent;
bound frame count, total bytes, queue pressure and rate; handle cursor/resize/full
redraw; and reject stale instance/epoch messages. The trusted receiver must snapshot
or otherwise prevent a hostile worker changing shared metadata during validation.

QEMU's device fence completion is not an Android host Surface presentation fence.
Copy completion could delimit safe pixel-buffer reuse, but guest atomic out-fence
translation and host presentation timing need separate proof. Source-level memory
and callback mechanisms do not prove a working launcher, frame pacing, text input,
rotation or latency. Management would receive bounded pixels through its own UI;
it is not proposed as a host for an untrusted GPU renderer. Any material expansion
of management authority/TCB requires later ADR and Tony approval.

## Negative controls and scope of rejection

These are manual checks against real source/contracts, not executed guest tests.

| Invalid claim | Actual counterevidence / disposition |
|---|---|
| 1. GPU exists, so any capset works | Q simple feature/command dispatch excludes accelerated contexts; M cross-domain rejects missing prerequisites. M's real 2D fallback prevents wrongly rejecting this software branch merely for no Virgl. |
| 2. Allocation proves compositor-compatible format/modifier | M removes scanout usage for non-XRGB; G AddFB2 and atomic plane commit remain separate. Generated RGBA/BGRA plus kernel format list missing: UNKNOWN, not pass. |
| 3. CPU pixels prove synchronization/ownership | G waits swapchain fences; Q frees old surfaces after switch and only reports device completion. An asynchronous raw-pointer copy or host-present-fence equivalence is unsupported. |
| 4. Software rendering guarantees no host peer | G pastel branch selects GuestFrameComposer; C auto disables GPU vhost-user. HostSwiftshader/gfxstream is a different branch. Reference VNC and unrelated host services remain; no whole-launcher closure inferred. |
| 5. Existing no-pixman executable proves GPU support | Actual allnoconfig control lacks GPU/PCI transport; Meson requires pixman. STOP unchanged recipe pairing. |
| 6. Mouse/keyboard proves full touch/text | Existing QEMU input and Android EventHub evidence distinguishes mouse/key events from multitouch association and IME composition. No new input implementation/test; reject claim. |
| 7. Synthetic frame proves SurfaceFlinger output | Current harness produces only two synthetic 64x64 frames. G even disables presenting after a failed initial flush; surviving service/headless boot is not visible Android. |
| 8. Upstream demo proves ordinary stock-app authority | Guest DRM-master/system permissions are inside guest; external reference launcher authority is not isolated Android authority. No phone execution or rights/containment inference. |

## Rights, dependencies and attack surface

No production dependency, binary or upstream implementation is imported. Source
licenses are obligations, not a legal conclusion or adoption approval. C/G source
headers are Apache-2.0 style; G composer also links libyuv, libdrm, libsync, libui,
Binder and graphics transport code. ANGLE has BSD-style project terms with
Vulkan/SPIR-V and other third-party dependencies. S declares Apache/BSD/MIT/NCSA
and other scoped notices; its selected LLVM16, Reactor, SPIR-V tools, ASTC and
Marl closure requires exact corresponding-source, tools and per-file notice review.
Minigbm is BSD-style with libdrm/native dependencies. D is a separately packaged
alternative, with its prior Apache/MIT-exception review retained. None is covered
by assuming a permissive root notice licenses all transitive files.

Q's GPU files carry GPL-2.0-or-later notices within QEMU's mixed/file-specific
closure. Pixman is an additional prospective host dependency, not selected/pinned
or rights-audited here; no version or binary is silently introduced. Existing
GLib, PCRE2, libffi, proxy-libintl, GVDB, dtc/libfdt and build-source obligations
remain in the [integration record](gate-0-qemu-worker-integration.md) and
[cross-build record](gate-0-qemu-android-linux-crossbuild.md). Exact guest kernel,
module, generated APEX/VINTF, linker, LLVM and complete transitive license/build
closure remain missing. No GMS or proprietary graphics binary was acquired.

Treat guest, renderer, QEMU and worker native code as hostile. Prospective host
attack surface includes virtqueue commands, descriptor/IOV lengths and guest
addresses, resource IDs, dimensions, formats/stride/offsets, fence IDs, allocation
sizes, mutable shared memory, cursor data, scanout replacement, detach/unref/reset,
callbacks and queued frame lifetimes. The adapter/receiver would add parsers and
presentation/lifetime authority; host kernel/framework and enforcement remain in
the TCB. QEMU's per-resource checks/default hostmem limit are not proven whole-worker
quotas or escape resistance. Existing containment, revocation, memory-limiter and
manager-loss unknowns remain unchanged.

## Smallest genuinely new next proof and stop boundary

Do not rebuild the failed unchanged pairing. The next useful **source/configuration
receipt** is a single coherent ARM64 product/release/variant graphics selection:
resolved TARGET_VULKAN_SUPPORT, mapper release flag, installed ANGLE/Pastel/composer
APEX modules and generated init/VINTF/linker data; actual guest-config proto or
android-info and emitted framebuffer bootconfig; matching virtio_gpu module source,
kernel config and accepted primary-plane formats/atomic fence support. Trace that
exact target through minigbm resolution, PRIME/AddFB2 and atomic commit to Q's 2D
format/transfer protocol. This can answer the current format/fence UNKNOWN before
any full guest construction.

Only after that and separate authorization would a new pixman/device-selected
Android QEMU build need an exact dependency/license pin, generated device config,
linked-object/ELF receipt and preserved strict worker/memfd constraints. Even a
positive source/build match would still require separately reviewed adapter,
authority, resource and runtime evidence. No such build, adapter, guest, emulator
workload, phone test, diagnostic modification, host permission change, network
change, Persona implementation or Gate A work occurred or is authorized here.

The full interactive Android hypothesis is **constrained, not globally falsified**.
This record establishes no usable phone, acceptable performance, isolation,
redistribution approval, certification or production readiness.

## Validation and publication boundary

Local validation used the existing Python 3.12.14, without installation:

- Foundation PASS: 129 files, 78 Markdown files, 54 requirements, two ADRs;
  local Markdown targets and repository hygiene included.
- Harness source/manifest authority validator PASS; no APK or Android execution.
- Repository regression: 141 total, 137 passed, four existing Windows skips.
  Skips are platform-specific controls, not passes.
- Desktop-readiness/journal controls: 27 passed; offline-image synthetic controls:
  45 passed. These validate existing repository tools, not guest graphics.
- Real pinned Kconfig selection control: 41 symbols, GPU/PCI transport absent.
  No configure, compilation, linking or device execution.
- All 36 published source-byte receipts independently recomputed and matched;
  supplied release pins and added goldfish pin reconciled.
- Complete two-file diff, whitespace, links, regular 100644 modes, source attribution,
  dependency/binary inventory and public-data hygiene reviewed.

NOT RUN: new QEMU build/link or ELF inspection, full Android build, graphics
adapter, Linux native controls locally, guest/renderer workload, SurfaceFlinger
output, touch/IME tests, physical-device/security/performance/resource tests.
No synthetic capability oracle was added. Baseline hosted results apply only to
old main; local documentation checks do not validate graphics compatibility.

After publishing exactly one focused PR, check its identity/head/base once, attach
it natively to the current chat and verify that association once, then stop.
New hosted CI is **pending/unobserved**; no post-publication CI/review polling or
merge is part of this task. Tony will obtain independent review before any merge.

## Immutable file references and byte receipts

The following selected decisive receipts use raw decoded source bytes. Product
and framework references are also retained in the prior source ledger linked
above. Reproduce Android receipts
with `curl -fLsS 'IMMUTABLE_URL?format=TEXT'`, base64 decode and SHA-256; Q receipts
with `git show Q_SHA:path` and SHA-256 (avoid text-mode newline conversion).
No source archive, tool installation or runtime execution is required.

| ID | Immutable source | SHA-256 |
|---|---|---|
| C1 | [cf: graphics_flags.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/graphics_flags.cc) | `90110f60b41133498df69bf943805c3dd2fc62cea3c914f215dafacd705b2846` |
| C2 | [cf: flags.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags.cc) | `52ba2555c01639b68dfc348fce73124e4b7afa35d82a93e0b1a58c6c59254de9` |
| C3 | [cf: bootconfig_args.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/bootconfig_args.cpp) | `64a5a2be99fa76080a16c45ba38831c264472ff3d882aa4bb9d79eb687d62117` |
| C4 | [cf: qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` |
| C5 | [cf: device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/graphics/device_vendor.mk) | `aaca0033829b1c239e894146d91cf10d37c832915ce1f040a11be514945e8fe8` |
| C6 | [cf: device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/swiftshader/device_vendor.mk) | `1710b075bc15363715d650eebf76225dc5851c0bae4966abebe6acd140e9eabc` |
| C7 | [cf: init_graphics.vendor.rc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/graphics/init_graphics.vendor.rc) | `cf45c91516ac2c5ef54feb5853bbdf9c9acdacef99d69b9eadff9f9b23eedae5` |
| C8 | [cf: Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/gralloc/Android.bp) | `14f8804ec74c7b21e4ae53cb6aecdba6eb88c3fd51c10a60f5ed20603f621874` |
| C9 | [cf: Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/vulkan/Android.bp) | `47c9045fb066a0cbdb219fb51991ee1dee0c659099a5da134dc6d88c79bb5369` |
| C10 | [cf: android-info.txt](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/android-info.txt) | `78bd68a29bf4f56599ad4b17540996c504ce1ef99aa9c1c0f128882d95607aa8` |
| G1 | [gold: Device.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/Device.cpp) | `32e06640c34d028c1bfe9b0e0c24aae03bf48ce00fbabdaed912f7fa2d4a9dbb` |
| G2 | [gold: GuestFrameComposer.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/GuestFrameComposer.cpp) | `56dd44c3c7b033edaa70f5c08361c6b6bacce1164f97cfe9f0e5e657080b2639` |
| G3 | [gold: DrmClient.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/DrmClient.cpp) | `ec344e434c9045da3f22c898c293989dc514405da1799fa7ee0317586fc65c70` |
| G4 | [gold: Common.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/Common.cpp) | `9bfd3d5b2fe31c6d61f2be291aab80eb6a5c4389ab3b2790e710afc87576e56f` |
| G5 | [gold: DrmDisplay.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/DrmDisplay.cpp) | `9d632c5c0217e8139ccf5453063fd41ecfa82536cd629ea6ccf648a1c1594e73` |
| G6 | [gold: DrmSwapchain.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/DrmSwapchain.cpp) | `16a57822c4417759cf964bdd2e3ad8b6a3f2eee855123ed57b5bf3ae452c1855` |
| G7 | [gold: DrmAtomicRequest.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/DrmAtomicRequest.cpp) | `f87ea35d47bdc2ea41f714148321fe782708ed03389ea1ae5bbb794e6bfd0753` |
| G8 | [gold: Android.bp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/hwc3/Android.bp) | `dd8102d85bfcf3898707a94f2d750e336339e5d4ec63fd75d3d5571e1d62c1cd` |
| M1 | [mini: virtgpu.c](https://android.googlesource.com/platform/external/minigbm/+/ce79bbee67b3e2ea7abb110e1415e9ceceaa6471/virtgpu.c) | `7361c5127f257d7d500f15d5f76d5165ae409a674fc26fde4ff0d7d0dcd66979` |
| M2 | [mini: virtgpu_cross_domain.c](https://android.googlesource.com/platform/external/minigbm/+/ce79bbee67b3e2ea7abb110e1415e9ceceaa6471/virtgpu_cross_domain.c) | `9574970430510226ec3731448044283ce3da7c8c11908bc9b5d4d2788ea98594` |
| M3 | [mini: virtgpu_virgl.c](https://android.googlesource.com/platform/external/minigbm/+/ce79bbee67b3e2ea7abb110e1415e9ceceaa6471/virtgpu_virgl.c) | `fe1f8b118858c4489047cd3b7f055e7d051705827c9b401d24b432b56c8fe594` |
| M4 | [mini: cros_gralloc_driver.cc](https://android.googlesource.com/platform/external/minigbm/+/ce79bbee67b3e2ea7abb110e1415e9ceceaa6471/cros_gralloc/cros_gralloc_driver.cc) | `98e9054d5f98c3d107c25be6ac240c0b4bb858717860657641479595d3ec3103` |
| A1 | [angle: Android.bp](https://android.googlesource.com/platform/external/angle/+/1f4500d3906c24de59eec5b9cda17a2ad2a8ba2d/Android.bp) | `193db8af085f83b1788b0e7d69d26a0ed23a97f2c2c6cd7c695e46184f8cadf2` |
| S1 | [swift: Android.bp](https://android.googlesource.com/platform/external/swiftshader/+/9a22bb9de00f5d8ddf4fc5ba5c2f425c2816e679/src/Android.bp) | `9e9bb27ab39199e794b294815ae83d0fcdb1badb05548ceae2353f09fa9eed0e` |
| S2 | [swift: Android.bp](https://android.googlesource.com/platform/external/swiftshader/+/9a22bb9de00f5d8ddf4fc5ba5c2f425c2816e679/Android.bp) | `6413c986f1be8a05d32b4834ec59ecbe3cd53ca10d102993909e502daa5c15c6` |
| D1 | [drm: Android.bp](https://android.googlesource.com/platform/external/drm_hwcomposer/+/87daba89b05fabc7f1e9316e3f283f19fd0c45cd/Android.bp) | `35c3d950a5f66b4ced0cd05c95ef60557bdb032e844eb7ffb761372d9cce1e60` |
| Q1 | [Q: hw/display/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/display/meson.build) | `36fb16a74d50369756313baaecee09b687139effa5bfa3aed03e2e61025e6abd` |
| Q2 | [Q: hw/display/Kconfig](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/display/Kconfig) | `e76462a4178c640b9dc6cb56b90f7364014ede7e80963303db930da534c966c3` |
| Q3 | [Q: hw/display/virtio-gpu-base.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/display/virtio-gpu-base.c) | `3e473f8e28da6a9fdd63e0d2fa823456e81a6cceb2a0141082c81e20e4719949` |
| Q4 | [Q: include/hw/virtio/virtio-gpu-pixman.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/hw/virtio/virtio-gpu-pixman.h) | `f0f406c638472e1d4825e27c4625f1ef0619050ca23171707493acdceb3019ed` |
| Q5 | [Q: hw/display/virtio-gpu.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/display/virtio-gpu.c) | `8a58affd517f00926207163d48b28f25f6deec84afb64c7e5a477bd3bb4bc2c6` |
| Q6 | [Q: ui/console.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/console.c) | `64b8452259df015b2bf867f49705526648b6d250bd52acdf1d9e32154dbb4372` |
| Q7 | [Q: ui/qemu-pixman.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/qemu-pixman.c) | `1294a43551794fb609bb54d30ff732ca90cccd8630fdd8726d441bfbaaa7ed8d` |
| Q8 | [Q: include/ui/console.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/ui/console.h) | `c801dcf1b40a34c733d6cf6a713ee780ea28eda25a06ab5a2993a1c258dbb8b5` |
| Q9 | [Q: scripts/minikconf.py](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/scripts/minikconf.py) | `eb30e55d2019cac67bdcc0532c7a3d6ee110643bbe2652acd8ddfdd98d035d09` |
| Q10 | [Q: meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/meson.build) | `7d45b715ca8e740d787eee6d4a1e8ae4a7456aecfe16dda2a7d32a0f2cc10591` |

Reproduce the declared QEMU selection control from its unchanged checkout with a
separate temporary input containing only `CONFIG_ARM_VIRT=y`:

```text
python scripts/minikconf.py --allnoconfig output.mak output.d input.mak Kconfig \
  CONFIG_TCG=y CONFIG_FDT=y CONFIG_LINUX=y CONFIG_AARCH64=y CONFIG_ARM=y \
  CONFIG_TARGET_BIG_ENDIAN=n
```

Inspect its emitted symbols, then independently inspect the Meson pixman gates;
do not label the control a compiled-device inventory. All new tracked files remain
public-safe Markdown, regular mode 100644. Public references are sufficient to
repeat the source observations if local convenience copies are lost.
