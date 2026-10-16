# Gate 0: bounded ARM64 kernel FD snapshot primitive

**2026-10-15, America/Fortaleza. Gate 0: Unresolved; Gates A–G: Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No engine or integration
architecture is selected. Phone access is neither authorized nor used.

This implements the explicitly permitted **standalone bounded-reader** scope:
one owned read-only regular-file FD becomes a private, digest-matched, strictly
validated ARM64 Image snapshot. It does **not** connect that primitive to QEMU,
publish a ROM, authenticate the origin of the expected digest, or establish
end-to-end capability safety. This is executable C research source, beyond
[PR #11's pathname witness](gate-0-qemu-kernel-resource.md).

Scope: PDVA-REQ-002–003, 006–015, 034–045, 048, 051, 054. The
[worker integration review](gate-0-qemu-worker-integration.md),
[security boundaries](../security-boundaries.md),
[source policy](../source-provenance-policy.md) and
[evidence criteria](../acceptance-evidence-criteria.md) remain governing records.

## Independent preflight

GitHub branch API and independent `git ls-remote` both returned canonical main
`973c9dddac4c0881d8ed5b6b3487330e31078483`, tree
`e48064e3afa6cdfb0d97a4b84ac5c31c587516cd`. Open PR inventory was zero, so no
open heads/bases/diffs/checks/reviews/comments/unresolved threads needed
reconciliation. [PR #11](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/11)
merged head `0af067e73b70907d845e46adb37300afeeb2773b` against base
`a99c6b26b28dad328cc410b786ff96d999ae7bb4`; its merge is that exact main.
Its four-file merged diff and tree correspondence were inspected. Reviews,
conversation/inline comments and review threads were empty. All three PR checks
succeeded; main's exact-head foundation and Android checks succeeded. The
combined commit status had zero contexts; its aggregate `pending` is not a check.
All three workflows were active. Exact-head checkout, filters, read-only
permissions, limits and test commands were inspected. GitHub Status reported
All Systems Operational, page update `2026-10-15T20:29:23.193Z`.

The existing [PR #11 QEMU log](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38783466509)
records both intended boot-witness exits (0 and 93), the strict TCG positive and
two intended mutant failures, and a completed Android cross-build. Its QEMU
artifact was 67,010,296 bytes, SHA-256
`0fb16e4f57528e4449b961cdbda577881cd7bbe022d8740d3876047d412e42ed`, with direct
dependencies `libz.so`, `libm.so`, `libc.so`. This is historical log evidence,
not a locally downloaded/rehashed binary and not a result for this new reader.

Local work began clean at PR #11's head, with one worktree and no stashes.
Existing branches, ignored dependency/build/reference trees and binary inventory
were preserved; the new branch starts at verified main. All 80 pre-existing
tracked entries had mode `100644`. No applicable AGENTS.md was found. No historical
Privacy-Decoy writes, reset, clean, dependency installation, security-policy change
or Windows native execution occurred. Initial sandbox network/Python-alias
access failed; explicit network retries and the existing bundled Python enabled
read-only preflight and validation. WSL inventory was access-denied and supplies
no usable local Linux environment evidence. The
[native-host antivirus incident](gate-0-native-host-antivirus.md) is not resolved
or bypassed by this work.

## Exact source, integration obstacle and remaining access

The retained QEMU checkout is clean at
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`. Upstream's commit API independently
matched both. All nine `QEMU_BOOT_INPUTS` blobs were read from that immutable Git
commit and SHA-256 verified; working bytes matched after CRLF normalization.
CI still verifies raw LF inputs from the unchanged hash-pinned whole archive.
Principal input hashes remain `3ee33e386c78e816410d7f897d616a1f2c44203e7a609671184a95153412311f`
for boot.c and `5adca2184d46e03eed1122fa9c6e920fe8ffc340be7507021ed5afe53b1c47f0`
for loader.c. No QEMU boot file is modified by this experiment.

| Pinned caller | Direct source observation and unresolved consequence |
|---|---|
| [virt.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c) | `virt_firmware_init` maps pflash and can resolve/load a BIOS before `arm_load_kernel`. A gate in the raw leaf or even the ARM dispatch is too late to exclude those resources. |
| [boot.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c) | `arm_load_kernel` copies kernel/initrd/shim/DTB names and selects firmware or direct mode. Direct mode tries ELF and uImage before raw ARM64. The raw leaf registers a ROM before later initrd/DTB placement, bootloader registration, board setup and device initialization. |
| [loader.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/loader.c) | Earlier ELF/uImage probes use ordinary open; raw/gzip paths use GLib pathname reads. FD-set lookup in a different helper does not cover them. |
| Generated DTB path | `create_fdt` constructs the virt tree; `machvirt_dtb` returns `ms->fdt`. `arm_load_dtb` uses this callback only without an external DTB name, otherwise resolving/loading a file. It later mutates and registers the tree. Generated virt DTB remains a source-supported candidate, not an admitted/tested resource here. |

**Integration decision:** a distinct path would need rejection of firmware/pflash
and all other external resources before their initialization, exclusive dispatch
before `arm_load_elf`, terminal errors without any loader retry, and a prevalidated
kernel/bootloader/generated-DTB memory layout before ROM registration. No reviewed
typed machine configuration/FD ownership path currently carries this contract.
Adding just a sentinel kernel filename or replacing `load_aarch64_image` would
leave bypasses and partial machine-state publication. Whole-caller observation
and a deliberate fallback mutant must cover that future path. This is a concrete
scope deferral, not a proof that such integration is impossible.

The standalone reader has no filenames, loader-selection option, firmware,
pflash, external DTB, initrd, shim, ROM-registration or guest-execution interface.
It returns a typed failure without opening another resource. **Ordinary QEMU
retains all its existing boot paths and ambient facilities.** None of the new
runtime tests traverses `machvirt_init`, `arm_load_kernel`, the QEMU raw leaf,
generated DTB construction, or ROM/reset handling. Those observations remain
source-only; PR #11's existing extracted witnesses are preserved separately.

## Implemented contract

The original C in [kernel-fd-research.py](../../.github/scripts/kernel-fd-research.py)
is generated with reviewed checksum functions into a temporary translation unit.
`pdva_snapshot_take(fd, request, output)` consumes one owned descriptor on every
return, including argument rejection. Request version is exactly 1, specifying
this raw Image subset, exact byte length, expected 32-byte SHA-256, and one RAM
interval. The trusted caller must provide valid disjoint private request/output
objects, an output with no owned buffer, and exclusive descriptor-table ownership
during the call. Concurrent close/reuse of the integer violates that contract.

1. Admit lengths 68 bytes through 16 MiB before allocation. Reject invalid,
   writable, O_PATH, O_DIRECT and nonregular FDs, and any stat length disagreement.
   `F_GETFL` and each `fstat` have at most eight EINTR attempts.
2. Allocate once, at most 16 MiB plus fixed stack bookkeeping. Read at offset zero
   using `pread`, at most 64 KiB per call, at most 8,192 calls total including
   interrupted/short reads. Bound offset conversions before the first call.
   EOF, other errors, impossible counts and budget exhaustion fail terminally.
3. Recheck size, identity, mode, mtime and ctime. Hash the private copy and compare
   it with the expected digest **before parsing or publication**. The private
   bytes subsequently returned are the same bytes hashed. Matching content does
   not authenticate the controller or digest origin; there is no signature,
   manifest trust root, authorization or rollback verifier here.
4. Apply the strict header policy below. Check RAM alignment, end overflow,
   48-bit address ceiling and the entire declared Image interval by subtraction
   before computing its entry. Actual bytes must fit within the declared extent.
5. Close the FD once before publishing. A close error also prevents success;
   Linux EINTR is not retried because that can close a reused descriptor number.
   Failure frees the private allocation and leaves output byte-for-byte unchanged.
   Success assigns one complete snapshot; `pdva_snapshot_release` frees and clears
   that owned result, including harmless repeated release of the cleared object.

The [ARM64 boot specification](https://docs.kernel.org/arch/arm64/booting.html)
defines the 64-byte header, little-endian modern fields, flags and placement.
The experiment intentionally supports a smaller non-EFI grammar: code0 is a
forward unconditional AArch64 B to a complete instruction inside the file and
past the header; code1 is zero; text offset is exactly `0x80000`; image size is
nonzero, at least file length and at most 64 MiB; flags equal 2 (LE, 4-KiB kernel
pages, low placement); all reserved fields/PE offset are zero; magic is exact.
ELF/uImage/gzip/zboot signatures, legacy raw, EFI forms, other page-size/placement
flags and unreviewed variants are rejected. The 2-MiB-aligned RAM base reserves
the initial 512 KiB outside the kernel interval; no actual bootloader/DTB placement
is claimed. Header acceptance does not validate all instructions, identify a
Linux release, prove bootability or select a guest image line.

An O_RDONLY FD is not immutable. A separate writer can alter the file; metadata
comparison is additional detection, not the identity guarantee. A same-size
change can evade metadata checks, but only private bytes matching the trusted
expected digest can succeed. Backing changes after copying do not change the
snapshot. This does not guarantee a single atomic read of a mutable backing file,
nor revoke other descriptors/mappings. A same-process attacker can corrupt this
code or memory; the primitive is not a hostile-worker security boundary.

## Falsifiable Linux controls

The existing Linux research workflow now runs the new controls before NDK and
dependency builds, after pinned source acquisition and the old boot witnesses.
Each test executes the actual generated reader and extracted SHA-256 functions,
with syscall/allocation wrappers for observation and explicitly selected faults.
The trusted Python controller creates synthetic bytes, computes expected hashes
independently with hashlib, opens FDs and passes them to the child. Its filesystem
authority is not granted by the reader API. The observer also receives a test-only
writer FD for deterministic changes; the unobserved adapter has no such argument.

**69 cases are configured; their Linux execution is pending/unobserved locally.**
No fixture is a downloaded kernel or executed guest. The normal case is 4,096
bytes; boundary/short-read cases include 64, 68, SHA-padding boundaries, 8,193 and
131,073 bytes. Oversize tests use sparse length 16 MiB + 1 without allocating it.

| Coverage | Mechanism and required result |
|---|---|
| Valid, multi-chunk, minimum extent, SHA padding, exact RAM fit | Real Linux file/FD/pread and extracted hash against Python's expected digest; success, precise result metadata, unchanged shared file offset. |
| Digest mismatch, changed bytes before admission | Real reads, stale or deliberately wrong expected digest; exact digest rejection. Malformed-header fixtures get a freshly computed correct digest so rejection must reach header policy. |
| Invalid, O_WRONLY, O_RDWR, O_PATH, directory and pipe FDs | Real kernel descriptors and `fcntl`/`fstat`; exact FD rejection before allocation/read. |
| Truncated, oversized, zero/tiny, length UINT64_MAX | Real backing length or explicit invalid metadata; exact size rejection before allocation/read. |
| Short reads, EINTR success/exhaustion, EOF, EIO, impossible read count | Controlled return substitution around the actual reader; short-read cases still call real pread with a reduced count. Exact retry counts/budgets and result codes required. |
| Mutation/truncation during reading | The observer calls real pwrite/ftruncate through the writer FD between actual preads. Mutation plus growth guarantees detectable metadata change even on coarse-timestamp filesystems; same-size stale content is separately digest-tested. |
| Allocation, fstat/fcntl, final-stat and close errors | Controlled substitutes; exact errors, one close attempt and no live private allocations. Simulated close EINTR closes the real FD first, modeling Linux descriptor-release semantics; actual kernel close failure is not induced. |
| Unsupported formats, flags/reserved fields, branch/size/offset and RAM bounds | Real fixture bytes, correct independent digest, actual C parser; exact header or range error. No decompressor or format fallback is invoked. |
| Cleanup and no partial publication | Every returned failure preserves a sentinel output, balances allocations and closes the transferred FD. Success is rehashed after real backing truncation, then released twice and checked empty. |

Positive execution must return exactly exit 0, one `PASS: FD snapshot case` line
and empty stderr for every case. Each invocation has a five-second timeout.
Three deliberately weakened variants must compile successfully, then fail for
the intended reason: skipping the digest check gives exit 90 / `FAIL: expected
result`; writing output before digest validation gives exit 90 / `FAIL: partial
publication`; reopening a path on failure gives exit 93 / `DENIED: adapter
pathname/fallback`. A separate observer control requires the same exit 93.
Signals, timeouts, compiler failures, missing/extra output or unrelated failures
cannot count as those expected observations. All expected diagnostics include
one trailing newline. Separate source/binary hashes are logged for each variant.

The path observer covers adapter calls to open/openat/fopen/GLib file reads via
macros; it is **not syscall confinement**, and does not instrument libc internals
or QEMU. The standalone Android artifact additionally rejects unreviewed dynamic
imports and requires the reader/release symbols. This observes the implemented
scope's fallback mutation; it does not prove absence across a future caller chain.

## Provenance, compilation and observed validation

No new package is introduced. SHA-256 uses unchanged functions/constants/types
extracted from already pinned GLib
[`e05063ccc6c8f222465a1080927f4c14349f3de6/glib/gchecksum.c`](https://github.com/GNOME/glib/blob/e05063ccc6c8f222465a1080927f4c14349f3de6/glib/gchecksum.c),
file SHA-256 `55e03a7ed5d654419a24505f39f73bacdbe79d3f2d8075b2724f34c3133dede1`.
Extraction preserves the LGPL-2.1-or-later file notice and Dave Benson SHA-256
attribution. Fixed-width C typedefs and statement macros supply the small GLib
type context; no replacement hash algorithm or host GLib installation is used.
This is scoped research source reuse, not product adoption. A distributed binary
would require applicable LGPL source/relinking notices and obligations to be
reviewed; no generated source, native binary or guest asset is committed/uploaded.
QEMU's existing GPL and all dependency provenance obligations remain unchanged.

The recipe preserves every archive, Git, wheel and NDK pin, prior portability
patch and strict TCG transformation/control. Local AST comparison confirmed those
declarations/functions unchanged. The workflow adds only a path trigger for the
new module; privileges, timeouts, limits, prior tests and upload policy remain.
The standalone adapter is cross-linked with a do-nothing main, then inspected;
its real functions must remain in the ELF. This artifact is not linked into QEMU
or the APK and is never executed. Full QEMU still builds through the old recipe.

Local environment: Windows x86_64, existing bundled Python and retained NDK r28c
`28.2.13676358`, Clang 19.0.1 / Android build 13624864, compiler revision
`97a699bf4812a18fb657c2779f5296a4ab2694d2`. Compiler SHA-256 is
`7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579`.
Commands explicitly select `--target=aarch64-linux-android30 -std=c11 -O0 -Wall
-Wextra -Werror`; linking adds stack protection, PIE, RELRO/NOW and 16-KiB segment
alignment. API 30 is only a compile target, not an established host minimum.

| Actual local check | Observation |
|---|---|
| Source identities | Nine QEMU boot blobs matched; checksum file matched before extraction. |
| C syntax | Unobserved reader, positive observer and all three mutant sources passed NDK ARM64 syntax checks with warnings as errors. |
| Standalone Android artifact | Compiled/linked, inspected, never executed: 25,352 bytes, SHA-256 `ef58c8fe1f6f9fd92b91ee72270f548bcc9bb6a0aba48566df02e1d3bcaa72bb`; ELF64 AArch64 dynamic PIE, API 30, `/system/bin/linker64`, 4 LOAD segments, 16-KiB alignment, no W+X/executable stack, RELRO/NOW. |
| Imports and symbols | Both primitive symbols retained. Exactly 13 imports, all present in API-30 NDK stubs and on the standalone allowlist; direct dependencies libc/libdl. No pathname or QEMU loader import. This does not inspect runtime libc behavior. |
| Python/repository checks | AST passed. All 127 repository regressions completed: 123 executed passes, four existing Windows skips. Foundation/link/provenance passed (82 files, 46 Markdown files, 54 requirements, two ADRs); harness source/manifest authority passed. Exact-base diff, new files, modes, public-data hygiene and whitespace reviewed before commit. |
| Linux FD behavior and complete Linux cross-build | Pending/unobserved at publication; no local Linux execution claimed. |

Generated LF source SHA-256s identify the exact modifications independently of
eventual PR commit metadata:

| Translation unit | SHA-256 |
|---|---|
| Standalone reader plus extracted hash | `3d6af3e7b991fdfbc3d85585c276b77f489a7e5259552a4e60f4017b3e71987d` |
| Positive observer/driver | `ecbc7baa4c04910ad43871ef3ad0e54efd64f20f3ee387f66b261dbbe2b66ae2` |
| Digest mutant | `4296ccd7f4d4bb6ddfe6de329c513a5d087a0fc215bb414b4759741c9f98017c` |
| Partial-publication mutant | `7fb2188f9a7eff38e2aa2d9fcd06d9d8c3f9b651d88b8cf334f15ec7461f619b` |
| Fallback mutant | `28d81321f8a9cbdcb2462791d25f9a8d8cfeb5d1e1daa27c9860cf61d59441bc` |

## Reproduction, limits and prerequisites

Use the existing [bounded Linux recipe](gate-0-qemu-android-linux-crossbuild.md#reproduction-and-bounded-workflow),
which invokes this module after source verification. For standalone controls on
an existing Linux development host, provide the exact pinned checksum source and
a fresh empty output directory, import `kernel-fd-research.py`, and call
`run_controls(read_checksum(path), output, run, print)` where `run` invokes the
supplied compiler argv with check=True. The recorded recipe provides bounded
compiler subprocess handling and logs; each fixture subprocess is separately
bounded here. No Android/QEMU binary execution is part of either procedure.

Iteration and byte limits do not bound an individual blocking kernel syscall on
a regular file (for example remote/FUSE storage). External supervision is still
required. Allocation failure and modeled close errors are covered, not process
death, allocator corruption or every filesystem/LSM behavior. Closing the owned
FD does not revoke aliases; private bytes are not securely erased. Request and
output pointer validity, caller exclusivity and expected-identity trust are
preconditions, not validated hostile IPC. Header constraints intentionally reject
many legitimate ARM64 images and establish no Android guest compatibility.

Next prerequisites are actual exact-head Linux results; review of the typed
exclusive machine admission and pre-firmware exclusions described above;
transactional bootloader/kernel/generated-DTB layout and cleanup; whole-caller
forbidden-path/fallback controls; authenticated resource metadata/delegation; and
separately authorized ordinary-app runtime experiments. Android runtime FD
authority, SELinux, seccomp, stock-device execution, guest boot and hostile-worker
isolation remain **Unknown**. No production ADB, phone, emulator, guest image,
proprietary asset or APK integration was used.

Publish one focused PR only after local validation. Hosted CI is
**pending/unobserved at publication**. Verify only the created PR's immediate
identity, branch and exact head/base, then stop without polling Actions/checks,
bots, reviews, approvals, mergeability or status propagation. Gate 0 remains
Unresolved; Gates A–G Not reached; ADR-0001 Accepted; ADR-0002 Proposed.
