# Gate 0: strict Android TCG executable-memory research

**2026-10-14, America/Fortaleza. Gate 0: Unresolved. Gates A–G: Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No engine or JNI/executable
integration architecture is selected. The isolated-worker launch contract is
unchanged. This is one non-physical source/build experiment, not guest integration.

The pinned QEMU source admits a narrow Android adaptation that requires explicit
split mappings and removes the two reviewed fallback paths. Local source,
preprocessor and compile-rejection evidence supports that statement. **Execution
of the extracted C fault controls on Linux and the modified full Android-targeted
QEMU cross-build are pending/unobserved at publication. Android runtime behavior
is Unknown.** There is no claim that these mappings work on a stock phone.

Scope: PDVA-REQ-002–003, 006–015, 036–045, 048, 051 and 054. This refines the TCG
finding in the [worker integration review](gate-0-qemu-worker-integration.md) and
uses the existing [Linux cross-build process](gate-0-qemu-android-linux-crossbuild.md).
The [security boundaries](../security-boundaries.md),
[provenance policy](../source-provenance-policy.md) and
[evidence criteria](../acceptance-evidence-criteria.md) continue to govern.

## Independent preflight

Canonical remote `innercoder78/privacy-decoy-virtual-android` resolved to
**`6bb491d3b8e40cf066bc1d71406f43fe8934a8d0`** independently through Git
`ls-remote` and GitHub's branch API; local HEAD matched. Repository metadata:
public, not a fork, not archived/disabled, default branch `main`. Open PR inventory
was **zero**: no open heads/bases/diffs/checks/reviews/comments/threads existed to
reconcile. One registered worktree, clean tracked state and no stashes were
observed. Existing branches, ignored build/reference trees and binaries were
inventoried and preserved. The historical Privacy-Decoy repository was untouched.
No applicable AGENTS.md was found in the workspace/parent inspection.

Exact-main [foundation run 38205888759](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38205888759)
and its validation/native positive/assertion-negative steps succeeded. It was the
only run/check returned for that main SHA; no new Android or QEMU success is
inferred from workflow filtering. All three workflows were active; their source
definitions, exact-head checkout, permissions, path filters and limits were read.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational, page update `2026-10-14T00:54:19.432Z`.

The prior successful [QEMU run 38095872712](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38095872712)
was rechecked at head `379822d7f1b56e8f6d0f06a2476d4f9387f80ae7`; its log contains
the cross-build completion marker. That is the **old unmodified allocator build**,
not evidence for this patch. Requirements, both ADRs, governance, boundary and
source/dependency records, earlier cross-build evidence and the
[unresolved native-host antivirus record](gate-0-native-host-antivirus.md) were
reviewed. No Windows PE is generated/run, no quarantine is restored and no
security setting is changed. This work supplies no antivirus clearance.

## Exact sources, transformations and provenance

The retained clean QEMU Git checkout resolves to
**`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`**, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`; GitHub's upstream commit API
independently returned that commit/tree. Reviewed working files matched the
immutable Git blobs after CRLF normalization. The build requires the unchanged
archive SHA-256 `a5a78e7d395ed096a7b2d98375978d0e2cf73f62c49a081ca48fa665d479b09f`
and exact **raw LF** file hashes below before transforming anything. It does not
normalize downloaded input, learn hashes from CI or accept an anchor alone.

| Pinned QEMU input | SHA-256 |
|---|---|
| [tcg/region.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/tcg/region.c) | `466f430bb52f1be9224d5339cc36ff6bae2769ca1f85e688ca2dfbacdf6cdc81` |
| [util/memfd.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/memfd.c) | `0e1e5d0f022727c39cebc651789601334e233b585fef490f84283fde72001c67` |
| [accel/tcg/tcg-all.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/accel/tcg/tcg-all.c) | `7ad8dcc2528e459abaf98787670d3674c570c689de6d9936fdaf761abcd43627` |
| [tcg/tcg.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/tcg/tcg.c) | `1dbcc86c7937f6b9251556cda93c53d112741d43da1e3c6f25ba8ba8f2540050` |
| [util/error.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/error.c) | `3aab61792ab9663febaa3020d25bb09c2ea02d662abd0155e9420d537ddd98b4` |
| [include/qapi/error.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/qapi/error.h) | `f2ef26ea43bb62243fb5217dded8fcae1ec56c8237aa97923d355307a7c0bcf3` |

Only `tcg/region.c` and `util/memfd.c` are transformed inside the ephemeral
cross-build source tree. Their resulting LF SHA-256s are respectively
`47e503c37f35ff0e5860289f08bbc7bdb8b4b2755a4db79cf1da2f2e673e5f15` and
`3a8c19c1aef80adb0cd8d14c8eb2d82752fbb1f0e4a345a8a0b49cd833748c02`.
The recipe logs before/after and unified-diff hashes, validates every input before
the first write, rejects repeat application, and rechecks patched bytes before
QEMU compilation. The retained upstream checkout is never patched.

Both modified upstream files carry permissive file-level notices; those notices
remain intact and accompany the extracted temporary control source. QEMU's
overall GPLv2 and existing dependency licensing/adoption obligations remain in
the [integration provenance review](gate-0-qemu-worker-integration.md). This is a
research-recipe adaptation, not runtime adoption or binary distribution approval.
No upstream engine source file or generated native executable is committed.

## Source guarantees and their boundary

1. Upstream `tcg_accel_instance_init` defaults split mode to off, or auto with
   debug TCG. The Boolean property setter supplies `1` for explicit
   `-accel tcg,split-wx=on`. `tcg_init_machine` forwards the value to `tcg_init`,
   then `tcg_region_init`. These callers remain unchanged and hash-verified.
2. The Android allocator rejects **every value except 1** before allocation.
   It returns the split allocator's result directly, with no auto-mode recovery.
   The Android preprocessor branch excludes the anonymous allocator and the
   downstream RWX protection call. It also checks RW protections and a nonzero
   split offset before region initialization continues; that check uses explicit
   exit, not an assertion that a release build could remove.
3. Android `qemu_memfd_alloc` performs one `qemu_memfd_create` call, preserving its
   error. Creation, resize or sealing failure returns failure without an unsealed
   retry, `g_get_tmp_dir`, `mkstemp`, pathname allocation or unlink. This applies
   to other Android callers of that helper too: they now receive failure rather
   than its previous best-effort fallback. The non-Android branch is retained.
4. The existing split allocator requests shared RW then shared RX aliases of the
   same descriptor, closes the descriptor on success, and releases RW/FD state
   on RX-map failure. `host_prot_read_exec` can add BTI, never write permission.
   TCG passes zero seals. The generic helper's sealing-failure control separately
   checks that the adaptation does not silently retry without requested seals.
5. `tcg_region_init` supplies `&error_fatal`; the pinned error implementation
   exits with status 1 on that error path. This is **source evidence**, not an
   observed QEMU process exit. Host controls model error objects and return paths;
   they do not execute QEMU's full startup, fatal-error machinery or region loop.
6. Compile guards admit only Android/Bionic AArch64 API 30 with Linux/POSIX/memfd
   configuration, excluding interpreter, user-only, static-buffer, Darwin and
   Windows alternatives. API 30 is a compile experiment, not a proven host minimum.

This allocation path uses a kernel memfd and mappings without requiring a temp
directory or unrestricted filesystem broker. **The rest of QEMU still has file
and syscall facilities**; removing this fallback does not confine arbitrary native
code, remove all `mkstemp` symbols from the binary or prove an entire engine can
run under the worker contract. Split aliases retain write access to executable
bytes through a different VMA; they are not a hostile-code isolation boundary.
The existing guard-page operation is best-effort and remains so; no new guard-page
enforcement claim is made.

## Controls, procedure and observed results

The [research recipe](../../.github/scripts/qemu-android-research.py) now performs
these controls after verified source acquisition and before dependency/NDK builds.
It extracts the actual patched `qemu_memfd_create`, `qemu_memfd_alloc`, split-memfd
allocator, split dispatcher and strict allocator. Linux `cc -std=gnu11 -O0 -Wall
-Wextra -Werror` uses ordinary host linking. All allocation syscalls are fakes;
no executable mapping, generated-code execution, real memfd or temp file is
required by the test. Android macros select the reviewed branches on the host.

The matrix is 4 modes (-1, 0, 1, invalid 2) × 5 outcomes (success, memfd failure,
resize failure, RW-map failure, RX-map failure) × 2 modeled byte sizes (4096,
16384), plus sealing failure. Checks cover exact syscall counts, permissions,
descriptor cleanup, RW cleanup, errors and absence of published region state on
failure. These byte sizes do not simulate or qualify actual device page sizes.

Two deliberately weakened extracted-source variants reintroduce a modeled
temporary-file fallback or RWX recovery. Each must produce **exit 91 and exactly
`FAIL: prohibited fallback`**. Compilation failure, timeout, signal, wrong
diagnostic or unexpected output cannot count as a successful negative control.
Positive execution must independently exit zero with the exact 40-case/seal
completion line. Every execution has a five-second timeout. Seven additional
compile controls must reject unavailable memfd/POSIX, wrong ABI/API, interpreter,
static buffer and user-only configurations with the intended guard diagnostic.

| Validation | Actual observation before publication |
|---|---|
| Source identity and rendering | All six real Git blobs verified; both transformations rendered; mutations of each input rejected. |
| Android branch preprocessing | Passed: includes removed only for branch inspection; no anonymous/RWX helper in region and no temp-path helpers in memfd. The same checker deliberately rejected both unmodified upstream files as negative controls. This is not full-TU compilation. The absence check is wired into Linux research CI. |
| Extracted C syntax | Positive, temp-fallback mutant and RWX mutant passed NDK Android AArch64/API-30 `-fsyntax-only`, with warnings treated as errors. None executed. |
| Deliberately failing compile controls | All seven failed with the expected strict-TCG diagnostic using the existing local NDK. |
| Repository regressions | 116 tests, OK: 112 executed passes, four pre-existing Windows skips. Eight new tests cover identity/admission, pre-write validation, nonregular inputs, forbidden-call detection and exact positive/negative result classification. |
| Linux extracted C execution | Pending/unobserved. No supported local native host compiler was found; no substitute Windows PE was built. |
| Modified full QEMU cross-build | Pending/unobserved. Existing Linux Actions recipe will attempt it; no target execution is configured. |
| Android/device runtime | Not run; all results Unknown. No phone, ADB, emulator, production APK or guest artifact used. |

Local environment: Windows x86_64, Python 3.12.14; retained NDK r28c
`28.2.13676358`, Clang 19.0.1 / Android build 13624864, upstream compiler revision
`97a699bf4812a18fb657c2779f5296a4ab2694d2`. Local compiler SHA-256:
`7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579`.
Syntax commands explicitly select `--target=aarch64-linux-android30`; no compiler,
dependency or host development runtime was installed. Local generated text remains
under ignored `android/build/tcg-fail-closed/` and is not published.

The existing archive/commit/tree/wheel/NDK pins, two earlier QEMU portability
patches, offline dependency configuration, ARM virt/TCG selection, output limits,
PIE/ELF acceptance and actual-link provenance checks are preserved. No workflow
authority, timeout, upload behavior or dependency changes. This script's path
already selects the Linux QEMU research job. Its native controls run before the
cross-build and any failure stops later stages.

## Remaining Unknowns and publication boundary

Stock-device memfd execution policy, SELinux/seccomp decisions, actual RX mapping,
BTI/CPU behavior, instruction-cache coherence, runtime page alignment, exhaustion,
signal/coroutine behavior and cleanup remain Unknown. Allocation success would
still not establish hostile-worker containment, external lifetime enforcement,
resource-FD integration or interactive Android feasibility. Device-policy failure
must not be rescued by temporary files, RWX, broader filesystem authority,
privilege, management-process execution or weaker platform policy.

Foundation/Markdown/provenance validation passed (79 files, 44 Markdown files,
54 requirements, two ADRs), as did harness source-authority validation, five
tracked Python syntax checks, exact-base text/mode inventory and whitespace.
Only the recipe, regression tests, this record and
its index entry belong to the PR. No launch-contract, requirement, ADR, runtime
dependency or historical-repository change is included.

Hosted CI is **pending/unobserved at publication**, including the actual Linux
fault-control outcomes and new cross-build. Publish one focused PR, verify only
its immediately available identity/branch/head/base, then STOP without waiting,
polling, rerunning or querying checks, bots, reviews, approvals or mergeability.
The PR's commit metadata identifies the submitted experiment. A later separately
authorized evidence review must classify the earliest real hosted result; this
record must not inherit success from the previous cross-build.
