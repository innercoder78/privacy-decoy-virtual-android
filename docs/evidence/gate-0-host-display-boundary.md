# Gate 0: host display boundary and untrusted frame ownership

Review: **2026-10-25; Windows x86_64; public-source review and desktop controls.**
**Gate 0 Unresolved; Gates A–G Not reached. ADR-0001 Accepted; ADR-0002 Proposed.**
Scope: PDVA-REQ-001–015, 016–027, 031–037, 039–048 and 054. This record adds
no engine selection, guest implementation, production bridge or trusted renderer.

## Question and disposition

Can an ordinary Android app display bounded pixels from a potentially compromised
isolated worker without giving it management, protected-data or trusted-UI authority?

**Source-supported mechanism lead, complete boundary UNKNOWN.** Public binding,
shared-memory/FD and app-owned presentation APIs exist; there is no source-grounded
need to give the worker a host Surface merely to display raw pixels. This supports
investigating a manager-owned bounded copy/presentation path, not declaring that
path secure, implemented or performant on stock Android 17.

**STOP treating read-only reception, a successful copy, an unchanged counter or
worker completion as a coherent-frame certificate.** In the inspected API contract,
read-only describes mapping permissions, not absence of writers. Even
`SharedMemory.isRegionReadOnly()` allows existing writable mappings. An owned copy
prevents subsequent source writes from changing that copy; it does not prove that
its bytes existed together at any instant. Neither coherence nor memory bounds
establish honest pixels, trusted UI or worker cleanup.

The new reusable disposition is to distinguish **bounded hostile raster data**
from **a coherent, authenticated guest display** at each admission and presentation
step. A future proposal must state whether mixed hostile pixels are acceptable
as data or supply an independent coherence mechanism. This record does not approve
either production contract or an extra trusted process to obtain it.

This is the **host transfer boundary**, separate from the unresolved guest
format/fence/kernel pairing in [graphics configuration closure](gate-0-android17-graphics-config-closure.md)
and [software graphics](gate-0-android17-software-graphics.md). Their scoped STOP
findings remain intact; no guest graphics configuration was reinvestigated.

## Baseline and prior evidence inventory

Live GitHub commit metadata and an independent `git ls-remote` agreed on main
`18d3480c36ebbbb85051d91592b326048f1976c0`, the merge of PR #37. Connector search
and REST open-PR inventory both returned zero; there were no open heads/bases,
diffs/files, checks, reviews, comments or threads to inspect. Exact-main workflow
inventory returned only [foundation run 40143471844](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40143471844).
Both job steps and execution logs were inspected: foundation `121019842114` and
offline-image-windows `121019842221` succeeded at that SHA. Foundation logs include
141 repository, 27 readiness and 45 image tests, seven native wait controls,
assertion rejection, dormant bootstrap controls, four lifetime cases/four mutants,
four seccomp cases and ten revocation cases/ten mutants. Windows logged 45 image
tests. These are existing hosted receipts, not new Android or local native runs.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational during preflight. Shell network restrictions required approved escalation.

Reviewed requirements, governance, both ADRs, gates/acceptance criteria,
architecture, boundaries, threat model, Persona, testing, networking, roadmap,
provenance/adoption records and all records in the following inventory. One local
worktree, branches, no stashes, clean tracked state and ignored build/source assets
were inventoried and preserved. The 130 baseline files had regular 100644 modes;
no applicable AGENTS.md was found. The focused branch starts at the exact main above.
Ignored checkpoints are interruption aids, not independent backups. No private
comparative material was reacquired; its independent retention remains unverified.

| Prior evidence | Already established / limit relevant here |
|---|---|
| [Isolated-worker harness](gate-0-isolated-worker-harness.md), [Protocol](../../android/gate0-harness/src/main/java/org/pdva/gate0/Protocol.java), [Session](../../android/gate0-harness/src/main/java/org/pdva/gate0/Session.java), [WorkerService](../../android/gate0-harness/src/main/java/org/pdva/gate0/WorkerService.java) | Fixed 64×64, stride 256, 16384-byte synthetic data; two frames, sixteen input tokens, epoch and worker-side UID checks. JVM tests cover shape/overflow/quota/order; instrumentation is not a physical result. Manager reads a RO mapping byte by byte after synchronous replies. No actual display or arbitrary guest receiver. |
| [QEMU integration](gate-0-qemu-worker-integration.md) | A future adapter needs bounded display/input ownership; existing executable/JNI and startup/TCG restrictions are not solved by pixels. |
| [Containment](gate-0-worker-containment.md), [capability revocation](gate-0-capability-revocation.md) | Worker-side checks can be bypassed after compromise. RO mapping is not immutable backing. Duplicates/maps survive owner close. No full deputy/handle inventory. |
| [Linux mediated revocation](gate-0-linux-mediated-revocation.md) | Existing independent mapping/mediated-operation, replay, epoch and uncertain-result controls; no need to duplicate them. Linux does not prove Android enforcement. |
| [Android lifetime](gate-0-android-lifetime-authority.md), [research recovery](gate-0-research-recovery.md) | Framework termination candidate lacks ordinary-app tree-empty receipt/deadline. Manager-loss enrollment and authenticated-journal rollback STOP results remain. |
| [Memory Limiter](gate-0-android17-memory-limiter.md) | Conditional BOUND_TOP state, shared-page/group accounting and unknown installed budget; mappings, copies and presentation must be counted separately. |
| [Comparison plan](gate-0-black-box-comparisons.md), [Persona policy](../persona-privacy-policy.md#identity-surface-contract-matrix) | Generic behavior questions and detailed identity semantics already exist; comparative context cannot establish source correspondence or isolation. New deltas below do not repeat the identity matrix. |

## Public Android contracts and their authority limits

F denotes frameworks/base `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`, the existing
Android 17 reference. N denotes frameworks/native
`ae266dcb706d083868578cfedce381ef44488a07`, resolved live from `android-17.0.0_r1`.
Immutable file receipts below identify actual reads. These project pins are not
an installed OEM manifest or proof of enabled release flags. Public API signatures
were checked in F `core/api/current.txt`; hidden methods are not ordinary-app grants.

**Source observations:**

- F `Context.bindIsolatedService` provides named isolated binding. Existing
  [lifetime trace](gate-0-android-lifetime-authority.md#caller-to-enforcer-trace)
  identifies component access checks, framework UID allocation and binding
  ownership. No privileged permission is needed for the existing own-service
  binding. An isolated UID is not an exemption from host policy or a complete
  containment certificate. PID/UID supplied by a worker in reply data are untrusted.
- F `Binder.getCallingUid()` describes the current incoming transaction's caller;
  outside that context it returns the local UID. Capture/authenticate at the
  receiver entry before dispatch or identity clearing. An epoch string is not a
  caller credential. The existing checks execute in the worker and protect the
  opposite direction; they do not implement an authenticated worker-to-manager
  receiver. Safe enrollment of a callback's exact live instance remains unproved.
  A manager-initiated pull can bind replies to its retained endpoint/session, but
  a hostile endpoint can block a synchronous transaction indefinitely; it must not
  run on the management UI thread or create unbounded replacement threads.
- F `SharedMemory.create/mapReadOnly/mapReadWrite/setProtect` are public (API 27
  for the original Java family). Creation is not a PDVA quota. Maps use MAP_SHARED.
  `setProtect` only narrows future mappings and must be checked for success.
  A worker retaining an earlier writable map can keep modifying it. Reducing
  protections before exposure cannot both remove write authority and let that
  recipient become a live writer. Reduction is not a reversible frame lock.
- F `isRegionReadOnly` is a flagged public signature. Its contract explicitly
  allows existing writers; implementation accepts either F_SEAL_WRITE **or**
  F_SEAL_FUTURE_WRITE, with an ashmem protection-mask fallback. Thus a true result
  is insufficient for immutable frame admission even where the API is available.
  No reliance on that release flag or direct seal syscall is proposed.
- F map bounds use signed `offset + length`; callers must independently check
  nonnegative values and `length <= size - offset` in an appropriately widened
  domain before mapping. A public API is not a substitute for hostile-metadata
  validation. This source observation is not a claimed demonstrated exploit.
- N `ASharedMemory_create/getSize/setProt` are public NDK API 26; dupFromJava is
  API 27. N's header says protection removal applies across descriptors but leaves
  existing maps unaffected. F's JNI and native wrapper call the ashmem abstraction;
  they do not establish the installed backend, seals or SELinux outcome. The NDK
  duplicate uses F_DUPFD_CLOEXEC in F; API documentation warns that intentional exec
  inheritance requires clearing CLOEXEC. No such new inheritance is authorized.
- F `ParcelFileDescriptor.dup/detachFd/writeToParcel` distinguish duplication,
  ownership handoff and local close. `SharedMemory.fromFileDescriptor` consumes
  the supplied PFD. Java `getFd/getFileDescriptor/getFdDup` on SharedMemory are
  hidden at F; public NDK interop is not permission to call hidden Java APIs.
  Closing a sender FD or unmapping a manager view does not revoke remote maps,
  duplicate FDs, queued transfers or copied bytes. Unknown object type/size cannot
  be made safe by trusting a producer's length field.
- F `Bitmap.copyPixelsFromBuffer` checks supported Buffer types and enough bytes,
  uses widened byte arithmetic, invokes native copy and advances buffer position.
  Its contract leaves pixel representation unchanged, including premultiplication
  and color space; it is not a stride/channel converter or an atomic-snapshot API.
  Any proposed raw RGBA transfer needs an explicit validated match to destination
  row bytes, channel order, alpha and color interpretation, without worker-selected
  allocation or decoder formats. Never present directly from a still-shared alias.
- F `SurfaceView`/`SurfaceHolder` provide ordinary app presentation. Window callbacks
  and drawing threads require synchronization; drawing is limited to surface
  lifetime. `lockCanvas` can return null, and its lock lasts until
  `unlockCanvasAndPost`; it protects the destination surface, not source pixels.
  SurfaceView describes default composition behind the window and caveats for
  transformed overlays. This is no guarantee that arbitrary z-order/full-screen
  layouts preserve trusted controls. Surface ownership, view geometry and posting
  remain in management; no Surface, GPU node, display-server connection or arbitrary
  Binder proxy is handed to the worker to simplify presentation.

Official mutable references checked during this review:
[SharedMemory](https://developer.android.com/reference/android/os/SharedMemory),
[NDK memory](https://developer.android.com/ndk/reference/group/memory),
[SurfaceView](https://developer.android.com/reference/android/view/SurfaceView).
The pinned implementation contracts, not a current website label alone, support
the distinctions above. No root, shell, hidden cgroup control, OEM permission,
host input injection, privileged display management or host VPN route is inferred.

## Prospective flow and receiver proof obligations

```text
hostile guest graphics → hostile rendering/VM worker → bounded producer interface
  → validated transport → trusted management receiver → app-owned display region
```

Everything through the producer remains untrusted. Only host OS enforcement and
trusted receiver decisions could constrain a compromised worker. The following is
a **hypothesis/proof checklist**, not an implemented protocol or revised architecture.

| Boundary | Actual or candidate enforcer; admission and ownership obligations | Failure / independent proof still missing |
|---|---|---|
| Guest → VM worker | Guest kernel/device model provide functionality, not host protection after compromise. Native worker may emit arbitrary metadata and pixels. | Guest-side formats/fences remain separately blocked; an Android-looking image proves neither a guest kernel nor isolation. |
| Worker → bounded producer | Kernel/SELinux and pre-exposure restrictions must bound real resources. Cooperative dimensions, completion and quotas in worker code do not constrain hostile native writes. | Inventory reachable devices, services, inherited handles, descendants and transfers; no management secrets, Persona master, host identifiers or peer-instance authority may be delegated. |
| Producer → transport | Prefer investigating manager-created, fixed-size, per-instance backing with only the required write capability; do not accept arbitrary worker FDs or paths. Kernel object rights and mappings enforce access, not claimed descriptor numbers. | Prove backing-object type, fixed extent, resize/truncation denial, access restrictions and every alias/transfer route on the actual Android backend. No assumption that fstat once or RO receiver prevents later mutation. |
| Transport → receiver | Trusted receiver independently owns metadata, caller/instance enrollment, epoch and monotonically accepted sequence. Fix one pixel representation; validate width/height, checked row-byte arithmetic, stride, offset and length before mapping/allocation/copy. | For a proposed padded layout, require positive bounded w/h, stride >= w×bpp, checked h×stride within an explicit cap, and offset/extent within the actual object. Reject unsupported formats, negatives, overflow, truncation, extra descriptors/fields and mismatched layout. Exact production dimensions/caps remain unselected. |
| Receiver admission → owned frame | Receiver bounds aggregate bytes/FDs, copy work, requests per interval, in-flight work and queue depth; rejects before allocations driven by hostile values. Recheck trusted epoch/surface generation before publishing; only successful admission advances sequence/display state. | Need independent replay/out-of-order, wrong-instance/stale-epoch, duplicate/premature completion, flood/quota and rejected-state tests for an actual receiver. A rate-limited consumer alone does not bound hostile Binder ingress or worker allocation. |
| Owned frame → app display | Trusted manager owns private bytes and destination bitmap/Surface; only raw validated raster data crosses. Manager chooses clipping, alpha, placement and fixed trusted chrome. Bound retained display frames and release after destination use, not worker acknowledgement. | No coherent frame claim without independent source-write exclusion or equivalent proof. No pointer/decoder/shader/arbitrary object supplied by the worker. Surface destruction, failed lock/post, backgrounding and interruption must discard pending stale work and preserve management responsiveness. |
| Reset/resize/rotation/input | Manager controls geometry generation and a new resource/epoch transition; old messages cannot resize a current destination. Input maps only app-owned guest-region events to bounded guest coordinates with cancel/release semantics. | Old contacts, rotation transforms, density/letterboxing, IME composition/focus and interrupted resize need tests. No host-wide injection or forwarding management-button input to the guest. Completion of one resize does not certify retirement of old writable objects. |
| Worker death/manager death/restart | Trusted receiver can revoke future presentation independently of worker consent. Local queues/maps can be retired with synchronization. System owns actual isolated-process termination. | Worker death is not all-reference closure; manager death ends its observer. Never reuse uncertain backing or clear lockout from an ack, blank screen, timeout or restored journal. Existing manager-death/rollback STOP findings remain. |

Aggregate accounting includes producer backing, private copies, destination bitmaps,
surface buffers, metadata/IPC and all instances. The formula is not merely
width×height×4; row padding, multiple retained frames and presentation allocations
matter. The [Memory Limiter record](gate-0-android17-memory-limiter.md) does not
provide an app-controlled reservation or hard total PDVA budget. Java heap/native
allocation accounting and shared-page cgroup charges are different measurements.

On timeout or renderer failure, management should label the guest view unavailable
or stale, stop accepting it and preserve a host-owned escape. That is a proposed
UI response, **not** permission to claim process termination, erased data or safe
restart. Never interpret guest pixels, notification text or a fake permission
dialog as authorization to disclose data or change control-plane policy.

## Bounded desktop control: ownership is separate from coherence

The existing synthetic protocol and Linux revocation suites already exercise
bounds/epochs/quotas and retained capabilities. The distinct control in
[test-frame-copy.py](../../.github/scripts/test-frame-copy.py) uses standard-library
Python mmap, two views of one 4096-byte synthetic temporary file, and at most one
fixed producer thread. No child/hostile process, native compiler, Android runtime,
guest, VM, device or downloaded dependency is used.

Reproduce at repository root: `python .github/scripts/test-frame-copy.py`.
The semantics being tested are actual read-only mapped views and independently
owned Python bytes. The two-byte payload is deliberately not a graphics protocol.
An event-controlled interleaving makes the counterexample deterministic, not a
claim about atomicity or race frequency of one particular bulk memcpy instruction.

| Control / actual Windows observation | What it establishes |
|---|---|
| Write through RO view raises TypeError; retaining a memoryview after AA → BB reads BB | The intentionally incorrect alias-as-copy implementation violates post-copy stability. Python rejects that write; no native fault or Android VMA enforcement is tested. The writer remains able to change the backing. |
| Before-copy mutation produces BA; owned bytes stay BA after backing becomes BB and after both mappings close | Copy owns its later byte lifetime. It incorporates earlier writes and supplies no independent producer-authenticity evidence. |
| Quiescent producer: copied AA, recorded source AA, constant even counter accepted | Positive control confirms the observer and collection path can capture stable bytes. |
| Controlled writer changes AA → BA → BB between the receiver's first and second byte reads; result AB; counter stays 2 | AB never existed in the backing payload. The intentionally incorrect equal-even-counter certificate accepts it. Later CC writes leave AB stable: stability and coherence remain distinct. |

All four tests **passed locally**, Python 3.11.4 on Windows x86_64. The tests use
unittest checks (not removable Python assert statements), bounded event waits,
thread join and context-managed mapping/file cleanup. A timeout, unexpected
exception or missing primitive is failure, not a passing skip. This fixed-thread
fixture does not test arbitrary producer hangs or certify hostile-worker cleanup.
No asynchronous producer-death, production parser, graphics layout, resource flood,
Binder caller/epoch, Android setProtect or Android presentation test was run.

The source state sequence is independently read from the receiver mapping after
each of the only two stores; synchronization prevents unobserved extra stores in
this fixture. A real attacker could also forge counters/checksums or report false
completion. No checksum test is needed to confer that nonexistent trust: a digest
of attacker-controlled bytes authenticates no independent producer or instant.

The foundation workflow executes this control on Linux and Windows with its
existing exact-head checkout and deadlines; all prior checks remain. Narrow
validator admission adds only this script. The Android build workflow is also
selected by .github changes; QEMU's specific path filters are not selected.
**New hosted execution is pending/unobserved until independent review.**

## Consolidated comparative lessons: hypotheses only

The task supplied generic lessons from private comparative research. These are
**owner-supplied context**, not independently reproduced findings about third-party
binaries. No product/publisher identifiers, proprietary filenames, sample paths,
hashes, extracted symbols/code, APKs/ROMs or private reports are published here.
Public Android source supports mechanisms above, never private binary behavior.

| Distinct lesson / proposed PDVA test | Existing contract preserved and remaining question |
|---|---|
| Rendering bridges and callbacks are authority boundaries | Native framebuffer/GPU-command functionality motivates the host receiver trace above; successful graphics is not independent guest-kernel execution. Test timeout during copy/post, stale geometry and trusted escape despite hostile imagery. Input/IME/touch/rotation need their own ownership contract, not a successful frame checksum. |
| Provisioning separates host runtime from guest system files | Bind one controlled Android 17/API 37 image, ABI and device-interface version to its authorized host runtime and instance-specific userdata. Test interrupted staging/activation/rollback and incompatible runtime/image pairs under [image lifecycle](../guest-image-lifecycle.md). A root filesystem of Android files is not a booted phone; multiple archives do not authorize arbitrary versions/ROM imports. Authenticity, source rights and updates remain required; ADR-0002 stays Proposed. |
| Graphics/model selection can reintroduce genuine identity | Proposed distinctive failure: deleting a synthetic graphics/model setting, changing renderer configuration or failing a fallback branch silently selects host hardware descriptors. Compare paths against synthetic host sentinels under the existing [identity test matrix](../testing.md#future-persona-identity-and-leakage-acceptance). This is a hypothesis, not an observed PDVA leak. No identity implementation is added. |
| Identity consistency includes missing state and transitions | Reuse existing tests for Java versus Binder/native/property paths, cross-instance identifiers, carrier/SIM/network consistency, region/locale/timezone, displayed number versus operational line, and restart/corruption/restore resurrecting Real. Preserve Real/Decoy/Empty/Deny and method-specific permission/scoping behavior. No host IMEI passthrough, host-GPS fallback or attestation bypass. The new display-specific risk is presenting a guest's claimed Persona as trusted management state. |
| Working host integration can hide ambient authority | Test absence of policy as denial, inherited/transferred FDs, Binder deputies, exposed instance services and native loader/executable authority. Installation success says nothing about privilege required by each feature. Hooks, profiles, namespace tricks, broad delegated permissions and unreviewed SDKs cannot become the primary PDVA boundary. No host Surface/device/proxy grant is justified by convenience. |
| Visible instance state must describe evidence | Distinguish hidden, paused, frozen, disconnected, stopped and independently terminated. Test guest notifications/actions impersonating management, status after renderer loss, persistent userdata across reset and reliable management return. A closed/frozen screen proves neither process-tree death nor FD revocation or erasure. Manager-loss enrollment and journal-rollback STOP findings are unchanged. |
| Network and supply-chain claims need independent receipts | Host VpnService use does not satisfy PDVA's no-VPN-slot-takeover contract; independently verify required external host VPN routing. Proprietary engine binaries are not automatically trusted, advertised virtualization is not a boundary, and open demo code does not prove opaque-engine source correspondence. Graphics/device-identity claims need independent evidence. Static APK analysis cannot establish runtime enforcement; Android source mechanisms do not prove stock-release behavior. |

The public record distinguishes source fact, direct desktop observation, upstream
claim, inference, hypothesis, Unsupported and Unknown under existing acceptance
criteria. The hypotheses add review questions only, with no private checkpoint
or private-data collection. Independent private backup was not verified.

## Remaining blockers and smallest legitimate proof

The first source falsifier is already present: **RO receiver / true
isRegionReadOnly / equal worker counter ⇒ coherent immutable frame** is invalid.
The desktop trace independently falsifies the counter and alias variants within
its stated environment. Reject such a proposed certificate before integration.

Smallest new independent receipt for this host-boundary slice: actual receiver
observations using synthetic bounded bytes, one exact manager-owned object and
an independently authenticated isolated-instance binding on an identified stock
Android build. A separately reviewed dormant experiment specification must precede
any execution. It must identify the actual fixed-extent/write/transfer enforcement,
receiver-owned copy and commit-time epoch/surface-generation checks, bounded IPC
and UI-thread behavior, explicit coherence claim (or lack of one), and an
independent observer capable of detecting wrong-instance publication or post-copy
mutation. The first runtime falsifiers would be any such acceptance/mutation,
access to protected sentinels, or loss of trusted escape under producer failure.
This is a proof requirement, not authorization to activate an Android diagnostic.

An eventual separately authorized stock nonrooted release-equivalent run must
also test actual Binder/FD/deputy authority, mappings, destination ownership,
rotation/background/death and memory accounting. No finite successful copy test
proves exhaustive isolation. The existing lifetime/enrollment/recovery blockers
must be resolved before any task that depends on cleanup can execute safely.

Complete Gate 0 still lacks ordinary-app stock execution and hostile-worker
containment, independent termination/retained-capability closure and safe manager
restart, installed memory budgets, and full guest build/toolchain/backend plus
guest-side graphics correspondence. No complete Android launcher, full guest,
protected Persona, VPN routing, retail certification or Play Integrity result is
established. These blockers cannot be repaired by choosing an engine, extra trusted
renderer, host privileges, hooks or a simulated UI in this evidence PR.

## Validation and source receipts

Local validation used the existing Python 3.11.4, without installation:

| Command / review | Actual result |
|---|---|
| `python .github/scripts/validate-foundation.py` | PASS: 132 files, 80 Markdown files, 54 requirements, two ADRs; local file targets and regular-mode checks included. |
| `python .github/scripts/validate-harness.py` | PASS: source/manifest authority checks only. |
| `python .github/scripts/test-repository-validation.py` | 141 tests: 137 passed, four existing Windows/platform skips; no failures. |
| `python .github/scripts/test-desktop-readiness.py` | 27 passed, no skips. |
| `python .github/scripts/test-offline-image-inspect.py` | 45 passed, no skips; synthetic inputs only. |
| `python .github/scripts/test-frame-copy.py` | Four passed, no skips; actual observations scoped above. |
| Diff / provenance / privacy | Complete six-file change, source receipts, local links/anchors, table structure, whitespace, regular modes and binary/dependency inventory reviewed. No private comparative material, host identifiers or normative changes included. |

Android runtime,
phone/ADB, VM/QEMU, guest boot, actual Surface presentation and hostile-process
experiments are **NOT RUN**. Linux native suites were not rerun locally; existing
hosted receipts above remain separately attributed. Windows skips remain skips.
Android build/lint was not rerun locally because no harness/build source changed;
its selected hosted workflow remains pending/unobserved. The new desktop code is
not imported by Android or connected to any phone-facing control. No CI check was
weakened. After one intended PR is published, attach it natively, check association
and exact head/base once, then stop without polling hosted execution or reviews.

Source procedure: retrieve immutable Gitiles paths with `?format=TEXT`, decode
base64 without newline conversion, SHA-256 the bytes and inspect methods with
their contracts/call sites. The attempted sharedmem header paths under F
`native/android/include/android` and N `libs/android/include/android` returned 404;
pinned directory/build inspection resolved N `include/android` instead. No failed
fetch counts as evidence of missing Android functionality. Read source and headers
carry Apache-2.0 notices; the API signature listing is metadata from the same
project. No external implementation is imported or adopted. New control code is
original PDVA standard-library research, with no new dependency or repository-wide
license inference. Existing Gradle/native/dependency inventories remain unchanged.

The immutable URLs and decoded-byte hashes below are public source receipts,
not private sample hashes. Existing [revocation source identities](gate-0-capability-revocation-sources.md)
and [containment ledger](gate-0-worker-containment-sources.md) supply the inherited
Binder/kernel/SELinux/lifetime witnesses; they are not new runtime observations.

| Immutable public source | SHA-256 of decoded bytes |
|---|---|
| [base: core/java/android/os/SharedMemory.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/SharedMemory.java) | `218bdffe38c40b599e516c338f5df94258750abab77b3a589c0a49dc288ea05c` |
| [base: core/jni/android_os_SharedMemory.cpp](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/jni/android_os_SharedMemory.cpp) | `1e2e951bb055af67dd72ced0acbb244a43cf46496b85d6ce729a4f2f26805082` |
| [base: core/java/android/os/ParcelFileDescriptor.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/ParcelFileDescriptor.java) | `dd76635b7ed062dac3d04f5941f39bf63c5680841292d1bc07c39845722d5cbf` |
| [base: core/java/android/os/Binder.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/Binder.java) | `502dcd0067b3603e321086917e8e2274a8fc7beae1e9a75b335c2a035707ea6e` |
| [base: core/java/android/content/Context.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/content/Context.java) | `a27cd9ce56a980932b3b03400c9394f97b04ef940b2a97db08109bae91a758b4` |
| [base: core/java/android/view/SurfaceView.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/SurfaceView.java) | `05b6e42eda667dc9bb140779b1df2b1dab4ebedd28a0d3363bf9fcaba72a3aca` |
| [base: core/java/android/view/SurfaceHolder.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/SurfaceHolder.java) | `a6799cd4dd4a9cf758cc49a417b0349c9c03fa8b1b09f196da14c3331e0aaf3b` |
| [base: graphics/java/android/graphics/Bitmap.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/graphics/java/android/graphics/Bitmap.java) | `6011a390d55adf562831a2677e40bb5f6d6b144e89693b14b209dff051839a4a` |
| [base: core/api/current.txt](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/api/current.txt) | `116c793ecd67c793fe3d51c0cbfa158dff2e7f2d8defcd1b9fc60d829547e18a` |
| [base: native/android/sharedmem.cpp](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/native/android/sharedmem.cpp) | `3bcda0fc7b97d009b3720e4ad80fa1f488da490f16c37d2889e563d8ea8ada05` |
| [base: native/android/Android.bp](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/native/android/Android.bp) | `776089657a799e7af8d592945c3ebf1428529642e162773b93d75d9429964bac` |
| [native: include/android/sharedmem.h](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/include/android/sharedmem.h) | `2314b7b0d81b77b23e99094911cbcc603e10e1860740c3546b0dfca683e3e9c4` |
| [native: include/android/sharedmem_jni.h](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/include/android/sharedmem_jni.h) | `565875c92ecd629339c5e9ec599520f16b2e02413956f27882faf4014bfb3a7a` |
