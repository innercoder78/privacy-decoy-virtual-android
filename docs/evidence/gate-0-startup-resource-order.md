# Gate 0: QEMU startup configuration ordering witness

**2026-10-16, America/Fortaleza. Non-physical research. Gate 0: Unresolved.
Gates A–G: Not reached. ADR-0001: Accepted. ADR-0002: Proposed.**
No production VM engine is selected. Runtime Android authority, guest execution,
hostile-worker containment and revocation remain **Unknown**.

The result is the authorized **smaller source-grounded ordering control**, not
an exclusive resource-policy guard. At pinned QEMU, a guard after option parsing,
at `qemu_create_machine`, or at ARM board entry is too late to exclude prior
configuration-file access. The new control extracts the real first parsing pass,
option lookup and configuration reader, with an independent file-call observer.
It does not repeat the typed reservation model and does not change QEMU startup.

Scope: PDVA-REQ-010–015, 034–045, 048, 051, 054. The
[requirements](../requirements.md), [source policy](../source-provenance-policy.md),
[worker review](gate-0-qemu-worker-integration.md),
[kernel pathname audit](gate-0-qemu-kernel-resource.md),
[snapshot reader](gate-0-kernel-fd-snapshot.md),
[reservation contract](gate-0-arm64-boot-plan.md) and
[strict TCG controls](gate-0-tcg-executable-memory.md) retain their limits.

## Independent preflight and previous hosted evidence

Canonical GitHub branch API and independent `git ls-remote` both returned main
`15086b1c6b4a5bcfe14bbca1c416079c9bf378e5`, tree
`cabeff696f74a6da2028d7b437e8519035dc73b7`. Open PR inventory was empty, so there
were no open heads/bases/diffs or review threads to reconcile.
[PR #13](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/13)
merged head `18b66b3024b08ea19c9391070366f807c375be04` against base
`8213f3dac3f98c39dc8454c6b337fed90edb1837`; its merge is current main. Its seven-file
diff and merged contents were reviewed; the merge tree has no difference from
that head. Reviews, conversation/inline comments and review threads were empty,
with no further thread page.

All three PR #13 checks succeeded. The actual
[cross-build job](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38835092912/job/116762318662)
at that head records 69 snapshot cases, 90 reservation cases, their observers,
reservation mutants with precise exits 90/90/93, and strict TCG controls 0/91/91.
The log records the `hw_arm_pdva-boot-plan.c.o` build/link input and a 67,107,064-byte
QEMU artifact with SHA-256
`11f07afae9f7c760e3c7e63d20e9bba0242ae1df0e651a8c46e5200609493c2c`.
The required research step and job completed successfully. These are hosted log
observations, not freshly downloaded/rehashed artifacts or Android execution.
They supersede PR #13's historical pending status only for that exact old head.

Exact-main foundation run `38853741490` and Android run `38853741691` succeeded.
All three workflows were active; definitions, read-only permissions, exact-head
checkout, timeout/resource limits, no-upload behavior and pins were inspected.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational, page update `2026-10-16T03:19:25.204Z` UTC. Network-sandbox
failure was followed by successful authorized read-only queries.

The initial checkout was clean on PR #13's branch, with one registered worktree
and no stashes. All 84 tracked files were regular mode 100644. Existing branches,
ignored source/tool/build trees and binaries were preserved; the new branch starts
at verified main. No applicable AGENTS.md was found. Historical Privacy-Decoy was
untouched. Existing dependencies, Android source and verification metadata are
unchanged. No native Windows executable or security-setting change was attempted;
the [antivirus investigation](gate-0-native-host-antivirus.md) remains unresolved.

## Exact startup ordering and earlier side effects

All upstream links below name QEMU commit
**`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`**, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`. Upstream API identity matched the clean
retained Git checkout. Reviewed files matched immutable Git blobs after CRLF
normalization; CI admits only exact raw LF hashes from the pinned archive.

This is a source audit of the relevant startup spine, not an exhaustive audit of
every transitive library call, dynamic loader, constructor, environment variable
or host syscall. Feature-dependent paths below are source possibilities, not
claims that every path is enabled in the Android research build.

| Ordered stage | Exact-source observation / consequence |
|---|---|
| [system/main.c main](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/main.c#L73) | Calls `qemu_init` before the main loop. ELF loader/constructor activity precedes this boundary and is outside this experiment. |
| [qemu_init before parsing](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2854) | Registers option groups/modules, initializes executable-directory state and OS limits, target/module information, then calls `qemu_init_subsystems`. An interception at the first parsing pass is already later than these calls. |
| [qemu_init_subsystems](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/runstate.c#L972) | Initializes trace/QOM/migration modules, CPU loop and locks, exit notifiers, migration infrastructure, monitor globals, crypto, signals, block-driver whitelist and sockets. No claim that these are all free of host access. |
| [First pass and default config](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2911) | `lookup_opt` scans syntax and arguments; only `-no-user-config` changes first-pass selection. Next, `qemu_read_default_config_file` resolves the config path and calls `qemu_read_config_file`. The latter performs `fopen` before parsing groups. This is the extracted witness. |
| [Second pass](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2933) | Architecture-mask validation happens here, after default config access. `-readconfig` reads another file; `-dump-vmstate` directly opens a file with mode `w`; `-trace events=...` reads an event file through `trace_opt_parse`. `-acpitable` / `-smbios` call loaders with file-opening paths where supported. Help/type discovery may load modules. `-run-with async-teardown=on` calls Linux helper setup during parsing. These precede any proposed post-parse guard. |
| [qemu_process_early_options](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2594) | Processes name; creates pre-sandbox `thread-context` objects; applies sandbox/action settings; duplicates/registers then cleans up add-FDs; configures/open logs; adds firmware search directories. The pre-sandbox predicate is specifically `thread-context`, not all secret objects. |
| [After early options](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L3752) | Help processing, daemonization/PID-file creation, trace backend/file initialization, main-loop/timer initialization, global properties, replay configuration, RTC and memory-option transfer all precede machine creation. |
| [qemu_create_machine](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2205) | Selects/creates QOM machine and containers, initializes machine memory, applies machine-class defaults. Immediately afterward `cpr_state_load` can import migration state/FDs. Display/default-device setup follows. |
| [qemu_create_early_backends](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2034) | Console/early objects, SPICE, chardevs, filesystem backends, block backends and audio occur before machine-property application. Early object completion can load secrets from files. Pflash backends can already exist before ARM firmware selection. |
| [qemu_apply_machine_options](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2019) | Applies actual QOM properties after legacy-option processing; includes semihosting argument fallback. Accelerator configuration follows and ordinary QEMU can try alternatives. A resource declaration supplied separately by a caller cannot certify this state. |
| [qemu_create_late_backends](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2101) | Qtest, network clients, late objects, memory preallocation, TPM, monitors, serial/parallel/debug channels and semihosting chardev setup precede the board. Migration object initialization, CPU selection, memory-backend resolution and NUMA parsing follow. |
| [qemu_init_board](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c#L2719) / [machine_run_board_init](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/machine.c#L1612) | Plugins load before CPUs. Board runner creates/consumes RAM backends, completes NUMA and accelerator interfaces before calling the board initializer. A board-local rejection does not undo any earlier work. |
| [machvirt_init / firmware](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c#L2880) | CPU/memory-map work and possible secure-memory publication precede `virt_firmware_init`; that maps flash and can resolve/load BIOS. `create_fdt` occurs later, at line 3030. |
| [Generated DTB and ARM dispatch](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/virt.c#L3257) | `bootinfo.get_dtb` receives `machvirt_dtb`, then `arm_load_kernel` is called. Generated DTB remains mutable; machine-done invokes `arm_load_dtb` and further tables. ARM dispatch can select firmware/direct pathname paths, resets and ROM publication. PR #13 remains reservation-only. |

Additional inspected file-opening implementations:
[config reader](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/qemu-config.c#L186),
[trace events](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/trace/control.c#L203),
[SMBIOS](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/smbios/smbios.c#L1273),
[ACPI](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/acpi/core.c#L281),
[secret file](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/crypto/secret.c#L50),
[logging](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/log.c#L99).

## Intervention decision and unresolved guard

**Inference from the above source:** a useful exclusive entry must prevent generic
configuration parsing and its side effects before they occur, then inspect the
actual options/QOM state at the necessary later boundaries. Merely adding a check
before `qemu_create_early_backends` closes only a subset of earlier resource paths.
Likewise `-no-user-config` suppresses one implicit read; it is not a policy against
explicit configuration, tracing, firmware, devices, helpers or later mutations.

A narrower pre-parser intervention is conceivable: a separately restricted,
fixed research entry that cannot enter generic parsing, followed by checks over
actual machine/accelerator/resource state. This review does not establish its
complete initialization closure, immutable selection, defaults or terminal
failure path. Adding a normal CLI flag would not establish trusted selection.
**Authenticated/trusted mode selection: Unimplemented. Exclusive early guard:
Unimplemented.** No new flag, pathname API, privileged channel or partial boot
dispatch is introduced. There is no claim that a safe guard is impossible in a
future reviewed change.

The requested positive ARM64 virt/TCG/single-CPU/RAM admission and negative tests
for firmware, both pflash slots, BIOS, DTB, initrd, shim, kernel pathname, blocks,
writes, network, monitor, audio, display, chardev, devices, plugins, sharing,
helpers, migration, unknown versions/features, contradictory declarations,
stale admissions and legacy fallback remain **unimplemented at a QEMU caller**.
PR #13's typed tests do not fill that gap. No new fallback-rejection or atomic
initialization/rollback claim is made. Generated-DTB ownership, ROM publication,
resource revocation and complete process cleanup remain separate barriers.

## Falsifiable extracted control

[startup-order-research.py](../../.github/scripts/startup-order-research.py)
checks three entire immutable files before extraction. It emits unchanged
`lookup_opt`, `qemu_read_default_config_file`, `qemu_read_config_file`, and the
contiguous `qemu_init` interval from the first-pass comment through just before
the second-pass comment. A small wrapper supplies the original local variables.
The option table takes the actual first three `DEF` fields for five exercised
options from `qemu-options.hx`; it is not the full compiled option table.

The observer intercepts the extracted `fopen` and `fclose` call sites. The allowed
case calls real libc on one controller-created synthetic comment file, reads its
first byte and closes it. The parser is modeled and counted: no real QEMU config
group, machine, device or subsystem is constructed. Relocation maps the fixed
compile-time config name to that fixed test file. Error/location/allocator context
is modeled; missing-file and fatal-error propagation are not tested. No arbitrary
path is accepted by the fixture. Earlier subsystem/module/loader work is omitted.

A marker after the extracted interval represents a point *earlier* than any
post-second-pass guard. An observed open before that marker falsifies the proposed
later interception without pretending to execute the rest of `qemu_init`.
The observer is a C call-boundary instrument, not syscall interposition or sandbox.

Thirteen fresh-process cases are configured: successful implicit read; denied
implicit read; disabled read; double-dash alias; duplicate disable; positional
disk; invalid machine value; kernel pathname; explicit config option; dump option;
`-no-user-config` consumed as another option's argument; unknown option; missing
argument. The recognized resource options are witnessed only in the first pass;
their second-pass operations are static source findings, not executed tests.
Unknown/missing syntax exits 1 before opening; otherwise the implicit read can
reach the observer first. Disabled cases require exactly zero calls. Success
requires exact open/parser/close counts and exact output.

| Deliberate mutant | Precise required result after successful compilation |
|---|---|
| Defer `userconfig = false` until after default configuration loading | Exit 93; `DENIED: config open before late marker` plus newline, empty stdout. |
| Omit that first-pass suppression | Same exact exit 93 and diagnostic, empty stdout. |
| Reopen configuration in the actual reader after closing it | Exit 90; `FAIL: configuration boundary counts` plus newline, empty stdout. |

The third mutant checks unexpected repeated resource access; it is **not** a
legacy-boot fallback test. Compiler errors, signals, timeouts, unrelated errors,
missing/extra output or exit zero cannot satisfy a negative expectation.
Each child has a five-second timeout. The workflow's existing memory, file-size,
core-dump and overall time limits remain. Output uses a new directory and refuses
an existing destination. No source tree is patched or overwritten by this module.

## Provenance and validation

Whole QEMU archive pin remains
`a5a78e7d395ed096a7b2d98375978d0e2cf73f62c49a081ca48fa665d479b09f`.
Input SHA-256 identities:

| File | SHA-256 |
|---|---|
| `system/vl.c` | `a5fb2a78e45ec8edb256188eed44e8f06f7dba99c1dd029dd8a0d74cfab74266` |
| `util/qemu-config.c` | `706ec50d468d2754c7278ec9d1904ad19c263bc72457830944c639fa25fd3b79` |
| `qemu-options.hx` | `39be98e63d1b2d7b65bcec4bca0e704a2bb79cc4bb52a6f6d071babc189c6e63` |

The emitted control retains `vl.c`'s GPL notice. QEMU LICENSE assigns files without
their own notice, including this config reader, GPL version 2 or later. The
experiment retains QEMU's source and license obligations; no permissive relicensing
or production adoption is inferred. No generated C, binary, guest image or private
host data is committed/uploaded. Existing GLib/license, NDK/toolchain, archive,
wheel and Git dependency pins are unchanged. The repository owner maintains this
research recipe; distribution would require the applicable corresponding source
and notices, independently of this experiment.

| Generated LF control | SHA-256 |
|---|---|
| Positive | `7cd0e9cf81ddd0fe121dacd8220504dae99b12fc19ac0facb54c5587c6bd7f4f` |
| Late suppression | `07c00b9e9f3649f21c2cd913a14dab301e874df63e8e5b64b70ff5baa1a7e839` |
| Omitted suppression | `14e7e645830c3aa19e4228b5433cd9f77f9d95a897f0fa79d398fc7ffa105e73` |
| Reopen | `0acddbb08aa2db7449594d8fed1533bad29dd0b5c68d1aa201b678d5307106f9` |

Local Python 3.12.14 validation: **138 tests, OK, four existing Windows skips**
(134 executed passes), foundation and Markdown/provenance/requirement/ADR checks,
harness source checks, Python syntax and whitespace inspection. New tests cover
source identity/set rejection, each pin, ambiguous extraction, exact outcome
classification and the distinction between syntax rejection and early file access.

All four generated variants passed `aarch64-linux-android30` Clang syntax checks
with `-std=c11 -O0 -Wall -Wextra -Werror`. Retained NDK r28c compiler SHA-256:
`7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579`.
This is compilation evidence, not Linux or Android execution. Local WSL inventory
returned access denied; no host C control was executed.

The positive control also linked as an 11,272-byte Android AArch64 dynamic PIE,
SHA-256 `7f019e6e6b2a6f76872595f7146d37aba79c3b78d0fd29c7d5a5dd3f6f59087b`.
The existing ELF inspector passed: four LOAD segments with 16-KiB alignment,
no W+X or executable stack, RELRO/NOW, `/system/bin/linker64`, API 30/NDK r28c
identification and only libc/libdl direct dependencies. Its `fopen` import is
intentional witness behavior, not evidence of a restricted loader. The artifact
remains in ignored local build storage and was not executed or uploaded.

The existing bounded Linux recipe invokes this control after verified source
acquisition and the previous pathname witness, before snapshot/reservation tests.
All older controls and full-QEMU Android cross-build/ELF checks remain required.
No new QEMU compilation unit is introduced, so no new production caller compilation
is claimed. Full-QEMU compilation remains the unchanged recipe with PR #13 and
strict-TCG adaptations. Linux execution of the new controls and candidate hosted
CI are **pending/unobserved at publication**. QEMU boot, guest execution, APK/worker
integration, guest downloads and Android-device use were not performed.

Publish one focused PR; verify only its identity, branch and exact head/base, then
stop. Do not wait for, poll, rerun or query Actions/checks/reviews/bots afterward.
