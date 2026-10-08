# Gate 0: QEMU Android cross-build feasibility

**2026-10-08. Gate 0: Unresolved. Gates A–G: Not reached.**
QEMU is a **reviewed research candidate**, not a selected production engine or
shipped TCB component. ADR-0001 remains Accepted; ADR-0002 remains PROPOSED.
No harness, Binder, permission, CI, requirements or containment change is made.
No phone, ADB, Android emulator, guest execution or physical test was used.

## Decision and scope

**Continue non-physical build research; do not integrate QEMU yet.** Two actual
out-of-tree Android-targeted QEMU configure attempts failed before Meson setup
completed. No QEMU emulator was compiled or linked. The immediate failure is a
Windows/Git Bash/native-Python build-host mismatch, not evidence that Bionic or
isolated Android execution is impossible. The complete dependency build remains
unfinished. Separately, the exact QEMU-pinned **libfdt** source cross-compiled and
linked successfully for Android ARM64/API 30. This is dependency evidence only.

There are concrete integration gaps: a JNI adapter, narrowly scoped boot-FD
loaders, TCG memory-allocation policy, signal coexistence, and a supervisor that
can observe/revoke a compromised native worker. A build will not resolve these
runtime questions. No architectural contradiction has been established by this
experiment. Stop work depending on a working emulator until one exists; retain
STOP/NARROW/REDESIGN if prohibited authority proves necessary. Do not select
another engine or weaken ordinary-app authority to repair this result.

Relevant obligations are PDVA-REQ-002, 003, 006–015, 034–045 and 048.
The [governing experiment](gate-0-isolated-qemu-proof.md) and
[evidence terminology](../acceptance-evidence-criteria.md) still govern.
The [execution ledger](gate-0-qemu-android-crossbuild-execution.md) contains
commands, versions, hashes, configuration, errors and reproducibility limits.

## Live preflight and inventory

Before edits, canonical remote main resolved to
`8ac8cd5390db51d334c09b336d40235a8859d41e`. PR #4 was merged at
`2026-10-08T07:27:10Z`, with that merge commit. Its six-file documentation change
covered ADR-0002, delivery, guest lifecycle, roadmap, UX and README. The clean
local PR #4 branch had identical content to main; it was preserved, and the
research branch was created from exact main. One worktree, no stashes and no
unrelated dirty tracked work were observed. Existing ignored tools were preserved.

Every open PR was enumerated: **zero**. Accordingly there were no open-PR
heads/bases, diffs/files, checks, reviews, comments or unresolved threads to
inspect. The exact-main foundation workflow was completed/success. The latest
Android substrate success was at `a7b0d2c6044cc3acf4569edb114c6e0622655ee9`;
the documentation merge did not rerun it. Both workflow definitions were read.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
`All Systems Operational`, indicator `none`, page update
`2026-10-08T14:54:42.139Z` at preflight. These are pre-publication observations.

The baseline has 64 regular `100644` tracked files, no submodule or symlink
entries, and no tracked APK/SO/JAR/kernel/image. Source policy, requirements,
ADRs, architecture, roadmap, gates, evidence criteria, existing QEMU evidence,
proof specification and worker source were inspected. The historical repository
was neither needed nor read or modified.

The existing dependency ledger lists 185 build-only Maven components and 322
hashed artifacts; the harness declares no runtime Maven dependency. Its only
native source is PDVA's substrate probe, linking platform libraries. Existing
trusted roles include management/supervision, broker validation, build/signing
infrastructure and the proposed Android kernel/UID/SELinux boundary. The latter
is **not proven**. This PR adds no runtime dependency to that inventory. Temporary
QEMU sources, bundled upstream wheels, libfdt, probes and outputs remain ignored
or outside the checkout; no experimental binary is published.

## Findings matrix

“Verified Fact” below means a direct build/repository observation for this run;
“Source Observation” is identified source behavior, not a runtime guarantee.
Upstream Claim, Inference, Hypothesis, Unsupported and Unknown retain their
separate meanings under the acceptance criteria.

| Question | Evidence | Finding | Limit |
|---|---|---|---|
| Exact QEMU source identity | GitLab tag/checkout and matching GitHub mirror | Verified Fact: v11.1.2, exact commit below | Tag signature not independently authenticated; no complete audit |
| Android NDK compilation | Actual configure attempts; compiler controls | Fail at QEMU build-host setup; full compilation Unknown | No QEMU C build/link or executable produced |
| Required native dependencies | QEMU/GLib Meson and wrap files; libfdt ELF | Source Observation: core graph identified; libfdt build Pass | Full configured/transitive linked graph Unknown |
| JNI/native launch route | QEMU main/Meson; harness source | Candidate: packaged JNI library with reviewed adapter | No stock stable Android embedding API; no adapter implemented |
| TCG executable memory | region.c, memfd.c, cacheflush.c | Hypothesis: explicit split-wx=on might operate | API link availability is not Android execution or policy evidence |
| Isolated UID containment | Existing worker/source only | Unknown until tested | No host-sandbox or post-compromise security claim |
| Tiny Linux fixture boot | Source/configuration proposal | Unknown: not built or booted | No desktop smoke test; no Gate 0 pass |
| Full Android 17 guest | Not implemented | Unknown | Gate A not reached |
| Root/KVM/AVF/shell-dependent repair | Requirements and experiment exclusions | Unsupported for this route | Intentional scope restriction, not a measured platform denial |

## Source candidate and supply chain

The [official download page](https://www.qemu.org/download/) listed 11.1.2
(released September 28, 2026) at review. Select that maintenance release for
research instead of automatically adopting the prior moving-development snapshot
`f9587d4045c67cd0d8d8bdcd5d0bb5b6b395b63c`.

- Upstream: `https://gitlab.com/qemu-project/qemu.git`.
- Annotated tag `v11.1.2`: `ceaea6cb3e2a7d966f9ca97c7ebb5b88cd764dd0`.
- Peeled commit: `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`.
- Independently queried `https://github.com/qemu/qemu.git` returned both same IDs.
- Git source and bundled wheel identities were inspected. Firmware submodules
  were not initialized; the optional Rust graph was disabled. No inherited
  Android fork patches or downloaded emulator binaries were used.

This identity and inspected source are adequate for the bounded local configure
experiment, not shipment or a complete source-completeness claim. The build must
still freeze every fetched wrap/patch and all compiled/generated inputs. Git
mirror agreement is consistency evidence, not independent publisher signature
verification. The official release-page URL returned 404 and the wiki changelog
was bot-blocked; release selection uses the official download page, exact refs
and inspected stable commit history, not those failed retrievals.

The exact [LICENSE][q-license] describes the emulator as GPLv2, file-specific
compatible licenses, and separately licensed firmware. TCG's largely permissive
files do not relicense the full emulator. Inherited coroutine code includes
LGPL-2.1-or-later notices; preserve file-level notices and provenance. Linking a
JNI adapter or statically bundling LGPL libraries creates distribution obligations
that require a separate review, including corresponding source/relinking details
as applicable. This experiment grants no distribution approval and adds no
repository-wide license declaration.

**Upstream Claim:** [the selected security policy][q-security] excludes TCG from
its supported guest-isolation guarantees and security-bug treatment. Even with
`virt`, hardware-accelerator coverage does not transfer to TCG. Assume arbitrary
native code execution in the worker. QEMU supplies the emulated machine, not the
post-compromise boundary. Guest RAM does not bound total QEMU memory consumption.

**Source Observation, bounded security-history review:** the selected stable
history includes [xHCI timer reentrancy hardening for CVE-2026-17588](https://gitlab.com/qemu-project/qemu/-/commit/ed582623e2372fdf862a804d122766052aba81c7)
and [9p FID race correction for CVE-2026-93834](https://gitlab.com/qemu-project/qemu/-/commit/abae50de244a51ae4e959274e2ef6cbf373464ff).
USB and host sharing are excluded from the fixture, but these illustrate device
and threaded-backend attack classes. The generic
[TCG multiply-folding correction](https://gitlab.com/qemu-project/qemu/-/commit/20d62bf3a9a083ca1580695d1f52b317e972734c)
and deposit optimization fix `99d5f67cc4eac27d231b8253f253042afa2a79f2`
show why an up-to-date translator baseline matters beyond CVE lists. This is not
a comprehensive vulnerability assessment or a claim that this release has no
unfixed bugs. Monitor ordinary TCG bug reports as well as
[upstream security notices/process](https://www.qemu.org/contribute/security-process/).

PDVA's repository owner retains research update/review responsibility under the
existing source policy: re-pin, inspect changes, rebuild, invalidate affected
results and stop using a suspect candidate. No separately staffed production
maintenance owner or response SLA is assigned; that remains a shipment blocker.

## Native dependency and tool graph

| Component | Reviewed identity / requirement | Role and unresolved work |
|---|---|---|
| QEMU | Exact commit above; Meson >=1.5.0, Python >=3.9, GNU11 C | Configure generates Meson cross/native files, then Ninja builds; host generators require host tools, not Android executables |
| NDK | Existing Google r28c `28.2.13676358`, clang-r530567e / Clang 19.0.1 | Actual Android compiler; API 30 selected to match harness research minSdk, not product host support |
| GLib | QEMU needs >=2.66.0; reviewed candidate 2.90.1, `e05063ccc6c8f222465a1080927f4c14349f3de6` | Required utility/main-loop library; LGPL-2.1-or-later root notice, file exceptions need inventory; not built |
| GLib transitives | Candidate's Meson: PCRE2 >=10.32, libffi >=3.0.0, zlib, iconv, intl/proxy-libintl as detected | Wrap pins in execution ledger; exact selected link closure remains Unknown; no host pkg-config contamination allowed |
| libfdt | QEMU dtc.wrap pins `b6910bec11614980a21e46fbccc35934b671bd81` (dtc v1.6.1) | Required for AArch64 target; all ten selected libfdt C units and headers carry GPL-2.0-or-later OR BSD-2-Clause; Android archive/shared library built |
| zlib | Required in QEMU Meson; NDK supplies Android libz interface | Platform runtime version follows host OS, not NDK revision; alternatively source-build a separately reviewed pin. No libz was linked in the libfdt-only experiment |
| Pixman | Optional >=0.21.8 check; explicitly disabled | Serial-only slice needs no display; later framebuffer/device choices must revisit source, license and build |
| GModule/GIO | Conditional in QEMU Meson | Modules/plugins/GIO disabled by small configuration; building GLib may still need GObject/libffi build dependencies |
| Other backends | Rust, SLIRP, GTK/SDL/VNC/SPICE, audio, VFIO/vhost, 9p, crypto/network storage and plugins not requested | Verify final Meson summary, Kconfig and link map before claiming exclusion; configure did not complete |

[GLib source][glib-build] distinguishes Android from generic Linux in some
checks; use Android host-system metadata for its cross file. Its 2.90.1 NEWS
includes bounds/overflow and malformed-input corrections. The older 2.86.1 tag
was initially resolved but not adopted; 2.90.1 is the source-analysis candidate.
The wrap dependencies and patches have not received complete file/security review
and were not automatically installed. QEMU's native dependency closure is
therefore **identified but not fully built or approved**.

The configured bootstrap used bundled Meson 1.11.1, pycotap 1.3.1 and qemu.qmp
0.0.6, plus local QEMU Python tooling. These are host-side packages, not Android
runtime payloads. Existing Python 3.12.14, pip 26.2.1, setuptools 84.0.0, wheel
0.48.0 and Ninja 1.10.2 were observed. The Python environment inherited unrelated
installed host packages, so it is not hermetic. No new CI dependency was added.

## Android portability and packaging

**Source Observation:** QEMU configure classifies an NDK compiler defining
`__linux__` as Linux. Its Rust detection additionally knows Android. That does
not make Bionic glibc: independently cross-compile every dependency, use the NDK
sysroot/API stubs, keep target pkg-config files separate, and never run a target
binary as a configuration probe. A Linux-desktop QEMU build is a different result.

[Android's build guidance](https://developer.android.com/ndk/guides/other_build_systems)
identifies `--target=aarch64-linux-android30` as an API-floor-qualified target.
The current harness compile/target SDK is 37; NDK API 30 is a separate research
floor. r28c is the already reviewed harness tool, not a claim to the newest NDK.
Its [changelog](https://github.com/android/ndk/wiki/Changelog-r28) records flexible
16-KiB alignment defaults. Inspect every final ELF segment and APK packaging;
never infer runtime page-size correctness from a compiler version alone.

**Verified Fact:** a small memfd/eventfd/pthread/sigaltstack program linked against
API 30, whereas the `makecontext` probe failed at undeclared-function compilation.
Neither ran. QEMU [Meson][q-meson] tries ucontext then sigaltstack. Its
[coroutine fallback][q-coroutine] temporarily manipulates SIGUSR2 handlers,
thread signal masks and alternate stacks and disables fortify for that unit.
Coexistence with ART/Bionic and other QEMU handlers is an unresolved review/test
item. Do not add a fake makecontext shim or suppress a hardening failure blindly.

Other required source paths include POSIX threads/mutexes/condition variables,
TLS, signals, clocks, poll/event notification, mmap/mprotect/munmap, memfd,
ftruncate, pread/pwrite, fcntl and file metadata. Header/link availability and
Meson feature tests cannot show SELinux/seccomp/kernel permission to execute
these operations in an isolated UID. Inspect getauxval/HWCAP, proc/sys accesses,
entropy, temporary files, thread naming and all fallback paths in the final build.

A candidate JNI shared object should use PIC objects, a narrow export map,
explicit SONAME, checked DT_NEEDED closure, no host RUNPATH, and only public NDK
libraries. QEMU's default `b_staticpic=false` and executable link recipe are not
a ready-made embeddable shared library. Static PIC GLib/libfdt/PCRE2 dependencies
could reduce loader dependencies but increase size and license/update duties;
dynamic libraries require a complete packaged closure and compatible namespaces.
Do not statically bundle a second libc into an ART-loaded JNI library.

[Android linker rules](https://android.googlesource.com/platform/bionic/+/master/android-changes-for-ndk-developers.md)
cover SONAME/DT_NEEDED, text relocations, ELF validation and direct APK loading.
Use ordinary package-managed native-library loading in the isolated worker as
the lead hypothesis. The current `System.loadLibrary("substrate")` is only a
source precedent, not a physical QEMU loading result.

An executable PIE is different from a shared library even when ELF type is DYN.
It may need `/system/bin/linker64`; renaming it `.so` does not create JNI exports
or prove launch authority. Android 10's
[app-home execution restrictions](https://developer.android.com/about/versions/10/behavior-changes-10#execute-permission)
rule out assuming arbitrary writable-private-directory executables can run.
APK extraction, native-library directories, isolated-UID accessibility, exec
policy, child lifetime and descriptor inheritance need their own evidence.
Do not grant filesystem/shell authority or make the manager execute QEMU to
rescue the experiment. No executable packaging route has been validated here.

## TCG memory, machine and boot resources

[region.c][q-region] implements POSIX split mappings through a shared backing FD:
a writable view and an executable view of the same storage. Explicit
`-accel tcg,thread=single,split-wx=on,tb-size=64` is the proposed fail-closed test
choice. Source allows default-on split failure to fall back; force-on reports
failure instead. Separate mappings still expose mutable generated code through
the alias and do not establish a security boundary.

[memfd.c][q-memfd] can fall back to `mkstemp` under GLib's temporary directory
when memfd creation fails. A future adapter must reject that ambient-file
fallback or replace it with specifically reviewed delegated backing authority.
Do not create a broad writable directory for convenience. Android memfd flags,
execution policy, quotas and syscall availability remain runtime Unknown.
[cacheflush.c][q-cache] handles distinct RX/RW addresses and AArch64 instruction
cache maintenance; replacing it with the harness's simple RW-to-RX probe is not
equivalent. TCG threading, cache invalidation, executable permissions, BTI/PAC
where applicable, and signal handling need exact-build review and later tests.

The executed Kconfig input explicitly selects `CONFIG_ARM_VIRT=y` with
`--allnoconfig`; it resolves 41 enabled device symbols, including PL011, GIC,
fw_cfg, ACPI, PCI, flash, SMMU and semihosting infrastructure. “Only virt” does
not mean only a UART is compiled. `--without-default-devices` alone is not enough;
use the actual `--with-devices-aarch64=pdva` mechanism and inspect its closure.
Disable semihosting at invocation; no guest NIC, passthrough, audio, GPU, host
sharing, monitor or generic QMP is part of the fixture. No final compiled-device
inventory exists yet. Optional backend switches are not a sandbox.

[ARM virt][q-virt] and [boot.c][q-boot] support a direct kernel/initramfs route
with QEMU-generated DTB; select a 64-bit CPU explicitly (candidate cortex-a53).
No UEFI, U-Boot, BIOS ROM or guest boot loader is required for the proposed
serial direct-boot slice. Firmware files bundled upstream remain separate
licensed programs and must not be installed/shipped by default. QEMU's generated
boot stub is source-derived machine code, not a separately imported ROM.

[loader.c][q-loader] uses ordinary `open` and GLib file reads on several
kernel/initramfs paths. QEMU fdsets apply to QEMU-aware block opens and do not
magically convert every POSIX/GLib open. `/proc/self/fd/N` reopening is also not
assumed available or authority-equivalent. Plan a small reviewed FD-backed loader
adapter: manager-authenticated bytes, exact length/hash, verified immutable backing,
a read-only FD, no filename supplied by the worker, bounded pread and no path
fallback. A read-only open alone does not freeze content; review seals or other
protection against post-verification mutation before delegation. Initial
scratch, if later added, must be explicit raw storage with no backing-chain or
format autodetection and a separate capability review.

## Tiny Linux fixture proposal — not built

Use current reviewed LTS candidate Linux **v6.12.112**, upstream
`https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git`, peeled commit
`7aba70ab2e8d8ab3cd45abcaa15e1119a00dc42a`, tag object
`1092ff6640e96a20f741340bac5187c31070f091`. Both were resolved live;
[kernel.org](https://www.kernel.org/) listed this LTS update on October 3.
An earlier v6.12.57 lookup is superseded, not a fixture pin. Source/kernel build,
signature verification, exact final .config and artifact hashes remain undone.
Linux is GPL-2.0-only with syscall-note/file exceptions; inspect exact licenses
before building. This is a trusted synthetic research fixture, never an Android
guest or approved product kernel.

Smallest candidate userspace: one reviewable, newly authored freestanding AArch64
`/init`, with an explicitly licensed source and direct Linux syscalls, avoiding
BusyBox/Buildroot/libc dependencies initially. It should print a fixed marker,
verify one deterministic arithmetic/memory result using guest syscalls, print
success/failure, and power off. Its exact source identity is **not assigned**;
freeze source, license and hash before the future build. No ready-made initramfs.

Proposed kernel configuration starts with ARM64 `allnoconfig` plus reviewed
fragments for MMU, ELF binaries, initramfs, OF/device tree, PL011 console,
ARM generic timer/GIC and required virt platform/poweroff support. Keep modules,
networking, PCI drivers, graphics, audio and unneeded filesystems off. Generate
an uncompressed `newc` archive containing `/init` and `/dev/console` (character
5:1) via the kernel's `usr/gen_init_cpio`; no root is needed to describe nodes.
Use the kernel's LLVM build route with a separately pinned host Linux LLVM/build
toolchain, not an Android Bionic userspace sysroot. Resolve final Kconfig
closure and compiler identity rather than calling this fragment build-tested.

Boot inputs: uncompressed ARM64 Image, reviewed initramfs, generated DTB,
`virt-11.1,gic-version=2`, cortex-a53, one vCPU, 256 MiB RAM, 64 MiB TCG cache,
`console=ttyAMA0 rdinit=/init panic=-1`, explicit TCG, no network/display/monitor,
semihosting disabled. Expected serial markers are
`PDVA_FIXTURE_BEGIN`, `PDVA_FIXTURE_SYSCALL_OK`, `PDVA_FIXTURE_DONE`; these are
acceptance targets, **not observed output**. Propose caps of 32 MiB kernel and
1 MiB initramfs, 64 KiB exported serial bytes, and the governing 120-second boot,
768-MiB worker and 5-second stop budgets. These remain hypotheses, not measured
size/performance or enforceable ordinary-app limits. An initramfs alone is not
inherently immutable after boot; its input FD can be read-only while guest RAM
changes. A block read-only OS/scratch proof is a later fixture extension.

Serial success would cover only the earliest boot sub-experiment. The governing
proof also needs disk controls, display/input, adversarial native probes,
revocation and repeated lifetime tests. Do not call a serial-only result its
completion. No desktop smoke test was possible with a completed known QEMU and
fixture in this run; no substitute prebuilt image was used.

## Future isolated-worker integration boundary — design only

[WorkerService](../../android/gate0-harness/src/main/java/org/pdva/gate0/WorkerService.java)
is non-exported/isolated, rejects callers outside the manager UID, validates
fixed transactions/epoch, and accepts only two 4096-byte regular files and fixed
shared memory today. [Session](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java)
binds a fresh named isolated service, generates its epoch, watches Binder death,
and blocks another session when the previous worker might retain capabilities.
The owner Binder exposes no application operations. The sentinel locator and
synthetic memory/FD test metadata must never be confused with Persona secrets.

The current RUN executes synchronously under the Binder transaction lock. QEMU
must not be inserted there: its main loop can block control indefinitely. A
future reviewed adapter would load only in the worker and start on a dedicated
native thread, with fixed internal options, one VM per fresh process, explicit
thread ownership and bounded control handoff. [main.c][q-main] initializes global
state and exits the process on completion; it is not a reentrant JNI function.
A wrapper needs defined error/exit handling and symbol scope, not a blind call
to `main` in management. No restart of QEMU globals within the same worker.

Management authenticates exact boot inputs, opens read-only kernel/initramfs FDs,
checks length/identity, and delegates only those plus a bounded console pipe/ring
and any separately approved scratch capability. It retains Persona databases,
keys, update verification, policy and other instances. No directory FD, arbitrary
path-open RPC, socket broker, general QMP, arbitrary exec or guest-selected host
operation. Keep `/dev/kvm`, AVF, GPU/render, camera/audio, external storage and
ambient network unavailable; source omission does not prove actual denial.

Console handling should drain off the UI/Binder path, cap bytes/rate and truncate
or fail with a fixed category, treating all content as attacker-controlled.
Never allow a full pipe to block STOP or a log string to become management code.
Kernel/DTB parsers and native device code stay in the assumed-compromisable
worker; the manager consumes only bounded typed reports tagged to the live epoch.

Existing cooperative termination uses owner-death callbacks, unbind/self-kill,
and an absolute 30-second lease on the Java main looper. Binder death is explicitly
not independent kernel reaping evidence. The future 120-second boot proposal is
incompatible with that current lease; it needs a separately reviewed experiment
change, not a silent timeout increase in this PR. A compromised native worker can
ignore callbacks, block threads or retain duplicated FDs/mappings. The manager
cannot assume permission to kill a different isolated UID. A credible enforced
stop/death mechanism, surviving-child observation and owner-death revocation are
unresolved prerequisites. Closing manager copies or unbinding is not sufficient.

TCG single-vCPU mode does not mean a single host thread. Inventory main loop,
vCPU, GLib, timers and any worker pools; audit signal/stack sharing with ART and
all inherited framework/Binder/logging FDs. Deny fork/exec functionality in the
adapter, then test the authority of arbitrary native code independently. A worker
native compromise invalidates all self-reported containment claims and still
exposes allowed host syscalls/services. Only host enforcement and narrow manager
interfaces could bound that compromise; neither is proven by this source review.

## Next falsifiable experiment and validation

1. Prepare a separately inventoried Linux build environment with native Python,
   compiler, make, Ninja and pkg-config plus Linux-host NDK r28c. This requires
   no Android phone. Resolve the GLib/PCRE2/libffi/intl graph with reviewed hashes
   and isolated target pkg-config paths; disable uncontrolled wrap downloads.
2. Build the exact virt-only QEMU executable first. Freeze commands, generated
   config, patches and dependency link map. Inspect ELF, Bionic symbols, sizes,
   interpreter, executable stack, RELRO, page alignment and all DT_NEEDED entries.
   A full executable build is still not a JNI or Android-run result.
3. Review a minimal PIC/JNI and boot-FD adapter, coroutine/ART interaction and
   fail-closed memfd/split-W^X behavior before proposing harness changes. Resolve
   non-cooperative lifetime enforcement separately; do not relax containment.
4. Freeze/build the tiny Linux fixture and, if useful, perform an explicitly
   desktop-only smoke test using exact source-built artifacts. Keep all outputs
   out of Git. Android loading, TCG policy, containment and lifecycle stay Unknown.

Local validation passed: foundation (66 files, 39 Markdown files, 54 requirements,
2 ADRs, including local Markdown file links), all 17 repository regression tests,
harness authority validation and whitespace checks. Exact-base review contains
only the two new evidence documents and their index link, all mode 100644; no
binary or dependency change. Public-data review found no private paths or
credentials. These checks do not exercise QEMU or turn this evidence into a gate
result. CI remains unchanged; publication reports checks pending and performs
no subsequent polling.

[q-license]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/LICENSE
[q-security]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/docs/system/security.rst
[q-meson]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/meson.build
[q-coroutine]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/coroutine-sigaltstack.c
[q-region]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/tcg/region.c
[q-memfd]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/memfd.c
[q-cache]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/cacheflush.c
[q-virt]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/docs/system/arm/virt.rst
[q-boot]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/arm/boot.c
[q-loader]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/core/loader.c
[q-main]: https://gitlab.com/qemu-project/qemu/-/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/system/main.c
[glib-build]: https://gitlab.gnome.org/GNOME/glib/-/blob/e05063ccc6c8f222465a1080927f4c14349f3de6/meson.build
