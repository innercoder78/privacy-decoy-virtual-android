# Recovery of eight completed research investigations

Review: **2026-10-23, America/Fortaleza; local Windows x86_64.** This is a
documentation recovery, not repeated runtime research. **Gate 0 Unresolved;
Gates A–G Not reached. ADR-0001 Accepted; ADR-0002 Proposed.** Scope:
PDVA-REQ-002–015, 034–045, 048 and 054. No architecture is adopted.

The eight original no-PR conclusions were supplied as **owner-relayed Codex
reports**. That attribution remains even when a source proposition is checked
again. Neither copying a report nor reading a saved test output reproduces a
test. Original archived conversations were not reopened. This public synthesis
does not reproduce the private inventory or handoff. Source observations below
are distinct from historical observations, inferences and still-missing evidence.

**PRESERVED-NOW** below means a public-safe disposition recorded in this recovery
PR, pending owner review, merge and independent verification of main. It does
not mean canonical merged evidence or restoration of every original artifact.
**ALREADY-PRESERVED** identifies earlier merged evidence, not new execution.
Private ignored storage is not an independently verified backup. Where such a
backup could not be verified, the private retention gap remains open.

## Eight dispositions

| ID | Historical objective / nature | Reported historical main | Outcome and preservation disposition |
|---|---|---|---|
| REC-01 | Source review: hand Keystore-protected management state to guest U-Boot | `19a7a56838e118c7756119cbd8e42077b3907727` | **STOP this candidate; PRESERVED-NOW.** New [Keystore handoff limits](gate-0-keystore-boot-handoff.md); firmware baseline ALREADY-PRESERVED in PR #26. |
| REC-02 | Source/desktop-control review: NNP and exact-zero TSYNC in a stock Android isolated service | Exact episode SHA unavailable; no invented pin | **Android UNKNOWN; ALREADY-PRESERVED**, with the historical episode and remaining limits recorded below. Later dormant preparation is PR #27. |
| REC-03 | Lifecycle analysis: manager dies between binding and durable endpoint/completion recording | Exact episode SHA unavailable | **NOT READY; PRESERVED-NOW.** Explicit missing-enrollment trace in the [recovery continuum](gate-0-diagnostic-recovery.md#rec-03--lost-enrollment-after-manager-death). Related lifecycle source findings ALREADY-PRESERVED. |
| REC-04 | Source review: boot count, broadcasts and elapsed time as a recovery boundary | Exact episode SHA unavailable; source revisions recorded separately | **STOP this design; PRESERVED-NOW.** [Authentic boot signals are insufficient](gate-0-diagnostic-recovery.md#rec-04--boot-signals-do-not-certify-a-new-kernel). No Android run. |
| REC-05 | Source and bounded synthetic model: smaller clock versus authentic journal rollback | `b25ebeae0b8e0db06903f65a3e5831b765459191` | **STOP automatic replacement from authenticated local history alone; PRESERVED-NOW.** [E1/E2/E3 counterexample](gate-0-diagnostic-recovery.md#rec-05--valid-e1-inference-stale-inventory). Historical model execution remains attributed. |
| REC-06 | Private source-material format feasibility investigation | Private context not published | **PRIVATE-ONLY-RECOVERY-GAP; UNKNOWN.** No public architecture or runtime-selection evidence. |
| REC-07 | Historical read-only audit of antivirus interference with a synthetic host control | `c2c63c86b5cee06d828d11377508cf54b3c0503e` | **ALREADY-PRESERVED** through PR #8; unrestricted physical handoff remains withdrawn. Original private audit backup unverified. |
| REC-08 | Source review: exact Android release Rust selection and ARM64 target prerequisites | `8a1b60222a380523049ee4caeffa1a2040194fd0` | **PRESERVED-NOW / SOURCE-UNKNOWN** for compiler correspondence. [Rust source-only prerequisites](gate-0-rust-toolchain-prerequisites.md). Backend limitations ALREADY-PRESERVED in PR #31. |

### REC-01: new finding versus earlier firmware evidence

[PR #26](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/26),
merged as `19a7a56838e118c7756119cbd8e42077b3907727`, already preserves the
[firmware assessment](gate-0-android17-uboot.md) and
[immutable ledger](gate-0-android17-uboot-sources.md). The new record adds the
specific public key-use limit versus arbitrary rollback-index distinction and
hostile CPU/RAM enforcement gap. The old report's statement that it created no
PR #27 describes that episode only. Actual later
[PR #27](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/27)
is the distinct dormant seccomp change, merged as
`ec14bbf578ee760512f83456d6e2b90302a44264`.

Fresh pinned source reads are identified in the focused record; no key, firmware
or transport was executed. Reopening requires a concrete independent ordinary-app
authority and enforced fresh boot/state transaction, not another general Keystore
survey. Public disposition is preserved; original private report backup is
unverified.

### REC-02: source/Linux findings do not establish Android installation

The owner-relayed objective was NNP plus irreversible filter stacking, exact-zero
TSYNC, and process denial with legitimate pthread creation. Most content is
ALREADY-PRESERVED in [PR #18](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/18)
(merge `0af04da8fcaad1c69db5b4f3c6459c8f9d433116`),
[seccomp process controls](gate-0-seccomp-process-control.md), PR #27's
[dormant bootstrap](gate-0-android-seccomp-bootstrap.md),
[containment](gate-0-worker-containment.md), its
[source ledger](gate-0-worker-containment-sources.md), and
[QEMU integration](gate-0-qemu-worker-integration.md).

Required distinctions: positive TSYNC TID and negative return both fail setup;
only zero succeeds, with no thread-only fallback. Trusted JNI setup must precede
engine loading and constructors. A child executable needs setup before exec and
a separately restricted parent; a desktop deny-exec filter cannot be reused
unchanged for that launch. Classic seccomp cannot inspect pointed-to `clone3`
flags; this candidate denies it and rejects unreviewed ABIs. Self-report, PID,
`Seccomp:2` and Binder liveness do not attest installation. Initial thread ancestry,
ART/SELinux compatibility, enrollment and bootstrap ordering remain Android
UNKNOWN. The compiled dormant diagnostic is not installed-device evidence.

This recovery read the merged records and existing exact-main hosted logs; it
did not install or rerun the diagnostic. Reopening activation requires independently
reviewed enrollment, trusted pre-exposure installation and cleanup/recovery closure
before separately authorized phone work. Original no-PR report backup is unverified;
the public technical baseline already has durable merged references.

### REC-03–05: related, independently useful failures

The [continuum](gate-0-diagnostic-recovery.md) separates lost endpoint enrollment,
false boot-boundary inference, and true old-epoch inference with stale current
inventory. [PR #19](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/19)
(merge `edc1d4ead49b8f5ac9696e91ceb070925e01e854`) and
[PR #20](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/20)
(merge `49be371f20107f9f2fb098270d68f092f4afb88e`) already preserve
[lifetime authority](gate-0-android-lifetime-authority.md) and
[exceptional lifecycle](gate-0-android-lifecycle-exceptions.md).
[Capability revocation](gate-0-capability-revocation.md), dormant bootstrap and
[desktop journaling](gate-0-desktop-readiness.md) remain related evidence, not
proof of these recovery transitions.

Current verification: public source reads for REC-04/05; read-only inspection of
the retained REC-05 report, model and saved output. The output records **1,348
assertions, no skips**; this remains a historical, bounded synthetic result,
not independently reproduced execution or Android validation. The replay fault,
trusted clock, durable-write and independent-anchor assumptions are explicit in
the focused record. Original REC-03/04 artifacts and independent backup of REC-05
were not established. Public reasoning is preserved without private scripts,
journals, paths, raw output or private hashes.

### REC-06: generic public disposition only

**Owner-relayed Codex report:** private source-material format feasibility
investigation concluded **UNKNOWN; no public architecture or runtime-selection
evidence**. Independently backed-up owner-controlled private evidence could not
be verified: **PRIVATE RECOVERY GAP**. No private material was reacquired or
re-examined in this recovery.

The [generic scanner record](gate-0-offline-image-inspection.md), previously
merged in [PR #29](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/29),
documents a tool, not identification of private material. No scanner defect or
new tool is established. Reopening requires rights-cleared, provenance-qualified
format/build documentation and a matching loader contract. The generic public
disposition does not close the private recovery gap.

### REC-07: preserve the correction, not a renewed safety claim

The owner-relayed audit followed [PR #7](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/7).
The later [PR #8](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/8),
merge `1303dabc44d52db5a7bf35e9de321796dbf2a66e`, substantially preserves it in
[native host antivirus evidence](gate-0-native-host-antivirus.md).
The quarantined synthetic Windows host-control executable was distinct from
the APK and Android payload. Exit-zero overlapping quarantine did not establish
valid control execution; stable APK bytes/build completion did not clear the
physical handoff. Maliciousness versus heuristic false positive remains UNKNOWN.

Current review checked the merged correction and exact-main Linux control
receipts. Those later Linux passes do not retroactively validate the blocked
Windows run, authenticate quarantined bytes, establish signing/host provenance,
or provide a vendor safety verdict. No security logs or private incident metadata
are republished. Original private audit/backup was not re-established. No restore,
allowlist, protection change or execution occurred. Any reopening of the blocked
handoff requires the recorded independent/vendor disposition and separately
qualified artifact/environment evidence; this recovery supplies no clearance.

### REC-08: new toolchain lead, existing backend blocker

Fresh text/metadata retrieval corroborates the release default, Rust selection
and target-library listing. The exact compiler-source and build-recipe endpoints
still return 404; correspondence remains UNKNOWN. The focused record retains
those unsuccessful scopes and distinguishes package metadata from verified bytes.
Retained private source receipts/progress were read, not treated as independent
backup or historical test reproduction. Original compiler availability findings
remain owner-relayed; no installed-toolchain resurvey or binary acquisition ran.

[PR #31](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/31),
merge `8a1b60222a380523049ee4caeffa1a2040194fd0`, already preserves
[backend endpoints](gate-0-backend-endpoints.md) and their
[source ledger](gate-0-backend-endpoints-sources.md). The new toolchain metadata
does not repair the host-only variants, missing library/JNI entry, late pathname
connections, writable guest RAM authority or incomplete dependency closure.
Reopening a build requires legitimate matching compiler/target/linker bytes and
source/license correspondence; no build is authorized by this record.

## Recovery verification and publication boundary

Git `ls-remote`, fetched main and GitHub main API independently agreed on
`8a1b60222a380523049ee4caeffa1a2040194fd0`. The initial tree was clean, one worktree,
no stashes; existing branches and ignored work were preserved. No applicable
AGENTS.md was found. All open-PR inventory was empty, so no pending head/base,
diff, review, thread or check required reconciliation. Merged PR identities and
relevant file history were compared to avoid duplicate recovery. The historical
repository was not modified or imported.

Existing exact-main [foundation run 39876468451](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39876468451)
was the only returned run. Job steps and full logs were retrieved and examined:
[foundation 120163169750](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39876468451/job/120163169750)
and [offline-image-windows 120163169634](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39876468451/job/120163169634)
succeeded. Linux receipts include 141 repository tests, 27 desktop journal tests,
45 scanner tests, seven native wait scenarios and an assertion negative control,
four lifetime cases/four mutants, four real seccomp cases and ten revocation
cases/ten mutants. The Windows job records 45 scanner tests. These are existing
hosted results, not local reruns or Android evidence.

Workflow inspection: foundation applies to this documentation PR; Android and
QEMU path filters do not select these files. Neither absent workflow is a pass.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported All Systems
Operational during preflight. Initial sandbox network/Git-index restrictions
were handled by approved operations without changing repository protections.

Local checks used existing Python **3.11.4**, Windows x86_64, with synthetic test
inputs only. Commands and observed outcomes:

| Command | Actual local outcome |
|---|---|
| `python .github/scripts/validate-foundation.py` | PASS: 126 files, 75 Markdown files, 54 requirements, two ADRs; includes internal file-link and regular-mode checks. |
| `python .github/scripts/validate-harness.py` | PASS: manifest authority; no runtime claim. |
| `python .github/scripts/test-repository-validation.py` | 141 total: 137 passed, four existing Windows/platform skips; no failures. |
| `python .github/scripts/test-desktop-readiness.py` | PASS: 27 tests, no skips. |
| `python .github/scripts/test-offline-image-inspect.py` | PASS: 45 tests, no skips; synthetic fixtures, not private source-material inspection. |
| `git diff --check` | PASS. |

The `python` command above denotes the already installed interpreter, invoked
by its explicit executable path. Skips concern Linux native execution, symlink
and file-mode coverage; they are not passes. The complete six-file Markdown diff,
internal section links, file modes/ownership and authored public text were reviewed
for unsupported claims and private disclosure. Original private artifacts and
the 1,348-assertion model were not executed or published.

The new PR's hosted CI is **pending/unobserved at publication**. No phone, ADB,
Android/guest/QEMU execution, compiler acquisition, native test execution,
security-setting change, diagnostic activation or production behavior change
belongs to this recovery. The [preservation rule](../governance.md#research-preservation)
requires one substantive public-safe evidence PR even for STOP/Unknown outcomes.
