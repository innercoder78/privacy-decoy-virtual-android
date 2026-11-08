# Java companion signed-artifact policy: owner assessment only

Date: **2026-11-08, America/Fortaleza**. Reviewed canonical main:
`bcbfb69b48af760b3da936f56fe831ec215fc2a1` (merged PR #69).
**UNAPPROVED assessment; no active policy changes or execution authority.**
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**
Traceability: PDVA-REQ-002–003, 006, 008, 010–013, 036–042, 044–045, 048,
051 and 054. No requirement is amended or marked satisfied.

## Decision and boundary

**Inference:** the separate Java memory diagnostic is a defensible *scope for
considering* a development-only artifact policy, but it supplies no materially
new policy mechanism beyond [ADR-0003's already considered Option B](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md).
No new reproducibility solution has been established. Do not create another ADR
or repeat the settled experiments merely to rename B. Option D's limited
correspondence cannot satisfy strict signed-byte equality; D1/D2 remain closed
at their recorded STOP disposition. Neither B nor D is approved here.

A future explicitly approved companion-only B policy could preserve **PDVA host
APK metadata retention and strict whole-signed-byte requirements intact**, while
also requiring strict equality for the companion's own complete original signed
artifacts. It would deliberately change the companion's metadata policy, not
repair or qualify the original metadata-bearing artifact. This distinction is
not an existing exemption: [PR #67's qualification packet](gate-0-java-memory-diagnostic.md)
currently requires retention and unchanged signing policy for the diagnostic too.
That applicability would need an explicit, dated owner disposition and separately
reviewed governance record before implementation. Package separation alone grants
no authority to reinterpret it. No required check may be removed or made green
when its actual assertion fails.

**Smallest owner decision:** retain STOP, or commission the exact companion-only
application of existing Option B described below for a later policy decision.
The latter commissions documentation and independent review only; it does not
approve B, a metadata opt-out, signing, a build, installation or a physical test.
If the owner wants an active policy exception later, its final scope, costs,
approval and affected companion obligations must first be recorded through
[governance](../governance.md). No new ADR is necessary for this assessment.
Creating or merging this evidence PR expresses no owner choice.

## What is distinct, and what is not

Sources are the exact-main [module](../../android/memory-diagnostic/build.gradle),
[manifest](../../android/memory-diagnostic/src/main/AndroidManifest.xml), four Java
sources, tests, and retained evidence from
[PR #67](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/67),
[PR #68](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/68) and
[PR #69](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/69).
Existing source ledgers supply upstream provenance; no new upstream survey or
private-output inspection was performed.

| Evidence classification | Observation and consequence |
|---|---|
| Current repository observation / #67 | `org.pdva.memorydiagnostic`, versionCode 1 / `0.1-diagnostic`, non-debuggable release, signing configuration null, debug disabled. No full guest, native worker, JNI/executable payload, external runtime library, networking or manifest permission. This is distinct from `org.pdva.gate0` and any eventual PDVA host product. |
| Current source observation / #67 | API exactly 37, ARM64 support, 64-bit process, 4/16-KiB page; one memfd page with separate shared RW/RX mappings, at most 16 KiB backing / 32 KiB mapped extent. No mapping-byte read/write/execution. A deliberate button press commits the one-way marker; cleanup attempts are independent. This is a narrow admission observation, not a guest or code-execution test. |
| Retained direct observation / #68, not rerun | A fresh unsigned build generated a 97-byte report with zero library/edge records but module/repository records, and a nonempty **185-byte encrypted dependency payload**. Fresh/retained reports matched while payloads differed; incomplete old correspondence precludes an independent signed-pair claim. No signed diagnostic was created. |
| Retained source inference / #68 | Pinned AGP/Builder/Signflinger 9.4.0 would insert the nonempty payload under the normal metadata-retaining v2/v3 signing path. The unsigned output's absent signing block does not establish a metadata-free signed artifact. Signed insertion and equality remain unmeasured for this diagnostic. |
| Retained direct observations / ADR-0003 | All **fifteen genuine signed-byte failures** remain failures. Later host pairs localized differences to encrypted dependency information; historical plaintext/random values remain Unknown. None is a signed diagnostic test. |
| #69 and current baseline CI | Installed-tool comparisons and mutation controls can detect bounded inconsistencies. Inventories remain **UNTRUSTED**, not authenticated baselines, incident clearance, source-to-binary reconstruction or build admission. Passing CI does not change that classification. |

The narrower runtime surface reduces what would need qualification; it does not
remove Android framework/kernel trust, build-tool compromise, signing compromise,
substitution or lifecycle risk. Synchronous calls have no hard latency bound;
interruption, process death, ANR or incomplete cleanup remains Unknown. The marker
is an accident-prevention measure, not authenticated physical authorization or a
proof against state rollback. A favorable Samsung mapping result would establish
only that attempt's admission/cleanup observations, not TCG execution, hostile
containment, full-phone feasibility or supported-device coverage.

## Exact limits for any later companion proposal

The candidate is only the source-defined diagnostic above, for one separately
authorized first stock/nonrooted Samsung Android 17 attempt, privately delivered
to the named owner/reviewer. Exact source/tree, variant, final artifact, device
scope and validity window would have to be bound in the private approval packet.
It cannot cover the host/harness APK, guest/image/runtime/helper, debug builds,
public releases, Play distribution, other recipients or future diagnostic versions.
Any source/tool/dependency/capability/audience change requires fresh review; there
is no inheritable "development" exception. The original execution lock stays
unconditional. [ADR-0004 Option A](../decisions/ADR-0004-gate-0-owner-disposition.md)
and all full interactive virtual-phone requirements remain intact.

| Review axis | Required tradeoff and limit; none is discharged here |
|---|---|
| Metadata and maintenance | B would remove this artifact's upstream-recommended dependency-reporting channel. Zero runtime libraries reduces its present library-reporting value, not the need for tool/transitive provenance or future vulnerability monitoring. A named maintainer must preserve exact inventories, notices, advisory review, expiry and withdrawal responsibility. No claim that disabled metadata makes an APK reproducible or safe. |
| Supply chain and security | Independently qualify the entire OS/administration, repository/workflow, JDK, SDK/build tools, Gradle/AGP, Maven metadata/transitives, packaging/signing/verifier chain. Existing 185-component/322-artifact pins include initial TOFU and are not independent authentication. Excluding NDK/native work from this companion does not exclude native build-tool executables from trust. |
| Rights and redistribution | Existing [adoption](gate-0-isolated-worker-adoption.md), [dependency ledger](gate-0-isolated-worker-dependencies.md) and [provenance policy](../source-provenance-policy.md) remain controlling. SDK terms, JDK GPLv2/Classpath Exception and bundled/transitive notices need competent review. Private delivery is still a transfer requiring rights; no tool archive, proprietary package or new license grant is authorized. |
| Signing and future misuse | A dedicated, independently qualified development identity, restricted private recipients and an explicit non-production/non-transferable scope would be necessary. No production/debug/affected-host key reuse; no public artifact upload. Labels and package IDs alone cannot prevent copying or later misuse. Approval must expire on scope change, forbid promotion to host/production evidence and define withdrawal/deletion with verified private retention. No custody system is implemented here. |
| Evidence and checks | Compare two genuine independent complete original signed companion artifacts under the approved signer policy; any byte difference fails. Retain both originals and distinct input/content/signature/whole-byte results. No ciphertext reuse, suppression, deterministic randomness, stripping, copying signing blocks, normalized digest or expected-failure conversion. B is an artifact policy choice, not a comparator exception. |

## Installation blockers and falsifiers

Reuse the [independent-chain NO-GO](gate-0-independent-linux-build.md) and
[diagnostic qualification/conditional procedure](gate-0-java-memory-diagnostic.md),
with the bounded corrections in #59–64 and #69; do not repeat their surveys.
The old unchecked extracted-Gradle finding has scoped corrections, but complete
independent trust is still missing. The [Windows incident](gate-0-native-host-antivirus.md)
remains unresolved. A fresh runner label or a self-generated matching inventory
does not close it.

| Prerequisite still blocking | Concrete falsifier / STOP outcome |
|---|---|
| Explicit companion policy and independent source/security review | Treating this assessment, merge, package name or "Java-only" label as approval; adding a native/guest/payload/network/library capability or extending the audience invalidates this scope. Retain STOP pending a new review. |
| Independent provisioning and authenticated complete build inputs, security disposition excluding incident effects or a qualified independent replacement chain | Shared suspect inputs/credentials/caches, unauthenticated baseline, unreviewed tool changes, incomplete closure or locally promoted UNTRUSTED inventory rejects qualification. Successful builds do not override rejection. |
| Qualified signing custody and independent verification | Missing custodian/backup/recovery, reused disallowed key, wrong signer, invalid signature, verifier failing its tamper control, artifact substitution or leaked signing data rejects the artifact. Valid signatures alone cannot establish whole-file equality or safety. |
| Actual signed-byte proof after separate method/build/signing authorization | Any difference in the complete genuine pair, even metadata-only, fails. Unsigned equality, fixtures, valid v2 signatures or content-only agreement cannot pass. If B later fails equality, STOP; do not silently move to D or remove another source of differing bytes. No successful pair is promised. |
| Authenticated owner-controlled private transfer and independent backup | Missing authenticated source/tool/output/signer binding, recipient mismatch, unverified backup or inability to recover the original evidence blocks delivery/testing. **Independent backup UNVERIFIED; private evidence UNPRESERVED.** No destination is invented. |
| Exact-artifact physical authorization after all qualifications and applicable real checks | Missing authorization/current receipts, unsupported phone/API/ABI/page scope or a platform protection blocking installation means STOP. No Android CLI, ADB, privilege or security-setting bypass. Interrupted/ambiguous result or incomplete cleanup remains Unknown; no data-clear/reinstall retry. |

A new supported metadata-retaining method with genuine independent signed-byte
proof could change the technical blocker and remove the reason to consider B;
none is established here. If the companion cannot remain operationally separate,
or its governance exception would waive a host requirement/check, reject that
proposal. Keeping metadata and accepting limited correspondence instead is the
already considered D policy question, not a distinct companion discovery.

## Live procedure, validation and preservation

Read-only GitHub connector/REST and fetched main agreed on the SHA above. Both
open-PR inventories returned **zero**: complete open heads/bases/diffs/files/modes,
checks/jobs/logs/reviews/comments/threads were an empty set. Merged #67–69 identities,
changes and discussion records were inspected; reviews/comments/review threads
were empty. Requirements, all four ADRs, governance, acceptance/gate/roadmap,
security/provenance/adoption/dependency records, relevant evidence/history,
tracked modes/binary inventory and all three workflows were reviewed.

Exact-main [foundation run 42453506611](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42453506611)
and [Android run 42453506473](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42453506473)
completed successfully: foundation `128647520968`, Windows `128647520732`, Android
`128647520285`. Check/job/step records and completed logs were retrieved. Logs
include unsigned diagnostic checks, ten real STRICT controls and 600 execution-lock
denials with three rejected mutants. These are baseline receipts, not new local
experiments or companion signing qualification. Legacy status was pending with
zero contexts; QEMU had no exact-main run. [GitHub Status](https://www.githubstatus.com/api/v2/summary.json)
reported All Systems Operational, no incidents, page update
`2026-11-08T15:09:39.377Z`. Initial sandbox network/Git-write denials were resolved
by scoped approvals; a CLI terminal-escape log-output refusal was resolved by
retrieval with display controls removed. None is a project test result.

Only this original assessment and its evidence-index entry change. No new source,
binary, dependency, license, requirement, ADR, signing configuration, metadata
setting, workflow or required check changes. All historical failures and the lock
remain intact. Existing five worktrees, branches, stashes (none initially), dirty
files (none initially in the primary checkout), ignored assets and private receipts are preserved; no
private receipt or inventory was opened for this assessment or copied publicly.

Actual local validation on Windows with bundled CPython 3.12.14:
`validate-foundation.py` passed (**181 files, 110 Markdown files, 54 requirements,
four ADRs**); `validate-harness.py` passed; `test-memory-diagnostic.py` passed
source policy and specific RWX/INTERNET negative controls without Java/APK options.
`test-repository-validation.py` completed **152 tests: 148 passed, four existing
Windows skips**, not passes. Full final text diff, local link targets, requirement/
ADR references, regular 100644 modes, whitespace, rights/provenance, privacy and
workflow applicability were reviewed; no new tests or validator changes were needed.

No APK build/signing, metadata experiment, key creation, installed-tool scan,
independent acquisition/security qualification, Android CLI, device/USB/ADB,
native/guest execution or physical test was run. No new source/security/rights
qualification is inferred from reviewing prior evidence. Private paths, inventories,
hashes, receipts, keys and samples remain off public GitHub.

The unchanged foundation workflow applies automatically, including its existing
host controls; Android and QEMU path filters do not select this two-document diff.
No workflow is manually dispatched; filtered/unrun checks are not passes.
New-head CI is **UNOBSERVED at publication**. Publish exactly one PR, attach it
natively to this chat, verify association once, then STOP without polling CI,
reviews, comments, bots, badges or mergeability. No owner policy choice or physical
authorization is implied by creation or merge.
