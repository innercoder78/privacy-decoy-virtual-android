# Android 17 QEMU U-Boot provenance and verified-boot closure

Review: **2026-10-19, America/Fortaleza; Codex Desktop LOCAL, Windows x86_64.**
Source and published text-metadata research only. **Gate 0 Unresolved; Gates A–G
Not reached. ADR-0001 Accepted; ADR-0002 Proposed.** No firmware, engine, guest
configuration or security architecture is adopted. The [companion ledger](gate-0-android17-uboot-sources.md)
records exact sources, build records, preflight, validation and retrieval limits.
This continues [PR #24](gate-0-android17-boot-hal.md), not a general engine survey.
Scope: PDVA-REQ-001–015, 028–045, 048 and 054.

## Decision

**STOP this unchanged firmware/reference configuration as a PDVA release-trust
candidate.** Its provenance is substantially more traceable than previously
established, but traceability does not repair its reference security behavior.
Continue only independent source research with a new concrete trust-state
mechanism/falsifier; do not repeat the firmware-origin search or start dependent
guest construction. This is not a conclusion that all source-built U-Boot or
ordinary-app full-guest routes are impossible.

Three new results justify this focused record:

1. The selected QEMU firmware has a specific upstream import, build **15108624**,
   target **u-boot_qemu_aarch64**, attempt **1**, a resolved source manifest and
   published provenance statement. Its U-Boot source is
   `3fe9647575890b846172e546201eff7614c8cb59`. The selected prebuilt's text
   `System.map` matches the published build's subject digest. This is a credible
   documentary lineage, not binary reproduction or verified attestation.
2. That source implements the actual Android command, persistent environment,
   separate boot/init_boot/vendor_boot loading, bootconfig assembly, AVB and
   QEMU-generated DTB handoff. It also retains an OEM-lock host-service dependency;
   guest-local KeyMint/Gatekeeper does not remove this dependency.
3. The reference uses public test trust keys; newly initialized OEM-lock state
   is unlocked; the non-OP-TEE AVB rollback callbacks return zero/discard writes.
   Signature verification, locked-mode rejection and rollback persistence are
   distinct properties. The unchanged reference cannot establish PDVA's required
   release signing, protected trust state or anti-rollback guarantees.

## Exact identity and degree of correspondence

R retains PR #24's Android 17 r1 `aosp_cf_arm64_phone` / `vsoc_arm64`, QEMU
manager, nonprotected Android boot flow, default relevant flags and no supplied
product-output bootloader override. Cuttlefish is
`283645aacf6cdb56cc31a9362f54d412dbc132a1`; prebuilts are
`36f427b7c46682cfcdb2e61eee6893acbfb2a606`. These remain the release references,
not today's moving branches. Actual product outputs and an executed instance
are absent. Existing persisted lock state is not inferred from a fresh-state
default. Compatible Linux hosts select KVM; other hosts select emulation. [C]

The prebuilt Android.bp maps `bootloader_qemu_aarch64` to
`bootloader/qemu_aarch64/u-boot.bin`, installed as
`etc/bootloader_aarch64/bootloader.qemu`. The QEMU-specific default in `flags.cc`
selects it; ARM64 `qemu_manager.cpp` passes `-bios`. The separately named crosvm
module and its `bootloader.crosvm` file are not this selection. [P1; C]

The release snapshot and its parent import
`cd77f9d3211a4f8c22beb631b4bddcd99802cae8` have the same tree
`2cf5a792a03d756be8633db52d982f36333e7f51`. The import changes the QEMU binary
to Git blob `e4f067f8fa49256e565e054bec069620b7d104db` and names build 15108624.
Its abbreviated U-Boot log endpoint resolves to the full source revision above.
The update script actually obtains its log revision from the **crosvm** binary;
therefore that commit message alone would not prove QEMU correspondence. The
QEMU-target BUILD_INFO and manifest independently identify the same source. [P;
B; U-build]

The attempt-specific XML has **32 projects**; BUILD_INFO, repo.prop and provenance
materials also identify the separate `kernel/manifest` revision, giving **33 Git
identities**. All agree. `applied.prop` is empty, which records no applied changes
there; it is not a universal proof that every build input was unmodified. The
published command runs `//u-boot:qemu_aarch64_dist` with Kleaf/Bazel. U-Boot's
BUILD.bazel selects `build.config.qemu.aarch64`, which merges, in order:
`qemu_arm64_defconfig`, `qemu-minimal.fragment`, `arm.fragment`, and
`cuttlefish.fragment`, generating `cf-arm64_defconfig`. Later fragments restore
options disabled by earlier ones. Reading the base defconfig alone is incorrect.
The declared outputs are `u-boot`, `u-boot.bin`, and `System.map`. [B; U-build]

Compiler selection is Clang **r584948**, version metadata **22.0.0**, with LLVM
tools/LLD, AArch64 guest ABI, and pinned GCC compatibility prebuilts. The compiler
metadata identifies LLVM base `6d4a0935c850ec3ddfc70c4ba97b98adc35c676e`, a
cherry-pick ledger and compiler build manifest. These are Linux build tools,
not an Android host execution dependency of guest firmware. The build container
digest is recorded in both BUILD_INFO and provenance materials. The build log
reports success with 776 actions, but also configuration/deprecation, conversion
and linker warnings. They are not erased by that success. [B; T]

**Remaining correspondence Unknowns:** independently verified DSSE signature and
publisher trust root; direct selected-binary SHA-256 comparison; reproduction;
the generated final `.config` and complete action-level input closure; full
transitive tool/source/license qualification. The provenance subject names
firmware SHA-256 `29fba6031de38de5ba225925ca41defa02c28e0257305c4829d417bdaff85f6b`;
this is a **published digest, not a locally measured binary hash**. No firmware
payload was acquired. A matching System.map corroborates the import, but cannot
substitute for hashing the binary. The statement's completeness object is empty;
its build-service entry point is not a fully public build-service implementation.
The public recipe and source are credible research inputs, not complete shipment
approval. [B]

## Firmware-dependent Android boot contract

### Entry, memory and device description

U-Boot is guest AArch64 machine code. Its ARMv8 startup handles guest exception
levels; these are not host Android privileges. QEMU virt maps flash at guest
address zero and low RAM at `0x40000000`. The existing pinned QEMU candidate
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb` loads `-bios` into the first flash
region through a pathname. Its firmware route supplies a generated DTB at low
RAM, while normal machine construction adds the configured devices. This QEMU
source is PDVA's candidate pin, **not a newly proven source identity for every
Cuttlefish-distributed QEMU executable**. Machine-version/device agreement still
requires qualification. [Q]

U-Boot's QEMU board reads `CONFIG_SYS_FDT_ADDR`, default `0x40000000`, and derives
DRAM banks from that tree. Board late init sets `fdtaddr`, `loadaddr`, preserves
`/chosen/bootargs` as `cbootargs`, and scans virtio. The base load/initial-stack
address is `0x40200000`. The QEMU and crosvm memory-map branches differ; they
cannot be interchanged. These addresses are guest layout observations, not a
host mmap recipe or validated total memory budget. [U-entry]

Android image code reads vendor_boot DTB size/address fields for layout, but the
reviewed Android kernel call passes environment `fdtaddr` to `booti`. Do not
silently substitute a vendor_boot DTB for the generated QEMU tree or claim AVB
authenticated that generated tree merely because vendor_boot was verified.
Firmware and emulator must own a coherent final tree, chosen/initrd properties,
device topology and memory reservations. U-Boot's ARM handoff performs its boot
preparation and passes the FDT to the guest kernel. No final generated DTB or
runtime register state was observed. [U-entry; U-image; Q]

### Environment, disks and image assembly

`default_env.txt` scans virtio and, when present, imports `virtio 1#uboot_env`
through `env verified_import`; a failed import resets. Its Android command is
`verified_boot_android virtio 0#misc`. Cuttlefish's generated supplementary
`uenvcmd` selects `run bootcmd_android` for Android, with kernel arguments and
optional slot selection. EFI/GBL code exists in the same source but is not
thereby the selected Android flow. An absent environment partition takes a
different default path, not proof of complete reference inputs. [U-env; C]

The command gets the primary virtio disk, named `misc`/BCB and A/B information,
plus persistent raw disk device **1**. It selects suffixed partitions and invokes
AVB. The verified normal set includes `boot`, `vendor_boot`, and `init_boot`;
older-device fallback code does not authorize omitting init_boot from this
Android 17 product. Source permissiveness for missing optional data is distinct
from closure of the selected product's mandatory inputs. [U-boot; U-avb]

The loader preloads verified images, with packed/dedicated 64-MiB placement
choices, extracts the kernel, lays out vendor ramdisk then generic init_boot
ramdisk, and appends assembled bootconfig. It reads bootconfig before moving
the generic ramdisk to avoid overwriting preloaded data. Bootconfig combines
vendor data, slot/normal-boot parameters, the persistent bootconfig partition
and AVB-derived arguments. The persistent partition has its own verification
path. The final ramdisk length includes both ramdisks and bootconfig. Kernel
decompression, sizes, overlap, allocation and final FDT remain validation work;
source arithmetic is not a measured safe memory envelope. [U-image; U-boot]

Cuttlefish generates environment/bootconfig and persistent vbmeta. Its persistent
vbmeta chains `uboot_env` at rollback location 1 and `bootconfig` at location 2
on the separate persistent disk. These numbers are locations, not proof that
rollback values are stored. The product's main-disk chains use locations 1–5
for system, boot, init_boot, vendor_dlkm and system_dlkm, with security-patch
timestamps as configured rollback indexes. Key and partition namespaces must
remain explicit across the two disks. [C; U-avb]

The product additionally requires the selected kernel/modules, header-v4 images,
matching generated fstab, super/logical partitions, metadata and encrypted
userdata. First-stage init loads required modules and mounts verified logical
partitions; guest init/SELinux, APEX, Binder, ART, Zygote and SystemServer remain
the PR #23–24 contracts. U-Boot does not replace first-stage logical-partition or
filesystem verification. Full resolved kernel/module ABI and product-output
closure remain Unknown. Required ramdisks, bootconfig, DTB, partitions, AVB,
encryption and enforcing guest SELinux must all be retained. [C]

### Trust state is the decisive unclosed dependency

`avb_pubkey_is_trusted` compares against the compiled public key selected by
`CONFIG_AVB_PUBKEY_FILE`; the fragment names `testkey_rsa4096.avbpubkey`.
Cuttlefish's product and persistent-data generators likewise select reference
test keys. A normal locked path rejects verification/key/rollback errors;
unknown lock state fails. The unlocked branch requests
`ALLOW_VERIFICATION_ERROR`, reports orange state and can accept the specified
verification, rollback or key-rejection errors. This is an upstream reference
behavior, never an acceptable repair or release-trust proposal. [U-avb; C]

Lock state is obtained over the configured OEM-lock virtio console, index 10.
The QEMU manager supplies its FIFO peer; `secure_env` handles requests. The
default `oemlock` HAL selection maps to the host secure OEM-lock variant, backed
by TpmStorage. Its TPM defaults to an in-process implementation, not automatically
`/dev/tpm0`; the latter is a separate host-device selection. New OEM-lock storage
initializes **locked=false**. Existing storage may differ. Calling this reference
service “secure” does not establish host hardware backing or PDVA's required
state protection. The responder includes lock-state write operations; a protected
endpoint and lifecycle/authorization analysis cannot be omitted. [C; U-lock]

`CONFIG_OPTEE_TA_AVB` is conditional on the TEE/OP-TEE configuration. The selected
defconfig/fragments do not enable TEE/OPTEE; the inspected Kconfig has no default
enabling that driver. **Source-based configuration inference:** this route uses
the non-OP-TEE callbacks, which always read rollback zero and make writes no-ops.
The matching symbol map contains the callbacks, but is not final `.config` or
runtime proof. libavb compares signed indexes with the supplied stored values;
comparison with an always-zero value is not durable anti-rollback. Merely setting
the OP-TEE option would require its actual guest secure-world service, protected
storage and update semantics; it does not grant host TrustZone/TEE authority.
No such complete replacement is established here. [U-avb; U-config; P3]

## R/H exact-source dependency matrix

**H** is only the narrow mechanism hypothesis: source-built guest firmware under
ARM virt/TCG, bounded authenticated resource admission, generated device
description and ordinary virtual block/console devices, retaining the complete
Android verification contract. It is not R with AVB disabled, not a runnable
configuration, and not a proven smallest Android product. **No source-supported
complete release-trust implementation for H was established.**

F = Fact (direct metadata/byte observation, not a platform runtime fact);
S = Source Observation; I = Inference; H = Hypothesis; U = Unknown;
Unsupported = explicit disposition under project requirements.

| Required item | R: selected unchanged reference | H: narrow possible mechanism and falsifier |
|---|---|---|
| Exact firmware/source/build | F: import/tree/build/target/manifests and map digest agree. U: binary comparison, attestation trust and reproduction. | H: same resolved source/config is a credible build input. Positive requires exact output correspondence, final config and all build inputs; repository/tag/name alone rejects closure. |
| Guest ABI/machine/entry | S: AArch64 QEMU board and ARMv8 startup; QEMU `-bios`/virt. U: exact shipped QEMU pairing and runtime. | I: guest privilege does not require host root. H: TCG and qualified device/CPU/GIC pairing; reject KVM or another inaccessible host device as a hidden prerequisite. |
| DTB and RAM ownership | S: QEMU-generated tree at RAM base; firmware uses `fdtaddr`; image layout has separate regions. | H: validate final generated bytes and all reservations before publication. Missing/wrong DTB, overlap or unreviewed mutation rejects closure; a reserved span is not admitted DTB data. |
| Environment and boot selection | S: AVB-backed import, Android command, BCB/A/B and persistent disk. | H: exact authorized environment and partition ordering; reject missing signed environment dependency or unreviewed alternative command/fallback. |
| Kernel/ramdisks/modules/bootconfig | S: three boot images and ordered composition; C names kernel/module inputs. U: generated artifacts and module ABI. | H: preserve all required inputs and first-stage init. Missing init_boot, vendor ramdisk, bootconfig or module rejects closure. Raw Linux boot is Unsupported as full Android proof. |
| AVB/key trust | S: libavb and locked rejection exist; public test key is configured; unlocked errors can pass. | Unsupported: reference/test signing as release trust. Positive needs controlled release root, locked policy and tamper rejection; no insecure branch adoption. |
| Rollback, lock state, restore | S: non-OP-TEE callback semantics; OEM-lock console/default-unlocked state. I: selected source config lacks durable AVB rollback. | U: enforcing, persistent, crash/restore-safe state outside hostile authority. No complete H mechanism. No-op writes, zero/reset indexes, stale snapshot acceptance or guest-controlled state falsify qualification. |
| Logical partitions/userdata | S: main/persistent disks, vbmeta chains, dynamic fstab, metadata/encrypted userdata. U: generated layout. | H: bounded authorized virtual disks, correct namespaces and verified first-stage mounting. Missing partitions or dropping encryption rejects closure. |
| Host loading and attack surface | S: generic QEMU BIOS/path loading and Cuttlefish helper paths/FIFOs; parser/device/TCG attack surface. | H: trusted expected identities, bounded snapshots/FDs, typed early startup and no ambient loaders. U: firmware caller, final DTB commit, block/helper/FD lifecycle and hostile-worker containment. |
| Rights and maintenance | S: GPL/BSD/MIT/Apache file-specific references and pinned tools; U: full distribution package and transitive qualification. | Positive requires corresponding source/build scripts, notices, chosen distribution compliance and maintained ownership. A root license alone rejects acceptance. |
| End-to-end feasibility | F: no build or guest/device run in this investigation. | Unsupported: source success as Gate 0 pass or Android execution authority. U: full guest operation, interactive performance, containment and phone execution. |

The similarly named crosvm firmware, a U-Boot source repository alone, missing
boot dependency, test signing, incomplete source/license package, raw Linux boot,
and source-only Gate 0 claims are explicit negative controls. These are manual
source/policy counterexamples, not executed boot tests. Positive criteria require
the corresponding actual records and later separately authorized observations.

## Ordinary-app resource and supply-chain assessment

The guest firmware's MMIO, block commands, RAM addresses and exception levels
operate on the emulated machine. A source-built bootloader is not inherently a
privileged host executable and supplies no host execution authority. Host TCG
still needs legitimate packaged-code execution, signals, threads, memory/JIT and
lifecycle behavior. QEMU BIOS/image/DTB/block parsing and all virtual devices
remain hostile-input host attack surface even with authentic guest firmware.

A bounded authenticated-FD route is plausible for immutable firmware bytes and
explicit disk resources: a trusted owner supplies expected identity, length and
digest; the loader admits a bounded private snapshot and publishes only a
validated coherent layout. This is an **unimplemented hypothesis**. Current
[ARM64 reservations](gate-0-arm64-boot-plan.md) explicitly reject firmware,
initrd, pflash and other resources, cover a restricted raw Image and have no
machine caller. The [FD snapshot](gate-0-kernel-fd-snapshot.md) does not establish
authentication of its expected digest. [Startup ordering](gate-0-startup-resource-order.md)
shows why a late board guard cannot exclude earlier file/backend effects.
Do not relabel those controls as a firmware loader or enlarge their supported
input grammar in this source-only task.

R's host files, FIFO creation, shared RAM and helper processes are a Linux
reference deployment. H would need explicit ordinary-app-owned resources and
reviewed bounded transports; receiving an FD does not create prohibited
authority. Neither manager FD closure nor AVB verifies revocation of retained
mappings. [Containment](gate-0-worker-containment.md) and [revocation](gate-0-capability-revocation.md)
remain independent blockers. No broker, helper or production architecture is
selected by this assessment.

U-Boot's project license is GPLv2 with file exceptions. The reviewed board,
startup, AVB adapter and image code carry GPL-2.0+ notices; Android command/boot
and OEM-lock code include BSD-2-Clause; libavb uses MIT; Cuttlefish helpers use
Apache-2.0. The prebuilt module declares GPL-2.0-only. Distribution review must
preserve applicable notices and provide complete corresponding source, changes
and build/install scripts under the applicable GPL distribution route, with
separate transitive/tool/license review. It must not infer blanket rights from
one header. Kernel/modules, compiler runtime, libfdt, compression/crypto, libxbc,
EFI and host helper dependencies retain their own obligations. Guest/host
separation does not erase these obligations. No complete rights certification,
security-history audit or production maintenance owner is established; pinning
an old reference also needs ongoing vulnerability/update ownership before use.

## Answers and smallest next discriminating work

**A — Complete credible lineage?** Credible documentary source/build lineage:
**yes, newly established for the QEMU target**. Complete independently verified
source-to-binary/build/distribution closure: **no, still Unknown** for the exact
limits listed above. This is materially stronger than a filename or partial ID.

**B — Interface sufficiently specified?** **Yes for further static research**:
entry/DTB, environment, partition/image composition, AVB and lock-state callers
are identifiable. **No boot-chain closure**: generated inputs, protected state,
final config and runtime agreement are missing or fail release qualification.

**C — Plausible without prohibited app authority?** The guest CPU/resource
mechanism is plausible; firmware privilege is guest privilege. **R unchanged is
not an ordinary-app recipe**, and **H's complete security/authority path is
Unknown**. Do not assume OP-TEE options, TPM names or host helpers grant authority.

**D — Exact blocker and falsifier?** The immediate firmware-specific blocker is
a qualifying release root plus independently protected persistent rollback/lock
state, including update, manager loss and snapshot restore. The selected
non-OP-TEE callbacks and fresh unlocked state already falsify treating R as that
implementation. The smallest next useful source experiment must start with a
**concrete alternative implementation and pinned configuration**, then trace
every rollback read/write/commit and lock-state caller to its enforcing owner.
The newly located OP-TEE callback branch and OEM-lock responder are specific
leads, not an approved solution: a proposed route must identify its actual TA,
storage, transport, build and host authority before dependent work. Acceptance
requires nondecreasing durable indexes and fail-closed unauthorized write,
power-loss/restore and wrong-key paths; zero/no-op/resettable state or prohibited
host authority rejects it. If no such source implementation can be identified,
**STOP**, rather than write another equivalent search PR. Firmware reproduction
is not the next experiment while this security blocker remains.

**E — Samsung native-launch test?** **No change.** The existing fixed trusted
native-launch control asks an independent ordinary-app execution question and
still needs separate phone authorization and its recorded prerequisites. It
cannot resolve firmware provenance, rollback, complete Android boot or hostile
worker containment. This research neither authorizes nor makes a phone test
necessary now.

**F — Disposition?** **STOP this unchanged candidate as release firmware;
conditional CONTINUE SOURCE RESEARCH only for a new explicit security mechanism.**
No owner approval is requested for an unspecified redesign. If a concrete
replacement materially changes trust ownership, architecture or product scope,
present that design and a reviewed ADR for Tony's explicit approval before
adoption. Preserve full Android 17, enforcing security, genuine guest/host
separation, narrow brokers, Real/Decoy/Empty/Deny, no GPS fallback, no VPN-slot
takeover, no privileged production authority and no unauthorized Google software
or attestation bypass.

No Android code, firmware compilation, image acquisition, new tool/dependency,
APK, phone, ADB, emulator execution, workflow or roadmap change is included.
Local results and skipped/unexecuted checks are in the ledger. New-head hosted
CI is **pending/unobserved at publication**; prior-main success is not this PR's
result. After one immediate PR identity and native attachment check, stop.
