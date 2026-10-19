# Android 17 boot/HAL source ledger

Companion to the [closure matrix and decision](gate-0-android17-boot-hal.md).
Review date **2026-10-19, America/Fortaleza**; Windows x86_64 desktop, source-only.
Gate 0 **Unresolved**; Gates A–G **Not reached**. ADR-0001 **Accepted**;
ADR-0002 **Proposed**. These are research references, not adopted dependencies.

## Independent live preflight

`git ls-remote` independently returned main
`24ddb82ab1b3a6b4bb4a07b5dcee1a7269700838`, matching the requested baseline.
[PR #23](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/23)
was merged at `2026-10-18T23:43:54Z`, head
`6d567f78a0147433a05aeafb5e3d4aeec8961460`, base
`42a397bb08f06cd43a593f6ff54994e8618a3519`; merge equals current main.
Its complete three-file change is the evidence index, assessment and source
ledger (429 additions). Those files were read; the local PR head tree and fetched
main have no difference. PR foundation run `39177327227`, job `117822581068`,
reported success. Reviews/comments were empty; GraphQL review threads were empty
with `hasNextPage=false`. Both connector search and REST open-PR inventory
returned no open PRs: no overlapping heads/bases/diffs/checks/reviews/comments or
unresolved threads required reconciliation, and no intended PR existed to update.

Exact-main [foundation run 39177737707](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39177737707),
[job 117823793048](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39177737707/job/117823793048),
completed successfully. Actual job steps and log receipts identify the exact
checkout and foundation/harness validation, 141 repository tests, seven native
wait controls, injected SIGABRT, four Linux lifetime cases/four mutants, four
seccomp cases, and ten revocation cases/ten semantic mutants with cleanup.
Only foundation was returned for this exact-main push. Android and QEMU workflows
have path filters that do not select PR #23's documentation changes; there is no
new exact-main Android or QEMU success claim. Historical cross-build and device
Unknowns remain as recorded in their respective evidence files.

[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational, page update `2026-10-19T00:34:15.596Z`. Initial sandbox
network access failed. Automatic approval review first failed for model capacity,
then timed out on resumption; the permitted retry succeeded. Failed requests
produced no repository edits or technical evidence. No approval check was bypassed.

Local initial tree was clean, one registered worktree, no stashes; old branches,
ignored assets and historical Privacy-Decoy were preserved. The new branch starts
at exact verified main. All 104 initial tracked entries were regular `100644`;
tracked binary-extension inventory was empty. Existing ignored Gradle/CMake/build
trees contain source/tool/artifact material; they are neither newly adopted nor
freshly attested. New ignored material is retrieved text/metadata and local
hashing/ledger helpers, not guest binaries. No applicable AGENTS.md was found.

Reviewed governing records: both ADRs, requirements, gates, architecture, roadmap,
security boundaries, acceptance criteria and source-provenance policy. Reviewed
PR #23's assessment/ledger and the existing cross-build/dependency, kernel-FD,
snapshot, ARM64 reservation, startup-order, strict TCG memory, isolated-worker,
containment, Android lifetime and Linux revocation evidence. Those controls keep
their narrow scope: no firmware caller admission, Android complete-guest runtime,
trusted whole-tree completion or revocation proof is inherited from them.

Workflows, build recipe and source pins were inspected. The constrained recipe
still disables KVM, SLIRP, pixman and OpenGL; its QEMU/GLib/PCRE2/libffi/
proxy-libintl/GVDB/libfdt/keycodemapdb/softfloat/testfloat and toolchain obligations
are unchanged. Checkout stays pinned to
`3d3c42e5aac5ba805825da76410c181273ba90b1`. No code, dependency, workflow,
permission, SDK, Android configuration or historical source change is included.

## Identity, method and correspondence limits

Files were retrieved using immutable Gitiles `?format=TEXT`, decoded as bytes,
and SHA-256 hashed; QEMU used immutable raw GitHub URLs. Each cited local byte
hash was independently recomputed when generating the table. No binary was
downloaded, built, executed or uploaded. Directory JSON inspection identified
available metadata/module names; directory listings do not prove module ABI or
binary source correspondence.

| Project | Immutable identity / origin |
|---|---|
| device/google/cuttlefish | `283645aacf6cdb56cc31a9362f54d412dbc132a1`, PR #23 Android 17 r1 pin; decisive files freshly retrieved |
| platform/hardware/interfaces | `0162af698935100a590b7359581ac8b1b80693e5`, Android 17 r1 tag independently resolved |
| device/google/cuttlefish_prebuilts | `36f427b7c46682cfcdb2e61eee6893acbfb2a606`, Android 17 r1 tag independently resolved |
| platform/external/rust/crates/vhost-device-vsock | `28233ae213b24a9a35f25e9e49bcadee2bf93821`, Android 17 r1 tag independently resolved |
| kernel/prebuilts/6.12/arm64 | `318576752b27af3d328e6deb5e6aa29b08f762c9`, PR #23 release pin; version/build metadata freshly retrieved |
| kernel/prebuilts/common-modules/virtual-device/6.12/arm64 | `e6673fcbd05e63e6fcc2c2d2cf33246108b73b0c`, PR #23 release pin; commit and root directory freshly inspected |
| kernel/common | `3ec022196c4e9d5c1434599cdda63f622dd6f586`, independently resolved from K1's abbreviated source revision; not claimed as a fully reproduced kernel build |
| qemu/qemu | `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, existing candidate pin; Q1–Q3 freshly retrieved |

K2 reports build `15076761`. K1 adds the version and short source revision;
kernel/common metadata resolves it to the full commit above. This improves PR
#23's build-ID-only evidence but leaves compiler/configuration, complete resolved
build manifest, patches, generated inputs and module source/ABI correspondence
Unknown. The module prebuilt's release-snapshot commit message identifies a
snapshot build, not a corresponding module source revision. Do not equate those.

QEMU default firmware selection is the QEMU-specific function in F1, not its
separate crosvm default function. B1 maps `bootloader_qemu_aarch64` to
`qemu_aarch64/u-boot.bin`. Both qemu_aarch64 and crosvm_aarch64 directory listings
contain a map and binary; neither supplies the missing resolved build manifest.
An ancillary metadata-only query of the crosvm binary is not evidence for the
selected QEMU firmware. No payload was acquired and no binary hash is asserted.

PR #23's system/core/frameworks/graphics source ledger remains the explicit
reference for unchanged Binder/APEX/Zygote/SystemServer and graphics contracts.
This ledger does not reclassify its unresolved whole-product graph as closed.
The selected release tag manifest still is not a SHA-resolved complete build.

## Cited source bytes

IDs are scoped to this record; PR #23 IDs are explicitly labeled in the matrix.
Each URL includes the exact revision. Hashes are source bytes, not executable
artifact or security attestations.

| ID | Immutable source | Retrieved-byte SHA-256 |
|---|---|---|
| C1 | [device/google/cuttlefish:host/libs/vm_manager/qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` |
| C2 | [device/google/cuttlefish:shared/BoardConfig.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/BoardConfig.mk) | `681ae40db963fbdcd59644f8d74fa16013c55e5f09127031c6dfdbe4e0b0df70` |
| C3 | [device/google/cuttlefish:shared/phone/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk) | `69645517941d7013eb798376faeee588cc86f9bfd117dd5eecd27b250b6ad176` |
| C4 | [device/google/cuttlefish:vsoc_arm64/BoardConfig.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/BoardConfig.mk) | `ac168c7015f9c56654f053fdc7bc543c5647fd5f1ba87c33b6b240248b0f1a79` |
| C5 | [device/google/cuttlefish:vsoc_arm64/bootloader.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/bootloader.mk) | `4d6de0b306d8ea180879d095cf4fe820dbe6e0ea0fb2798804752c6545151761` |
| C6 | [device/google/cuttlefish:shared/config/fstab.in](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/fstab.in) | `fb23d90d908c629174ed8c551bc551d712023c0ac394d81afedcc1b0d746c37e` |
| C7 | [device/google/cuttlefish:shared/device.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/device.mk) | `cfd71dfa943e83cb96d64f9cd8e1e1331b2fedca8719b37e1eed372b44876355` |
| C8 | [device/google/cuttlefish:vsoc_arm64/phone/aosp_cf.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/phone/aosp_cf.mk) | `ba74bdb141f2346a53b516fecb9cda9337c903185cdf7b4603b25a7293c77579` |
| F1 | [device/google/cuttlefish:host/commands/assemble_cvd/flags.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags.cc) | `52ba2555c01639b68dfc348fce73124e4b7afa35d82a93e0b1a58c6c59254de9` |
| F2 | [device/google/cuttlefish:host/commands/assemble_cvd/bootconfig_args.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/bootconfig_args.cpp) | `64a5a2be99fa76080a16c45ba38831c264472ff3d882aa4bb9d79eb687d62117` |
| F3 | [device/google/cuttlefish:host/commands/assemble_cvd/flags_defaults.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags_defaults.h) | `c2f95f666070036d10c9160d11fcc080a864c4df3da60d98747bdadfcb5f310a` |
| F4 | [device/google/cuttlefish:host/commands/assemble_cvd/graphics_flags.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/graphics_flags.cc) | `90110f60b41133498df69bf943805c3dd2fc62cea3c914f215dafacd705b2846` |
| B1 | [device/google/cuttlefish_prebuilts:bootloader/Android.bp](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/36f427b7c46682cfcdb2e61eee6893acbfb2a606/bootloader/Android.bp) | `f380f7cbec4c4823a4b20ddcc49590dfd496bc1d9843b085472d5deab18adb29` |
| B2 | [device/google/cuttlefish:host/commands/assemble_cvd/boot_config.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/boot_config.cc) | `057c15874e8706621df790eb1c5e95b6c05926b8fb2a6a9972007b532f136d60` |
| B3 | [device/google/cuttlefish:host/commands/assemble_cvd/disk/generate_persistent_bootconfig.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/disk/generate_persistent_bootconfig.cpp) | `9bf0afc45c2942f23534997bbfb95ec4b4c529f3bf351993bf3b4c2b89a2fc3b` |
| B4 | [device/google/cuttlefish:host/commands/assemble_cvd/disk/generate_persistent_vbmeta.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/disk/generate_persistent_vbmeta.cpp) | `820bcaa5f84a55ec3eb40bb6e10b8cd23d7c2d11858ceec070efc593d758b16d` |
| B5 | [device/google/cuttlefish:host/commands/assemble_cvd/disk/initialize_instance_composite_disk.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/disk/initialize_instance_composite_disk.cc) | `b8446de5acbca34898cce0931c033f780ec74f93dd3f27f2e462ec171405f26c` |
| B6 | [device/google/cuttlefish:shared/config/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/Android.bp) | `f991a5cc35d3bd2edf35160279808a4b6f25ba8e3020494629b363437673c8cb` |
| B7 | [device/google/cuttlefish:shared/config/sed.f2fs](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/sed.f2fs) | `5bcfcdbcde66e8b61df7fb754c9c428e7a1c84664c8ffee54a432d83921c1ce5` |
| B8 | [device/google/cuttlefish:shared/config/sed.hctr2](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/sed.hctr2) | `c85afd7e5b619e9437974313df858ef03d4552d482248b9fbc3a316ed38ee77e` |
| K1 | [kernel/prebuilts/6.12/arm64:kernel_version.mk](https://android.googlesource.com/kernel/prebuilts/6.12/arm64/+/318576752b27af3d328e6deb5e6aa29b08f762c9/kernel_version.mk) | `1c1b36fb95392de6c8a5655c5afc3c46bb5cdec298b662e851ebe65363c311c0` |
| K2 | [kernel/prebuilts/6.12/arm64:prebuilt-info.txt](https://android.googlesource.com/kernel/prebuilts/6.12/arm64/+/318576752b27af3d328e6deb5e6aa29b08f762c9/prebuilt-info.txt) | `3eb143aa24d25af5fe80e9cc67210dca7d6fb8654fac8791e300cd4251bbc3e2` |
| K3 | [kernel/common:Makefile](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/Makefile) | `914a590a9e42c564b2eb8c29ab36bd5ff76110fcf286d1932c71a4c71695d227` |
| K4 | [kernel/common:BUILD.bazel](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/BUILD.bazel) | `1226e7a29bdcbaa838e4ab1b25b821bd0efe1b40236b101af77bdf31b3078c53` |
| H1 | [platform/hardware/interfaces:security/keymint/aidl/default/Android.bp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/security/keymint/aidl/default/Android.bp) | `4fd5f0e9eb3a299ecaa59f6b943bf405be885c0f4174b1897fe90ee5aaedc2a6` |
| H2 | [platform/hardware/interfaces:security/keymint/aidl/default/main.rs](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/security/keymint/aidl/default/main.rs) | `d130b0a47cde3d8b6c191bb25cd6c4c6cd9e1650d5f48896f70ac446ce077a10` |
| H3 | [platform/hardware/interfaces:gatekeeper/aidl/software/Android.bp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/gatekeeper/aidl/software/Android.bp) | `195824e42c91bcea88eb884821de518afc316f46dd4dbfc26fe969b2b9c9c9eb` |
| H4 | [platform/hardware/interfaces:gatekeeper/aidl/software/service.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/gatekeeper/aidl/software/service.cpp) | `9a5a9df96f8864b0b58517fee440b9266d448e469e0d8c5f8c330bdf57f1f996` |
| H5 | [device/google/cuttlefish:guest/hals/keymint/rust/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/keymint/rust/Android.bp) | `7b7f7e8580356d26b4d4ad426a55878526cb2d7c1452ed7da59f5a3381233996` |
| H6 | [device/google/cuttlefish:guest/hals/keymint/rust/src/keymint_hal_main.rs](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/keymint/rust/src/keymint_hal_main.rs) | `dbdab62e5804413815367d5da6e12dd6aa58c66dcd60b5627cd1937d6d714752` |
| S1 | [device/google/cuttlefish:shared/sensors/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/device_vendor.mk) | `f55bf215c446d97e0ee8b009f5f047733093d4a99854ed895cd4db634d3b258b` |
| S2 | [device/google/cuttlefish:shared/sensors/multihal/entry.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/entry.cpp) | `8063cd2e5f58b6202826546738ff04b1388eb49f6c78226dd59f578243795f53` |
| S3 | [device/google/cuttlefish:shared/sensors/multihal/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/sensors/multihal/Android.bp) | `732677a4f80e34fa333103195b08bbed5bcd33c6a4a8322f6e27d56f28e59011` |
| S4 | [device/google/cuttlefish:host/commands/run_cvd/launch/sensors_simulator.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/sensors_simulator.cpp) | `5308ddd96d5ed5ae574de49416117690f415e4595987e32966e504b33939318b` |
| S5 | [device/google/cuttlefish:host/commands/sensors_simulator/main.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/main.cpp) | `2f84b0563ff7b347ccd99de97d08b6eef725970dd9c0a98666ec6845dc9333cc` |
| S6 | [device/google/cuttlefish:host/commands/sensors_simulator/sensors_simulator.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/sensors_simulator/sensors_simulator.cpp) | `13cfcce005c151e9f094887712d5f0aa3205f0f4b467b81ac309c94afc0db38d` |
| Q1 | [qemu/qemu:hw/virtio/vhost-user-vsock.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/vhost-user-vsock.c) | `852c7f3df0c8cb0fa0f5df6c9ed5f6c7d431d6778409799c2791ea3b1a01ff64` |
| Q2 | [qemu/qemu:hw/virtio/vhost-vsock.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/vhost-vsock.c) | `d54faa0905b66d1e233940d03778b06d73cc80d5c7285e6744d4b43e40b08d28` |
| Q3 | [qemu/qemu:net/slirp.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/net/slirp.c) | `f1eb0ede4b4d8016679ef176e33dccfbf659afab1b007ba2a92050a0afbbe799` |
| V1 | [platform/external/rust/crates/vhost-device-vsock:Cargo.toml](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/Cargo.toml) | `9be6642f2fe16fd4ea4577793e36b12202e86a2e68672b19b46d2f28e27e16b0` |
| V2 | [platform/external/rust/crates/vhost-device-vsock:src/main.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/main.rs) | `ec96c3c5bab617b04531b261f23bdb253de733355361ed97f6e0cc63dce8d45f` |
| V3 | [platform/external/rust/crates/vhost-device-vsock:src/vhu_vsock.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/vhu_vsock.rs) | `5052a4deb6f2cc34d6715e19f86db737f52738af08ecee55c4f9fb2daba16e27` |
| V4 | [platform/external/rust/crates/vhost-device-vsock:src/thread_backend.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/thread_backend.rs) | `42aea2cc67d1874716fcb8f918d29da39c4f2832c8a9e3ba5ca732f46780be1b` |
| V5 | [platform/external/rust/crates/vhost-device-vsock:src/vhu_vsock_thread.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/vhu_vsock_thread.rs) | `13d4d8beb2bffcb4bc8c7b369503467c6c7a1ad15d486db57ffd901b142d7074` |
| V6 | [platform/external/rust/crates/vhost-device-vsock:Android.bp](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/Android.bp) | `05cdeeb7f85109f4a9ca4039ed7e383ccb98fecde2c99e9773fb226c3294ec8a` |
| V7 | [platform/external/rust/crates/vhost-device-vsock:LICENSE-APACHE](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/LICENSE-APACHE) | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| V8 | [platform/external/rust/crates/vhost-device-vsock:LICENSE-BSD-3-Clause](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/LICENSE-BSD-3-Clause) | `a408ca693a3359c5d56de80ee73db9b62ca4a179adb12e131230c10e915b05f2` |
| V9 | [device/google/cuttlefish:common/libs/fs/shared_fd.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/shared_fd.cpp) | `7b14de57239c6d7383e96b6420acdeec841a04d6862fa3208da164932e633d1e` |
| V10 | [device/google/cuttlefish:host/commands/run_cvd/launch/tombstone_receiver.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/tombstone_receiver.cpp) | `d7546b2799390d08da28e73c1a936761dd6d27497791d7cbc804af98c9488b0a` |
| V11 | [device/google/cuttlefish:host/commands/run_cvd/launch/vhost_device_vsock.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/vhost_device_vsock.cpp) | `b34c77e9f23928d82f2d74e88937cfcdaa13f62fbdb3b49edc42336be14ea183` |
| L1 | [device/google/cuttlefish_prebuilts:bootloader/LICENSE](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/36f427b7c46682cfcdb2e61eee6893acbfb2a606/bootloader/LICENSE) | `7e354ab349b7c11f1fe93639c3096bfe2bb4591659caaa712e2ee101299cf1d4` |


## Dependency, rights and trusted-computing-base review

| Reference family | Source/license observation and remaining obligation |
|---|---|
| Cuttlefish configuration, host helpers, guest clients | Inspected files predominantly carry Apache-2.0 headers. Host helpers use Cuttlefish filesystem/transport, logging, configuration and other libraries; sensor multihal imports goldfish virtual defaults. Neither an Android backend port nor transitive license/build closure is reviewed. Client and protocol parsers, management-facing transport and helper lifetime affect the host TCB. |
| Guest KeyMint/Gatekeeper | H1–H4 supply actual software service and APEX definitions. Dependencies include Rust Binder, kmr HAL/TA, crypto, libgatekeeper/keymaster, libscrypt and SharedSecret interfaces. APEX certificate/key modules are reference choices, not PDVA signing. Apache-2.0 notices do not resolve security suitability or all crypto/source obligations. Test-only/nonsecure restrictions are technical qualification blockers, not erased by source availability. |
| Userspace-vsock | V1/file SPDX notices identify Apache-2.0 OR BSD-3-Clause; V6's Android license selection names Apache-2.0. V7–V8 contain license texts. `rust_binary_host` lists vhost, vhost-user-backend, virtio queue/vsock/bindings, vm-memory, vmm-sys-util, epoll, config/serde/yaml, CLI/logging and utility crates. Cargo version ranges are not a resolved transitive source manifest. Android/Bionic build, syscall, FD-sharing, SELinux and all-service-client compatibility remain U. The helper maps guest memory, parses hostile queues and has its own retained handles/threads; isolating only QEMU is insufficient. |
| QEMU and SLIRP | QEMU retains GPL/file-specific terms and existing research adoption limits. Q1's USER backend is distinct from Q2's kernel backend. Q3 calls libslirp; no new libslirp version, build or transitive rights audit is accepted here. The current cross-build disables it. Reference DNS and host filesystem sockets cannot be transplanted as an approved Android/VPN transport. |
| Kernel/modules | Kernel GPLv2 and file/module notices, complete corresponding source, config, generated inputs, compiler and ABI closure are required. K1–K4 are a lead, not artifact reproduction. No kernel/module license or binary is imported by this PR. |
| Firmware | B1 explicitly declares GPL-2.0-only and L1 supplies the license. This establishes an obligation, not fulfillment of corresponding-source or redistribution requirements for the exact selected prebuilt. Source/build/DTB/AVB correspondence remains a blocking next question. |
| Full guest and graphics | Existing mixed AOSP and graphics/component licenses remain in PR #23. Generated VINTF/APEX/init, AVB signing, encryption services, software graphics and interactive input need a consistent reviewed build. No blanket AOSP image rights, GMS rights, hardware-backed attestation or certification are inferred. |

Missing corresponding source or redistribution rights prevents acceptance even
where a mechanism looks viable. These source references do not authorize engine
adoption, full guest building, production helpers, additional privileges or an
architecture change. No source implementation is copied into tracked runtime code.

## Negative evidence and retrieval limits

Failed guessed paths were not used as evidence of absence. Gitiles returned 404
for `host/libs/config/bootconfig_args.*` (actual path is assemble_cvd), top-level
guest KeyMint/Gatekeeper Android.bp files (actual subdirectories were discovered),
KeyMint `src/main.rs` (actual `keymint_hal_main.rs`), hardware Gatekeeper
`aidl/default` (actual `aidl/software`), and KeyMint `default/rust` (files are in
default). The vsock README names `vhost_user_vsock_thread.rs`, but the tree/source
uses `vhu_vsock_thread.rs`; the latter was retrieved and reviewed. A guessed
`src/vsock.rs` failed. `platform/external/u-boot` at the Android 17 release tag
returned 404; this does not prove U-Boot source is unavailable. Exact firmware
correspondence remains Unknown rather than an invented pin.

Manual counterexamples remain explicit: kernel vhost survives TCG; userspace
backend existence does not repair launcher selection or all callers; remote
FIFO declarations do not select remote HAL APEXes; a nonsecure HAL is not a
secure-environment implementation; an init_boot omission breaks this boot
contract; headless output is not an interactive phone; license text is not
complete corresponding source. No table-only automated oracle was added.

## Local validation and publication boundary

Validation results are recorded after execution below. The initial unchanged
baseline passed foundation (104 files, 60 Markdown, 54 requirements, two ADRs),
harness authority validation and repository regression (141 tests: 137 passed,
four existing Windows skips). The default Python command was an unavailable
Store alias; the existing NDK Python ran these checks, without installation.

Final documentation validation with the existing NDK Python:

- Foundation: **106 files, 62 Markdown files, 54 requirements, two ADRs**, passed;
  includes local Markdown targets and foundation hygiene.
- Repository regressions: **141 tests, 137 passed, four skipped**. Existing
  Windows skips are Linux host C controls, destination/ancestor symlinks,
  executable modes and real POSIX symlink/type substitution; not passes.
- Harness manifest/source authority validation passed; no Android execution.
- **51 cited source byte hashes** recomputed and matched; all table source URLs
  contain immutable 40-hex revisions. Retrieval failures are documented above.
- Whitespace, exact-base three-file documentation diff, text/file-mode inventory,
  source-reference consistency and public-data hygiene reviewed. No runtime,
  binary, dependency, workflow, requirement or ADR changes are intended.

No Android or guest runtime tests, new QEMU cross-build, APK build, Linux native
controls or phone operation ran locally. Skips and unexecuted tests are not
passes. Hosted preflight results apply only to exact old main. New-PR hosted CI
is **pending/unobserved at publication**. After creation, verify the PR identity,
branch/head/base and native chat attachment once, then stop without polling CI,
reviews, comments, bots or mergeability. No merge is requested.
