# Android 17 QEMU U-Boot source and provenance ledger

Companion to the [assessment and R/H matrix](gate-0-android17-uboot.md).
Review date **2026-10-19, America/Fortaleza**, Windows x86_64 local desktop.
**Gate 0 Unresolved; Gates A–G Not reached; ADR-0001 Accepted; ADR-0002 Proposed.**
References are not adopted dependencies. No guest or compiler payload was acquired.

## Live preflight before tracked edits

GitHub branch metadata and independent `git ls-remote` agreed on main
`1cdd679df2806ccd171ddd83697a9da4f4468598`, the requested baseline. Its tree is
`50b328471ea00c8ac451c7a5fbddfaf782616a6c`. [PR #25](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/25)
was merged by repository owner `innercoder78`; GitHub recorded the merge at
`2026-10-19T18:26:27Z`, with merge commit equal to main, exact head
`1381846d4c91c85939191884915d9b6641bda65c` and base
`8ed024150019a0c9d07fc66e2463ced755d589c0`. The commit is GitHub-verified.
Its complete exact-base/head change is one roadmap file, 418 additions and 50
deletions; the full patch and resulting roadmap were reviewed. Reviews,
conversation/inline comments and review threads were empty. Connector search
and REST inventory returned **zero open PRs**, so there were no open heads,
bases, diffs, checks, reviews or unresolved threads to reconcile.

PR #25's exact-head [foundation run 39302037350](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39302037350),
job `118229434938`, succeeded. Independently, exact-main
[foundation run 39302783384](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39302783384),
[job 118232014915](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39302783384/job/118232014915),
succeeded. Actual logs identify each checkout and receipts for foundation/harness
validation, 141 repository tests, seven native wait controls, one injected
SIGABRT, four Linux lifetime cases/four mutants, four seccomp cases, and ten
revocation cases/ten semantic mutants with cleanup. Only foundation was returned
for exact-main; no new Android/QEMU success is inferred. Legacy status returned
zero contexts; its aggregate `pending` is not another pending job. Workflows'
triggers, exact-head checkout pin, read-only permissions and limits were reviewed.

[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational, page update `2026-10-19T18:14:45.54Z`. These are pre-publication
observations, not new-head CI or a runtime result.

Local state began clean on PR #25's branch at its exact head, one registered
worktree, no stashes. All branches were inventoried; cached origin/main was
stale and was fetched without pruning. The head tree equaled newly fetched main.
The one research branch starts at verified main. All 106 tracked entries were
regular `100644`; tracked binary-extension inventory was empty. Ignored Gradle,
CMake, build/tool/source and Python-cache assets were inventoried and preserved.
Historical Privacy-Decoy was untouched. No applicable AGENTS.md was found.

Reviewed both ADRs, requirements, roadmap, feasibility gates, architecture,
security boundaries, evidence criteria and source policy; complete PR #23–24
source ledgers and feasibility records; existing ARM64 reservation, resource-FD,
startup ordering, cross-build/integration and containment research. Earlier
source/build evidence retains its limits. Dependency pins and existing native/
build inventory remain unchanged; no new runtime, Android code, permission, SDK,
workflow or tool installation is included. The checkout action remains
`3d3c42e5aac5ba805825da76410c181273ba90b1`.

## P: exact prebuilt metadata

- [Release snapshot](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/36f427b7c46682cfcdb2e61eee6893acbfb2a606):
  tree `2cf5a792a03d756be8633db52d982f36333e7f51`.
- [Import commit](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/cd77f9d3211a4f8c22beb631b4bddcd99802cae8):
  same tree; build 15108624; selected QEMU binary Git blob
  `e4f067f8fa49256e565e054bec069620b7d104db`, regular `100644`.
- [Selected QEMU directory](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/36f427b7c46682cfcdb2e61eee6893acbfb2a606/bootloader/qemu_aarch64):
  tree `87fb2e9780449910f6702d56b46336ab1869d59b`; map Git blob
  `eab5b9e3f197032bd4816510c61002032e34f7de`. Directory metadata was read;
  the firmware binary was not downloaded.
- [Resolved U-Boot commit](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59):
  tree `c9ccd58fc02647095d2b2d458253b7190534cd9d`. The import log alone is
  insufficient because the actual pinned update script extracts its version
  from crosvm; the QEMU build records below provide the target-specific check.

## B: published target-specific build records

All following URLs select build **15108624**, **u-boot_qemu_aarch64**, attempt
**1**. Initial discovery used the official update script's `latest/raw` form;
the same text was subsequently obtained through explicit `1/raw` URLs. Hashes
identify the retrieved bytes. They do not make the remote service append-only.

| Record | Retrieved-byte SHA-256 |
|---|---|
| [BUILD_INFO](https://ci.android.com/builds/submitted/15108624/u-boot_qemu_aarch64/1/raw/BUILD_INFO) | `ff9e64b634aa5c631ed09719efcb48c82ee19cf70910904e47e5d01406d3a0f5` |
| [Resolved manifest](https://ci.android.com/builds/submitted/15108624/u-boot_qemu_aarch64/1/raw/manifest_15108624.xml) | `7b6ec03ba0d98c26be5da9b2468ba2b98b31c056ff41af00281b0a407839b279` |
| [DSSE provenance envelope](https://ci.android.com/builds/submitted/15108624/u-boot_qemu_aarch64/1/raw/multiple.intoto.jsonl) | `15a9ff2bee53692aa14fa9220fc4cc84bd605d735ab0afc11b99395a2ce0996f` |
| [repo.prop](https://ci.android.com/builds/submitted/15108624/u-boot_qemu_aarch64/1/raw/repo.prop) | `94fe23cdca7cb13370ec365c50236707771f51f3b69eefe8a1ed116765742f16` |
| [applied.prop](https://ci.android.com/builds/submitted/15108624/u-boot_qemu_aarch64/1/raw/applied.prop) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |
| [Build log](https://ci.android.com/builds/submitted/15108624/u-boot_qemu_aarch64/1/raw/logs/build.log) | `1bc4a004fea331f4075a8670451839a393cf9212b1c5a6ee9328fa8a1a5099f1` |

The envelope payload is an in-toto Statement v0.1 with SLSA provenance v0.2.
Its QEMU entry point and 33 Git materials agree with BUILD_INFO/repo.prop;
32 projects agree with XML, which excludes the manifest repository itself.
Container material SHA-256
`fa18c78d3fb21c25313f2d748195b3fbfbee9829e110d99cefca2b06cbaf237e`
agrees with BUILD_INFO. Neither container availability nor its full build-source
closure was tested. No container was downloaded or run. The statement's
completeness object is empty; **its signature was not cryptographically verified**.

Retrieved manifest, repo.prop, empty applied.prop and build.log hashes match
their statement subjects. The selected prebuilt's System.map independently
hashes to subject `b3de55bd712e450ae9a1819f98a54fde2e3fe418c8a974bc405956c49ddc6002`.
The firmware subject is
`29fba6031de38de5ba225925ca41defa02c28e0257305c4829d417bdaff85f6b`;
the ELF subject is
`c1c5a7ac8c620029ccca0e6306b28ea7082008187e080662fcc4ceb58b4bf2dd`.
Those two are **upstream published digests only**. No executable bytes were
retrieved or locally hashed. This is consistency evidence, not an authenticated
attestation, reproduced firmware, verified `.config` or PDVA release trust.

The log reports successful target execution/installation by the upstream build
service, not guest execution. It also records deprecated build settings,
invalid/overridden fragment values, conversion warnings and linker warnings
about `_start`. The latter are not attributed to the final firmware without
action-level evidence. No warning is classified as fixed or harmless by this
audit. No generated final `.config` is listed among the published artifacts.

## Resolved build manifest inventory

These are **recorded build inputs**, not 33 independently rebuilt/audited
dependencies. Immutable source links identify their repositories; only the
specific text files in the next table were fetched/reviewed in this investigation.
Kernel manifest is recorded separately from the 32 XML project elements.

| Repository | Exact recorded revision |
|---|---|
| [platform/bootable/libbootloader](https://android.googlesource.com/platform/bootable/libbootloader/+/9adba3c4ef90eaa7c6506fdf224850c1a994595d) | `9adba3c4ef90eaa7c6506fdf224850c1a994595d` |
| [kernel/build](https://android.googlesource.com/kernel/build/+/b6b2ec88ae2ef29b031db9f8e63cd91c4d7c7882) | `b6b2ec88ae2ef29b031db9f8e63cd91c4d7c7882` |
| [platform/external/bazel-contrib-bazel_features](https://android.googlesource.com/platform/external/bazel-contrib-bazel_features/+/256208a0ba60adcb57c9d83197fbb363446a065e) | `256208a0ba60adcb57c9d83197fbb363446a065e` |
| [platform/external/bazel-contrib-rules_devicetree](https://android.googlesource.com/platform/external/bazel-contrib-rules_devicetree/+/bc0509e0ae6195f9a47764c3d846459f713fa741) | `bc0509e0ae6195f9a47764c3d846459f713fa741` |
| [platform/external/bazel-contrib-supply-chain](https://android.googlesource.com/platform/external/bazel-contrib-supply-chain/+/d272ef31b0c4f743fdc5fe7a211ddf47816585e8) | `d272ef31b0c4f743fdc5fe7a211ddf47816585e8` |
| [platform/external/bazel-skylib](https://android.googlesource.com/platform/external/bazel-skylib/+/5b1ebf307a37c3cd369e2bcf2f5b7e9cbfb79b36) | `5b1ebf307a37c3cd369e2bcf2f5b7e9cbfb79b36` |
| [platform/external/bazelbuild-bazel-central-registry](https://android.googlesource.com/platform/external/bazelbuild-bazel-central-registry/+/0480a0059a84904eff350db29b3c54c9ca0acaa2) | `0480a0059a84904eff350db29b3c54c9ca0acaa2` |
| [platform/external/bazelbuild-rules_cc](https://android.googlesource.com/platform/external/bazelbuild-rules_cc/+/c4e256680710e65f1305b8ded16e5394a0572dca) | `c4e256680710e65f1305b8ded16e5394a0572dca` |
| [platform/external/bazelbuild-rules_license](https://android.googlesource.com/platform/external/bazelbuild-rules_license/+/8252dd056e1381eb60300c4158522318eb2eaafd) | `8252dd056e1381eb60300c4158522318eb2eaafd` |
| [platform/external/bazelbuild-rules_pkg](https://android.googlesource.com/platform/external/bazelbuild-rules_pkg/+/d7c6270a04f291875abac6fd218575b2a45ba09d) | `d7c6270a04f291875abac6fd218575b2a45ba09d` |
| [platform/external/bazelbuild-rules_python](https://android.googlesource.com/platform/external/bazelbuild-rules_python/+/571592f347f363a88facb851536befcbf6f73700) | `571592f347f363a88facb851536befcbf6f73700` |
| [platform/external/bazelbuild-rules_rust](https://android.googlesource.com/platform/external/bazelbuild-rules_rust/+/5975ad7ee75212b585f75da60444fcc4a43ff5f3) | `5975ad7ee75212b585f75da60444fcc4a43ff5f3` |
| [platform/external/bazelbuild-rules_shell](https://android.googlesource.com/platform/external/bazelbuild-rules_shell/+/32f339bedfd8d37f33d4f0790fbad66b9829dbc9) | `32f339bedfd8d37f33d4f0790fbad66b9829dbc9` |
| [platform/external/bazelbuild-platforms](https://android.googlesource.com/platform/external/bazelbuild-platforms/+/41b8b91d2eab15a3573b740358dd4b1b3f7d5097) | `41b8b91d2eab15a3573b740358dd4b1b3f7d5097` |
| [platform/external/compiler-rt](https://android.googlesource.com/platform/external/compiler-rt/+/fca7d4641819e50d89374a1dadb615bd8991ebf4) | `fca7d4641819e50d89374a1dadb615bd8991ebf4` |
| [platform/external/dtc](https://android.googlesource.com/platform/external/dtc/+/6ab7e35a241f6b1513c4701c66fe479ab040eafb) | `6ab7e35a241f6b1513c4701c66fe479ab040eafb` |
| [platform/external/kmod](https://android.googlesource.com/platform/external/kmod/+/dda7839f3e2d13e1cc241e2fee020452552f88d2) | `dda7839f3e2d13e1cc241e2fee020452552f88d2` |
| [platform/external/lz4](https://android.googlesource.com/platform/external/lz4/+/6fa8b6928ae968ef70ea1d7b8a94b6fc4ed638a5) | `6fa8b6928ae968ef70ea1d7b8a94b6fc4ed638a5` |
| [platform/external/pigz](https://android.googlesource.com/platform/external/pigz/+/9bc9fa17d499ddde88b77820f6d063e16c0cdd42) | `9bc9fa17d499ddde88b77820f6d063e16c0cdd42` |
| [platform/external/python/absl-py](https://android.googlesource.com/platform/external/python/absl-py/+/5b421cafc7c99c63c8c5221f6d256dde1c27087b) | `5b421cafc7c99c63c8c5221f6d256dde1c27087b` |
| [platform/external/toybox](https://android.googlesource.com/platform/external/toybox/+/f0ccff13b546eab589b926eec9e2c0a2898c5473) | `f0ccff13b546eab589b926eec9e2c0a2898c5473` |
| [platform/external/zlib](https://android.googlesource.com/platform/external/zlib/+/7089b1ed7711800ae5a8a69e11ab1b447e0edaa5) | `7089b1ed7711800ae5a8a69e11ab1b447e0edaa5` |
| [platform/external/zopfli](https://android.googlesource.com/platform/external/zopfli/+/feec88f5d5e2b9ab0c0c3ae1e4ed543f105426aa) | `feec88f5d5e2b9ab0c0c3ae1e4ed543f105426aa` |
| [platform/external/zstd](https://android.googlesource.com/platform/external/zstd/+/f31aa294448119d34b5678a2949899a2f89da084) | `f31aa294448119d34b5678a2949899a2f89da084` |
| [platform/external/u-boot](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59) | `3fe9647575890b846172e546201eff7614c8cb59` |
| [platform/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9](https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/+/083aa5efe67a40d8c300bfd02293659341975042) | `083aa5efe67a40d8c300bfd02293659341975042` |
| [platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9](https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9/+/8da8c8e22d3b4ce7ba8b432eb3870739ea58c72f) | `8da8c8e22d3b4ce7ba8b432eb3870739ea58c72f` |
| [platform/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.17-4.8](https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.17-4.8/+/cd42c5fe8fe7db6c3247b53c6560fd0ae065cb20) | `cd42c5fe8fe7db6c3247b53c6560fd0ae065cb20` |
| [platform/prebuilts/gcc/linux-x86/x86/x86_64-linux-android-4.9](https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/x86/x86_64-linux-android-4.9/+/317f01f3deebab8f1e0630e7bd905209e1e4e6b6) | `317f01f3deebab8f1e0630e7bd905209e1e4e6b6` |
| [platform/prebuilts/build-tools](https://android.googlesource.com/platform/prebuilts/build-tools/+/cc697f4ee06fa1d564c6fdcbf0fa2159deb1440d) | `cc697f4ee06fa1d564c6fdcbf0fa2159deb1440d` |
| [kernel/prebuilts/build-tools](https://android.googlesource.com/kernel/prebuilts/build-tools/+/7a6eb02373935c2c60846e79c2d66f5f5bd56d85) | `7a6eb02373935c2c60846e79c2d66f5f5bd56d85` |
| [platform/prebuilts/clang/host/linux-x86](https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/+/b5f16aee7b8af4c339972027e91e7e793c2e55d9) | `b5f16aee7b8af4c339972027e91e7e793c2e55d9` |
| [kernel/manifest](https://android.googlesource.com/kernel/manifest/+/62a75c3e72e6f7990b361898b48017b42fd9f236) | `62a75c3e72e6f7990b361898b48017b42fd9f236` |

## Retrieved immutable text sources

Gitiles TEXT responses were base64-decoded without newline normalization and
SHA-256 hashed. The table hashes were independently recomputed from retained
bytes. P1/P2/P3 denote module/license/map; U-build, U-config, U-entry, U-env,
U-boot, U-image, U-avb and U-lock group the actual source contracts cited in the
assessment. T identifies compiler-source metadata. R-source rows are supporting
reads, not an adopted transitive dependency audit.

| Group | Immutable source file | Retrieved-byte SHA-256 |
|---|---|---|
| U-build | [platform/external/u-boot: BUILD.bazel](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/BUILD.bazel) | `e283c416a7767844bdf7e1ba6cb32fe9f4281d20ce1dbcb79a2608c99394b6f5` |
| U-build | [platform/external/u-boot: build.config.qemu.aarch64](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/build.config.qemu.aarch64) | `ec42510727be218802016013e928f3443a62e44f2070f785e122ae2beaa32704` |
| U-build | [platform/external/u-boot: build.config.common](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/build.config.common) | `f72888137ecb2954ae832eb4e58b911f0dac2ca550dc4e07316a664ad46452c1` |
| U-config | [platform/external/u-boot: cuttlefish.fragment](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/cuttlefish.fragment) | `437c203cb04497360a1e8f270f0314fed35e73e54206d851e3bbc521998c6adc` |
| U-config | [platform/external/u-boot: configs/qemu_arm64_defconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/configs/qemu_arm64_defconfig) | `4d48287b840d9019c0b27c30c5cf6935c3737105dc80b695b3a7d97a65c5b0a3` |
| U-entry | [platform/external/u-boot: include/configs/qemu-arm.h](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/include/configs/qemu-arm.h) | `0546d4dcc751a7cd36e2946cef745059fd389a5efcd94218a94b0177d3c2542c` |
| U-entry | [platform/external/u-boot: board/emulation/qemu-arm/qemu-arm.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/board/emulation/qemu-arm/qemu-arm.c) | `451843b4a6f2a9ba337d855323c836e0192362f541c63dec1567a1e33bfba8a1` |
| U-boot | [platform/external/u-boot: cmd/boot_android.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/cmd/boot_android.c) | `9c723cced51c3be42e7dee8d938f78dd6edb2f05ceb7ed5f12427ae2544fda60` |
| U-build | [platform/external/u-boot: build.config.constants](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/build.config.constants) | `4ea3593449f595811572ead402d97eb0bec85a1a57a688e5c9cb8d3d88bafd0a` |
| U-build | [platform/external/u-boot: build.config.aarch64](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/build.config.aarch64) | `2d271a902a25ab6fdc1f40511b7f07949ea3cacee2943d84b8b915ad724e7759` |
| U-config | [platform/external/u-boot: qemu-minimal.fragment](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/qemu-minimal.fragment) | `86bce1dc62bfc376e4f7b9702cabc2334fa1da3450a31c25932fcaf5cd6236d2` |
| U-config | [platform/external/u-boot: arm.fragment](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/arm.fragment) | `c264de430f2b373dd0efe14f910465d6be9f3ff74c73bff8ae89028cfa1888c7` |
| U-env | [platform/external/u-boot: default_env.txt](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/default_env.txt) | `eab9500f90d0ee8a80e5b47e38fc29b2074bb8cf3a782fdbbb4c7d05c2bb1280` |
| U-boot | [platform/external/u-boot: boot/android_bootloader.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/boot/android_bootloader.c) | `bb62884aa6153270fa6250bcc2daee74aa6cacbb1c0960c34591aebb29001689` |
| R-source | [platform/external/u-boot: Licenses/README](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/Licenses/README) | `79feed9f3865276aa9acb7fdc5ea2aba63d2f2502eda0327c10af03c8f639db2` |
| U-build | [kernel/build: gki/download_from_ci](https://android.googlesource.com/kernel/build/+/b6b2ec88ae2ef29b031db9f8e63cd91c4d7c7882/gki/download_from_ci) | `a992f9e086f24fc65e5dafc3fdc7281eec5de0f8903be99404031b0e64d0cef9` |
| U-avb | [platform/external/u-boot: common/avb_verify.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/common/avb_verify.c) | `17662d82919f8dd49b1c8d9f94069b8dcd5d92170dc9c02f57069e6cbdae3c3b` |
| U-env | [platform/external/u-boot: cmd/nvedit.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/cmd/nvedit.c) | `b8348b97c7c5eec978e35b1b0ade76ec21715d1bf2dd94768d67b0392125f5f0` |
| U-lock | [platform/external/u-boot: boot/android_bootloader_oemlock.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/boot/android_bootloader_oemlock.c) | `57ccc4eb6731723a24d65c5882d4b51566717acea6578a68c5360a830ee5d4f3` |
| U-image | [platform/external/u-boot: boot/image-android.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/boot/image-android.c) | `a06c4489e51cf6939971c974b82c5db9babd709a8d912816f355d46121e289c6` |
| U-entry | [platform/external/u-boot: arch/arm/mach-qemu/Kconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/arch/arm/mach-qemu/Kconfig) | `23c753e141324eb54b6febfef79456d7f5ab0896b1179a0c04c7cc420c7e861b` |
| R-source | [platform/external/u-boot: Licenses/gpl-2.0.txt](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/Licenses/gpl-2.0.txt) | `8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643` |
| P1 | [device/google/cuttlefish_prebuilts: bootloader/Android.bp](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/36f427b7c46682cfcdb2e61eee6893acbfb2a606/bootloader/Android.bp) | `f380f7cbec4c4823a4b20ddcc49590dfd496bc1d9843b085472d5deab18adb29` |
| P2 | [device/google/cuttlefish_prebuilts: bootloader/LICENSE](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/36f427b7c46682cfcdb2e61eee6893acbfb2a606/bootloader/LICENSE) | `7e354ab349b7c11f1fe93639c3096bfe2bb4591659caaa712e2ee101299cf1d4` |
| P3 | [device/google/cuttlefish_prebuilts: bootloader/qemu_aarch64/System.map](https://android.googlesource.com/device/google/cuttlefish_prebuilts/+/36f427b7c46682cfcdb2e61eee6893acbfb2a606/bootloader/qemu_aarch64/System.map) | `b3de55bd712e450ae9a1819f98a54fde2e3fe418c8a974bc405956c49ddc6002` |
| U-entry | [platform/external/u-boot: arch/arm/lib/bootm.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/arch/arm/lib/bootm.c) | `fb327db986fc096f512d869975cf536adeae7a91e18b8731f3aabf025c29e9d1` |
| R-source | [platform/external/u-boot: env/Kconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/env/Kconfig) | `b040d7f9f17aed51954a429833640a87beab17900ae982cc62e0bc98b20e7c4c` |
| U-avb | [platform/external/u-boot: cmd/avb.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/cmd/avb.c) | `eec4f249359bb24a85ccbaeec690e87b8b4dc6f8c4e6844c991de4b30f90e809` |
| U-avb | [platform/external/u-boot: lib/libavb/avb_slot_verify.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/lib/libavb/avb_slot_verify.c) | `d5eff9321e3fa0e98de9a78ea276dec2f8341ba7405300060a45f4757ca765fb` |
| R-source | [platform/external/u-boot: lib/libavb/avb_sysdeps_posix.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/lib/libavb/avb_sysdeps_posix.c) | `7ff411616a6b5f2dcca767e21c57cb3b15dd25e4c16e5dbe713e39c885325dfa` |
| U-lock | [device/google/cuttlefish: host/commands/run_cvd/launch/secure_env.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/secure_env.cpp) | `cc153e140e49854c9fb667b5a9deb13a493251910a473ebcd43e933f0144a600` |
| R-source | [platform/external/u-boot: lib/Kconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/lib/Kconfig) | `5ff2da5c8ad8c5b136d11f4e2c63f561c6d07b7eef935caa2ab97b2e69f69e17` |
| U-lock | [platform/external/u-boot: boot/android_bootloader_transport.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/boot/android_bootloader_transport.c) | `8be56a807bfba72d271770c8afe344566a37704d70700a77bb067d72db7962d2` |
| U-entry | [platform/external/u-boot: arch/arm/cpu/armv8/start.S](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/arch/arm/cpu/armv8/start.S) | `f6a909c87e6db70ef1748c2b62e2c4514b78a8d071d5fe9abd7c99d9d34987f5` |
| U-config | [platform/external/u-boot: drivers/tee/Kconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/drivers/tee/Kconfig) | `62d995ce94c117bf4a10b822aab2313b96bf6f0b07432db85d9ac5e26059b79c` |
| R-source | [platform/external/u-boot: common/Kconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/common/Kconfig) | `889741271651b2d0b4bb52a8a210c694eafd91900b3f712d9b8cf97c5fb1d3a6` |
| U-lock | [device/google/cuttlefish: host/commands/secure_env/oemlock/oemlock.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/secure_env/oemlock/oemlock.cpp) | `e370176bf24981957c53b9abaef96206b6ccec76dfeb4610119fa07685cb7162` |
| U-lock | [device/google/cuttlefish: host/commands/secure_env/oemlock/oemlock_responder.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/secure_env/oemlock/oemlock_responder.cpp) | `807607917676905cd37f4a18f599cb34ad3ec7521bb94eabd74d9b1db0c09dc8` |
| U-lock | [device/google/cuttlefish: host/commands/secure_env/secure_env_not_windows_main.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/secure_env/secure_env_not_windows_main.cpp) | `f857332d642fc2245446c86302ef7d65782ac38dbc89685a43999e4efaf21275` |
| R-source | [platform/external/u-boot: cmd/Kconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/cmd/Kconfig) | `fdc9d5d70474733b6ccb96b235fbb57036251f2e7bc9d621bfd52fd9411bf2ef` |
| U-config | [platform/external/u-boot: drivers/tee/optee/Kconfig](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/drivers/tee/optee/Kconfig) | `13a4c5928702ec7e9378fa57b750ec44f645151bf58909dec934ea4deb9cb719` |
| T | [platform/prebuilts/clang/host/linux-x86: clang-r584948/AndroidVersion.txt](https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/+/b5f16aee7b8af4c339972027e91e7e793c2e55d9/clang-r584948/AndroidVersion.txt) | `806a5e0cdfc35398f74653f45276554f4f3dd3b1575ff76d900cd9ddadec155c` |
| T | [platform/prebuilts/clang/host/linux-x86: clang-r584948/clang_source_info.md](https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/+/b5f16aee7b8af4c339972027e91e7e793c2e55d9/clang-r584948/clang_source_info.md) | `892504643453bafbe27c976ca5cea2e21b88577d990569c47e90e4ba8c0ec321` |
| T | [platform/prebuilts/clang/host/linux-x86: clang-r584948/manifest_14488419.xml](https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/+/b5f16aee7b8af4c339972027e91e7e793c2e55d9/clang-r584948/manifest_14488419.xml) | `d7cd7c7b07ef3e6a25890c228493ba27e83ec2b962d8561ca55ce94c03237662` |

## C and Q: retained immutable reference contracts

C refers to the complete [PR #24 source ledger](gate-0-android17-boot-hal-sources.md)
and [PR #23 ledger](gate-0-complete-android-sources.md), with their original
immutable URLs and hashes. Retained bytes were rehashed for the Cuttlefish files
used here: QEMU manager, flags/defaults, secure-HAL mapping, boot_config,
bootconfig_args, persistent bootconfig/vbmeta and composite disk generators,
shared BoardConfig/fstab, ARM64 product/board/bootloader, and first-stage init.
New OEM-lock/secure_env source reads appear above. No historical record is
rewritten to claim that its earlier Unknown was already resolved.

Q uses the existing clean QEMU checkout at
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`. Exact Git blob reads of
[virt.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c),
[boot.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c),
[loader.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/loader.c)
and [device_tree.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/device_tree.c)
retain the prior [ARM64 source audit](gate-0-arm64-boot-plan.md) and
[integration limits](gate-0-qemu-worker-integration.md). No claim is made that
this research QEMU binary equals the Cuttlefish host-distribution binary.

## Retrieval failures, validation and excluded claims

Initial CLI network calls were sandbox-blocked; authorized escalated reads and
the connector supplied live preflight. Branch creation initially hit the
read-only Git-index boundary; the authorized retry succeeded. No automatic
approval rejection, security-policy change or bypass occurred. GitHub CLI
initially refused terminal escapes in a log; the read-only escape-enabled query
and bounded receipt extraction supplied the actual log review.

AOSP history returned a CAPTCHA block; browser access to that history and a
directory failed. No challenge was bypassed. Ordinary immutable commit/file
metadata supplied the snapshot/import chain. Trailing-slash directory requests
returned 503; the normal directory object URL succeeded. Guessed
`lib/avb/avb_ops.c`, `lib/libavb/Kconfig`, `lib/libavb/README`, board-local
`lowlevel_init.S` and top-level secure_env OEM-lock/main paths returned 404.
Tree discovery located the actual `common/avb_verify.c`, TEE Kconfig,
ARMv8 startup and nested OEM-lock files. A transient `lib/Kconfig` 503 was followed
by a successful source read. None of these failures proves source absence.
The moving main U-Boot metadata and search-discovered build recipes were only
discovery leads; the final analysis uses the build-resolved immutable source.

A temporary standard-library text-record checker compared independent published
inventories and hashes, not this hand-authored matrix. Its first run stopped on
the non-Git container material; the corrected parser explicitly checks that
SHA-256 material separately and the XML's separately recorded manifest project.
Final result: 32 XML projects plus kernel/manifest agree across four records;
container digest and five retrieved-text subject hashes agree; snapshot/import
tree and selected Git blob metadata agree. Wrong QEMU/crosvm target, changed
source revision and changed subject digest were each rejected. These synthetic
mutations test the consistency checker, not firmware boot or AVB enforcement.
The temporary helper remains ignored; no recurring CI oracle or dependency was
added for this one-off source comparison.

Local foundation validation passed (108 files, 64 Markdown files, 54 requirements,
two ADRs); harness-authority validation passed. Repository regressions ran 141
tests: 137 passed and four expected Windows/platform checks were skipped
(Linux C execution, symlink and file-mode coverage), with no failures. These
skips are not Linux or Android runtime passes.

All 44 newly recorded immutable source files were rehashed. All 65 retained
boot/HAL source records and the retained first-stage init record matched their
recorded SHA-256 values. Four QEMU files were read as exact pinned Git blobs;
the retained checkout was clean. Relative documentation links resolved. Source
URLs and build records were checked during retrieval; no moving branch is used
as final source identity. Public-data review found no credentials, private keys,
internal build-service paths or local-machine paths in the proposed documents.
Whitespace, complete three-file diff and regular file modes were reviewed.

A final hash-check invocation initially hit the Windows Store Python alias and
did not execute; native PowerShell hashing completed those checks. A Windows
wildcard path passed directly to ripgrep also failed; its supported glob option
completed that read. Neither failure is counted as a successful validation.
Immediately before publication, live main still matched the baseline, PR #25's
merge actor was confirmed as `innercoder78`, and the open-PR inventory was empty.

No firmware compilation/reproduction, complete guest build, downloaded image,
APK build/install, Android runtime, phone/ADB, Linux native control execution,
new QEMU build, signing-key acquisition or security-policy change ran locally.
No absent check is counted as a pass. Source signature verification, final
configuration reproduction, full transitive license/security-history review and
exact executable-byte correspondence remain unexecuted/Unknown.

Publication is one focused three-file documentation PR. The roadmap is unchanged.
Hosted checks for the new head remain **pending/unobserved at publication**.
After one immediate PR identity and native conversation-attachment metadata
check, stop without polling CI, reviews, comments, bots or mergeability.
