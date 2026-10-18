# Gate 0: retained authority and independent revocation

Review: **2026-10-18, America/Fortaleza. Source research only; no new Linux or
Android experiment.** Gate 0 remains **Unresolved**, Gates A–G **Not reached**,
ADR-0001 **Accepted**, ADR-0002 **Proposed**. No engine or broker is adopted.

**Finding / inference:** revocation must be specified per resource and operation.
A trusted endpoint can reject future mediated operations without trusting the
worker. Closing management's raw file or shared-memory handle cannot revoke
the worker's references. Killing the original worker cannot recall transferred
references or copied information. Never delegate authority whose continued use
cannot be tolerated and whose complete reference lifetime cannot be established.
This sharpens a possible ownership design, but leaves the hostile-worker lifetime
blocker intact. It is not permission to integrate a guest or implement a broker.

This extends the [candidate hypothesis](gate-0-userspace-vmm-candidate.md),
[containment audit](gate-0-worker-containment.md) and
[exceptional lifecycle review](gate-0-android-lifecycle-exceptions.md).
**Fact** means identified source behavior; **Observation** means an actual review
or validation result; **Inference** is its reasoned implication; **Hypothesis** is
an unimplemented proposal; **Unknown** is missing evidence. No source fact below
is an observed stock-device outcome. Assume arbitrary worker-native execution,
direct syscalls, threads and any subprocesses/transfers that host policy permits.

## Live preflight and scope

**Observation:** canonical main matched
`49be371f20107f9f2fb098270d68f092f4afb88e`. There were **zero open PRs**, hence no
open diffs, jobs, reviews, comments or unresolved threads to reconcile.
[PR #20](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/20)
merged head `9cf93a3e5b7f1abfc03d63031d96b9d1bb404e88` against
`edc1d4ead49b8f5ac9696e91ceb070925e01e854`; its merge is current main and the
head/merge trees match. Its foundation check succeeded; reviews and conversation
comments returned empty. The three-file documentation change and source ledger
were inspected.

Exact-main [foundation run 39100531326](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39100531326),
job `117595699396`, succeeded at that exact SHA. Its log contains seven native
wait controls and the exact injected SIGABRT rejection, 168 modeled lifetime
oracle rejections, four real Linux lifetime cases plus four exact-status-42
mutations, and four real seccomp cases with all owned children reaped. The
grandchild receipt includes post-parent-reap challenge, live pidfd, adoption and
SIGKILL reap. Seccomp receipts include the live peer-creation negative control
and terminal invalid/divergent-installation cases. These are **existing Linux
receipts**, not new revocation or Android evidence. Runner kernel was
`6.17.0-1022-azure`, x86_64; compiler Ubuntu GCC 13.3.0.

All three workflows were active. Definitions retain immutable checkout
`3d3c42e5aac5ba805825da76410c181273ba90b1`, exact source checkout, read-only
permissions, bounded jobs and existing positive/negative controls. Only foundation
is selected by this documentation change; no missing Android or QEMU run is a
pass. GitHub Status reported All Systems Operational, no incidents, page updated
`2026-10-18T04:44:16.876Z`.

The clean prior branch, all other branches, one worktree, empty stash inventory
and ignored build/reference assets were preserved. This branch starts at verified
main. Historical Privacy-Decoy is untouched. Requirements, security boundaries,
threat model, gates, roadmap, both ADRs, provenance, harness/launcher/protocol,
Linux lifetime, Android lifetime/exception and QEMU integration records informed
the review. Tracked baseline files have mode 100644. Existing tool/native license
and dependency inventories remain in the [adoption record](gate-0-isolated-worker-adoption.md).
Gradle verification metadata still hashes to
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.
Existing Android/QEMU and native-control binaries were neither executed nor
newly attested; local validation uses the already installed Python interpreter.

## Existing harness inventory: A–D (creation, delegation, enforcement, compromise)

Repository facts refer to the main SHA above:
[Session](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java),
[WorkerService](../../android/gate0-harness/src/main/java/org/pdva/gate0/WorkerService.java),
[Protocol](../../android/gate0-harness/src/main/java/org/pdva/gate0/Protocol.java),
[native probes](../../android/gate0-harness/src/main/cpp/probe.c) and
[launcher](../../android/gate0-harness/src/main/cpp/launch.c).
The table gives implementation facts followed by compromise implications.

| Capability | A: creator/owner; B: duplication, mapping, transfer | C: enforcing authority; D: consequence of native compromise |
|---|---|---|
| Canary PFD | Manager creates 4096 synthetic C bytes, opens O_RDONLY and parcels it with flags 0. Worker gets its own FD; native probe already duplicates it. Holders can copy bytes and attempt further mapping/IPC transfer. | Kernel open-file access mode limits writes through that description; DAC/SELinux/seccomp govern other paths. **Read-only is not immutable:** manager retains pathname authority. Worker-side FD validation is not post-compromise enforcement. |
| Scratch PFD | Manager creates a zero-filled 4096-byte file and sends O_RDWR. Worker receives whole-file authority, not a byte-range capability. | Kernel/LSM govern actual operations. Native code can attempt arbitrary offsets, growth, truncation and writable mapping; initial fstat and manager's later byte check do not impose a quota or prevent mutation. |
| Shared frame | Manager creates 16384-byte SharedMemory, maps RO, sends the object; worker maps RW. No setProtect call. Native compromise can retain aliases/FDs and transfer if policy permits. | Kernel VMA protections/backing object enforce actual access. Manager RO mapping does not make backing memory RO. Two FRAME calls and shape checks constrain cooperative Java only; hostile writes can race manager reads at any time. |
| Sentinel / management allocation | Manager owns random synthetic sentinel FD and memory allocation. INIT sends only sentinel FD **number**, memory address and owner Binder; manager PID comes from Binder at worker entry. No sentinel FD or contents are parceled. | A number/address is not a transferred reference. Cross-UID path/proc/ptrace/process_vm access needs separate kernel authority. Probe results are physically Unknown; successful access would be a blocker. Synthetic identifiers are disclosed information. |
| Owner Binder | Manager creates plain Binder with no application operations; worker holds it and registers a death recipient. | Binder reference/transaction transport plus endpoint behavior. No file-open, policy, Persona or signing operation is provided. Base Binder machinery is still attack surface. Owner-death self-kill runs inside compromised worker and can be suppressed. |
| Worker endpoint and control | Worker implements INIT/RUN/FRAME/INPUT/STOP/KILL/LAUNCH. Manager holds endpoint and death subscription. UID checks, epoch, fixed operations, size/order/quota checks live in worker. | Binder supplies caller credentials; **worker code** applies these checks. Compromise can bypass checks, ignore STOP, lie in reports or suppress callbacks. This is not an independently mediated worker-to-manager resource API. |
| Runtime/inherited descriptors and mappings | Zygote/framework/runtime establish worker state; JNI creates temporary maps/memfd probes. Self-FD/map counts exist, not an exhaustive object/recipient inventory. | Kernel credentials, object types, SELinux and installed seccomp. Binder/logging/runtime handles cannot be assumed absent. All usable references in compromised address space are in scope, even if absent from INIT. Exact deployed inventory Unknown. |
| Native launcher pipes/child | Worker opens fixed installed executable for checks, closes it; creates pipes and /dev/null; fork inherits address space and FDs before child setup. Child remaps 0–3, closes 4–65535, then execs fixed payload. FD 3 is CLOEXEC. | This source bounds the **cooperative fixed launcher**, not arbitrary worker code. Compromised worker can bypass it and invoke allowed syscalls. Successful exec replaces mappings, but an allowed hostile fork need not exec. Child setup is not a separate trust boundary. |
| Framework/service endpoints | Worker queries camera/audio/location/storage wrappers without capture. Policy admits selected service-manager lookups; framework startup provides other IPC state. | Lookup, Binder transfer and each service's operation authorization are separate checks. Wrapper presence is not data access; lookup denial is not proof that supplied Binder references cannot work. No complete reachable-service/deputy audit exists. |
| Network/socket | Manager passes no network socket; manifest grants no permissions. Native probes attempt TCP/UDP creation and loopback connect, without application data. Runtime Unix/logging sockets are separate. | Pinned isolated policy prohibits listed non-Unix socket creation but allows defined use of received TCP/UDP sockets. No INTERNET declaration is not a universal no-network theorem. Direct, inherited or deputy paths remain physically Unknown. |
| Host secrets/peer resources | No Persona master data, credentials, signing keys, host camera/mic stream, directory FD, peer disk, arbitrary open/syscall/Binder proxy or VM resource is deliberately delegated. | Preserve absence plus independently enforced path/service denial. Ordinary host metadata visible through allowed native/runtime interfaces is not necessarily secret or revocable. A future proposal must not inherit an assumption of complete denial. |

## E–J: residual use, death, restart, recipients, denial and certificates

This table is an **inference from source semantics**, not a runtime receipt.
“Other holder” includes a permitted descendant, IPC recipient and in-flight
transfer; transfer reachability must be proved for the actual Android build.

| Capability | E: manager close; F: worker versus descendant death; G: manager death/restart | H: external retention; I: independent future denial; J: possible certificate |
|---|---|---|
| Canary read FD | Other FDs/mappings remain usable after manager close/death. Worker death drops its references, not survivors'. Restart does not invalidate old open descriptions. | Permitted recipients can retain/read/copy. Avoid disclosure initially; after transfer no manager close operation revokes all reads. Only independently established removal of **all** accessible references/maps/transfer queues can close that raw authority; copied bytes remain. |
| Scratch write FD | Other holders can continue writes, including after original worker dies. Existing filesystem effects persist; queued I/O/writeback may finish after process death. | Same complete-reference problem, plus outstanding operations and persistent effects. Stop future reuse/publication of contaminated storage. No CLEAN/close/Binder-death certificate; need authoritative closure and completion for the actual scope. |
| Shared frame/map | Manager unmap affects its mapping only. SharedMemory.close leaves existing maps valid. Worker death removes its own address space, not inherited or external mappings. Manager restart cannot withdraw old maps. | Recipients/maps may retain reads/writes. setProtect can reduce **future** map permissions on success, not existing mappings. Full revocation needs all relevant mapping/reference lifetimes closed; copied frames cannot be recalled. |
| Sentinel/allocation never delegated | Manager close/free/death ends its own resource lifetime but supplies no remote-revocation proof. A new manager gets new resources; reuse is unsafe if unauthorized access or old authority is unresolved. | Numbers alone cannot be duplicated into capabilities. Independent host denial is the candidate protection. If any read/copy actually succeeded, treat those bytes as disclosed. No worker report certifies the absence of other access paths. |
| Owner Binder | Dropping one Java reference is not revocation. Actual owner-process death ends that hosted endpoint; worker can remain alive. Restart must create fresh trusted authorization, not revive old state. | A reference can be forwarded where Binder policy allows, but cannot keep a dead owner executing. Death of this endpoint certifies only its scope, not worker/tree death or closure of FDs previously sent. |
| Worker endpoint | Manager discarding proxy/unbinding does not prove worker death. Actual endpoint death is scoped; descendants may retain other authority. | Recipient of a worker endpoint may retain the reference but current endpoint checks expect management UID while honest. Future denial cannot rely on compromised server. Endpoint death does not certify resource revocation. |
| Runtime/launcher handles | Close affects one reference; fork inheritance precedes launcher closure. Fixed child reaping establishes only that child. Manager loss does not instantly close worker-owned pipes/handles. | Queued bytes, duplicates, inherited memory and external recipients require separate accounting. Trusted pre-exposure FD minimization helps; launcher CLEAN from compromised worker is not a certificate. Complete inherited inventory and independent lifetime proof are missing. |
| Framework Binder | Manager death does not kill system-service endpoints; worker death need not remove recipient references. | Service authorization can deny individual future calls independently. A service-specific revocation result has only its documented scope. No generic manager-controlled revocation of every reachable framework service is established. |
| Network/socket | A retained socket may outlive sender/worker through other references; manager close is not universal closure. Already queued/sent traffic is not recalled. | Trusted network endpoint/backend may stop future mediated traffic; raw socket shutdown is object/operation-specific and not a universal route control. No such broker/enforcer is implemented or validated. Exact routing/closure receipts belong to Gate D. |
| Already copied bytes | Can survive manager/worker death in surviving processes, durable storage or recipients. | Non-revocable once disclosed. No epoch, key rotation, deletion of original, process kill or completion certificate proves erasure of adversary copies. Prevent disclosure or accept its irreversible scope. |

**New repository inference:** Session uses fixed canary/scratch filenames and
FileOutputStream with append=false. Recreating an existing file truncates/writes
the same backing file rather than necessarily replacing its inode. A surviving
read FD can therefore observe later canary contents, and a surviving scratch
writer can affect a later session's backing file. No runtime occurrence is claimed.
Even an atomic new-file replacement would only separate new authority: the old
open object remains usable. Never reuse an uncertain raw object for a new epoch.

Session's ACTIVE guard is process-local; it can be released after worker Binder
death. The durable uncertain_child flag surrounds LAUNCH and can be cleared by
a valid worker-supplied cleanup result. Neither mechanism independently certifies
all references after arbitrary compromise, nor records all INIT delegation across
manager restart. Existing harness limits are retained, not represented as a
production fail-closed implementation. No Android source is changed here.

## Revocation classes and precise source witnesses

Future boot/image/disk FDs, guest RAM/TCG mappings, display adapters, capture
streams and network backends remain **proposals**, not existing harness grants.
Immutable boot data, mutable userdata and genuinely sensitive host data need
different lifetime/disclosure contracts; none is authorized by the synthetic
canary, scratch or frame controls.

| Class | Disposition |
|---|---|
| Never delegated | Prevent disclosure; prove independent denial of every alternate direct/deputy path. No retroactive recovery claim needed if absence is established. |
| Immutable read-only | Reads/copies are irreversible once possible. Immutability needs backing-object enforcement against **every writer**, not merely O_RDONLY on one FD. Current canary is read-only delegation, not proven immutable storage. |
| Raw writable | Owner close/epoch changes do not revoke other open descriptions or mappings. Potentially revocable only after actual complete reference/process closure and accounting for outstanding work; external recipients can prevent certification. |
| Independently mediated request/response | Future operations can be denied by a trusted sole resource owner checking every operation. Prior results and committed side effects remain. Not implemented in current harness. |
| Shared mapping | Existing mapping authority survives FD close. Restrict before exposure; later protection reduction is not withdrawal of existing maps. |
| Binder reference | Reference lifetime differs from method authorization. Trusted server can deny operations; dead server cannot execute them. Previously returned raw FDs/data escape that mediation. |
| Network/socket | No raw socket is deliberately delegated now. Future mediation must retain socket ownership and cover all egress; copies/queues/routes and direct syscall paths need separate proofs. |
| Disclosed/copied information | Non-revocable. Data minimization before disclosure is the control. |

**Fact, source:** SharedMemory.java at the pinned framework revision documents
that setProtect only narrows future mappings, while existing mappings retain
their protections (128–156). map uses MAP_SHARED (266–281); close explicitly
preserves open mappings (301–314). Its JNI nSetProt calls ashmem_set_prot_region;
this review does not infer a particular deployed ashmem/memfd backend or seal
implementation. Reducing protections before transfer is a public-API feasibility
lead; late setProtect(PROT_NONE) is not an existing-map revocation certificate.

**Fact, source:** ParcelFileDescriptor.dup uses F_DUPFD_CLOEXEC on current API
levels (370–391); detachFd hands native code responsibility without closing the
FD (787–802). closeWithError sends status and closes that local FD (830–857),
not every duplicate. writeToParcel copies the FD and only optionally closes its
local copy for return-value semantics (1124–1148). Session uses flags 0. Reliable
close/error notification cannot become a hostile-holder revocation protocol.

**Fact, source:** Linux v6.12 binder_translate_fd acquires fget, checks receiver
acceptance and security_binder_transfer_file, then holds a fixup reference
(2345–2410); binder_apply_fd_fixups installs a receiver FD with O_CLOEXEC
(4609–4643). binder_translate_binder/handle applies the Binder transfer security
hook and creates recipient references (2219–2343). Thus sending FD integers
through Binder has different semantics from sending Session's plain sentinel
integer. The source is a reference Linux kernel, **not** a deployed Android
kernel identity. Actual SELinux/credentials/receiver rules still constrain transfer.

**Fact, source:** scm_fp_copy takes file references for SCM_RIGHTS, and
scm_detach_fds installs receiver descriptors; MSG_CMSG_CLOEXEC controls the
receiver close-on-exec flag. Queued transfers can hold references even before
delivery. Linux mmap stores get_file(file) in the VMA. The previous ledger's
fs/file.c and kernel/fork.c establish separate/retained file references and
fork inheritance. FD_CLOEXEC affects successful exec, not fork, current use,
or data already copied; a permitted dup/fcntl can change descriptor inheritance.
Threads may share the FD table/address space. Exec drops old VMAs but does not
erase data sent elsewhere. MAP_PRIVATE copies can retain disclosed bytes;
MAP_SHARED writes can affect backing state. Unmap/close is not rollback of writes
or proof that asynchronous writeback has stopped.

**Fact, policy:** the existing pinned isolated_app_all.te allows read/write/map
on specified received app-data files while neverallowing direct app-data open.
It restricts service-manager lookup and non-Unix socket creation. isolated_app.te
allows specified received TCP/UDP use. These are concrete source authorities,
not a claim of unrestricted Binder/socket transfer or observed OEM enforcement.
System policy changes are not an ordinary-app revocation mechanism proposed here.

## Trusted ownership research, not an adopted architecture

**Hypothesis:** keep sensitive backing objects outside worker authority and expose
only bounded operations/results. This can independently stop **future mediated
access** after worker compromise if every path to that resource crosses the
trusted owner. Raw FDs, directory access, writable aliases or unrestricted proxies
would defeat that premise. It does not contain direct syscalls, kill descendants,
solve inherited FDs, certify cgroup cleanup, or erase results already disclosed.

| Ownership alternative | Benefit, failure semantics and unresolved authority |
|---|---|
| Existing trusted manager owns resource and mediation | No additional app process needed conceptually. Host isolation must protect its memory/FDs. Manager death stops its own execution, but completed replies, kernel work and copies may survive. Restart must default deny using durable authorization state. Hosting robust mediation in management increases parser/availability TCB; current empty owner Binder implements none of it. |
| Separately owned trusted broker | Can retain revocation state/quotas and observe manager loss independently of worker. A separate process with management UID is not a separate kernel protection domain from management; an isolated service has different resource authority. Separate package/UID or new service changes architecture and lifecycle. Manager loss detection is asynchronous: a death callback/lease gives no instantaneous crash-time cutoff. No new process/service/package is authorized. |

Public Binder caller UID, ordinary app-private storage and SharedMemory provide
legitimate building blocks; none grants privileged process-tree control. Binder's
pinned public contract warns against PID as a security identifier and can return
PID zero; UID describes the caller of the current transaction. A secure proposal
must capture caller credentials at entry before async dispatch/clearCallingIdentity,
and bind them to a trusted, live per-instance endpoint registration plus a server
generation and policy epoch. A UUID supplied by the worker, a recycled UID/PID or
an interface descriptor is not authentication. A transferable endpoint/token alone
is bearer authority; define whether descendants/forwarding are forbidden and how
the host actually enforces that. Exact-instance enrollment remains **Unknown**;
worker-reported INIT identity is insufficient as its trust root.

**Hypothesis: minimum reviewable mediation contract, not implementation:**

1. Trusted owner keeps a fixed resource allowlist; no arbitrary path, Binder,
   ioctl, shell, syscall, network-connect or open proxy. It never returns underlying
   sensitive raw authority. Return only deliberately disclosed bounded bytes.
2. Authenticate live caller/endpoint and generation; authorize resource, operation
   and epoch **on every request**. Server-owned sequence/use state rejects replay
   and stale generations. Restart must not reload old bearer grants as live.
3. Validate integer ranges with overflow-safe arithmetic, e.g. length <= size
   and offset <= size-length; bound total bytes, work, queue depth, concurrent
   requests, per-instance/global rate and lifetime. Copy hostile request metadata
   before use; untrusted shared buffers may change after validation.
4. Serialize revocation with authorization and the defined commit/disclosure point.
   Mark old grants inactive before acknowledging revocation. Recheck queued work;
   explicitly drain/cancel admitted operations, or report **RevocationPending**.
   Checking an epoch once and performing later I/O outside that ordering is a race.
5. Define what a receipt means: future admissions denied, or all relevant admitted
   work also completed/cancelled. An accepted pre-revocation operation can have
   completed effects or an already queued reply delivered later. Revocation cannot
   promise retroactive secrecy. Failure/timeout/absent reply means **Unknown**, not
   cancelled or denied. Downstream operations may lack cancellation entirely.
6. Persist inactive/uncertain state before exposing authority. Manager/broker loss,
   missed heartbeat or missing state never automatically enables access. A separate
   broker needs a trusted loss policy and expiration checks at admission/commit;
   operations during detection delay remain explicitly in scope. Reauthorization
   needs fresh trusted registration and reconciliation, not worker CLEAN.

Any material ownership/process/interface redesign is an **owner decision requiring
Tony's approval and an ADR** under PDVA-REQ-008. This record does not amend
ADR-0001/0002 or authorize implementation. Ordinary-app legitimacy remains a
conditional research lead; complete execution, confinement, distribution and
recoverable lifetime authority have not been established.

## Falsifiers, experiment disposition and enduring lockout

**Observation:** local host is Windows; WSL distribution inventory was empty.
No Linux runtime was installed and no Codex Cloud was used. A real independently
supervised mapping/broker test could add evidence, but was **not run or added**
here. Repeating PR #16's retained-FD case would add no new result. The stronger
new witnesses are the public SharedMemory limitation and repository ownership/
restart facts above. No simulated broker is reported as enforcement evidence.

| Proposition / falsifier | Exact future observation needed; current status |
|---|---|
| Close revokes mapping | Independent child still reads/writes known synthetic mapping after all its FDs and original owner's FD close. Parent independently observes shared-byte change. **Not run**; source contradicts the revocation claim. |
| Late protection change revokes old map | Successful setProtect followed by old-map access versus independently attempted new map under reduced protection. Test separately; no crash/timeout is successful denial. **Android physical Unknown**. |
| Broker can deny future access | Authorized request yields exact synthetic result; after trusted revocation acknowledgement, fresh requests receive exact DENIED_REVOKED with no resource operation. Disable the trusted check as a negative control and require the observer to reject the resulting access. **Not implemented/run**. |
| Epoch/instance checks suffice | Valid current caller succeeds; stale epoch, wrong instance, replay and transferred caller get distinct exact rejection statuses. Independent resource-operation counter remains unchanged. A check-bypass mutant must be rejected. **Not implemented/run**; registration authority unresolved. |
| Revocation undoes completed work | Pre-revocation copy remains readable while new request is denied. Count queued/in-flight work separately; any unaccounted operation keeps revocation pending. **Not run**; copied-data recall claim unsupported. |
| Manager/broker loss means clean | Independently identify and reap only fixed registered fixture children; next requests must yield exact trusted denial or explicitly Unknown transport outcome. EOF/crash/nonzero alone cannot pass. Restart with missing/stale state must remain denied. **Not run**. |

A future Linux-only fixture must use synthetic private data, no network/host data,
root, process scanning or security-setting changes; bound all creation, registration,
I/O, signaling and cleanup under an external supervisor. Use trusted parent-created
identities/pidfds, exact wait statuses and complete receipts. A mutated assertion
passes its negative test only after its expected rejection **and** independently
verified cleanup, never after arbitrary nonzero/timeout. It must add no Android
authority claim. These criteria specify falsifiers, not manufactured test receipts.

**Inference: persistent fail-closed lockout is required** before further sensitive
delegation or reuse when prior issuance/transfer is uncertain; a raw FD/map or
descendant may remain; instance authentication fails; launch/termination or I/O
completion is unknown; callbacks/replies are lost; manager/broker restarts without
durable reconciliation; an old grant may be replayed; or unexpected direct/deputy
access is observed. Persist uncertainty before exposure, including partial INIT,
not only before LAUNCH. Broker denial of old epochs can coexist with **CleanupUnknown**
for raw resources. Never promote one scoped denial to whole-worker revocation.

Only an independently justified, scope-complete reference/process/operation closure
or a reviewed abandonment of affected resources can allow the corresponding reuse;
abandonment does not certify revocation or undo disclosure. No ordinary-app global
certificate is established. Lockout can be indefinite. Fresh UUIDs, process IDs,
Binder death, elapsed time, reinstall/data clearing and manager restart cannot
clear it by themselves. The current research harness is not retrofitted here.

Physical Android work remains necessary for actual received-FD/map and transfer
policy; framework/inherited descriptor inventory; installed SELinux/seccomp and
kernel/ABI behavior; direct service/deputy authority; native launch inheritance;
manager death/restart, blocked threads and teardown latency; and trusted instance
enrollment. Exact source/manifest/configuration closure and independent observation
are prerequisites. A phone test alone cannot prove erasure of external copies.

**Decision:** narrow trusted ownership is a plausible way to avoid raw sensitive
authority, strengthening the Gate 0 research question. It does not resolve the
existing lifetime/descendant/direct-syscall blockers or establish a shippable full
Android VM. STOP dependent guest/engine integration and production security claims.
compileSdk/targetSdk stay 37, research minSdk 30; supported host minimum Unknown.

## Provenance and validation

The [source ledger](gate-0-capability-revocation-sources.md) records immutable
identities, licenses and reproduction. New text is original PDVA analysis; no
upstream implementation, binary or dependency is imported. Existing source pins,
workflows, controls, Android application and architecture are unchanged.

**Observation:** foundation validation passed: 99 files, 57 Markdown files,
54 requirements and two ADRs. Harness authority validation passed. The existing
regression suite completed 138 tests: 134 passes and four existing Windows skips;
skips are not passes. Tests used the existing NDK-bundled Python 3.11.4 after the
WindowsApps Python alias could not execute. No interpreter/dependency was installed.
The seven newly retrieved source hashes and two retained policy hashes matched
their ledgers. Full three-file diff review covered source claims, links, licenses,
100644 text modes, whitespace, public-data hygiene and unchanged CI filters.

New Linux mapping/broker controls and physical Android tests: **NOT RUN**. No
Android rebuild was needed for this documentation-only change. Hosted CI for this
new PR is **pending/unobserved at publication**; the exact-main baseline receipts
above are separate. Stop after one immediate PR identity/native-attachment check.
