# Gate 0 user-space VMM source research

**Research date: 2026-10-07. Gate 0: Unresolved. A–G: Not reached.**
No engine is selected. No code, runtime, dependency, image or binary is adopted.
This record supports the [candidate hypotheses](gate-0-userspace-vmm-candidate.md)
and [next physical experiment](gate-0-isolated-qemu-proof.md), not a security claim.

## Method, scope and repository preflight

Question: is full-system ARM64 software emulation a credible ordinary-app mechanism
worth testing with a separate isolated UID? Relevant obligations: PDVA-REQ-002,
PDVA-REQ-003, PDVA-REQ-006 through PDVA-REQ-015, PDVA-REQ-036 through PDVA-REQ-045.
Method: read-only GitHub API/raw source, official Gitiles refs/TEXT, upstream and
Android documentation. Source observations below are distinct from upstream claims
and PDVA hypotheses. No APK, VM, emulator or physical device was executed; host
Android, OEM, ABI and release-equivalent runtime observations are **not applicable**
to this documentary review and remain **Unknown** for PDVA. Positive/negative
runtime controls are specified in the experiment, not reported as performed.

Before editing, canonical `main` independently resolved to
`6ee428a90aee57409ca1db945c4ff671450cf5e2`. All open PRs: zero, so per-open-PR
head/base/diff/files/checks/statuses/reviews/comments/unresolved-thread inspection
had no subjects. The exact-main [PDVA foundation run](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/37569094968)
was completed/success; its `foundation` check was successful. Combined status had
zero contexts (its aggregate `pending` was not an extra pending check). The only
registered workflow was active `.github/workflows/foundation.yml`; its exact-head
checkout, read-only permissions and validation were inspected and are unchanged.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
`All Systems Operational`, indicator `none`, with page update
`2026-10-07T17:27:12.671Z` at retrieval. This is preflight, not post-publication CI.

The clean local bootstrap branch had the same content as verified main and was
preserved; the research branch starts at that exact main commit. There was one
worktree and no stashes. Tracked inventory: 33 regular `100644` files, no submodules,
symlinks, LFS pointers, runtime dependency declarations or binary/image artifacts;
`android/` contained only `README.md`. The sole external CI action is the existing
reviewed checkout pin. Requirements, governance, gates, evidence, source policy,
architecture, privacy/network/image contracts and validator were reviewed. No
normative gap requires a requirement change. Historical Privacy-Decoy is read only
and was not modified. No physical execution evidence was produced in this research PR.

## Immutable identities

GitHub default HEADs were resolved through commit APIs; QEMU's GitLab HEAD was
independently compared with its GitHub mirror and matched. These are research
snapshots, **not dependency pins or recommended production releases**. AOSP release
tags were resolved to peeled commits through official Gitiles refs.

| Source | Retrieved identity | Treatment |
|---|---|---|
| [qemu/qemu](https://github.com/qemu/qemu/tree/f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c) | `f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c` | Full-system/TCG, security and resource-interface reference |
| [ExTV/Podroid](https://github.com/ExTV/Podroid/tree/ce0121896b2895637ab1f656cbb0d75fa2874489) | `ce0121896b2895637ab1f656cbb0d75fa2874489` | Executable-packaging reference |
| [rhn-1k/QubeVM](https://github.com/rhn-1k/QubeVM/tree/f860230c179e1cc10d5079a31215fa25cb5ad8ad) | `f860230c179e1cc10d5079a31215fa25cb5ad8ad` | JNI/shared-library reference |
| [AI2TH/Linxr](https://github.com/AI2TH/Linxr/tree/6216357b5af9d96defb772c3d06e9218c7d52b81) | `6216357b5af9d96defb772c3d06e9218c7d52b81` | Executable-packaging reference |
| [f-droid/fdroiddata](https://github.com/f-droid/fdroiddata/tree/7a3a14575311f6bbed71c2883050fa08a2644163) | `7a3a14575311f6bbed71c2883050fa08a2644163` | Historical source-build recipe |
| [limboemu/limbo](https://github.com/limboemu/limbo/tree/887c6a68cd6b414377d7f8071bc12bbc16e59809) | `887c6a68cd6b414377d7f8071bc12bbc16e59809` | Default HEAD and v6.0.1-LimboEmulator resolve to this commit |
| [Fiki-io/RootlessAndroid15VM](https://github.com/Fiki-io/RootlessAndroid15VM/tree/455b26da0d274b1d99434c70a98963a47dacdf29) | `455b26da0d274b1d99434c70a98963a47dacdf29` | Shared-host-kernel mediation comparison |
| [Hexadecinull/VineOS](https://github.com/Hexadecinull/VineOS/tree/f72a8ccdc69ea474cc60d4855c836121adbcf273) | `f72a8ccdc69ea474cc60d4855c836121adbcf273` | Namespace/container comparison |
| [jacksonmafra-umain/draugr](https://github.com/jacksonmafra-umain/draugr/tree/ac9cb0aa0fbe52b1a2597f4c8f91a687e909b2ac) | `ac9cb0aa0fbe52b1a2597f4c8f91a687e909b2ac` | WASM/WebView fallback research |
| [copy/v86](https://github.com/copy/v86/tree/6db8b157974dbaf1b54d2c2ec12dd71ddc1891e9) | `6db8b157974dbaf1b54d2c2ec12dd71ddc1891e9` | x86/WASM fallback research |
| AOSP system/sepolicy Android 17 r1 | `e066568e98d86db31a9346d30977f3632fa7073c`; tag object `689b4b99b953ff2c29a2f1b520e9361a7cc7b633` | [S1][S1], [S2][S2], [S3][S3], [S4][S4] |
| AOSP system/sepolicy main | `4571ddd9440721fec583c906a337de949a77749e` | [SM1][SM1], [SM2][SM2], [SM3][SM3] |
| AOSP frameworks/base Android 17 r1 | `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`; tag object `23149ba144e850fe494a91ffa13f8019455c0804` | [Manifest attributes][A1], [Process UID definitions][A2] |
| AOSP device/google/cuttlefish Android 17 r1 | `283645aacf6cdb56cc31a9362f54d412dbc132a1`; tag object `fc81d4d790cf71b00c17dbcb476c9cf05279f3ff` | [QEMU manager][C1], [guest SwiftShader configuration][C2] |

Frameworks/base main also resolved to `1cdfff555f4a21f71ccc978290e2e212e2f8b168`
and Cuttlefish main to `a1162ca7a4e6297f1699b65052a8c2dd466fd518`; behavioral
citations here use their Android 17 release files, not an assumption that moving
main is newer. A guessed `platform/device/google/cuttlefish` path failed; the
correct upstream is `device/google/cuttlefish`. No identity from the failed query
is used. AVF refs were re-resolved and match the existing
[platform-authority record](gate-0-platform-authority.md).

## QEMU: machine implementation, not a TCG security boundary

**Source observations:** [ARM virt documentation][Q2] describes a system machine
with AArch64 CPUs, interrupt controllers and virtio transports. A 64-bit CPU must
be selected explicitly; the documented default is a 32-bit CPU. [Invocation][Q3]
documents TCG, threading, code-cache sizing and split write/execute mappings.
Together these support a full-system ARM64-on-ARM64 software-emulation hypothesis;
they do not prove an Android package, an isolated-process JIT, an Android 17 guest,
or acceptable performance. `aarch64-softmmu` executes a guest kernel and devices;
QEMU user-mode translation alone is not that full-system boundary.

**Upstream security policy:** [security.rst][Q1] excludes TCG's non-virtualization
use case from its supported guest-isolation/security guarantees and security-bug
handling. The hardware-virtualization security policy for selected machines must
not be transferred to TCG just because both use `virt`. PDVA therefore assumes
arbitrary native compromise of the QEMU worker. QEMU/TCG implements the machine;
the proposed post-compromise containment is the host UID/process/SELinux sandbox
and narrow brokers, still unproved. Its emulated devices, parsers and translator
remain attack surface. Upstream also warns about large memory peaks; guest RAM
size alone is not a host memory bound. Optional QEMU sandboxing is defense in
depth, not a demonstrated Android authority substitute.

**Resource mechanisms:** [Q3][Q3] documents `-add-fd` and opening block images via
`/dev/fdset/N`; [QMP definitions][Q4] describe `getfd`, `add-fd`, `remove-fd` and
`query-fdsets`. These are useful pre-opened-resource mechanisms. They do not
establish that every kernel/initrd/firmware/display path accepts FDs on Android,
that QMP is safe to expose to a guest, or that removing an FD set revokes existing
duplicates/mappings. Test every chosen loader and backend. A path-shaped FD-set
reference is not permission to hand the worker a directory or a general file-open
broker. Stock QEMU's command-line program is not a stable Android embedding API;
JNI/shared-library adaptation and exported-function compatibility need review.

**Provenance:** [upstream LICENSE][Q5] describes QEMU overall as GPLv2, with
file-specific licenses and separate firmware licensing. TCG includes permissive
and other licensed parts; extracting that label does not relicense the machine.
Any later experiment needs exact QEMU/patch/dependency/toolchain identities,
file-level notices, build-to-artifact correspondence, security/update ownership
and an adoption decision. This review grants no redistribution conclusion.

## Android packaging precedents: useful mechanisms, different authority

### ExTV/Podroid

**Upstream claim:** [README][P1] describes rootless Alpine/full-kernel operation.
This is not a PDVA physical observation. **Source observations:** [QemuEngine][P2]
launches `ProcessBuilder` with a packaged `libqemu-system-aarch64.so` from
`applicationInfo.nativeLibraryDir`, optionally through its packaged launcher.
It selects `virt`/TCG, uses private image paths, QMP/console sockets and user
networking with forwarding. The `.so` suffix here packages a program for execution;
it is not evidence of a JNI-loaded shared-library service. [Dockerfile][P4]
configures `aarch64-softmmu`, TCG, SLIRP, virtfs and libusb, then copies the QEMU
executable under the native-library name (QEMU version argument `11.0.4`).

[Manifest][P3] requests INTERNET/network state, wake lock, vibration, foreground
special-use service, notifications, boot receive, battery-optimization exemption
and broad/legacy storage. USB support and a Downloads-sharing 9p path expand its
surfaces. The service is non-exported but does not declare `isolatedProcess`;
exported automation and a protected diagnostic provider also require review.
Optional AVF permissions and development-grant instructions are a separate route,
excluded from PDVA's ordinary-app proof. No general no-root claim erases those
optional privileges. [License][P5] contains GPLv2; inspected source headers offer
v2-or-later. Full bundled-file/dependency/firmware rights and reproducibility remain
unreviewed. Do not import its broad sharing, bridge or security comments as PDVA
policy. Source launch logic is credible packaging evidence, not execution proof.

### rhn-1k/QubeVM

**Source observations:** [JNI executor][U2] calls `dlopen` (with a fallback library
path), resolves `qemu_init` using `dlsym`, falls back to `main` for older variants,
and resolves `qemu_main_loop`/`qemu_cleanup` for the modern path. [MachineService][U4]
starts a Java thread that enters the native execution path. The [library manifest][U3]
and [ARM manifest][U9] do not declare an isolated worker or separate service
process. A foreground thread is not a separate UID or security boundary.

[Developer instructions][U5] and [Makefile][U6]/[native link recipe][U8] support the
claimed QEMU `11.1.2` and `7.2.22` integration: Android NDK r30/Clang, SDK 37,
Meson/Ninja and local patches, with `arm64-v8a` host and `aarch64-softmmu` examples.
This describes upstream build infrastructure; no build was reproduced here and
SDK 37 tooling does not establish a required Android 17 host. The instructions
also warn that the x86_64 host path is not yet supported. Dependency examples
include GLib, libffi, pixman, libslirp, libepoxy and virglrenderer; the latter is
fetched from a moving branch in the recipe, so the recipe alone is insufficient
for immutable reproducibility. Internal symbol signatures and cleanup are not a
stable embedding contract; one fresh worker per VM avoids assuming reentrancy.

**Upstream claims:** [README][U1] presents TCG/MTTCG, QGE native display/audio and
VNC; SLIRP is the unprivileged network choice, while TAP/root and KVM/custom-kernel
options are distinct and excluded. Build instructions include virgl/Venus options;
none are adopted. The manifest requests INTERNET, network/Wi-Fi state/change,
broad storage, wake lock, vibration, audio settings, foreground data-sync service
and notifications. These surfaces are not PDVA's capability design.

[Copyright notice][U7] states GPLv3 for the fork and identifies Limbo ancestry.
Upstream QEMU, libraries, inherited files and assets need separate compatible
license/provenance review; a root notice is not an audit. This is the closest
inspected shared-library/JNI precedent, **not** a production engine selection or
proof of isolation, source completeness or distributable release correspondence.

### AI2TH/Linxr

**Upstream claim:** [README][L1] describes full Alpine on ARM64 without root.
**Source observations:** [VmManager][L2] resolves `libqemu.so` and `libqemu_img.so`
from `nativeLibraryDir`, then launches them with `ProcessBuilder`. The QEMU payload
is packaged under a shared-library filename but invoked as a process, not the
QubeVM `dlopen` model. ARM launch uses `virt`, `cortex-a57`, TCG, block/virtio devices
and a qcow2 path. User/SLIRP arguments include DNS `1.1.1.1` and SSH/API port forwards;
9p sharing can fall back to the external-storage root. These source choices do
not establish external-host-VPN inheritance or privacy and are not copied.

[Manifest][L3] requests INTERNET, foreground/data-sync service, notifications,
wake lock, read/write external storage and MANAGE_EXTERNAL_STORAGE. `VmService`
is non-exported and has no isolated-process declaration. App authority is broader
than the proposed PDVA worker. [Root LICENSE][L4] is MIT, while its README lists
QEMU as GPL-2.0 and other components separately. [Build container][L5] describes
SDK/Flutter tooling; the reviewed material does not establish a complete immutable
QEMU source/patch-to-distributed-binary chain. No `.so` or image was fetched or
validated. MIT at the root does not grant permissive rights to the QEMU payload.

### Limbo / F-Droid

[Pinned F-Droid metadata][F1] contains source recipes for Limbo, including
`v6.0.1-LimboEmulator`, QEMU `5.1.0`, NDK r22b and a
`make limbo BUILD_HOST=arm64-v8a` step. The source tag resolves to the Limbo commit
in the table. Metadata declares GPL-2.0-or-later and identifies external source
libraries/patching/native builds. This is historical recipe evidence for Android
ARM64 **host packaging**, not necessarily an ARM64 guest in that particular app
variant, current store availability, reproduced builds, or isolated-UID operation.
It does not waive modern target-SDK, page-size, provenance or security obligations.

## Android isolation, native services and executable constraints

**Documented semantics:** the official
[service manifest reference](https://developer.android.com/guide/topics/manifest/service-element)
specifies an isolated service process without ordinary app permissions of its own.
[Android 17 Process.java][A2] defines separate isolated UID ranges, including the
app-zygote range; do not hard-code only 99000–99999 or confuse `:process` naming with
UID separation. This supports the containment hypothesis, not total absence of
reachable host services or capabilities. Binding/FD transfer intentionally supplies
authority, and the host kernel remains shared by Android host processes.

**Policy observations at Android 17 r1:** [isolated_app][S1] invokes `app_domain` and
permits use of certain TCP/UDP sockets received from app domains. [isolated_app_all][S2]
allows read/write/map of passed app-data FDs while forbidding direct file open;
external storage is similarly constrained to passed descriptors. It restricts
service-manager discovery (activity, activity_structured, display and webviewupdate
exceptions), HwBinder/VndBinder, direct GPU driver access and USB, and forbids
creation of the enumerated non-AF_UNIX sockets. This is a specific policy, not
"no Binder" or "no network under any circumstances." Main [SM1][SM1]/[SM2][SM2]
has similar restrictions but lacks the release's activity_structured exception;
release and main must not be collapsed into one policy or every OEM.

**JIT:** release [app.te][S3] and main [app.te][SM3] grant `appdomain` self-process
`execmem`; release [app_domain macro][S4] includes executable tmpfs/memfd mappings.
These are direct source observations, not an inference from WebView/ART being able
to JIT. They make testing reasonable but do not prove the exact QEMU TCG allocator,
W^X transitions, memfd behavior, linker namespaces, signal handling, seccomp,
page size, target SDK or OEM policy. The [Android 10 execution rule](https://developer.android.com/about/versions/10/behavior-changes-10#execute-permission)
restricts direct execution from writable app home for target-29+ apps. Packaged
native loading, executable subprocess launch and generated memory are different
mechanisms requiring distinct tests. No copying an executable into writable data,
old-target workaround, permissive policy, or hidden grant is an acceptable proof.

**Optional Android-17-host mechanism:** [Android 17 manifest source][A1] defines
`android:nativeService`, used with `isolatedProcess`; it omits ART initialization
and loads a native entry point (defaults `libmain.so` / `ANativeService_onCreate`,
configurable by service properties). The official
[NDK NativeService reference](https://developer.android.com/ndk/reference/group/native-service)
marks its callbacks and binder interface API 37. This may reduce worker overhead
on Android 17 hosts, but it is **optional** and unmeasured. The primary experiment
uses an ordinary isolated Android Service plus JNI; host Android 17 is not made a
requirement. A no-ART service would need a native entry adapter, not an assumption
that Java/JNI bootstrap code works unchanged. NativeService supplies no extra
filesystem, JIT, network or longevity entitlement. Host minimum remains Unknown.

## Complete-guest references and alternatives

| Reference | Verified source / upstream description | Classification and limit |
|---|---|---|
| AOSP Cuttlefish | [Release QEMU manager][C1] has aarch64 QEMU selection, virtio block/console/input/GPU and guest-SwiftShader branches. [SwiftShader guest makefile][C2] explicitly requests guest execmem support. | Android guest/device-model reference only. A desktop/platform launch configuration does not satisfy ordinary-app Gate 0. Guest execmem is not host TCG permission. Selected virtual hardware, kernel drivers and Android HALs still need a controlled image design. Apache-2.0 headers on these files do not license every guest component. |
| AVF/Microdroid | [Existing exact-source evidence](gate-0-platform-authority.md), refs rechecked | Keep scoped negative ordinary-app MANAGE/custom-VM authority findings and Microdroid's incomplete-phone scope. No universal Android virtualization impossibility follows. |
| Virtual Master | Public distribution metadata and vendor statements, separately recorded in the [black-box study](gate-0-black-box-comparisons.md) | CLOSED-SOURCE / BLACK-BOX behavioral reference. Distinct guest-kernel boundary is Unknown. |
| VMOS / VPhoneOS and similar | Vendor product descriptions linked in that study | Black-box comparisons only; marketing, root toggles or compatibility do not identify an enforcing boundary. |
| RootlessAndroid15VM | [README][R1] claims ptrace-based interception; [interceptor][R2] uses PTRACE_TRACEME, register access and syscall tracing. | Shared-host-kernel/syscall mediation, not an independently emulated guest kernel in the inspected route; unsuitable as PDVA's primary boundary. Techniques/comparison only; README license claim is not a full file audit. |
| VineOS | [Architecture][V1] explicitly describes a shared host kernel and namespaces; [README][V2] uses QEMU user-mode for compatibility and describes a planned no-root path. | Unsuitable as primary full-system isolation. Namespaces, ptrace, Binder proxies or QEMU user-mode do not create a separate full-system kernel. Optional root/Shizuku paths also violate the production contract. |
| Draugr | [Pinned README][D1] describes WASM emulators in a platform WebView, loopback serving, v86/TinyEMU and mobile memory/threading limitations. | Alternate/fallback research, not lead. Reported boots are upstream claims; no PDVA run. Browser process/JIT authority and guest ISA/Android 17 support need separate proof. |
| TinyEMU | [Author's project page](https://bellard.org/tinyemu/) lists RISC-V, native x86/KVM and a JavaScript variant; dated source release `2019-12-21`, MIT claim. | Fallback/technique reference; dated archive name is not a verified content hash. No ARM64 Android 17 result or adopted component. |
| v86 | [Pinned README][W1] describes x86 hardware translated to WebAssembly and old Android-x86 examples; BSD notice with separately licensed dependencies. | Fallback only; neither native ARM64 guest support nor modern complete Android is established. |

**Supported conclusion (inference):** several independently inspectable Android
packaging approaches make QEMU/TCG a credible lead mechanism to test. None of these
sources demonstrates the proposed PDVA isolated-worker security model, a complete
Android 17 guest, acceptable usability, distribution approval or Gate 0 completion.
Source/license completeness, exact build correspondence and all physical results
remain open. Passing the experiment would narrow specific Unknowns, not adopt an
engine or pass a gate automatically.

## Immutable source links

The labels above resolve to exact files at the ledger revisions. Live Android,
product and TinyEMU pages have retrieval date only, not claimed immutable versions.

[Q1]: https://github.com/qemu/qemu/blob/f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c/docs/system/security.rst
[Q2]: https://github.com/qemu/qemu/blob/f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c/docs/system/arm/virt.rst
[Q3]: https://github.com/qemu/qemu/blob/f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c/qemu-options.hx
[Q4]: https://github.com/qemu/qemu/blob/f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c/qapi/misc.json
[Q5]: https://github.com/qemu/qemu/blob/f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c/LICENSE
[P1]: https://github.com/ExTV/Podroid/blob/ce0121896b2895637ab1f656cbb0d75fa2874489/README.md
[P2]: https://github.com/ExTV/Podroid/blob/ce0121896b2895637ab1f656cbb0d75fa2874489/app/src/main/java/com/excp/podroid/engine/QemuEngine.kt
[P3]: https://github.com/ExTV/Podroid/blob/ce0121896b2895637ab1f656cbb0d75fa2874489/app/src/main/AndroidManifest.xml
[P4]: https://github.com/ExTV/Podroid/blob/ce0121896b2895637ab1f656cbb0d75fa2874489/Dockerfile
[P5]: https://github.com/ExTV/Podroid/blob/ce0121896b2895637ab1f656cbb0d75fa2874489/LICENSE
[U1]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/README.md
[U2]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/qube-android-lib/src/main/jni/qube/vm-executor-jni.c
[U3]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/qube-android-lib/src/main/AndroidManifest.xml
[U4]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/qube-android-lib/src/main/java/com/max2idea/android/qube/machine/MachineService.java
[U5]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/README.developers
[U6]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/qube-android-lib/src/main/jni/Makefile
[U7]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/COPYING
[U8]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/qube-android-lib/src/main/jni/android-qemu-build.mak
[U9]: https://github.com/rhn-1k/QubeVM/blob/f860230c179e1cc10d5079a31215fa25cb5ad8ad/qube-android-arm/src/main/AndroidManifest.xml
[L1]: https://github.com/AI2TH/Linxr/blob/6216357b5af9d96defb772c3d06e9218c7d52b81/README.md
[L2]: https://github.com/AI2TH/Linxr/blob/6216357b5af9d96defb772c3d06e9218c7d52b81/android/app/src/main/kotlin/com/ai2th/linxr/VmManager.kt
[L3]: https://github.com/AI2TH/Linxr/blob/6216357b5af9d96defb772c3d06e9218c7d52b81/android/app/src/main/AndroidManifest.xml
[L4]: https://github.com/AI2TH/Linxr/blob/6216357b5af9d96defb772c3d06e9218c7d52b81/LICENSE
[L5]: https://github.com/AI2TH/Linxr/blob/6216357b5af9d96defb772c3d06e9218c7d52b81/docker/Dockerfile.build
[F1]: https://github.com/f-droid/fdroiddata/blob/7a3a14575311f6bbed71c2883050fa08a2644163/metadata/com.limbo.emu.main.yml
[R1]: https://github.com/Fiki-io/RootlessAndroid15VM/blob/455b26da0d274b1d99434c70a98963a47dacdf29/README.md
[R2]: https://github.com/Fiki-io/RootlessAndroid15VM/blob/455b26da0d274b1d99434c70a98963a47dacdf29/engine/syscall_interceptor.cpp
[V1]: https://github.com/Hexadecinull/VineOS/blob/f72a8ccdc69ea474cc60d4855c836121adbcf273/docs/ARCHITECTURE.md
[V2]: https://github.com/Hexadecinull/VineOS/blob/f72a8ccdc69ea474cc60d4855c836121adbcf273/README.md
[D1]: https://github.com/jacksonmafra-umain/draugr/blob/ac9cb0aa0fbe52b1a2597f4c8f91a687e909b2ac/README.md
[W1]: https://github.com/copy/v86/blob/6db8b157974dbaf1b54d2c2ec12dd71ddc1891e9/Readme.md
[S1]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app.te
[S2]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te
[S3]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te
[SM1]: https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/isolated_app.te
[SM2]: https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/isolated_app_all.te
[SM3]: https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/app.te
[S4]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/public/te_macros
[A1]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/res/res/values/attrs_manifest.xml
[A2]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/Process.java
[C1]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp
[C2]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/swiftshader/device_vendor.mk
