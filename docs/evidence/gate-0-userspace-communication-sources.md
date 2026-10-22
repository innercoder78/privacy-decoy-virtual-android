# Userspace communication source ledger

Companion to [the assessment](gate-0-userspace-communication.md).
Review date: **2026-10-22, America/Fortaleza**. Source inspection on Windows
x86_64 only. Gate 0 **Unresolved**; Gates A–G **Not reached**.

## Live preflight and preservation

Canonical remote fetch and independent `git ls-remote` verified main
`b25ebeae0b8e0db06903f65a3e5831b765459191`, matching the supplied baseline.
The GitHub connector's repository-scoped open-PR search returned an empty list;
there were no open heads/bases, diffs/files, checks/jobs, reviews, comments or
unresolved threads to reconcile. This is not a claim about closed PRs or fresh
exact-main CI success. Registered workflow definitions, pins, permissions and
path filters were inspected locally. No hosted checks were polled.

[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
**Partially Degraded Service**, update `2026-10-22T17:16:06.227Z`.
The initial sandbox fetch failed (Git metadata write/network access); the approved
retry succeeded. Source retrieval similarly required approved network access.
These failures did not produce source findings or change security settings.

Initial tracked tree was clean on main, one registered worktree, no stashes.
Existing local/remote branches and ignored build/Gradle/CMake/cache assets were
preserved. No applicable AGENTS.md was found. Tracked entries were regular
100644 files; the focused change introduces only Markdown. The historical
repository was not modified. A durable ignored private progress/source receipt
record records intent, results, recovery and next operations; none is published.

Governing inputs: actual ADR-0001 Accepted and ADR-0002 Proposed, requirements,
feasibility gates, security boundaries, roadmap and source-provenance policy.
Evidence inputs include complete Android 17, boot/HAL and their source ledgers,
QEMU worker integration, process seccomp, worker containment, capability
revocation, U-Boot and dormant Android bootstrap findings. Existing QEMU recipe,
source/toolchain pins and dependency records retain their earlier adoption scope.
No preexisting guest/backend/native research binary is re-attested or executed.
Validation uses the already available NDK-bundled Python interpreter.

## Identity and method

C = `device/google/cuttlefish` at
`283645aacf6cdb56cc31a9362f54d412dbc132a1`.
G = `device/generic/goldfish` at
`296e55aa0244e8929e393e00e34471fef2a5d662`.
V = `platform/external/rust/crates/vhost-device-vsock` at
`28233ae213b24a9a35f25e9e49bcadee2bf93821`.
D = `platform/external/rust/android-crates-io` at
`1f5e95cd6e996995023c9c0f7df0f15a8a43269e`.
Q = `qemu/qemu` at `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`.
M = `platform/manifest` at `5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f`.
S = `platform/system/sepolicy` at
`e066568e98d86db31a9346d30977f3632fa7073c`.

G and D were resolved from `android-17.0.0_r1` commit metadata, then retrieved by
immutable SHA. Other pins match the prior PDVA ledgers. Gitiles file TEXT was
base64-decoded to bytes; QEMU files used immutable raw GitHub URLs. SHA-256s below
were recomputed from saved bytes. Directory JSON was used to discover actual
paths; it is not build or runtime proof. No source code is copied into runtime.

The release manifest, rather than guessed standalone crate repository names,
locates D. `libvhost_user_backend`, `libvm_memory_android` and `libvhost_android`
module names connect V's Soong build to D. This is a source build-graph trace,
not a completed build or artifact correspondence certificate. D's host backend
0.17.0 and vm-memory 0.16.2 must not be equated with V Cargo's 0.10/0.12 ranges.
No newly resolved full transitive lockfile, linker map, Android/Bionic build,
installed executable or complete guest product is claimed.

## Retrieved source bytes

Each row is an immutable source reference and a text-byte hash, never a binary
attestation. Family identifiers above scope the assessment's citations.

| Immutable source | SHA-256 |
|---|---|
| [src/main.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/main.rs) | `ec96c3c5bab617b04531b261f23bdb253de733355361ed97f6e0cc63dce8d45f` |
| [src/vhu_vsock.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/vhu_vsock.rs) | `5052a4deb6f2cc34d6715e19f86db737f52738af08ecee55c4f9fb2daba16e27` |
| [src/thread_backend.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/thread_backend.rs) | `42aea2cc67d1874716fcb8f918d29da39c4f2832c8a9e3ba5ca732f46780be1b` |
| [src/vhu_vsock_thread.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/vhu_vsock_thread.rs) | `13d4d8beb2bffcb4bc8c7b369503467c6c7a1ad15d486db57ffd901b142d7074` |
| [src/vsock_conn.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/vsock_conn.rs) | `d856ec756ff3681410e9bd438d48a3946c330d6b41dafe898ed03070f4aa6821` |
| [Cargo.toml](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/Cargo.toml) | `9be6642f2fe16fd4ea4577793e36b12202e86a2e68672b19b46d2f28e27e16b0` |
| [README.md](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/README.md) | `588ac459957641b4d75ba0d96be8d5e1849be50bc8deb6fcb79866ee1fb72e52` |
| [common/libs/fs/shared_fd.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/common/libs/fs/shared_fd.cpp) | `7b14de57239c6d7383e96b6420acdeec841a04d6862fa3208da164932e633d1e` |
| [host/commands/run_cvd/launch/vhost_device_vsock.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/vhost_device_vsock.cpp) | `b34c77e9f23928d82f2d74e88937cfcdaa13f62fbdb3b49edc42336be14ea183` |
| [host/commands/assemble_cvd/bootconfig_args.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/bootconfig_args.cpp) | `64a5a2be99fa76080a16c45ba38831c264472ff3d882aa4bb9d79eb687d62117` |
| [shared/device.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/device.mk) | `cfd71dfa943e83cb96d64f9cd8e1e1331b2fedca8719b37e1eed372b44876355` |
| [shared/config/init.vendor.rc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/init.vendor.rc) | `cef836b44936042d1c71561db0d9064f2613ec19da594ab68c1ceeb0fe181033` |
| [Android.bp](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/Android.bp) | `05cdeeb7f85109f4a9ca4039ed7e383ccb98fecde2c99e9773fb226c3294ec8a` |
| [host/commands/run_cvd/launch/streamer.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/streamer.cpp) | `f748cce3b7402e07aac47abb4f1568d7a458ed4db8ed3ddd833fcd7b025d0bbe` |
| [host/commands/run_cvd/launch/tombstone_receiver.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/tombstone_receiver.cpp) | `d7546b2799390d08da28e73c1a936761dd6d27497791d7cbc804af98c9488b0a` |
| [host/commands/run_cvd/launch/modem.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/modem.cpp) | `a786ea3697c43399b0e835d9d9e9b9fb2cb48d929c74cc1be02497f7353ec113` |
| [host/commands/run_cvd/launch/control_env_proxy_server.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/control_env_proxy_server.cpp) | `4a61d61aa4de0d163ba21670a2597cd356f6f62b1dd18d9a8b65e8a78668ab78` |
| [guest/hals/light/main.rs](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/light/main.rs) | `7b409bb3994ccd467d5ef884c42dc7131e18fa4d8970248bc17e9774ebeaa67f` |
| [guest/hals/light/lights.rs](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/light/lights.rs) | `a602857727a92e84ec36d8a1c9d77c72c69bcf93ea0beb8dbeb26fd4facb1be3` |
| [guest/hals/camera/vsock_camera_server.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/camera/vsock_camera_server.cpp) | `cdf782a4c8088311e3ef772b6e04af94f5ae6367f6f71d73e3f87b0ee20b4462` |
| [guest/hals/camera/vsock_camera_provider_2_7.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/camera/vsock_camera_provider_2_7.cpp) | `35bbcd0416bd6e38a1c7a324ea96f40e221482d4e28b693db53430106e8a3b16` |
| [shared/telephony/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/telephony/device_vendor.mk) | `8e5f7480bdf713649614dce3335b76d1b47f5fc9cec138a5fa7c4ac475fe7b43` |
| [hw_virtio_vhost-user-vsock.c](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/vhost-user-vsock.c) | `852c7f3df0c8cb0fa0f5df6c9ed5f6c7d431d6778409799c2791ea3b1a01ff64` |
| [hw_virtio_vhost-user.c](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/vhost-user.c) | `8ff3ae4c8d4b4fce2f210f27a2ab58722e1e4de7ec6699659e852656943720a9` |
| [docs_interop_vhost-user.rst](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/docs/interop/vhost-user.rst) | `6350c5fe2425be9028519050d164cbee7d277fa199959efe48e5ec859b74d787` |
| [guest/hals/light/lights/lights_vsock_server.rs](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/hals/light/lights/lights_vsock_server.rs) | `3e2ee335967cb1fa58b890f87a1e95dce8ab38cacce7cf1b3ec04da972516f38` |
| [apex/com.google.cf.rild/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/apex/com.google.cf.rild/Android.bp) | `1d9e868739afff9b3d82ef6d447bafbf3be1fa8a191ff3695ccd89622acd5c4d` |
| [guest/monitoring/tombstone_transmit/tombstone_transmit.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/monitoring/tombstone_transmit/tombstone_transmit.cpp) | `d42f1912cb1da7d13a43c774d2dab5f4ae0af87137c0079ee0e58226cae81f10` |
| [guest/monitoring/tombstone_transmit/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/guest/monitoring/tombstone_transmit/Android.bp) | `986a2b9bac16d6839c16d1a1445b4201827041ba31d051108444566dc2076910` |
| [default.xml](https://android.googlesource.com/platform/manifest/+/5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f/default.xml) | `76ef74339da1e0c973d1ec7cb92045e823223a7724d9aa453b4cab4e246122c4` |
| [private/isolated_app_all.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te) | `e65adb199d7fc26cd716f4e376f6068edcd3c350647f121e8d5937fa9bca4ad9` |
| [private/app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te) | `6a18ae176e35cf19ab022cc75887a5c77aae55f00e8a1ebddd7ebd75aea64525` |
| [private/isolated_app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app.te) | `a088dfeaf2dabbfcd4327c01549096c88db22687c2fceb51c797ede552bb2d51` |
| [hals/radio/AtChannel.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/radio/AtChannel.cpp) | `df0b156952b4f41a9f97a3b74de7113726700cd550f57718b360bd38fa5f4a33` |
| [hals/radio/Android.bp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/radio/Android.bp) | `ddbcef89fdab47bb41e89ed9a0e827f06660f3ee0e0c13fd0d145cb31e5d955f` |
| [hals/radio/main.cpp](https://android.googlesource.com/device/generic/goldfish/+/296e55aa0244e8929e393e00e34471fef2a5d662/hals/radio/main.cpp) | `6f1a94ab47996fa119fc5561a8075b21c4e4f2d5201752645f5c143714355a38` |
| [crates/vhost-user-backend/src/handler.rs](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost-user-backend/src/handler.rs) | `4971aa35ea16f5dd0d3fec5b8233e8d3f5020faf7f7b2ae9f454c342a3d167e1` |
| [crates/vhost-user-backend/src/lib.rs](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost-user-backend/src/lib.rs) | `d289603d79044227dd9b9d2c6302372126498b1c5c149ac0e808ffa96b1244b0` |
| [crates/vhost-user-backend/Android.bp](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost-user-backend/Android.bp) | `833f637f07c73a17b02f134d34098909b812cbaadacca310fb444a8b9a04e7a4` |
| [crates/vm-memory/src/mmap_unix.rs](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vm-memory/src/mmap_unix.rs) | `f6aa6869492c476936124f926afa6a0d3a30c747e7f14343a69f99c8cee952e3` |
| [crates/vm-memory/Android.bp](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vm-memory/Android.bp) | `7d56df517c4783f44b2d68343fb6e61f812bb69fd625af96620970b2cd55974f` |
| [crates/vhost/Android.bp](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost/Android.bp) | `1fc24e6c1093d11dbd135710dc79e29b5523447776480d52fa7e9df8a0645527` |
| [crates/vhost/src/vhost_user/message.rs](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost/src/vhost_user/message.rs) | `b58886ab563c1e198c7a9e04fbbcaff74d5dc4b6ae7e1aa67a5963641141bd03` |
| [shared/phone/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk) | `69645517941d7013eb798376faeee588cc86f9bfd117dd5eecd27b250b6ad176` |
| [shared/camera/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/camera/device_vendor.mk) | `be79a83891bb678d4678c61077b20d9c6e3d9015b4dc353c6997deda42441093` |
| [host/commands/assemble_cvd/flags_defaults.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags_defaults.h) | `c2f95f666070036d10c9160d11fcc080a864c4df3da60d98747bdadfcb5f310a` |
| [host/libs/vm_manager/qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` |

## Rights, build and TCB limits

C/G inspected source uses Apache-2.0 notices. V declares Apache-2.0 OR BSD-3-Clause;
its generated Android module chooses Apache-2.0. D's inspected Soong modules
identify Apache-2.0 and host-only builds; file-specific and transitive obligations
remain to be qualified. QEMU's vsock device has GPL-2.0-or-later terms; existing
QEMU/GLib/static-link and corresponding-source obligations are unchanged. These
are source-license observations, not legal or distribution approval.

The new source graph includes backend, vhost, vm-memory, virtio queues/bindings,
vmm-sys-util, epoll, CLI/config/serde/logging and Rust/native runtime dependencies.
Only the decisive source paths are inspected; a complete build/license/security
history and maintenance adoption review remains required. A backend trusted with
all shared guest RAM cannot be described as a narrow management message parser.
Separate trusted service adapters add their own parsers and lifetime authority.
No new runtime dependency, binary, build tool or service was adopted.

## Retrieval limits and negative controls

A transient 503 interrupted initial Cargo retrieval; retry obtained its prior
ledger hash. Android.bp retrieval initially failed and later matched its prior
hash. Guessed separate crate repositories did not resolve at the release tag
(the backend query explicitly returned 404); the actual manifest led to D.
Guessed tombstone `main.cpp` and `.rc`, and `shared/lights/device_vendor.mk`, failed;
actual tombstone paths were discovered from directory JSON and light selection
was found in shared/device.mk. None of these failed URLs proves feature absence.

Manual code-grounded negative controls: TCG plus unchanged kernel vhost is not
userspace-vsock; a host-library ARM64 target is not an Android app binary;
standalone Cargo ranges are not the selected Soong graph; a read-only FD cannot
satisfy the selected shared writable RAM map; getuid-derived names are not a
cross-isolated-UID endpoint contract; failed connect does not execute an
implemented reset in the TODO path; a loop/restarter does not enforce session
loss; missing camera host settings is not a working external camera; a lights
console TODO is not an alternate transport; closing an FD is not map revocation.
These observations were checked against the cited code, not encoded in tests
that merely assert a hand-authored table.

## Validation

Local checks used the existing NDK-bundled Python 3.11 interpreter:

- Foundation passed: 120 files, 69 Markdown files, 54 requirements, two ADRs.
- Harness manifest/source authority validation passed; no Android execution.
- Repository regression suite: 141 tests, 137 passed and four existing Windows
  skips. Skips are not passes or Linux execution evidence.
- Desktop readiness/journal suite: 27 tests passed, including rejection controls.
- Offline image-inspection suite: 45 tests passed on synthetic fixtures.
- All 47 unique retrieved text-source hashes were recomputed and matched the
  receipt ledger; all corresponding URLs contain immutable 40-hex revisions.
- Complete three-file diff, regular 100644 modes, whitespace, Markdown targets,
  public-data hygiene and unchanged runtime/dependency/workflow scope reviewed.

No new build,
guest/backend execution, native Linux control or physical Android result is
claimed. Publication-time hosted CI is **pending/unobserved**. After publication,
check the intended PR branch/head/base and native chat attachment once, then stop
without polling Actions, bots, checks, reviews, comments or mergeability.
