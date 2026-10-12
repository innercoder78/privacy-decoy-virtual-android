# Gate 0: QEMU integration requirements inside the isolated worker

Review: **2026-10-11, America/Fortaleza. Source-only research.** Gate 0 remains
**Unresolved**; Gates A–G remain **Not reached**. ADR-0001 remains Accepted and
ADR-0002 Proposed. Full interactive Android 17 remains the product objective.
No engine, JNI architecture, runtime dependency or new host authority is adopted.

The existing Android dynamic PIE is a credible **experimental executable**, not
a drop-in worker payload. JNI is not established as necessary. The concrete
obstacles are the current launch protocol, incomplete boot-FD coverage, TCG
memory fallback, display/input adaptation and unproved hostile-worker lifetime
enforcement. No inspected path proves a fundamental root/privilege requirement
for TCG. Conversely, no source/build observation proves stock-device execution
or guest-host containment. The smallest next experiment remains the existing
PDVA-owned native executable control, under a separately authorized physical run.

This record covers PDVA-REQ-002–015, 034–045, 048, 051 and 054. It refines the
[source survey](gate-0-userspace-vmm-sources.md),
[candidate assessment](gate-0-userspace-vmm-candidate.md),
[physical proof](gate-0-isolated-qemu-proof.md),
[cross-build record](gate-0-qemu-android-linux-crossbuild.md) and
[native-launch record](gate-0-isolated-native-launch.md). The physical proof's
JNI primary hypothesis is preserved; this comparison does not silently replace
it with an executable architecture. Its later Linux fixture is a mechanism test,
never a substitute for the required Android guest.

## Independent preflight and evidence identities

Canonical main independently resolved to
`1303dabc44d52db5a7bf35e9de321796dbf2a66e`. Open PR inventory: **zero**; there
were no open heads/bases/diffs/files/reviews/threads to reconcile. PR #8 was
merged from `ce2e3e50fb59aafb23f6a0dfa66ef874dc996112` against
`c2c63c86b5cee06d828d11377508cf54b3c0503e`; its five-file diff was inspected.
Reviews, conversation comments, inline comments and review threads were empty.
Its Android and foundation checks succeeded. Exact-main
[foundation run](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38183944688)
and [Android run](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38183944772)
and their required steps succeeded, including Ubuntu native positive/assertion
negative controls and Android build/protocol/release inspection. Combined commit
status had zero contexts; its aggregate `pending` is not another pending check.
All three registered workflows were active; their exact-head checkout, permissions,
paths and validation definitions were read. No workflow is changed here.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational, page update `2026-10-11T22:39:26.610Z`.

Local preflight: one registered worktree, clean at PR #8's source head, no stashes.
All local/remote branches were inventoried; the new research branch starts at the
verified main. Ignored nested build/reference trees, including a clean nested
canonical clone, were preserved. No reset, clean, stash pop or historical write
occurred. Requirements, both ADRs, authority/boundary/provenance records, build
dependencies, native inventory and the [antivirus incident](gate-0-native-host-antivirus.md)
were reviewed. Tracked entries have regular `100644` modes; foundation validation
checks tracked and non-ignored inputs for binaries, links and sensitive names.
Existing ignored artifacts are retained, not newly attested or redistributed.

QEMU inspection uses the retained clean checkout at
**`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`**, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`, independently matched to upstream's
commit API. This is the cross-build input, not the older `f9587d4…` survey snapshot.
The reviewed files below were compared, after CRLF normalization, with immutable
Git blobs. QEMU's two local cross-build adaptations live in the pinned
[research recipe](../../.github/scripts/qemu-android-research.py): Android
`qemu_shm_alloc` and libfdt discovery. They are **not** a patch to `util/memfd.c`.
The upstream checkout remains unchanged.

| Source at that QEMU commit | Reviewed functions / integration fact |
|---|---|
| [system/main.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/main.c) | `main`, `qemu_default_main`: initialization, BQL/replay lock transfer, loop, cleanup and process exit |
| [system/vl.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/vl.c) | `parse_add_fd`, `cleanup_add_fd`, `qemu_init`: FD inheritance, configuration and fatal exits |
| [tcg/region.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/tcg/region.c) and [accel/tcg/tcg-all.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/accel/tcg/tcg-all.c) | Split aliases, force-on failure, default setting, host-page alignment and cache sizing |
| [util/memfd.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/memfd.c) | `qemu_memfd_create/alloc`: memfd, resize, RW map and temporary-file fallback |
| [hw/arm/boot.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c) and [hw/core/loader.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/loader.c) | ARM kernel/initrd/DTB loading; ordinary `open` and GLib file reads alongside QEMU helpers |
| [util/osdep.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/osdep.c), [monitor/fds.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/monitor/fds.c), [block/file-posix.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/block/file-posix.c) | QEMU-specific `/dev/fdset/` resolution, access-mode checks, duplicate tracking, raw file backend and locking |
| [include/ui/console.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/ui/console.h), [ui/display-surface.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/display-surface.c), [ui/input.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/input.c), [ui/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/meson.build) | Display listeners/surfaces, typed event dispatch/synchronization, conditional UI dependencies |
| [util/coroutine-sigaltstack.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/coroutine-sigaltstack.c) and [meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/meson.build) | Coroutine backend selection, process-wide SIGUSR2 disposition, per-thread alternate stacks, executable target |
| [LICENSE](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/LICENSE), [COPYING](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/COPYING), [security.rst](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/docs/system/security.rst) | File-specific licensing, distribution conditions and absence of TCG isolation guarantees |

Selected SHA-256s of those LF source bytes:

| File | SHA-256 |
|---|---|
| `system/main.c` | `5209f230ab4a0d0794d3a2669b2a6d8154349283d8560eb8670044877122c242` |
| `tcg/region.c` | `466f430bb52f1be9224d5339cc36ff6bae2769ca1f85e688ca2dfbacdf6cdc81` |
| `util/memfd.c` | `0e1e5d0f022727c39cebc651789601334e233b585fef490f84283fde72001c67` |
| `hw/core/loader.c` | `5adca2184d46e03eed1122fa9c6e920fe8ffc340be7507021ed5afe53b1c47f0` |
| `util/coroutine-sigaltstack.c` | `89a4df0d94e9b541f01f96258f4f9e1312bc8d0b4794ba5accae383982817479` |

Retained AOSP `app.te`, `isolated_app.te`, `NativeLibraryHelper.cpp` and
`linker_main.cpp` were also read and rehashed: all four match the source hashes
and immutable identities in the [native-launch source ledger](gate-0-isolated-native-launch.md#official-documentation-and-source-review).
In particular, sepolicy `4571ddd9440721fec583c906a337de949a77749e` supplies
app-domain executable-memory and installed-APK-file rules; frameworks/base
`1cdfff555f4a21f71ccc978290e2e212e2f8b168` supplies native extraction; Bionic
`731631f300090436d7f5df80d50b6275c8c60a93` supplies executable-linker context.
These are source snapshots, not any OEM's installed policy. Browser retrieval
of the pinned QEMU and AOSP pages failed; clean local Git blobs and previously
hashed AOSP source bytes supplied the actual reads. No failed fetch is evidence.

## Previously observed build evidence, freshly checked against its log

[Run 38095872712](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38095872712),
job `114341523528`, succeeded at exact head
`379822d7f1b56e8f6d0f06a2476d4f9387f80ae7`. Its QEMU output was **66,991,384
bytes**, SHA-256 **`30e259f29a2cd7418bd674a1fb640f0608e9e571632e0ee2a4d06439bbdcab24`**.
The structured inspector reports Android API 30, NDK r28c, dynamic PIE, entry
`0x491240`, direct `DT_NEEDED` = `libz.so`, `libm.so`, `libc.so`; relocations are
7 ABS64, 11 GLOB_DAT, 351 JUMP_SLOT and 68,114 RELATIVE. Actual-link provenance
and ELF acceptance completed before the final inventory and completion marker.
This is a CI log observation; the binary was not downloaded or rehashed locally.
Earlier failed/static outputs must not inherit this identity or acceptance.

The log confirms `sigaltstack`, `CONFIG_MEMFD` and no `CONFIG_PIXMAN`. The recipe
uses `aarch64-softmmu`, ARM virt, TCG, PIC static third-party archives and dynamic
Bionic startup; modules/plugins, KVM, SLIRP, virtfs, libusb, OpenGL and blob
installation are disabled. Disabling defaults is not a runtime authority filter:
linked helpers and arbitrary native syscalls remain review surfaces. The build
proves neither a JNI library nor a graphical Android machine. No new compilation,
APK packaging, target execution, phone connection or ADB occurred here.

## Findings for the eight integration questions

Each numbered finding distinguishes source facts (S), earlier build evidence (B),
supported inference (I), an untested proposal/hypothesis (H), Unknowns (U), and
mechanisms unsupported for this scope (X). These are evidence classes, not scores.

### 1. Executable launch

**S:** QEMU's normal entry initializes the machine, runs its loop, cleans up and
exits the process. PDVA's [launch.c](../../android/gate0-harness/src/main/cpp/launch.c)
forks from the isolated worker and execs one fixed installer-owned executable;
it does not use a shell or run from writable app data. A `.so` packaging suffix
does not make an executable loadable through JNI. **B:** the dynamic PIE above
passed cross-build inspection; PDVA's separate small executable passed earlier
packaging inspection. Neither has observed physical launch evidence.

**I:** the executable route is credible for an experiment and avoids making QEMU
share ART's address space, signal state and JNI lifetime. The child remains under
inherited isolated authority, subject to actual exec policy; it is not a new
privilege boundary from its same-UID worker parent. **H:** a future fixed adapter
could deliberately retain exact resource FDs across exec. **U:** extraction,
fork/exec/seccomp, linker closure, identity/domain and descendant cleanup on a
stock device. **X:** substituting QEMU into today's launcher: its 1-MiB file cap
rejects this 66.99-MB output; it closes FDs 4–65535, reserves FD 3 as a CLOEXEC
error pipe, accepts only fixed argv, expects a 40-byte result/exit 42, and imposes
one CPU second plus a two-second alarm. Its wait-before-read pattern is for the
tiny payload and is unsuitable for continuous QEMU output. These are concrete
static contradictions to unchanged integration, not invitations to loosen caps.

### 2. Shared library / JNI

**S:** Meson produces an executable; `qemu_init`, `qemu_main_loop` and
`qemu_cleanup` are internal lifecycle entry points. `system/main.c` transfers
BQL/replay lock ownership; `vl.c` contains fatal process exits. The selected
coroutine source temporarily changes process-wide SIGUSR2 disposition and
per-thread masks/alternate stacks, protected only against its own concurrent
initialization. **B:** PIC archives were built; no reviewed shared-library export,
JNI entry, ART compatibility or repeated initialization result exists.

**I:** JNI can simplify direct display/input and FD handoff and remove the normal
extra child, but adds signal/thread/ART integration and broad framework state to
the compromised address space. It does not solve TCG authority or revocation.
**H:** a separately reviewed one-shot worker library could own QEMU's native loop
and a bounded queue, tolerating fatal exit of that disposable worker. **U:** symbol
visibility, TLS/relocations, packaging/namespace closure, cancellation, thread
ownership and coroutine coexistence. **X:** dlopening the dynamic PIE, calling
`main` as a reusable JNI function, relying on PIC alone, invoking QEMU inside the
current synchronized Binder handler, or loading it in management. Neither route
is selected; the earlier JNI-first hypothesis is not an adoption decision.

### 3. TCG executable memory, page sizes and isolation

**S:** `region.c:584–625` obtains a shared RW mapping through `qemu_memfd_alloc`,
then maps the same FD RX and closes it; mappings survive that close. Force-on
split-W^X failure returns an error (`694–729`). Auto mode may fall through to
anonymous memory later protected RWX (`823–850`). `tcg-all.c` normally defaults
split-W^X off unless debug TCG selects auto; explicitly request `split-wx=on` in
any future strict experiment. `memfd.c:108–148` retries memfd and then uses
`g_get_tmp_dir`/`mkstemp`. The reviewed Android `qemu_shm_alloc` portability patch
does not remove this independent TCG fallback. **B:** ELF 16-KiB load-alignment
inspection is build evidence; the existing generated-code probe is only RW→RX,
not QEMU's simultaneous alias allocation/cache-flush/coroutine path.

**I:** no static W+X ELF segment does not imply no runtime RWX. Split mappings
avoid a writable-executable VMA but retain a writable alias of executable bytes;
they are not containment of arbitrary native worker code. **H:** explicit split-on
plus a separately reviewed no-filesystem-fallback allocator could fail closed.
**U:** device memfd execution policy, seccomp/SELinux, executable mapping errors,
host page size, guard pages, instruction-cache coherence and CPU features. QEMU
uses actual host page size for region alignment; guest page size, ELF alignment,
APK packaging alignment and runtime mapping alignment are distinct obligations.
Dual mappings also consume virtual address space beyond the backing byte count.
**X:** granting directory access to rescue mkstemp, silent RWX fallback, policy
bypass, declaring a 4-KiB result valid on 16-KiB devices, or treating an API-30
compile target as a proven host minimum. JNI versus exec does not remove these
kernel-mediated requirements.

### 4. Kernel, initrd, disk and other resource capabilities

**S:** `parse_add_fd` requires inherited non-CLOEXEC FDs above stderr, duplicates
them CLOEXEC into a set, then closes originals. `qemu_open_internal` recognizes
`/dev/fdset/N`; the raw file backend uses it. FD-set duplication checks access
flags. In contrast, ELF/uImage loaders use ordinary `open`, and the compressed
ARM image and ROM paths use `g_file_get_contents`. A kernel's format/fallback
path therefore matters; `/dev/fdset/N` is not a universal OS filename.
**B:** loaders compiled, but no kernel/initrd/disk capability was exercised.

**I:** raw disks have a narrower existing FD mechanism than boot loaders.
**H:** management could authenticate immutable input, delegate exact read-only
regular-file FDs, and a reviewed loader adapter could read bounded offsets from
those FDs without reopening names. Restrict formats before parsing, cap encoded
and expanded lengths, audit overflow and short reads; avoid writable aliases or
concurrent replacement between authentication and use. Prefer generated virt DTB
over an extra external path; any supplied DTB/firmware/ROM needs the same inventory.
**U:** FD label/use permission, mmap/read/lock behavior, raw backend probes and
actual boot parser coverage. **X:** general open RPC, directory FDs, implicit
backing chains, arbitrary firmware search, writable-home extraction, or assuming
`/proc/self/fd/N` reopening is equivalent to using an already authorized FD.

### 5. Display and input

**S:** `DisplayChangeListener` provides graphics update/surface-switch callbacks;
QEMU input dispatch has typed key/button/axis/multitouch events and synchronization,
with run-state checks. These are internal hooks, not an Android transport.
PDVA's [Protocol](../../android/gate0-harness/src/main/java/org/pdva/gate0/Protocol.java)
only handles two synthetic 64×64 frames and 16 echo-like input tokens.
**B:** the build has no pixman; UI source uses conditional backends and compatibility
helpers. No display listener adapter, host renderer or guest input round trip was
built/tested. A compiled input helper is not proof that a desired guest device is
configured or usable.

**I:** both launch routes need a new bounded transport; JNI can call internal hooks
directly, exec needs a child-to-worker transport. **H:** copy a fixed-size software
frame into bounded shared storage and dispatch validated input on QEMU's owning
event-loop thread. **U:** chosen graphics/input devices, format conversion,
resize/stride behavior, concurrency, latency, ART/UI scheduling and the required
Android compositor/HAL/software-rendering path. **X:** claiming this binary already
implements an interactive guest, direct GPU/host-input passthrough, generic QMP,
unbounded VNC/network listeners or worker-supplied host Surface/service authority.

### 6. Death, cancellation, descendants and exhaustion

**S:** the current worker relies on cooperative owner-death/self-kill and a
30-second Java-looper lease. The fixed child sets PDEATHSIG, checks its parent
and uses bounded wait/kill/reap; the creating thread's lifetime matters.
Management persists uncertainty before launch and blocks retry without valid
cleanup acknowledgement. **B:** Ubuntu fake-operation wait controls passed;
there is no physical hostile-worker, orphan or quota result.

**I:** a compromised native worker/child can subvert cooperative callbacks and
self-reports, duplicate FDs or create descendants where policy permits. An exec
child adds cleanup complexity; JNI eliminates that normal child but not native
fork authority. Numeric PID/UID and Binder death alone are insufficient evidence
of descendant teardown or safe capability reuse. The 30-second lease and current
two-second child alarm contradict the later 120-second guest-boot proposal.
**H:** fixed stop messages, drained bounded output, per-epoch lockout and a reviewed
host-enforced termination/descendant strategy might establish a testable lifetime.
**U:** an ordinary-app mechanism that independently enforces this against native
compromise; process-level memory/thread/FD/CPU limits and Android background/OEM
behavior. **X:** treating self-imposed alarms/PDEATHSIG/process groups as a hostile
process-tree jail; assuming management can kill a distinct isolated UID; closing
its FD copy as revocation; treating RAM/TCG cache settings as total RSS quotas.
This is a **security blocker for guest integration**, not a passed prerequisite.

### 7. Adoption, redistribution and TCB

**S:** QEMU's LICENSE identifies GPLv2 overall, per-file terms and separately
licensed firmware. COPYING includes corresponding-source conditions for binary
distribution; TCG's permissive portions do not relicense the whole emulator.
The recipe pins QEMU, GLib, PCRE2, libffi, proxy-libintl, GVDB, dtc/libfdt,
keycodemapdb, softfloat/testfloat and host Python wheels. **B:** static target
archives and final link provenance were inventoried; a built dependency is not
necessarily linked into the final runtime. Direct platform imports were listed
above; the NDK stubs are build inputs, not the device's implementation.

**I:** exec can separate ART from QEMU's immediate memory/signal environment; it
does not automatically settle GPL combination questions. JNI linking demands
explicit review of the combined distribution. **H:** a future adoption record
could approve an exact minimal link/device/adapter closure with an assigned
maintenance owner. **U:** full file-level license compatibility, release source
completeness, independent reproducibility, security-update ownership and store
distribution eligibility. **X:** treating this research build's adoption scope as
APK redistribution approval, claiming a root license covers firmware or Google
binaries, or calling QEMU/TCG the trusted isolation boundary.

Required review before either integration includes:

| Component / obligation | Review needed beyond this source-only PR |
|---|---|
| QEMU, both existing patches and all future adapters | Immutable source/patch IDs, exact generated device/config/link maps, notices, corresponding source/build scripts and invocation/redistribution decision |
| GLib and its static closure | Exact GLib `e05063ccc6c8f222465a1080927f4c14349f3de6`, LGPL/file-specific terms; review static-link relinking obligations and provide applicable source/object/relink materials, not just a license label |
| PCRE2 10.46, libffi 3.5.2, proxy-libintl 0.5, GVDB and dtc/libfdt | Preserve recipe archive hashes and commit/tree identities; distinguish build-only from actually linked code; inspect BSD/MIT/LGPL and per-file exceptions as applicable |
| Generated keymaps, softfloat and test inputs | Record generator/data licenses and actual generated/linked closure; downloading a source subproject does not establish a runtime dependency |
| NDK r28c/LLVM, Bionic/zlib, SDK/AGP/Gradle and build infrastructure | Tool/source/binary correspondence, platform import closure, LLVM/runtime notices and SDK terms; retain existing Maven verification metadata, no new dependency adoption |
| Future graphics libraries, firmware, Linux fixture or Android guest | Separate immutable provenance/rights review; none imported. Avoid assuming pixman, renderer, firmware or a kernel is already approved |
| Enforcement TCB | Host kernel/SELinux/seccomp, linker/installer/framework, Binder/FD transfer, manager authentication/presenter/brokers, lifecycle observer and build/signing chain |
| Compromisable worker | QEMU, devices, translators, parsers, GLib/native closure and adapters; JNI also exposes resident ART/framework state. Review their vulnerabilities even though post-compromise containment must come from outside |

The existing [dependency ledger](gate-0-isolated-worker-dependencies.md) inventories
185 Maven components / 322 pinned artifacts for research tooling; no Maven app
runtime dependency is declared. The APK inventory remains two ABI-specific
`libsubstrate.so` entries and the ARM64 `libpdva_launch.so` executable. Neither
that inventory nor the old retained APK hashes imply fresh binary validation here.

### 8. Physical facts that source cannot resolve

**S:** the inspected Android rules and extraction/linker paths support hypotheses,
with platform/OEM policy and installed labels deciding actual authority.
**B:** CI built/inspected artifacts without executing them on Android.
**I:** credible compilation is necessary but insufficient. **H:** a release-equivalent
stock ARM64 device can exercise the existing tiny native control before QEMU.
**U:** all rows below. **X:** substituting emulator/root/userdebug, desktop Linux,
debug grants, synthetic fixtures or absent failure logs for stock physical evidence.

| Required observation | Why static inspection is insufficient |
|---|---|
| Host model/public build/API/kernel/ABI/page size, SELinux/seccomp and child identity | Source snapshot is not the OEM image; compile API is not host support |
| Native extraction, executable startup and platform symbols | Packaging and NDK exports do not establish installed paths/labels/namespace behavior |
| Split alias execution, cache flush, signals/coroutines and thread behavior | ELF W^X/alignment and the RW→RX toy probe do not exercise this path |
| Each delegated FD's actual label, access mode, bounds and retained mappings | Binder transfer does not prove loader/backend compatibility or revocation |
| Native attack authority and forbidden-resource probes | Disabled QEMU options do not remove arbitrary native syscalls |
| Non-cooperative death, descendants, manager death/restart and exhaustion | Self-report, unbind and Binder death cannot prove complete teardown |
| Sustained display/input, background operation, thermal/memory/energy limits | A boot or one frame cannot qualify the interactive Android guest |

## Narrow capability proposal, conditional on later review

This is an interface review target, not implemented authority. Keep management
secrets and image/signing/Persona state outside all worker and child address spaces.
Authorize each message by live caller/instance/epoch and fixed operation; child
transport would be bound to an exact FD and session, not a child-supplied UID string.

| Capability | Minimal proposed contract / mandatory rejection |
|---|---|
| Kernel/initrd | One authenticated immutable read-only regular FD each, fixed format and offset/length, bounded parsing/decompression. No name reopen or arbitrary resource request |
| Raw OS disk | Read-only file FD, explicitly raw backend, fixed size, no auto format detection/backing chain/device node. Validate requested open flags/locking against FD-set semantics |
| Scratch/userdata | Per-instance writable capability only. A regular writable FD grants resize/write authority beyond a QEMU logical disk cap: require independently enforced quota or a reviewed bounded block broker before claiming a hard disk limit |
| DTB/firmware/config | Generated/fixed internal configuration where possible; any external resource gets a separate approved identity/FD. No ambient config, firmware search, ROM, plugin, semihosting, hostfs or helper execution |
| Display | Manager-owned fixed dimensions/stride/format/byte cap; bounded copies of attacker-controlled pixels. Shared mutable metadata is never trusted for allocation or pointer arithmetic; snapshot and validate once, tolerate torn pixel content safely |
| Input | Fixed enumerated events, sequence/epoch, coordinate/contact limits, bounded queue/rate and overflow behavior; no host event-device or arbitrary command access |
| Serial/diagnostics | Bounded bytes/rate, independently drained pipe/ring, fixed numeric failure categories; no raw confidential logs, ANSI/command interpretation or UI/Binder blocking |
| Lifecycle | Fixed start/stop/status only, one fresh worker, no restart on uncertain cleanup; invalid epoch/duplicate/trailing fields/extra handles fail. Establish enforcement outside compromised code before claiming revocation |
| Network and personal data | No NIC, delegated socket, resolver, camera/mic/location/clipboard capability in this mechanism slice. No host VPN, GPS fallback, generic Binder proxy or management filesystem access |

The exec FD allowlist must be explicit and collision-safe, preserving only declared
resource slots while closing framework/Binder/logging handles; the current close-all
routine cannot provide that transport unchanged. JNI must inventory its inherited
framework handles too. Boot-FD ownership, shared buffers and raw disks need tests
for read-only violations, duplicate handles, stale epochs, truncated/mutated inputs,
overflow, resize, full queues and crash midway through handoff. No guest is needed
to design those controls; their future implementation remains separately reviewed.

## Single smallest next experiment and STOP conditions

**Propose only the already implemented fixed PDVA native-launch control on one
stock non-rooted ARM64 physical device, using a reviewed non-debuggable APK.**
It asks whether installed dynamic-PIE extraction → isolated-worker fork/exec →
linker startup → fixed result → direct-child reap is possible. It requires no
QEMU integration, JNI redesign, Linux kernel/rootfs or guest image. No phone/ADB
operation is authorized or performed by this PR. This is the next experiment
proposal, not a request to run it during this source-only task.

Prerequisites: separate physical-test authorization; review of the antivirus
incident and resolution of applicable execution/security blockers without
restoration/exclusions; exact APK/source/toolchain/signing identity and static
release authority/native inventory; normal user installation; public host
build/ABI/page-size inventory; synthetic data only; observable fresh worker and
durable uncertainty lockout. The successful main CI is useful baseline evidence,
not antivirus clearance or identity of an arbitrary local APK. Use the existing
control's fixed budgets/protocol and record individual fields, errors and Unknowns.

The scoped positive requires the expected 40-byte record and exit 42, successful
exec and PID/UID/eUID relations, expected isolation/context/capability/FD fields,
and matching direct-child reap with no timeout/kill/cleanup uncertainty. It says
only that this **trusted non-forking payload** completed that launch mechanism on
that host. Current in-app self-observation cannot independently prove hostile
descendant absence. No result passes TCG, QEMU, containment or Gate 0.

STOP on any new security alert; missing extraction or executable/loader denial;
unexpected identity/domain/capabilities/FDs; malformed/partial response; signal,
timeout, lost reply, uncertain reap or persisted uncertainty; observation failure;
or a proposed remedy requiring forbidden authority. Preserve bounded evidence,
do not retry around lockout, lower target SDK, move execution to management,
restore quarantine, allowlist, weaken protection or obtain development grants.
Classify a device-policy denial as a scoped failure only with sufficient evidence;
otherwise Unknown. A failure does not prove JNI succeeds or all OEMs fail.

Even a scoped positive leaves the FD-loader, strict TCG allocator, display/input,
licensing and external lifetime-enforcement blockers above. Review those before
authorizing any guest integration. Root/system installation, host VpnService,
unrestricted brokers and attestation bypass remain prohibited. NARROW/REDESIGN
requires the existing owner/ADR governance, not an implicit research PR decision.

## Validation and publication scope

Only this evidence record and its index cross-reference are intended changes.
Foundation/Markdown/provenance validation passed: 78 files, 43 Markdown files,
54 requirements and two ADRs. Existing repository regressions: 108 tests, OK,
four pre-existing Windows skips (104 executed passes). Harness source/manifest
authority and tracked Python AST syntax checks passed. All 19 linked QEMU source
files matched the pinned Git blobs after CRLF normalization. Exact-base text,
regular-file modes, public-data hygiene and whitespace were inspected; no binary,
dependency, production code or workflow change is included. The unavailable
WindowsApps Python alias was replaced with the already bundled Python runtime;
no interpreter was installed. No Windows PE compilation/execution, new Android or QEMU build,
runtime/guest/image import, phone/ADB access or external scanner submission occurs.
The antivirus incident remains unresolved; no binary safety verdict is inferred.

New-PR hosted checks are **pending/unobserved at publication**. Foundation applies;
unchanged Android and QEMU workflow path filters do not select these two Markdown
paths. No filtered job is represented as passing. Publish one focused PR, verify
only its immediately available number/branch/head/base, and stop without waiting
or polling checks, bots, comments, reviews, approvals or mergeability.
