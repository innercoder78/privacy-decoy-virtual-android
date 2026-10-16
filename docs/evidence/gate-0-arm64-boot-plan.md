# Gate 0: typed ARM64 boot reservation control

**2026-10-15, America/Fortaleza. Gate 0: Unresolved. Gates Aâ€“G: Not reached.**
ADR-0001: Accepted. ADR-0002: Proposed. Production VM engine: Not selected.
Android runtime execution and isolation: Unknown. This is non-physical research.

The implemented result is the permitted **typed preflight/boot-plan control**,
not an exclusive QEMU boot path. It constructs a single-owner admission using
PR #12's actual snapshot reader, then checks resource declarations, identity and
kernel/bootloader/generated-DTB reservations before returning a complete private
plan. It adds one experimental compilation unit to the pinned ephemeral QEMU
source tree. **No QEMU machine caller invokes it.** There is no CLI switch, ROM
publication, generated-DTB admission, reset integration or guest execution.

This advances the [snapshot primitive](gate-0-kernel-fd-snapshot.md) with a new
state/ownership/layout contract. It does not turn the
[pathname witness](gate-0-qemu-kernel-resource.md) into a safe loader. Scope:
PDVA-REQ-002â€“015, 034â€“045, 048, 051, 054. The [worker integration review](gate-0-qemu-worker-integration.md),
[strict TCG controls](gate-0-tcg-executable-memory.md), [source policy](../source-provenance-policy.md),
[security boundaries](../security-boundaries.md), [gates](../feasibility-gates.md)
and [adoption limits](gate-0-isolated-worker-adoption.md) continue to apply.

## Independent preflight and earlier hosted evidence

GitHub branch API and independent `git ls-remote` both returned canonical main
`8213f3dac3f98c39dc8454c6b337fed90edb1837`, tree
`26438c08cbfa180279637bb14a241c8498f657ab`. The repository is public, not a fork,
not archived or disabled; default branch is main. Open PR inventory was **zero**,
so there were no open heads/bases/diffs/checks/reviews/comments/threads to reconcile.
[PR #12](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/12) is
merged: head `1128c0c76523203abfc48836e1d488103d8739f8`, base
`973c9dddac4c0881d8ed5b6b3487330e31078483`, merge equal to expected main. Its complete
seven-file change was inspected locally, including the actual reader, generated
controls, workflow and evidence. Reviews, conversation comments, inline comments
and review threads were empty; thread pagination had no further page.

All three PR checks succeeded. The actual [QEMU job log](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38821156132)
at that exact head records 69 FD cases, the observer control and three intended
mutant exits (90, 90, 93), both prior pathname witnesses (0/93), strict TCG positive
and fallback controls (0/91/91), and cross-build completion. The standalone FD
Android artifact logged SHA-256
`795b46088186e0a2ace639f479b785663dffdca4b6bb3d2f275df04bc6ec9d6e`.
These are hosted **log observations**, not downloaded/rehashed binaries or target
execution. They update the historical pending observation in PR #12's record;
they do not establish success of this new plan control.

Exact-main [foundation](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38831819652)
and [Android](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38831819514)
jobs and their required steps succeeded. Combined status had zero contexts;
aggregate `pending` was not an additional check. All three workflows were active.
Definitions, exact-head checkout, read-only authority, filters, timeouts, limits,
source/dependency pins, ELF inspection and no-upload behavior were inspected.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational, page update `2026-10-16T00:47:28.408Z` (UTC).

Local tracked state began clean on PR #12's branch, with one worktree and no
stashes. All 82 tracked entries were regular mode `100644`. Existing branches,
ignored source/tool/build trees and binaries were inventoried and preserved.
The new branch starts at verified main; the historical Privacy-Decoy repository
was untouched. No applicable nonempty AGENTS.md was found. Sandbox network access
initially failed; authorized read-only retries supplied GitHub evidence. Local
WSL inventory returned access denied, so no Linux execution is claimed. The
[native-host antivirus incident](gate-0-native-host-antivirus.md) remains unresolved;
no Windows test executable, security-policy change or quarantine restoration was used.

## Caller order and the integration decision

All source links in this section identify QEMU
**`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`**, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`. The retained checkout is clean and
upstream's commit API independently matched both identities. Reviewed working
files matched immutable Git blobs after CRLF normalization. CI requires raw LF
hashes; it does not normalize or learn new source identities from downloaded files.

| Entry point / caller | Source observation and consequence |
|---|---|
| [qemu_init / qemu_create_early_backends](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L3781) | Creates early objects and block backends before applying machine options and before board initialization. Rejecting a pflash declaration inside `machvirt_init` alone would not prove that its backend was never opened. A future fixed typed entry must exclude unapproved backends before this stage. Generic CLI configuration is not an acceptable trusted adapter. |
| [machine_run_board_init](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/machine.c#L1612) | Creates/consumes RAM backends, completes NUMA and initializes accelerator interfaces before invoking `machine_class->init`. A board-local guard cannot establish rollback of these effects. |
| [machvirt_init](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c#L2880) | Computes CPU/memory-map details and can publish secure-memory regions before `virt_firmware_init`; that call precedes `create_fdt`. Board-level resource selection must precede firmware initialization, preferably the first side effect in the function, with earlier lifecycle restrictions separately enforced. |
| [virt_firmware_init](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c#L1893) | Maps legacy pflash drives to flash properties, maps flash, and can resolve/load BIOS bytes. Checking only the primary pflash or the raw Image leaf is insufficient. |
| [create_fdt / machvirt_dtb / virt_machine_done](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c#L2412) | The generated tree is published as `ms->fdt`; the callback returns that same pointer. Device construction adds nodes, and machine-done adds platform-bus nodes before `arm_load_dtb`, then builds ACPI/SMBIOS. Early reservations cannot certify the eventual tree or all later effects. |
| [arm_load_kernel](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c#L1178) | Registers CPU resets and copies path fields before selecting firmware/direct mode. An exclusive branch must precede that ordinary dispatch, with terminal failure and no pathname sentinel. The new control does not add this branch. |
| [arm_setup_direct_kernel_boot / load_aarch64_image](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c#L892) | Probes ELF then uImage then ARM64 gzip/raw (or ARM32 raw). The raw leaf registers a ROM before subsequent placement and bootloader work. Existing initrd loading, bootloader registration, board hooks and device firmware emulation are additional publication paths. |
| [arm_load_dtb](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c#L467) | Can load an external filename or use the callback; mutates memory/chosen/PSCI nodes and registers both ROM and seed-reset state. Its limit-exceeded branch frees the tree and returns **zero**, while `virt_machine_done` checks only `< 0`. This contract cannot simply be treated as an exclusive-path terminal error/rollback API; ownership and exact positive-size handling require review. This is a source-contract observation, not a demonstrated upstream vulnerability. |
| [rom_add_blob / rom_insert](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/loader.c#L1161) | Allocates/copies bytes and inserts a ROM into global state immediately. Later overlap/reset registration is a different stage. No multi-resource atomic publication/rollback facility was established by this inspection. |

**Decision/inference:** there is no single reviewed insertion point that both
excludes early resources and knows the final generated DTB. The smallest defensible
next implementation is a reservation calculation without QEMU-global side effects over a private
validated snapshot, preceded by single-owner admission. Whole-caller integration
needs at least an early closed configuration path and a later private final-DTB/
ROM commit design. Abort here frees only this control's private snapshot. It does
not roll back QEMU, undo memory regions, close arbitrary backends or unregister ROMs.

The generated virt DTB is a justified candidate because it avoids external loading.
[create_device_tree](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/device_tree.c#L38)
allocates `FDT_MAX_SIZE = 1 MiB`; ARM boot uses `BOOTLOADER_MAX_SIZE = 4 KiB`.
Those exact-source constants define reservations here. A reserved span does **not**
admit DTB bytes, validate a DTB header or prove final device configuration fits.
Final generation, mutation, packing, ownership, reset and allocation failure remain
unexecuted. General device loaders, firmware tables, migration, all block backends
and arbitrary hostile native behavior are not exhaustively audited by this slice.

## Implemented state, ownership and layout contract

[arm64-boot-plan-research.py](../../.github/scripts/arm64-boot-plan-research.py)
emits `hw/arm/pdva-boot-plan.c` and adds it to the existing ARM virt Meson source
set in the ephemeral research tree. The upstream boot/virt/loader functions are
unchanged. The module has no initializer, ordinary-mode caller or CLI property;
ordinary upstream dispatch retains its existing behavior and ambient file access.

The module is intentionally one process, one owning thread, one attempt. Its
private registry moves EMPTY â†’ ADMITTED â†’ RESERVED; any failure or abort moves
to DEAD, with no reinitialization API. `pdva_boot_admit` consumes one FD on every
return and calls the exact PR #12 reader. Only success publishes a version-1,
format-1 admission identifying one nonzero resource/epoch and expected digest.
It binds the token to the output object's address and keeps the bytes private.
Copying the token, changing its fields, repeating admission or using it after
abort fails. Caller request/output objects must be valid, private, disjoint and
stable for their specified lifetimes; C pointers are not a memory-safety boundary.

`pdva_boot_reserve` requires that token, matching expected identity and version-1
research raw-ARM64 mode. The exact supported declaration is AArch64 virt, TCG,
one CPU, plain low RAM, no additional feature flags and generated-DTB reservation.
Every resource flag is rejected: firmware, both pflash slots, BIOS, shim, initrd,
external DTB, kernel pathname, option ROM and other/unknown resources. Feature
flags for secure/EL2/MTE/NUMA/hotplug/backends/hooks/extra devices are all rejected.
**These are typed caller declarations, not an inspection of actual MachineState.**
A future adapter must establish their truth before initialization; this PR does
not make forbidden paths unreachable across QEMU.

The RAM interval must match admission, begin at virt's `0x40000000`, and be at most
1 GiB. Checked subtraction proves containment and non-wrapping ends before overlap
arithmetic. The full declared kernel Image extent is reserved, not merely the
file length. A 4-KiB bootloader span must start at RAM base. The 1-MiB DTB span must
be 2-MiB aligned, after the declared kernel, within RAM and pairwise disjoint.
Only after all checks does one assignment return a versioned **reservation-only**
plan. No bytes are exposed and no firmware, ROM, CPU, FDT or guest-memory state
is committed. Even success is not authorization to boot.

Ordinary mode returns a no-op result only from EMPTY with no admission/identity.
It cannot recover a failed or admitted attempt. All other failures release the
private allocation and leave plan output unchanged. Abort is idempotent. A returned
plan/token can remain as stale caller data; no API can use it to publish resources.
There is no thread safety, revocation authority, crash recovery or process-tree
containment. Unexpected process death relies on OS cleanup and a future external
supervisor, not this cooperative abort function.

The FD and size limits remain PR #12's: one allocation at most 16 MiB, declared
Image at most 64 MiB, bounded positional IO and retries, strict raw grammar and
close-before-admission. No generic file-opening API, directory capability or path
transport is added. Matching a digest or epoch does not authenticate its origin:
**a future trusted controller must supply the expected resource digest and identity**.
No authenticated host trust path is invented here.

## Exact integration and provenance

The unchanged whole-QEMU archive SHA-256 is
`a5a78e7d395ed096a7b2d98375978d0e2cf73f62c49a081ca48fa665d479b09f`.
All nine prior boot-audit inputs remain verified. The new module separately checks
seven full-file inputs before any write; the additional source identities are:

| Input | SHA-256 |
|---|---|
| `hw/arm/meson.build` | `8efe237c39a11996ea7fb6cbd9bcbeb87412796c3c9e48bbb0634768e1efcfd9` |
| `hw/core/machine.c` | `189c891714f0928cdd6648f7d2799b529029345a4c47fcf1fc92adb01a9d6e27` |
| `include/hw/arm/boot.h` | `0989956cac29b6652f1182edf314df328859b71900304f296df7db40c27e8129` |

PR #12's original `ADAPTER` text must hash to
`95e69229f79201e2f644ec1af7e731dd95e4e21c1e97843092ff4a822d5b5805`.
Integration changes only its two exported functions to **static** linkage; no
reader logic changes. QEMU's `qemu/osdep.h` supplies the compilation context in the
full build, with the 64-bit `off_t` assertion retained. Standalone controls replace
that single include with PR #12's standard-header context and observers, preserving
the emitted functions. They do not compile or execute the full machine callers.

SHA-256 implementation remains the unchanged extraction from pinned GLib
`e05063ccc6c8f222465a1080927f4c14349f3de6`, `glib/gchecksum.c` SHA-256
`55e03a7ed5d654419a24505f39f73bacdbe79d3f2d8075b2724f34c3133dede1`.
Its LGPL-2.1-or-later notice and SHA-256 attribution remain in every generated
source. The plan/observer code is original PDVA research source. This exact-source
integration is proposed only for research review, not approved production adoption
of PR #12 or an added runtime dependency. No repository-wide license is inferred.
QEMU GPL and GLib LGPL corresponding-source, notice and applicable static-link
relinking obligations remain; production combination/distribution rights need
separate review. No generated C, native binary, guest image or proprietary asset
is committed or uploaded. The repository owner maintains this research recipe.

| Generated LF artifact | SHA-256 |
|---|---|
| `hw/arm/pdva-boot-plan.c` | `82c16bca8f04af75491c3f9bbde96537ace1357bee84d5c97b57ccfd1ca096dc` |
| Modified `hw/arm/meson.build` | `2061d6152c357a41b761798534fee13f4259e57c7b04a8e64770399641586879` |
| New C unified diff | `9af39bed0aec446b968c8337a87c4d5cb97a745d881d119e6409b157b8156436` |
| Meson unified diff | `d8fda02175c86094fbb73d333e2c216b98d0ff50d4e5599f7565e80d13a0f7c6` |
| Unobserved standalone C context | `889b1451208e8f22d6b2b5fd4ee7f03d089de33d15f51cf2ad4bdf36cef0067f` |
| Positive observer/driver | `85bae41ab20db61decb7523f2cf113c0eb52165f6606c616943421b1c2325e48` |
| Policy / partial / fallback mutants | `60dd05921fbea8b15091099302292068748f3216cf0eed4f845357e5e17d3f55` / `2704d6693821e080175fcbf15223bdbf61ebde62420e2cc8498d9c3809144aa1` / `d9188c1549f5a8f4986b58170119f74d1300d63c317fd9829e72007c9f8119bb` |

The recipe rejects input drift, nonregular/symlink inputs, existing destinations,
repeat application and changed test-source bytes. It rechecks transformed bytes
before full QEMU compilation and requires the new unit in the actual compiler log.
Unused functions may be eliminated by the linker; compilation is not caller wiring.
All earlier strict-TCG transformations, source/archive/Git/wheel/NDK pins, build
limits, actual-link provenance and full-QEMU ELF checks are preserved. Only the
new module's path trigger is added to the existing workflow. No new dependency,
action, upload, privilege, target execution or Android APK/worker change is made.

## Controls and actual validation

Linux CI compiles the **actual emitted new translation unit** with an observed
OS context, then invokes the real constructor and planner. The trusted Python
controller creates synthetic input bytes, hashes them independently, and passes
read-only FDs. It also passes a test-only writer to change the backing after
admission. Neither a guest nor a downloaded kernel is used. The original 69 FD
tests and prior pathname/TCG controls remain separate and required.

**90 new cases are configured; Linux execution is pending/unobserved locally.**
They cover valid/exact-fit plans, empty ordinary mode, missing/null/copied/altered
admission, unknown versions, stale resource/epoch/digest, repeated admission and
planning, abort and cleanup, allocation/IO failure, ELF/uImage/gzip/zboot/legacy,
malformed and oversized Image extents, RAM wrap, changed RAM, all three overlap
pairs, alignment/size errors, each resource and feature flag, unknown bits and
unsupported machine/architecture/accelerator/CPU/DTB declarations. One declared
extent overlaps despite a short file; the same extent succeeds with a later DTB.
Each success/failure has an exact result, output and ownership expectation.

Positive children must exit 0, print exactly `PASS: typed boot plan case` plus
newline and have empty stderr. Independent source mutations must **compile first**:

| Mutation | Required failure |
|---|---|
| Skip the external-resource policy check; attempt external initrd | Exit 90, exactly `FAIL: plan expected result` plus newline |
| Write the output version before overlap validation | Exit 90, exactly `FAIL: partial plan publication` plus newline |
| Reopen a pathname after identity rejection | Exit 93, exactly `DENIED: adapter pathname/fallback` plus newline |

The pathname observer has a separate positive tripwire. Compiler failure, signal,
timeout, absent/extra output or a different error never counts as the expected
negative. Each execution is limited to five seconds. Source and binary hashes are
logged. Observers cover these C call boundaries, not libc internals or arbitrary
syscalls. No simulated firmware/ROM callback is presented as actual QEMU execution.

| Actual local evidence | Result and scope |
|---|---|
| Repository tests | 133 tests, OK: 129 executed passes and four pre-existing Windows skips. Six new tests cover source drift, transformation scope, pre-write validation, preserved destinations/reapplication, nonregular inputs and matrix/result classification. |
| Android syntax | Unobserved unit, positive observer and all three mutants passed NDK ARM64/API-30 syntax checks with warnings as errors, including missing/strict prototype checks. None executed. |
| Standalone link / ELF | 28,552-byte AArch64 dynamic PIE; SHA-256 `fcc79f8359afb87fcad385a78499cad9c626abff5a8e4c0015b40baec361aecc`. Four LOAD segments, 16-KiB alignment, no W+X or executable stack, RELRO/NOW, `/system/bin/linker64`, direct libc/libdl. Three plan API symbols present; snapshot constructor is private. All 14 dynamic imports match API-30 stubs and the narrow allowlist. This uses standalone include context, not the full QEMU translation-unit environment. |
| Source and repository hygiene | Immutable blobs, adapter identity, transformation hashes, Python AST, foundation/Markdown/requirements/ADR/provenance and harness-authority checks passed. Existing dependency declarations and all old top-level research functions are AST-identical. Exact-base full diff, modes, binary/dependency and public-data review completed before commit. |
| New Linux control execution / full modified QEMU cross-build | Pending/unobserved at publication. Existing Linux CI attempts both, preserving full artifact/link/ELF checks. |
| Android runtime, guest boot, physical isolation | Not run; Unknown. |

Local tools: bundled Python 3.12.14 and retained NDK r28c `28.2.13676358`, Clang
19.0.1 / Android build 13624864, upstream revision
`97a699bf4812a18fb657c2779f5296a4ab2694d2`; compiler SHA-256
`7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579`.
Compilation explicitly targets `aarch64-linux-android30`; this is not a proven
minimum host version. Local generated evidence stays under ignored build storage.
Reproduction uses the existing [bounded Linux recipe](gate-0-qemu-android-linux-crossbuild.md#reproduction-and-bounded-workflow),
which calls `apply` and `run_controls` after verified acquisition and prior controls.

## Remaining barrier and publication boundary

Within the tested helper there is no pathname or alternate-format fallback,
firmware invocation or ROM publication. **Across QEMU these paths remain available.**
No validated snapshot is handed to the ordinary pathname chain. The missing work
is a closed early machine-entry adapter, actual declaration verification, final
generated-DTB validation/ownership, private bootloader construction, address-space
correspondence, atomic or explicitly terminal ROM/reset publication and whole-caller
negative controls. A partial QEMU initialization cannot be called safely rolled back.

Even completing those steps would not contain hostile QEMU code. Independently
enforced worker containment, revocation, resource limits and trustworthy controller
identity remain blockers. This PR neither changes the host protocol nor integrates
QEMU into the APK or isolated worker. No phone, ADB, root, custom ROM, privileged
installation, host VPN slot, guest image or proprietary Google software is used.
A material production proposal still needs a separate ADR and Tony's approval.

Publish one focused research PR. Hosted CI is **pending/unobserved at publication**.
Immediately verify only PR identity, branch, exact head and available base, then
STOP without waiting, polling, rerunning or querying checks, Actions, reviews,
bots, approvals or status propagation. This reservation control does not constitute
Gate 0 success or advance any gate.
