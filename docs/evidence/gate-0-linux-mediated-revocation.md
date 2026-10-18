# Gate 0: disposable Linux mapping and mediated revocation controls

Review: **2026-10-18, America/Fortaleza**. Linux compilation, execution and real
negative controls are **pending/unobserved**. Windows validation below is not
Linux evidence. Gate 0 remains **Unresolved**; Gates A–G **Not reached**;
ADR-0001 **Accepted**; ADR-0002 **Proposed**. No production broker is authorized.

This implements the unrun falsifiers from [PR #21's capability inventory](gate-0-capability-revocation.md).
Its [source ledger](gate-0-capability-revocation-sources.md) remains reference
evidence, not runtime receipts. A retained mapping is a different witness from
PR #16's duplicated-FD test. Future mediated access, admitted but uncommitted
operations, completed effects, and previously disclosed bytes are separate claims.

## Independently verified baseline and publication exception

Live main matched `7e68da5d4fe489828bbadc7615265652bc8d38de`. Open PR inventory
was empty, including the immediate pre-implementation recheck. [PR #21](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/21)
merged head `bfec49a98b1c75e04358457c40eded356ed2dde8` against base
`49be371f20107f9f2fb098270d68f092f4afb88e`; its merge equals verified main.
Head and merge trees both equal `b810d5f3c9680e70075c504d449d8dbd4c0b2473`.
The complete three-file diff, reviews, conversation comments, inline comments
and review threads were inspected; all comment/review inventories were empty,
with no next thread page. There were no open PR diffs or unresolved threads.

The exact-head [foundation run 39101437431](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39101437431),
job `117598348539`, and exact-merge [foundation run 39102209895](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39102209895),
job `117600614091`, succeeded. Logs identify the exact checkouts and contain
138 passing repository tests, seven native wait positives, the injected SIGABRT
negative, four lifetime positives/four mutation rejections, and four seccomp
cases with cleanup receipts. The merge runner reported Linux `6.17.0-1022-azure`,
x86_64, glibc 2.39, Ubuntu GCC 13.3.0. These are **prior controls**, not execution
of this new fixture. All three workflows were active; definitions, pins, filters
and read-only permissions were inspected. GitHub Status reported operational
components and no incidents. No repository protection setting was changed.

The clean prior branch, existing branches, one worktree, empty stash inventory
and ignored build/reference assets were preserved. The new branch starts at
verified main. Historical Privacy-Decoy remains read-only. Requirements,
boundaries, gates, both ADRs, provenance/dependency records, capability,
lifetime, containment, seccomp and exceptional Android lifecycle evidence
informed the implementation. No Android application or approved requirement changes.

The local host is Windows, with no installed WSL distribution and no Docker on
PATH. The owner explicitly prohibited installing tools and authorized publishing
this executable research with Linux **pending/unobserved**, superseding the
initial requirement for pre-publication Linux receipts. The exact-head Ubuntu
results must be independently reviewed after publication and before merge.
After one immediate PR identity/native attachment check, stop without CI polling.

## Implementation, observation and trust boundary

The original [C fixture](../../.github/scripts/revocation-control.c) has four
fixed roles. The [Python runner/oracle](../../.github/scripts/revocation-research.py)
launches each as its own direct child; no C role forks, execs another image or
creates threads. Each invocation uses a fresh anonymous 4096-byte memfd containing
synthetic byte 80 and operation counter zero. No pathname or host data is exposed.

In the mapping case, the writer and read-only observer independently map the
memfd and close their FDs. Before releasing the writer, Python verifies absence
of the backing device/inode in each child's bounded descriptor range 0–63 and
closes the original creator FD. Children remain alive and unreaped, with pidfds
checked before and after inspection. This is inspection of owned registered
processes, not PID discovery or unrelated-process scanning. Writer stores 90;
observer reads its own mapping. Mutation 1 uses MAP_PRIVATE, so a claimed write
without shared visibility cannot pass. No duplicated FD substitutes for a map.

In mediated cases, a trusted test owner retains the backing FD and writable
mapping. The worker receives only one endpoint of a private AF_UNIX
SOCK_SEQPACKET pair; it receives no backing FD or mapping. Python's close_fds,
explicit pass_fds and exec establish that fixed inheritance topology. The
observer has a read-only mapping and closes its mapping FD; Python again closes
the creator FD and independently checks worker/observer descriptor absence.

The only protected operation is a fixed fetch-and-increment of byte zero; its
returned old value is deliberate disclosure. The owner also increments byte one
as an operation counter. A separate observer reads both actual backing bytes
after deterministic pipe/socket barriers. Thus denial needs both an exact reply
and unchanged resource effects, not merely a controller-reported counter.
Instrumentation and the small reviewed operation body are trusted: this does not
prove absence of arbitrary uninstrumented reads, syscalls or a lying controller.

The supervisor is trusted; the owner is trusted except for each named check
mutation; the observer is trusted; the worker executes fixed reviewed scripts.
Instance 7, epoch 11 and the private endpoint are enrolled by test construction,
not authenticated from a worker assertion. Requests use a fixed 16-byte native
packet. Sequence state belongs to the owner. The worker cannot forge these
assumptions in this experiment because arbitrary code is never executed.
The same-UID processes are **not** independently secured from hostile native
peers: procfs, ptrace/process-memory authority, inherited ambient authority and
host policy could invalidate separation. This is not a secure Android broker.

## Required observations and independent semantic mutations

Every row below is a **required future runtime receipt**, not a recorded result.
All positive and mutant processes must exit exactly zero, have verified owned
reaping/ECHILD, exact protocol completion, stdout/stderr EOF and no residue.
Crashes, generic nonzero exits, skipped cases and timeouts cannot reject a mutant
successfully. Python first requires the exact changed effects and then requires
the independent positive oracle to reject those effects.

| Scenario | Required positive observations | Real implementation mutation / falsifier |
|---|---|---|
| A: mapping | Both mapping FDs and original creator FD closed; observer 80 → 90 after writer's store | MAP_PRIVATE writer reports store but observer stays 80 |
| B: mediated | First result OK/80; backing 81/count 1; owner REVOKED; next result exactly DENIED_REVOKED; backing unchanged | Omit revoked admission/commit checks; second result OK/81, backing 82/count 2 |
| C: disclosure | OK/80 retained in worker; new request DENIED_REVOKED; worker still returns COPY 1 80; backing 81/count 1 | Erase the worker's retained copy on denial; COPY 0 0 rejected |
| D: in-flight | Owner AUTHORIZED_PENDING; backing 80/count 0; revoke returns REVOCATION_PENDING; explicit commit attempt ABORTED/DENIED_REVOKED; backing unchanged | Skip commit-time check; COMMITTED/OK and backing 81/count 1 rejected |
| E: stale epoch | Epoch 10 gives DENIED_EPOCH; backing 80/count 0 | Skip epoch check; OK and backing 81/count 1 rejected |
| E: wrong instance | Instance 8 gives DENIED_INSTANCE; backing 80/count 0 | Skip instance check; OK and backing 81/count 1 rejected |
| E: replay | Sequence 1 succeeds once; replay gives DENIED_REPLAY; backing stays 81/count 1 | Skip sequence check; second operation changes backing to 82/count 2 |
| E: missing state | Owner explicitly removes authorization state; DENIED_STATE; backing 80/count 0 | Skip missing-state checks; OK and backing 81/count 1 rejected |
| E: lost controller transport | Owner deliberately closes endpoint, exits normally and is reaped; worker UNKNOWN_TRANSPORT, then LOCKED_UNKNOWN; backing 80/count 0 | Skip worker uncertainty lockout; another transport attempt instead of LOCKED_UNKNOWN is rejected |
| E: uncertain outcome | Pause authorized request; owner commits but deliberately drops reply and exits normally; worker UNKNOWN_TRANSPORT then LOCKED_UNKNOWN; observer sees 81/count 1 | Same lockout bypass attempts another request; rejected despite no surviving owner |

In-flight ordering uses an explicit H → AUTHORIZED_PENDING → V →
REVOCATION_PENDING → C protocol, with an observer read before revocation.
There is no sleep/race window deciding whether revoke precedes commit. Pending
is not successful completed revocation; only the subsequent abort plus unchanged
backing state resolves this operation. The incorrect commit mutant is compiled
from the same source with a single semantic change, not a mutated final assertion.

Loss is deliberately an orderly endpoint-loss injection, **not an accepted crash**.
It explores a worker's uncertainty, not actual asynchronous manager death or
restart recovery. UNKNOWN_TRANSPORT is never converted into DENIED_REVOKED,
permission to retry, or permission to reuse the old resource. A fixed-worker
lockout is cooperative behavior, not enforcement against compromise. The observer
knows the committed effect in the uncertain case; the worker still cannot infer
its outcome. Missing-state and transport-loss properties beyond this construction
remain **Unknown**. No durable restart implementation or recovery claim is made.

Each scenario gets new resources. Expected injected loss is resolved at the
supervision level by exact normal exits, reaping and destruction of all fixture
references. Unexpected observation or cleanup uncertainty stops the entire suite;
it never authorizes the next experiment. Resource reuse is not tested or permitted.

## Supervision, ceilings and cleanup

Python registers every spawned fixture immediately, opens a pidfd while it owns
the unreaped child, then releases a startup barrier. SIGCHLD is default and no
other reaper exists. Every normal completion requires pidfd exit readiness,
wait returning zero, an additional exact-owned wait reporting ECHILD, DONE and
both output EOFs. On errors it sends SIGKILL using the pidfd and waits explicitly.
Only failure to acquire a pidfd permits killing that still-owned unreaped direct
child through its Popen handle; setup still fails. There are no numeric-PID scans,
process-group kills, unrelated signals, namespaces or privilege operations.

| Scope | Hard bounds and rationale |
|---|---|
| Each C process | CPU 2 s, AS 64 MiB, FD 64, file size 4096 bytes, core 0, NPROC 0; sufficient for libc, one page, bounded pipes/socket, no further processes/threads needed |
| Python/compiler infrastructure | CPU 10 s per process, AS 256 MiB, FD 64, file size 16 MiB, core 0; enough for this small C compile and standard-library observer; not a product resource budget |
| Process/thread topology | At most three direct fixture children plus Python; all single-threaded; compiler builds run separately and sequentially using existing trusted toolchain helpers |
| Protocol | At most 12 commands in worker/map roles, 16 in owner; one-byte supervisor commands, 16-byte socket packets, receipt line below 100 bytes; one admitted operation at a time |
| Deadlines | 2 s per receipt/pidfd wait, 1 s normal wait, 2 s failure reap per child; C alarm 8 s; compile 30 s; compiler identity 5 s; runner alarm 120 s; CI timeout 140 s plus 15 s termination grace |

UID zero and nonzero inherited/permitted/effective/ambient capability sets fail
before compilation. NPROC is real-UID scoped but the lowered limit applies to
the disposable process's creation attempts; no host-wide configuration is changed.
Source topology is also bounded. These are test-safety limits, not containment
evidence. The outer foundation job retains its existing five-minute deadline;
an aggregate timeout is failure, never permission to omit a scenario.

Caught errors and supervisor TERM/INT/ALRM attempt independent cleanup in finally
blocks. Temporary build directories are mode 0700; memfds have no filesystem
path; scenario directories must remain empty. Binaries and directories are
removed on normal and handled error paths. Cleanup failure stops the run. Abrupt
supervisor SIGKILL, host failure or toolchain-helper failure cannot certify cleanup;
child alarms are only backstops. No complete arbitrary process-tree claim follows.

## Provenance, validation and exact-source CI

New C/Python are original PDVA work, with no upstream implementation, downloaded
executable, new library or copied historical code. Existing libc/Python/compiler
are infrastructure, not adopted Android product components. The immutable
references in PR #21 remain unchanged. Linux manual pages for
[mmap](https://man7.org/linux/man-pages/man2/mmap.2.html),
[pidfd_open](https://man7.org/linux/man-pages/man2/pidfd_open.2.html) and
[rlimits](https://man7.org/linux/man-pages/man2/getrlimit.2.html) were consulted
as mutable documentation; no sample code was imported. Owner maintains this
disposable research. No repository-wide redistribution license is inferred.

Reproduce the complete experiment on unprivileged native Linux x86_64:

```sh
git rev-parse HEAD
python3 .github/scripts/revocation-research.py
```

The runner logs C and runner SHA-256, kernel, ABI, libc/Python/compiler identity,
flags `-std=c11 -O0 -Wall -Wextra -Werror`, mutation number and every resulting
binary SHA-256. It builds positive mutation 0 and mutations 1–9, then runs ten
positive scenarios and ten semantic negative invocations separately. Mutation 9
is used in both loss cases. Exact JSON observations and cleanup accompany each
accepted result. A missing primitive, build failure or unexpected result fails
without a passing skip. No research binary is uploaded or committed.

The foundation workflow adds a mandatory full runner invocation after all
unchanged existing checks, using its existing exact-head checkout, immutable
checkout pin, read-only permissions and time bound. The narrow source admission
list adds only the two new exact paths. No CI is weakened, skipped or replaced.
Existing Android path filters also select .github changes; no Android build or
runtime result is claimed locally. QEMU workflow/filter remains unchanged.
Mandatory means required for workflow success, not new branch protection.

Local validation uses installed NDK r28c Python 3.11.4 and Clang 19.0.1 on
Windows. All ten C variants pass `--target=x86_64-linux-android30 -std=c11 -O0
-Wall -Wextra -Werror -DMUTATION=N -fsyntax-only`. This emits no binary and is
**not native Linux/glibc compilation or Android execution**. The Windows full-run
guard exits exactly 1 before compiler/experiment launch. Modeled oracle checks,
Python syntax, foundation/harness validators and repository regressions are
recorded separately from Linux results. Existing regressions: 138 tests,
134 executed passes and four existing Windows skips; skips are not passes.

Final local receipts: foundation validation passed (102 files, 58 Markdown
files, 54 requirements, two ADRs); harness validation passed; Python AST passed;
802 invalid modeled revocation receipts rejected, with twenty valid modeled
positive/mutant receipts accepted. Preserved lifetime/seccomp modeled oracles
rejected 168/143 invalid receipts. All ten C syntax variants passed. Full intended
diff, UTF-8 text, regular 100644 modes, local Markdown targets, whitespace and
public-data hygiene were reviewed. These checks do not establish Linux outcomes.

| Final LF source / retained metadata | SHA-256 |
|---|---|
| revocation-control.c | `3a00fc4d055bb93b210ffacc88edd4e93ddf38124bc186ec2fa354a25defea89` |
| revocation-research.py | `55ead027c7405d15ff2feca80b71b96b8f0b3a2562d1195368b506d61ac3b942` |
| Unchanged Gradle verification metadata | `4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a` |
| Existing NDK r28c source.properties | `c00aa236fdb205e9be9edd9e2169763e48aca52735efff4e16f34205d49783b5` |

The PR commit identifies the complete source/workflow/evidence tree. New native
Linux compiler identity, binary hashes, positive/negative runtime receipts and
cleanup observations remain **pending/unobserved** until exact-head CI review.

## Requirement implications and exclusions

This adds falsifiable research for PDVA-REQ-010–014 (authority, control-plane,
interfaces, disclosure), 036–037 (provenance), 039–043 (evidence and negative
tests), 048–051 (hygiene/CI) and 054 (Gate 0 discipline). It satisfies no Android
security requirement by itself and modifies no requirement or architecture.

It does **not** prove hostile-worker containment, ordinary-app Android 17
authority, Android SELinux/Binder behavior, general syscall protection, complete
process-tree termination, revocation of raw FDs/mappings/copied bytes,
manager-restart recovery, a production-ready broker, or Gate 0 Passed.
Actual Android instance enrollment, inherited/deputy authority, stock OEM policy,
cross-UID resource protection, lifecycle/death ordering and durable uncertainty
remain Unknown. compileSdk/targetSdk 37 and research minSdk 30 are unchanged;
supported host minimum remains Unknown. No phone, ADB, Android execution, guest,
QEMU integration, VPN changes or Codex Cloud are part of this work.
