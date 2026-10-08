# Gate 0 isolated-worker tool adoption record

Review date: **2026-10-07**. Adoption scope: building and testing the
[pre-QEMU research harness](gate-0-isolated-worker-harness.md), under the explicit
first-implementation request. No production engine, guest dependency or opaque
runtime is adopted. Maintainer/update owner for every row is the PDVA repository
owner, with exact version/hash changes requiring a reviewed PR.

## Exact tools and trust roles

| Component | Exact identity and provenance | License / role / limitation |
|---|---|---|
| Gradle | Official 9.6.0 distribution; source tag resolves to `3f750f03d77e42327c5f9fcb9992110088330a32`. [Release](https://github.com/gradle/gradle/releases/tag/v9.6.0), [checksum authority](https://gradle.org/release-checksums/) | Apache-2.0 plus bundled third-party notices. Build execution trust only. Binary distribution not independently rebuilt. |
| AGP | `com.android.application:com.android.application.gradle.plugin:9.4.0` and `com.android.tools.build:gradle:9.4.0`, official Google Maven; [release/compatibility](https://developer.android.com/build/releases/agp-9-4-0-release-notes) | Apache-2.0 Android tools source and transitive licenses. Compiles/packages APK; build compromise could affect output. No app runtime dependency. |
| JDK | Local Eclipse Temurin `17.0.20.1+1`, [official release](https://github.com/adoptium/temurin17-binaries/releases/tag/jdk-17.0.20.1%2B1). Source metadata `79597447bd94`, build source `e6ba7dec3d07654074559310376a3ae89da5f4ac` | OpenJDK GPLv2 with Classpath Exception and bundled notices. JDK 17 required. Hosted CI uses its recorded JDK-17 runner installation; its exact patch is infrastructure, not claimed reproducible. |
| SDK platform | Google `platforms;android-37.0`, local revision 2, extension 22. Compile/target 37; research minimum 30 | Android SDK terms and package-specific notices. API compile stubs, not an Android guest/runtime. Package revision can change under SDK ID; record installed revision in CI. |
| Build tools | Google `build-tools;36.0.0`. AGP-selected aapt2 `9.4.0-15978811` Windows/Linux/macOS artifacts hash-pinned separately | SDK terms / Android tools Apache-2.0 and included notices. DEX/resources/signing/packaging build trust. |
| NDK | Google r28c `28.2.13676358`; [upstream changelog](https://github.com/android/ndk/wiki/Changelog-r28). clang-r530567e, LLVM base `3b5e7c83a6e226d5bd7ed2e9b67449b64812074c`, Android patch source `e727bfb014bd436f581a66a450c939a6983a1fc3` from packaged source ledger | SDK terms and component notices in NOTICE/NOTICE.toolchain: LLVM Apache-2.0 with exceptions, Bionic BSD and other components. Native compiler/linker trust. Chosen AGP default, not latest NDK. Default flexible/16-KiB alignment; no page-size override. |
| CMake / Ninja | Google SDK `cmake;3.22.1`, with packaged Ninja 1.10.2; [CMake release](https://cmake.org/cmake/help/v3.22/release/3.22.html) | CMake BSD-3-Clause, Ninja Apache-2.0. Native build orchestration only. SDK package distribution, not vendored source. |
| SDK command tools | Local Google `cmdline-tools;22.0`; SDK manager / APK analyzer from that package | Android SDK terms plus included open-source notices. Installation/inspection only. CI's SDK manager and APK analyzer are hosted infrastructure, invoked by explicit checked paths with versions printed. |
| Python | Local CPython 3.12.14; scripts need standard-library Python 3.11+ | PSF license and bundled notices. Download/hash bootstrap and validators, no pip dependencies. CI interpreter is recorded runner infrastructure. |
| GitHub Action | Official actions/checkout v7.0.1, independently re-resolved `3d3c42e5aac5ba805825da76410c181273ba90b1` | Existing MIT adoption in [catalog](../source-reference-catalog.md). Only external action, now also used for Android CI. Read-only contents, no persisted credentials, no secrets, no privileged PR trigger. |
| Git / Ubuntu runner | Hosted Ubuntu 24.04 Git/Python/JDK/SDK environment, exact image reported by Actions | Build infrastructure with its own packaged licenses. Mutable image; not reproducible product dependency. No new third-party cache/setup/upload action. |

Google tools are invoked under [Android SDK terms](https://developer.android.com/studio/terms).
No SDK/JDK/NDK archives, licenses acceptance files, keys, native binaries, APKs or
wrapper JARs are committed. The SDK's tools are not Google guest software.
SDK installation should use the developer's ordinary license acceptance process.

The local existing upstream tool installations were copied from ignored tool
storage under the historical checkout into ignored canonical build storage.
This was read-only access to build tools, **not reuse of historical implementation
or scaffolding**. The JDK archive was independently compared to its official
release checksum:
`e53a79c3c3d86865bd7e787903884331068e71321714ffd44f145785affc7cb0`.
NDK r28c was installed into canonical ignored tool storage through Google's SDK
manager. Tool metadata and compiler source ledger were inspected.

## Binary avoidance and exact artifact verification

[build.py](../../android/build.py) downloads only the official Gradle binary ZIP
and checks SHA-256
`bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01`
before extraction/use. The value was independently retrieved from Gradle's
official distribution checksum endpoint. No wrapper binary exemption is needed.
Tradeoff: Python and first-use network access are needed; the installed/extracted
local tool directory remains trusted developer build infrastructure.

[Verification metadata](../../android/gradle/verification-metadata.xml) records
exact SHA-256 identities for the resolved build graph: 184 Maven components,
including POM metadata and AGP/lint transitives. The
[coordinate/license inventory](gate-0-isolated-worker-dependencies.md) lists them.
These include AGP's Kotlin, AndroidX databinding and crypto/XML/network tooling
dependencies, even though the app contains no Kotlin or AndroidX runtime library.
Artifact verification is enabled in ordinary builds. No trusted wildcard,
ignored component, checksum bypass or signature-verification claim is added.

Initial Maven identities were recorded from official Google Maven/Maven Central
resolution and the existing local cache. This is initial trust-on-first-use
pinning, not independent source-to-binary reconstruction. Linux/macOS aapt2
classifiers were independently retrieved from Google Maven and hashed so CI
does not need to regenerate metadata. Unexpected or changed coordinates fail
verification and require review. No production security assertion follows from
a matching checksum. The POM license ledger is not a file-level audit of all
upstream distribution bundles.

No runtime Maven dependency is declared. The two packaged native payloads are
PDVA-built `libsubstrate.so`, one per arm64-v8a/x86_64 ABI; they link only platform
libc/libdl/libm. No C++ shared runtime, downloaded native runtime or third-party
source is linked. The tests use an Android-free Java main and platform
Instrumentation, avoiding JUnit/AndroidX-test dependencies.

## Security history, reproducibility and maintenance disposition

AGP 9.4's release notes and r28c's compiler/page-alignment fixes were reviewed;
this is not a comprehensive CVE audit. Full transitive security history and
independent reproducibility of upstream tool distributions remain Unknown.
Adoption is limited to auditable research builds with pinned Maven/distribution
identities. The repository owner must review upstream security updates and
invalidate affected artifact/runtime conclusions on tool changes.

JDK/SDK packages and hosted runner images are not all rebuilt from source.
Signing identity, build environment, file timestamps, platform package revisions
and AGP native tool classifiers can affect APK identity; bit-for-bit reproducible
APKs are not claimed. APK/source correspondence requires recording the exact
checkout, tool versions and output hash for each later physical experiment.
No build cache or APK artifact is uploaded by CI.

Repository validation retains the original root set, binary/secret rejection,
regular-100644/no-conflict requirement, UTF-8/control-byte and symlink checks,
requirements/ADR sequences, history notices and local Markdown links. It adds
only named research source/config/test paths and the hash metadata XML.
Unknown implementation paths and all JAR/SO/APK/image/key files still fail.

The always-running foundation job has no path filter. Android CI is path-aware,
read-only and limited to build/JVM/lint/static checks, with a 25-minute timeout.
It prints tool versions, installs named Android packages, builds both variants,
compiles instrumentation and inspects the release APK. No emulator, device,
gate evaluation, status polling, secret or privileged grant is part of CI.

## CI path correction reviewed 2026-10-08

At head `07242e856b337303baca53b491807b7a64def9ea`, the
[Android run](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/37707262682)
failed with `sdkmanager: command not found` (exit 127). Build and release inspection
were skipped, so that run supplies no successful Android build evidence.
Its Ubuntu 24.04 runner image was `20260927.320.1`; the
[published provisioning script](https://github.com/actions/runner-images/blob/ubuntu24/20260927.320/images/ubuntu/scripts/build/install-android-sdk.sh)
installs command tools under `cmdline-tools/latest/bin`. The workflow now checks
SDK manager and APK analyzer executability at those explicit paths under
`ANDROID_HOME`, prints the SDK manager version and the APK analyzer command-tool
package identity from `source.properties`, and fails clearly if either is absent.
APK analyzer does not provide a version verb; its containing package revision
identifies the installed tool.
There is no fallback download, setup action or suppression of installation errors.
All build, test, lint and APK inspection steps remain required.

The `latest` directory names the runner's provisioned command-tool installation,
not a newly adopted or pinned application dependency. Its package version and
the runner's JDK patch remain mutable build infrastructure. Local validation uses
Windows, Temurin 17.0.20.1+1 and Google command tools 22.0; it does not establish
success on GitHub's Ubuntu runner. The platform, build-tools, NDK and CMake package
identities above, Gradle hash and Maven verification metadata are unchanged.
No emulator or physical device is used for this revision; physical results remain
Unknown, and further useful non-physical work may continue under the
[slice's evidence policy](gate-0-isolated-worker-harness.md).
