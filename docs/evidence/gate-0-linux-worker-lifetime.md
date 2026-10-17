# Gate 0: bounded Linux worker lifetime implementation

Continuation: [case C's surviving-grandchild implementation](gate-0-surviving-grandchild.md)
records the independently verified PR #16 post-merge A/B/D receipts and extends
the fixture. The original publication observations and deferrals below are
historical; the new case's Linux execution remains pending/unobserved.

Review: **2026-10-16, America/Fortaleza**. Real Linux execution **NOT RUN locally**;
hosted results **pending/unobserved at publication**. This is executable research,
not a containment result. Gate 0 remains **Unresolved**, Gates A–G **Not reached**,
ADR-0001 Accepted, ADR-0002 Proposed. No production engine is selected.

Companion to [PR #15's containment audit](gate-0-worker-containment.md) and its
[unchanged immutable source ledger](gate-0-worker-containment-sources.md).
The original ten-case proposal remains historical unrun evidence. This change
implements only A, B and D from the continuation request, using actual Linux
fork, pipe, pidfd, signal, descriptor and wait operations. It does not substitute
mocked syscall outcomes for these operations.

## Verified preflight

Canonical main and the clean local checkout both resolved to
`5615927d675b3b4214e6165249373b8ee191a050`. Open PR inventory was empty.
[PR #15](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/15)
merged head `d1e5923aa7566d890655e6ad3be5bdd93ea3f63d` against base
`99b11b6c4aaff42a25f99b33e712dde52dfe2fdc`; its merge equals current main and
its source-head tree equals the merge tree. Its complete three-file, 480-line
addition was inspected. Reviews, comments, inline comments and review threads
were empty. No unresolved thread existed.

PR foundation check succeeded. Exact-main
[run 38953344382](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38953344382)
succeeded, including repository validation, the existing modeled native wait
controls, their assertion negative control and whitespace checking. These are
baseline observations, not new process-test results. Combined status had zero
contexts (its aggregate pending was not an additional check). All three registered
workflows were active; their definitions, pins, filters and permissions were read.
Main was not branch-protected; no repository setting was changed.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational, page updated `2026-10-16T15:14:19.772Z`.

One worktree, existing branches, no stashes, and ignored Gradle/native/build trees
were inventoried and preserved. Initial network and WSL inventory attempts were
sandbox-denied; authorized read-only retries succeeded. WSL listed no installed
distribution. No Linux runtime was installed and no Codex Cloud job was used.
Historical Privacy-Decoy remains read-only. Requirements, boundaries, gates,
roadmap, both ADRs, provenance, prior harness/integration evidence and native wait
sources were read. Existing native artifacts were not executed or newly attested.

## Implementation and safety argument

The original PDVA [C fixture](../../.github/scripts/worker-lifetime.c) is a
controller outside its tested child subtree. Every invocation creates exactly
one direct child, with no grandchild, thread creation or child exec. The independent
[Python runner](../../.github/scripts/worker-lifetime-research.py) builds that source
in a mode-0700 temporary directory and validates exact status/stdout/stderr. Each
invocation has a fresh mode-0700 subdirectory and only fixed synthetic data.

Before fork the controller closes all inherited FDs above stderr, resets SIGCHLD
to default, unblocks signals and disables core dumps. The child retains only its
command/read pipe, reply/write pipe, diagnostic stderr and (for D) one synthetic
file FD. It closes unused pipe ends and stdin/stdout. The controller obtains a
pidfd for its own unreaped direct child before sending GO; the single-threaded
controller has no other reaper. No child-supplied numeric PID is trusted. The
unreaped child cannot have its PID reused under these conditions, as documented
by [pidfd_open](https://man7.org/linux/man-pages/man2/pidfd_open.2.html).

All normal signaling uses that pidfd. Only pidfd setup failure permits a numeric
SIGKILL of this still-owned, unreaped direct child; setup failure never passes.
There are no process-group/cgroup kills, arbitrary process scans, network calls,
privileges, security-policy changes or access to unrelated files. The only data
file contains the four bytes `PDVA`, is created exclusively with mode 0600, then
reopened read-only and unlinked before fork. Child duplication preserves this
read-only access. No external source or binary is downloaded by the experiment.

The child arms a ten-second SIGALRM at entry after fork (fork does not inherit an
alarm), before resource setup or handshake waits. It does not exec/fork again or
cancel expiration. The controller separately arms twelve seconds; Python bounds
each invocation at fifteen seconds. Poll operations allow one second for protocol
I/O, three seconds for pidfd death; fallback wait has at most 300 ten-millisecond
pauses. EINTR fails instead of extending a deadline. The whole CI command has a
150-second timeout with a fifteen-second termination grace, within the existing
five-minute job. These are scheduling-dependent bounds, not real-time guarantees.

Both processes lower hard core/file-size/FD/address-space limits to 0/4096/32/64 MiB;
CPU limits are two seconds for the controller and one for the child. NPROC is
not changed because it is UID-wide; the fixed trusted source bounds child count.
The child alarm is a **TEST SAFETY BACKSTOP**, not proof against arbitrary native
code that can cancel it. Setup and handshakes are cooperative. Only B's refusal
of SIGTERM is non-cooperative; independent authorized SIGKILL and wait are the
enforcement under test. Same-UID Linux authority grants no Android cross-UID power.

On errors the controller attempts identity-safe SIGKILL and bounded reaping,
reports the failing stage and cleanup state, and fails. Python stops immediately
on any invalid result, compiler failure, missing support, crash, timeout or residue.
If the controller itself dies or times out, its result is rejected and cleanup is
**unproven**; child expiration is a safety backstop, never a substitute receipt.
No later adversarial case runs. Abrupt external runner/host loss cannot guarantee
reaping by the dead controller and is not reported as successful cleanup.

## Exact propositions and negative controls

| Case | Required real observation before acceptance | Deliberate false assertion |
|---|---|---|
| A: exit | Released child exits 42; exact owned wait, normal exit/42, second wait ECHILD | Treat this child as normal exit 0 |
| B: TERM refusal | Child acknowledges ignore setup; successful pidfd TERM; post-TERM challenge reply and non-readable live pidfd; pidfd KILL; exact SIGKILL reap | Treat successful TERM as confirmed death |
| D: retained FD | Child duplicates inherited read-only FD and closes its original; controller closes its own FD before GO; exact four-byte read through duplicate; child closes duplicate and exits 0 | Treat original-owner close as universal revocation |

Every case additionally requires no remaining waitable children (ECHILD) and reply
EOF with no extra bytes. This proves cleanup of the known fixed, non-forking
fixture, **not absence of arbitrary descendants**. C (surviving grandchild) is
deferred: orphan adoption and registration before parent exit need their own
reviewed protocol and failure-cleanup paths. This subset deliberately makes no
descendant-tree, parent-death, cgroup, mapping or stale-PID experiment claim.

Each case runs once positively and once with its named assertion mutation. The
mutation changes only the final assertion after all setup, exact real observations
and cleanup checks have succeeded. A rejected mutation must exit exactly 42,
produce the complete expected evidence line, and emit exactly
`REJECTED:<case>:cleanup-verified`. A crash, arbitrary nonzero, timeout, missing
output, unsupported kernel or unverified cleanup cannot satisfy this contract.
Positive exit must be exactly zero with empty stderr and the exact evidence line.

Separately, 87 modeled oracle controls reject wrong status, unrelated SIGABRT,
timeout, skip/missing status, missing/extra output, extra diagnostics, wrong wait
result, missing pidfd identity, missing EOF, missing cleanup/ECHILD and wrong or
missing mutation diagnostics. These checks exercise assertion logic without
abandoning real descendants. They are fixture evidence, not real process outcomes.

## CI, provenance and scope

Run `python3 .github/scripts/worker-lifetime-research.py` on Linux with the existing
host C compiler. Missing pidfd/close_range support fails explicitly; there is no
fallback pass or skip. `--check-oracle` runs only platform-neutral modeled checks.
The foundation workflow runs the full suite on **every PR**, including docs-only
changes, and main pushes. Exact-head checkout, read-only permissions, existing
immutable checkout pin and all previous checks remain. No artifacts are uploaded.
The Android workflow's existing `.github/**` filter also selects this change;
the unchanged QEMU cross-build filter does not select it.

Compilation uses standard C11, `-O0 -Wall -Wextra -Werror`, conventional compiler
linking/libc, a thirty-second deadline and no package installation. Logs identify
source SHA-256, compiler version, kernel release and architecture. Existing Ubuntu
runner compiler/libc/Python are infrastructure, not reproducibly pinned product
inputs. New C/Python is original PDVA work; no upstream/predecessor implementation,
new license, library dependency or security-critical prebuilt binary is adopted.
The owner maintains the research source; it is not a production supervisor.

The existing 185-component/322-artifact Gradle ledger and verification policy are
unchanged. Verification metadata SHA-256 still equals
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.
Retained NDK r28c package metadata matches its recorded hash. Previous immutable
Android/Linux source identities and license obligations are preserved. The Linux
[alarm documentation](https://man7.org/linux/man-pages/man2/alarm.2.html) and
[pidfd signaling documentation](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html)
were additionally read; no example code was imported. No engine, Android worker,
launcher, protocol, PR #12 FD reader, PR #13 planner, PR #14 witness or TCG control
is modified. There is no phone, ADB, guest image, QEMU/APK integration or guest run.

## Observed results and explicit unknowns

| Validation | Observation in this change |
|---|---|
| Platform-neutral result oracle | PASS: 87 invalid modeled observations rejected; six valid fixtures accepted |
| Repository regression suite | PASS: 138 tests, four existing Windows skips; 134 executed passes |
| Foundation and Android manifest/source-authority validators | PASS locally |
| Python AST syntax, whitespace, full intended diff and public text/binary inventory | PASS locally; seven intended text files only |
| Linux-only guard invoked on Windows | Expected rejection: exact exit 1 and failure diagnostic; no process experiment started |
| C syntax with existing NDK r28c, x86_64 Android 30 headers, warnings as errors | PASS, `-fsyntax-only`; no object/binary produced or executed; not Linux/glibc compilation evidence |
| Linux host compiler/linker and A/B/D process operations | NOT RUN locally: no installed WSL distribution; hosted pending/unobserved |
| Three real assertion-mutation invocations and cleanup receipts | NOT RUN locally; hosted pending/unobserved |
| Grandchild and other deferred scenarios | NOT IMPLEMENTED / NOT RUN |
| Fresh Android/QEMU builds or physical execution | NOT RUN; existing production/research implementations unchanged |
| Stock Android 17 isolated-process cleanup, production authority, hostile-VM containment | UNKNOWN; no claim established |

Linux kernel behavior will count as observed only when exact-source hosted output
and statuses are independently reviewed in a later authorized task. The modeled
oracle and old injected wait controls stay separate from real Linux operations,
Android 17 source findings and unknown physical stock-Android behavior. Process
death differs from descendant-tree absence; FD closure differs from capability
revocation. No result from this suite alone can pass Gate 0.

After publishing one focused PR, verify only its immediately available identity,
branch, head and base, report hosted CI pending/unobserved, and stop. No checks,
reviews, bots, comments, mergeability or status polling is authorized afterward.
