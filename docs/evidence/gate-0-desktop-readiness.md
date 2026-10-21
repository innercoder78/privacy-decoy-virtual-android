# Gate 0 desktop artifact preparation and private journal

Date: **2026-10-21, America/Fortaleza**. Desktop-only preparation under
PDVA-REQ-036, 039–045, 048 and 054. **Gate 0 remains Unresolved; Gates A–G
remain Not reached. ADR-0001 Accepted; ADR-0002 Proposed.** No engine selected.
The complete interactive Android 17/API 37 objective, ordinary-app-only authority,
genuine isolation, host VPN contract and privacy obligations remain unchanged.
No physical device has been contacted. No future phone operation is authorized.

## What already exists and what this adds

The [existing Android harness](../../android/README.md) builds debug, nondebuggable
release and development instrumentation APKs. Release uses an ordinary local
development signing key, not a production signing identity. The manifest requests
zero permissions; research minSdk 30 and target/compile 37 are not host-support
claims. Gradle 9.6.0, AGP 9.4.0, build-tools 36.0.0, NDK r28c/28.2.13676358 and
CMake 3.22.1 remain unchanged. The existing adoption/license record and
[185-component/322-artifact build ledger](gate-0-isolated-worker-dependencies.md)
remain applicable. No dependency, license grant, source pin or native code is added.

Packaged native inventory remains exactly:

| Entry | Role |
|---|---|
| `lib/arm64-v8a/libsubstrate.so` | JNI shared library |
| `lib/x86_64/libsubstrate.so` | JNI shared library |
| `lib/arm64-v8a/libpdva_launch.so` | Source-built ARM64 dynamic PIE, not JNI |

The [launch control](gate-0-isolated-native-launch.md) already builds from the
reviewed C source; this work neither copies it nor executes it. Existing RUN,
LAUNCH, lifecycle uncertainty lockout, manifest and Android source are unchanged.
The [seccomp fixture](gate-0-android-seccomp-bootstrap.md) stays dormant, outside
the APK. Physical-worker recovery remains unresolved under the
[exceptional-lifecycle review](gate-0-android-lifecycle-exceptions.md).

The new [Python tool](../../.github/scripts/desktop-readiness.py) records an exact
declared revision, APK SHA-256, variant and local native-file correspondence.
It requires that revision to equal HEAD and tracked Android inputs to match it,
with no untracked nonignored Android input. It reuses the existing packaged
manifest/native/ELF validator; that validator now exposes its unchanged checks
through `inspect_apk`, returns native identities, and also rejects a release
manifest falsely declared debug. No saved manifest is accepted as APK evidence.
The installed APK analyzer runs locally with a 120-second limit. No network,
download, ADB, device control or native-payload execution is implemented.

The APK and analyzer/validator hashes are checked before and after inspection;
the native files must match the exact packaged bytes, including stripping.
Missing, extra, duplicate, wrong-ABI and unreviewed native entries are rejected by
the existing validator; local missing/extra/mismatched mappings are rejected too.
The revision-to-APK relationship is a **declared build association**, constrained
by source checks and matching local outputs, not independent reproducible-build
attestation. An old APK can have the same bytes. The tool does not verify the APK
signing certificate/signature or assert installability, device support, Android
execution, cleanup, containment or safety. Toolchain installations and the local
workspace are trusted inputs; this is not protection against a malicious local
administrator swapping files between observations.

## Short Windows procedure for later desktop use

Use an existing Python 3.11+ installation, Git, JDK 17 and the pinned SDK above.
No WSL, Docker or Linux compiler is needed. Keep journals on a private local disk,
outside synced/shared folders; Git ignore rules do not provide confidentiality.
Set `JAVA_HOME` and `ANDROID_HOME` to the existing local installations. First run
the ordinary build commands in the Android instructions if artifacts are absent.
Do not connect a phone. From the repository root in PowerShell:

1. Set the identities and choose a **new** journal name for this offline build.
   Keep these variables for the following commands. Compare the hash with your
   independently retained build receipt when one exists; computing it here only
   identifies the current file.

   ```powershell
   $tool = '.github/scripts/desktop-readiness.py'
   $apk = 'android/gate0-harness/build/outputs/apk/release/gate0-harness-release.apk'
   $revision = git rev-parse HEAD
   $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $apk).Hash.ToLowerInvariant()
   $identity = @('--journal', 'desktop-release-01', '--source', $revision, '--apk-sha256', $hash, '--variant', 'release')
   $native = 'android/gate0-harness/build/intermediates/stripped_native_libs/release/stripReleaseDebugSymbols/out/lib'
   ```

2. Create the private record and persist the intended offline action. Stop if
   either command fails; do not overwrite an existing journal.

   ```powershell
   python $tool init @identity
   if ($LASTEXITCODE -ne 0) { throw 'Stop and preserve the journal' }
   python $tool prepare @identity --operation release-inspection
   if ($LASTEXITCODE -ne 0) { throw 'Stop and inspect the journal' }
   ```

3. Inspect the existing package and its three corresponding build outputs.

   ```powershell
   python $tool inspect @identity --operation release-inspection --apk $apk --apkanalyzer "$env:ANDROID_HOME/cmdline-tools/22.0/bin/apkanalyzer.bat" --native "lib/arm64-v8a/libsubstrate.so=$native/arm64-v8a/libsubstrate.so" --native "lib/x86_64/libsubstrate.so=$native/x86_64/libsubstrate.so" --native "lib/arm64-v8a/libpdva_launch.so=$native/arm64-v8a/libpdva_launch.so"
   if ($LASTEXITCODE -ne 0) { throw 'Stop; do not retry automatically' }
   python $tool status --journal desktop-release-01
   ```

After an interruption, use only `python $tool resume-plan --journal
desktop-release-01` first (one line). This is read-only. If it says PREPARED,
the fixed offline inspection has no dispatch record and may be explicitly run
with the same identity. If UNKNOWN, malformed, missing or locked, preserve it
and stop. Do not delete, edit, truncate, reinitialize or create another journal
to bypass uncertainty. FAILED is a recorded offline validation rejection; after
review, a separately named operation may be explicitly prepared for the same
build. A completed operation cannot be dispatched again.

`record-cleanup-unknown` with the same identity and a new operation ID can only
record an externally reported uncertainty; it cannot perform or authorize an
action. It blocks further dispatch in that journal. There is deliberately no
phone prepare/dispatch/completion, cleanup-clear, automatic retry, reset, deletion
or reboot-recovery command. A future phone procedure needs separate approval,
integration review and independent observation; this desktop journal is not its
authorization or its enforcing lockout.

## State and durability contract

| State | Meaning and recovery |
|---|---|
| NOT_STARTED | Valid initialization, no operation yet. A missing file is an error, not this state. |
| PREPARED | Build, operation ID, fixed intended action and explicit offline/no-phone/no-cleanup-authority preconditions persisted; no dispatch. |
| IN_PROGRESS | Append and `flush`/`os.fsync` succeeded before inspector dispatch. Held OS lock excludes cooperating writers. |
| COMPLETED | This process persisted an offline validator receipt after inspection; never phone completion. |
| FAILED | This process persisted an offline rejection; never inferred cleanup. |
| UNKNOWN | Read-only status interprets any unfinished IN_PROGRESS this way, even if its writer may still be live. No elapsed-time/PID inference. |
| CLEANUP_UNKNOWN | External uncertainty is recorded; no supported transition can clear it. |

One append-only JSONL file per journal lives in the already ignored
`android/build/private-readiness/`. Exclusive creation refuses existing files,
including empty remnants. Each write holds a nonblocking OS lock on the same
file: Windows `msvcrt.locking` byte zero, POSIX `flock`. A second writer fails;
the OS releases a dead writer's lock, but its unfinished operation stays UNKNOWN.
No stale-lock deletion is needed. Records use canonical JSON, strict schemas,
sequence numbers, previous-record SHA-256 and record SHA-256. A reader validates
the entire chain, journal name, build identity and legal transitions. Duplicate
IDs/results, stale appended records, malformed/truncated records, completion
without dispatch and invented phone/cleanup-success transitions fail closed.

Writes flush and fsync before any subsequent action. Torn result persistence is
never repaired or silently dropped. An interruption before the dispatch record
is written leaves PREPARED; after any ambiguous dispatch persistence it leaves
UNKNOWN or an invalid journal, even if the inspector never ran. Read-only status
may fail or conservatively report UNKNOWN during an active writer; dispatch
always reacquires the lock and revalidates the current complete record.

**Limits:** fsync is the strongest portable file flush used here, not a guarantee
against disk/controller failure. Windows directory-entry durability is not
promised. Use local storage with ordinary locking semantics, not network shares.
Whole-file loss, restoration of an older valid prefix, deliberate hash-chain
reconstruction by a local writer, journal copying/renaming plus forgery, or a
new journal bypass cannot be reliably detected without external trusted storage.
No secure anti-rollback, authenticity, encryption, kernel-boot attestation or
independent Android teardown evidence is provided. The negative controls reject
invalid receipts and replay through this protocol, not an attacker able to
rewrite all local records consistently. A reboot checkbox, worker report,
elapsed time, user confirmation or local COMPLETED record never clears an
Android uncertainty lockout. Physical-worker recovery remains **Unknown**.

## Evidence schema and public boundary

Private record envelope: `version` (1), zero-based `sequence`, `previous`,
`kind`, `operation`, `data`, `hash`. INIT data contains `journal` and `build`;
build is exact 40-hex `source`, 64-hex `apk_sha256`, declared `variant`.
PREPARED data records `intended_operation=inspect-apk` and fixed preconditions.
IN_PROGRESS data is empty. COMPLETED data contains the same build,
`source_tree`, `validator_sha256`, `analyzer_sha256`,
`scope=offline-inspection-only`, validation (`manifest=passed` and native entry
hash/role/NEEDED inventory) and matching local artifact paths/hashes. FAILED
records only `observation=offline-validation-rejected`; terminal error output is
private diagnostic context. CLEANUP_UNKNOWN records only external uncertainty
and `phone_authorized=false`. There is no result-import API.

Journals contain local paths and must stay private. Do not paste status output,
raw logs, APKs, keys, device identifiers or journal files into GitHub. A manually
reviewed public evidence summary should contain: date/timezone, exact source
and tree, build commands and tool versions, declared variant/APK/native hashes,
validator identity and scoped results, negative-control results, limitations,
remaining Unknowns and next safe action. Omit private paths and signing assets.
CI leaves the journal in its local ignored build directory and does not upload
or dump it. No automatic sanitized export claims to solve public-data review.

## Preflight and validation evidence

Live main was `b91864cb0967c16335800daff2c66c8e96d0baae`, tree
`d0e776adada2c8841d6f128c1127de145c804543`. Connector and REST open-PR inventories
were empty: no open heads/bases/diffs/checks/reviews/threads to reconcile.
Merged PR #27 head `7b73b2c896bbf9cbeeb43090cb9721203e43be0c`, base
`19a7a56838e118c7756119cbd8e42077b3907727`, supplied the dormant fixture; main
adds its merge and Tony's README edit. No overlapping implementation exists.
PR #27 reviews, conversation/inline comments and review threads were empty.
Main foundation [job 118944174703](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39514771319/job/118944174703)
passed with actual steps. PR #27 Android
[job 118847383750](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/39484622343/job/118847383750)
built all variants, passed 68 protocol checks, lint, dormant-fixture byte checks
and both APK inventories. These are existing hosted build/model results, not
Android execution. Main's README-only push did not select the Android workflow.
Legacy commit status had zero contexts; its aggregate pending was not a failed job.
GitHub Status reported All Systems Operational, page update
`2026-10-21T03:19:34.307Z`.

Initial checkout was clean, one worktree, no stashes, 112 regular `100644` files.
Existing branches and ignored artifacts were preserved; the new branch starts
at verified main. Requirements, both ADRs, governance, roadmap, security/evidence
records, build/adoption/license/pin inventory, CI, manifest, validators and
launch/lifecycle source were inspected. Historical Privacy-Decoy stays read only.
Only original PDVA Python/tests and documentation are added; the repository owner
maintains them. Standard-library Python introduces no third-party package.
The root README, all Android source/permissions and native sources are unchanged.

Local Windows validation used existing bundled CPython **3.12.14**, Temurin
**17.0.20.1+1**, and SDK command tools **22.0**. `python` below denotes that
explicit interpreter, since the system Store alias was unavailable. Commands:

```text
python .github/scripts/validate-foundation.py
python .github/scripts/test-repository-validation.py
python .github/scripts/validate-harness.py
python .github/scripts/test-desktop-readiness.py
git diff --check
```

The existing regression suite passed **141 tests, four existing platform skips**
(137 executed). The new suite passed **27 tests, no skips**, including real
controlled host-Python process exit and OS writer contention, pre-dispatch
flush interruption, post-dispatch interruption, partial result persistence,
corruption/truncation/duplicate keys, stale/replayed records, duplicate IDs,
identity mismatch, forged/phone completion and unsafe retry/cleanup-clear
rejection. Reused synthetic ELF fixtures exercise the actual existing validators
with a mocked analyzer text transport; real APK inspection below is separate.
CLI negative controls also require exit 2 for manual completion, cleanup-clear,
retry and phone-dispatch commands; none exists. Final foundation validation
passed 115 files, 66 Markdown files, 54 requirements and two ADRs.
New tests require rejection, not any nominally successful command. They include
a positive PREPARED offline continuation, positive byte correspondence, native
missing/extra/mismatch controls, permission/variant rejection and input mutation.
These are desktop protocol/model results, not Linux/Android enforcement.

The exact attempted Gradle command was:

```text
python android/build.py --offline :gate0-harness:assembleDebug :gate0-harness:assembleRelease :gate0-harness:assembleDebugAndroidTest :gate0-harness:protocolTest :gate0-harness:lintDebug
```

Sandbox attempt failed before build with native-platform.dll initialization.
The identical authorized outside-sandbox retry reached Gradle but failed offline
resolution of `com.android.application:com.android.application.gradle.plugin:9.4.0`.
No dependency pin was changed, no online download/rebuild was substituted, and
**no fresh Gradle build or lint pass is claimed**. Direct JDK compilation of
Protocol.java, Report.java, LaunchResult.java and ProtocolTest.java to ignored
`android/build/desktop-readiness/protocol`, followed by
`java -cp android/build/desktop-readiness/protocol org.pdva.gate0.ProtocolTest`,
passed **68 protocol/report checks**. Android instrumentation was not run.

Both retained APKs passed `validate-harness.py --apkanalyzer <installed-22.0-tool>
--apk <existing-variant-apk>` (debug additionally `--variant debug`). The initial
assumption that the local `latest/bin` tool existed failed; the actual installed
22.0 path succeeded. These artifacts retain PR #27's previously recorded local
hashes; inspection does not turn them into fresh builds:

| Retained artifact | SHA-256 |
|---|---|
| Release APK | `1445ddf0d06bbd0ca49ceac64c25fd386c55ed84401ff5a66f067d6c13477354` |
| Debug APK | `1236e0ca1cba0c6f915e5831da9ebb7d6d1f570a1f2aca9890aab6864e96f442` |
| Release ARM64 JNI | `71bb7cbb85665f30c6dd92e9b3039ce34d9a04cdb1c0a2a8ebeba10dd4676b35` |
| Release x86_64 JNI | `8e78104351acc567691562e644af0e3b80ef5b75277db4d742b1fec73c365bea` |
| Release ARM64 launch executable | `6c95e1aa9342422e7c70ce8bc63c318408e628bd7eea5507aca3d4081033e789` |

The new CLI's `init`, `prepare`, `inspect` and read-only `resume-plan` commands
all exited zero for the retained release APK, declared baseline revision and
three matching stripped build outputs. Its private record is COMPLETED for
offline inspection only. No APK, local paths, signing assets or journal are
published. Existing Maven metadata SHA-256 remains
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.

Foundation CI adds the standard-library suite; Android CI adds the same private
release correspondence procedure after all previous builds/inspection checks.
Existing pins, permissions, exact-head checkout, path filters, negative controls
and workflows remain. New hosted CI is **pending/unobserved at publication**;
no post-publication polling is authorized. Next safe action: review this source
change and its hosted results separately. No phone test or cleanup recovery is
authorized by these desktop results.
