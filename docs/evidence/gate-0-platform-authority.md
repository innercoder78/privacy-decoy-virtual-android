# Gate 0: ordinary-app platform authority

**Gate 0 status: Unresolved.** **Observation/retrieval date: 2026-10-07.**
**Method:** read-only authoritative source/document inspection in Codex Desktop
local mode. No VM, guest image, app, emulator or physical device was executed.

## Scope and evidence terms

The question is whether an ordinary distributable user-installed third-party app
on supported stock non-rooted production Android can legitimately obtain a
mechanism, authority and guest configuration suitable for PDVA's full interactive
Android phone and defensible guest/host separation. This is narrower than asking
whether Android has virtualization and broader than asking whether AVF is public.

Use [PDVA evidence terms](../acceptance-evidence-criteria.md): the code below gives
source-code observations, official documentation gives verified platform facts
within its stated scope or upstream architectural descriptions, and candidate
exclusions are explicitly scoped inferences. No direct PDVA runtime observation
exists. Unknown is missing evidence; Unsupported is a product disposition, not
an automatic conclusion from missing evidence.

## Exact source identities

Refs were resolved through the official Gitiles `+refs?format=JSON` endpoint;
files were retrieved at immutable commit URLs using Gitiles TEXT and inspected.
Moving `main` is a separately inspected snapshot, not assumed newer than a release.

| Repository | Retrieved ref | Commit / tag object |
|---|---|---|
| platform/packages/modules/Virtualization | refs/heads/main | `175a51b30123fa6b02b541f1969665708f7ec2c3` |
| platform/packages/modules/Virtualization | refs/tags/android-17.0.0_r1 | Peeled commit `22f1c9ee92b146e10c8f5e71338618f77ab1631e`; tag object `ebd97321b98872cfedb76dbac693f22033d4481b` |
| platform/system/sepolicy | refs/heads/main | `4571ddd9440721fec583c906a337de949a77749e` |
| platform/system/sepolicy | refs/tags/android-17.0.0_r1 | Peeled commit `e066568e98d86db31a9346d30977f3632fa7073c`; tag object `689b4b99b953ff2c29a2f1b520e9361a7cc7b633` |

No other Android 17 tag was returned in those two ref listings at retrieval.
Commit/path identities below identify the reviewed blobs without relying on
moving URLs. These are source snapshots, not a claim about every OEM shipping build.

| ID | Source area | Immutable sources | What was inspected |
|---|---|---|---|
| V1 | `android/android.system.virtualmachine.res/AndroidManifest.xml` | [main](https://android.googlesource.com/platform/packages/modules/Virtualization/+/175a51b30123fa6b02b541f1969665708f7ec2c3/android/android.system.virtualmachine.res/AndroidManifest.xml), [Android 17](https://android.googlesource.com/platform/packages/modules/Virtualization/+/22f1c9ee92b146e10c8f5e71338618f77ab1631e/android/android.system.virtualmachine.res/AndroidManifest.xml) | Permission definitions; both refs retain restricted protection levels. |
| V2 | `libs/framework-virtualization/README.md` | [main](https://android.googlesource.com/platform/packages/modules/Virtualization/+/175a51b30123fa6b02b541f1969665708f7ec2c3/libs/framework-virtualization/README.md), [Android 17](https://android.googlesource.com/platform/packages/modules/Virtualization/+/22f1c9ee92b146e10c8f5e71338618f77ab1631e/libs/framework-virtualization/README.md) | Upstream API documentation: SystemApi and restricted MANAGE authority; development grants are distinct. |
| V3 | `android/virtmgr/src/aidl.rs` | [main](https://android.googlesource.com/platform/packages/modules/Virtualization/+/175a51b30123fa6b02b541f1969665708f7ec2c3/android/virtmgr/src/aidl.rs), [Android 17](https://android.googlesource.com/platform/packages/modules/Virtualization/+/22f1c9ee92b146e10c8f5e71338618f77ab1631e/android/virtmgr/src/aidl.rs) | main contains VM configuration/permission checks; Android 17 file re-exports types after refactoring. |
| V4 | `build/microdroid/README.md` | [main](https://android.googlesource.com/platform/packages/modules/Virtualization/+/175a51b30123fa6b02b541f1969665708f7ec2c3/build/microdroid/README.md), [Android 17](https://android.googlesource.com/platform/packages/modules/Virtualization/+/22f1c9ee92b146e10c8f5e71338618f77ab1631e/build/microdroid/README.md) | Upstream guest description: headless native workloads, no SystemServer/HALs/GUI. |
| V5 | `docs/custom_vm.md` | [main](https://android.googlesource.com/platform/packages/modules/Virtualization/+/175a51b30123fa6b02b541f1969665708f7ec2c3/docs/custom_vm.md), [Android 17](https://android.googlesource.com/platform/packages/modules/Virtualization/+/22f1c9ee92b146e10c8f5e71338618f77ab1631e/docs/custom_vm.md) | Root/ADB custom-VM recipe; Terminal GUI support does not establish ordinary-app launch authority. |
| V6 | `android/virtmgr/src/virtualmachine.rs` | [Android 17](https://android.googlesource.com/platform/packages/modules/Virtualization/+/22f1c9ee92b146e10c8f5e71338618f77ab1631e/android/virtmgr/src/virtualmachine.rs) | Release implementation of custom-configuration and permission checks; followed from refactored aidl.rs. |
| S1 | `private/crosvm.te` | [main](https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/crosvm.te), [Android 17](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/crosvm.te) | VM-manager/KVM access and system crosvm execution exclusions. |
| S2 | `private/app.te` | [main](https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/app.te), [Android 17](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te) | App-domain process/transition constraints; not a blanket denial of every virtualization service contact. |
| S3 | `private/untrusted_app_all.te` | [main](https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/untrusted_app_all.te), [Android 17](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/untrusted_app_all.te) | Test/demo service use allowed but separately permission guarded; stale permission-level comment noted below. |
| S4 | `private/virtualizationmanager.te` | [main](https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/virtualizationmanager.te), [Android 17](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/virtualizationmanager.te) | Specialized manager domain and crosvm transition authority. |
| S5 | `private/vmlauncher_app.te` | [main](https://android.googlesource.com/platform/system/sepolicy/+/4571ddd9440721fec583c906a337de949a77749e/private/vmlauncher_app.te), [Android 17](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/vmlauncher_app.te) | Special launcher policy exceptions; ordinary installed apps do not acquire this domain by naming a binary. |

| ID | Official documentation (retrieved 2026-10-07; live pages, no immutable revision claimed) | Establishes / limitation |
|---|---|---|
| D1 | [Android 17 all-app changes](https://developer.android.com/about/versions/17/behavior-changes-all) | Android 17 is API 37; device-RAM-based app memory limits. Does not establish an emulator's viable memory budget. |
| D2 | [Android 16 release notes, virtualization](https://source.android.com/docs/whatsnew/android-16-release#virtualization) | LL-NDK permits vendors to launch VMs from the vendor partition using managed AVF; not a user-installed application API grant. |
| D3 | [AVF architecture](https://source.android.com/docs/core/virtualization/architecture) | pKVM is the hypervisor component, with kernel/firmware/hardware dependencies; not an app permission bypass. |
| D4 | [Android process lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle) | Processes can be terminated according to importance/resource pressure; no indefinitely resident app entitlement. |
| D5 | [Android 10 executable restrictions](https://developer.android.com/about/versions/10/behavior-changes-10#execute-permission) | Target-29+ apps cannot directly execute files from writable app home; packaging/JIT strategy needs separate analysis, not a blanket claim that all CPU emulation is forbidden. |
| D6 | [Application sandbox](https://source.android.com/docs/security/app-sandbox) | UID/kernel/SELinux sandbox applies to native code too; it does not prove a guest cannot compromise a VMM sharing the app's authority. |
| D7 | [Android 17 release notes](https://source.android.com/docs/whatsnew/android-17-release), [targeted-app changes](https://developer.android.com/about/versions/17/behavior-changes-17) | Current release/restriction review context; no ordinary third-party AVF grant established. |

## Observations and scoped conclusions

1. **Source/document observation (V1/V2):** AVF Java VM APIs remain `@SystemApi`
   and require `android.permission.MANAGE_VIRTUAL_MACHINE`. Both inspected
   manifests declare `signature|preinstalled|development`. This is not ordinary
   user-installed production-app authority. Android 17 adds the
   `allowedInPrivateComputeCore` permission flag; it does not make the permission
   a normal user-grantable runtime permission.
2. **Source observation (V1/V3/V6):** `USE_CUSTOM_VIRTUAL_MACHINE` is
   `signature|development`, with an explicit third-party exclusion in the
   manifest. Raw configurations, a non-Microdroid OS and enumerated custom
   AppConfig options are treated as custom. Both implementations call the custom
   permission check; a full guest cannot inherit authority merely because a
   limited payload can run.
3. **Version distinction:** Android 17 `aidl.rs` re-exports types; relevant checks
   are in `virtualmachine.rs` (VM creation around lines 661–669, classification
   around 910–935, permission helper around 1400–1407). The main snapshot retains
   these in `aidl.rs` (around 674–682, 1040 onward and 1630 onward). Do not cite
   release `aidl.rs` as if it still contained those checks.
4. **Policy observation (S1–S5):** KVM/VM-manager access is granted to crosvm's
   specialized domain; neverallow rules exclude ordinary app domains. The tagged
   policy uses `crosvm_domain`/manager domain attributes where main uses
   `crosvm` names. System `crosvm_exec` execution is restricted to specialized
   manager/launcher/helper exceptions. The shell `getattr` exception is not
   general KVM use.
5. **Important qualification (S3):** `virtualizationservice_use(untrusted_app_all)`
   exists for test/demo use. It does not remove the permission check. Its comment
   says the older `signature|privileged|development`; V1's actual manifest is
   authoritative for the current declared level. It would be incorrect to claim
   that SELinux blocks every Binder contact with AVF or that this macro grants
   ordinary production VM authority.
6. **Documentation and inference (D3 with V1/S1):** pKVM enforces beneath the
   Android virtualization stack; naming it does not supply a public ordinary-app
   route around the stack's access controls.
7. **Documentation (V5/D2):** shell `vm`, root/ADB recipes, development grants,
   platform signing, preinstallation and vendor integration do not satisfy PDVA's
   normal contract. Terminal GUI capability or a special launcher package does
   not establish equivalent rights for an independently installed PDVA app.
   Android 16's LL-NDK change explicitly concerns vendor-partition integration.
8. **Upstream guest description (V4):** Microdroid omits the normal SystemServer,
   HAL and GUI environment and targets headless native workloads. Independently
   of access restrictions, it does not satisfy Gate A's complete-phone requirement.
9. **Verified documented restriction (D1):** Android 17 introduces app memory
   limits tied to total device RAM. D4/D5 add lifetime/executable constraints.
   An ADB-adjusted memory limit is a research condition, not acceptable production
   evidence. No numeric safe budget, JIT entitlement or emulation performance
   result is inferred here.

## Candidate authority matrix

“Scoped negative” means the inspected route does not meet the ordinary installed
production-app authority category. It is not universal Android impossibility.
No row is a selected engine or architecture.

| Candidate | Production access class | Required API/service/device authority | Guest configuration authority | Production user build without prohibited setup? | Evidence / disposition |
|---|---|---|---|---|---|
| AVF Java/SystemApi | Preinstalled/platform-authorized; development grants separately | SystemApi, VM service, MANAGE permission | Normal payload path is Microdroid; custom options separately gated | **No for ordinary user-installed app under inspected permissions** | V1/V2; scoped negative |
| AVF raw/custom VM | Platform-signed or development-authorized, not ordinary app | VM service, MANAGE plus USE_CUSTOM permission | Raw/non-Microdroid/custom configuration requires separate restricted authority | **No for target access class** | V1/V3/V6; scoped negative |
| pKVM through Android stack | Authorized platform/AVF client | AVF/crosvm/kernel hypervisor path and the above access controls | Guest support also constrained by stack/configuration | **No independent ordinary-app bypass** | D3 + V1/S1; scoped negative for this route |
| Direct system crosvm invocation | Specialized manager/launcher domains and enumerated helpers | crosvm_exec execution/domain transition, VM-manager device access | Invoking a binary cannot confer custom-image or device rights | **No for ordinary app domain** | S1/S4/S5; scoped negative |
| Direct /dev/kvm or equivalent VM-manager device | Specialized crosvm path; limited policy exceptions | Device node open/ioctl, kernel facility and SELinux authority | Hardware support alone does not grant VM creation/configuration | **No under inspected AOSP app-domain policy** | S1/S2; scoped negative |
| Shell vm tooling | Shell/ADB, often root/debug workflow | /apex/com.android.virt/bin/vm, service authority, development setup | Rooted custom configuration is documented; not app authority | **No under PDVA production contract** | V5; scoped negative |
| AVF LL-NDK | OEM/vendor/platform component | Vendor-partition integration with managed AVF and platform policy | Vendor configuration is not an ordinary-app custom-guest grant | **No for target access class** | D2; scoped negative |
| Pure user-space VMM / software CPU emulation | Hypothesized ordinary app sandbox | Packaged code/interpreter or permissible JIT; host APIs, process/memory/storage authority; no assumed KVM | Full Android 17 machine/boot/device model not demonstrated | **Unknown** | D1/D4/D5/D6 constrain research; no engine or proof |
| Other legitimate shippable mechanism | Unknown; must explicitly fit ordinary app category | Unknown; enumerate every helper, grant and kernel/service dependency | Unknown for required complete guest | **Unknown** | Survey incomplete; no additional qualifying mechanism established |

| Candidate | Host/ABI/hardware/OEM dependencies | Shippability, provenance and TCB | Runtime constraints / remaining Unknowns |
|---|---|---|---|
| AVF Java | APIs documented from Android 14/API 34; AVF feature/capabilities vary; device support not claimed | Platform-delivered service/APEX/kernel plus app; no adoption or redistribution audit | Limited guest class; ordinary access excluded; authorized-client limits not measured |
| AVF custom | AVF/device/firmware and custom-VM configuration dependent | Platform service, crosvm/device model, guest kernel/image; rights and full configuration unreviewed | Full Android device model and performance unproven despite access negative |
| pKVM stack | ARM64/hypervisor/GKI/firmware/OEM configuration; x86_64 testing differs | Kernel/hypervisor, firmware, stack and devices form prospective TCB | Availability does not grant use; full guest and resource behavior unmeasured |
| Direct crosvm | Installed APEX binary, SELinux labels, manager/helper domains, kernel VM facilities | A system binary's presence/license is not permission to execute; repackaging reviewed separately | Bundling the same binary would not confer its SELinux domain or KVM authority |
| Direct VM device | Kernel/hardware support and enforced device labels/policy | Host kernel/hypervisor/device surface; no shipped helper adopted | Read-only metadata or hardware capability probes are not creation rights |
| Shell vm | Debug/ADB/root setup and AVF-enabled target | Development platform tools only, no production helper design | Research only; cannot require setup once then call it ordinary-app operation |
| LL-NDK | Android 16+ vendor integration and device platform build | Vendor/platform maintenance and TCB; no ordinary distributable app path | Vendor configuration and performance not tested; contract exclusion is enough |
| User-space emulation | Host minimum Unknown; ARM64 priority; guest/host ABI, page size, graphics and OEM limits untested | Need immutable source/license, dependency/binary inventory, reproducible packaging and review of interpreter/JIT/device-model TCB; no engine selected | CPU execution/JIT, full boot, memory limits, graphics, latency, audio, storage, battery/thermals, process death/background and management isolation all Unknown |
| Other mechanism | Unknown | Must pass full source/adoption and ordinary-app authority review | Unknown; no success inferred from survey gaps |

## Limitations and next falsifiable questions

These are independently read source/doc observations, not tests of installed OEM
policy, app behavior, distribution approval, legal rights or production isolation.
Initial web rendering failed for some Gitiles files; direct official TEXT retrieval
at the recorded commits succeeded. A guessed libavf README path returned 404;
no claim relies on that missing file. LL-NDK classification relies on the official
Android 16 release documentation, not an invented public native SDK entitlement.

Next research must ask:

- Can a concretely identified candidate package its CPU execution mechanism and
  required native code legitimately for an ordinary app, without hidden grants,
  executable-policy bypasses, system helpers or KVM?
- Does its guest configuration model plausibly cover Android 17's complete boot,
  SystemServer/Zygote, virtual devices and interactive graphics? What smallest
  authority/configuration test could falsify that hypothesis before Gate A work?
- What exact host API/ABI/device scope and memory envelope remain after normal
  process/background, storage and thermal limits, without ADB exemptions?
- Which component enforces guest-native containment, and can a device-model or
  translator compromise reach management secrets? What separate host authority
  protects management and peer instances?
- Are its source, licenses, transitive dependencies, generated/native binaries,
  update ownership and distribution route defensible?

The [follow-up source survey](gate-0-userspace-vmm-sources.md) now identifies
QEMU/TCG as the lead user-space candidate and records Android packaging precedents
and isolated-process policy. The [separate proof proposal](gate-0-isolated-qemu-proof.md)
defines the smallest next physical experiment, controls and stop conditions.
Neither record selects an engine or supplies execution evidence. No VM is
implemented or run here. **Overall Gate 0: Unresolved.**
The scoped negative platform routes do not eliminate pure user-space emulation or
all other legitimate mechanisms. PDVA feasibility is not established or disproven.

## Android 17 authority delta check — 2026-10-31

**Result: no new qualifying ordinary-app execution authority found; STOP this
bounded source investigation. Gate 0 Unresolved; Gates A–G Not reached.
Physical-test readiness: NOT READY — STOP.** This is a delta against merged
PDVA evidence, not a claim that Android 17 adds no APIs or that software emulation
is impossible. No implementation, dependency, requirement or security boundary changes.

### Baseline and procedure

Codex Desktop local mode, Windows x86_64, America/Fortaleza. Live GitHub branch
and commit queries agreed with clean local main
`12a7549464239aeb07f01bdae84f607f4641a504`. The paginated open-PR collection was
empty: no open heads, diffs, reviews, threads or checks remained to inspect.
Exact-main [foundation run 41169122616](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41169122616)
reported completed successful `foundation` and `offline-image-windows` checks;
their logs were not reread and are not fresh local test evidence. Legacy status
had zero contexts; its aggregate pending value is not another check.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported all
systems operational, updated `2026-10-31T17:09:41.552Z`. One worktree, no stashes,
existing branches and ignored build/tool/source assets were inventoried and
preserved. No applicable workspace/ancestor AGENTS.md was found.

Before selecting sources, reviewed the roadmap, requirements, gates, governance,
ADRs, provenance/dependency records and relevant history, plus this record,
[userspace sources](gate-0-userspace-vmm-sources.md),
[strict TCG memory](gate-0-tcg-executable-memory.md),
[integrated decision](gate-0-integrated-feasibility-decision.md),
[lifetime](gate-0-android-lifetime-authority.md),
[recovery](gate-0-diagnostic-recovery.md),
[native launch](gate-0-isolated-native-launch.md),
[readiness audit](gate-0-native-launch-readiness-audit.md) and
[Memory Limiter](gate-0-android17-memory-limiter.md). ADR-0001 remains Accepted;
ADR-0002/0003 remain Proposed, with only ADR-0003 Option A approved. PR #50's
research-preservation disposition is retained without reopening its experiment.

Used the selected official Google Android CLI skill with installed version
1.1.16717390 as previously verified by the owner; version was not remeasured.
After inspecting documented effects, per-command sandbox approvals covered
`android --no-metrics docs search --help` and documentation searches for
`Android 17 API 37 memfd_class executable memory isolatedProcess` and
`Android 17 nativeService executable memory`. The latter returned memory-budget,
Android 17 summary/behavior and memory-management pages, not an authority proof.
Search ranking is not evidence of absence. No init, installation, SDK change,
credentials, device, ADB, emulator or cloud service operation was performed.

Read the official [features](https://developer.android.com/about/versions/17/features),
[all-app changes](https://developer.android.com/about/versions/17/behavior-changes-all),
[target-37 changes](https://developer.android.com/about/versions/17/behavior-changes-17),
[release notes](https://source.android.com/docs/whatsnew/android-17-release) and
[36→37 API diff](https://developer.android.com/sdk/api_diff/37/changes/changes-summary),
following only relevant native-memory, process and binding entries. Live pages
were retrieved on this date; no immutable website revision is claimed. The API
diff labels itself generated `2026.03.25 19:47`; it is not proof about every later
37.x feature. Current reference pages can include later minor-version APIs.

Fresh official Gitiles `+refs?format=JSON` reads returned only
`android-17.0.0_r1` among Android 17 tags in each of the following projects.
Both that tag's peeled commit and `android17-release` matched prior evidence:

| Project | Unchanged immutable release commit |
|---|---|
| platform/system/sepolicy | `e066568e98d86db31a9346d30977f3632fa7073c` |
| platform/frameworks/base | `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` |
| platform/packages/modules/Virtualization | `22f1c9ee92b146e10c8f5e71338618f77ab1631e` |

These are per-project reference identities, not an installed OEM image or complete
release manifest. SELinux main also remains `4571ddd9440721fec583c906a337de949a77749e`.
Retrieved the following release files with Gitiles `?format=TEXT`, base64-decoded
in memory without newline conversion, inspected relevant rules and calculated
SHA-256. All four match the existing [containment ledger](gate-0-worker-containment-sources.md).

| File at the SELinux commit above | Fresh decoded-byte SHA-256 |
|---|---|
| [public/te_macros](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/public/te_macros) | `9825ba9b9bd742070683f21ad636e930ec24c73e3ec9dcb22b85e2dcb9b0367d` |
| [private/app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/app.te) | `6a18ae176e35cf19ab022cc75887a5c77aae55f00e8a1ebddd7ebd75aea64525` |
| [private/isolated_app.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app.te) | `a088dfeaf2dabbfcd4327c01549096c88db22687c2fceb51c797ede552bb2d51` |
| [private/isolated_app_all.te](https://android.googlesource.com/platform/system/sepolicy/+/e066568e98d86db31a9346d30977f3632fa7073c/private/isolated_app_all.te) | `e65adb199d7fc26cd716f4e376f6068edcd3c350647f121e8d5937fa9bca4ad9` |

### Candidate deltas and falsifiable disposition

**Official claim:** [policy compatibility, Android 17 shared memory](https://source.android.com/docs/security/features/selinux/compatibility#shared-memory-changes-for-android-17)
requires `memfd_class` on launching devices meeting both vendor API 202604+
and android16-6.12+ kernel conditions. It labels memfds with the allocating
process context and uses `memfd_file`, enabling finer policy distinctions.
Enabling it is an OEM policy/image operation, not an app permission or SDK switch.

**Source observation:** `app_domain` already grants execute/getattr/map/read/write
on `appdomain:memfd_file` alongside executable app tmpfs; `app.te` grants
appdomain self-process `execmem`; `isolated_app` invokes `app_domain`.
**Inference:** this is an already assessed mapping route under platform policy,
not a newly discovered JIT entitlement. Neither the macro nor separate RW/RX
aliases contains hostile native code after worker compromise. Installed kernel,
seccomp, SELinux, FD authority and exact allocator behavior remain independent.

| Screened mechanism | Production access/API and constraints | Delta disposition / falsifier |
|---|---|---|
| memfd/JIT policy migration | Ordinary app/isolated domain only within actual kernel/SELinux/seccomp policy; no new runtime permission. OEM enables the class under the conditions above. ARM64 instruction-cache/BTI, 4/16-KiB pages, executable memfd and strict split-wx still need exact-build proof. No new lifecycle or distribution entitlement. | Same pinned rule and hash already assessed. A changed applicable execute rule or kernel enforcement contract affecting the selected allocator would reopen this comparison; a policy label alone does not. |
| API 37 [NativeService](https://developer.android.com/ndk/reference/group/native-service) | Already assessed ordinary isolated native-service entry path, `android:nativeService` with `isolatedProcess`; API 37 host and packaged ABI-compatible native entry required. No ART-dependent API assumption; documented NDK subset applies. No extra JIT/device rights, persistence or tree-cleanup receipt; packaged-code provenance/distribution review remains required. | New relative to older Android, **not new to PDVA evidence**. No changed native authority contract found. Successful native loading alone would not qualify TCG or the complete guest. |
| API 37 [Context binding updates](https://developer.android.com/reference/android/content/Context#updateServiceBindings(java.util.Collection%3Candroid.content.Context.UpdateBindingParams%3E)) | Public ordinary-client APIs on existing bindings: rebind with permitted flags or batch rebind/unbind; no additional special permission is documented for these operations. Existing service access controls apply. No new native ABI/JIT/kernel device access or distribution privilege. | Official contract permits changes to enumerated importance-related flags; batch behavior is ordered rebind/unbind. **Inference:** it supplies no independent descendant-empty/resource-revocation receipt or survival guarantee. A documented identity-bound completion guarantee would falsify this exclusion. Server-side implementation correspondence was not freshly established. |

The focused API diff also adds [Os.dladdr](https://developer.android.com/sdk/api_diff/37/changes/android.system.Os),
[Process.isPrivateComputeCoreUid](https://developer.android.com/sdk/api_diff/37/changes/android.os.Process),
[ANR listeners](https://developer.android.com/sdk/api_diff/37/changes/android.app.ActivityManager)
and [ANR information](https://developer.android.com/sdk/api_diff/37/changes/android.app.ApplicationExitInfo).
These entries establish no executable-memory grant or whole-worker completion
contract. [PccSandboxManager](https://developer.android.com/reference/android/app/privatecompute/PccSandboxManager)
describes PCC interaction/migration and identity queries, not ordinary-app custom
guest authority; its later-version egress API requires a valid PCC sandbox.
No PCC access class, platform trust or restricted AVF permission is conferred
merely by a public query or service name. No new candidate is adopted.

### Limits, remaining blockers and next proof

**Unknown:** OEM applicability, installed execution/JIT behavior, useful memory
and performance budgets, distribution acceptance, and complete adversarial
containment. Existing memory-limit and process-death constraints remain; neither
profiling nor binding-priority updates supplies exemptions. Restricted AVF/custom
VM routes retain their recorded exclusions. This bounded negative is not an
exhaustive search of every Android branch or a universal impossibility proof.

The integrated decision is unchanged: reference R is STOP; software hypothesis H
has no coherent qualified build/device/backend graph. Full boot/services,
interactive graphics/input/audio, protected boot state, provenance and resource
budgets remain blocked. Management/Persona secrets must remain outside hostile
guest/worker authority; independent enrollment, descendant termination,
retained-FD/mapping revocation and recovery remain unresolved. More native code
or a cooperative service callback cannot establish that boundary.

Reopen only for a concrete authoritative permission/API/enforcement delta with
ordinary production access and a falsifiable effect on an identified missing
edge. The existing narrow installed native-launch proof remains conditional on
its unchanged readiness prerequisites and separate authorization; it is **not
ready or authorized here**, and a positive result would not prove JIT or a guest.
No repeated build, model, native experiment or general survey follows this result.

Retrieval limits: sandboxed Git network access failed; approved read-only GitHub
queries succeeded. Web Gitiles rendering failed; approved PowerShell TEXT reads
succeeded for the four policy files. An initial Python retrieval never ran
because PATH resolved to an unavailable launcher. A fresh pinned `Context.java`
TEXT request returned HTTP 503; no hash or source finding is claimed from it.
Binding conclusions above rely on the official public contract, not a fabricated
implementation observation. Existing immutable framework evidence is retained.

Publication resumed on **2026-11-03** without repeating source research. Live
main remained the same SHA; open PRs and all-state PRs for the intended branch
were empty. Both exact-main checks still reported success. The source findings
and website retrieval dates above remain October 31 observations.

**Actual local validation:** existing NDK-bundled Python 3.11.4 ran foundation
validation (147 files, 92 Markdown files, 54 requirements, three ADRs), harness
authority validation, 149 repository tests (145 passed, four existing Windows
skips), and four frame-copy tests successfully. Desktop-readiness and offline-image
tests were started, but completion output was unavailable after interruption;
their sessions/processes no longer existed on resume. Results are **unverified**,
not passes. No previous ignored files were removed. Final foundation validation,
local-link/anchor, UTF-8, full two-file diff, regular `100644` modes, privacy,
provenance/license scope and whitespace were checked before commit.
**Not Run:** Linux native/process suites, Android builds/runtime, JIT mappings,
guest/VM/QEMU execution, devices, performance or physical security tests.

Only this dated
addendum and its index entry are changed. References and brief original analysis
import no implementation or binary; existing file-level licenses, dependencies
and adoption obligations remain unchanged. Public-data review excludes private
paths, credentials and device/Persona data. New-head hosted CI is unobserved;
foundation applies, Android/QEMU workflows are path-filtered, not passing results.
Publish exactly one PR, attach natively, verify association once, then STOP
without polling checks, reviews, bots or mergeability.
