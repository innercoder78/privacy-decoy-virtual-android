# Gate 0: compiled APK extraction-policy verification

Date: **2026-10-29, America/Fortaleza**. Scope: PDVA-REQ-036–043, 048,
050–051 and 054. **Gate 0 Unresolved; Gates A–G Not reached. Physical native
launch NOT READY — STOP.** ADR-0001 Accepted; ADR-0002 Proposed.

## Question and disposition

Can the shared offline validator reject a compiled APK whose referenced extraction
policy differs materially from the reviewed source while other manifest authority
fields remain acceptable? **Yes, for the exercised compiled fixtures and supported
SDK output format.** The original omission identified by
[PR #47's evidence](gate-0-managed-restore-lifetime.md) is corrected in
[validate-harness.py](../../.github/scripts/validate-harness.py). Both its CLI
and [desktop-readiness.py](../../.github/scripts/desktop-readiness.py) require the
new check. No application manifest, resource policy or runtime behavior changes.

This establishes packaged bytes and reviewed policy semantics. It does not prove
Android/OEM restore enforcement, artifact safety, signing trust, source-to-binary
reproducibility or complete worker cleanup. No recovery mechanism is adopted.

## Live preflight and preserved work

Canonical main independently read by `git ls-remote origin refs/heads/main` was
`7a39cd954c3df084232a433996c46c0a44478ac5`, tree
`092cf46808cb4a3a45bd7b034771e3d5c01aa062`. PR #47 is merged from head
`25676d2daa0160d1f07a1d25e90ffb5ecda25ea7`; its merge is that main commit.
The live open-PR search returned **zero**: open heads/bases, complete diffs,
modes, checks/jobs/logs, reviews/comments/threads and dependencies were an empty
set. No existing intended PR needed reuse.

Exact-main [foundation run 40800406511](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40800406511)
completed successfully: jobs `123206875818` (foundation) and `123206875632`
(offline-image-windows). Job/step metadata and the foundation execution log were
inspected. Those are baseline hosted results. Android and QEMU workflows were
not selected by PR #47's documentation paths, not passing Android builds.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported All
Systems Operational, update `2026-10-29T05:25:25.715Z`, no active incidents.

Initial tracked checkout was clean, with one registered worktree and no stashes.
Local/remote branches, ignored toolchains, caches, APKs and research directories
were inventoried and preserved. No applicable AGENTS.md was found. The single
branch starts at verified main. No reset, clean, restore, stash pop, force push,
security exclusion or quarantine operation occurred. Sandbox network denial was
resolved through an approved read-only query; it was not counted as verification.

Read requirements, Gate 0, acceptance criteria, governance, security boundaries,
architecture, both ADRs, roadmap, threat model, provenance/adoption/dependency
records, contribution instructions and all workflows. Reviewed original Android
build/inspection instructions, build configuration, manifest/rules, validator,
desktop inspector and regression paths, plus the
[readiness audit](gate-0-native-launch-readiness-audit.md),
[process-history reconciliation](gate-0-process-history-reconciliation.md),
[native-host incident](gate-0-native-host-antivirus.md) and
[desktop evidence](gate-0-desktop-readiness.md). Relevant history includes the
original harness, native-launch validator and shared desktop-inspection commits.

## Actual resolution, decoding and acceptance

The existing reviewed SDK command tools **22.0** expose `resources xml --file`
in their installed help. Build-tools **36.0.0**, aapt2 **2.20-13193326**, expose
`dump resources`, `compile --dir` and `link --manifest -I` in installed help.
No new parser, downloaded binary, Python package or app dependency was adopted.
Original PDVA standard-library code remains repository-owner maintained. Existing
[tool licenses and provenance limitations](gate-0-isolated-worker-adoption.md)
and the 185-component/322-artifact build ledger remain unchanged.

Direct output from the retained release APK was:

```text
manifest: android:dataExtractionRules="@ref/0x7f020000"
Binary APK
Package name=org.pdva.gate0 id=7f
  type xml id=02 entryCount=1
    resource 0x7f020000 xml/data_extraction_rules
      () (file) res/4j.xml type=XML
```

The initially attempted source-like ZIP path `res/xml/data_extraction_rules.xml`
was absent. APK analyzer's `resources value --type xml --config default --name
data_extraction_rules` and aapt2 independently showed `res/4j.xml`; decoding that
actual entry succeeded. A direct Java invocation initially lacked the SDK toolsdir
property; using the existing reviewed launcher-equivalent invocation resolved it.
Neither initial error is a successful decode.

The validator now:

1. Retains existing native/ELF, inventory, duplicate-entry, permission, SDK,
   component, variant and packaging checks. Inventory bounds entries before SDK
   parsing, and an APK SHA-256 before/after check binds the inspection interval.
2. Requires the source/merged manifest's intended named reference and the actual
   packaged manifest's application-resource ID reference.
3. Uses the same SDK's fixed `build-tools/36.0.0/aapt2` to resolve that ID to
   `xml/data_extraction_rules`, exactly one XML resource and exactly one default
   file value. Extra packages, resource IDs, aliases, configurations, XML resources
   or unfamiliar dump shapes fail closed. This is deliberately narrower than
   general Android resource resolution; a future legitimate expansion needs review.
4. Reads that unique ZIP entry, limits it to 64 KiB, checks the binary XML outer
   type/header/total length, and invokes APK analyzer on that entry in the same APK.
   Missing tools, nonzero exits, timeout, absent entries and invalid XML cannot pass.
5. Validates both current source and decoded XML structurally: one
   `data-extraction-rules` root; exactly one `cloud-backup` and one `device-transfer`;
   nine distinct `exclude` leaves in each, each with only `domain` and `path="."`.
   Domains are `root`, `file`, `database`, `sharedpref`, `external`, `device_root`,
   `device_file`, `device_database`, `device_sharedpref`. Unexpected attributes,
   nesting, text, includes, duplicates, domains and paths fail. Normalized semantic
   policies must agree; whitespace, formatting and ordering are not the oracle.
6. Hashes the compiled payload, source policy and aapt2; checks source/tool identity
   stability across decoding. No filename equality or source hash alone substitutes
   for compiled-policy inspection.

## Tool and artifact identities

Local environment: Windows x86_64, bundled CPython **3.12.14**, existing Temurin
**17.0.20.1+1**, SDK command tools **22.0** and build-tools **36.0.0**. The system
Python Store alias was unavailable; commands below use the explicit bundled
interpreter. Existing AGP 9.4.0, Gradle 9.6.0, NDK r28c and CMake 3.22.1 pins
are unchanged. These local tools retain the existing reviewed research trust,
not independent rebuild or security-incident clearance.

| Observed bytes | SHA-256 |
|---|---|
| Retained release APK | `1445ddf0d06bbd0ca49ceac64c25fd386c55ed84401ff5a66f067d6c13477354` |
| Retained debug APK | `1236e0ca1cba0c6f915e5831da9ebb7d6d1f570a1f2aca9890aab6864e96f442` |
| Release compiled extraction XML | `6ec8b1ce5ec70df6f8fa78a0a814192d13d9a4a6de850be1b65d9239fd6d4b33` |
| Current source extraction XML | `b0e88f2e1ffb1c8de5783db430a938f0bb86987ded7aca3b5cf77590247ae09d` |
| Windows aapt2 executable | `babf3122e515ddb954c5ac4669e085ce990536c035e3072de30127bddd6e3608` |
| APK analyzer launcher | `7603a0a7ec99140c08918c35a1d8c3c85a795d40956d3897cce1dc6b45b87fa4` |
| APK analyzer classpath JAR | `a41766a6bf679feae9d8c65cfead8ba7573bd7762feedd808715a72a808328b2` |
| Java executable | `1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406` |

The APK hashes equal the previously recorded retained PR #27 artifacts. `git diff
7b73b2c896bbf9cbeeb43090cb9721203e43be0c HEAD -- android` was empty. This qualifies
them as existing reviewed-source research artifacts for offline inspection, not
fresh builds from this branch. The real desktop inspector also passed with the
three original stripped build-output native files, not just APK-extracted copies.
Exact source/build/signing trust for physical execution remains unresolved.

## Positive and negative controls actually executed

[The compiled suite](../../.github/scripts/test-packaged-rules.py) passed five
test methods, with **28 distinct negative APK cases**:

| Control | Actual outcome |
|---|---|
| Retained release and debug APK CLI inspection | Both passed new policy plus unchanged authority/native checks. |
| aapt2 recompiled intended policy transplanted into disposable APK copy | Passed shared validator; native results equal the retained artifact. |
| Missing cloud-backup or device-transfer | 2 compiled cases rejected by policy validation. |
| Remove root/sharedpref/device_root/device_sharedpref, separately in each section | 8 compiled cases rejected. |
| Altered path/domain, include, duplicate domain, section attribute, duplicate section, wrong root, nested rule | 8 compiled cases rejected. |
| Missing reference, nonexistent ID, different resource, alternate configuration | 4 cases rejected by reference/resource validation. |
| Missing payload, truncated binary, plain-text substitution, malformed chunks, stale compiled replacement, duplicate ZIP entry | 6 cases rejected. |
| Actual desktop journal path | Real valid APK reaches COMPLETED; compiled duplicate-section policy reaches FAILED, never COMPLETED. |

The nonexistent-ID fixture changes one uniquely located typed ID in the original
compiled manifest, preserving its size. aapt2 correctly refused to link a
nonexistent source symbol in the first fixture attempt; that construction error
was corrected and is not counted as validator rejection. Policy variants are
genuinely compiled/linked by aapt2 before inspection. Stale replacement swaps a
different compiled payload into the retained APK while preserving its manifest
and resource table. Mutation APKs are disposable, unsigned copies, never signed,
installed, executed or uploaded. No binary fixture is committed.

The first sandbox suite attempt hit analyzer access-denied errors on temporary
fixtures and was interrupted; the desktop suite also stalled in fixture setup.
Approved runs with fixture access completed. The first full compiled run exposed
the nonexistent-symbol construction error and a duplicate-ZIP diagnostic mismatch
(aapt2 rejected it before the Python duplicate check). Moving existing inventory
checks before SDK parsing made the latter deterministic. The corrected suite
passed in **76.190 seconds**. Expected malformed-chunk diagnostics are negative
evidence, not suppressed failures or a passing fixture.

Repository regression suite: **146 total, 142 passed, four existing platform
skips**. Desktop suite: **28 passed**, preserving interruption, process-exit,
contention, corruption, replay and identity tests, plus old/incomplete resource
receipt rejection. Synthetic transport fixtures remain explicitly synthetic;
they do not stand in for the separate real compiled tests. Additional mapping
controls reject unsupported formats/qualifiers, ambiguous IDs and unresolved
references; missing-tool, timeout and decoder failures propagate.

## Commands and receipt contract

Set `JAVA_HOME` to the existing JDK and `ANDROID_HOME` to the existing SDK.
`python` denotes the explicit interpreter above; `<analyzer>` is its installed
`cmdline-tools/22.0/bin/apkanalyzer.bat` on Windows or installed runner launcher.
Commands executed from the repository root:

```text
python .github/scripts/validate-foundation.py
python .github/scripts/test-repository-validation.py
python .github/scripts/test-desktop-readiness.py
python .github/scripts/validate-harness.py --apkanalyzer <analyzer> --apk android/gate0-harness/build/outputs/apk/release/gate0-harness-release.apk
python .github/scripts/validate-harness.py --apkanalyzer <analyzer> --apk android/gate0-harness/build/outputs/apk/debug/gate0-harness-debug.apk --variant debug
python .github/scripts/test-packaged-rules.py --apkanalyzer <analyzer> --apk android/gate0-harness/build/outputs/apk/release/gate0-harness-release.apk --android-jar <sdk>/platforms/android-37.0/android.jar
git diff --check
```

Foundation/whitespace checks passed. The actual direct `desktop-readiness.inspect`
call used baseline `HEAD`, release APK hash and the three original
`stripped_native_libs/release/stripReleaseDebugSymbols/out/lib` mappings; `receipt`
accepted its result. Full Gradle build/JVM/lint, native-host controls, image/frame
suites and physical/ADB/emulator/guest/native-launch execution were **not run**
in this change. Existing ignored APKs/build outputs were preserved. New resource
compilation alone is not a full Android rebuild; existing full-build limitations
remain as recorded in the desktop evidence.

The validation result gains required `extraction_rules` containing policy marker
`all-domains-excluded-v1`, resource ID, ZIP entry, compiled/source SHA-256 and aapt2
SHA-256. Existing source tree/APK/analyzer/validator/native identity fields remain.
Journal envelope version and transition/durability semantics stay unchanged.
The strict completion consumer rejects older or incomplete validation receipts;
reading a historical completed journal now fails closed rather than upgrading its
claim. Preserve those bytes as historical evidence. There is no automatic migration,
forged completion or modification of existing journals. A new inspection requires
the existing explicit prepare/dispatch procedure and cannot clear prior uncertainty.

Android CI now records build-tools/aapt2 identity and runs the mandatory compiled
controls after both APK inspections, before private receipt generation. No skip
fallback, weaker job, changed path filter, new dependency or artifact upload.
Foundation and Android workflows apply; QEMU does not. New-head hosted execution
is **unobserved at publication**, independently reviewed later.

## Limits and preservation

Ordinary-app execution authority, durable enrollment before transfer, independent
worker/descendant termination, complete current-worker inventory, revocation of
transferred FDs/mappings/copied data, incident clearance, physical artifact trust
and full Android 17 guest feasibility remain unresolved. No gate or readiness
disposition changes. OEM restoration behavior is not established by textual or
semantic policy matching. Unfamiliar SDK dump formats deliberately block acceptance.

Final review covers the complete intended diff, regular 100644 modes, local links,
whitespace, workflow applicability, unchanged source/dependency licenses and public
data. Only original source/tests and scoped evidence are published: no private paths,
keys, APKs, incident samples, Persona data or sensitive logs. Temporary fixtures are
not independently backed-up evidence; prior private recovery gaps are not cleared.

Exactly one intended PR is published and natively attached, followed by one
identity/association verification, then STOP without CI/review/status polling.
If publication or association fails, report **UNPRESERVED pending recovery of
the same PR or association**, never create a duplicate.
