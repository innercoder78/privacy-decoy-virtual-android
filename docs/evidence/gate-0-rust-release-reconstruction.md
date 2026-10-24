# Android 17 Rust release reconstruction: matching records, inaccessible source

Review: **2026-10-23, America/Fortaleza; local Windows x86_64, text/metadata only.**
Question: can the exact Android 17 release Rust compiler, ARM64 standard libraries
and compatible linker inputs become a provenance-qualified research toolchain?
Scope: PDVA-REQ-002–003, 034–045, 048 and 054. **Stage 1 STOP / SOURCE-ONLY;
Gate 0 Unresolved; Gates A–G Not reached.** ADR-0001 Accepted; ADR-0002 Proposed.

**Latest disposition:** the [bounded public-mirror continuation](#public-mirror-correspondence-continuation)
below found release-named public candidates, but no authoritative correspondence
to either exact manifest revision. **STOP repetition of this provenance route
unless genuinely new correspondence evidence becomes available.** The earlier
401/404 observations below remain historical; they were not repeated.

## New result and first blocker

The official reconstruction inventory contains **build 14933020** records for
Rust **1.93.1**. Its manifest is byte-identical to the manifest in the selected
release prebuilt. This is a concrete connection between two upstream text
records, beyond the [previous prerequisite investigation](gate-0-rust-toolchain-prerequisites.md).
It is not verified source-to-binary correspondence or a reproduced toolchain.

The manifest's declared fetch host is `googleplex-android.googlesource.com`, not
the public host used by the earlier failed source-root queries. Unauthenticated
read-only requests to that declared host for both exact source revisions returned
**HTTP 401 Unauthorized** [N1, N2]. Consequently the corresponding compiler source,
Android patches and build recipes could not be inspected at their declared
revisions through this route. **Stop at this source-correspondence boundary.**
No credentials were requested or supplied to that host, and no access restriction
was bypassed. These observations do not establish universal source absence,
impossibility of legitimate access, or absence of an equivalent public export.

## Procedure and immutable text evidence

The starting branch `mirror-goog-main-rust-toolchain-source` resolved during this
investigation to **D = `b0bc6178a885a2b474f3ef4525fd05b4fb8640b3`**, whose commit
message identifies Rust 1.98.1 build 16655164. Its root tree is
`7fffce5997dab5e820d00a3a812d5b4e0d9501b0`. D is a pinned documentation/inventory
snapshot, **not** a substitute for the release build-recipe revision. Subsequent
reads used D. The retained `artifacts/1.93.1` tree is
`18cf59b575e701a20c6ecb6246eb0f347fdce926`.

P = release prebuilt repository `platform/prebuilts/rust-toolchain/linux-x86`,
revision **`fa2b1777b1f5c0471bb54ad4026feb1f6e94ea70`**. The prior merged record
supplies the release selection chain: Android `android-17.0.0_r1`, manifest
`5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f`, and Soong
`6722dd8833db7482df1a2543ca3fcf67ddf0f7b1` selecting 1.93.1. That broad survey
was not repeated. This continuation freshly retrieved P's build manifest.

Procedure: HTTPS Gitiles file reads with `?format=TEXT`, base64-decoded before
SHA-256; directory reads with `?format=JSON`, hashing the received UTF-8 text
including Gitiles' prefix. Requests used a 30-second timeout; all retained
successful receipts were below 8 KiB. No upstream script was executed. Public
text hashes below identify receipts, not signatures, compiler hashes or private
artifacts. A web-view cache miss on the starting URL was followed by successful
direct Gitiles retrieval; it was not treated as upstream source absence.

| ID / exact source URL | Bytes / SHA-256 / observed result |
|---|---|
| [D1 README](https://android.googlesource.com/toolchain/android_rust/+/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3/README.md?format=TEXT) | 2678; `7633097e037b316c936a2cbe7cadba26e26122178a497222b6478b4206df9d2e`; HTTP 200 |
| [D2 artifact directory](https://android.googlesource.com/toolchain/android_rust/+/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3/artifacts/1.93.1/?format=JSON) | 1510; `24900aacde78daa740f6f911b9c52535fe7e431feaf3709f4a6fbe9072bbf6f9`; HTTP 200 |
| [D3 reconstruction manifest](https://android.googlesource.com/toolchain/android_rust/+/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3/artifacts/1.93.1/manifest_14933020.xml?format=TEXT) | 7443; `99c9b965b1a61ae49426ec9480f933d39fdee7aa37d78668667fbae9319ea698`; HTTP 200 |
| [P1 release-package manifest](https://android.googlesource.com/platform/prebuilts/rust-toolchain/linux-x86/+/fa2b1777b1f5c0471bb54ad4026feb1f6e94ea70/1.93.1/manifest_14933020.xml?format=TEXT) | 7443; `99c9b965b1a61ae49426ec9480f933d39fdee7aa37d78668667fbae9319ea698`; HTTP 200; same bytes as D3 |
| [D4 Linux build command](https://android.googlesource.com/toolchain/android_rust/+/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3/artifacts/1.93.1/rust_build_command.linux-x86.14933020.sh?format=TEXT) | 391; `d794b2551b3843261c62304171cfc2e88189a1319b2f5c7e0097706b468c30de`; HTTP 200 |
| [D5 version record](https://android.googlesource.com/toolchain/android_rust/+/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3/artifacts/1.93.1/rust_version?format=TEXT) | 29; `75afd87d9a7c29f48f98a4ee7b3f3692692bde72c771d46c71e8871a3d50013a`; HTTP 200 |
| [D6 setup documentation](https://android.googlesource.com/toolchain/android_rust/+/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3/documents/SETUP.md?format=TEXT) | 1810; `1238d11110cb4484a96bf74eee4584e378db7b870026cecb17f340f0a6a48ca5`; HTTP 200 |
| [N1 declared recipe source](https://googleplex-android.googlesource.com/toolchain/android_rust/+/fd3c251016559fa70d31861d507dde14160515a2/?format=JSON) | HTTP 401 Unauthorized; source not retrieved |
| [N2 declared compiler source](https://googleplex-android.googlesource.com/toolchain/rustc/+/3b396167a567d74f6fe75444780fc25832928858/?format=JSON) | HTTP 401 Unauthorized; source not retrieved |

## What the reconstruction records actually establish

D1 instructs reconstruction from the prebuilt manifest using Repo, then the saved
version/build-specific command, with profile paths replaced by inventory paths.
It documents a `repo sync` parallelism of 16. This is an upstream procedure,
not a successful local execution or a measured memory/disk/time budget. D6's
development setup uses an authenticated SSO source route and a broader Android
checkout for testing and profile generation. Neither instruction grants access
or justifies silently provisioning a host, syncing a large source graph or
installing the suggested tools.

D3/P1 name compiler revision `3b396167a567d74f6fe75444780fc25832928858` and
recipe revision `fd3c251016559fa70d31861d507dde14160515a2`, under default branch
`rust-1.93.0-release`. D5 records `1.93.1 (01f6ddf75 2026-02-11)`; this is
stored version text, not observed `rustc --version`. The different branch name,
full source revision and short version hash are not silently conflated. Their
source relationship remains unverified at the STOP boundary.

D4 invokes `toolchain/android_rust/tools/build.py`, selecting build name
`14933020-linux-x86`, BOLT name `bolt-14933020-linux-x86`, static LLVM linkage,
thin LTO, one codegen unit and emitted relocations. It references cached PGO,
BOLT and a wildcarded prebuilt LLVM builders archive. D2 lists
`llvm.14926043.profdata`, `rust.14926043.profdata` and
`bolt-profiles-14926043.tar.xz`. Their Git blob identifiers are inventory metadata;
their bytes were not acquired. The differing profile/build IDs do not by
themselves prove a mismatch; exact application and fallback semantics require
the release recipe. The LLVM archive's exact expanded name, bytes and provenance
are not established by the saved wildcard. PGO/BOLT completeness is unverified.

The manifest also pins LLVM source `2d65e4108033380e6fe8e08b1f1826cd2bfb0c99`,
LLVM Android recipes `5f256f3c301c8be09c02a71119cb5505f4ff5ddc`, Linux Clang
prebuilts `3abca941ab774253b8447d71e14f72b40ed9fc95`, and NDK releases
`fe7dffc28e346df68199eefc0f1f3b6dbe6a669e`. These are declared reconstruction
inputs, not inspected source closure or a chosen Android linker. The manifest's
Rust prebuilt input revision `cf75859632dd17b3a0bf25040f92e12b588a8d7d` is not P;
an input prebuilt cannot be mistaken for the selected output distribution.

## Separate readiness dispositions

| Classification | Exact scope and remaining gap |
|---|---|
| SOURCE CONFIRMED | Only the fetched documentation, inventory, manifest, saved command and version text. Full compiler source, Android patch set and exact recipe contents remain UNKNOWN. |
| BINARY IDENTITY CONFIRMED | **Not established.** P/1.93.1 and build 14933020 identify the selected distribution in metadata; no compiler/component byte hashes or signatures were independently verified. |
| SOURCE/BINARY CORRESPONDENCE CONFIRMED | **Not established.** Matching manifests connect records, not installed bytes or reproducible outputs; exact source retrieval is blocked. |
| LICENSE/RIGHTS CONFIRMED | **Not established** for the complete compiler, target libraries, profiles, cached LLVM and native closure. Public availability of text is not blanket redistribution authorization. No component adoption or binary redistribution occurs. |
| INSTALLATION READY | **Not established.** Selected package is Linux-hosted, with x86_64 execution expected from its Linux-x86 host context; actual executable ABI/loader and host requirements were not inspected. Exact resource budget remains UNKNOWN. Stage 2 NOT RUN. |
| EXECUTION OBSERVED | **None for the toolchain or Android.** Stage 3 NOT RUN. Text retrieval and repository validation are separate observations. |
| UNKNOWN | Usable `aarch64-linux-android` std bytes, actual compiler/sysroot resolution, selected linker/Bionic/native inputs and API compatibility. Prior target-directory evidence lists libraries; it does not authenticate them. NDK r28c/28.2.13676358 remains an existing lead, not the release Rust compiler or a demonstrated compatible linker selection. |

No compiler archive, library, profile or LLVM binary was acquired or executed.
No WSL/Docker/compiler inventory was repeated; no execution host was provisioned.
No Cargo/rustup/newer-release substitution, backend port, phone/ADB work, guest
boot, APK integration, security-setting change or hosted research workflow was
performed. Opaque components are not adopted into the product TCB.

## Controls, tests and excluded conclusions

**RUN:** successful reads of D1–D6 and P1; identical D3/P1 length and SHA-256;
manifest-declared N1/N2 requests returning 401. The positive public reads and
failed declared-source reads distinguish accessible records from inaccessible
source. The historical public-root 404s were not retried or relabeled as new
results. These are retrieval outcomes, not synthetic compiler negative controls.

**NOT RUN:** compiler executable identity/version measurement; synthetic C-ABI
Rust `cdylib`; incompatible-target/missing-linker negative control; independent
ELF reader; ELF machine/class/type, exported symbol, undefined imports,
DT_NEEDED, PIC/relocations, TLS, panic/unwind, Bionic/API checks, program headers
and 4-KiB/16-KiB alignment. There is no resulting ELF, so every corresponding
ABI assertion is NOT RUN, including properties suggested by expected flags.

Even a later tiny-library success would establish only its observed build/ABI.
It would not supply a backend/JNI entrypoint, safe preopening, process/SELinux
confinement, revocation of mapped RAM or retained FDs, guest boot, guest/host
security, ordinary-app authority, Play availability or Gate 0 passage. The
[backend blockers](gate-0-backend-endpoints.md) and
[communication limits](gate-0-userspace-communication.md) remain independent.
All product, privilege, Persona, policy, networking and guest requirements remain
unchanged; no architecture decision follows from this source investigation.

**Smallest next proof:** obtain an authoritative accessible export or legitimate
access mapping for the two manifest-pinned source revisions, including Android
patches and exact recipe/license contents, tied explicitly to build 14933020.
Do not repeat the public-root probes or substitute the current branch. Then
resolve that recipe's cached LLVM/profile identities and rights before acquiring
compiler/target/linker bytes or qualifying a bounded Linux host. This task does
not claim the required mapping is absent everywhere or authorize a new host.

## Repository preflight, preservation and validation

GitHub main API, independent `git ls-remote` and fetched main agreed on
`ff444b9cf1f0ca457456de3460b99b5c679d3945`. PR #32 is merged at that SHA; its
recovery and prerequisite records are present, and the initial checkout tree
matches main. All-open-PR inventory returned zero: no open diff/files, head/base,
checks, jobs/logs, reviews, comments or review threads required reconciliation.
One worktree, clean tracked tree, no stashes; existing branches and ignored
assets were preserved. No applicable AGENTS.md or tracked nonregular mode was
found. Both ADRs, requirements, evidence criteria, source policy/catalog,
governance, dependency records, relevant binary/build declarations and history
were read. The historical repository was untouched.

Existing exact-main [run 40003089526](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40003089526)
and full job logs were inspected: foundation job **120583990553** and
offline-image-windows job **120583990178** succeeded. Logs identify the exact
main SHA, Linux repository/desktop/scanner suites of 141/27/45 tests and Windows
45 scanner tests, plus existing native/model controls. These are prior hosted
observations, not this investigation's Rust execution or new-head validation.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational. Foundation applies to this documentation PR; existing
Android/QEMU path filters do not select these files. Absence is not a pass.

A private ignored checkpoint and bounded source receipts were retained locally.
Independent private backup is **unverified**, leaving a private retention gap;
the public-safe findings are preserved through the single intended evidence PR,
pending review and merge. No private paths, host identifiers, raw logs, binaries
or private hashes belong to that PR. New hosted checks remain
**pending/unobserved at publication**; no post-publication CI/review polling.

Local validation used the existing NDK-bundled Python **3.11.4**, with synthetic
fixtures only; the toolchain research itself remained stopped:

| Command | Observed local result |
|---|---|
| `python .github/scripts/validate-foundation.py` | PASS: 127 files, 76 Markdown files, 54 requirements, two ADRs; internal file links and tracked modes included. |
| `python .github/scripts/validate-harness.py` | PASS: manifest/source authority; no installed Android result. |
| `python .github/scripts/test-repository-validation.py` | 141 total: 137 passed, four existing Windows/platform skips; no failures. |
| `python .github/scripts/test-desktop-readiness.py` | 27 passed, no skips. |
| `python .github/scripts/test-offline-image-inspect.py` | 45 passed, no skips; synthetic fixtures, not a toolchain ELF inspection. |
| `git diff --check` | PASS. |

The complete two-file Markdown change, source receipts, links, regular modes,
dependency scope and public-data hygiene were reviewed. Receipt files were
rehashed with no mismatch. Platform skips concern Linux native execution,
symlink and POSIX-mode coverage; they are not passes. No code, dependency,
workflow, runtime or product behavior changed.

## Public-mirror correspondence continuation

Review: **2026-10-23, America/Fortaleza; Windows x86_64; source/metadata only.**
Question: does the officially documented public mirror establish correspondence
to compiler `3b396167a567d74f6fe75444780fc25832928858` **and** Android recipe
`fd3c251016559fa70d31861d507dde14160515a2` for Rust 1.93.1 build 14933020?
**No qualifying mapping was established. Both remain UNKNOWN.** This closes the
specific public-mirror discriminator left by PR #33 without asserting universal
source absence or impossibility of PDVA, Android Rust or ordinary-app virtualization.

### Bound, environment and export contract

The investigation used existing Git/PowerShell HTTPS readers, GitHub metadata and
existing Python for repository checks. No compiler acquisition, tool installation,
source clone/sync, archive download, upstream script execution or new environment
occurred. The limit was 30 direct Gitiles text/metadata requests, at most two
100-entry history pages per repository; **28 requests were made**, including two
repeated head reads to retain receipts after oversized console output. Two narrow
web discovery queries located the documented export statement; unrelated returned
results were not followed. Two initial web mirror-page reads failed with a reader
cache miss; direct public HTTPS reads succeeded. A cache miss is not an upstream
404. No protected service was queried, credentials requested or bypass attempted.

The compiler head's commit JSON unexpectedly included a large tree diff
(13,352,038 bytes); it was retained locally as metadata, not a source archive or
binary. Subsequent investigation used compact histories and selected files.
The three history receipts contain 100 + 100 recipe entries and 98 compiler
entries. The compiler response has no next cursor; the second recipe response
does, and was deliberately not followed. This is not an exhaustive search of
every branch, ref or possible export. Neither exact requested revision appears
in those histories' commit/parent/message records.

The public `android_rust/main` documentation pin is
**M = `c4dbee9ebc9af3d3084786951ca129b72ee916ff`**.
[M documents/BUILDS.md](https://android.googlesource.com/toolchain/android_rust/+/c4dbee9ebc9af3d3084786951ca129b72ee916ff/documents/BUILDS.md)
states that development moved internally, identifies the public mirror branch,
and leaves public mirrored top-of-tree reproduction guidance for the future.
It does **not** specify a historical release mapping, commit-identity preservation,
tree-equivalence guarantee or complete-input export contract. The pinned mirror
README's manifest-based reconstruction guidance and SETUP's authenticated source
route, already recorded as D1/D6, supply no such mapping either. Reading an
instruction is not executing or qualifying it.

### Immutable identities and release candidates

| Official public source | Direct observation and limit |
|---|---|
| [Recipe mirror head D](https://android.googlesource.com/toolchain/android_rust/+/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3) | Fresh branch resolution agrees with PR #33: `b0bc6178a885a2b474f3ef4525fd05b4fb8640b3`, tree `7fffce5997dab5e820d00a3a812d5b4e0d9501b0`, message names 1.98.1 build 16655164. Not the 1.93.1 recipe. |
| [Compiler mirror head](https://android.googlesource.com/toolchain/rustc/+/7c63db00dbb7e83b8b8b0de26ce80d121307ffa6) | `7c63db00dbb7e83b8b8b0de26ce80d121307ffa6`, tree `514650faa8a5bfcfa53aa7dfa00afa549e7ee765`, imports 1.98.1. Not the historical release. |
| [Compiler history](https://android.googlesource.com/toolchain/rustc/+log/7c63db00dbb7e83b8b8b0de26ce80d121307ffa6?format=JSON&n=100) | Reveals candidate **C = `cc5730c125b43b896979e633fcaa222625d9b108`**, message `Import rustc-1.93.1`, tree `e68eac89129665e552693739c27099b1655f9b94`, parent `4234e9069232aa43f125da57b4a64b3f2fb631d1`. No mapping to `3b396167...` in its message. |
| [Recipe history page 1](https://android.googlesource.com/toolchain/android_rust/+log/b0bc6178a885a2b474f3ef4525fd05b4fb8640b3?format=JSON&n=100), [page 2](https://android.googlesource.com/toolchain/android_rust/+log/a0a9b72409ed5ad72a81d44c8db32b05f57c5ef8?format=JSON&n=100) | Reveals candidate **R = `cae2c8431b3a1c9cf351bb916c051c131616e263`**, message `rustc-1.93.1 Build 14933020`, tree `435c7b2695f2b45d94325110edfaec47dadb3b83`, parent `baa85ee93572b620f54f403f8b0d7800456339cd` (profile update). No mapping to `fd3c2510...`. |
| [R commit metadata/diff inventory](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263?format=JSON) | Adds the manifest, four host build-command records and rust_version; modifies `src/android_rust/paths.py`. This is publication of build records, not proof that R itself was the recipe used to create the build. |
| [R release manifest](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263/artifacts/1.93.1/manifest_14933020.xml) | 7,443 bytes; SHA-256 `99c9b965b1a61ae49426ec9480f933d39fdee7aa37d78668667fbae9319ea698`, matching retained D3/P1. It still names the two internal revisions and declared internal remote; it does not map them to C/R. |
| [C git-commit-hash](https://android.googlesource.com/toolchain/rustc/+/cc5730c125b43b896979e633fcaa222625d9b108/git-commit-hash), [git-commit-info](https://android.googlesource.com/toolchain/rustc/+/cc5730c125b43b896979e633fcaa222625d9b108/git-commit-info) | Source text names `01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf`, short `01f6ddf75`, date 2026-02-11. This agrees with D5's version string, but does not authenticate equality to the manifest compiler revision or Android-patched build input. |

C and R are legitimate public candidates, not uncertain third-party mirrors.
Their Git identities differ from the manifest pins. Different commit IDs alone
do not prove different contents, but no independent internal/public tree digest,
authoritative revision crosswalk or reproducible corresponding source/package
attestation was found in the inspected records. Shared version text, issue or
Change-Id context, filenames, chronological proximity, branch naming and matching
manifest copies cannot establish that missing equality. No candidate was adopted.

### Android patches, recipe and disclosed rights

At R, [tools/build.py](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263/tools/build.py)
defaults to copying and patching compiler source and calls `source_manager.setup_files`.
[source_manager.py](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263/src/android_rust/source_manager.py)
recursively selects `rustc-*` patches, sorts by filename, checks unique patch
numbers and applies them with `patch -p1 -l`, failing on nonzero status.
[paths.py](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263/src/android_rust/paths.py)
identifies the separate patch and output-source paths. This is static candidate
behavior; no patch or build command was executed.

The [development directory](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263/patches/development/)
contains seven patch entries (tree `74e86f3e2c52e1137cff6d2888e47586ce8eed29`);
the [longterm directory](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263/patches/longterm/)
contains four (tree `225bfca9a813668aee7db1fb709bf2c001286d47`). The inspected
[Android abort-message patch](https://android.googlesource.com/toolchain/android_rust/+/cae2c8431b3a1c9cf351bb916c051c131616e263/patches/longterm/rustc-0014-Statically-link-android_set_abort_message.patch)
replaces dynamic symbol lookup with a direct `libc::android_set_abort_message`
call in panic-abort source. Thus a matching vanilla Rust version string omits
material Android build-input distinctions. The eleven candidate patch entries
are not proven to be the patch set at the manifest's recipe revision. Only one
patch's contents were inspected; no full patch-set audit or application is claimed.

[C COPYRIGHT](https://android.googlesource.com/toolchain/rustc/+/cc5730c125b43b896979e633fcaa222625d9b108/COPYRIGHT)
discloses Apache-2.0/MIT defaults with exceptions, in-tree REUSE/license metadata,
Cargo-tracked external dependencies and generated binary-release copyright
inventories. Its README also discloses BSD-like portions. R's three inspected
Python files carry Apache-2.0 notices; its root listing has no blanket LICENSE
file. These are file/project disclosures, not a full transitive license audit,
rights to inaccessible material or distribution clearance for build 14933020.
The public patch has provenance headers; a header is not complete license closure.
No release mapping was established on which to assert complete source/rights
verification. Cached LLVM, profiles, target libraries and binary correspondence
remain the separate prerequisites already recorded above.

### Separate dispositions and STOP

| Category | Result |
|---|---|
| Public mirror existence and immutable identity | **VERIFIED**, limited to D, compiler head, C/R and the inspected public records. |
| Exact compiler revision mapping | **UNKNOWN**: C is not the manifest commit; content correspondence unproved. |
| Exact Android recipe revision mapping | **UNKNOWN**: R publishes records but no equivalence to the manifest recipe. |
| Android patch correspondence | **UNKNOWN**: candidate patches/application path visible, exact release correspondence absent. |
| License/source completeness | **UNKNOWN** for the release and its full input closure. |
| Build-input equivalence | **UNKNOWN**, including patched source, cached LLVM and profile application. |
| Actual compiler binary identity | **NOT VERIFIED**. |
| Source-to-binary correspondence | **NOT VERIFIED**. |
| Toolchain installation/readiness | **NOT VERIFIED**. |
| ARM64 cdylib build | **NOT RUN**. |
| ELF/ABI inspection | **NOT RUN** for this toolchain; repository synthetic fixture tests are separate. |
| Android device/guest execution | **NOT RUN**. |

**STOP this exact Rust provenance route.** Do not schedule another similar mirror
survey or repeat the historical 404/401 probes because the answer remains Unknown.
Reopen only for genuinely new evidence: an authoritative release-export mapping
covering both pins and Android patches, legitimate authorization to the exact
sources, or independently reproducible matching source/package provenance.
Such evidence would first resolve source correspondence; binary identity,
source-to-binary reproduction, complete rights and host/toolchain qualification
would still need separate proof before an ARM64 build.

**Gate 0 Unresolved; Gates A–G Not reached.** The full interactive Android 17/API
37 guest under ordinary distributable stock nonrooted app authority remains the
contract. No engine selection, guest implementation, privileged substitute,
Persona/network/permission change or architecture decision follows. Host/guest
isolation, hostile native execution, lifecycle/descendants, FDs, mapped RAM and
revocation remain unproved. No phone, ADB, APK installation or runtime activation.

### Continuation preflight, receipts and preservation

Live GitHub main API, `git ls-remote` and fetched main agreed on
`243d3977944149baaf5d205612d9f9ebc8cca57e`; PR #33 is merged there. PR #31/#32
merged identities and relevant findings were checked against their records.
All-open-PR inventory was empty, so there were no open heads/bases, entire diffs,
files, checks, jobs/logs, reviews, comments or review threads to reconcile.
Governance, requirements, both ADRs, gates, provenance policy/catalog, acceptance
criteria, evidence index and prior Rust/backend/recovery records were read.
Dependency/binary declarations and workflows were inspected. One worktree, clean
tracked tree and no stashes preceded the new branch; existing branches, ignored
assets and unrelated files were preserved. No applicable AGENTS.md or tracked
nonregular file mode was found. The historical repository remains read-only.

Existing exact-main [run 40039756781](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40039756781)
has successful foundation **120707791569** and offline-image-windows
**120707791726** jobs. Their downloaded logs identify the exact baseline and
141/27/45 Linux repository/journal/scanner tests, native/model controls and
45 Windows scanner tests. These are existing baseline observations, not new-head
or Rust execution. [GitHub Status](https://www.githubstatus.com/api/v2/status.json)
reported All Systems Operational. Foundation applies; Android/QEMU workflow path
filters do not select these two Markdown files. Filtered/unrun is not passed.

Public source receipts were retained locally, with Gitiles TEXT base64-decoded
before hashing. Selected SHA-256 receipts for independently repeatable checks:

| Source identified above | Bytes | SHA-256 |
|---|---:|---|
| M documents/BUILDS.md | 16766 | `9130c6709c316c0e83849a634bb9388be08e002d77d665628b65347bf0bf08b7` |
| R tools/build.py | 30269 | `7381b5890648b0d676033217c931ae5ea02e501a85f67c26b479aebbf0e3f212` |
| R source_manager.py | 5178 | `a9c41ea1a0b4f3fe0facbf8722413757af92fbcde5cbc7bdad229fd00eed12da` |
| R Android abort-message patch | 3034 | `e313d7d2ebc16adf1aad5c0f4fd5e0a6c10f7b6d87637faca28593b2d8aebc6b` |
| C COPYRIGHT | 1571 | `172020dbfd5b53a226dfde77616190a48dcff519b0bc0e6deb91a8450782c4af` |

Private local receipts/checkpoint are retained; independently backed-up
owner-controlled private retention is **unverified**, leaving a recovery gap.
Only this public-safe disposition and index are intended for the single evidence
PR, pending independent review and merge. No raw logs, private paths/identifiers,
private hashes, credentials, binaries, upstream implementation, new dependencies
or license adoption are included. New hosted CI remains **pending/unobserved at
publication**; stop after one immediate PR identity and native association check.

Local validation used existing Python **3.11.4** with synthetic fixtures only:

| Check | Observed result |
|---|---|
| `validate-foundation.py` | PASS: 127 files, 76 Markdown files, 54 requirements, two ADRs. |
| `validate-harness.py` | PASS: manifest/source authority only. |
| `test-repository-validation.py` | 141 total, 137 passed, four existing Windows/platform skips. |
| `test-desktop-readiness.py` | 27 passed, no skips. |
| `test-offline-image-inspect.py` | 45 passed, no skips; synthetic inputs, no toolchain ELF. |
| `git diff --check` | PASS. |

The complete two-file diff was reviewed for source claims, public-data hygiene,
licenses, dependencies, links and unchanged regular `100644` modes. No new tests
or upstream code were added. Windows skips and unrun Linux-native checks are not
passes; existing hosted baseline observations remain separately attributed.
