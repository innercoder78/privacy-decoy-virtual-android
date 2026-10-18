# Capability-revocation source ledger

Companion to the [findings](gate-0-capability-revocation.md). Retrieved and reviewed
2026-10-18. Hashes cover raw/decoded bytes without newline conversion. Sources are
references, not adopted dependencies, a complete release manifest or device evidence.

## Android public API implementation

Repository `platform/frameworks/base`, commit
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`, the same Android 17 reference used by
the lifetime investigation. These four files carry Apache-2.0 notices. No code
or examples are copied into tracked application/test source.

| Exact source | SHA-256 | Reviewed witness |
|---|---|---|
| [SharedMemory.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/SharedMemory.java) | `218bdffe38c40b599e516c338f5df94258750abab77b3a589c0a49dc288ea05c` | setProtect, MAP_SHARED mapping, unmap/close, parcel transport |
| [ParcelFileDescriptor.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/ParcelFileDescriptor.java) | `dd76635b7ed062dac3d04f5941f39bf63c5680841292d1bc07c39845722d5cbf` | dup, detachFd, closeWithStatus, writeToParcel/CREATOR |
| [Binder.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/Binder.java) | `502dcd0067b3603e321086917e8e2274a8fc7beae1e9a75b335c2a035707ea6e` | Public calling PID/UID contract, identity handling, base endpoint surface |
| [android_os_SharedMemory.cpp](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/jni/android_os_SharedMemory.cpp) | `1e2e951bb055af67dd72ced0acbb244a43cf46496b85d6ce729a4f2f26805082` | JNI delegates creation/protection to ashmem abstraction; not backend/device closure |

## Linux reference semantics

Repository `torvalds/linux`, v6.12 commit
`adc218676eef25575469234709c2d87185ca223a`. Binder and mmap files declare
GPL-2.0-only; scm.c declares GPL-2.0-or-later. Reference-only review imports no Linux
implementation and adopts no kernel. Android's actual kernel may differ.

| Exact source | SHA-256 | Reviewed witness |
|---|---|---|
| [drivers/android/binder.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/drivers/android/binder.c) | `da11c5da4904dc99df8996ecb8683db9523f99d6a850065a94efad3c914d9ede` | Binder object/handle/FD translation, LSM hooks, in-flight fixups and receiver FD installation |
| [net/core/scm.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/net/core/scm.c) | `2fb9947ab7dded9dcdc4710970150918f017420a0acfb5bf8896a105a4d7eac9` | SCM_RIGHTS file references, detach/install and release of queued references |
| [mm/mmap.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/mm/mmap.c) | `590721f62c718c191496173fa34cf1187c39f5043a272afd1065fb7358ab9f7d` | VMA holds file reference; freshly retrieved hash matches prior ledger |

Existing [containment source identities](gate-0-worker-containment-sources.md)
remain authoritative for fs/file.c, kernel/fork.c and policy at
`platform/system/sepolicy` commit `e066568e98d86db31a9346d30977f3632fa7073c`.
The retained isolated_app.te and isolated_app_all.te were read for received-file,
map, service-manager and socket permissions and compared to their recorded hashes.
Policy source is not compiled OEM policy; an allow is not proof that all other
authorization checks succeed. Existing lifecycle sources/limits are not superseded.

Supplementary mutable documentation read on the review date:
[SharedMemory public API](https://developer.android.com/reference/android/os/SharedMemory),
[Linux mmap manual](https://man7.org/linux/man-pages/man2/mmap.2.html) and
[Unix-domain socket manual](https://man7.org/linux/man-pages/man7/unix.7.html).
Immutable files above anchor the findings; no manual-page implementation is adopted.

## Reproduction and rights limits

1. Fetch each Gitiles link with `?format=TEXT`, base64-decode before hashing.
   Fetch Linux Git blobs at the full commit. Compare SHA-256 without CRLF rewriting.
2. Read the complete named methods and callers; distinguish original references,
   in-flight references, receiver installation and existing mappings.
3. Compare actual INIT fields, manager cleanup, fixed filenames, worker mapping,
   protocol checks and launcher FD handling at PDVA main
   `49be371f20107f9f2fb098270d68f092f4afb88e`.
4. Reject mismatches/unavailable sources; never replace immutable refs with main
   or treat retrieval errors as denial evidence. Retained files are ignored review
   artifacts only. No source was compiled or executed for this review.

New Markdown is original analysis with links and source identities; no general
repository license or redistribution rights for future product dependencies are
inferred. Any future broker/VM adoption requires separate file-level provenance,
license, dependency, security, maintenance and owner/ADR review. Repository owner
maintains this evidence. No proprietary data, binaries, SDK changes or new package
dependencies enter this change.
