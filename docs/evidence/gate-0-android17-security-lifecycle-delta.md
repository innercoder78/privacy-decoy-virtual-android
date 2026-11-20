# Gate 0 — Android 17 security-branch lifecycle comparison

**NO NEW QUALIFYING AUTHORITY EVIDENCE.** On 2026-11-20, the Android 17 security
branch differed from the previously reviewed release in ActivityManagerService.
Its single changed line in that file affects creator tokens for nested intents.
It provides no completion receipt for an isolated worker. **Gate 0 Unresolved.
Gates A–G Not reached. Dependent implementation STOP.**

## Question and baseline

Can this framework change give an ordinary installed manager independent proof
of teardown after manager death, including descendants and retained authority?
PDVA main resolved remotely and after fetch to
`3ef791c33205eb58b323c5b539fc468f74eda2b5` (merged PR #96). The open PR list
was empty. GitHub Status reported All Systems Operational. The acceptance boundary
comes from [ADR-0004 Option A](../decisions/ADR-0004-gate-0-owner-disposition.md)
and the [roadmap](../roadmap.md). The earlier [platform authority](gate-0-platform-authority.md)
and [integrated decision](gate-0-integrated-feasibility-decision.md) delimit the
ordinary-app and complete-guest requirements.

## Reproducible source comparison

An exact-ref query against AOSP `platform/frameworks/base` returned
`android17-release` and peeled tag `android-17.0.0_r1` at the prior commit
`94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`. The separately named
`android17-security-release` resolved to `3433336c6477a3b33a6ccb880cd8b06d99139370`.
The comparison uses these two endpoints without assuming a particular OEM build
or patch level. The following Gitiles directory entries had identical Git blob
IDs at both immutable commits. The first three files are in
`services/core/java/com/android/server/am/`.

| File | Git blob at both revisions |
|---|---|
| ActiveServices.java | `32c6f6f031c86d02e75df7474af213ac451ea1df` |
| ProcessRecord.java | `da58696a735690bc9374436662a3a4f3d32762fd` |
| ProcessList.java | `d8e2cfaae0671d20740f11da8698eace47e925d4` |
| core/java/android/os/Process.java | `00dd71b722675356b923decfeb2db3085fab03b3` |
| core/api/current.txt | `572012ca464337b2c65ed83e68a711811d639e61` |

For the differing file, decode each Gitiles TEXT response, hash the bytes and
diff the complete source lines. SHA-256 was
`17923170a97fb001c3892ab4e0d71f9e249f9ea0b427a7aaf29916aae5208797` at release and
`d61d3962392cc4e3d8ffab66eb9c6782d988d2a030b3b53b1dbe48716d2d898b` at the security head.
At line 21101, when an intent lacks an explicit component, the security version
uses a null target for its same-creator comparison. Previously it used the intent's
package field. A package-only match therefore no longer skips creator-token
handling on that basis. Lines 21077–21120 place this decision inside the
flag-guarded handling of nested intents using the Binder caller UID.
[Release source](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/am/ActivityManagerService.java#21101)
and [security-branch source](https://android.googlesource.com/platform/frameworks/base/+/3433336c6477a3b33a6ccb880cd8b06d99139370/services/core/java/com/android/server/am/ActivityManagerService.java#21101).

## Ordinary-app authority and decision

An ordinary app can bind its own non-exported isolated service without a special
grant. The manager retains its app UID and app domain. The worker has a distinct
isolated UID and domain. The changed code runs in system_server and uses caller
identity to attribute an intent. It grants the caller no signal or cgroup
permission, SELinux transition, ownership of the worker's descendants, or Binder
operation for joining cleanup. In the identical ProcessList source, lines 799–810
discard the group-kill result and lines 1689–1699 schedule the operation.
[Security-branch ProcessList](https://android.googlesource.com/platform/frameworks/base/+/3433336c6477a3b33a6ccb880cd8b06d99139370/services/core/java/com/android/server/am/ProcessList.java#799).

After manager death, the changed method neither enumerates surviving processes
nor revokes a retained descriptor, mapping or delegated handle. Whether a given
holder survives on a device remains unmeasured. Unbind, Binder death and process
exit history still supply no independent observation that every holder lost access.
Restart, crash, restore or loss of manager state supplies no fresh enrollment or
authenticated result for the prior worker. The prior
[lifetime trace](gate-0-android-lifetime-authority.md),
[lifecycle exceptions](gate-0-android-lifecycle-exceptions.md),
[revocation](gate-0-capability-revocation.md),
[restore](gate-0-managed-restore-lifetime.md) and
[process history](gate-0-process-history-reconciliation.md) records give the
underlying counterexamples.

**Falsifier.** A completion claim fails if a surviving holder can still use a
previously delegated descriptor after the enforcer reports that the old worker
and its authority are gone. Loss of the observer leaves completion Unknown.
This delta exposes no such result to test. Reopening requires a concrete
ordinary-app-accessible independent enforcer that accounts for descendants and
retained grants across manager loss and can establish a trustworthy fresh boundary.

Only the named framework sources and API signature were compared. Kernel,
SELinux, other framework files, OEM correspondence and device behavior were
outside this comparison. No upstream code was adopted and no Android, native
worker or VM experiment was run. This scoped negative justifies no follow-up
execution or change to the accepted decision.
