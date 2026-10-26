# Gate 0: Android 17 audio service, virtual sound and host authority

Review: **2026-10-25; Windows x86_64; source-only.** Guest reference:
Android 17/API 37 r1, `aosp_cf_arm64_phone` / `vsoc_arm64`, little-endian ARM64,
nonprotected phone, default audio package and policy choices. **Gate 0 Unresolved;
Gates A–G Not reached. ADR-0001 Accepted; ADR-0002 Proposed.** No engine,
process placement, bridge or capture policy is adopted.

## Question and disposition

Can this guest obtain functional, source-compatible playback and explicitly
authorized capture through a virtual device and narrowly controlled host peer,
without privileged host access, unintended microphone disclosure or additional
authority for a hostile VM worker?

| Question | Disposition and evidence limit |
|---|---|
| A. Is the unchanged reference a complete functional audio path? | **SCOPED STOP.** QEMU declares AC97 with `driver=none`; that backend consumes output without presentation and supplies silence on input. The separately created audio socket is not connected by this QEMU launcher. HAL registration/advancing frames cannot repair this. [qemu-launch] [none] [streamer-launch] |
| B. Is a software-only guest mechanism available? | **SOURCE-SUPPORTED** at mechanism level: the selected AIDL primary HAL has an ALSA PCM path; the kernel source has virtio-sound and the pinned QEMU implements an internal software virtio-sound device. Their complete configured pairing is **CONDITIONAL**, not an installed or runnable result. AC97 is another source mechanism, with its guest driver/configuration correspondence unclosed. [primary] [kernel-card] [virtio] |
| C. Can ordinary host playback avoid prohibited authority? | **CONDITIONAL.** Public `AudioTrack` accepts app-supplied PCM. A narrow, independently authorized receiver could own it; no such QEMU-to-Android adapter or enforcing arrangement is established. Host `/dev/snd`, HAL ownership and privileged audio control are not ordinary-app substitutes. [track] [app-policy] |
| D. Is source/build correspondence complete? | **UNKNOWN.** Generated product/APEX/configuration and exact kernel/module/toolchain agreement are missing. The selected audio APEX additionally names classifier/separator model prebuilts; model-generation correspondence is not established. No payload was downloaded. [apex] [eraser-build] |
| E. Can Real microphone authority be withheld? | **SOURCE-SUPPORTED** separation of public recording permission/system checks from playback; **CONDITIONAL / UNKNOWN** for a genuine PDVA enforcing boundary. Keep capture ownership outside hostile code and default-deny Real. Existing containment, direct-service and lifetime gaps prevent claiming enforced isolation. [record] [record-policy] |
| F. Smallest new proof before build/runtime? | Independently reproduce one exact source-selection and endpoint contract: actual product/release overrides, service/configuration, card/driver/PCM tuple, QEMU device/backend build closure, and a bounded host admission interface with no capture capability in the worker. Reject on any missing mandatory edge, silent stub, unqualified prebuilt or prohibited host authority. This record supplies source leads, not that completed proof. |

S = source observation; I = inference; H = proposed responsibility; U = Unknown.
**Every behavioral/negative-control experiment below is NOT RUN.** A negative
unchanged pairing does not establish that all ordinary-app audio designs fail.

New findings beyond the merged [complete guest](gate-0-complete-android.md),
[boot/HAL](gate-0-android17-boot-hal.md) and
[communication](gate-0-userspace-communication.md) evidence are the actual AIDL
APEX selection, default ALSA card/device, conditional simulation properties,
nonpresenting MMAP/offload paths, PCM loss with reported progress, the distinct
socket/FD protocol, and model-prebuilt dependency. The guest HAL is not selected
merely by the presence of the older goldfish audio sources or a HIDL comment.

## Baseline, preflight and preservation

Live GitHub commit metadata and fetched `origin/main` agree on
`6f82c654caf6c35894fb930f6596defa55aa77bb`, the merge of
[PR #40](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/40).
Relevant history includes input #40, sensor #39, display #38 and graphics #37.
The all-open-PR query returned zero: no open heads/bases, full diffs/files,
checks/jobs/logs, reviews/comments/threads needed reconciliation, and no audio
PR existed to reuse.

[Foundation run 40249529961](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40249529961)
completed successfully. Actual logs for foundation job `121338164579` and
offline-image-windows job `121338164476` were inspected; both identify the exact
main SHA. Foundation records 141 repository, 27 readiness, 45 image and four
frame tests plus the existing native/bootstrap/lifetime/seccomp/revocation
controls. Windows records 45 image and four frame tests. These are baseline
controls, not audio tests. All three workflow definitions were inspected;
foundation applies, while Android and QEMU path filters do not select this
two-Markdown-file change. Filtered jobs are not passes.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All
Systems Operational during preflight (page update `2026-10-25T21:34:17.136Z`).

Initial tracked state was clean on the previous input branch, with one worktree
and no stashes. Branches, ignored build/source/tool assets, tracked modes,
native/dependency inventory and notices were inspected and preserved. No
applicable AGENTS.md was found. Git metadata writes and public-source networking
required authorized sandbox escalation; no setting or approval gate was bypassed.
The intended branch starts at exact main. No reset, clean, restore, destructive
stash operation, force push or historical-repository write occurred.

Governing inputs are requirements, architecture, gates, acceptance criteria,
governance, security boundaries, threat model, Persona policy, networking,
testing, roadmap, provenance policy and both ADRs. The requested earlier
evidence and companion ledgers retain their scope: [backend endpoints](gate-0-backend-endpoints.md),
[worker integration](gate-0-qemu-worker-integration.md),
[graphics](gate-0-android17-software-graphics.md),
[input](gate-0-android17-input-compatibility.md),
[sensors](gate-0-android17-sensor-service-closure.md),
[host display](gate-0-host-display-boundary.md),
[containment](gate-0-worker-containment.md),
[revocation](gate-0-capability-revocation.md),
[Android lifetime](gate-0-android-lifetime-authority.md) and
[memory limiter](gate-0-android17-memory-limiter.md). None is reopened as a general
survey. Scope includes PDVA-REQ-001–019, 034–048 and 054.

An ignored interruption checkpoint records stages, exact receipts, changed files,
blockers and next safe step. It is **not an independent backup**. The single
public evidence PR is the intended preservation path; canonical status requires
independent review/merge verification. Publication or required association failure
means **UNPRESERVED pending recovery PR or association repair**; reuse an existing
PR and never create a duplicate.

## Exact selected configuration and conditional alternatives

R means the unchanged reference product, default `enable_audio=true`, QEMU
manager and no audio package/policy/boot overrides. R-off means explicitly
disabled audio; H means a comparison using the pinned internal virtio-sound
device and a future bounded Android peer. H is not an adopted architecture or
command line. Actual generated release variant, installation and running services
remain U; source selection is distinguished from active-device evidence.

| Layer | Exact selection/caller and mandatory versus conditional status |
|---|---|
| Product inheritance | `vsoc_arm64/phone/aosp_cf.mk` inherits `shared/phone/device_vendor.mk`, which inherits `shared/device.mk`. Without `LOCAL_AUDIO_PRODUCT_PACKAGE`, shared device adds `com.android.hardware.audio` and `android.hardware.audio.parameter_parser.example_service`. Its HIDL comment does not override these build definitions. [product] [phone] [device] |
| Actual audio implementation | The vendor, nonupdatable APEX packages `android.hardware.audio.service-aidl.example` and `android.hardware.audio.effect.service-aidl.example`. `main.cpp` loads audio-policy XML and registers IConfig plus modules; the converter renames XML `primary` to AIDL `default`; `Module::createInstance(DEFAULT)` constructs `ModulePrimary`. This is the default AIDL implementation, not the unrelated HIDL ranchu HAL. [apex] [hal-build] [hal-main] [converter] [module] |
| Init/VINTF | `vendor.audio-hal-aidl` and `vendor.audio-effect-hal-aidl` execute under guest audioserver UID, audio group and other listed groups/capabilities; class hal, restart audioserver on service restart. APEX manifest fragment declares audio.core v4 IModule/default, r_submix, bluetooth and IConfig/default; audio.effect v4 IFactory/default. USB/stub module declarations are commented alternatives. These privileges are guest-local. [init] [vintf] [apex-contexts] |
| Configuration | Unless vendor/copy overrides apply, install `audio_policy_configuration.xml` and `primary_audio_policy_configuration.xml`; include r_submix, Bluetooth/LE policy, legacy volume tables, vendor engine configuration and default AIDL effects. Phone feature declaration includes microphone. Attached Speaker and Built-In Mic are advertised; neither proves hardware. [config-build] [policy] [primary-policy] [vendor-policy] [effects-mk] [features] |
| Ordinary PCM | `ModulePrimary::createInputStream/createOutputStream` selects StreamInPrimary/StreamOutPrimary for ordinary PCM. `StreamPrimary` derives from `StreamAlsaMonoPipe`; default card/device is **0/0**, or parsed `CARD_n_DEV_n` address. Built-In Mic address `bottom` does not parse as that override. `libalsautilsv2` opens through `libtinyalsav2`, whose hardware backend opens guest `/dev/snd/pcmC0D0p` or `pcmC0D0c`. [primary-module] [primary] [primary-header] [mixer-header] [alsa-build] [proxy] [tiny-build] [tiny-hw] |
| Stub selection | Empty connected-device list, telephony/FM/bus cases and boot simulation flags select the stub. `enable_audio=false` emits `androidboot.audio.tinyalsa.ignore_output=true` and `simulate_input=true`. Stub input fills random bytes; it is not absence or permission denial. MMAP input/output and compressed/nonblocking offload select separate stubs even when ordinary PCM is enabled. [bootconfig] [primary] [stub] [primary-module] |
| R virtual device | QEMU manager adds `AC97,audiodev=audio_none` and `driver=none,id=audio_none` unconditionally at this point, independent of `enable_audio`. AC97 emulates PCI 82801AA audio, codec registers, DMA and interrupts. It remains guest-visible with `none`; the backend does not remove the card. [qemu-launch] [ac97] [none] |
| R driver correspondence | ALSA card 0 need not be virtio. If guest `SND_INTEL8X0`/AC97 support binds and enumerates at 0/0, R's primary PCM could use AC97. That installed driver/configuration/card ordering is U. Do not claim AC97 is definitely unused or functional. The inspected virtual-device module directories list `virtio_snd.ko` and `snd-aloop.ko`; no intel8x0 entry there proves neither built-in absence nor presence in another module tree. [intel-driver] [kernel-pci-config] [board] |
| H device/driver | QEMU `VIRTIO_SND` source and `virtio-sound-pci` wrapper, guest `CONFIG_SND_VIRTIO`, SND_PCM/SND_JACK and matching virtio PCI transport form a software mechanism. BoardConfig packages remaining vendor `.ko` files by wildcard, including the listed `virtio_snd.ko`; it is not in the explicit early ramdisk list. Exact load order, kernel ABI/configuration and source-to-prebuilt correspondence remain U. [virtio] [virtio-pci] [q-kconfig] [q-build] [kernel-config] [kernel-card] [board] |
| Existing constrained build | Repository recipe uses all-no-default ARM_VIRT and an empty audio-driver list. Source availability is not a link receipt for AC97/virtio-sound or an Android audio backend. Existing device-closure evidence already lacks virtio PCI. H requires a separately reviewed exact build graph; no rebuild or device-selection change is made. [worker integration](gate-0-qemu-worker-integration.md), [input](gate-0-android17-input-compatibility.md). |
| Separate reference socket | With audio enabled, streamer setup creates pathname `audio_server.sock`, AF_UNIX SOCK_SEQPACKET mode 0666, and supplies its FD to host `webRTC`. It uses the default-instance path in setup. The other VM manager passes `--sound=instance.audio_server_path()`; QEMU does not. This is a specialized virtio-sound peer protocol, not a QEMU AC97 audiodev or guest userspace/vsock forwarding channel. Directory/UID permissions and actual multi-instance binding remain separate. [streamer-launch] [config-instance] [other-launch] [server] |

Service registration does not open a working PCM device. Startup constructs and
registers services before `StreamAlsaMonoPipe::start` opens PCM proxies. Missing
device/failed open can therefore coexist with a registered service. No source
claim establishes that the entire guest boots without all selected dependencies.
Missing specialized peer blocks that separate path; it is not an observed boot
dependency of QEMU R. [hal-main] [mono-pipe] [alsa-base] [proxy]

`driver=none` specifically removes real host input/output from that selected
backend: `no_write` returns rate-controlled consumed bytes, `no_read` clears the
input buffer to format-appropriate silence, and each voice initializes 1024
samples. It retains timers, codec/device processing, DMA and status progression.
It is neither working playback nor guest-visible absence. No PulseAudio/ALSA
host daemon or host microphone is used by this backend. Changing to a different
backend changes the examined configuration and its authority. [none] [ac97]

## Playback responsibility trace and stream contract

```text
Guest app media / AudioTrack
  -> guest AudioFlinger playback/mixing thread and HAL adapter
  -> AIDL IModule/default, StreamOutPrimary, command/reply/data FMQs
  -> MonoPipe + ALSA I/O thread -> libalsautilsv2 -> libtinyalsav2
  -> guest PCM device and matching kernel driver
  -> R: AC97 -> QEMU none backend -> consumed/discarded (no presentation)
     H: virtio-sound -> hostile VM/audio worker -> [missing bounded adapter]
        -> [proposed trusted admission/copy receiver] -> host AudioTrack
        -> host Android audio policy/service/HAL -> permitted output route
```

The two H brackets are H, not source-present PDVA components. Guest and host
AudioFlinger are different system services in different operating systems. The
inspected guest framework opens output through its HAL device interface and
writes through its playback thread; AIDL factory resolves declared modules.
Host `AudioTrack` is relevant only after a receiver has validated and owned PCM.
It does not implement a virtual sound card or authenticate a worker. [flinger]
[threads] [factory] [track]

| Contract | Source behavior and unresolved obligation |
|---|---|
| PCM and endian | Primary policy advertises signed PCM16, 8000/11025/16000/32000/44100/48000 Hz, mono/stereo for ordinary input/output. HAL conversion maps INT_16_BIT to S16_LE; ARM64 is little-endian. Interleaved stereo PCM16 is four bytes/frame, mono two. Formats in generic converter code are not all selected-policy formats. [primary-policy] [alsa-utils] |
| H negotiation | QEMU advertises S8/U8/S16/U16/S32/U32/FLOAT and rates 5512 through 384000 from an explicit bitmap; default two streams split output/input, two channels, S16/48 kHz, buffer 8192 and period 2048 bytes. These defaults are not PDVA targets. Guest driver intersects advertised rates/formats/channels and sends SET_PARAMS/PREPARE/START/STOP/RELEASE through virtqueues. Matching PCM16 stereo/48 kHz is a source intersection, not proof of every HAL-advertised rate/channel tuple. [virtio] [kernel-pcm] [kernel-ops] |
| Buffer sizing/alignment | AIDL Module checks minimum frame count, zero frame size and maximum-byte division before constructing FMQs; data queue is frame-size times buffer frames. ALSA builtin profile derives period size from buffer frames, period-count and multiplier properties. Exact generated values and total allocations are U. A future receiver must independently check frame-byte multiplication, alignment, offsets and aggregate quotas before allocation/copy. [module] [alsa-profile] |
| Latency/clock | HAL nominal standard latency is 85 ms (comment relates it to 4096 frames at 48 kHz); MMAP nominal 10 ms is attached to a stub. Neither is measured latency or an approved budget. Primary synchronous transfer sleeps or skips to follow uptime; `refinePosition` leaves framework-counted position because not all data reaches ALSA. Host clock, guest clock, resampling drift, timestamp discontinuity and acoustic presentation remain U. [primary-module] [primary] |
| Partial writes/underrun | Primary MonoPipe output drops unwritten remainder, yet reports requested frame count; its I/O thread logs failed ALSA writes. Input short reads insert silence. Primary may skip a transfer and still count it, zeroing skipped input. Proxy retries EIO/EAGAIN up to the supplied count (three here). Successful reported frame progress is not proof of full presentation or actual capture. [mono-pipe] [primary] [proxy] |
| Start/pause/resume/stop | Start opens proxies and creates I/O threads; existing proxies allow resume. Base pause/flush return OK without an independent host drain barrier. Standby/shutdown stop PCM, shut down input pipes and join threads. Primary input flush invokes standby. These are cooperative guest lifecycles, not hostile-host cleanup proofs. [mono-pipe] [alsa-base] [primary] |
| Volume/mute | Guest framework mixing, HAL gain application and PrimaryMixer controls are distinct from host track volume/system mute. HAL mixer control availability/errors must be checked. A silent muted stream remains a stream, not Empty/Deny. A future receiver owns permissible host gain/routing and must reject worker requests to change global volume or capture state. [alsa-utils] [mixer] [primary] [track] |
| Concurrent streams | AudioFlinger can mix guest app tracks; HAL streams, PCM substreams and VM stream IDs are different counts. QEMU defaults to one output/one input; reference streamer has configurable output streams and mixing. Multiple independently opened HAL streams against 0/0 require actual driver/substream agreement. No unlimited-concurrency or latency claim. [threads] [virtio] [streamer-main] [audio-mixer] |
| Disconnect/restart | Kernel remove/freeze and PCM error paths, guest service restart, VM loss and host AudioTrack dead-object recovery are separate. Recreating a host track must require fresh external instance/epoch admission and discard queued old samples. A connected socket or restarted daemon is not recovery authorization. [kernel-card] [tiny-pcm] [track] |
| Host lifecycle/routes | Public API supports blocking/nonblocking writes, pause/stop/flush, routing listeners and preferred-device requests. Writes can be short or fail; preferred route is not guaranteed. Audio focus, foreground/background policy, Bluetooth changes and system mute may suppress/reroute playback independently of guest success. Host support and synchronization with guest state remain U. [track] [manager] |
| Resources | Budget guest RAM/FM Qs/MonoPipes, ALSA buffers, VM descriptor queues, shared audio objects, receiver-owned copies, host track buffering, threads, resampling CPU and descriptors together. Per-buffer sizes or a queue length do not supply an independently enforced total memory/CPU/FD cap. The existing Android memory-limiter and worker-lifetime Unknowns remain. |

For apps targeting API 35 or later, current Android documentation restricts audio
focus requests to the top app or a foreground service. Loss can cause system
fade/mute; a future host owner must handle focus rejection/loss and background
transition explicitly. A mediaPlayback foreground service has its own declaration
and lifecycle requirements; none is added here. Bluetooth/system route control
remains with the host OS; no guest Bluetooth HAL grant implies host Bluetooth
authority. [Audio focus](https://developer.android.com/media/optimize/audio-focus),
[foreground service types](https://developer.android.com/develop/background-work/services/fgs/service-types).

## Separate host peer and capture path

S: `AudioServer::AcceptClient/Create` accepts the Unix connection, allocates two
262144-byte memfds (caller-selected here), maps them RW/MAP_SHARED, creates three
SOCK_SEQPACKET pairs, and sends **five FDs**: event/TX/RX endpoints and TX/RX
shared-memory objects. This is not a stream of PCM bytes on one socket, nor the
general vhost-user RAM-table protocol. PCM control headers use explicit
little-endian wrappers; shared buffers/signaling structures have their own ABI.
`BufferAt` checks bounds with a fatal CHECK. The server allocates a query reply
from untrusted `info_count` before the executor's stream-range validation.
Consequently fixed shared areas do not establish bounded hostile-client memory
or graceful malformed-input handling. [server] [shm]

S: `AudioHandler` runs command, playback and capture handling; accepts a new
client in an endless loop and joins peer threads after command loss. Prepare and
release validate stream index then reply OK; start/stop toggle active state.
Inactive playback is acknowledged with full consumed length while ignored.
Status sending is nonblocking; a failed/short reply is logged, not proven
delivered. The capture handler obtains a stream-descriptor reference before its
range check; this is another reason not to promote it into a trusted hostile-VM
receiver. These are source review findings, not executed exploits. [audio-handler]
[server]

S: playback goes to AudioMixer and a WebRTC audio track source. Capture calls
`audio_source_->GetMoreAudioData`, which reaches the custom
`CfAudioDeviceModule::GetMoreAudioData` and WebRTC `NeedMorePlayData` callback.
That is received client audio, not an Android host AudioRecord acquisition.
When the callback/playout is absent, the custom source reports muted and the
handler fills silence. Error branches can still send OK/full length. No PDVA
consent, Persona epoch or per-instance capture authorization exists in this
path. Actual client microphone acquisition/permission and complete upstream
media dependency graph are U here. [audio-handler] [streamer-main] [streamer]
[audio-device] [audio-mixer] [audio-track-source]

The peer build is host `webRTC` plus `libcuttlefish_audio_connector`, using
Cuttlefish host defaults, WebRTC, codecs/resampling, protobuf/config, shared-FD
utilities and other non-audio launcher facilities. This is not an Android-app
library closure. Its socket pathname and 0666 mode neither authenticate an
instance nor override DAC/SELinux. Importing the host launcher would also retain
the separately documented privileged Linux VM dependencies. No privileged audio
daemon is intrinsically required by an internal PCM software device, but this
host process bundle is not an approved ordinary-app audio peer. [peer-build]
[connector-build] [host-defaults] [qemu-launch]

Capture direction, for a future authorized design, is:

```text
host user + system authorization + PDVA scoped Real decision (all required)
 -> trusted capture owner / host AudioRecord (hypothesis; never worker-owned)
 -> bounded copied samples, current instance/stream/epoch admission
 -> hostile audio device input -> guest ALSA/HAL -> guest AudioFlinger
 -> guest app (subject to its separate guest recording permission)
```

| Mode/interface | What source supports; policy consequence |
|---|---|
| Real | Ordinary host AudioRecord requires RECORD_AUDIO and actual system recording admission. AudioPolicyService checks input permissions and `startRecording` before starting input. Host permission alone is not user consent for a particular PDVA disclosure or Persona authorization. Actual host capture is **NOT RUN**. No real microphone route is provided by R's none backend. [record] [record-policy] [none] |
| Decoy | Source supplies synthetic paths: QEMU none returns silence; HAL simulation returns pseudo-random bytes. These demonstrate non-Real generation, **not** a coherent Persona microphone provider or its enforcement. A deliberate deterministic/scoped synthetic provider and failure semantics remain U. [none] [stub] |
| Empty | Advertised Built-In Mic plus silent successful recording is not legitimate absence. Exact method-specific absence, feature/configuration consistency and app-visible outcome are U. Removing input streams or the microphone feature changes configuration and needs review; not done here. [features] [primary-policy] |
| Deny | Guest Android can deny its app recording permission; host system can deny recording. PDVA denial must independently prevent host acquisition/disclosure even if the guest grants permission. The exact guest-visible error contract under a PDVA deny remains U. [record-policy] |
| No input stream | QEMU's configurable stream count permits an output-only device (one stream is assigned output), but R advertises microphone and H's default has input. Output-only transport is not automatically a compatible selected phone or method-specific Empty. No change selected. [virtio] |

Five boundaries stay separate: guest permission, host app permission, host user
consent for this operation, PDVA Persona policy, and system-enforced recording
admission. None substitutes for another. Current microphone foreground-service
rules require RECORD_AUDIO, the microphone service type/permission when using
that service, and while-in-use eligibility; a background start is restricted
except defined exceptions. This is an authority constraint, not permission to
request a grant or exploit an exception. [Microphone foreground service](https://developer.android.com/develop/background-work/services/fgs/service-types#microphone).

I/H: Real can be withheld prospectively by keeping the acquisition API/objects
and all raw capture handles in an external trusted owner which refuses creation
and sample delivery unless all boundaries authorize the current scope. Host
system permission/AppOps and kernel/SELinux enforce their own boundaries; PDVA
must enforce its finer policy outside the worker. No unrestricted AudioRecord,
AudioManager, Binder/service proxy, host audio FD, other-app capture, manager
database, Persona master, credential, signing object or peer-instance object may
be delegated. Grant-free/Decoy/Empty/Deny operation must never fall back to Real.
Silencing in a compromised worker cannot enforce this. Complete PDVA enforcement
remains U, including direct-service/deputy paths and independent worker confinement.

## Ordinary-app authority and ownership matrix

| Component/resource | Authority classification | Actual or proposed owner; remaining limit |
|---|---|---|
| Host AudioTrack PCM playback in own app | **Ordinary installed-app** API, conditional lifecycle/focus/routing | H trusted audio receiver owns track, bounded copies, backpressure and focus; worker gets only a narrow data endpoint. No existing adapter. |
| Host AudioRecord microphone | **Ordinary installed-app with explicit permissions/system admission**, not ambient authority | H trusted capture owner with visible scoped consent, instance binding and revocation. Worker ownership is prohibited by PDVA. Full enforcement U. |
| Host AudioFlinger/device HAL control and `/dev/snd` | **Privileged/system/platform policy**, **unsupported** ordinary direct route | Host OS owns services/HAL/device. Appdomain audio-device access is prohibited in inspected policy; HAL server has explicit device access. Guest service UID/capabilities do not transfer to host. [app-policy] [hal-policy] [uevent] |
| Guest audio HAL, init, Binder/FMQ and ALSA device | **Guest-local system authority**; host privileges not implied | Guest OS owns service/stream lifecycle and sample buffers; entire guest remains hostile to host. Guest normal boot, generated VINTF and labels U. |
| Internal emulated AC97/virtio sound | **Conditional ordinary-app software mechanism** | Hostile VM worker owns guest memory/device state; installed native execution/build authority remains U from prior Gate 0 evidence. No direct host device needed by these algorithms. |
| Specialized Unix peer and five transferred FDs | **Unknown** complete ordinary Android packaging/transfer/SELinux contract | Reference launcher/server own pathname, memfds and sockets. Proposed bounded endpoint ownership cannot be inferred from reference names/modes; host-only build is not an Android app target. |
| Global route/focus policy, other-app audio capture, audio daemon ownership | **Privileged/system**, some route behavior **OEM-dependent** | Host OS owns global policy; public requests are limited app operations. No arbitrary service passthrough, privileged broker or daemon ownership adopted. |
| Shell grants, root device opens or development launch controls | **Root/development/shell-only; unsupported** product route | Excluded, not an alternative proof. No phone, ADB or permissions operation performed. |
| Instance/epoch, Persona policy, protected state | H trusted management plus external admission boundary; actual enforcement **Unknown** | Authorize against trusted enrollment, not worker-provided IDs. Protected state stays outside every hostile mapping and process. |
| Independent termination, aggregate CPU/RAM/FD quotas | **Unknown** complete ordinary-app enforcement; privileged fixes unsupported | Host OS is ultimate authority; management must retain uncertainty/lockout without a scope-complete witness. Existing lifetime/memory findings remain unresolved. |

## Hostile-worker boundary obligations

These are required H contracts, not a bridge implementation. Treat the guest,
engine and audio backend as arbitrary native adversaries. Do not trust their
format declarations, timestamps, stream-close callbacks or “played” receipts.

- Admit a fixed operation vocabulary and allowlisted PCM formats/rates/channels.
  Check signedness, overflow, frame alignment, range containment and lengths before
  allocation. Bound individual frames, queued duration, stream count, descriptors,
  total memory and work/CPU. Malformed data must receive bounded rejection, not
  an unbounded allocation or trusted-process fatal CHECK.
- Authenticate the endpoint through trusted enrollment and bind each operation
  to instance, direction, stream and epoch. Worker-supplied IDs alone confer no
  authority. Bind capture recipients before acquisition and again at delivery;
  do not let a shared “default instance” name select an authorized recipient.
- Copy admitted bytes into receiver-owned bounded memory before passing to the
  host audio API. Read-only mapping is not immutable memory: a hostile writer can
  change shared PCM during copying. An owned copy stabilizes subsequent use but
  does not prove coherent/honest guest samples. Neither permits sharing protected
  objects, unrestricted FDs, extra mappings or a general file opener.
- Backpressure must bound queue growth and blocking. Explicitly choose and account
  for dropping, rejection and discontinuity; do not report acoustic presentation
  from successful enqueuing. Guest timestamps cannot schedule unbounded future
  playback or evade quotas. Clock reconciliation/resampling needs its own evidence.
- On policy/Persona change, reject the old epoch, stop future capture admission,
  discard pending captures and queued old playback according to an explicit
  commit barrier. Already handed-off host buffers and previously disclosed samples
  cannot be recalled by changing an ID. Account for in-flight work and capture
  device closure separately from stopping future delivery.
- Manager loss defaults to no new protected operation; uncertain state blocks
  reauthorization/reuse. Worker death, EOF, Binder death or a close acknowledgement
  does not prove every process, duplicated FD, queued transfer or retained mapping
  ended. Never move capture into the worker to avoid this problem. Maintain
  CleanupUnknown where independent closure is missing.

The prospective TCB includes trusted admission/copy/capture code, protected policy
storage, host kernel/SELinux/Binder and Android audio services. Any new receiver
placement or trusted parser enlarges that TCB and needs reviewed authority evidence.
This record does not authorize a new process/broker architecture. The reference
peer's query-allocation, fatal-check, mutable-buffer and reconnect behavior does
not satisfy these obligations. Existing [display ownership](gate-0-host-display-boundary.md)
and [revocation](gate-0-capability-revocation.md) distinctions apply to audio bytes
without repeating those surveys.

## Source-grounded negative controls and falsifiers

All rows are **NOT RUN**. “Reject” below is the proposed proof's falsifier, not
an observed passing denial. Use independent host presentation/resource witnesses
in any later separately authorized experiment; no microphone recording is
authorized by this table.

| Condition | Actual source behavior / precise falsifier | Status |
|---|---|---|
| HAL selected, device missing | Service registration precedes PCM start; proxy open fails. Reject any complete-path claim based only on service listing. [hal-main] [proxy] | NOT RUN |
| Sound card exists, output disabled | R none backend consumes bytes without presenting. A guest progress counter cannot pass audible playback. [none] | NOT RUN |
| Missing/mismatched kernel driver | AC97 needs matching PCI driver; virtio needs SND_VIRTIO/transport and module ABI. Missing binding or wrong card/PCM tuple rejects pairing. [intel-driver] [kernel-card] | NOT RUN |
| Service registers but cannot play | Stub/MMAP/offload can return progress without real PCM. Require independently witnessed presentation for the exact selected stream. [primary-module] [stub] | NOT RUN |
| Required socket/peer absent | Specialized server accepts a client and exchanges FDs; QEMU R never connects it. A listener alone cannot establish a path. [server] [qemu-launch] | NOT RUN |
| Wrong socket/stream identity | Reference pathname/index checks are not PDVA identity. Delivery from wrong endpoint, instance or epoch rejects isolation even with valid PCM. [streamer-launch] [audio-handler] | NOT RUN |
| Unsupported rate/channel/format | Policy and device bitmaps differ; handler validates some parameters. Any unnegotiated interpretation or silent reinterpretation rejects compatibility. [primary-policy] [virtio] [audio-handler] | NOT RUN |
| Malformed/oversized buffer or query | Server checks shared ranges fatally and allocates query count before range validation. Trusted crash/unbounded allocation rejects bounded receiver; no synthetic success oracle. [server] | NOT RUN |
| Partial write/dropped frames | MonoPipe drops remainder and reports requested count. Independent missing frames invalidate complete-presentation inference even with OK reply. [mono-pipe] | NOT RUN |
| Backend stalls, framework advances | Primary skips/counts transfers; output I/O logs failures. Unbounded queues/blocking or hidden loss falsify proposed bounded-progress contract. [primary] [mono-pipe] | NOT RUN |
| Output route/device/Bluetooth changes | Public track routing may change; preferred route is only a request. Continued unauthorized route or stale-route claim rejects host contract. [track] | NOT RUN |
| Host focus lost | Focus and system fade/mute are independent of guest. Continuing contrary to declared focus policy or treating guest success as audible rejects claim. [manager] | NOT RUN |
| Host app backgrounded | Foreground-service/focus/recording eligibility applies independently. Unapproved keepalive, permission workaround or continued unauthorized capture rejects ordinary-app design. [record] [manager] | NOT RUN |
| Guest recording permission granted, Persona denies Real | Guest permission has no host-policy authority. Any real-host acquisition/delivery after denial falsifies boundary. [record-policy] | NOT RUN |
| Host permission granted, policy Decoy/Empty/Deny | Permission availability is not PDVA authorization. Any Real samples or acquisition in these modes falsify fail-closed behavior. | NOT RUN |
| Provider fails and starts genuine capture | Reference simulation/none does not require a microphone; no Real fallback is allowed. Creating AudioRecord or forwarding genuine samples as recovery rejects policy. [none] [stub] | NOT RUN |
| Stale samples after Persona change | Shared areas and holding buffers retain samples; no reference Persona epoch exists. Old-epoch delivery after the defined barrier rejects revocation. [server] [audio-handler] | NOT RUN |
| Worker survives nominal stop with FD/capture access | Close/ack/death is not whole-scope revocation. Independent continuing protected operation or premature reuse rejects containment. [revocation](gate-0-capability-revocation.md) | NOT RUN |
| Capture reaches another instance | Reference default-instance socket and stream IDs are not authorization. Wrong-recipient disclosure rejects boundary even if media is well formed. [streamer-launch] | NOT RUN |
| Guest reports success without presentation | None, stubs, skipped transfers and inactive-stream OK are concrete false-positive controls. Require evidence downstream of host admission/actual presentation. [none] [primary] [audio-handler] | NOT RUN |

## Build, provenance, licenses and remaining correspondence

Guest artifacts are ARM64 Android vendor APEX/services, framework, generated AIDL
NDK interfaces/FMQ and XML-schema code, TinyALSA v2/ALSA utilities, PCM drivers
and configuration. `libaudioserviceexampleimpl` includes primary/ALSA/stub/USB/
Bluetooth/submix paths and uses libbinder_ndk, libfmq, libnbaio_mono, audio
conversion/utilities, libxml2 and the other declared native edges. A package name
does not close their generated version/link graph. The product also selects
`android.hardware.audio.parameter_parser.example_service` and enables
`ro.audio.ihaladaptervendorextension_enabled`. The framework wrapper then waits
for `IHalAdapterVendorExtension/default` when resolving that extension. This
is another service dependency, not the PCM transport. Its implementation,
init/VINTF and generated link closure remain **UNKNOWN** in this receipt set;
the similarly named default effects `extension` directory does not establish
the parser's implementation. [hal-build] [device] [factory]

The selected APEX explicitly packages `liberaser` and
`audio_eraser_classifier_model` / `audio_eraser_separator_model`.
Framework build definitions map these to `models/classifier.tflite` and
`models/separator.tflite`, and liberaser depends on libtflite and TensorFlow/
FlatBuffer headers. Apache-2.0 module/NOTICE declarations were inspected, but
model-generation inputs, reproducibility, per-artifact provenance and full
transitive rights are **UNKNOWN**. They are required packaging edges of this
unchanged APEX, not established mandatory signal-processing operations for basic
PCM. No assertion that they are proprietary is supported; no assertion of
complete corresponding source or permission to omit them is supported either.
No model, ROM, SDK archive or opaque payload was downloaded. [apex]
[eraser-build] [eraser-notice] [effects-config]

Host artifacts are different: the reference peer is `cc_binary_host`, and QEMU
requires a compatible Android/Bionic target, selected sound objects and a real
host backend/adapter. Existing cross-link/toolchain receipts do not provide
that audio build, executable authority, 4/16-KiB compatibility or supported
host minimum. The guest API level is not the host minimum. No new build/link
or ELF inspection is represented as completed.

| Source family / per-file notice scope | License observation and obligation before any adoption |
|---|---|
| Cuttlefish source/build/config and AOSP HAL/framework/ALSA utilities | Inspected code/XML headers or nearest Android.bp license declarations generally specify Apache-2.0; retain applicable notices, identify modifications and audit transitive terms. TinyALSA v1 is not substituted for selected v2. No blanket image redistribution approval. |
| TinyALSA v2 PCM and build/NOTICE | Source headers and NOTICE carry BSD-style redistribution conditions; preserve exact notices and disclaimer. Complete compiled closure still requires review. [tiny-build] [tiny-pcm] [tiny-hw] [tiny-notice] |
| Kernel sound sources | Virtio source files/Kconfig carry GPL-2.0+; intel8x0 has GPL terms. Kernel/module correspondence, configuration, compiler and corresponding-source delivery remain required; listing a `.ko` name is not an ABI or rights certificate. |
| QEMU sound files | virtio-snd is GPL-2.0-or-later; AC97 and none contain permissive notice text, while the complete QEMU distribution has its own GPL and file-specific obligations. Preserve file notices and full corresponding source/build changes where required. No QEMU binary adopted. |
| Models, WebRTC/codecs, generated inputs, toolchain and other transitive sources | Individual model provenance and full dependency/license/reproducibility closure U. Host build labels and source availability do not establish ordinary-app packaging or redistribution approval. |

Only original evidence text and an index entry are published. No upstream
implementation, new dependency, native binary, permission, workflow change or
security relaxation is introduced. Any future adoption needs named maintenance,
vulnerability response, exact revisions/patches and build/notice ownership under
[source policy](../source-provenance-policy.md). No opaque component is promoted
into the TCB by this investigation.

## Validation, limits and next independent proof

Local foundation validation passed (135 files, 83 Markdown documents,
54 requirements, two ADRs), and harness validation passed. Repository tests
ran 141 cases: 137 passed and four Windows-inapplicable cases skipped.
Desktop-readiness tests passed 27/27, offline-image tests 45/45 and frame-copy
tests 4/4. The receipt verifier rehashed all 99 retained text receipts and
checked 84 published references, including matching QEMU receipts against
immutable local Git blobs. `git diff --check` passed. Existing Linux-native
controls were not rerun on Windows; their baseline CI evidence is separate.
Source receipts are hashes of exact downloaded text bytes, not runtime artifacts.
Manual review covers immutable references, full two-file diff, local links,
UTF-8/whitespace, regular text modes, dependencies/licenses and public-data hygiene.
No private paths, host identifiers, accounts, credentials or Persona secrets are
needed in public evidence.

**NOT RUN:** Android/guest build, QEMU/VM/emulator execution, APK installation,
phone/USB/ADB, microphone permission request, capture/recording, acoustic
presentation, runtime service/driver enumeration, focus/route tests and every
negative control above. Hosted CI for this PR is **pending/unobserved**; the
baseline logs are separate. No synthetic audio “tests” were added to check a
hand-authored table against itself.

The smallest independent pre-build falsifier is a reviewer-reproduced selection
closure for **one** explicit PCM route: no stub properties/stream flags, exact
AIDL module/configuration, 0/0 mapping, matching kernel driver/config/module ABI,
and the selected QEMU sound/backend source objects. Reject immediately if it
still terminates in `none`, a stub, an absent driver or the unrelated socket.
Then require a concrete source-level bounded endpoint/ownership specification
that retains no host microphone/API authority in the hostile worker, defines
all epochs/queues/loss barriers, and resolves the selected model/prebuilt graph.
Missing source or a requirement for privileged host audio falsifies that proposal.
Do not build first and infer the contract from a successful demo.

Only after those findings and the existing Gate 0 prerequisites are reviewed
could separately authorized bounded runtime work examine actual presentation
and enforcing host denial with independent witnesses. No such work is authorized
here. Material architecture/process/trust/capture-policy changes require a reviewed
ADR and Tony's explicit approval. **SCOPED STOP** for unchanged functional audio
and dependent construction; **CONDITIONAL** software/ordinary-playback lead;
complete correspondence, containment and authorized Real capture **UNKNOWN**.
Gate 0 remains **Unresolved**; Gates A–G remain **Not reached**.

## Immutable source receipts and reproduction

The ledger below is generated from rehashed retrieved source bytes. Gitiles URLs
use full commits and `?format=TEXT` base64 decoded without newline conversion;
QEMU uses raw GitHub bytes. Cuttlefish, hardware/interfaces, frameworks/base,
frameworks/av, system/media and TinyALSA v2 release identities were independently
resolved from `android-17.0.0_r1`; kernel/QEMU and remaining identities retain
the merged ledgers' explicit provenance scope. Kernel source is a correspondence
lead, not proof of the prebuilt module's source. Module-directory JSON at
`e6673fcbd05e63e6fcc2c2d2cf33246108b73b0c` was inspected for root and `16k`
names only; no module payload was acquired.

Initial guessed shared-audio, bootconfig, HAL-primary, ALSA and audio-device paths
returned 404. Directory/build/manifest discovery located the actual paths and
the separate `external/tinyalsa_new` v2 project. Those failed guesses are not
evidence of component absence. Current Android website guidance above is mutable
documentation consulted on the review date, not an immutable OEM manifest.

| Receipt | Immutable source | SHA-256 |
|---|---|---|
| product | [vsoc_arm64/phone/aosp_cf.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/phone/aosp_cf.mk) | `ba74bdb141f2346a53b516fecb9cda9337c903185cdf7b4603b25a7293c77579` |
| phone | [shared/phone/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk) | `69645517941d7013eb798376faeee588cc86f9bfd117dd5eecd27b250b6ad176` |
| device | [shared/device.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/device.mk) | `cfd71dfa943e83cb96d64f9cd8e1e1331b2fedca8719b37e1eed372b44876355` |
| board | [shared/BoardConfig.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/BoardConfig.mk) | `681ae40db963fbdcd59644f8d74fa16013c55e5f09127031c6dfdbe4e0b0df70` |
| apex | [audio/aidl/default/apex/com.android.hardware.audio/Android.bp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/apex/com.android.hardware.audio/Android.bp) | `d998859f94c2152732132eeb2d814845c01f2bd1664997a82e2813dea8a796d1` |
| hal-build | [audio/aidl/default/Android.bp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/Android.bp) | `bc49f4cec84035cb086a0d73e53bf35e1c72fa3a0ade2460eb834a1399066755` |
| hal-main | [audio/aidl/default/main.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/main.cpp) | `7b8c71833b5088e46f5033dd82f3e240288ee642d5f969ca4eb71e84f9f7a8f6` |
| converter | [audio/aidl/default/AudioPolicyConfigXmlConverter.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/AudioPolicyConfigXmlConverter.cpp) | `2176aa4b1db681683a2d9bab5645a388dedbedee00968cb21f63403f6dc1f015` |
| module | [audio/aidl/default/Module.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/Module.cpp) | `bdc2914a2787b40c6148c7e16ded18001b66d74a6b132745299ab08030265233` |
| init | [audio/aidl/default/android.hardware.audio.service-aidl.example.rc](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/android.hardware.audio.service-aidl.example.rc) | `5096f6cadf1bb27e4cfc54d31e34f743c4b64eae4f72a3f6115818a3b94868c5` |
| vintf | [audio/aidl/default/android.hardware.audio.service-aidl.xml](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/android.hardware.audio.service-aidl.xml) | `f2a6fd326cf77b4219a4d2db89b1172d40c3b3fef081e9c9dc7eb2386fe82019` |
| apex-contexts | [audio/aidl/default/apex/com.android.hardware.audio/file_contexts](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/apex/com.android.hardware.audio/file_contexts) | `3dfe6070d52d7a3457e2cfd5948227b04a23db03a91d29b461a55be7a4096a47` |
| config-build | [shared/config/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/Android.bp) | `f991a5cc35d3bd2edf35160279808a4b6f25ba8e3020494629b363437673c8cb` |
| policy | [shared/config/audio/policy/audio_policy_configuration.xml](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/audio/policy/audio_policy_configuration.xml) | `7b5981137bcf324d1f66d331a134a4facbba758622c4567ec310eb7b26719022` |
| primary-policy | [shared/config/audio/policy/primary_audio_policy_configuration.xml](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/audio/policy/primary_audio_policy_configuration.xml) | `cffc32aa4eee6a8c0c5071711247ab4bd03c053b73df1241f7e2b53a304fe5ca` |
| vendor-policy | [services/audiopolicy/audio_policy_config_vendor_1.mk](https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audiopolicy/audio_policy_config_vendor_1.mk) | `a50e94e66a46845f5091b66fda181753349b65155b68eb82be939c62d96cef06` |
| effects-mk | [audio/aidl/default/audio_effects.mk](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/audio_effects.mk) | `a9df1799ea83c622b59040c1f12edc8f07d33338d3c3db919766a45d2be54ca0` |
| effects-config | [audio/aidl/default/audio_effects_config.xml](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/audio_effects_config.xml) | `834bd23e17a980ba81cddfa72c44871fd39e4df95a26c78aa477fdfcada3a8d5` |
| features | [data/etc/handheld_core_hardware.xml](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/data/etc/handheld_core_hardware.xml) | `8dbd117a8c9a908a65cb43973d8d40504512c0afa1a220404fb14b1e552bf138` |
| primary-module | [audio/aidl/default/ModulePrimary.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/ModulePrimary.cpp) | `38a3899c72fc1935299712bf0800c14ce8dc86e93330fd61e2af1257240bdf60` |
| primary | [audio/aidl/default/primary/StreamPrimary.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/primary/StreamPrimary.cpp) | `f547f764270d89849ad31e04588d10eaa3f99dbfee7cdcd9d7904182be308cd5` |
| primary-header | [audio/aidl/default/include/core-impl/StreamPrimary.h](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/include/core-impl/StreamPrimary.h) | `f5e4d6bf737835b471b9a228e8060472cea5d814e72d17f03ed219afa5185ac9` |
| mixer-header | [audio/aidl/default/primary/PrimaryMixer.h](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/primary/PrimaryMixer.h) | `ea352ed244ac999f020d5aa105201ae30938f99633fbcd6c02ad963c7b0f2789` |
| mixer | [audio/aidl/default/alsa/Mixer.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/Mixer.cpp) | `3969577ffa54f4db69aa751475ae4e857addfcaaf788a97b382a42527643103b` |
| mono-pipe | [audio/aidl/default/alsa/StreamAlsaMonoPipe.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/StreamAlsaMonoPipe.cpp) | `e64ea5ea74bb1e8a0f6bff4228c365fe43358ceda0e01596fd993faf2ea30324` |
| alsa-base | [audio/aidl/default/alsa/StreamAlsaBase.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/StreamAlsaBase.cpp) | `7c970dc5c703ec995c457a7a0a3eb1db73560426d072721bd88c8d9730653d01` |
| alsa-utils | [audio/aidl/default/alsa/UtilsAlsa.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/UtilsAlsa.cpp) | `e90f1619e94e7dbfc2b7e65ab8a7089385777a7cb0202b857a76ea21c10e92cc` |
| alsa-build | [alsa_utils/Android.bp](https://android.googlesource.com/platform/system/media/+/440eb272fd3da0ca7bdae932e61e7fd9be1fd324/alsa_utils/Android.bp) | `def7d4b8f234dda77e148722a89779caba321eb4440fa77cdd50c94e8910644f` |
| alsa-profile | [alsa_utils/alsa_device_profile.c](https://android.googlesource.com/platform/system/media/+/440eb272fd3da0ca7bdae932e61e7fd9be1fd324/alsa_utils/alsa_device_profile.c) | `a5ee98aa3329ee080b9abe9fc098d44d9f85a99fc0bedcd7dacc0e49cc5b3632` |
| proxy | [alsa_utils/alsa_device_proxy.c](https://android.googlesource.com/platform/system/media/+/440eb272fd3da0ca7bdae932e61e7fd9be1fd324/alsa_utils/alsa_device_proxy.c) | `1a3ee158136d4d18a1fa401ca4bd24dfb770f4ab53397002801ba1b06a556969` |
| tiny-build | [Android.bp](https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/Android.bp) | `565f447f3398821ea3d743786f73e0e6fe06fa1afedf5528a3891bd14d384bd9` |
| tiny-pcm | [src/pcm.c](https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/src/pcm.c) | `c6f79c09ddaef501f7f0df99d0d666ac1c3d78deda3e68033e5d2d9d7d9427cd` |
| tiny-hw | [src/pcm_hw.c](https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/src/pcm_hw.c) | `d7404b9870ef77536928bfa063ccb744a96460c2d80197ee524efd52dadb19b8` |
| tiny-notice | [NOTICE](https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/NOTICE) | `1401e1769d37424806c1f453124a7220b7fe544c82cdc68d3137c64451baf61e` |
| bootconfig | [host/commands/assemble_cvd/bootconfig_args.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/bootconfig_args.cpp) | `64a5a2be99fa76080a16c45ba38831c264472ff3d882aa4bb9d79eb687d62117` |
| defaults | [host/commands/assemble_cvd/flags_defaults.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags_defaults.h) | `c2f95f666070036d10c9160d11fcc080a864c4df3da60d98747bdadfcb5f310a` |
| flags | [host/commands/assemble_cvd/flags.cc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags.cc) | `52ba2555c01639b68dfc348fce73124e4b7afa35d82a93e0b1a58c6c59254de9` |
| stub | [audio/aidl/default/stub/DriverStubImpl.cpp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/stub/DriverStubImpl.cpp) | `d3090f75f9b4752d1ebb8e80766f33c152f5ea7f7fc8f7ae66daa0674d1a2f47` |
| qemu-launch | [host/libs/vm_manager/qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` |
| ac97 | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/ac97.c](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/ac97.c) | `8a6c7481850e2ef4abbf9d68a080ad9dc6d0a2cfc29119c7db01ea6db79200b5` |
| none | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/noaudio.c](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/noaudio.c) | `61642224c5e079dc39f8a71cf45b9f86b47b637e559bef841aa3b4005900d110` |
| virtio | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/virtio-snd.c](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/virtio-snd.c) | `fe33f3fdf897c98cb1cceae49121f0d28ea3ae783523c41e8a9b9a3af37ec821` |
| virtio-pci | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/virtio-snd-pci.c](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/virtio-snd-pci.c) | `8778ea2514738f6b5e1f59d409e2959ffdf09ec79cc3b1dd1fe4f5b48048f0c9` |
| q-kconfig | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/Kconfig](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/Kconfig) | `dcf1725b7cf96c0eec4707c262a2bc1d28b54754707b2aa1b91b4b8acd184180` |
| q-build | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/meson.build](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/meson.build) | `860cd5d42c8efa4aacd10af6d5e86bc9804c6f8046cb58755f4eeb8e3c1fe2c5` |
| q-audio | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/audio.c](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/audio.c) | `df8074f45258364dcdd4da4258d0caf0eab623fc0338132cb7f046171765467e` |
| q-audio-build | [4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/meson.build](https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/meson.build) | `9d0e35cba851d385f8d08ed37a5dfacf4f0678209a3671fa39a0a83643981243` |
| kernel-card | [sound/virtio/virtio_card.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_card.c) | `1d431b4f8529f46edead3b82db6ec671880a3b97c7e6886736878ed5b899b0f8` |
| kernel-pcm | [sound/virtio/virtio_pcm.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_pcm.c) | `198a67ea57655c4ba32d057c81418396d86f8b27a81f9757a452ce3fc21c1687` |
| kernel-ops | [sound/virtio/virtio_pcm_ops.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_pcm_ops.c) | `f2b31587bb66b540ce1109a985ac0702209d1bfd376de90fc6430ca21dc83c87` |
| kernel-msg | [sound/virtio/virtio_pcm_msg.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_pcm_msg.c) | `c0595e352cea83d5247a9e6f5d4ef0f599cf72030aa81a7e2c19e42c24d6c4f1` |
| kernel-config | [sound/virtio/Kconfig](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/Kconfig) | `60c804a5f24ad282bda45684b3c3d246eeb0d57829f7e35730b12b4a2b6fd827` |
| kernel-pci-config | [sound/pci/Kconfig](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/pci/Kconfig) | `75bb38d82a9cd0f774c15da3b72fbb16a97e32e8737e81526cd72d9eefaa618c` |
| intel-driver | [sound/pci/intel8x0.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/pci/intel8x0.c) | `0c22002d13e8ec9b8512fe2efd345e369e8a81709b9a2a2141f191657c24b4e1` |
| streamer-launch | [host/commands/run_cvd/launch/streamer.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/streamer.cpp) | `f748cce3b7402e07aac47abb4f1568d7a458ed4db8ed3ddd833fcd7b025d0bbe` |
| config-instance | [host/libs/config/cuttlefish_config_instance.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/config/cuttlefish_config_instance.cpp) | `c0b0ed9d56832df7cad6646f8efb3c3118750e1ef742100d88266e5d2179f8c3` |
| other-launch | [host/libs/vm_manager/crosvm_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/crosvm_manager.cpp) | `8e8e783274f8e8279cccdcfb95c4ba3595de54ea1f0241d498d34d0511b9307c` |
| server | [host/libs/audio_connector/server.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/audio_connector/server.cpp) | `23fc487188e717569a5f85420760e571a09d0649cb4fa3b1fd2b312f57f9f7ac` |
| shm | [host/libs/audio_connector/shm_layout.h](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/audio_connector/shm_layout.h) | `a97972bff89542647b1ea19b50988e099a0e6e4b5321b8f1831b5f2c222e698b` |
| audio-handler | [host/frontend/webrtc/audio_handler.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/audio_handler.cpp) | `66c2451c0bba78f9d96d8ee9bc211c7755a53f59895349399c73372cf0b44006` |
| streamer-main | [host/frontend/webrtc/main.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/main.cpp) | `ba4748ab39a369991f34ed5f24ff1d74cd389f0b1935de89700cd9a198f8e800` |
| streamer | [host/frontend/webrtc/libdevice/streamer.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/libdevice/streamer.cpp) | `c708c46b683892c6570b6c4fcbdc79c78dbca51a39d594168889ab2b40a0a9d4` |
| audio-device | [host/frontend/webrtc/libcommon/audio_device.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/libcommon/audio_device.cpp) | `2ed317bcd655644db753c1d59352eca2b182891f740aaa6b07c77106380503dc` |
| audio-mixer | [host/frontend/webrtc/audio_mixer.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/audio_mixer.cpp) | `0201f4804814341c997f294a34037cad07babf4def670af234cccc7666c34474` |
| audio-track-source | [host/frontend/webrtc/libdevice/audio_track_source_impl.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/libdevice/audio_track_source_impl.cpp) | `89057f6c12010fb2be1d5b1a7a9883faed214097164482d9ad4a7906b3f0c1f1` |
| peer-build | [host/frontend/webrtc/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/Android.bp) | `26c58dbb890dfbee4bd232328422f2fb54eae7922ea7ce4bcb1454946d4f5345` |
| connector-build | [host/libs/audio_connector/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/audio_connector/Android.bp) | `2790fec9b34bba4b2132d4bf2bf0f183ba5c70f0f34ea197eab6fc8c12c76310` |
| host-defaults | [Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/Android.bp) | `2580299ebf86ef24dbf06e497dae23ae91d8db61262fd9aea07721dee234143b` |
| track | [media/java/android/media/AudioTrack.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/media/java/android/media/AudioTrack.java) | `7612d69230cb50f8271408662aca6e6b2a468222e441ec131aa30c38a254433b` |
| record | [media/java/android/media/AudioRecord.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/media/java/android/media/AudioRecord.java) | `2fd4d03808687498d018bee0b4c45872451888e141ae0817fdedb7a56d05ad02` |
| manager | [media/java/android/media/AudioManager.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/media/java/android/media/AudioManager.java) | `9492248a1563900a3e28e9267cf3019ed7ed58aed514b08bc98f377176bf15a4` |
| flinger | [services/audioflinger/AudioFlinger.cpp](https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audioflinger/AudioFlinger.cpp) | `4906b0655b008b9fdb5584bca19128ecbe0beee3ec1105a103f17b4ce06e1a76` |
| threads | [services/audioflinger/Threads.cpp](https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audioflinger/Threads.cpp) | `a5416ff05a3683712075ca1a383a73ebfb9331b18e88bfadfbc6aba2b62a13bc` |
| factory | [media/libaudiohal/impl/DevicesFactoryHalAidl.cpp](https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/media/libaudiohal/impl/DevicesFactoryHalAidl.cpp) | `6d498d185fe644146256902825d5267fa98153b973061e3bb502f39c40397629` |
| record-policy | [services/audiopolicy/service/AudioPolicyInterfaceImpl.cpp](https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audiopolicy/service/AudioPolicyInterfaceImpl.cpp) | `2ded7d737574e6878a35e77ded3641747a55dff732a386610314babc2105b15b` |
| app-policy | [private/app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te) | `6a18ae176e35cf19ab022cc75887a5c77aae55f00e8a1ebddd7ebd75aea64525` |
| isolated-policy | [private/isolated_app_all.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te) | `e65adb199d7fc26cd716f4e376f6068edcd3c350647f121e8d5937fa9bca4ad9` |
| hal-policy | [private/hal_audio.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/hal_audio.te) | `d8e503a74a52fc9bd62469cd94a2f90568ce0a931138dca2be1a1e78a65a73e0` |
| hal-domain | [vendor/hal_audio_default.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/vendor/hal_audio_default.te) | `f3ad6badfb42f195807bfc6c888e24ca8e7af930e292e4d8a0af6482190a8da4` |
| uevent | [rootdir/ueventd.rc](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/rootdir/ueventd.rc) | `7a26df7521ecba3b3fd66df438b4e5d1b5e8fa6fc5ea1a73c2c93eed803f985e` |
| eraser-build | [media/libeffects/eraser/Android.bp](https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/media/libeffects/eraser/Android.bp) | `6fe0016b8dd7a37b64fdc6a7b53bb765bea96166721fe0bf4a7bd07f4c1b8402` |
| eraser-notice | [media/libeffects/eraser/NOTICE](https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/media/libeffects/eraser/NOTICE) | `fe018f8288fe90440735c6eb4257ce2736017b562fb1c1ff94cfbc823770ca7a` |
| extension-build | [audio/aidl/default/extension/Android.bp](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/extension/Android.bp) | `606a713d24ca5f389cdbd520fd6b317f1e89ae672107f4429f5b8a533b33b80e` |
| manifest | [default.xml](https://android.googlesource.com/platform/manifest/+/5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f/default.xml) | `76ef74339da1e0c973d1ec7cb92045e823223a7724d9aa453b4cab4e246122c4` |

[product]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/vsoc_arm64/phone/aosp_cf.mk
[phone]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk
[device]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/device.mk
[board]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/BoardConfig.mk
[apex]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/apex/com.android.hardware.audio/Android.bp
[hal-build]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/Android.bp
[hal-main]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/main.cpp
[converter]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/AudioPolicyConfigXmlConverter.cpp
[module]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/Module.cpp
[init]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/android.hardware.audio.service-aidl.example.rc
[vintf]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/android.hardware.audio.service-aidl.xml
[apex-contexts]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/apex/com.android.hardware.audio/file_contexts
[config-build]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/Android.bp
[policy]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/audio/policy/audio_policy_configuration.xml
[primary-policy]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/audio/policy/primary_audio_policy_configuration.xml
[vendor-policy]: https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audiopolicy/audio_policy_config_vendor_1.mk
[effects-mk]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/audio_effects.mk
[effects-config]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/audio_effects_config.xml
[features]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/data/etc/handheld_core_hardware.xml
[primary-module]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/ModulePrimary.cpp
[primary]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/primary/StreamPrimary.cpp
[primary-header]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/include/core-impl/StreamPrimary.h
[mixer-header]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/primary/PrimaryMixer.h
[mixer]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/Mixer.cpp
[mono-pipe]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/StreamAlsaMonoPipe.cpp
[alsa-base]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/StreamAlsaBase.cpp
[alsa-utils]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/alsa/UtilsAlsa.cpp
[alsa-build]: https://android.googlesource.com/platform/system/media/+/440eb272fd3da0ca7bdae932e61e7fd9be1fd324/alsa_utils/Android.bp
[alsa-profile]: https://android.googlesource.com/platform/system/media/+/440eb272fd3da0ca7bdae932e61e7fd9be1fd324/alsa_utils/alsa_device_profile.c
[proxy]: https://android.googlesource.com/platform/system/media/+/440eb272fd3da0ca7bdae932e61e7fd9be1fd324/alsa_utils/alsa_device_proxy.c
[tiny-build]: https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/Android.bp
[tiny-pcm]: https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/src/pcm.c
[tiny-hw]: https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/src/pcm_hw.c
[tiny-notice]: https://android.googlesource.com/platform/external/tinyalsa_new/+/faac725f32811c68eb40e2d5956eadc51dbb8a60/NOTICE
[bootconfig]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/bootconfig_args.cpp
[defaults]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags_defaults.h
[flags]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/assemble_cvd/flags.cc
[stub]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/stub/DriverStubImpl.cpp
[qemu-launch]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp
[ac97]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/ac97.c
[none]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/noaudio.c
[virtio]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/virtio-snd.c
[virtio-pci]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/virtio-snd-pci.c
[q-kconfig]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/Kconfig
[q-build]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/audio/meson.build
[q-audio]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/audio.c
[q-audio-build]: https://raw.githubusercontent.com/qemu/qemu/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/audio/meson.build
[kernel-card]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_card.c
[kernel-pcm]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_pcm.c
[kernel-ops]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_pcm_ops.c
[kernel-msg]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/virtio_pcm_msg.c
[kernel-config]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/virtio/Kconfig
[kernel-pci-config]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/pci/Kconfig
[intel-driver]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/sound/pci/intel8x0.c
[streamer-launch]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/commands/run_cvd/launch/streamer.cpp
[config-instance]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/config/cuttlefish_config_instance.cpp
[other-launch]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/crosvm_manager.cpp
[server]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/audio_connector/server.cpp
[shm]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/audio_connector/shm_layout.h
[audio-handler]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/audio_handler.cpp
[streamer-main]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/main.cpp
[streamer]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/libdevice/streamer.cpp
[audio-device]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/libcommon/audio_device.cpp
[audio-mixer]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/audio_mixer.cpp
[audio-track-source]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/libdevice/audio_track_source_impl.cpp
[peer-build]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/frontend/webrtc/Android.bp
[connector-build]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/audio_connector/Android.bp
[host-defaults]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/Android.bp
[track]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/media/java/android/media/AudioTrack.java
[record]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/media/java/android/media/AudioRecord.java
[manager]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/media/java/android/media/AudioManager.java
[flinger]: https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audioflinger/AudioFlinger.cpp
[threads]: https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audioflinger/Threads.cpp
[factory]: https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/media/libaudiohal/impl/DevicesFactoryHalAidl.cpp
[record-policy]: https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/services/audiopolicy/service/AudioPolicyInterfaceImpl.cpp
[app-policy]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te
[isolated-policy]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te
[hal-policy]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/hal_audio.te
[hal-domain]: https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/vendor/hal_audio_default.te
[uevent]: https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/rootdir/ueventd.rc
[eraser-build]: https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/media/libeffects/eraser/Android.bp
[eraser-notice]: https://android.googlesource.com/platform/frameworks/av/+/475269ec44acec82792be6b01fb8e16357d4d2c8/media/libeffects/eraser/NOTICE
[extension-build]: https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/audio/aidl/default/extension/Android.bp
[manifest]: https://android.googlesource.com/platform/manifest/+/5bc9a7ce1cd78dd53613bbfd0ebf506e1e4adb0f/default.xml
