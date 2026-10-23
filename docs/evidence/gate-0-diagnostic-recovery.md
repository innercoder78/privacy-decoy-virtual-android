# Diagnostic recovery: enrollment, boot signals and stale inventory

Review: **2026-10-23, America/Fortaleza; source and reasoning only, Windows
x86_64.** [REC-03–05 provenance](gate-0-research-recovery.md) distinguishes original
owner-relayed Codex reports from current source reads. Scope: PDVA-REQ-002–003,
009–015, 035, 039–045 and 054. **Gate 0 Unresolved; Gates A–G Not reached.**
No Android run, storage restore, phone operation or diagnostic activation occurred.

## REC-03 — lost enrollment after manager death

**Recovered owner-relayed failure trace; independently reviewed reasoning:**

1. Management durably records uncertainty for an attempt, then begins binding
   a fixed isolated diagnostic.
2. Management dies before durably recording an authenticated endpoint and its
   completion observation. On restart, enrollment/completion state is missing
   or uncertain; volatile Binder identity and the death subscription are gone.
3. A new endpoint, one-shot token or new user approval does not establish that
   the old attempt ended. Unbinding is not synchronous death acknowledgement.
4. A replacement could overlap uncertain old work. The transition remains
   **NOT READY**, even if the old diagnostic was intended never to create children.

The already merged [lifetime authority](gate-0-android-lifetime-authority.md),
[lifecycle exceptions](gate-0-android-lifecycle-exceptions.md#exit-history-negative-witness)
and [dormant bootstrap](gate-0-android-seccomp-bootstrap.md) supply the surrounding
source constraints. Exit history is bounded; a kill-decision record can precede
confirmed death. Neither it nor one Binder obituary is a whole-tree/resource
completion certificate. A fixed trusted no-child diagnostic may permit limited
observation while management is alive; no qualified missing-record restart
procedure follows. Manual full reboot was a hypothesis requiring an independently
verified boundary, which REC-04 examines separately.

**Reopening condition:** an independently justified enrollment continuity and
exact-attempt completion/recovery procedure that remains sound across this cut.
Do not connect UI/JNI, package or activate the dormant diagnostic while it is
unresolved. User approval cannot replace process/resource evidence.

## REC-04 — boot signals do not certify a new kernel

**Fresh source observations**, all at frameworks/base
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` unless stated otherwise:

| Source inspected | Observation and precise limit |
|---|---|
| [PowerManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/power/PowerManagerService.java), `onBootPhase`, `incrementBootCount` | At `PHASE_THIRD_PARTY_APPS_CAN_START`, reads BOOT_COUNT and writes `count + 1`; missing setting defaults to zero. The shown path has no kernel-incarnation/runtime-restart test. |
| [SystemServer.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/java/com/android/server/SystemServer.java), constructor/startup | Records `mRuntimeRestart` separately and reaches that boot phase without guarding it by the restart flag. Inference: a framework runtime restart can increase an authentic BOOT_COUNT without a new kernel. Not an observed OEM event. |
| [SettingsProvider.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/packages/SettingsProvider/src/com/android/providers/settings/SettingsProvider.java) and [SettingsState.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/packages/SettingsProvider/src/com/android/providers/settings/SettingsState.java) | Global mutation checks WRITE_SECURE_SETTINGS; BOOT_COUNT is not in the critical synchronous-persistence set. SettingsState schedules asynchronous writes. No atomic transaction with the app journal is established. Write restriction is not boot attestation; missing/malformed/overflow values must not authorize recovery. |
| [ActivityManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActivityManagerService.java), boot broadcast to previously stopped app | `wasForceStopped` and unlocked-storage branches can send a genuine BOOT_COMPLETED from system identity during app lifecycle. Authentic sender does not imply fresh kernel boot. |
| [UserController.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/UserController.java), `finishUserUnlockedCompleted` | Boot broadcast belongs to user unlock/start processing; runtime-restart exclusion guards timing statistics, not the following broadcast. Unlock/storage availability is not reboot identity. |

**STOP this design:** BOOT_COUNT plus protected broadcast, unlock state and local
journal cannot certify the required recovery boundary. These source witnesses
falsify the unconditional implication; they do not describe every installed OEM.
Even a true full boot ending the old **fixed trusted diagnostic's** live threads
and old kernel references needs an app-visible predicate that establishes that
boundary. Such a predicate remains UNKNOWN. Copied data, persistent state and
external authority require separate treatment.

Manager restart, framework restart, force-stop, app update, user change,
reinstall/data clear, backup restore and factory reset are distinct events; none
may silently become clean enrollment. A full kernel boot is a different boundary.
Reopening needs an ordinary-app-accessible independent witness and recovery
protocol closing those identity/persistence cases. REC-05 shows why even a valid
one-sided old-clock inference is insufficient for current inventory.

## REC-05 — valid E1 inference, stale inventory

**Source chain rechecked:** [SystemClock.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/os/SystemClock.java)
declares elapsed realtime; [JNI bindings](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/jni/android_os_SystemClock.cpp)
map to libutils. At system/core `545d2487e38192a2ce25040897ced877cf6b4f53`,
[SystemClock.cpp](https://android.googlesource.com/platform/system/core/+/545d2487e38192a2ce25040897ced877cf6b4f53/libutils/SystemClock.cpp)
uses `CLOCK_BOOTTIME` and returns zero on a failed read. Bionic
`06356e41c5ed7b12220b24c05ba4fdb873b126a7`
[vdso.cpp](https://android.googlesource.com/platform/bionic/+/06356e41c5ed7b12220b24c05ba4fdb873b126a7/libc/bionic/vdso.cpp)
dispatches to vDSO or `__clock_gettime`. Linux reference
`adc218676eef25575469234709c2d87185ca223a`
[namespace.c](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/kernel/time/namespace.c)
has time-namespace offsets with capability restrictions. This is a qualification
on clock-domain continuity, not observed ordinary-app authority to change it.
The reference Linux pin is not an installed Android kernel identity.

**Conditional inference:** successful valid ordered readings in the same continuous
clock domain, without overflow, interposition, timebase replacement or snapshot
rollback, satisfy `now >= baseline` during an uninterrupted lifetime. A valid
decrease contradicts that lifetime for the specific trusted baseline. Zero on
failure is invalid. A reboot can yield equal or larger elapsed time. A clock
discontinuity is not independently proof of a full boot or complete worker inventory.

**SYNTHETIC / OWNER-RELAYED counterexample; model not rerun in this recovery:**

1. Boot A: authentic E1 baseline is **120 hours**.
2. Boot B at **15 minutes**: a smaller clock supports only the scoped E1 deduction.
3. Management correctly durably records E2 with a fresh **15-minute** baseline,
   then launches E2.
4. Same Boot B at **20 minutes**: management restarts; storage restores the whole
   old authentic E1 journal. **E2 remains live**, but its record is absent.
5. E1's MAC validates and `20 minutes < 120 hours` remains true for E1.
6. A false policy treats the restored journal as the latest complete inventory,
   then admits E3 alongside still-live E2.

The E1 conclusion is true; E3 authorization is false. Epoch binding prevents
mislabeling E1 evidence as E2 evidence but cannot recover the erased E2 entry.
Assigning E1's high baseline directly to E2 is a separate false-clear negative
control. A MAC, UUID, local generation, backup exclusion or user confirmation
does not independently prove that an authentic local snapshot is current.

**Explicit fault-model assumption:** storage can restore old authentic state
without first terminating E2. This does not attribute manager-storage access to
an isolated hostile worker. If a concrete restore mechanism always terminates
all relevant workers first, that independent invariant must be proved. The
synthetic model assumes trusted management/clock, abstract durable commits and,
for positive cases, a hypothetical external current-generation anchor. It does
not implement that anchor, test Android persistence/clock behavior, or cover
arbitrary execution histories.

Current procedure read the retained report/model/output without execution and
checked the trace logically. The saved **1,348 assertions, no skips** remains an
attributed historical bounded-model receipt. Original scripts/output stay private;
independent backup/durability is not verified. Fresh public-source reads above
are independent source observations, not reexecution of the model.

**STOP automatic replacement under authenticated local history alone.** Missing
freshness retains UNKNOWN/uncertainty lockout; no cross-reboot recovery transition
or production indefinite-lockout policy is adopted. Reopening requires a truly
independent ordinary-app-accessible current-generation/complete-inventory authority
or independently proven termination through restore. Another successful run of
the same finite model, or another clock/JNI survey, would not supply it.

All three cases preserve independent policy admission and the distinctions among
process termination requests, endpoint death, descendants, retained FDs/mappings,
copied data, Binder/device/network authority and exhaustion. None turns protected
management state into trusted execution of a hostile guest CPU.
