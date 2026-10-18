# Complete Android 17 source ledger and preflight

Companion to the [focused feasibility assessment](gate-0-complete-android.md).
Review date: **2026-10-18, America/Fortaleza**. Windows x86_64 local desktop;
source retrieval/read-only GitHub queries, no Cloud or guest execution.
Gate 0 **Unresolved**; Gates A–G **Not reached**. ADR-0001 **Accepted**;
ADR-0002 **Proposed**. Sources below are references, not adopted dependencies.

## Live preflight before tracked edits

Independent `git ls-remote` returned main
`42a397bb08f06cd43a593f6ff54994e8618a3519`, matching the owner-provided baseline.
Fetch preserved the old branch; its tree had no difference from the merge.
The research branch starts at that exact main. [PR #22](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/22)
was MERGED at `2026-10-18T18:35:41Z`, head
`b4d137d6980b3ed5db25938408a520847dd72d82`, base
`7e68da5d4fe489828bbadc7615265652bc8d38de`; merge equals expected main.
PR checks reported foundation and android SUCCESS. Reviews, conversation
comments and review threads were empty. Open PR REST inventory returned `[]`:
there were no open heads/bases, complete diffs, jobs/logs, reviews/comments or
threads to reconcile, and no existing intended PR to duplicate.

Exact-main [foundation run 39154869218](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39154869218),
job `117755898829`, and [Android run 39154869252](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39154869252),
job `117755903051`, completed successfully. Both logs identify the exact checkout.
Job/step records and actual log receipts were read. Foundation receipts include
seven native wait cases, one injected SIGABRT, four Linux lifetime cases/four
mutations, four seccomp cases, and **ten revocation cases/ten semantic mutants**
with cleanup. This newly observes the corrected PR #22 controls on merged main;
its old publication-time pending text is historical, not current failure.
Android receipts include 68 protocol/report checks, BUILD SUCCESSFUL and release
authority/native inspection. No target execution follows from these receipts.
Two exact-main check runs returned success. Combined commit status returned zero
contexts; its aggregate `pending` is not another pending CI job. No exact-main
QEMU run was returned, and no new QEMU success is inferred.

[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational, page update `2026-10-18T22:19:11.280Z`. That is a preflight snapshot,
not a promise about publication-time CI.

Local tracked state was clean, one registered worktree, no stashes; existing
local/remote branches and ignored assets were preserved. All 102 tracked entries
were regular `100644`; no tracked APK/AAR/JAR/SO/image/EXE/ZIP was returned by
the inventory. Existing ignored build/tool/reference assets include binaries;
they were not executed as guests, newly adopted, redistributed, deleted or
re-attested. No applicable AGENTS.md was found. Historical Privacy-Decoy stayed
read-only and unchanged. Sandbox Git index/network access required authorized
escalated retries; no security settings were changed.

Reviewed prerequisites: requirements, both ADRs, gates/evidence criteria,
provenance and guest-image policy; platform, cross-build/execution, worker
integration, TCG memory and ARM64 boot records; containment, lifecycle exceptions,
retained-capability/revocation evidence; dependency/adoption and antivirus
records; workflow/source pins, build configuration and native inventory.
The existing source-pinned recipe carries QEMU, GLib, PCRE2, libffi,
proxy-libintl, GVDB, dtc/libfdt, keycodemapdb, softfloat/testfloat and build tools.
Those prior adoption limits remain; no new dependency, binary, workflow,
permission, SDK setting, Android code or security gate is changed.

## Identity and retrieval method

AOSP `+/refs/tags/android-17.0.0_r1?format=JSON` commit metadata independently
resolved the revisions below. Files were then fetched at those immutable IDs
through Gitiles `?format=TEXT`, base64-decoded and SHA-256 hashed. The manifest
itself defaults projects to the release tag: it is not a fully SHA-resolved
build manifest or proof that every included prebuilt has corresponding source.

| Project | Android 17 r1 resolved commit |
|---|---|
| platform/manifest | `5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f` |
| platform/build | `5ce6f787337d0223710bf7d4a16dbe6d2a35f777` |
| platform/system/core | `545d2487e38192a2ce25040897ced877cf6b4f53` |
| platform/frameworks/base | `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` |
| platform/frameworks/native | `ae266dcb706d083868578cfedce381ef44488a07` |
| device/google/cuttlefish | `283645aacf6cdb56cc31a9362f54d412dbc132a1` |
| platform/external/angle | `1f4500d3906c24de59eec5b9cda17a2ad2a8ba2d` |
| platform/external/swiftshader | `9a22bb9de00f5d8ddf4fc5ba5c2f425c2816e679` |
| platform/external/minigbm | `ce79bbee67b3e2ea7abb110e1415e9ceceaa6471` |
| platform/external/drm_hwcomposer | `87daba89b05fabc7f1e9316e3f283f19fd0c45cd` |
| kernel/prebuilts/6.12/arm64 | `318576752b27af3d328e6deb5e6aa29b08f762c9` |
| kernel/prebuilts/common-modules/virtual-device/6.12/arm64 | `e6673fcbd05e63e6fcc2c2d2cf33246108b73b0c` |

The kernel/module entries identify reference repositories, **not** audited
kernel source or downloaded payloads. K1 yielded only a build ID. No exact
matching kernel source/configuration/toolchain closure was established.
The sepolicy S1 revision is the existing Android 17 r1 identity; its file was
freshly retrieved/hashed, without claiming a new tag-resolution query for it.

QEMU remains the cross-build input
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`. Upstream commit API and the retained
clean checkout independently matched. Q1–Q5 fetched from immutable upstream
raw URLs were byte-identical to `git show HEAD:path`; no newline normalization
was needed for that comparison. Earlier QEMU hashes/adaptations and dependency
licenses remain in the [integration](gate-0-qemu-worker-integration.md) and
[cross-build](gate-0-qemu-android-crossbuild-feasibility.md) ledgers.

## Inspected immutable files

Grouped IDs A1/A3/A4 in the assessment refer to all letter-suffixed rows.
Hashes describe retrieved source bytes, not any compiled artifact. License
headers in C/A files are principally Apache-2.0; QEMU retains its overall GPL
and file-specific terms. L1–L4 are scoped notices, not a transitive rights audit.

| ID | Immutable file | SHA-256 | Inspected contract / limitation |
|---|---|---|---|
| C1 | [device/google/cuttlefish: host/libs/vm_manager/qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` | Boot/configuration, KVM condition, kernel vhost, HAL console peers, graphics/input |
| C2 | [device/google/cuttlefish: shared/BoardConfig.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/BoardConfig.mk) | `681ae40db963fbdcd59644f8d74fa16013c55e5f09127031c6dfdbe4e0b0df70` | Kernel default, modules, AVB, boot headers and guest policy |
| C3 | [device/google/cuttlefish: shared/device.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/device.mk) | `cfd71dfa943e83cb96d64f9cd8e1e1331b2fedca8719b37e1eed372b44876355` | HAL packages, remote/nonsecure/Trusty choices, conditional proprietary paths |
| C4 | [device/google/cuttlefish: shared/phone/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk) | `69645517941d7013eb798376faeee588cc86f9bfd117dd5eecd27b250b6ad176` | Phone vendor include graph and declared touch features |
| C5 | [device/google/cuttlefish: vsoc_arm64/phone/aosp_cf.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/phone/aosp_cf.mk) | `ba74bdb141f2346a53b516fecb9cda9337c903185cdf7b4603b25a7293c77579` | System/system_ext/product/vendor inheritance; 16-KiB support setting |
| C6 | [device/google/cuttlefish: shared/config/fstab.in](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/fstab.in) | `fb23d90d908c629174ed8c551bc551d712023c0ac394d81afedcc1b0d746c37e` | Logical partitions, AVB, metadata, userdata and filesystems |
| C7 | [device/google/cuttlefish: shared/graphics/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/graphics/device_vendor.mk) | `aaca0033829b1c239e894146d91cf10d37c832915ce1f040a11be514945e8fe8` | Composer, gralloc, mapper and graphics packages |
| C8 | [device/google/cuttlefish: shared/swiftshader/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/swiftshader/device_vendor.mk) | `1710b075bc15363715d650eebf76225dc5851c0bae4966abebe6acd140e9eabc` | Guest executable-memory requirement |
| C9 | [device/google/cuttlefish: vsoc_arm64/bootloader.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/bootloader.mk) | `4d6de0b306d8ea180879d095cf4fe820dbe6e0ea0fb2798804752c6545151761` | No single product-built bootloader, not no launcher firmware |
| C10 | [device/google/cuttlefish: shared/config/graphics/init_graphics.vendor.rc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/graphics/init_graphics.vendor.rc) | `cf45c91516ac2c5ef54feb5853bbdf9c9acdacef99d69b9eadff9f9b23eedae5` | Boot-property to HAL-property propagation |
| C11 | [device/google/cuttlefish: shared/config/input/Cuttlefish_Vhost_User_Multitouch_Touchscreen_0.idc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/input/Cuttlefish_Vhost_User_Multitouch_Touchscreen_0.idc) | `67468f7a834581bd1b8f31785b50bf9b8ba35eac87525e1b3328177b26f691af` | Device/display association and orientation |
| C12 | [device/google/cuttlefish: vsoc_arm64/BoardConfig.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/BoardConfig.mk) | `ac168c7015f9c56654f053fdc7bc543c5647fd5f1ba87c33b6b240248b0f1a79` | ARM64/secondary ARM ABI and board includes |
| M1 | [platform/manifest: default.xml](https://android.googlesource.com/platform/manifest/+/5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f/default.xml) | `76ef74339da1e0c973d1ec7cb92045e823223a7724d9aa453b4cab4e246122c4` | Manifest defaults to release tag and includes kernel prebuilts |
| A4a | [platform/build: target/product/base_system.mk](https://android.googlesource.com/platform/build/+/5ce6f787337d0223710bf7d4a16dbe6d2a35f777/target/product/base_system.mk) | `1846bed2dc61a52b90db0bfaaabc1cc24a2326113ff9c3069af649bfde1dcd12` | Base system services and ART product include |
| A4b | [platform/build: target/product/handheld_system_ext.mk](https://android.googlesource.com/platform/build/+/5ce6f787337d0223710bf7d4a16dbe6d2a35f777/target/product/handheld_system_ext.mk) | `9e548dc57becae4dddea2ef93a6a3eaa831396de205fabc35b6a063adcb284c8` | Launcher and SystemUI |
| A4c | [platform/build: target/product/aosp_product.mk](https://android.googlesource.com/platform/build/+/5ce6f787337d0223710bf7d4a16dbe6d2a35f777/target/product/aosp_product.mk) | `7299651a28575223fba525d59caa007bc9f932ad71d50476ab860696027f87c2` | AOSP product include graph |
| A1a | [platform/system/core: rootdir/init.rc](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/rootdir/init.rc) | `8b8d9d9c2c17fcb1f907b0a369aae03632976dff8f4cf603b1d5ef83cad78225` | binderfs/APEX/init requirements |
| A1b | [platform/system/core: init/first_stage_init.cpp](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/init/first_stage_init.cpp) | `ddb34b37d470ad8266150865513ed25cbf29e1d404e248022765fbb1d9bc3b31` | First-stage mounting and module/boot preparation |
| A3a | [platform/frameworks/base: core/java/com/android/internal/os/ZygoteInit.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/com/android/internal/os/ZygoteInit.java) | `d989ee5ad700785596b584ae6d09e1c19c0354275323cb13b420c8783b28ab84` | SystemServer process/classpath initialization |
| A3b | [platform/frameworks/base: services/java/com/android/server/SystemServer.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/java/com/android/server/SystemServer.java) | `5138c483c8495bac185e1bdbd328d287a1235ff0549e124e8c3d2d3a4fc473bd` | Core/app/window/input/IME services |
| A5 | [platform/frameworks/native: services/inputflinger/reader/EventHub.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/EventHub.cpp) | `38f5775af51d5bbe09d7c87778a510a35f52120e46f1b000202aa16052659d97` | Guest event-device discovery and touch classification |
| A6 | [platform/frameworks/native: services/surfaceflinger/SurfaceFlinger.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/surfaceflinger/SurfaceFlinger.cpp) | `13b03a5c51750456a169ab8801efe933ecc18a966421b8821043b37c321b7fb2` | Composer and RenderEngine integration |
| A2 | [platform/system/core: rootdir/init.zygote64.rc](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/rootdir/init.zygote64.rc) | `7be8fde03ec2cc4417aecf1a79163e0e4088fdff02ee6cd2426d02f91127e479` | app_process64 starts system_server |
| S1 | [platform/system/sepolicy: private/isolated_app_all.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te) | `e65adb199d7fc26cd716f4e376f6068edcd3c350647f121e8d5937fa9bca4ad9` | Guest/host distinction: host isolated GPU/socket/file restrictions |
| Q1 | [qemu/qemu: hw/virtio/vhost-vsock.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/vhost-vsock.c) | `d54faa0905b66d1e233940d03778b06d73cc80d5c7285e6744d4b43e40b08d28` | Host kernel device open and kernel backend |
| Q2 | [qemu/qemu: hw/input/virtio-input-hid.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/virtio-input-hid.c) | `aae90a22fda46a0a61939cf3f4e56f93bf751215dffb3d2ba643b7f09a3693f9` | Virtual multitouch slot/event/feature contract |
| Q3 | [qemu/qemu: hw/display/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/display/meson.build) | `36fb16a74d50369756313baaecee09b687139effa5bfa3aed03e2e61025e6abd` | Graphics device source dependencies |
| Q4 | [qemu/qemu: ui/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/meson.build) | `388b34e5e83aa13579622e366e211a411cfeb9777ed341b7c0ca251e381434ea` | VNC requires pixman; UI helper distinction |
| Q5 | [qemu/qemu: include/ui/pixman-minimal.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/ui/pixman-minimal.h) | `951305c142fa19cc857d36f29b880299f787439d3f447e58b7721134e7e161d9` | Minimal compatibility code does not prove a selected GUI device |
| L1 | [platform/external/angle: LICENSE](https://android.googlesource.com/platform/external/angle/+/1f4500d3906c24de59eec5b9cda17a2ad2a8ba2d/LICENSE) | `b9c83eb591e222e3b742d4c71d2fc496ca3f50c14de621c52c317b51972897ca` | BSD-style project notice; transitive dependencies unreviewed |
| L2 | [platform/external/swiftshader: LICENSE.txt](https://android.googlesource.com/platform/external/swiftshader/+/9a22bb9de00f5d8ddf4fc5ba5c2f425c2816e679/LICENSE.txt) | `3ddf9be5c28fe27dad143a5dc76eea25222ad1dd68934a047064e56ed2fa40c5` | Apache-2.0 project text; transitive dependencies unreviewed |
| L3 | [platform/external/minigbm: LICENSE](https://android.googlesource.com/platform/external/minigbm/+/ce79bbee67b3e2ea7abb110e1415e9ceceaa6471/LICENSE) | `8610954adbca6c6b85d8b1ae5613b44b0014e437d32fcad6683bb27541411686` | BSD-style notice; full file inventory unreviewed |
| L4 | [platform/external/drm_hwcomposer: LICENSE](https://android.googlesource.com/platform/external/drm_hwcomposer/+/87daba89b05fabc7f1e9316e3f283f19fd0c45cd/LICENSE) | `ebdb70f58fa8708044dcbba80f51dd7c31973a7fa15ae83fa50ed7da6cf8d7a8` | Apache-2.0 with named MIT test-header exception |
| K1 | [kernel/prebuilts/6.12/arm64: prebuilt-info.txt](https://android.googlesource.com/kernel/prebuilts/6.12/arm64/+/318576752b27af3d328e6deb5e6aa29b08f762c9/prebuilt-info.txt) | `3eb143aa24d25af5fe80e9cc67210dca7d6fb8654fac8791e300cd4251bbc3e2` | Build ID only; not corresponding kernel source |

## Live documentation, assumptions and negative evidence

Retrieved official [Android 17 behavior changes](https://developer.android.com/about/versions/17/behavior-changes-all)
identify API 37 and device-RAM-dependent app limits. This establishes no safe
numerical guest-memory allowance or per-OEM behavior. The host Android version
is distinct from the guest target; API 30 is only the existing cross-link target.
No development memory exemption was used or proposed.

Official [AOSP build prerequisites](https://source.android.com/docs/setup/start/requirements)
describe Linux, at least 400 GB free disk and 64 GB RAM for building. These are
build-workstation recommendations, not guest or phone RAM requirements.
Official [license guidance](https://source.android.com/docs/setup/contribute/licenses)
describes preferred Apache-2.0 and exceptions including kernel GPLv2; it does
not grant blanket image rights. No proprietary Google software was retrieved.

Assumptions under test: a source-built guest virtual device can use software
rendering, guest-local key services where appropriate, and explicit virtual
input without host hardware passthrough; a bounded host transport can expose
these to an ordinary app while preserving separate management authority.
Neither assumption is an implementation fact or an accepted architecture.

Source counterexamples were retained: C1's kernel vhost dependency survives
replacing KVM; its ARM firmware path differs from the raw-Image control; mouse
and keyboard declarations do not establish multitouch; minimal pixman helpers
do not establish a selected GPU/VNC build; a build ID is not kernel provenance.
These are manually traced source witnesses, not executable negative tests.

Retrieval failures: initial sandbox Git network failed and succeeded on the
authorized retry. `python` resolved to an unavailable Store alias; the already
installed NDK Python was used for local hashing/validation, without installation.
Its urllib HTTPS support was unavailable; PowerShell HTTPS retrieval succeeded.
Guessed Cuttlefish `shared/config/init.graphics.rc` and drm_hwcomposer `NOTICE`
returned 404; tree discovery located the actual C10 and L4 files. Guessed
`kernel/common` branch `android17-6.12` and virtual-device prebuilt-info paths
returned 404. Neither is proof that corresponding source is absent; that chain
remains Unknown. No failed lookup is cited as a positive observation.

## Local validation and publication boundary

Local validation used the existing NDK Python and completed successfully:

- Foundation validation: 104 files, 60 Markdown files, 54 requirements, two ADRs;
  local Markdown targets and repository hygiene accepted.
- Repository regression suite: 141 tests discovered, **137 passed, four skipped**.
  The Windows skips cover Linux host C controls, destination/ancestor symlinks,
  executable modes and real POSIX symlink/type substitution. They are not passes.
- Harness manifest authority validation passed; this is not Android execution.
- `git diff --check` passed. The complete three-file documentation diff,
  source identities, link targets, regular text modes and absence of new
  runtime/binary/dependency/workflow changes were reviewed before publication.

No runtime code or test fixture is changed. Android build/device/guest tests
were not rerun for documentation changes; no missing test is counted as a pass.

The new PR's hosted CI remains **pending/unobserved**. After creation, perform
one immediate PR/branch/head/base and native conversation-attachment check and
stop. The old exact-main CI above is not evidence for this new head. Do not poll
CI, reviews, comments, bots or mergeability, and do not merge this research PR.
