# Gate 0 isolated Android native launch control

Review dates: **2026-10-10–2026-10-11** (America/Fortaleza). **Gate 0: Unresolved. Gates A–G:
Not reached. Physical execution: NOT RUN / Unknown.** ADR-0001 remains Accepted;
ADR-0002 remains Proposed. No production VM engine is selected.

This record covers PDVA-REQ-002, PDVA-REQ-003, PDVA-REQ-010 through PDVA-REQ-013,
PDVA-REQ-036, PDVA-REQ-039 through PDVA-REQ-045 and PDVA-REQ-048. It prepares a
separate executable control in the existing [isolated worker](gate-0-isolated-worker-harness.md).
No QEMU, kernel, rootfs, guest image, Android guest, permission or production
architecture is introduced. A success from this control cannot pass Gate 0.

## Independently checked preflight

Canonical repository: `innercoder78/privacy-decoy-virtual-android`. Clean local
main and independently queried remote main were both
`cb6eb6853b79f7035ea96e26068b3771409f3425`. No PRs were open, so there were no open
heads/bases/diffs/checks/comments to reconcile. PR #6 was merged from
`379822d7f1b56e8f6d0f06a2476d4f9387f80ae7` into main at the above merge commit;
its conversation comments and reviews were empty at preflight.

- [Main foundation run](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38099220222): success.
- [Main Android run](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38099220220): success; Android job successful.
- [PR #6 final-head cross-build](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38095872712): success.
- [GitHub Status](https://www.githubstatus.com/api/v2/status.json): All Systems Operational at preflight.

All three workflows were active. Workflow definitions, the harness, requirements,
governance, ADRs, evidence criteria, source-adoption and hashed dependency records
were inspected before implementation. The checkout had one worktree, was on main,
and had no dirty tracked changes or stashes. Existing ignored builds/tools were
retained. Historical Privacy-Decoy was not modified or used as implementation
source. One new branch was created.

The resumed pre-publication check on 2026-10-11 found the same main SHA, no open
PRs, and the same successful latest main/final-PR-6 runs. There was no existing
PR to update or changed base to reconcile.

## Authority hypothesis and falsifiers

**Hypothesis:** an ordinary installed zero-permission target-37 APK can ask its
non-exported isolated Service to fork and `execve` one installer-extracted ARM64
dynamic PIE, retaining the isolated worker UID without granting the child existing
worker descriptors. This is about one trusted synthetic payload, not an adversarial
process supervisor or VM-engine adoption.

| Separate proposition | Evidence prepared here | Still unobserved |
|---|---|---|
| JNI execution | Existing `System.loadLibrary("substrate")` and native probes retained | Actual stock-phone release execution |
| Separate executable | Fixed-path `fork`/`execve`; ELF entry, interpreter and `DF_1_PIE` | Installed lookup, creation, exec and linker startup authority |
| Executable memory | Existing RW-to-RX/generated-return probes retained | Device policy and any eventual TCG/JIT compatibility |
| Identity/capabilities | Child self-observation and PID/UID/eUID relations; manager verifies distinct worker UID | Actual child domain, capabilities, seccomp and FD exposure |
| Packaging | Actual debug/release APK manifests and native bytes inspected | Installer extraction and physical execution |

Falsifiers include missing extraction, wrong ELF, fork failure, exec errno, linker
failure, signal/timeout, malformed output, unexpected UID/context/FDs, incomplete
reaping or a lost reply. `EACCES`/`EPERM` alone cannot attribute a denial to SELinux
rather than DAC or another policy. Missing evidence is never a successful result.

## Official documentation and source review

Documentation was read on the review date. AOSP revisions below are source
observations, not a claim that any OEM production image matches AOSP main.

- [Android 10 executable restriction](https://developer.android.com/about/versions/10/behavior-changes-10#execute-permission):
  target-29+ apps cannot directly execute files in writable app home. This experiment
  never copies an executable there or reduces target SDK.
- [Native extraction](https://developer.android.com/guide/topics/manifest/application-element#extractNativeLibs):
  `useLegacyPackaging` controls extraction packaging. Generated native sources use
  the public [AGP Variant API](https://developer.android.com/reference/tools/gradle-api/9.4/com/android/build/api/variant/AndroidComponentsExtension).
- [Isolated Service](https://developer.android.com/guide/topics/manifest/service-element):
  `isolatedProcess` uses a special process without its own permissions. This does
  not erase explicitly delegated descriptor capabilities.
- [Android 17 target behavior](https://developer.android.com/about/versions/17/behavior-changes-17)
  adds read-only requirements for native files loaded with `System.load`. That API
  differs from `execve`. The [all-app changes](https://developer.android.com/about/versions/17/behavior-changes-all)
  were also reviewed. Neither page guarantees isolated-worker execution. No network
  permission is added; compile/target 37 remains unchanged.
- [Public native APIs](https://developer.android.com/ndk/guides/stable_apis) and
  [ABIs](https://developer.android.com/ndk/guides/abis) describe the NDK interface.
  This payload uses public Bionic libc functions only.
- [Linker namespaces](https://source.android.com/docs/core/architecture/vndk/linker-namespace)
  constrain dependency resolution. Executable startup differs from ART/JNI loading.
  No private platform library, `LD_LIBRARY_PATH`, `LD_PRELOAD` or namespace override
  is used; full device linker closure still needs observation.

| Pinned upstream revision | Reviewed source and finding |
|---|---|
| `platform/system/sepolicy` at `4571ddd9440721fec583c906a337de949a77749e` | [private/app.te](https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/app.te) permits app-domain installed `apk_data_file` read/execute and distinguishes it from writable data restrictions. [private/isolated_app.te](https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/isolated_app.te) applies app/isolated attributes. These justify a probe, not a device outcome. |
| `platform/frameworks/base` at `1cdfff555f4a21f71ccc978290e2e212e2f8b168` | [NativeLibraryHelper](https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/jni/com_android_internal_content_NativeLibraryHelper.cpp) selects safe `lib/<abi>/lib*.so` names for release extraction and applies 0755. [ApplicationInfo](https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/content/pm/ApplicationInfo.java) supplies public `nativeLibraryDir`. No hidden API is called. |
| `platform/bionic` at `731631f300090436d7f5df80d50b6275c8c60a93` | [fork.cpp](https://android.googlesource.com/platform/bionic/+/731631f300090436d7f5df80d50b6275c8c60a93/libc/bionic/fork.cpp) uses clone/at-fork handlers and disables child fdsan/fdtrack. [prctl.h](https://android.googlesource.com/platform/bionic/+/731631f300090436d7f5df80d50b6275c8c60a93/libc/include/sys/prctl.h) and [resource.h](https://android.googlesource.com/platform/bionic/+/731631f300090436d7f5df80d50b6275c8c60a93/libc/include/sys/resource.h) expose process/resource controls. [linker_main.cpp](https://android.googlesource.com/platform/bionic/+/731631f300090436d7f5df80d50b6275c8c60a93/linker/linker_main.cpp) checks executable PIE and establishes namespaces. |
| Same Bionic revision | [SYSCALLS.TXT](https://android.googlesource.com/platform/bionic/+/731631f300090436d7f5df80d50b6275c8c60a93/libc/SYSCALLS.TXT), app/common `SECCOMP_ALLOWLIST` and `SECCOMP_BLOCKLIST`, `libc/tools/genseccomp.py`, and `libc/seccomp/seccomp_policy.cpp` were retrieved. Required exec/wait/prctl/kill/FD interfaces and clone appear in the inputs. Installed device BPF/OEM policy was not inspected; blocked calls may kill the worker instead of returning errno. |

Selected SHA-256 values of retrieved source bytes:

| Source | SHA-256 |
|---|---|
| AOSP `private/app.te` | `a50dfdd87f88aca3480a8c9d21cbf6d1243cab8b2beaafbc638bf3b94eed8fd6` |
| AOSP `private/isolated_app.te` | `cde4bf0d9db990ab76479ab95ed7b2502ede8c9cbaa1c8f785df61b5c16f4ae0` |
| `NativeLibraryHelper.cpp` | `a9be4f061cac10b7c659622869cdcb4d7d830a0e1933a714691ba54d983893bd` |
| Bionic `fork.cpp` | `bccf700dca41f6d9d2fea0adc24f6cbfb86f3edfe50738b1bfd3b4fb981b7c30` |
| Bionic `linker_main.cpp` | `1ffb11db2bf705d35dfccaa0c8230115c0d7860932f39c3dc5b0773a0cb9a82c` |
| Bionic `SYSCALLS.TXT` | `a521919656163efb00468ee807a49dc5ea1fd82f66695e8ce32056c9356bc94e` |

Browser retrieval of some Gitiles pages failed; direct pinned HTTPS reads succeeded.
The guessed generated `arm64_app_policy.cpp` path did not resolve and is not
evidence; actual generator/policy inputs replaced that guess. No upstream
implementation was copied into application source.

## Source-owned executable and packaging

[launch_payload.c](../../android/gate0-harness/src/main/cpp/launch_payload.c) computes
twice the sum 1 through 6, writes one 40-byte numeric record and intentionally exits
**42**. It reads only its own FD directory, SELinux context and bounded process
status to classify effective capabilities. It reads no management/host-file content,
account data, stdin or network data and has no configurable operation.

NDK r28c builds `aarch64-linux-android30`, matching the existing research floor.
`lib/arm64-v8a/libpdva_launch.so` matches installer naming, but remains a dynamic PIE
with `PT_INTERP`, nonzero entry and `DF_1_PIE`; it is never JNI-loaded. Renaming a
QEMU executable would likewise not create a JNI library. No QEMU is packaged.
AGP task dependencies build this generated entry before merging. Both variants use
`useLegacyPackaging=true` for compressed entries and installer extraction. Apart
from extraction packaging, release authority remains unchanged: no permissions,
extra components, exported worker, shared UID, app zygote or debuggable release.
Both existing JNI ABI builds remain; x86_64 has no executable and reports
`UNSUPPORTED` for the new operation.

The native inventory is two JNI `libsubstrate.so` entries plus the ARM64 executable.
Direct dependencies are platform libc/libdl for the executable and libc/libdl/libm
for JNI. No C++ runtime, runtime Maven dependency or downloaded native code is added.
The validator inspects actual APK entries and rejects extra native/hidden ELF files,
missing payload, JNI/executable substitution, wrong ABI/API/NDK notes, interpreter,
entry, dependencies, W+X loads, missing RELRO/immediate binding, executable stack,
text relocations, RPATH/RUNPATH and lost 16 KiB alignment. It checks the executable's
stack-canary reference. Packaging success establishes none of the runtime claims.

## Launch and lifecycle boundaries

`LAUNCH` is a typed parameterless operation after existing `RUN`. Caller UID,
epoch, control size, no trailing fields, synchronized endpoint and protocol state
apply. An attempt consumes the slot even on failure or Unsupported. No caller
command, argv, environment, path or FD is accepted. Only the isolated Service calls
the private JNI launch entry after checking the framework isolation predicate.

[launch.c](../../android/gate0-harness/src/main/cpp/launch.c) uses framework
`nativeLibraryDir` plus one literal basename. It opens the leaf with `O_NOFOLLOW`,
checks a regular bounded file owned by another UID, rejects group/other writable
or set-ID files, and checks ARM64 ELF/interpreter headers. The signed installed APK
and installer ownership are trusted. This is structural verification, not runtime
cryptographic attestation: `launch_payload` names the fixed version; package
inspection records its exact byte hash. Do not update/install during measurement.
There is no writable-data, alternate-loader or manager-UID fallback.

Only argv0 `pdva_launch_v1` and environment `LANG=C` go to `execve`. No shell or PATH
search exists. Child stdin is `/dev/null`; stdout and stderr are private pipes;
FD 3 is a close-on-exec error pipe. Sources are duplicated above 3 before fork to
prevent remapping collisions. The child closes 4 through 65535, including inherited
Binder, canary, scratch and shared-memory handles. Preflight rejects a larger hard
FD limit, enumeration failure or an already-open descriptor beyond that ceiling.
Only FD names/counts are inspected, never contents.

Only syscall wrappers run in the child before exec: no JNI, allocation, logging,
stdio or arbitrary callback. Bionic at-fork handlers remain trusted. A
`PR_SET_PDEATHSIG(SIGKILL)` setup and parent-PID race check cover ordinary parent
death for this fixed child. The
[upstream parent-death contract](https://www.man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html)
ties this signal to the creating thread: early Binder-thread death can abort the
experiment, and credential-changing execution can clear the setting. This payload
changes no credentials and is not set-ID. This is not hostile-descendant containment.

The direct man7 fetch timed out; the contract was additionally read from the
[upstream source mirror](https://kernel.googlesource.com/pub/scm/docs/man-pages/man-pages/+/master/man/man2const/PR_SET_PDEATHSIG.2const),
blob `1084df2c89ef542f5e5a8d91cf530253a8eda3c8`. No example code was copied.

CPU hard/soft limit is one second, core dumps disabled, and a two-second alarm is
set before exec. The wait strategy uses a 2.5-second deadline and 300-iteration cap,
then one SIGKILL and at most 50 further waits, with 10 ms pauses. Wait-ownership
loss never authorizes signalling a potentially reused PID. These are scheduling-
dependent bounds, not real-time guarantees. The 30-second worker lease and owner-
death self-kill remain; a stuck fork/runtime or lost worker is Unknown.

The payload does not fork. A matching `waitpid` acknowledges direct-child reaping.
Incomplete wait/termination remains Unknown. Management synchronously persists an
uncertainty flag **before** launch IPC and clears it only after a valid typed cleanup
acknowledgement. Lost reply, worker/owner death, malformed result or uncertain reaping
blocks sessions across app restarts. There is no UI reset or automatic retry.
Clearing data/reinstalling is not reaping evidence and is not a retry workaround.
Stop after an unresolved run; separately document a device reboot and investigation
before deliberately resetting research state.

## Bounded reports and controls

`LaunchResult` validates 24 bounded integers. Separate rows cover payload, ABI/ELF,
mechanism, creation, setup, exec errno, wait error, exit, signal, timeout, cleanup,
output, PID/UID/eUID relations, SELinux class, seccomp, effective capabilities,
extra FDs and coarse linker diagnostics. A valid payload record evidences main;
error-pipe EOF alone does not. Context is reduced to isolated-app/other/unobserved.
No new raw PID/UID, context, path, stderr or private-data field is exported. At most
256 stderr bytes are classified then discarded; no SELinux audit logs are read,
so denial attribution remains Unknown. Nonblocking pipes bound buffered output;
41 inspected stdout bytes detect oversize records. Missing/malformed output cannot
pass. The old synthetic sentinel, management-memory, delegated FD, frame/input,
worker-death and stale-session checks remain. Gate and physical labels remain
Unresolved/UNKNOWN. Clipboard export still requires the existing user button.

Native host controls exercise the shared wait strategy with fake wait/clock/kill
operations: immediate exit, EINTR, deadline/reap, ECHILD without kill, kill failure,
failed clock and frozen-clock iteration bound. They run no Android code, fork or
real signals. Locally the existing LLVM tools compile a freestanding Windows COFF
test (`--target=x86_64-pc-windows-msvc -ffreestanding -O2`) and link it with
`ld.lld -flavor link /entry:main /subsystem:console /nodefaultlib`. Linux CI uses
the runner's printed `cc` identity and a five-second timeout. JVM tests cover order,
stale/stopped epochs, replay/concurrency, result bounds and error/timeout/Unknown/
Unsupported mapping. These controls do not prove actual Android lifecycle policy.
Instrumentation is compiled, not executed.

## Adoption and build identity

All new C/Java/test/validator source is original PDVA work authorized for this PR.
No predecessor/upstream implementation or new general license was imported.
Existing NDK CRT/compiler-runtime notices and terms remain applicable; see the
[adoption record](gate-0-isolated-worker-adoption.md). The repository owner maintains
this code and tool updates. Native creation code adds research TCB surface; it is
not a production supervisor or completed security audit.

Local environment: Windows x86_64, Python 3.12.14, Temurin 17.0.20.1+1, Gradle 9.6.0,
AGP 9.4.0, SDK 37 revision 2, build-tools 36.0.0, command tools 22.0, NDK
28.2.13676358 and CMake 3.22.1. No phone/ADB/emulator. The existing **185 Maven
components / 322 hashed artifacts**, Gradle distribution hash and verification
configuration remain unchanged. No verification-write mode or bypass was used.

| Build identity | SHA-256 |
|---|---|
| Gradle verification metadata | `4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a` |
| NDK `source.properties` | `c00aa236fdb205e9be9edd9e2169763e48aca52735efff4e16f34205d49783b5` |
| Local Windows `clang.exe` | `7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579` |

Final source/package hashes and validation results are appended below. CI prints
source/compiler/native/APK hashes; Linux outputs need not match Windows. Neither
bit-reproducible APKs nor independently rebuilt tooling is claimed. Direct ELF
dependencies do not establish complete device loader closure.

## Next bounded physical experiment

1. Record exact source revision, release APK and packaged executable hashes, public
   device model/OS/security patch/ABI and stock non-rooted production status. Install
   the non-debuggable release-equivalent APK as an ordinary user app, without special
   grants, root, platform signing, shell authority or target-SDK changes.
2. With no update/install in progress, open normally and run **one fresh epoch**.
   Keep JNI, executable-memory, executable, identity and cleanup results separate.
   Compare the package to its build ledger. No phone is required for this PR.
3. On lost reply, incomplete cleanup or lockout, stop and investigate. Do not run
   cycles, clear state or use management execution. Only known cleanup permits a
   separately reviewed bounded repetition.
4. Explicitly copy only sanitized JSON and review it before publication. No serials,
   accounts, raw logcat, host paths or keys. Later evidence must distinguish
   worker-reported results from independent kernel observations and explicitly
   investigate owner death/background behavior.

Even main/exit-42 success proves neither guest boot, Android 17 guest compatibility,
TCG memory authority, acceptable performance, hostile-native lifecycle robustness
nor post-compromise containment. Persona, VPN, Google Play and image-delivery
architecture are unchanged. Gate 0 remains Unresolved.

## Final local validation and artifact ledger — 2026-10-11

Final debug/release/instrumentation APK builds, `protocolTest` and `lintDebug`
succeeded using strict existing dependency verification. Lint reported **No issues
found**; **68 JVM checks** passed. Foundation/Markdown-link validation passed for
76 source-controlled/non-ignored files, 41 Markdown documents, 54 requirements and
two ADRs. The repository suite reported **108 tests, OK, four existing Windows
exclusions**: one Linux host-C control and three POSIX mode/symlink controls. Those
existing guards were not changed or disabled and remain enabled on Ubuntu CI.
The seven new native wait scenarios separately executed successfully as Windows
host code (exit 0). They are also required in foundation CI on Ubuntu.

Both exact packaged native inventories and manifests passed inspection, including
release non-debuggability, target/minimum SDK, extraction and unchanged authority.
Python AST parsing, all six modified-workflow shell blocks (`bash -n`), whitespace,
local Markdown links, dependency metadata, binary/mode inventory and full diff
review passed. Token/private-local-path pattern checks and manual public-data review
found no new secret, private host identifier, generated binary or historical-source
import. This is hygiene review, not a claim of complete secret-scanner coverage.
A separate YAML/Markdown parser was unavailable; workflow/Markdown syntax was
reviewed as source with the foundation link checks. No package was installed or
test weakened to hide this limitation. Existing AGP deprecation warnings remain.

The local APKs were built from the final working source on verified base
`cb6eb6853b79f7035ea96e26068b3771409f3425`, before the publication commit. Their
source identity is the following content ledger, not an assertion that an earlier
base commit contains the experiment. The final PR commit captures these sources;
Git/build metadata may make a later rebuild's APK hash differ.

All 25 non-Markdown tracked/new files under `android/` have aggregate SHA-256
`d2de9462d4778e57f74184d1b24466123514d719ce58c3c923597e469aa5ecb8`.
Recompute by sorting repository-relative paths, normalizing each file's CRLF to LF,
concatenating `UTF8(path) + NUL + binary_SHA256(contents)` for each file, and hashing
the resulting bytes. Ignored build files are excluded. This covers build config,
manifest, resources, all Java/native/test source and verification metadata.

| New source identity | SHA-256 of LF-normalized bytes |
|---|---|
| `launch.c` | `def91eb93e67e3fde07bfb37db9392eefe7f9e92b72c81b87a50661140a6a050` |
| `launch_payload.c` | `80e9acaf8a14cac4df2d968480ac5dd2548ba21b5fde67ba860456ed0ac98c88` |
| `launch_wait.h` | `ecd9bacd370214fd87fd78c6680a2a3a5b3904b71e02d343fb9cc57a0c2f14be` |
| `launch_wire.h` | `c56553c1099f0ab6cd73881654a72ed45dec58cafb70706ec65eedd75bf62f70` |
| `LaunchResult.java` | `3b6723e111d5f16dbd80ad6e00265ac0ddf5633d0a91a9faf34824f303503f71` |
| `launch_wait_test.c` | `1d3af4e9d558f1a7907b18d3c1e926fb5e5c8b29df22b942cad17269c21ea7f1` |

| Locally inspected artifact, not committed/uploaded | SHA-256 |
|---|---|
| Non-debuggable release APK | `1445ddf0d06bbd0ca49ceac64c25fd386c55ed84401ff5a66f067d6c13477354` |
| Debug APK | `1236e0ca1cba0c6f915e5831da9ebb7d6d1f570a1f2aca9890aab6864e96f442` |
| Packaged ARM64 executable, same in both APKs | `6c95e1aa9342422e7c70ce8bc63c318408e628bd7eea5507aca3d4081033e789` |
| Release ARM64 JNI | `71bb7cbb85665f30c6dd92e9b3039ce34d9a04cdb1c0a2a8ebeba10dd4676b35` |
| Release x86_64 JNI | `8e78104351acc567691562e644af0e3b80ef5b75277db4d742b1fec73c365bea` |

At publication, new-head CI/checks are **pending**. No post-publication status
polling, review polling, rerun, mergeability check or CI-success claim is authorized
in this task. Physical launch, stock-device lifecycle and containment are **Unknown**.
