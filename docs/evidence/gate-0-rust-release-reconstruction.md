# Android 17 Rust release reconstruction: matching records, inaccessible source

Review: **2026-10-23, America/Fortaleza; local Windows x86_64, text/metadata only.**
Question: can the exact Android 17 release Rust compiler, ARM64 standard libraries
and compatible linker inputs become a provenance-qualified research toolchain?
Scope: PDVA-REQ-002–003, 034–045, 048 and 054. **Stage 1 STOP / SOURCE-ONLY;
Gate 0 Unresolved; Gates A–G Not reached.** ADR-0001 Accepted; ADR-0002 Proposed.

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
