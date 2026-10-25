# Gate 0: Android 17 interactive input compatibility and trusted input boundary

Review: **2026-10-25; Windows x86_64; source-only.** Candidate guest: Android
17/API 37, little-endian ARM64. **Gate 0 Unresolved; Gates A–G Not reached.**
ADR-0001 remains Accepted; ADR-0002 remains Proposed. No engine is selected.

## Question, disposition and new findings

Can the selected phone receive a complete virtual multitouch and keyboard stream
through a software-only device controlled by an ordinary Android app, without
privileged host injection or exposing trusted PDVA management authority?

**Unchanged reference and unchanged constrained QEMU recipe: source-incompatible
with that complete input requirement; scoped STOP.** The reference selects a
relative mouse and keyboard, not a multitouch touchscreen. The constrained
recipe's declared device selection lacks virtio-input and its PCI transport.
**Replacement software multitouch mechanism: conditionally source-compatible
at the capability/driver/mapper level; complete path Unknown.** No installed
Android recognition, display association, transport, cancellation or text-entry
round trip is established. This does not falsify all ordinary-app designs.

New findings beyond the [complete-Android assessment](gate-0-complete-android.md)
and [source ledger](gate-0-complete-android-sources.md):

1. QEMU's multitouch advertises `BTN_TOUCH` as well as slots. Android's button
   accumulator treats a supported but false BTN_TOUCH as hovering. Sending only
   plausible slot/coordinate events is therefore insufficient. [Q-hid] [N-button]
   [N-multi]
2. The device advertises slot maximum 10 (11 slots), while the convenience helper
   accepts only indices 0–9. Android's mapper accepts the advertised range; this
   is a helper/device capacity discrepancy, not proof of driver incompatibility.
   The helper reuses slot indices as tracking IDs, and sends no BTN_TOUCH=0 on
   final release. These facts require explicit state reconciliation. [Q-header]
   [Q-hid] [Q-ui] [N-multi]
3. QEMU drops a complete report when the guest event queue lacks enough buffers.
   It does not retry, return delivery success, or emit SYN_DROPPED there. Missing
   release can leave guest state held; Android's separate evdev-overrun recovery
   cannot be assumed to repair a report that never reached the kernel. [Q-device]
   [K-evdev] [N-device]
4. QEMU keyboard advertises Linux keys 1–231. Generic.kl maps Back to 158 and
   Home to 172, but APP_SWITCH to 580, outside that bitmap. Linux filters
   unadvertised key codes. A direct raw APP_SWITCH path through this unchanged
   keyboard is source-incompatible. Guest-rendered navigation remains a separate
   conditional touch path. [Q-hid] [Q-codes] [K-input] [B-layout]
5. Android can classify the proposed device as direct touch without the named
   Cuttlefish IDC. That IDC does not match its name; a wrong explicit display ID
   can prevent viewport resolution, whereas an absent IDC permits a fallback.
   Neither proves the correct installed display. [N-event] [N-touch] [N-config]
   [C-idc]

Evidence notation: **S** source observation, **I** inference, **H** hypothesis,
**U** Unknown. All Android/input runtime cases below are **NOT RUN**. Required
means required for the examined configuration or PDVA contract, not every Android
device. Source references are not adopted dependencies.

## Exact baseline and live preflight

GitHub commit metadata and fetched `origin/main` agree on
`53ea1c499493d74a13df4149e6148407435a3547`, merging
[PR #39](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/39).
Relevant history includes PRs #36–39. The live open-PR search returned zero;
there were no open head/base pairs, diffs/files, checks/jobs/logs, reviews,
comments or review threads to reconcile, and no intended input PR to reuse.

[Foundation run 40213575444](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40213575444)
has successful foundation job `121229808830` and Windows job `121229808597`.
Job steps and actual execution logs were retrieved and inspected for checkout
identity and control results. Both identify the exact main SHA. Windows records
45 image and four frame controls; foundation includes repository/readiness/image/
frame and existing native/lifetime/seccomp/revocation controls. These are existing
baseline results, not virtual-input tests. All three repository workflows and
their path filters were inspected. Android and QEMU workflows are not selected
by this two-Markdown-file slice; no filtered job is a pass.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational and no incidents during preflight.

Initial tracked state was clean, with one worktree and no stashes. Local branches
and ignored Gradle/CMake/build/source assets were inventoried and preserved.
No applicable AGENTS.md was found. On resumption the clean checkout was on main
at the verified SHA; the focused branch was created there. Initial shell network
and Git-index writes required approved escalation. One branch-creation approval
could not complete because of an approval-service usage limit; no action executed
on that failure, and the authorized resumed request succeeded. No security setting
was changed or approval bypassed.

Governing inputs are requirements, architecture, acceptance criteria, gates,
security boundaries, threat model, testing, roadmap, governance and both ADRs.
The requested existing evidence, dependency/provenance records, native inventory,
workflow pins and cross-build recipe inform this comparison. Inherited limits
remain in [boot/HAL](gate-0-android17-boot-hal.md),
[software graphics](gate-0-android17-software-graphics.md),
[graphics configuration](gate-0-android17-graphics-config-closure.md),
[host display](gate-0-host-display-boundary.md),
[worker integration](gate-0-qemu-worker-integration.md),
[containment](gate-0-worker-containment.md),
[revocation](gate-0-capability-revocation.md),
[Android lifetime](gate-0-android-lifetime-authority.md) and
[userspace communication](gate-0-userspace-communication.md).
[Sensor STOP](gate-0-android17-sensor-service-closure.md) is a distinct result.
No graphics, sensor, firmware or general-engine resurvey is added.

An ignored checkpoint and immutable-source receipts support interruption recovery;
they are **not an independently verified backup**. The public evidence PR is the
intended durable disposition. A hard publication/association failure requires
**UNPRESERVED pending recovery PR or association repair**, never a duplicate PR.

## Selected configuration and falsifiable compatibility matrix

R is the existing Android 17 r1 `aosp_cf_arm64_phone`, `vsoc_arm64`, nonprotected
phone and unchanged QEMU-manager input declarations. H is a comparison only:
the same guest contracts with QEMU's internal software multitouch plus keyboard,
an explicitly matched virtual display and a future narrow app-to-worker adapter.
H is not implemented, adopted, or a runnable launcher. The complete release
variant/generated image is U. The prior boot/HAL ledger supplies the product and
kernel-version correspondence; the kernel source lead is not an attestation of
the separately packaged `virtio_input.ko`.

| Layer | Source-selected or available mechanism | Build/recognition/authority disposition and falsifier |
|---|---|---|
| R launcher | `virtio-mouse-pci,disable-legacy=on` and `virtio-keyboard-pci,disable-legacy=on`; two `vhost-user-input-pci` socket peers for switches and rotary. A comment retains VNC input and defers vhost-user mouse/keyboard use. No tablet or multitouch is added. [C-launch] | S/I: STOP treating R as a complete multitouch configuration. Switch/rotary endpoints are not unnamed touchscreens. Their socket peers are additional contracts, not proven ordinary-app bridges. |
| QEMU software devices | Keyboard, relative mouse, absolute tablet and multitouch HID implementations; matching PCI wrappers, forcing virtio 1. [Q-hid] [Q-pci] | S: available at the immutable QEMU pin. Tablet ABS_X/Y and mouse REL_X/Y are not multitouch. Availability does not establish compilation, realization or use. |
| Device build gates | `CONFIG_VIRTIO_INPUT` requires VIRTIO; HID and base device follow that symbol. PCI wrapper is in the PCI source set. HOST variant and VHOST_USER_INPUT are different choices. [Q-kconfig] [Q-meson] [Q-vmeson] [Q-vkconfig] | S/I: declared `--allnoconfig` + ARM_VIRT closure in the existing recipe/control has VIRTIO/MMIO but lacks VIRTIO_INPUT and VIRTIO_PCI. STOP unchanged build pairing. This is configuration evidence, not a fresh ELF inventory. |
| Pixman/display | Input HID source rule has no pixman prerequisite. UI has input helpers; VNC is gated by both VNC and pixman. [Q-meson] [Q-uimeson] | I: disabling pixman alone is not a universal input impossibility. Existing no-pixman/no-display build is not the reference VNC front end or an interactive phone. H still needs a matching display/console and adapter. No graphics rebuild. |
| Guest Linux | Board lists `virtio_input.ko`; kernel lead has VIRTIO_INPUT depending on INPUT/VIRTIO. Driver reads advertised IDs, property/event bitmaps and axis information, creates MT slots, registers an input device, and delivers little-endian events through `input_event`. [C-board] [K-config] [K-driver] | S: protocol mechanism fits ordinary software virtio input; guest PCI transport, exact module source/config/ABI, load/init/SELinux/evdev correspondence U. Missing selected module or transport rejects closure. Guest `/dev/input` authority is not host authority. |
| EventHub/InputReader | MT position X/Y plus BTN_TOUCH or no gamepad buttons establishes TOUCH/TOUCH_MT. INPUT_PROP_DIRECT selects touchscreen absent overrides. Slot min 0, max >0 and tracking axis select protocol B. [N-event] [N-multi] [N-touch] | S/I: QEMU multitouch satisfies these source predicates. A relative mouse fails them. Property/IDC overrides and actual discovered device/mapper are U. |
| IDC/identity/display | QEMU name is `QEMU Virtio MultiTouch`, BUS_VIRTUAL, vendor 0627, product 0003, version 0001; optional serial. Cuttlefish IDC names another device and a fixed display unique ID. [Q-hid] [Q-device] [C-idc] | S/I: name does not match; do not silently apply its settings. Exact selected IDC/APEX/property/viewport and multiple-display association U. Wrong explicit ID can disable input; absent IDC is not automatically fatal. |
| Host admission/transport | Own-window View/MotionEvent/KeyEvent processing exists; internal QEMU typed events are not an Android IPC protocol. [B-view] [B-motion] [B-key] [Q-ui] | H/U: manager-owned admission, bounded transport and worker event-loop adapter missing. No host injection, general Binder, shell or QMP capability is implied. |
| App/window receipt | InputDispatcher routes pointer events using touch windows/display, and keys using focused window; policy/channel failure may prevent delivery. [N-dispatch] | S mechanisms; U actual guest app input, focus, navigation, gesture correctness, latency and text commits. A virtqueue write is not an app receipt. |

The [cross-build feasibility](gate-0-qemu-android-crossbuild-feasibility.md) and
[Linux cross-build](gate-0-qemu-android-linux-crossbuild.md) records already
distinguish generated selection, compiled helper code and ARM64 dynamic-PIE link
results. No retained binary was executed or newly certified here. The declared
41-symbol source control is reused, not relabeled a new compatibility test.

## Multitouch wire, state and recognition contract

**S:** QEMU emits a little-endian `virtio_input_event` (16-bit type, 16-bit code,
32-bit value). The HID config includes EV_KEY button bits, EV_ABS slot/tracking/
MT-X/MT-Y, INPUT_PROP_DIRECT and absolute X/Y ranges **0–32767**. It emits
EV_SYN/SYN_REPORT to finish a report. No MT pressure, tool-type, touch-major/minor,
orientation, distance or stylus axes are advertised. BTN_TOOL_FINGER is not
advertised; Android falls back to FINGER when no explicit tool is recognized,
and derives pressure 0 for hover or 1 for touching when uncalibrated. Those are
framework-derived values, not sensed pressure or palm discrimination. [Q-hid]
[Q-header] [N-multi] [N-touch]

**S/I: protocol B.** ABS_MT_SLOT selects the persistent slot; nonnegative
ABS_MT_TRACKING_ID creates/continues a contact and -1 ends it. Each report must
select the intended slot before its coordinates. In QEMU's DATA branch the HID
handler emits only the axis/value: it does **not** use the slot field to select
a slot. A caller cannot interleave DATA for arbitrary slots without preceding
slot selection. Android retains slot contents across reports and uses tracking
IDs to preserve pointer identity. A new down needs fresh position values before
sync, and an ID must not identify two simultaneously live contacts. Reuse after
a completed release is legitimate; reuse after a lost release is not evidence
of a new gesture. [Q-hid] [Q-ui] [N-accumulator] [N-multi] [K-mt]

The helper `qemu_input_touch_event` accepts slot <10, stores x/y, assigns the slot
index as tracking ID on BEGIN, then reports the changed slot and other active
slots. It sends BTN_TOUCH=true on active updates and -1 on END, followed by sync.
It does not emit BTN_TOUCH=false when the final slot ends. **I:** Android's slot
accumulator still retires the slot on -1, so that omission alone does not prove
a stuck Android pointer. It does leave the advertised button state unreconciled;
it cannot be called a complete release/cancel implementation. Sending MT data
without setting BTN_TOUCH true can produce hover instead of a touch because the
device advertises that button. [Q-ui] [N-button] [N-accumulator] [N-multi]

The device's ABS_MT_SLOT and tracking maxima are both 10, while the helper uses
ten array entries. Android permits up to 32 protocol-B slots and separately caps
emitted pointer count. Thus the advertised 11 slots fit the inspected mapper;
no claim of 11-contact support through the ten-slot helper is valid. A candidate
must choose and enforce one explicit supported contact cap, independently of
host pointer IDs and of the device's advertised maximum. [Q-header] [Q-hid]
[N-multi]

**Grouping/backpressure:** QEMU appends events until SYN_REPORT, growing its
staging array without a report-size ceiling in `virtio_input_send`. It pops enough
guest buffers for the whole report, or unpops acquired buffers and discards the
report. Inactive devices discard input. The guest driver supplies 64 event buffers;
availability is dynamic, not guaranteed by that array size. The separate delayed
keyboard queue's limit is not an aggregate touch/IPC/worker-memory quota.
The send function returns void, not an application-delivery acknowledgement.
[Q-device] [Q-ui] [K-driver]

**I:** a lost final -1 or key-up can leave the guest's last state active; a later
reuse of the same helper tracking ID can continue an old gesture. Linux evdev
can signal SYN_DROPPED on its own client-buffer overrun, and Android then waits
for sync and resets/requeries mapper state. QEMU's earlier report-drop path does
not generate that notification or update the guest kernel's state. Therefore
do not claim Android's recovery solves it. A bounded reliable admission/loss
and resynchronization contract is missing. [K-evdev] [N-device] [Q-device]

**Cancellation/reset:** host ACTION_CANCEL is not a wire-level Android
MotionEvent delivered by virtio. Releasing slots is not necessarily equivalent
to guest ACTION_CANCEL (an UP can complete a click). A candidate must define how
interruption aborts an already-dispatched gesture without committing unintended
actions, and what independent observation demonstrates that. QEMU's device reset
deactivates the handler but does not explicitly clear the pending report index
in that reset callback. Android mapper reset, kernel driver remove/freeze/restore,
and device hotplug are separate lifecycles. A host view loss triggers none of
them automatically. Partial reports, held modifiers and contact state must be
retired before reauthorization; actual cross-layer behavior remains U. [Q-device]
[K-driver] [N-device] [N-multi] [N-keyboard]

## Identity, display association and coordinates

Android probes vendor/product/version IDC first, then vendor/product, then a
sanitized device name. For H the name form is `QEMU_Virtio_MultiTouch.idc`, not
`Cuttlefish_Vhost_User_Multitouch_Touchscreen_0.idc`. Cuttlefish packages its IDC
files in `com.google.cf.input.config`; Android can search the APEX named by
`input_device.config_file.apex` as well as product/system_ext/odm/vendor/system
locations. Installed precedence/contents remain U. A matching file elsewhere
could override assumptions. [N-config] [C-inputbuild]

The Cuttlefish IDC sets internal=true, touchScreen, orientationAware=true and
`touch.displayId=local:4619827353912518656` (an upstream reference display value,
not a host identifier). It supplies no automatic match to H. TouchInputMapper
prioritizes associated viewport, then applicable pointer-display selection,
then explicit IDC unique display ID, then display-type fallback. An explicit
nonexistent ID returns no viewport; it does not simply retry the internal default.
With no override INPUT_PROP_DIRECT supplies touchscreen classification and
orientation awareness defaults true. **I:** lack of a matching IDC alone is not
a source falsifier of direct touch, but correct display association is U.
[C-idc] [N-touch]

Kernel `phys` is derived from the virtio device index and `uniq` from the optional
serial. EventHub constructs descriptors and uses a nonce to disambiguate duplicate
descriptors. No source rule requires a globally unique display-like name for
touch recognition. A stable explicit serial/port/viewport binding may be needed
for deterministic multi-device association, but it is not trusted PDVA instance
authentication. QEMU's `display`/`head` handler binding selects a QEMU console;
it does not set Android's display unique ID. [K-driver] [N-event] [Q-hid]

**H: required mapping owner.** Management owns the current guest-region rectangle,
clip, display/geometry generation and inverse presentation transform. Reject
letterbox/chrome hits; map finite in-region view pixels through crop/scale/rotation
to the device's unrotated raw coordinate space. QEMU helper scales against width/
height while Android uses axis extents and viewport transforms; exact endpoint
rounding and inclusive maxima require a single declared convention. Do not treat
dp/density as raw coordinates or rotate twice: Android's orientation-aware mapper
already rotates/scales into display space, then window transforms apply. On resize,
rotation or view replacement retire the old input generation and resolve gesture
cancellation before admitting new input. No transform implementation or test is
supplied. [Q-ui] [N-touch] [B-motion]

## Keyboard, navigation, focus and text

| Function | Source disposition and remaining contract |
|---|---|
| Physical-style keys | QEMU's internal KEY event is a Linux input code with down boolean, emitted as EV_KEY 1/0 plus sync. Android KeyEvent codes are a different namespace and cannot be copied numerically. Source keymap generators support front-end mappings; no Android host-key translator is implemented. [Q-hid] [Q-ui] [Q-keymap] [Q-uimeson] [B-key] |
| Down/up/repeat | Device advertises EV_REP; Android KeyboardInputMapper ignores Linux value 2 because Android handles repeat. Release, focus and policy still govern repetition. Duplicate downs or loss of key-up are not Unicode commits; modifier state must be reconciled on interruption. Mapper reset releases down keys and resets state, but host backgrounding does not invoke guest reset by itself. [Q-hid] [N-keyboard] |
| Back/Home/Recent | Under Generic.kl fallback, Linux 158→BACK and 172→HOME; Linux 102→MOVE_HOME is cursor navigation, not Android Home. Linux 580→APP_SWITCH exceeds QEMU's 1–231 advertised range and is filtered by Linux. STOP that direct unchanged-keyboard Recent route. A different reviewed layout/advertisement or guest SystemUI touch route is conditional, not an implemented fix. Guest policy may consume navigation instead of delivering it to an app. [B-layout] [Q-codes] [K-input] [N-keymaps] |
| Focus and dismissal | Host focus belongs to PDVA's own window; guest key focus belongs to guest InputDispatcher/window/IME policy. One does not set the other. A guest field must receive touch/focus and the guest IME must be active. Keyboard dismissal/Back behavior and focus after interruptions are U. No host-wide Back/Home interception is assumed. [B-view] [N-dispatch] |
| Guest-rendered IME | The selected AOSP product inherits handheld_product, which includes LatinIME. This is a package-selection lead beyond service startup, not an installed/active keyboard receipt. Touching guest keys could keep composition, selection and surrounding text inside the guest. Exact module/source/build, enabled/default subtype, editor/InputConnection and composed-character results are U. [P-product] [P-handheld] |
| Unicode/composition | Raw physical key events, key-layout lookup and Virtual.kcm are not a general Unicode commit protocol. Layout/dead-key behavior is distinct from IME composing text, candidate selection and commit. No complete text-entry mechanism is qualified. Missing proof: selected guest IME/editor transaction plus display/touch/focus agreement, including multi-code-point and composed text. [B-virtual] [N-keymaps] |
| Rotation during typing | Guest window/IME reconfiguration and host geometry generation must agree while preserving or deliberately canceling composition and releasing keys/contacts. Keyboard mapper preserves an already-down key's mapping across repeats/rotation; this does not qualify the whole session. NOT RUN. [N-keyboard] [N-touch] |
| Host IME / clipboard | No independently necessary host IME bridge established. An optional bridge would add surrounding-text, selection, composition, deletion, privacy and focus authority; it is not adopted. Guest-local selection/copy can remain guest-local. No general host clipboard broker, autofill or clipboard disclosure is required by the examined virtio route. |

## Trusted input responsibility trace and ordinary-app authority

This is an unimplemented responsibility trace, not an accepted architecture:

```text
PDVA-owned guest display region and trusted escape controls
  -> manager hit-testing, focus/lifecycle and geometry validation
  -> manager-owned instance/epoch, sequence and bounded input authorization
  -> narrow one-way worker command and bounded transport
  -> worker event-loop adapter -> virtual input device
  -> guest virtio_input -> Linux input/evdev
  -> EventHub -> InputReader/mapper -> InputDispatcher
  -> guest application/window and guest IME/SystemUI as applicable
```

| Host mechanism | Actual authority class and enforcing owner |
|---|---|
| View dispatch, MotionEvent pointer IDs/actions/history and KeyEvent handling in the app's delivered window | **Ordinary installed app.** Host framework owns delivery; PDVA manager owns hit-testing, focus and accepted region. Not a grant to collect all host input or suppress host escape gestures. [B-view] [B-motion] [B-key] |
| System `injectInputEvent` / host-wide injection | **Restricted/system/signature.** InputManagerService checks INJECT_EVENTS and manifest declares it signature. **Unsupported for this route**; no permission is added. Instrumentation/shell development authority is not production app authority. [B-service] [B-manifest] |
| Host `/dev/input`, uinput or evdev passthrough | **Unsupported for this route**; ordinary own-window processing grants no node access. Specific OEM node policy is not newly qualified here. Root/shell/OEM-specific access cannot repair the ordinary-app contract. QEMU's host-input variant must not be confused with internal HID emulation. |
| Internal software virtual input | **No intrinsic privileged host injection.** Worker changes guest device state in software; Linux event privileges are guest-local. Actual Android native execution/isolated policy remains **Unknown**, as in prior integration evidence. |
| Manager queue and instance authorization | **Ordinary app logic, proposed.** Trusted manager owns admission, current epoch, sequence, contact/key state, geometry generation, aggregate size/rate/queue budgets and revocation of future sends. Worker-supplied identity/epoch is not authorization. No implementation or numerical production quota selected. |
| Worker transport / inbound requests | **Unknown composed isolated-process authority.** Exact Binder/FD endpoint and cross-UID enrollment are missing. Trusted receiver must bound parsing/work and reject management requests; OS owns IPC/UID enforcement. Worker cooperation alone cannot bound hostile Binder traffic or total resource consumption. |
| Independent worker containment and termination | **Unknown.** Host OS is enforcement owner; manager cannot infer hostile-tree death from timeout, Binder death, ack or view removal. Root/system force-stop/cgroup remedies are not ordinary-app solutions. Prior lifetime/revocation blockers remain. |

Management chooses guest versus trusted-control ownership before dispatch. A touch
starting on trusted PDVA controls must never enter the guest stream; a guest
gesture crossing into trusted chrome cannot authorize a management action.
Do not interpret guest pixels, fake dialogs, guest labels or worker requests as
management consent. Trusted escape must remain available despite guest stalls,
floods or misleading imagery; UI gesture success proves neither isolation nor
completed revocation.

Required admission checks include authenticated endpoint binding to one live
instance/epoch; strictly scoped sequence/replay rules; bounded pointer count and
history; finite coordinates within current geometry; down-before-move/up; no
duplicate active IDs, impossible slot transitions or stale geometry. Bound event
bytes, messages, rate, queued work and all-instance totals before allocations and
off the UI blocking path. Limit any worker replies to fixed status data, never
arbitrary Binder objects, shell strings, QMP operations or host-input requests.
Worker-side checks are useful correctness defenses but cannot enforce policy
against a hostile worker.

Backgrounding, focus loss, view destruction, resize and worker timeout/crash must
first stop future admission and invalidate queued old-generation commands under
trusted ownership. Guest contact/key cancellation needs its separate verified
contract; sending a best-effort cancel is not proof it arrived. A compromised
worker can retain or replay already disclosed input and can synthesize arbitrary
guest input itself. The enforceable host claim is exclusion from management and
other instances, not obedience inside a hostile guest. Never share management
secrets, Persona master state, signing credentials or another instance's backing
objects; independently establish UID/SELinux/FD and lifetime separation. Uncertain
termination retains existing lockout and cannot authorize resource reuse.

## Source-grounded negative controls

These are source comparisons and future falsifiers, **not executed input tests**.

| Invalid condition | Source witness / required rejection |
|---|---|
| Mouse accepted as multitouch | R mouse has relative axes, not MT X/Y; reject by [Q-hid]/[N-event]. Already falsifies unchanged selection. |
| Missing slots/tracking | Android protocol-B predicate requires both axes and valid slot range. Missing them changes protocol handling; cannot claim persistent-slot compatibility. [N-multi] |
| Slot-only down without BTN_TOUCH | Supported false BTN_TOUCH makes active pointers hover; require coherent button state. [N-button]/[N-multi] |
| DATA addressed to another slot without slot selection | QEMU DATA handler ignores its slot field; reject such encoder assumptions. [Q-hid] |
| Wrong name or display ID | IDC lookup will not match a different sanitized name; nonexistent explicit display ID can leave no viewport. Correct direct classification alone does not pass. [N-config]/[N-touch] |
| Wrong orientation / letterbox coordinate | Compare declared inverse presentation transform with raw range and viewport/window transforms; reject old generation and out-of-region coordinates. Source mechanism exists, actual transform U. |
| Stale tracking ID reuse | Slot identity persists until -1; a lost release makes reuse unsafe. Require acknowledged reconciliation or terminal loss, not a fresh host pointer index alone. [N-accumulator]/[Q-device] |
| Missing release/cancel | Queue-full can drop release; generic UP can commit an action and is not semantic CANCEL. No complete recovery contract established. |
| One gesture reaches two instances | Manager must bind one authorized endpoint/epoch and reject cross-instance forwarding. Internal QEMU console binding does not authenticate PDVA ownership. NOT RUN. |
| Queued input after view destruction | Trusted admission/queue retirement must reject old geometry generation even if worker remains alive. NOT RUN; existing synthetic token checks do not exercise real input. |
| Worker asks to activate management control | No such inbound operation may exist. Reject independent of claimed epoch, displayed pixels or a prior successful gesture. NOT RUN. |
| Unbounded flood or missing sync | QEMU staging grows before sync; keyboard delay cap is not total resource enforcement. Require trusted bounds and independent worker containment. [Q-device]/[Q-ui] |
| Raw codes called complete text entry | Keyboard bitmap/layout does not implement IME composition or arbitrary commits; exact guest IME/editor proof missing. Direct code 580 is unsupported by this keyboard. |
| Hotplug/reset without state reconciliation | Device reset/deactivation, mapper reset and host lifecycle are different events; no automatic cross-layer release guarantee. Reject stale slots, modifiers and partial reports. [Q-device]/[N-device]/[N-keyboard] |

## Source correspondence, dependencies, licenses and TCB limits

Pins retain the prior release: QEMU
`4fc49f46dc95d4a27de2509e7fceb2931e91faeb`; Cuttlefish
`283645aacf6cdb56cc31a9362f54d412dbc132a1`; frameworks/native
`ae266dcb706d083868578cfedce381ef44488a07`; frameworks/base
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`; platform/build
`5ce6f787337d0223710bf7d4a16dbe6d2a35f777`; kernel/common source lead
`3ec022196c4e9d5c1434599cdda63f622dd6f586`.

The existing Android cross-build targets AArch64/Bionic API 30 with NDK r28c,
TCG/system-only constrained devices, disabled pixman/GL/front ends and prior
strict-memory adaptations. It is not an Android 17 guest build or supported-host
minimum. No compiler/build flags are changed. Exact linked device objects,
generated configuration, selected guest module ABI, keymap/IDC/APEX installation,
guest IME and linker/toolchain correspondence remain missing. Generated QEMU
keymaps use keycodemapdb CSV/generator inputs already pinned in the recipe;
their presence is not an Android KeyEvent translator. [Q-uimeson]

QEMU input files carry GPL-2.0-or-later notices; its Linux-derived standard header
has its own syscall-note terms. Kernel sources retain GPL/file-specific terms.
Inspected Android framework/config/keymap sources carry Apache-2.0 notices.
Existing GLib, PCRE2, libffi, proxy-libintl, GVDB, dtc/libfdt and build-tool license/
corresponding-source obligations remain in the integration/dependency ledgers.
An IME package name is not a complete source/license audit of that package.
No additional library, SDK, ROM, binary, third-party app code or proprietary asset
is imported or adopted; no transitive rights/shipment approval is inferred.

Potential hostile native parsers include virtqueues, config bitmap/axis data,
guest descriptor/IOV lengths, input status/LED messages, device state, generated
keymap lookup and the future worker command adapter. The trusted TCB would include
host OS input/IPC/UID enforcement, management hit-testing/admission, bounded
transport receiver, lifecycle authority and supply chain. Guest InputReader/
Dispatcher are functionality components, not enforcement against compromised
guest/worker access to management. No success here would establish containment.

## Test decision, remaining requirements and smallest next proof

No new synthetic input implementation/test suite is justified: it would restate
invented adapter behavior and could not establish selected Android compatibility.
This record uses source/configuration closure and actual repository hygiene
checks. Runtime input cases, QEMU execution/build, guest construction/boot,
emulator, phone, host IME, guest text composition, hotplug, latency and security
tests are **NOT RUN**. Existing protocol tokens are bounded synthetic values,
not guest events; the [harness](gate-0-isolated-worker-harness.md) is unchanged.

**Smallest new independent falsifier before any build:** obtain one coherent
source/configuration receipt for an explicitly proposed device and guest pair:
exact selected input/PCI symbols, module/config/source correspondence, complete
event/property/axis and key bitmaps, effective IDC/keymap/APEX precedence,
display-viewport identity, and producer state transitions including BTN_TOUCH,
slot selection, loss, final release and cancellation. Compare it directly with
the pinned kernel and mapper predicates. The current direct APP_SWITCH bitmap
mismatch and missing multitouch selection are already source falsifiers; do not
rerun the unchanged pairing to rediscover them. A revised proposal must explicitly
resolve the queue-loss/cancel and Recent-navigation contracts rather than only
adding a device name. This receipt can reject an invalid pairing without building
a full guest or running QEMU.

Only after source closure and separate authorization would a real built guest
need independent app/window observations of simultaneous contacts, loss recovery,
orientation/cancel, navigation and composed text using synthetic data. That later
experiment must also distinguish device receipt, framework receipt and app action;
one layer's log cannot certify all three. No such experiment is authorized here.

**STOP conditions:** unchanged mouse-only selection or missing device transport;
unadvertised required key/axis; mismatched effective display association; no bounded
loss/cancel/resynchronization contract; missing mandatory module/IME/build/source
correspondence; dependence on privileged host injection or unrestricted broker;
management/Persona/peer authority entering the hostile worker; uncertain cleanup
used to authorize restart. A new material authority or architecture requires a
concrete ADR and Tony's explicit approval, not this evidence PR.

Remaining Gate 0 obligations include ordinary stock-app execution, hostile-worker
containment and independent lifetime/revocation, manager-loss recovery, complete
guest source/build/backend correspondence, graphics/display ownership, resource
budgets and sustained interactivity. No root/system grant, production ADB, custom
ROM/hooks, profile substitute, host VPN takeover, genuine-GPS fallback or
attestation bypass is introduced. **Gate 0 Unresolved; Gates A–G Not reached.**

## Validation and publication boundary

Local checks used the existing Python 3.11.4, without installing tools:

| Check | Actual observation |
|---|---|
| Foundation validator | PASS: 134 files, 82 Markdown files, 54 requirements, two ADRs; local Markdown file targets and repository hygiene included. |
| Harness authority validator | PASS: source/manifest checks, not Android execution. |
| Repository regression suite | 141 tests, 137 passed and four existing Windows/platform skips. Skips are not passes. |
| Desktop-readiness suite | 27 passed. |
| Offline-image controls | 45 passed on synthetic inputs. |
| Frame-copy controls | Four passed; existing mapped-buffer tests, not guest frames. |
| Source receipts | All 42 raw-byte hashes checked; downloaded QEMU sources matched pinned Git blobs byte-for-byte. Prior matching launcher/EventHub/HID/IDC receipts agree. |
| Final review | Exact-base two-file diff, local links, source reference IDs, whitespace, regular 100644 modes, dependency/binary absence and public privacy reviewed. |

Linux-specific native suites were not run locally; their existing exact-main
hosted logs are separately attributed above. Android build/lint and QEMU build
were not rerun because their sources/configuration are unchanged. No newly run
check establishes guest input, installed recognition, IME or sandbox isolation.
The final change contains only this evidence record and its index entry.
No new production code, dependency, permission, workflow or test is added.
After exactly one PR, verify its number/branch/head/base once, attach natively
to this chat and verify association once, then STOP. Hosted checks remain
**pending/unobserved until independent review**; no CI/review/mergeability polling.

## Immutable source receipts

Retrieve Gitiles links with `?format=TEXT`, base64-decode and SHA-256 the raw
bytes; QEMU receipts use raw upstream bytes or `git show PIN:path`. Downloaded
QEMU files were compared byte-for-byte with the pinned Git blobs. Android files
were decoded without newline conversion. A guessed native `data/keyboards/Generic.kl`
returned 404; its actual frameworks/base path is B-layout below. That retrieval
failure is not evidence of an absent Android key layout. Hashes describe source,
not compiled or installed artifacts. The receipt table and reference definitions
below make the source observations reproducible without the local checkpoint.

| ID / immutable file | SHA-256 |
|---|---|
| [B-view: core/java/android/view/View.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/View.java) | `625091021aefed43fac12e1198c6efa5b9f87287c1bd072b7bb2502d106021ee` |
| [B-motion: core/java/android/view/MotionEvent.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/MotionEvent.java) | `f82bc419f663a62171e254cea757ebbb091112744676a40655bd5681b147757d` |
| [B-key: core/java/android/view/KeyEvent.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/KeyEvent.java) | `1f4ac4a6b669e19046e1c925e71d77938edf8575f87900d84d411403956e914b` |
| [B-service: services/core/java/com/android/server/input/InputManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/input/InputManagerService.java) | `df0e4cc78508383cd60fd2cd534ba450a0df2071b211ee21115fa71f35470dc1` |
| [B-manifest: core/res/AndroidManifest.xml](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/res/AndroidManifest.xml) | `26d188bfdc84ab67d3e999227d07fa273fb28c8581225cb74ea956ab93e084ec` |
| [N-event: services/inputflinger/reader/EventHub.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/EventHub.cpp) | `38f5775af51d5bbe09d7c87778a510a35f52120e46f1b000202aa16052659d97` |
| [N-multi: services/inputflinger/reader/mapper/MultiTouchInputMapper.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/MultiTouchInputMapper.cpp) | `d82c368bdc922fa4cfcef401e057d48144134ee2b3f15688f7916acca8cf901c` |
| [N-touch: services/inputflinger/reader/mapper/TouchInputMapper.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/TouchInputMapper.cpp) | `8e2886c7c5d95c7cf3aff1b0b43cecd9b7eed8c01092281afaddb649bf6eddbd` |
| [N-keyboard: services/inputflinger/reader/mapper/KeyboardInputMapper.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/KeyboardInputMapper.cpp) | `0a8bc5d7d66b02d4faac11f9c8252e6bb059f7ad2f4cbbae80865d32a810f303` |
| [N-accumulator: services/inputflinger/reader/mapper/accumulator/MultiTouchMotionAccumulator.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/accumulator/MultiTouchMotionAccumulator.cpp) | `6a83cd7734a2e0f3ab458e71f5e01cb4c362eca87013d7a9a9bc81e24d78926a` |
| [N-device: services/inputflinger/reader/InputDevice.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/InputDevice.cpp) | `5a27592c180326513ef9aa3260a8f126ada0c5b3cfe24b942bf63c59ae339cea` |
| [N-dispatch: services/inputflinger/dispatcher/InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/dispatcher/InputDispatcher.cpp) | `4598e3a96e0196a5965be2a4232736ba7e14616c8435b201ab6d394e44b762c9` |
| [N-config: libs/input/InputDevice.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/libs/input/InputDevice.cpp) | `51ff0cb46fff83aa7f74152c28d0bb954eb598f3faddc4345e5509736c4640f9` |
| [Q-hid: hw/input/virtio-input-hid.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/virtio-input-hid.c) | `aae90a22fda46a0a61939cf3f4e56f93bf751215dffb3d2ba643b7f09a3693f9` |
| [Q-device: hw/input/virtio-input.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/virtio-input.c) | `0c3cecb7be4b5a115358643ca95788fa111d17efe41ecb3c0124bf73c7d4aad5` |
| [Q-kconfig: hw/input/Kconfig](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/Kconfig) | `e245f5e6ffef7500496cce482fc6c2bf9664c1e9369eb6c5f618fd64da9e94f1` |
| [Q-meson: hw/input/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/meson.build) | `00d81d8ed37c1489258b28ec3a09a9673352eb8cbcc0f450727f5732fd0e7b35` |
| [Q-pci: hw/virtio/virtio-input-pci.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/virtio-input-pci.c) | `73fbebf24dc71c194e8dc2d029eb359057005724c5bf32bc7514cd498c48a1d6` |
| [Q-ui: ui/input.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/input.c) | `619089241c78af002e296ce54627ae2a30cb3421dc8684e8d879471e3af43b83` |
| [Q-keymap: ui/input-keymap.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/input-keymap.c) | `432c4b759ef624b58882185d8f042514ec1c913a71b58bcc4ff9b123bb6f0af5` |
| [Q-uimeson: ui/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/meson.build) | `388b34e5e83aa13579622e366e211a411cfeb9777ed341b7c0ca251e381434ea` |
| [C-launch: host/libs/vm_manager/qemu_manager.cpp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp) | `d36a0826bcaff78dff15ea2aa5d1bd13ae3a97649b9bc2d130031d3f8fe379e7` |
| [C-idc: shared/config/input/Cuttlefish_Vhost_User_Multitouch_Touchscreen_0.idc](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/input/Cuttlefish_Vhost_User_Multitouch_Touchscreen_0.idc) | `67468f7a834581bd1b8f31785b50bf9b8ba35eac87525e1b3328177b26f691af` |
| [C-inputbuild: shared/config/input/Android.bp](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/input/Android.bp) | `ebf64938fdbd173e0bf41f91698bacdc2cb2e5a99e48c7aee5fbe4c2cc44bdb9` |
| [C-board: shared/BoardConfig.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/BoardConfig.mk) | `681ae40db963fbdcd59644f8d74fa16013c55e5f09127031c6dfdbe4e0b0df70` |
| [C-phone: shared/phone/device_vendor.mk](https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk) | `69645517941d7013eb798376faeee588cc86f9bfd117dd5eecd27b250b6ad176` |
| [K-driver: drivers/virtio/virtio_input.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/virtio/virtio_input.c) | `c4e8e4c96fc93cce27889b4d433a69012e12d018c48d279082777f732acc229a` |
| [K-config: drivers/virtio/Kconfig](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/virtio/Kconfig) | `ac1654cf69cdbd16894cc93569b88e6f8001cdac4715592384d32e969756a84e` |
| [K-evdev: drivers/input/evdev.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/input/evdev.c) | `b1a622fad1920e8400e12a039329699ae3fddfe995be5a508cbc699550dd5570` |
| [K-mt: Documentation/input/multi-touch-protocol.rst](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/Documentation/input/multi-touch-protocol.rst) | `a3f694bd62083791569d4cab833eeec85f5250c0e68a00dfb602ed76499fd04f` |
| [Q-header: include/ui/input.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/ui/input.h) | `7ebddaca72c431b3fd91fd4b96fb5c23d2bdd99b416da655625339b8d515426f` |
| [Q-vmeson: hw/virtio/meson.build](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/meson.build) | `26ee116a285af2cc7afd82b2360ac54f679e809a04233ff5799248cc7daad01e` |
| [N-button: services/inputflinger/reader/mapper/accumulator/TouchButtonAccumulator.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/accumulator/TouchButtonAccumulator.cpp) | `c29a36658d35c8bd78926421d1b7d735cccb951e80eb9c2d964f2402932cbcef` |
| [B-layout: data/keyboards/Generic.kl](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/data/keyboards/Generic.kl) | `4d28d904e72ea3beb4d32d73437cf9e7f1ed297a436d51d53b1a248a5cd5f773` |
| [B-virtual: data/keyboards/Virtual.kcm](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/data/keyboards/Virtual.kcm) | `6356265ec24b7eb2bf835ea269247cf46de646bd0d40a5755cf75d5fa7c581f1` |
| [P-handheld: target/product/handheld_product.mk](https://android.googlesource.com/platform/build/+/5ce6f787337d0223710bf7d4a16dbe6d2a35f777/target/product/handheld_product.mk) | `a450148917a5d5affd30d7b75f1bffb56a6b78678ba6bd4ed4472fae9da21c7a` |
| [K-input: drivers/input/input.c](https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/input/input.c) | `117d587a0fa0cbbe30e104602ff3e5eecd4c7a9263bb5fbaf2d4915441b36036` |
| [N-keymaps: libs/input/Keyboard.cpp](https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/libs/input/Keyboard.cpp) | `2c2dd7704bb90bb325b9fdbfe56314598661b71136722f33d9eede61dd79b6d9` |
| [P-product: target/product/aosp_product.mk](https://android.googlesource.com/platform/build/+/5ce6f787337d0223710bf7d4a16dbe6d2a35f777/target/product/aosp_product.mk) | `7299651a28575223fba525d59caa007bc9f932ad71d50476ab860696027f87c2` |
| [Q-codes: include/standard-headers/linux/input-event-codes.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/standard-headers/linux/input-event-codes.h) | `187e0e862d88ef6ce0114c994dde053b2a034fb2c82357ff4ba65c71cdf861f0` |
| [Q-deviceheader: include/hw/virtio/virtio-input.h](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/hw/virtio/virtio-input.h) | `34cf6aeb9717d3ff6ba0107ef437d08db915119e49f9925ed5769f54881a89f2` |
| [Q-vkconfig: hw/virtio/Kconfig](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/Kconfig) | `931dafedf7b6869847e7b97cc720357ce6af1ffd6c1518092333c9fd03753bc7` |

[B-view]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/View.java
[B-motion]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/MotionEvent.java
[B-key]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/view/KeyEvent.java
[B-service]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/input/InputManagerService.java
[B-manifest]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/res/AndroidManifest.xml
[N-event]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/EventHub.cpp
[N-multi]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/MultiTouchInputMapper.cpp
[N-touch]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/TouchInputMapper.cpp
[N-keyboard]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/KeyboardInputMapper.cpp
[N-accumulator]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/accumulator/MultiTouchMotionAccumulator.cpp
[N-device]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/InputDevice.cpp
[N-dispatch]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/dispatcher/InputDispatcher.cpp
[N-config]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/libs/input/InputDevice.cpp
[Q-hid]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/virtio-input-hid.c
[Q-device]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/virtio-input.c
[Q-kconfig]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/Kconfig
[Q-meson]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/input/meson.build
[Q-pci]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/virtio-input-pci.c
[Q-ui]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/input.c
[Q-keymap]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/input-keymap.c
[Q-uimeson]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/ui/meson.build
[C-launch]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/host/libs/vm_manager/qemu_manager.cpp
[C-idc]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/input/Cuttlefish_Vhost_User_Multitouch_Touchscreen_0.idc
[C-inputbuild]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/config/input/Android.bp
[C-board]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/BoardConfig.mk
[C-phone]: https://android.googlesource.com/device/google/cuttlefish/+/283645aacf6cdb56cc31a9362f54d412dbc132a1/shared/phone/device_vendor.mk
[K-driver]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/virtio/virtio_input.c
[K-config]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/virtio/Kconfig
[K-evdev]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/input/evdev.c
[K-mt]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/Documentation/input/multi-touch-protocol.rst
[Q-header]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/ui/input.h
[Q-vmeson]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/meson.build
[N-button]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/services/inputflinger/reader/mapper/accumulator/TouchButtonAccumulator.cpp
[B-layout]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/data/keyboards/Generic.kl
[B-virtual]: https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/data/keyboards/Virtual.kcm
[P-handheld]: https://android.googlesource.com/platform/build/+/5ce6f787337d0223710bf7d4a16dbe6d2a35f777/target/product/handheld_product.mk
[K-input]: https://android.googlesource.com/kernel/common/+/3ec022196c4e9d5c1434599cdda63f622dd6f586/drivers/input/input.c
[N-keymaps]: https://android.googlesource.com/platform/frameworks/native/+/ae266dcb706d083868578cfedce381ef44488a07/libs/input/Keyboard.cpp
[P-product]: https://android.googlesource.com/platform/build/+/5ce6f787337d0223710bf7d4a16dbe6d2a35f777/target/product/aosp_product.mk
[Q-codes]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/standard-headers/linux/input-event-codes.h
[Q-deviceheader]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/include/hw/virtio/virtio-input.h
[Q-vkconfig]: https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/hw/virtio/Kconfig
