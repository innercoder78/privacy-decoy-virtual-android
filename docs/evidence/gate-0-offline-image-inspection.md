# Gate 0: offline image structure investigation

Review date: **2026-10-21, America/Fortaleza**. **Gate 0 Unresolved; Gates A–G
Not reached. ADR-0001 Accepted; ADR-0002 Proposed. No engine adopted.**
The complete interactive Android 17/API 37 guest, ordinary distributable host
app, normally unrooted controlled image line, genuine guest/host separation,
narrow brokers, Real/Decoy/Empty/Deny, no host-GPS fallback and existing host VPN
contract remain requirements. This tool supplies structural observations only.
It cannot establish a boot, Android compatibility or a security boundary.

## Procedure on Windows 10

Install a trusted Python **3.11+** distribution with its standard-library
`bz2`, `lzma` and `zlib` modules. No package installation, WSL, container,
administrator rights, compiler, Android tools or device connection is required.
Use local storage with ordinary OS locking semantics. The repository checkout
must be writable for ignored reports. Run from its root in PowerShell.

1. Select one regular local file explicitly. The tool never searches personal
   directories, downloads samples or follows archive filenames. Use a generic
   journal ID that does not identify the sample. Paths typed at the prompt may
   still be retained by the terminal's own history; treat that history as private.

   ```powershell
   $tool = '.github/scripts/offline-image-inspect.py'
   $image = Read-Host 'Explicit local image path'
   python $tool inspect --journal inspection-01 --input $image
   if ($LASTEXITCODE -ne 0) { throw 'Stop and preserve the private checkpoint' }
   ```

2. Read the sanitized status. It never prints sample names, paths, hashes,
   binary strings, archive member names, identifiers or host details.

   ```powershell
   python $tool status --journal inspection-01
   if ($LASTEXITCODE -ne 0) { throw 'Checkpoint unreadable; preserve it' }
   ```

3. Inspect the private report locally. The append-only JSONL checkpoint is the
   report; its `OBSERVED` record contains findings. Use them only when the last
   verified state is `COMPLETED`. An `OBSERVED` record followed by interruption
   or `FAILED` is provisional. Do not upload or paste this file.

   ```powershell
   $records = Get-Content -LiteralPath 'android/build/private-image-inspection/inspection-01.jsonl' |
       ForEach-Object { $_ | ConvertFrom-Json }
   $records | Where-Object kind -eq 'OBSERVED' | Select-Object -Last 1 |
       ForEach-Object { $_.data | ConvertTo-Json -Depth 10 }
   ```

   The status command validates the record chain before this manual viewing
   step. The private file also contains content hashes, a hashed path token and
   filesystem identity metadata. Hashing does not make these safe to publish.
   Ignore rules provide repository hygiene, not encryption or access control.

4. After interruption, run `status` first. Resume is explicit and restricted to
   this tool's read-only inspection, using the same file, journal, scanner bytes
   and size limit:

   ```powershell
   python $tool resume --journal inspection-01 --input $image
   if ($LASTEXITCODE -ne 0) { throw 'Resume rejected; preserve all records' }
   ```

   A valid incomplete checkpoint with a completed initial identity hash may
   resume only after a new complete hash and file identity comparison. A crash
   before that first identity was persisted cannot be reconciled and is rejected.
   Missing, empty, torn, corrupted, mismatched, completed or failed checkpoints
   cannot resume. Do not edit, truncate or replace them. Review the cause before
   deliberately starting a separate new read-only investigation with a new ID.
   No such action clears another journal or Android-worker uncertainty.

Default maximum input size is **64 GiB**. `--max-bytes` can explicitly choose a
positive ceiling up to **1 TiB**; use exactly the same value for resume. Hashing
reads the full input twice, or twice again on resume, in chunks of at most 1 MiB.
Large files can take substantial time even when their structural probes are
small. Source images are opened read-only and never mounted, modified, extracted,
executed, decrypted or repackaged. Device paths, alternate data streams, UNC
paths, redirected input/storage paths and nonregular files are rejected.

## Recognition contract and deliberate Unknowns

`outer_format` identifies a supported structurally consistent container, **not
full semantic validity or trust**. Magic alone never produces that result.
`candidate` is only a signature hint. `validation` distinguishes structural
recognition, limited metadata and no validation. Numeric metadata is deliberately
narrow; strings supplied by an image are never included in reports.

| Format | Checks actually performed | Important exclusions / Unknowns |
|---|---|---|
| Android boot v3/v4 | Header size/version/reserved fields; bounded aligned kernel, ramdisk and signature slots; at least one payload | v0–v2 and future versions UNKNOWN; payload bootability and signatures unchecked; kernel slot can be empty for a ramdisk-only image |
| Android vendor boot v3/v4 | Header/page sizes, bounded ramdisk/DTB; v4 table count/entry sizes, ramdisk subranges and overlap, bootconfig range | DTB and ramdisk contents, load addresses, runtime selection and bootconfig meaning unvalidated |
| Android sparse v1.0 | Exact supported header sizes; bounded RAW/FILL/DONT_CARE chunk lengths and total block accounting; exact encoded file end | CRC-bearing variants, extensions, excessive chunk counts UNKNOWN; no expansion or inner filesystem inference |
| AVB/vbmeta | Big-endian version, block alignment, reserved bytes, authentication/auxiliary subranges, algorithm-dependent sizes, descriptor framing | No trusted key, signature verification or descriptor semantics; this is never verification/admission authority; AVB footer discovery not implemented |
| ELF32/ELF64, either byte order | Header version/class, ordinary section/program table sizes and ranges, segment sizes/alignment, file-backed section ranges | Extended numbering and excessive tables UNKNOWN; no linking, symbol parsing or execution; machine/class/OSABI values are metadata, not compatibility proof |
| ZIP | Single-disk central directory/end accounting, bounded entry count, matching local headers/names/sizes, nonoverlapping payload ranges | No payload decompression/CRC verification; encrypted, descriptor, ZIP64 and extra-field variants UNKNOWN; no file extraction or Android-component inference from names |
| gzip, XZ, bzip2 | Incremental standard-library decoder reaches stream end within budgets; native stream integrity checks where present | At most 8 MiB encoded and 8 MiB decoded; decoded chunks discarded; XZ decoder memory capped at 64 MiB; concatenated streams/trailing data UNKNOWN; no nested inspection |
| ext4 | Supported superblock fields, extents feature, block/inode counts/sizes, filesystem byte bounds | **Outer UNKNOWN**: group descriptors, inode trees, allocation and checksums not validated; unsupported features rejected; not proof of Android userspace |
| EROFS | Minimal feature-free superblock, file bounds, metadata address and compact directory root inode | **Outer UNKNOWN**: directory contents, data mapping, checksums and advanced features unvalidated |
| Dynamic/super | Matching primary/backup geometry, SHA-256 geometry checksum, slot/size/alignment fields and metadata-area bounds | **Outer UNKNOWN**: slot headers/tables, active slot, logical extents and complete partition layout not parsed; geometry alone is insufficient |
| Other/wrapped/opaque data | Only fixed supported probe positions | **UNKNOWN**; no entropy claim, brute-force signature sweep, encryption identification or proprietary decoder |

Each structural reader caps a single read at 1 MiB and aggregate metadata reads
at 32 MiB. Container tables cap at 4,096 entries; ELF tables at fewer than 4,096.
ZIP and descriptor metadata cap at 8 MiB. File ranges use subtraction-based
bounds checks and Python integers. Expansion lengths cannot allocate arbitrary
memory. Boot kernel slots may contain a separately validated ELF object: this
appears in `embedded` with role `kernel-slot`. No recursive general extraction
or scanning of arbitrary offsets is performed. A kernel-slot ELF is only a
candidate component; it does not prove that the object is a kernel.

`boot_evidence` records only the checked container. `userspace_evidence`,
`partition_evidence` and `execution_architecture` remain **UNKNOWN** in this
slice. Neither a filesystem superblock nor an archive filename establishes
Android framework/service contents. Absence of a detected kernel is not proof
that no kernel exists elsewhere, is wrapped, or is obtained separately.

## Separate checkpoint and recovery contract

[PR #28's APK journal](gate-0-desktop-readiness.md) has a fixed APK correspondence
state machine and fail-closed external cleanup handling. Its code and tests are
unchanged. Generalizing its retry behavior would blur that authority, so image
inspection uses an independent, narrowly scoped implementation and store.

The journal persists and flushes/fsyncs `START` and `HASH_INTENT` before opening
the input, `IDENTIFIED` immediately after hashing, `SCAN_INTENT` before parsing,
`OBSERVED` immediately after parsing, `VERIFY_INTENT` before the final identity
hash, then `COMPLETED` with the matching identity and report digest. Resume first
persists `RECONCILE_INTENT`, hashes and compares the original identity, persists
`RECONCILED`, then repeats the idempotent scan. An interrupted reconciliation
can only repeat reconciliation. Exceptions record `FAILED` if the journal is
still valid; process death and interrupts never manufacture completion.

Exclusive creation prevents overwrite. A nonblocking OS lock on the journal
excludes cooperating writers and is released by process death. The lock is never
stolen or deleted. Windows readers can also be denied while the writer holds
the byte lock; this is an incomplete/unavailable status, not success. Canonical
JSON, strict event envelopes, sequence numbers, hash chaining, legal transitions,
tool/input binding and bounded journal reads reject partial writes and replay.
Journal limits are 2 MiB and 256 records. No automatic repair is provided.

Identity uses filesystem device/file ID, size, modification time and full SHA-256
before and after inspection, including path-to-open-handle correspondence.
POSIX additionally includes change time. Windows legacy creation-time values
are deliberately excluded because path and descriptor queries disagreed in local
controls; the mandatory full hashes remain. These checks detect accidental
replacement/mutation, not a malicious concurrent writer able to change and
restore bytes between observations. Keep supplied files quiescent while scanning.

This is not authenticated or anti-rollback storage: a local writer can rewrite
the entire chain, restore a valid prefix, or remove it. Portable fsync cannot
guarantee directory-entry survival or disk/controller behavior. Stored reports
are neither executable instructions nor trusted input to a runtime. No journal
record can resolve device cleanup, worker lifetime uncertainty or isolation.

## Falsifiable architecture comparison

| Hypothesis | Evidence needed in separately authorized research | What would contradict it | Offline conclusion |
|---|---|---|---|
| Independent guest-kernel execution | Exact source-built kernel and loader correspondence; independently observed entry/execution and guest hardware/syscall path | Evidence that supposed guest syscalls execute directly through a shared host kernel without a guest kernel | Boot/kernel candidates can guide questions; execution remains UNKNOWN |
| Android userspace sharing the host kernel | Source and observed native syscall/namespace/service routing, authority and lifetime model | Independently verified guest-kernel execution for the claimed workload instead of that path | Android-looking files cannot decide this; it cannot silently replace required separation |
| Custom loader/runtime | Reviewed loader, supported binary/component contract and independently observed dispatch path | Unmediated execution or a different kernel/runtime path inconsistent with its stated contract | A wrapper or opaque blob supplies no proof of the mechanism |
| Unknown/hybrid | Separate evidence for each execution path, workload and authority boundary | A reproducible complete path inventory that excludes the claimed alternative | Default classification for every report here |

The next safe step is to inspect an explicitly selected, lawfully held image
privately, or obtain a reproducible source-built synthetic/reference layout with
clear provenance. Translate observations into narrow source/authority questions
under [Gate 0](../feasibility-gates.md), [source policy](../source-provenance-policy.md)
and [image lifecycle](../guest-image-lifecycle.md). Any incompatible architecture
is a finding, not permission to weaken requirements. Material changes require a
separate ADR and Tony's explicit approval.

## Public evidence and provenance

No actual local guest-image paths were supplied; **actual guest-image examination
was not performed**. No personal-directory search was made. All public controls
generate deterministic fixtures from source; no sample bytes, hashes, paths or
identifying metadata are published. Repository-owned Python is newly authored
from format descriptions; no upstream implementation code or binary is copied.
No runtime, dependency, license grant or source pin changes are introduced.

Reviewed specifications (retrieved 2026-10-21; live documentation can change):

- [Boot/vendor boot field definitions](https://android.googlesource.com/platform/system/tools/mkbootimg/+/refs/heads/main/include/bootimg/bootimg.h), observed blob `67ae349583e66424e5af0a3b7a386b42b6c958e0`; BSD-style header notice.
- [Sparse field definitions](https://android.googlesource.com/platform/system/core/+/refs/heads/main/libsparse/sparse_format.h), observed blob `a8a721e6e8d7b895280fb79899b8e35571870277`; Apache-2.0.
- [Logical-partition geometry](https://android.googlesource.com/platform/system/core/+/refs/heads/main/fs_mgr/liblp/include/liblp/metadata_format.h), observed blob `8d77097ed67b047603d4571e514730ca98b63cf8`; Apache-2.0.
- [vbmeta header](https://android.googlesource.com/platform/external/avb/+/refs/heads/main/libavb/avb_vbmeta_image.h), observed blob `f9cbac447d0941429d813ca0aadef4401e7ec8d7`; MIT-style notice. Header observation is explicitly not signature verification.
- [ext4 superblock](https://docs.kernel.org/filesystems/ext4/super.html) and [EROFS format definitions, v6.12](https://raw.githubusercontent.com/torvalds/linux/v6.12/fs/erofs/erofs_fs.h); the latter declares GPL-2.0-only OR Apache-2.0. No filesystem implementation adopted.
- [ELF header specification](https://gabi.xinuos.com/elf/02-eheader.html) and [ZIP specification 6.3.10](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT). Reference only; no document reproduction or library adoption.
- [gzip framing, RFC 1952](https://www.rfc-editor.org/info/rfc1952/), [incremental XZ decoder](https://docs.python.org/3/library/lzma.html) and [incremental bzip2 decoder](https://docs.python.org/3/library/bz2.html). Standard-library APIs supply bounded decoding; decoded data is discarded.

Preflight verified live main `3fbcc2fa8177ca55574872534c98441b68ada375`, a clean
working tree, one worktree and no stashes. The live open-PR inventory was zero,
so there were no open PR heads/bases/diffs/checks/jobs/logs/comments/reviews/threads
to reconcile. Service status was operational. PR #28 was merged at that revision;
its infrastructure, policies, ADRs, packaging, existing toolchain/dependency
ledger, image research, workflows and regular `100644` modes were reviewed.
Existing ignored build outputs and historical references were preserved.

Validation commands (Python 3.11+; no synthetic fixture is skipped):

```powershell
python .github/scripts/test-offline-image-inspect.py
python .github/scripts/validate-foundation.py
python .github/scripts/test-repository-validation.py
python .github/scripts/validate-harness.py
python .github/scripts/test-desktop-readiness.py
git diff --check
```

The new suite covers positive headers and embedded ELF; truncation, misleading
magic, length/range errors, unsupported variants, malformed archive metadata,
bounded compression, opaque deterministic data, a seek-created 5 GiB file,
mutation, interrupted hashing/scanning, corrupt checkpoints, ambiguous resume,
missing/unreadable/nonregular inputs and competing writers. A real controlled
Python process is terminated after durable scan intent, its competing writer
is rejected, and reconciliation/resume is then exercised. No native image
payload executes. Existing foundation checks remain; CI adds the suite to the
existing job and a Windows job using the same reviewed checkout pin and read-only
permissions. No private report or sample is uploaded. Hosted results are separate
from local evidence and remain pending/unobserved at publication.

Local validation used Python **3.12.14 on Windows**: **45 new tests passed,
zero skips**; the unchanged desktop journal suite passed **27/27**. The existing
repository suite ran **141 tests: 137 passed and four pre-existing platform
skips** (host C compilation, real destination/ancestor symlinks, POSIX executable
modes and POSIX symlink types). Those four are not counted as passes and remain
Linux-CI obligations. Foundation validation passed for 118 text files, 67 Markdown
files, 54 requirements and two ADRs; harness manifest validation and whitespace
checks passed. This is local Windows evidence, not a separately verified Windows
10 installation or a hosted result. No Android source changed; Android builds,
physical runs and dormant native diagnostics were not dispatched for this slice.
