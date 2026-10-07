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
