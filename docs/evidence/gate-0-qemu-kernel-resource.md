# Gate 0: ARM64 kernel-resource pathname investigation

**2026-10-15, America/Fortaleza. Gate 0: Unresolved; Gates A–G: Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No engine is adopted.

The pinned QEMU direct-boot path does **not** provide an authenticated,
descriptor-only raw ARM64 kernel interface. A narrowly bounded descriptor reader
is technically plausible, but replacing only `load_aarch64_image` would leave
earlier ambient ELF/uImage probes reachable. This investigation therefore takes
the authorized **smaller, falsifiable control** option: source-verified witnesses
of the existing loader's pathname and bounds behavior, with an explicit admission
contract for a later adapter. No kernel adapter is implemented or integrated.
This is a scoped implementation deferral, not evidence of fundamental infeasibility.

Scope: PDVA-REQ-002–003, 006–015, 034–045, 048, 051, 054. The
[worker-integration review](gate-0-qemu-worker-integration.md),
[source policy](../source-provenance-policy.md),
[security boundaries](../security-boundaries.md) and
[evidence criteria](../acceptance-evidence-criteria.md) remain governing records.

## Independent preflight

GitHub branch API and independent `git ls-remote` both resolved canonical main to
`a99c6b26b28dad328cc410b786ff96d999ae7bb4`. Local main matched; tracked state was
clean, with one worktree and no stashes. Local/remote branches and ignored build,
dependency and binary locations were inventoried and preserved. The historical
Privacy-Decoy repository was untouched. No applicable AGENTS.md was found.
All tracked file modes were `100644`. No generated binary or dependency is added.

Open PR inventory was **zero**: no open heads/bases/diffs/checks/reviews/comments
or unresolved threads existed to reconcile. Merged [PR #10](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/10)
had head `827d97db7b0d7675a0def3c2464f1d5ab92f83bf`, base
`6bb491d3b8e40cf066bc1d71406f43fe8934a8d0`, and merge commit equal to current main.
Its complete four-file merged diff was reviewed. Reviews, conversation comments,
inline comments and review threads were empty. Its foundation, Android and QEMU
checks succeeded. Main's exact-head foundation and Android checks also succeeded;
combined commit status had zero contexts (its aggregate `pending` is not a check).
All three workflows were active; exact-head checkout, filters, permissions,
timeouts and build controls were inspected. GitHub Status reported All Systems
Operational, page update `2026-10-15T17:28:05.728Z`. Initial sandbox network requests
failed; successful read-only network retries supplied these observations.

The actual [PR #10 QEMU log](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38509812333)
at its exact head records all 40 modeled allocation cases plus seal failure,
the two expected fallback-mutant failures, and all seven configuration rejections.
It also records successful Android dynamic PIE inspection and the final completion
marker: QEMU size **66,987,144 bytes**, SHA-256
`ca9bb3d21df4bf91be12b02fe5c872b4157596753948dd9991d40b880fd2b801`, direct
`DT_NEEDED` = `libz.so`, `libm.so`, `libc.so`. This updates the historical
pending-at-publication observation in the [TCG record](gate-0-tcg-executable-memory.md);
it is log evidence, not a downloaded/rehashed binary or Android execution.
The strict TCG transformation and its controls are unchanged by this work.

Requirements, ADRs, gates, source/provenance and boundary records, cross-build
evidence and the unresolved [native-host incident](gate-0-native-host-antivirus.md)
were reviewed. The existing archive/NDK/wheel/Git pins, dependency graph and
licensing remain unchanged: QEMU, GLib, PCRE2, libffi, libfdt, proxy-libintl,
GVDB and QEMU subproject tooling retain the existing research scope. No new
package, compiler, SDK, runtime dependency or target execution is introduced.
Retained binaries are inventory only, not freshly attested artifacts.

## Exact source and caller audit

The clean retained QEMU checkout is commit
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`; upstream GitHub's commit API
independently matched both. Every file below matched its immutable Git blob after
local CRLF normalization. CI requires the raw LF identities in `QEMU_BOOT_INPUTS`
in the [recipe](../../.github/scripts/qemu-android-research.py), after the existing
whole-archive SHA-256 verification. It does not normalize downloaded inputs.

| Pinned source | Reviewed behavior and scope |
|---|---|
| [hw/arm/virt.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c) | `machvirt_init` invokes firmware initialization before `arm_load_kernel`. `virt_firmware_init` can search/load a BIOS path or use pflash; raw-kernel admission alone cannot cover these. |
| [hw/arm/boot.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c) | `arm_load_kernel` copies machine filenames and selects firmware/direct boot. `arm_setup_direct_kernel_boot` tries `arm_load_elf`, then uImage, then the AArch64 Image path. Initrd and later DTB loading are independent paths. |
| [hw/core/loader.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/loader.c) | ELF header and ELF image functions use ordinary `open`; uImage/ramdisk delegate to `load_uboot_image`, also ordinary `open`. Gzip probing and ROM file loading use GLib pathname readers. `get_image_size` alone uses `qemu_open`; subsequent raw ROM loading still uses a filename. |
| [util/osdep.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/osdep.c) | `qemu_open_internal` recognizes `/dev/fdset/N` and calls `monitor_fdset_dup_fd_add`; ordinary names use `qemu_open_cloexec`. This is a QEMU helper convention, not an OS-wide pathname mechanism. |
| [monitor/fds.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/monitor/fds.c) | FD-set lookup matches access flags (and O_DIRECT when available), duplicates one matching descriptor and tracks the duplicate. It does not authenticate bytes, ensure immutability, or uniquely select a resource among multiple matching descriptors. |
| [system/vl.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c) | `parse_add_fd` requires an inherited valid non-CLOEXEC FD above stderr and nonnegative set ID, duplicates CLOEXEC into the set; `cleanup_add_fd` closes originals. This is not an Android delegation experiment. |
| [system/device_tree.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/device_tree.c) | External DTB uses `get_image_size` followed by ordinary-open `load_image_size`; ARM's caller first uses `qemu_find_file`. Generated virt DTB is a different path. |
| [hw/nvram/fw_cfg.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/nvram/fw_cfg.c) | Firmware kernel/initrd loading uses gzip probing/GLib reads; shim loading uses `g_mapped_file_new`. Firmware mode bypasses the direct Image leaf. |
| [include/hw/core/loader.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/hw/core/loader.h) | Supplies the extracted decompression cap and loader declarations. That cap is not a bound on the raw pathname read. |

The principal hashes are `3ee33e386c78e816410d7f897d616a1f2c44203e7a609671184a95153412311f`
for boot.c and `5adca2184d46e03eed1122fa9c6e920fe8ffc340be7507021ed5afe53b1c47f0`
for loader.c. The recipe lists all nine full-file hashes, including unchanged callers.

At boot.c:826, gzip probing reads the whole file through `g_file_get_contents`
before checking gzip magic. A raw input then reaches another `g_file_get_contents`
at line 832. The second buffer goes through EFI zboot handling, then optional
ARM64 header parsing, then ROM registration at line 885. Missing ARM64 magic is
accepted as legacy raw input. `text_offset`, declared `image_size`, actual byte
length and available guest RAM are different quantities. The caller's RAM-size
check occurs after the leaf has registered the blob; it cannot serve as a
pre-allocation or pre-publication bound. These are findings about this candidate
capability contract, not claims of a demonstrated upstream vulnerability.

**Inference:** `/dev/fdset/N` cannot make this entire chain descriptor-only.
`/proc/self/fd/N` would still reopen a pathname and is not an accepted substitute.
Replacing the leaf's GLib calls alone leaves earlier format probes, optional
initrd/DTB and firmware paths. No claim is made that all QEMU file access has been
enumerated or that arbitrary native code is confined.

## Smaller falsifiable experiment

The recipe verifies all nine files, extracts the unchanged
`load_image_gzipped_buffer` and `load_aarch64_image` functions and their constants,
and preserves both upstream file notices in temporary generated C. ARM boot code
is GPL; loader.c carries permissive and GPL-derived gunzip notices. Existing QEMU
license obligations continue to apply. No upstream engine file is committed.

Linux CI compiles this extraction with ordinary host `cc -std=c11 -O0 -Wall
-Wextra -Werror` and a five-second execution timeout. GLib IO, decompression/zboot
and ROM publication boundaries are modeled. Fixtures are 1 or 64 synthetic bytes;
they are not kernels and are never executed. No real file is opened by the modeled
reader. Decompression is deliberately outside the witness; reaching it is fatal.

| Case | Required source-derived observation, not a runtime result yet |
|---|---|
| Raw 64-byte header | Two pathname requests, one blob, exact entry/length and buffer cleanup. |
| Both pathname reads fail | Two attempts, failure sentinel, no entry/blob publication. |
| Second read fails | First buffer freed, failure, no publication. |
| Different bytes on second read | Published byte is from the second read; first read does not bind input identity. |
| One-byte non-Image | Accepted by the leaf as legacy raw; demonstrates absence of the proposed strict format admission. |
| Declared image size UINT64_MAX | Blob registered before returning this value; caller rejection is not transactional admission. |
| Large text offset | Unsigned load-address addition wraps below RAM base in the leaf; no guest memory is touched by the observer. |

The separate `--deny-paths` run must terminate on the first observed GLib
pathname call with **exit 93 and exactly `DENIED: GLib pathname read`**. It
demonstrates that even the leaf cannot run under a no-pathname policy. Normal
execution must independently exit zero with the exact seven-case completion line.
Missing output, unrelated errors, signals, compiler failure and timeout cannot
count as either result. This denial is a test observer, not an OS sandbox.

This is **not** a no-fallback adapter test: no adapter exists to mutate. Invalid
FD, short `pread`, authentication mismatch, descriptor cleanup and immutable-object
enforcement are **not tested**. The experiment deliberately does not relabel these
as passing because modeled pathname failures were observed. Whole-caller execution,
actual GLib/kernel filesystem behavior and QEMU guest-memory registration remain
outside the extraction; caller bypass findings above are static source evidence.

## Contract required before an adapter is defensible

The next experiment should have an exclusive raw-resource entry before any ELF,
uImage, gzip or firmware dispatch, and a terminal failure outcome with no format
fallback. Admission must reject firmware/pflash, external DTB/initrd/shim and all
other external boot resources for that experiment; use only the generated virt
DTB. Enforce this at the relevant callers, not through a filename convention or
an assumption about a future launcher. It does not require granting new privileges.

The proposed research API should take one owned read-only regular-file descriptor,
an explicit resource type/version, expected length, authenticated digest and a
bounded guest-memory interval. It must bind these to the same bytes: an O_RDONLY
descriptor alone does not prevent a separate writer changing the underlying file.
A bounded private snapshot whose digest is checked before parsing/publication is
one candidate; the digest itself must come from an authenticated trusted manifest,
not the hostile worker. Neither signature verification nor a trust root is supplied
by this investigation. Linux sealing is another hypothesis, not proven Android FD
authority. Duplication does not reduce descriptor access rights.

Use positional bounded reads without pathname reopening; reject nonregular,
invalid and writable descriptors, zero/truncated/oversized lengths, unknown format
versions and unsupported gzip/ELF/uImage/zboot. Require an explicit ARM64 header
policy, including modern nonzero image size and admitted flags; legacy input is
outside the initial format. Bound allocation before reading, handle short reads
and EINTR with a finite budget, check offset/length conversions and overflow before
every addition, and validate both actual-byte and declared-image guest intervals
before publishing anything. Define descriptor ownership on all returns, free
partial buffers and publish no state on failure. Closing a duplicate is cleanup,
not revocation of other copies or mappings.

A future falsifier must observe forbidden open/openat/GLib/path-resolution calls
independently across the **whole admitted caller path** and deliberately reintroduce
fallback to show that observer fails. It must cover malformed headers, truncation,
oversize, invalid/writable descriptors, short read/EINTR exhaustion, concurrent
mutation, digest mismatch, arithmetic overflow, unsupported formats and cleanup.
Do not infer those properties from this much smaller witness or a cross-build.

## Validation and disposition

Local Windows validation: all nine immutable source blobs matched; extraction
succeeded; the generated C passed NDK r28c Android AArch64 API-30 syntax checking
with warnings as errors. The NDK was used only for syntax, producing no binary.
Repository regressions: **121 tests, OK; 117 executed passes and four existing
Windows skips**. Five new tests exercise source admission, per-caller identity,
nonregular input rejection and exact positive/denial result classification.
Foundation/link/provenance and harness manifest checks passed. Full intended diff,
Python syntax, modes and whitespace were reviewed before commit.

No local host C compiler was found; a WSL inventory attempt was access-denied,
so it supplied no Linux execution environment evidence. Linux witness
execution and this head's cross-build are **pending/unobserved at publication**.
The existing source-pinned Linux research job runs the witness before the unchanged
strict TCG controls and dependency build. No workflow, permission, budget, archive,
dependency pin, production protocol or worker code changes. The QEMU loader itself
is unchanged. Reproduction uses the existing Linux research procedure in the
[cross-build record](gate-0-qemu-android-linux-crossbuild.md#reproduction-and-bounded-workflow).

No phone, USB, ADB, Android emulator, production APK, guest boot, downloaded image
or proprietary guest software was used. Authentication, actual Android descriptor
authority, complete kernel boot support, memory/process isolation and security
certification remain Unknown. Host witnesses and Android-targeted compilation
cannot supply stock-device evidence. Gate 0 remains Unresolved, A–G Not reached,
ADR-0001 Accepted and ADR-0002 Proposed; no engine or production architecture is
selected. Publish one focused PR, report new CI pending/unobserved, then stop
without polling checks, Actions, reviews, bots or mergeability.
