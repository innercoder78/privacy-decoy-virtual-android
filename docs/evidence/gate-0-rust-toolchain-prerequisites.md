# Android release Rust toolchain: source leads and unverified prerequisites

Review: **2026-10-23, America/Fortaleza; Windows x86_64 source/metadata only.**
[REC-08 attribution](gate-0-research-recovery.md) applies. Scope: PDVA-REQ-002–003,
034–045 and 054. **Gate 0 Unresolved; Gates A–G Not reached.**
No compiler/target-library bytes were acquired, installed or executed; no build ran.

**Question:** which exact release compiler/target prerequisites would be needed
before a bounded Android ARM64 library build? **Source lead preserved; build
readiness and compiler correspondence UNKNOWN.** The earlier report's installed
compiler search, unavailable Linux execution environment and historical tests
remain owner-relayed; this recovery does not repeat them.

## Freshly retrieved public metadata

| Immutable reference | Independently observed declaration; excluded conclusion |
|---|---|
| [Release default.xml](https://android.googlesource.com/platform/manifest/+/5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f/default.xml), `5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f` | Default is `refs/tags/android-17.0.0_r1`. It is release-source context, not a binary manifest for an installed device. |
| [Soong rust/config/global.go](https://android.googlesource.com/platform/build/soong/+/6722dd8833db7482df1a2543ca3fcf67ddf0f7b1/rust/config/global.go), `6722dd8833db7482df1a2543ca3fcf67ddf0f7b1` | Defaults select Rust **1.93.1** under `prebuilts/rust-toolchain/`; environment override paths exist. Device flags include panic abort, global-dynamic TLS and PIC. Defaults are not an observed compiler invocation or ABI pass. |
| [Linux prebuilt target directory](https://android.googlesource.com/platform/prebuilts/rust-toolchain/linux-x86/+/fa2b1777b1f5c0471bb54ad4026feb1f6e94ea70/1.93.1/lib/rustlib/aarch64-linux-android/lib/), `fa2b1777b1f5c0471bb54ad4026feb1f6e94ea70` | Directory metadata lists std `.rlib`/`.so`, core, alloc, compiler builtins, panic-abort/panic-unwind and unwind components. Listing names does not verify binary contents, compatibility, license closure or install readiness. |
| [manifest_14933020.xml](https://android.googlesource.com/platform/prebuilts/rust-toolchain/linux-x86/+/fa2b1777b1f5c0471bb54ad4026feb1f6e94ea70/1.93.1/manifest_14933020.xml), same prebuilt pin | Names `toolchain/rustc` revision `3b396167a567d74f6fe75444780fc25832928858` and `toolchain/android_rust` revision `fd3c251016559fa70d31861d507dde14160515a2`. The compiler-build manifest's default branch is `rust-1.93.0-release`; that name is not a measured compiler version or a reason to overwrite Soong's 1.93.1 default. |
| [Prebuilt Android.bp](https://android.googlesource.com/platform/prebuilts/rust-toolchain/linux-x86/+/fa2b1777b1f5c0471bb54ad4026feb1f6e94ea70/Android.bp), same pin | Separates host-prebuilt std from source-built toolchain-library std. Sysroot defaults declare min SDK 29 and SDK 30 in that context. These are neither PDVA's supported host minimum nor the guest Android 17/API 37 requirement. |

Procedure: exact Gitiles `?format=TEXT` retrieval and base64 decoding for files;
`?format=JSON` for target directory metadata. The four Soong/prebuilt file or
directory receipts matched the corresponding retained source-text/metadata
SHA-256 values; this compares public source receipts, not compiler binaries.
No third-party implementation is committed or adopted.

**Fresh failed retrieval scopes:** the exact root-directory JSON requests to
[toolchain/rustc at the named revision](https://android.googlesource.com/toolchain/rustc/+/3b396167a567d74f6fe75444780fc25832928858/?format=JSON)
and [toolchain/android_rust at the named revision](https://android.googlesource.com/toolchain/android_rust/+/fd3c251016559fa70d31861d507dde14160515a2/?format=JSON)
both returned **HTTP 404**. Source correspondence remains UNKNOWN; those failures
do not prove the source is globally absent. No mirror substitution or floating
toolchain acquisition was used to conceal the gap.

## STOP boundary and relationship to merged backend evidence

NDK r28c does not itself supply the selected Rust compiler and target std.
Compiler hashes/signatures, source/build/license correspondence, selected linker,
transitive proc-macro/native closure, ELF ABI/imports/DT_NEEDED, Bionic symbol/API
availability, TLS/panic/unwind and 4/16-KiB properties remain **NOT VERIFIED**.
There is no synthetic `cdylib`, backend port or runtime result in this record.

The merged [backend assessment](gate-0-backend-endpoints.md) and
[source ledger](gate-0-backend-endpoints-sources.md), PR #31, already establish
the selected `vhost_device_vsock` host executable and host-library dependencies,
missing library/JNI entry, late pathname connections and guest RAM authority.
The new source-version/target-inventory lead narrows that record's compiler-version
Unknown; it does not supersede its binary, endpoint or security blockers. Successful
compilation alone would not repair them or establish ordinary-app authority.

**Reopening condition, not an authorized experiment:** independently verify
legitimate exactly matching compiler and target-library bytes, corresponding
source/licenses and selected linker on a controlled host before any small
synthetic ARM64 ABI build. Stop on mismatch or unresolved provenance. Do not
substitute a standalone Cargo graph for the release Soong graph. This preservation
task obtains no toolchain, changes no module type and adopts no dependency.
