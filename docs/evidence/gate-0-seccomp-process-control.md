# Gate 0: additional seccomp process-creation research

Review: **2026-10-17, America/Fortaleza**. New Linux execution **NOT RUN locally**;
new hosted CI **pending/unobserved at publication**. Gate 0 remains **Unresolved**,
Gates A–G **Not reached**, ADR-0001 **Accepted**, ADR-0002 **Proposed**. No production
filter, engine, supervisor or VM architecture is selected. No Android worker,
QEMU, APK, guest, ADB or physical-device execution is part of this change.

**Source-supported answer:** an unprivileged Linux task can set `no_new_privs`
and install a kernel-enforced seccomp filter that its own unprivileged native
code cannot remove or weaken. A carefully limited legacy `clone` policy can
retain pthread creation while excluding a new process. That is a candidate
additional restriction, not a complete sandbox or Android authority result.
It depends on trusted installation, exact ABI coverage, successful synchronization
of existing threads, and separate accounting for preexisting descendants and
capabilities. A real Linux fixture is implemented below; compilation and its
modeled oracle do **not** establish its runtime propositions.

## Independently checked baseline

Canonical main resolved through `git ls-remote` and the branch API to the expected
`c2c3b19d0c75f508c52608bb2ed80a8bb974c69a`. Open PR inventory was empty, so there
were no open heads/bases/diffs to reconcile. [PR #17](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/17)
is merged: head `12509e04d330e426393cae33b64ffd4c35003b85`, base
`60aa377edcabe0db576348cd3825aa10942cdb49`, merge equal to main. Its entire
five-file diff was inspected; head and merge trees match. Reviews, conversation
comments, inline comments and review threads were empty (no next thread page).
Both head checks succeeded. All three workflows are active; definitions, pins,
permissions, exact checkout, path filters and required steps were inspected.
Main is not branch-protected; no repository security setting was changed.

Exact-main [foundation run 38999832358](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38999832358)
actually executed PR #17's source, SHA-256
`892165a858eddbad3643c4bbe2e7f75cbb79446d7c442e1124c3c87533df3a7f`;
its built binary hash was
`944431b963940a21ae38028026716bfd2c7784cc8555bc5d808ea76894a26ba2`.
Host: Ubuntu 24.04.5, image `20261012.334.1`, Linux `6.17.0-1022-azure`, x86_64,
`cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`. The log contains four exact positive
receipts with controller exit 0 and four real assertion-mutation rejections with
exit 42 and `REJECTED:<case>:cleanup-verified`. Case C recorded parent exit 42,
post-reap challenge, surviving/adopted grandchild, pidfd SIGKILL, exact grandchild
reap, both EOFs, ECHILD and verified cleanup. The final receipt was
`PASS: Linux lifetime controls=4 mutations=4 all-owned-children-reaped`.
These are **old lifetime controls, not new seccomp execution**. The same run passed
138 repository tests, 168 modeled oracle rejections and existing native wait tests.

Exact-main [Android run 38999832433](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38999832433)
succeeded through build/protocol/lint and APK inspection. No physical observation
is inferred. Combined commit status had zero contexts; aggregate pending was not
an additional check. [GitHub Status](https://www.githubstatus.com/api/v2/status.json)
reported All Systems Operational, page updated `2026-10-17T02:49:33.597Z`.

The starting checkout was clean on PR #17's head, with one registered worktree
and no stashes. Existing branches and ignored build/reference assets were
inventoried and preserved. The research branch starts at verified main. No
applicable AGENTS.md was found; historical Privacy-Decoy was not changed. All
requested containment, lifetime, grandchild, integration, startup-order,
requirements, boundary, gate, roadmap, provenance and ADR records were reviewed.
Sandbox-denied network and WSL inventory calls were followed by authorized
read-only retries. WSL listed no installed distribution; Docker and a Linux host
compiler/runtime were not available. No runtime or executable was downloaded.

## Linux policy and ABI limits

The [immutable source ledger](gate-0-worker-containment-sources.md) anchors Linux
v6.12 `kernel/seccomp.c`, `kernel/sys.c` and `kernel/fork.c`. This is a semantic
reference, not an Android kernel identity. `seccomp_prepare_filter` accepts the
NNP path without CAP_SYS_ADMIN. `seccomp_run_filters` evaluates the stacked filter
tree; an appended ALLOW does not erase an earlier denial. NNP cannot be cleared
with `PR_SET_NO_NEW_PRIVS`; there is no ordinary remove-filter operation.
`copy_seccomp` carries filters to new tasks. Allowed exec preserves restrictions.
The [kernel seccomp documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html)
also explains argument inspection and why syscall filtering alone is not a sandbox.

Installation with flags zero affects the calling thread. `SECCOMP_FILTER_FLAG_TSYNC`
synchronizes the calling process's thread group, including NNP where needed. It
does not filter already-existing child processes. Incompatible filter ancestry
can cause a **positive thread-ID return**, not just -1/errno; only zero is success.
The fixture deliberately tests both this failure and the omission of TSYNC.
Trusted setup must finish successfully before hostile code runs; TSYNC cannot
undo earlier process creation, disclosure or descriptor transfer. A compromised
installer could omit the call entirely. The experiment is not installer attestation.

| Syscall | Native Linux x86_64 number | Native AArch64 number / distinction |
|---|---|---|
| `fork` | 57 | No separate native syscall; libc uses clone-family operations |
| `vfork` | 58 | No separate native syscall; do not reuse the x86 number |
| `clone` | 56 | 220; flags are argument 0 on both, but TLS/child-TID positions differ |
| `clone3` | 435 | 435; argument 0 points to a structure |
| `execve` | 59 | 221; replaces an image, does not itself add a process |
| `execveat` | 322 | 281; must be considered separately from `execve` |
| `prctl` / `seccomp` | 157 / 317 | 167 / 277 |

The new C fixture supports **only native Linux x86_64 LP64**. It checks
`AUDIT_ARCH_X86_64`, kills on a different audit architecture, and denies numbers
at or above 512 with ENOSYS, including x32 and the historical x32 confusion range.
This is deliberately restrictive research, not a future-proof syscall policy.
It denies fork/vfork/execve/execveat with EPERM. Legacy clone requires
VM/FS/FILES/SIGHAND/THREAD/SYSVSEM, permits only the enumerated TLS/TID/DETACHED
additional bits, requires zero high argument bits, and rejects all other flags
and nonzero exit-signal bits. In particular, CLONE_VM alone is not a thread.

Classic BPF cannot dereference `clone3`'s argument structure. **Every clone3 is
denied with ENOSYS**. There is no allowed clone3 path. A libc may then attempt
legacy clone, which is still constrained by the filter. Pinned glibc 2.39's
`__clone_internal` makes precisely this ENOSYS fallback; EPERM does not select
that fallback. The fixture requires an actual post-filter pthread creation and
join before accepting it. This is pending runtime verification, not a claim
that every libc falls back. The pinned QEMU source independently uses this
ENOSYS approach for its optional spawn-denial policy; PDVA imports neither that
implementation nor libseccomp. Bionic's separately reviewed pthread path below
uses legacy clone directly.

The implemented runtime probes are intentionally narrower than the policy: fixed legacy
clone and clone3 process probes, pthreads, and invalid-path execve/execveat calls.
Standalone fork/vfork, alternate-ABI instructions, arbitrary flag combinations,
successful exec inheritance and namespace operations are **not executed**. Their
policy/source assessment is not labeled runtime coverage. There is no invalid
pointer substituted for a process-creation probe: both process probes supply
valid fixed fork-like arguments and pre-established kernel identity registration.

## Pinned QEMU and legitimate threading

QEMU revision `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`, tree
`0e6dfe70f3ae7b3ffc985c183e9df1b7ae3df4de`, matches the clean retained source
checkout and the existing cross-build recipe. Reviewed file bytes match immutable
Git blobs after removing local CRLF translation. This is not QEMU execution.

| Stage | Exact-source finding and consequence |
|---|---|
| Early initialization | `util/rcu.c`'s constructor calls `rcu_init_complete`, creating detached `call_rcu` before main. `util/thread-context.c` creates a context thread and can create requested threads. `system/vl.c` permits thread-context objects before its normal sandbox stage. Installing only on main is insufficient. |
| TCG setup | `tcg-accel-ops-rr.c` creates one joinable CPU thread even for round-robin/single-thread TCG. `tcg-accel-ops-mttcg.c` creates one per vCPU. A guest single-CPU choice does not eliminate host threading. |
| CPU execution | Those threads execute translated CPUs; CPU lifecycle/hotplug may invoke creation later. There is no demonstrated boundary after which every possible CPU thread already exists. |
| Event loop | `system/main.c` normally calls the default loop directly on this POSIX path, but has a conditional background-main-loop thread path. `iothread.c` creates joinable IOThreads. Futexes, signals and event I/O remain necessary; preventing process creation is not their validation. |
| Devices/backends | `util/thread-pool.c` can grow AIO worker threads from a bottom half or existing worker. Its separate GLib pool also creates threads through pinned GLib's pthread implementation. `io/task.c` creates detached task workers; `util/oslib-posix.c` can create page-preallocation workers. Backend/configuration choices determine the reachable set. A fixed early thread count is not established. |
| Shutdown/cleanup | `qemu_cleanup` shuts down migration/VM activity, drains/closes blocks and cleans up backends. IOThreads join; AIO pool cleanup cancels pending creation and waits for workers. Work already submitted must finish. No whole-backend closure proves shutdown can never need new threads. |
| Actual process conflicts | Optional `system/async-teardown.c` uses `clone(CLONE_VM)` **without CLONE_THREAD** and is invoked during option processing. The candidate rejects this process creation if already active; a later filter cannot retroactively constrain that helper. `net/tap.c` has fork/exec helper/script paths that conflict too. They are source possibilities, not approved PDVA features. |

`util/qemu-thread-posix.c` wraps `pthread_create` and handles joinable/detached
threads, signal masks, attributes and cleanup. A successful tiny pthread test
would establish only that host libc's tested operation, not QEMU/TCG compatibility,
ART/JNI compatibility, every backend or Android shutdown. Existing startup-order
evidence already shows side effects before a late guard. No QEMU boundary is
selected, patched or weakened here. Feature exclusions and complete initialization
closure would need separate review before any architecture proposal.

## Disposable experiment and independent supervision

One original [C source](../../.github/scripts/seccomp-process.c) and one independent
[Python validation runner](../../.github/scripts/seccomp-process-research.py) are
added. The C supervisor never installs NNP or seccomp. It reads its own state
before and after and requires it unchanged. Only disposable worker threads install
filters. The supervisor rejects UID 0 and nonempty effective/permitted/inheritable
capability sets. No namespace, privilege escalation, host security-setting or external networking
operation is used.

Before creating the worker, the supervisor closes inherited FDs above stderr,
sets default SIGCHLD/SIGALRM disposition, ignores SIGPIPE to handle pipe failure,
unblocks signals, verifies subreaper status and allocates a zeroed shared PID slot.
`clone3(CLONE_PIDFD)` atomically creates the sole worker and returns its pidfd;
failure aborts. The worker cannot proceed past GO until the supervisor owns this
identity. Successful unfiltered worker creation also proves clone3 exists in the
host environment; later ENOSYS cannot be accepted merely as missing host support.

Every potentially successful process probe uses CLONE_PARENT_SETTID with the
preallocated shared slot, SIGCHLD and a private address space. The kernel writes
the PID before waking the child. The worker never reaps or overwrites that identity.
An unexpectedly created child immediately exits 95, with a two-second alarm as
backstop. Its creator immediately exits the entire worker (42 only for the
intentional thread-only negative; otherwise 91). No second process attempt follows
a successful creation. Even creator death before a return/receipt leaves the
kernel-written slot available. After stopping/reaping the worker, the supervisor
owns the unreaped adopted child and acquires its pidfd without PID-reuse risk.
It never signals an arbitrary numeric PID or scans host processes.

This registry is valid for the fixed trusted source topology, **not hostile
worker reports or writable shared memory**. At most two descendant processes
exist. Within the worker there is one existing pthread; after its join, at most
one new pthread is created. On successful TSYNC the actual observations must
include equal process IDs, distinct thread IDs and exact denial from both the
existing and newly inherited thread. Threads are not counted as separate processes.
Release/acquire C11 atomics accompany the pipe handshakes so receipt access
between worker threads does not depend on compiler assumptions about pipe I/O.

| Case | Required exact result after real observations and cleanup |
|---|---|
| `tsync` | NNP set/readback 1; filter return **0** and mode 2; existing-thread clone EPERM; clone3 ENOSYS; execve/execveat EPERM; NNP-clear and mode-disable attempts EINVAL; clone remains denied after those attempts and after a successfully appended ALLOW filter; new pthread creates/joins and its clone is EPERM; retained pipe still reads exactly `PDVA`; five process probes, zero creations; worker exit 0, supervisor exit 0. |
| `thread-only` | Same filter installs successfully with flags zero on main only. Main's clone returns EPERM; then the existing peer actually creates the one registered child (two probes total). Worker exits 42; probe exits 95; supervisor independently reaps both and exits **42**, with exact `REJECTED:thread-only-is-all-threads:cleanup-verified`. Missing denial is deliberately observed, not guessed from the flag. |
| `invalid-install` | Invalid filter-install flags actually return -1/EINVAL. Worker terminates with exit **43**, zero process probes and no continuation release. Supervisor verifies cleanup and exits 0 for this terminal-failure control. |
| `divergent-tsync` | Existing peer first installs its own ALLOW filter. Main TSYNC must return exactly that peer's positive TID. Worker terminates with exit **43**, zero process probes and no release. Supervisor verifies cleanup and exits 0. Treating any nonnegative return as installed would fail the oracle. |

The runner requires exact status, stdout and stderr for each case; four valid
modeled fixtures are accepted and **143 deliberately invalid fixtures rejected**.
Fixtures corrupt/remove each field, mix cases and test unavailable/denied/created
confusion, attempted installation, thread/process confusion, missing installation,
terminal continuation, missing cleanup, signals, timeouts, wrong statuses and extra
output. These are modeled oracle checks, not 143 kernel observations. A crash,
timeout, compile error, unsupported syscall or generic nonzero never counts as a
successful negative control. Actual wait status and installation result/errno are
reported on an unexpected worker termination; only fixed diagnostic formats enter
public logs.

Hard ceilings: supervisor CPU 2 s; worker CPU 1 s; inherited address space 64 MiB,
32 FDs, file size 4096 bytes, zero core dumps. Pthread stacks are 256 KiB. Process
and thread count bounds follow fixed source, not a claimed hostile-code quota or
UID-wide NPROC change. Worker alarm is 8 s; supervisor observes its pidfd for at
most 5 s then performs identity-safe SIGKILL and bounded reaping on failure.
Each reap has at most 200 ten-millisecond sleeps; protocol waits allow 1 s.
Supervisor alarm is 12 s; Python per-case timeout is 15 s. EINTR fails rather
than extending a deadline. These are scheduling-dependent bounds, not real-time
guarantees. All tests use private mode-0700 temporary directories and no host data.

Failure cleanup first stops/reaps the only creator, then inspects the final
kernel registration slot, signals by pidfd where obtainable, and actually reaps
the adopted process. There is no numeric-signal fallback. Missing pidfd support
still fails even if the fixed child has exited and can be reaped. Residual waitable
children or missing reap yields `cleanup=UNPROVEN`. Python stops on either failure
status. Successful cases require ECHILD over this exact owned topology; that is
not a scan or absence proof for arbitrary hostile descendants.

Controller crash/death, outer timeout or abrupt host loss remains **unproven
cleanup**, never passing evidence. Child expiration is a fixed-fixture backstop,
not the enforcing authority being claimed. The unfiltered supervisor controls
ordinary failure cleanup independently of the candidate filter. No test asks
compromised code to certify its own safety. No new case runs after uncertainty.

## Android 17 source assessment and limits

The ledger retains the exact `android17-release` reference snapshots from the
prior containment review, not an OEM release manifest. Forty retained source
files were independently rehashed against it. The small additional Bionic files
are pinned to the same `06356e41c5ed7b12220b24c05ba4fdb873b126a7` commit.

**AOSP implementation:** Bionic policy inputs admit prctl, seccomp, clone,
clone3, execve and execveat for the relevant native ABI; the inspected app/common
blocklists do not remove these entries. The generator merges base minus blocklist
plus allowlist. `seccomp_policy.cpp` builds architecture-specific app filters and
installs through prctl; zygote selects the app filter while it still has system
authority. That privileged installation does not grant PDVA privileges. Linux's
separate NNP route is why another unprivileged filter is plausible. Actual kernel
support, generated/installed policy, filter ancestry and LSM constraints still matter.

**Bionic threading:** `pthread_create.cpp` supplies the normal VM/FS/FILES/SIGHAND/
THREAD/SYSVSEM/SETTLS/PARENT_SETTID/CHILD_CLEARTID flags. `clone.cpp` calls
`__bionic_clone`, and ARM64 `__bionic_clone.S` issues the legacy clone syscall.
Its TLS/child-TID order differs from x86_64. The candidate flag set admits these
source flags, but the fixture intentionally cannot compile as an ARM64 policy.
Neither NDK headers nor Linux/glibc behavior proves Android/Bionic execution.

**Public contract versus authority:** the official [isolated-service contract](https://developer.android.com/guide/topics/manifest/service-element#isolated)
describes isolated execution without the app's own permissions; it is not a public
TSYNC, descendant-revocation or QEMU-threading guarantee. SELinux domain rules
allow self fork in the reviewed source while isolated-app rules restrict path
opens and allow defined use of received descriptors. Syscall-number admission
and a source allow rule do not alone establish ordinary third-party app authority.

**Installed Android/OEM Unknowns:** release-equivalent stock physical evidence
would have to establish the actual kernel/configuration, native/compat ABI, app
UID/SELinux domain, existing filters and thread ancestry; successful NNP and TSYNC;
the exact shipped Bionic and enabled QEMU/backend paths; all-thread denial and
inheritance; lifecycle, background/thermal/resource behavior; and independently
observed cleanup after failures and manager loss. No such test was performed or
authorized here. No host support minimum or device qualification is inferred.

## What this candidate cannot enforce

- Code running before installation can create descendants or distribute capabilities.
  A later TSYNC cannot pull them back. PR #17's independently observed surviving
  grandchild remains a separate counterexample to direct-reap/tree-empty confusion.
- Permitted threads can execute malicious native code, consume resources, mutate
  shared memory and issue every other syscall allowed by the combined host policy.
  This filter neither identifies legitimate QEMU callers nor confines threads.
- Existing FDs, mappings, Binder objects, sockets and already disclosed bytes remain
  capabilities. Even this fixture requires a retained synthetic pipe read to
  succeed after filtering. Brokers or other processes can retain independent authority.
- Process-creation denial does not establish termination authority, a wall-clock
  lease, a total thread/memory/disk budget or manager-controlled revocation.
- An added filter supplements Android's system-owned cgroup cleanup. It does not
  replace that mechanism or supply a public PDVA tree-empty acknowledgement.

**Disposition:** this is a defensible candidate for further scoped research,
conditional on the exact-source hosted results and later Android qualification.
Do not adopt the filter, permit clone3 to rescue compatibility, select an engine,
integrate QEMU or claim a gate pass. A material architecture decision still needs
Tony's explicit approval and an ADR.

## Validation, provenance and publication boundary

Original PDVA C/Python only; no libseccomp or other new build/runtime dependency.
Upstream sources are read-only references, not copied/extracted implementations.
The source ledger records file-level reference identities/licensing limits.
The existing 185-component/322-artifact Gradle ledger is unchanged; metadata hash
remains `4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.
Retained binaries are not re-executed, redistributed or newly attested. Existing
NDK r28c compiler hash is
`7d31c6f6fad98987b6c9d21b800afaa8b3e37f052e94aaddc941d42ff2a35579`.

Local checks: C11 syntax using existing NDK x86_64 Android-30 headers with
`-O0 -Wall -Wextra -Werror -pthread -fsyntax-only`; modeled oracle; repository
regressions; foundation/harness validators; Python syntax and full diff/hygiene
review. Syntax produces no executable and is **not Linux/glibc build evidence**.
The Linux-only runner guard rejects Windows before compilation or experiments.
New Linux kernel outcomes, thread compatibility and failure cleanup are **NOT RUN
locally**; no new binary hash or runtime success is manufactured.

| Completed local validation | Observed result |
|---|---|
| Foundation and harness validators | PASS: 95 files, 53 Markdown files, 54 requirements, two ADRs; manifest/source authority checks pass |
| Existing repository regression | 138 tests, OK, four existing Windows skips (134 executed passes) |
| New independent oracle | Four valid modeled fixtures accepted; 143 invalid modeled fixtures rejected |
| Preserved lifetime oracle | 168 invalid modeled fixtures rejected |
| New C syntax / Python AST | PASS; syntax only, no new native executable |
| Windows runtime guard | Exact exit 1 and failure diagnostic; no Linux process experiment started |
| Whitespace, full diff, source identities, modes and public-data review | PASS; only seven intended text files, no dependency/binary adoption |

Final LF source SHA-256: C
`f4702f368a09989f5359b63852aabe22e7bf93afeda0649a53304a4871d169fc`;
Python runner
`9a07c19b93d09eff941d1274b39d2c78e8b1bf43d7374c848a1bcb27c9096d93`.
The eventual PR head identifies the entire source/workflow/evidence change;
the runner will hash the actual Linux compilation input independently.

The existing foundation job requires the full Linux runner after all unchanged
lifetime/native/repository controls, on every PR and main push. It has a bounded
100-second command plus 15-second termination grace within the existing five-minute
job. Compilation timeout is 30 s; compiler version timeout 5 s; four case timeouts
are 15 s each. Missing support fails, with no passing skip or optional failure.
Checkout remains exact, action pinned, permissions read-only and credentials
unpersisted. No packages are installed and no research binaries are uploaded.
“Required” here means necessary for workflow success, not newly configured branch
protection. The Android job's existing path filter also selects this change;
the QEMU cross-build recipe and selection remain unchanged.

The runner logs kernel release, architecture, libc version string, compiler version,
source SHA-256, build flags and resulting binary SHA-256. Runner compiler/libc are
execution infrastructure, not reproducibly pinned product inputs. The glibc source
reference in the ledger is not an attestation of a runner distribution's patched libc.

After publishing one focused PR, verify only its immediately available identity,
branch and exact head/base. New CI remains **pending/unobserved**. Do not poll,
wait for, rerun or query checks, reviews, comments, bots or mergeability afterward.
