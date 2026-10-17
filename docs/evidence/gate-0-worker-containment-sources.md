# Worker-containment immutable source ledger

Companion to the [containment findings](gate-0-worker-containment.md). Retrieved
2026-10-16. Hashes cover decoded Gitiles/raw Git bytes, without newline rewriting.
These are reference sources, not adopted dependencies or a device build manifest.

AOSP revisions were resolved from `android17-release`; subsequent file retrieval
used only the full commit. Linux v6.12 tag object resolved to the commit below.
This does not identify a deployed Android kernel. Source copies are retained in
ignored research storage, not included in the PR. No upstream source is executed.

Framework Java/JNI and Android policy files carry Apache-2.0 notices or belong
to the corresponding AOSP policy tree; Bionic includes BSD-style and Apache
file-specific notices. Linux sources carry GPL-family SPDX/file notices; its
documentation has its own applicable terms. This is reference-only review: no
code extraction, linking, redistribution or new security-critical dependency.
Any future adoption requires the full file-level license, provenance, maintenance
and TCB review required by the [policy](../source-provenance-policy.md).

The review covers the functions and policy paths discussed in the findings, not
a whole-tree audit. A successful fetch/hash is identity evidence, not a security
test. Earlier attempted paths `libc/SECCOMP_COMMON.TXT`, `private/appdomain.te`
and `services/core/java/com/android/server/am/OomAdjuster.java` returned 404 and
supply no evidence. The actual common lists, domain rules and OomAdjuster design
document below were inspected instead.

## Reproduction

Resolve each link at its full commit; for Gitiles append `?format=TEXT` and
base64-decode the response before computing SHA-256. Reject mismatches. Do not
replace a missing immutable file with a moving branch or treat fetch failure as
a denial finding. Hashes are independent of local platform line-ending settings.

## Framework

Repository: `platform/frameworks/base`. Commit: `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`.

| Exact source path | SHA-256 |
|---|---|
| [core/java/android/app/ActivityManager.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/ActivityManager.java) | `b77a98e9aad8110436048ded1c86f36515fba9ac406703eaf21f297acfb7af02` |
| [core/java/android/content/ServiceConnection.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/content/ServiceConnection.java) | `9ca2d88cc4150dcdf70b7e3392e848542c046cc174162f1fe0522190108e4b36` |
| [core/java/android/os/Process.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/Process.java) | `8547aa39e94af29c0455977ac40bfdc1a15678f07182dd8b0c1e0e6f8d513b76` |
| [core/jni/com_android_internal_os_Zygote.cpp](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/jni/com_android_internal_os_Zygote.cpp) | `006e4c3a51fd32eef1d41b3c2553a907e9b7b33b2bf605706921852ba8854a9a` |
| [services/core/java/com/android/server/am/ActiveServices.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActiveServices.java) | `bd27258e4fd4bacec2924fdd6366166104f5961c6600945ae2aedb0163aca7db` |
| [services/core/java/com/android/server/am/ActivityManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActivityManagerService.java) | `17923170a97fb001c3892ab4e0d71f9e249f9ea0b427a7aaf29916aae5208797` |
| [services/core/java/com/android/server/am/MemoryLimiter.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/MemoryLimiter.java) | `6713fd65cfc4bab10069734d09b2fb46c884c27ec0fee76f553295a31f733dc0` |
| [services/core/java/com/android/server/am/MemoryLimiter.md](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/MemoryLimiter.md) | `ab6da0575c1a0118f0f0dab5b49f4dc146c1ce589d07632bd4ca590a45443d59` |
| [services/core/java/com/android/server/am/OomAdjuster.md](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/OomAdjuster.md) | `b9a8240aaba879f257c7af96e8175635c985de7d173418e765fba80bdc7129b7` |
| [services/core/java/com/android/server/am/PhantomProcessList.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/PhantomProcessList.java) | `7e9eede2ff733df5acbff812b13ffb523f5e7d190481e04635afa5193b5049a4` |
| [services/core/java/com/android/server/am/PhantomProcessRecord.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/PhantomProcessRecord.java) | `c92dfa421a3066106f9437df420e56f6ce1b48cc8e70314670f8f2e0396559ad` |
| [services/core/java/com/android/server/am/ProcessList.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessList.java) | `96bfea0a32f822a04e46a16279100d5fdc718b909999df4962f2bd15c8ac55fc` |
| [services/core/java/com/android/server/am/ProcessRecord.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ProcessRecord.java) | `f4f07c1ba18fe28c66664c7300b9e5d22d5136358b136d3562aab401b0d616a0` |

## Process groups

Repository: `platform/system/core`. Commit: `545d2487e38192a2ce25040897ced877cf6b4f53`.

| Exact source path | SHA-256 |
|---|---|
| [libprocessgroup/processgroup.cpp](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/libprocessgroup/processgroup.cpp) | `61825c2354e9472b0f08ddd20bdcf415d27910e9549bc5f3744b7293b2d1d0ab` |
| [libprocessgroup/profiles/cgroups.json](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/libprocessgroup/profiles/cgroups.json) | `ab2ed667ff45958843fb0c6ee953a5512def0ae87470c4358aa9576a6a4b2e22` |

## SELinux

Repository: `platform/system/sepolicy`. Commit: `e066568e98d86db31a9346d30977f3632fa7073c`.

| Exact source path | SHA-256 |
|---|---|
| [private/app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te) | `6a18ae176e35cf19ab022cc75887a5c77aae55f00e8a1ebddd7ebd75aea64525` |
| [private/domain.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/domain.te) | `793eb29f8621bc3318cdb9c40cce39f954999d2152b2bd45b812955ce5b1de16` |
| [private/isolated_app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app.te) | `a088dfeaf2dabbfcd4327c01549096c88db22687c2fceb51c797ede552bb2d51` |
| [private/isolated_app_all.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te) | `e65adb199d7fc26cd716f4e376f6068edcd3c350647f121e8d5937fa9bca4ad9` |
| [private/seapp_contexts](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/seapp_contexts) | `3aa66e127e6941eb2dfda03dc1cff9519fa0ec0f4237e87e033ce357b535379d` |
| [private/untrusted_app_all.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/untrusted_app_all.te) | `c0a3f00205519925e1c05119dfef03016650c1e0acc71046952d63001ae5dbb5` |
| [public/app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/public/app.te) | `0a68032adf7973769e1e430a5b169c39807691776698d504fd2dce75641fb3c9` |
| [public/te_macros](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/public/te_macros) | `9825ba9b9bd742070683f21ad636e930ec24c73e3ec9dcb22b85e2dcb9b0367d` |

## Bionic

Repository: `platform/bionic`. Commit: `06356e41c5ed7b12220b24c05ba4fdb873b126a7`.

| Exact source path | SHA-256 |
|---|---|
| [libc/Android.bp](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/Android.bp) | `2d0cdb26a1546694d1cded95ba84b10b3ba2bda78f783a3a9830d0e47661ac10` |
| [libc/seccomp/seccomp_policy.cpp](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/seccomp/seccomp_policy.cpp) | `ca8b2270bc0f1ab4f108ee13185ae81b22245bbf9036c33628d97e857363a35b` |
| [libc/SECCOMP_ALLOWLIST_APP.TXT](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/SECCOMP_ALLOWLIST_APP.TXT) | `8bc68ba9dbe187bcc9f98b5fcb5126c533c2be4d3bbd482a2b09fd09e4d81be0` |
| [libc/SECCOMP_ALLOWLIST_COMMON.TXT](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/SECCOMP_ALLOWLIST_COMMON.TXT) | `ff5f568282194d72f3bf94ff293fb35a8712926391b9c62f173bdb78d009cd92` |
| [libc/SECCOMP_BLOCKLIST_APP.TXT](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/SECCOMP_BLOCKLIST_APP.TXT) | `a907336b094d978a609fe155762e1cd055c6a3e861424cd1faafb0200045142c` |
| [libc/SECCOMP_BLOCKLIST_COMMON.TXT](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/SECCOMP_BLOCKLIST_COMMON.TXT) | `aedf47d745ad3bfc6fc9646a46264569268a047e6e5762501450feb47b3988e4` |
| [libc/SYSCALLS.TXT](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/SYSCALLS.TXT) | `c00e3c8d61e83e4c1a1f206474edca23483ba845967fb936dea1d49e62311adf` |
| [libc/tools/genseccomp.py](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/tools/genseccomp.py) | `f3b525b82e0ae13b58f17f401238d55c16d913da88f32b536e16456df3f8abaa` |

## Linux v6.12

Repository: `torvalds/linux`. Commit: `adc218676eef25575469234709c2d87185ca223a`.

| Exact source path | SHA-256 |
|---|---|
| [Documentation/admin-guide/cgroup-v2.rst](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/Documentation/admin-guide/cgroup-v2.rst) | `ad3bd37498a57cc249326fd5c2d609669b32611fe69d126df3c3abec1539f572` |
| [fs/file.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/fs/file.c) | `b7941baea1a17ce6bedc84fdf7096ecf4963ff0ee65929ed620a6b56401be99b` |
| [kernel/cgroup/cgroup.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/cgroup/cgroup.c) | `7442351a48fc3daf1f510ca066dfa310821c85062f30b0ea469ca03ede2c7880` |
| [kernel/exit.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/exit.c) | `7c28bfc644117470b9cbe6d46c84580de98225755bbb227e61d638ea7104025d` |
| [kernel/fork.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/fork.c) | `90342b5b1d7708052564b95a8855a19b3925fe0d1c3f018b472dc66045328433` |
| [kernel/seccomp.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/seccomp.c) | `7396faa0f0edada2a4df6602a421dc633aa155cbee7893afd5ddebef4fcda4ca` |
| [kernel/signal.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/signal.c) | `e93c014e2354c8806dfe3504c4f274cab250df0251745e1fd9af9c60616e9326` |
| [kernel/sys.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/sys.c) | `e43eb875410d607ccf91ca00d88433052b58fdae4e4ccdd12c53c458f1ce1d69` |
| [mm/mmap.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/mm/mmap.c) | `590721f62c718c191496173fa34cf1187c39f5043a272afd1065fb7358ab9f7d` |

## Mutable documentation read on the review date

- [Android isolated service](https://developer.android.com/guide/topics/manifest/service-element#isolated): public component semantics.
- [Android 17 behavior changes](https://developer.android.com/about/versions/17/behavior-changes-all#app-memory-limits): platform memory policy, not a PDVA quota API.
- [PDEATHSIG](https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html): inheritance, cancellation, creating-thread and credential-transition caveats.
- [pidfd_send_signal](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html): identity handle and permission distinction.
- [wait](https://man7.org/linux/man-pages/man2/waitpid.2.html): child observation and reaping scope.
- [getrlimit](https://man7.org/linux/man-pages/man2/getrlimit.2.html): per-resource scope and hard-limit authority.

Manual pages explain Linux semantics; pinned Linux sources above anchor the
key findings. Neither is an Android runtime observation. Official Android docs
and AOSP implementation are recorded separately because API promises, source
behavior and installed OEM behavior need not be identical.

## Seccomp continuation references (2026-10-17)

The [seccomp process-control review](gate-0-seccomp-process-control.md) independently
rehashed the 40 retained files above. The following additional decoded/raw source
files extend the reference set. No upstream implementation is imported, compiled
or executed. Bionic files retain BSD-style notices; glibc/GLib retain LGPL-family
file terms; QEMU retains its per-file GPL/LGPL/other notices. Linux syscall tables
and UAPI files retain their SPDX terms (including applicable syscall-note exceptions).
These references grant no product adoption or redistribution approval.

Bionic uses the **same Android 17 reference commit**
`06356e41c5ed7b12220b24c05ba4fdb873b126a7` as above. An attempted
`libc/arch-arm64/bionic/__clone.S` URL returned 404; it supplies no source evidence.
The actual assembly path is `__bionic_clone.S`, verified from the pinned tree.

| Exact source path | SHA-256 |
|---|---|
| [libc/bionic/pthread_create.cpp](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/bionic/pthread_create.cpp) | `1bbcc146ff4b24732df036422c1d17c694cbc8c466d55052414cc0ed49c2beeb` |
| [libc/bionic/clone.cpp](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/bionic/clone.cpp) | `53704fa1f326b88b9e208067df6a875893a7d43257bb7d608452144fd0d81ecb` |
| [libc/arch-arm64/bionic/__bionic_clone.S](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/arch-arm64/bionic/__bionic_clone.S) | `a8b3862bdbb539841c9ada95b74d34880be030442cb189e3e18f4cfe7a51a8ed` |

Linux ABI references at the existing v6.12 commit
`adc218676eef25575469234709c2d87185ca223a`:

| Exact source path | SHA-256 |
|---|---|
| [arch/x86/entry/syscalls/syscall_64.tbl](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/arch/x86/entry/syscalls/syscall_64.tbl) | `980ce3115028c71c5618e7864d262017bde8103bcfe7b413147a14fd312c92ac` |
| [include/uapi/asm-generic/unistd.h](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/include/uapi/asm-generic/unistd.h) | `aec51e459e2b113bcf8e16c99be09d5384fe3f4fa4a16100dfe0e71dbc0e172a` |
| [arch/arm64/include/asm/unistd.h](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/arch/arm64/include/asm/unistd.h) | `a6a15366cd333284fbd82ddc4fc01ce58efd06b4640d30da347eaeb985c8008f` |

glibc tag `glibc-2.39` resolves through annotated tag object
`9609a435f3f9a07c1cf607ad5821b12f735abd69` to commit
`ef321e23c20eebc6d6fb4044425c00e6df27b05f`. It is a fallback-source reference,
not the exact Ubuntu runner libc build. GLib is at PDVA's existing recipe pin
`e05063ccc6c8f222465a1080927f4c14349f3de6`.

| Exact source path | SHA-256 |
|---|---|
| [glibc sysdeps/unix/sysv/linux/clone-internal.c](https://github.com/bminor/glibc/blob/ef321e23c20eebc6d6fb4044425c00e6df27b05f/sysdeps/unix/sysv/linux/clone-internal.c) | `4f0775bc386892e382893e9148f64c68d5947106ada4e7baef482db8c616d0b6` |
| [glibc nptl/pthread_create.c](https://github.com/bminor/glibc/blob/ef321e23c20eebc6d6fb4044425c00e6df27b05f/nptl/pthread_create.c) | `36fd1e6da5cee9ce31c58c8689f751542fd49f6c8214557b80925f049df8c050` |
| [GLib glib/gthread-posix.c](https://github.com/GNOME/glib/blob/e05063ccc6c8f222465a1080927f4c14349f3de6/glib/gthread-posix.c) | `d7e9654c26bfade3079c39c112e832fe7bd9932b99d7886f75a49081f0fa0b0e` |
| [GLib glib/gthreadpool.c](https://github.com/GNOME/glib/blob/e05063ccc6c8f222465a1080927f4c14349f3de6/glib/gthreadpool.c) | `6a48875831af755ded48b1018a4798ba3c18c3684276d549eff5844526113ea0` |

QEMU reference commit `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`. Hashes are over exact LF Git blobs;
retained worktree files were independently compared after CRLF normalization.
This preserves the existing source/archive pin and imports no QEMU sandbox code.

| Exact source path | SHA-256 |
|---|---|
| [util/qemu-thread-posix.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/qemu-thread-posix.c) | `ec784f93b3c7ef9bc5215b1987166510ec2f87ee09b5de43c17e8c32b5be7f9c` |
| [util/rcu.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/rcu.c) | `3e4c5e57c126e26f67d8bd9f9e033f0cc059ed3d0a685da38a84c14f61371d51` |
| [util/thread-context.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/thread-context.c) | `0540e5d83a0ded3595552a92a40e58978f6abdc9b0c090d591d081c833188c40` |
| [accel/tcg/tcg-accel-ops-rr.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/accel/tcg/tcg-accel-ops-rr.c) | `6265dd582ec86bd9073a0c8366846f31dd0a9a36b96bd1d3f30845a7f8df03ab` |
| [accel/tcg/tcg-accel-ops-mttcg.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/accel/tcg/tcg-accel-ops-mttcg.c) | `2810da98449127088e22441e08d253fc84d254e0f23086c5791aecf5574671bc` |
| [system/main.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/main.c) | `5209f230ab4a0d0794d3a2669b2a6d8154349283d8560eb8670044877122c242` |
| [system/vl.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c) | `a5fb2a78e45ec8edb256188eed44e8f06f7dba99c1dd029dd8a0d74cfab74266` |
| [system/runstate.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/runstate.c) | `cc0ceeffd2dd2b8c61eed5d9bf14c25d211c2259df3de537ebf8f2927c1ae7ab` |
| [system/async-teardown.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/async-teardown.c) | `86f926eb46ee7aa8533061a65c1c598bc38c1795f034ae56651af267d09c2c46` |
| [system/qemu-seccomp.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/qemu-seccomp.c) | `fa45c2fceb986158ed98d6c412efab6714604b58a2591782bcc3c8758f7aad46` |
| [util/thread-pool.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/thread-pool.c) | `cd7848272ace041fa9e991369b216657d7b7ba076f22b9029a204f60c42a8c75` |
| [util/oslib-posix.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/oslib-posix.c) | `ad7bc820a4ab61fa0b00502a0a04540228a7cc60da5cb8908fcbc2af2419b869` |
| [iothread.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/iothread.c) | `7c19678153aae69f373f278ddbb1dc0158d2c050b34843792acf5302e72a7e0b` |
| [io/task.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/io/task.c) | `9bfb237a80cd540dd90316c41a170f9a32b9ebbcf76b76429c063fbf3f1167f4` |
| [net/tap.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/net/tap.c) | `ea07bd8b232a7a5a094f359913d9ffa7e1894ef50b19f117a673b4e984e0b28a` |

Additional mutable documentation read on 2026-10-17:
[kernel seccomp BPF](https://docs.kernel.org/userspace-api/seccomp_filter.html),
[seccomp syscall](https://man7.org/linux/man-pages/man2/seccomp.2.html), and
[clone/clone3 syscall](https://man7.org/linux/man-pages/man2/clone.2.html).
Source semantics, public contracts, new unrun Linux controls and installed Android
authority remain distinct evidence classes.
