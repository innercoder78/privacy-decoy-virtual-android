# Gate 0: fixed surviving-grandchild experiment

Review: **2026-10-17, America/Fortaleza**. New Linux execution **NOT RUN locally**;
hosted results **pending/unobserved at publication**. This implements case C from
the [containment specification](gate-0-worker-containment.md), preserving PR #16's
three cases. Gate 0 remains **Unresolved**, A–G **Not reached**, ADR-0001 Accepted,
ADR-0002 Proposed. No production engine or Android supervisor is selected.

## Live preflight and baseline observations

Canonical main and the initially clean local checkout both resolved to
`60aa377edcabe0db576348cd3825aa10942cdb49`. The open PR inventory was empty.
[PR #16](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/16)
is merged, head `32549e79d2ff1d3c3b25908cdfc027d2ead22c32`, base
`5615927d675b3b4214e6165249373b8ee191a050`, merge equal to current main.
Its entire seven-file change was inspected; head and merge trees match.
Reviews, conversation comments, inline comments and review threads were empty.
Its foundation and Android checks succeeded. All three workflows were active;
their definitions, pins, permissions and path filters were inspected.

Exact-main [foundation run 38957154702](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38957154702)
actually executed the previous source, SHA-256
`73a1312809d8b48345fde0f5a85d07b070910c079e8738ea303137850f7d3f65`.
Host: Ubuntu 24.04.5, image `20261012.334.1`, Linux `6.17.0-1022-azure`, x86_64;
compiler `cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`.
The log contains all six exact evidence records, three positive status-0 receipts
and three status-42 mutation rejections:

| Baseline real case | Observed receipt in both positive and mutation runs |
|---|---|
| exit | `status=exit42 observed=0 identity=pidfd reaped=1 echild=1 eof=1` |
| term | `status=SIGKILL observed=1 identity=pidfd reaped=1 echild=1 eof=1` |
| fd | `status=exit0 observed=1 identity=pidfd reaped=1 echild=1 eof=1` |

Each mutation emitted `REJECTED:<case>:cleanup-verified`. The final receipt was
`PASS: Linux lifetime controls=3 mutations=3 all-owned-children-reaped`.
The separate 87 modeled oracle controls, 138 repository tests and native injected
wait controls also passed; these are not additional real process observations.
Exact-main [Android run 38957154720](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/38957154720)
succeeded through build, protocol, lint and APK inspection. No new Android runtime
result is inferred. These baseline results do not validate the new case C source.

[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational, page updated `2026-10-17T02:49:33.597Z`. Requirements,
boundaries, gates, roadmap, both ADRs, provenance policy, containment source ledger,
QEMU integration and isolated-worker evidence were read. One worktree, existing
branches, no stashes and ignored build/reference trees were inventoried and
preserved. Historical Privacy-Decoy was not changed. No WSL distribution or
Linux host compiler/runtime was found; no runtime was installed.

## Identity, creation and release protocol

The existing [C fixture](../../.github/scripts/worker-lifetime.c) adds a separate
`grandchild` branch. Its controller becomes and verifies a subreaper before
creating anything. It creates one immediate child with `clone3(CLONE_PIDFD)`:
failure creates no runnable child without the controller's atomic pidfd receipt.
There are no shared file tables, namespaces, threads, execs, session/group changes,
network calls or extra descendants. The direct child waits for controller `F`.

The direct child then creates exactly one grandchild with
`clone3(CLONE_PARENT_SETTID)`, pointing `parent_tid` at a preallocated anonymous
shared PID slot. Only the kernel writes this slot after its zero initialization.
The source never unmaps it in the descendants, overwrites it or reaps a grandchild
in the direct child. The kernel publishes the PID before waking the grandchild.
This also covers creator death between creation and a pipe registration message.
It is not authority derived from an arbitrary child-supplied numeric PID.

The controller reads the slot after the parent's `R` handshake, then obtains a
pidfd. The PID cannot be recycled: the parent never reaps it, SIGCHLD has default
disposition with no SA_NOCLDWAIT, and orphan adoption transfers wait ownership to
the already-established controller subreaper. There is no competing reaper.
The child's syscall return and the grandchild's own getpid must match the slot.
Those cooperative cross-checks supplement, rather than replace, the fixed-source
kernel-publication invariant. A malicious writer could falsify shared memory;
this protocol is expressly not a hostile-worker registration API.

The grandchild sends `R`, waits for `I` after controller pidfd acquisition, then
acknowledges `A`. The controller checks both live pidfds (zero-time poll plus
authorized signal zero) before releasing the parent with `E`. The parent exits
42. The controller observes pidfd termination, reaps that exact child, verifies
normal exit 42 and parent reply EOF. Only then does it send grandchild challenge
`C`. The grandchild verifies its new parent is the controller and answers `S`.
The controller checks the retained grandchild pidfd is still live after this
reply, sends SIGKILL through it, observes termination, reaps the exact adopted
grandchild with SIGKILL status, and observes its reply EOF. Separate repeat waits
return ECHILD, followed by ECHILD for all children of this fixed controller.

Parentage and wait ownership change on adoption. A numeric PID is not a durable
handle by itself; the unreaped-source invariant makes initial acquisition safe,
and retained pidfds provide stable signal/exit identities. Process-group identity,
session identity and cgroup membership are distinct and are not changed or used
as kill authority. ECHILD here concerns exactly the two source-bounded descendants,
not an enumeration or proof of absence of unknown hostile processes.

Semantics reviewed: [clone and clone3](https://man7.org/linux/man-pages/man2/clone.2.html),
[subreaper adoption](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html),
[pidfd acquisition](https://man7.org/linux/man-pages/man2/pidfd_open.2.html), and
[wait ownership](https://man7.org/linux/man-pages/man2/waitid.2.html).
The existing immutable Linux v6.12 [kernel/fork.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/fork.c)
was additionally retrieved and inspected for pidfd allocation/error handling and
`put_user(nr, args->parent_tid)` before `wake_up_new_task`. Its identity remains
the [existing source ledger](gate-0-worker-containment-sources.md) entry. Reference
review imports no upstream implementation and does not identify an Android kernel.

## Failure handling, limits and exact oracle

Controller limits remain CPU 2 s, address space 64 MiB, 32 FDs, file size 4096
bytes and no cores. Descendants inherit these hard ceilings and CPU is lowered
to 1 s before the second creation. The direct child re-arms its alarm to 10 s,
the grandchild re-arms to 8 s; controller alarm is 12 s and Python timeout 15 s.
Each protocol poll permits 1 s; each pidfd death poll permits 3 s and waitpid
fallback has at most 300 ten-millisecond sleeps. EINTR fails without retrying
the deadline. These are scheduling-dependent bounds, not real-time guarantees.
Unused inherited pipe ends and stdin/stdout are closed in each descendant.

On failure, controller cleanup attempts pidfd SIGKILL of any already-registered
grandchild, then of the only creator, and reaps the creator before inspecting
the final shared slot. It can then safely acquire
the known, unreaped/adopted grandchild's pidfd even if registration failed. It
attempts pidfd SIGKILL and exact reaping, retaining identities until cleanup.
There is no numeric-PID signal fallback in the new case C. If pidfd acquisition is unavailable,
closing the command pipe requests the fixed grandchild's failure exit; a bounded
wait must still actually observe reaping. This remains a failed experiment,
never a successful or skipped pidfd control. Missing reaps or residual children
produce `cleanup=UNPROVEN`. Python stops on either failure status (1 or 2).
An unexpected child failure diagnostic also invalidates the exact result.

Controller death or timeout provides no cleanup proof. Independent descendant
expiration is only a cooperative safety backstop; even its expiration cannot
substitute for observed reap receipts. The runner aborts on timeout/crash and
does not start subsequent cases. Abrupt host loss remains outside a guaranteed
cleanup contract. No process scan, arbitrary signal, group/cgroup kill, root,
elevation or host security-setting change is used. The new case rejects UID 0.

The independent [Python oracle](../../.github/scripts/worker-lifetime-research.py)
requires exactly this record, exit 0 and empty stderr for the positive case:

```text
EVIDENCE:grandchild status=exit42 registered=1 identity=pidfd parent-reaped=1 post-reap-challenge=1 alive=1 adopted=1 termination=SIGKILL grand-reaped=1 echild=1 parent-eof=1 grand-eof=1 cleanup=verified
```

Only after all real observations and eventual cleanup does the mutation evaluate
the false assertion, "Once the direct child is reaped, the complete process tree
is gone." Its required result is exit 42, the same complete stdout record and
exact stderr `REJECTED:grandchild:cleanup-verified`. It rejects the assertion
because survival was observed after the parent's reap, even though the grandchild
has subsequently been killed and reaped. Compile errors, unsupported syscalls,
timeouts, crashes, wrong statuses, missing/extra output and uncertain cleanup
cannot reach the accepted mutation result.

Modeled oracle tests remove and corrupt every new receipt individually, in both
positive and mutation modes, in addition to the existing invalid-result controls.
They test registration, identity, parent status/reap, post-reap challenge, live
state, adoption, termination, grandchild reap, both EOFs and cleanup. Their result
is **168 invalid modeled observations rejected; eight valid fixtures accepted**.
This count is not real Linux execution evidence.

## Validation, provenance and remaining scope

The existing five-minute foundation workflow already runs the complete Python
suite on every PR and main push, with its 150-second command deadline and 15-second
termination grace. No workflow changes, optional failures, support skips, package
installs or artifact uploads are introduced. Exact-commit checkout, read-only
permissions, pinned action, prior foundation/Android checks and all QEMU controls
remain. The runner logs kernel/architecture, source SHA-256, compiler version,
build flags and resulting binary SHA-256. New hosted observations are unobserved.
Eight successful controllers each finish before their 12-second expiration;
compiler/version deadlines remain 30/5 seconds. Any failed invocation aborts the
suite. This fits the existing command/job envelope without extending it.

All changes are original PDVA C/Python and research text. No dependency, binary,
license adoption, engine, guest or production behavior changes. Existing compiler,
libc and Python are CI infrastructure, not pinned product inputs. The 185-component,
322-artifact Gradle ledger is unchanged; verification metadata SHA-256 remains
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.
Retained NDK r28c metadata matches its recorded identity; retained build artifacts
are not executed or newly attested. No phone, Android device, ADB, Codex Cloud or
QEMU execution is used.

Local verification: modeled oracle passed; C11 syntax with existing NDK r28c
x86_64 Android-30 headers and `-Wall -Wextra -Werror -fsyntax-only` passed, producing
no object or executable. That is not Linux/glibc compilation or execution evidence.
Foundation and harness validators passed (92 files, 52 Markdown files, 54
requirements, two ADRs). Repository regression: 138 tests, OK with four existing
Windows skips (134 executed passes). Python AST syntax, complete intended diff,
text/provenance/public-data review, regular modes and whitespace passed. The
Windows Linux-only guard rejected execution; no real process scenario started.
Actual Linux creation, adoption, challenge, termination, reaping and mutation for
the new source are **NOT RUN locally; hosted pending/unobserved at publication**.

The sole intended proposition is that direct-parent reaping does not establish
an empty descendant tree. Fixed cooperative Linux fixture cleanup does not prove
ordinary Android app authority to kill an isolated worker's descendants, a cgroup
escape, defeat of Android system cleanup, capability revocation, malicious-native
containment or a Gate 0 pass. Android 17 source findings remain source findings;
stock Android runtime behavior and ordinary-app versus privileged authority remain
separate Unknowns. PDEATHSIG inheritance/cancellation, detached sessions, mappings,
stale identifiers, manager loss and forged reports remain unimplemented scenarios.

After publication, only immediate PR identity/head/base verification is authorized;
new CI remains pending/unobserved and no post-publication polling is performed.
