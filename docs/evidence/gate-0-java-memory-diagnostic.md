# Separate Java memory diagnostic: source prepared, installation blocked

Date: **2026-11-07, America/Fortaleza**. Base main:
`3099ef684e20d84c2eb50f9dd9970646b8cb7b70`.
**Gate 0 Unresolved; Gates A–G Not reached. Original native harness locked.**
**No separately qualified installable APK exists; no phone operation performed.**

## Scope and authorization

The owner explicitly authorized this separate harmless diagnostic's source,
tests and unsigned development checks while retaining ADR-0004 Option A and the
original complete interactive virtual Android contract. This supersedes PR #57's
task-specific source-preparation stop for this narrow work only. It does not
resolve that record's artifact qualification stop, amend ADR-0003 Option A,
authorize a full guest, unlock the original harness or authorize installation.
Traceability: PDVA-REQ-002–003, 006, 008, 010–013, 036–042, 044–045, 048, 051, 054.

Implemented [module](../../android/memory-diagnostic/README.md) and
[test runner](../../.github/scripts/test-memory-diagnostic.py) reuse the exact
[PR #57 experiment](gate-0-java-memory-feasibility.md). There is no new feasibility
survey. Minimum/target SDK are 37; runtime requires API 37, ARM64 support, a 64-bit process and page size
4096 or 16384. A deliberate button press first commits a one-way boolean marker.
One fixed-name `MFD_CLOEXEC` memfd is truncated to one page. Two address-hint-zero,
offset-zero `MAP_SHARED` calls request RW and RX separately. Maximum backing is
16 KiB, total mapped extent 32 KiB. Nothing writes, reads or executes mapping
bytes. No RWX, JNI, payload, subprocess, worker, VM, networking or permission.

Each acquired resource has its own ownership flag; RX unmap, RW unmap and close
are independently attempted. No retry, fallback or close retry can reuse a freed
descriptor. The first failing operation/errno remains visible; the first cleanup
failure has a separate field. Any incomplete cleanup is Unknown. Unexpected
exceptions are Unknown without exception text. The fixed report has six fields:
Result, Operation, Errno, Cleanup, CleanupOperation, CleanupErrno. Numeric errno
is restricted to 1–4095; absence/unexpected exception is 0. No addresses, paths,
identifiers, logs, uploads or persisted results. Only the started flag persists.

Repeated activation, Activity recreation and reopening after a started run cannot
run again. Reopening shows Unknown rather than reconstructing a result. Synchronous
foreground calls have no hard latency bound; an ANR, crash, process death or lost
observation remains Unknown. JVM doubles test implementation transitions, not
real Android lifecycle, syscall cleanup, persistence guarantees or OEM behavior.

## Preflight, provenance and preservation

Live Git fetch and GitHub REST agreed on the base SHA above. Connector and CLI
returned zero open PRs: open heads/bases/full diffs/files/checks/jobs/logs/reviews/
comments/threads were an empty set. Merged #57–64 identities, changed files and
their retained research were reviewed, particularly the independent-build NO-GO,
installed Gradle integrity, startup admission and real STRICT experiment.
Requirements, all four ADRs, provenance/dependency records, signing configuration
and all three existing workflows were inspected. No architecture decision reopened.

Baseline main [foundation run 42398851026](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42398851026)
had successful Linux and Windows jobs; check/job metadata and logs were retrieved.
The latest applicable baseline [Android run 42308760908](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42308760908)
at `f73949464a0e75b7d17fc5092f15346f52ccc6bd` was successful and its logs retrieved.
That earlier source is not this diagnostic. GitHub Status reported All Systems
Operational, no incidents, page updated `2026-11-07T17:14:32.953Z`. Sandbox socket
denials were resolved by scoped command approval, not security-setting changes.

The clean primary checkout was branched from live main. Five existing worktrees,
branches, ignored assets and private evidence were preserved; no stashes existed.
No private evidence read, deletion, quarantine operation or independent backup
attestation. The unresolved Windows security incident remains unresolved.

New implementation/tests/docs are original task-authored Java/Python/Groovy/XML;
no third-party source or runtime library adopted. Maintainer: repository owner.
Existing pins remain Gradle 9.6.0, AGP 9.4.0, JDK 17, API 37/revision 2 and
build-tools 36.0.0. Existing license/dependency inventory remains applicable:
JDK GPLv2 with Classpath Exception, Gradle/AGP Apache-2.0, SDK terms and transitive
notices require their existing review; no new redistribution rights claimed.
The 185-component/322-artifact verification metadata and bootstrap are unchanged.
SDK JAR SHA-256 matches PR #57:
`bf1b4387cc7ca94fc6ef684f040d9d16fbf16248e181819f020736ea2053f177`.
Local JDK reports Temurin `17.0.20.1+1`; Python is `3.12.14`.

## Actual validation and limits

| Check actually executed | Observation and limit |
|---|---|
| Source controls | PASS; fixed syscall/mapping bounds, manifest authority, payload/dependency/signing exclusions, explicit initiation and extraction rules. RWX and INTERNET mutations rejected for their specific unsafe changes. |
| Desktop JVM engine/session | PASS, **190 assertions**: both admitted page sizes; API/ABI/bitness/page rejection; every acquisition/cleanup fault; unexpected exceptions at every operation; partial ownership, first failure, independent cleanup, errno/report bounds, durable marker failure and repeated/recreated admission. |
| Unsafe compiled mutant | PASS: removing descriptor close compiled successfully and was rejected at the expected behavioral sequence assertion. Compiler errors/timeouts cannot satisfy the control. |
| Actual Activity bytecode with desktop framework doubles | PASS: onCreate makes no experiment call; button triggers once after marker; duplicate listener invocation, recreation and reopening cannot reacquire. These doubles are not an Android lifecycle implementation. |
| SDK compile | PASS: all four production Java files compile cleanly against the hash-matched API 37 JAR with existing Temurin 17. Initial sandbox JAR access diagnostics were resolved by a scoped execution retry; only clean compiler completion is accepted. |
| Unsigned release assembly and Gradle JVM task | PASS through unchanged pinned bootstrap with STRICT verification; final release build configured only `:memory-diagnostic`, not the native harness. Final assembly succeeded offline. No signing task or key is used. |
| Release lint | PASS, **0 errors / 5 retained fixed-English-text warnings**; no lint baseline/suppression or mandatory check removed. Backup/transfer rules and icon warnings were fixed. |
| Compiled unsigned package | PASS: exact app/version/minimum/target identity, non-debuggable ordinary launcher, no permissions/extra components/native payloads/assets/prohibited DEX references/v1 signatures/APK signing block; compiled extraction exclusions present. AAPT2's shortened resource path is inspected without modifying bytes. This bounded parser is not an independent artifact/security verifier. |
| Existing repository checks | PASS: **148 repository tests + four existing Windows skips** (152 total), **28** readiness, **45** offline-image, **4** frame-copy, **38** Gradle bootstrap tests; harness source manifest validation. |
| Existing execution lock | PASS: **600 entry denials in three fresh JVMs**, all **three compiled unsafe lock mutants** rejected at the expected SDK Binder tripwire. Original harness source is unchanged. |
| Foundation / review | PASS: **176 files, 107 Markdown files, 54 requirements, four ADRs**; local links, modes, UTF-8/public-data hygiene and whitespace checked. |

Final unsigned development package (not an installation identity): SHA-256
`bb4658a4b4d09160a5699d0ce0b022501ca520f63a37d6aaa5bdaf5370a5bca4`.
This identifies the observed precommit development output only; a later build's
version-control metadata can differ. No signed equality/reproducibility follows.
Verification XML remains SHA-256
`4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`.

Retained failed development observations: default whole-project configuration
stopped at the unrelated harness's missing NDK; configuration-on-demand isolated
the Java module. One offline plugin resolution failed; resolving the existing
pinned closure through configured official repositories with STRICT enabled
allowed the build, followed by successful offline assembly. No checksum was added
or changed. An initial optional debug APK failed the conservative prohibited-DEX
reference check because generated compatibility DEX contained broad platform
references. Moving the minimum API to the actual API-37 scope did not remove all
those debug references. The final module deliberately disables debug generation
and tests only its non-debuggable release candidate; that failed debug observation
is not a pass and no existing harness debug check was changed. Existing ignored
unsigned intermediate outputs remain development-only and are not distributed.

Android runtime remains **NOT TESTED**. New-head hosted CI is **UNOBSERVED at publication**; existing Linux
native controls cannot be executed on this Windows host, and no Windows native
control was built/run. No signed artifact, signing key, APK binary, raw private
log or device identifier is committed or uploaded.

Existing workflows retain every mandatory check and their triggers. Foundation
adds the diagnostic source controls; Android adds separate unsigned assembly,
JVM, SDK compilation, lint and packaged manifest/DEX/native/signature inspection.
No workflow is manually dispatched, no APK artifact upload is added, and no
filtered/skipped/unobserved job is counted as a pass. Existing harness signing
configuration is unchanged; the diagnostic does not use it and disables its debug variant.

## Decisive installation blocker and minimum next action

**Decisive blocker: independent qualification of this exact signed diagnostic
artifact does not exist.** Source preparation and unsigned build evidence do
not discharge it. Minimum permissible next action is an independent reviewer/
custodian qualification packet for this source under unchanged policy, covering:

1. A qualified security disposition excluding an effect of the unresolved Windows
   incident on this chain, **or** an independently provisioned replacement chain
   with independent administrative/repository authority. A fresh Linux runner
   label alone is insufficient.
2. Authenticated acquisition and installed-input manifests for OS/runner, JDK,
   SDK/build tools, Gradle, AGP and complete metadata/transitive closure;
   configuration/cache provenance, CLI-free SDK acquisition, rights, maintenance
   ownership and independent security review. The later Gradle protections and
   PR #64's ten real STRICT controls resolve their bounded findings only.
3. Independently qualified private signing custody and verifier, approved signing
   behavior, backup, private transfer/recipient verification and exact source/
   workflow/tool/output/signer binding. No existing Windows/debug key reuse.
4. A genuinely new reviewed method addressing the strict signed-byte blocker,
   then authorized genuinely independent builds/signing with whole signed APK
   equality under ADR-0003 Option A. Retain dependency metadata, unchanged signing
   policy and all fifteen historical failures. No normalization or stripped bytes.
5. Independent review of this implementation and exact packaged artifact, complete
   applicable checks including Linux controls/current-head CI, the conditional
   physical-test packet, and explicit owner approval for one physical attempt.

The [independent-chain record](gate-0-independent-linux-build.md),
[real STRICT evidence](gate-0-gradle-strict-runtime.md) and
[ADR-0003](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md)
retain the detailed obligations. No new signing method/key or repeat signed-APK
experiment is authorized here. Preserve this working source while these gaps
remain open; do not substitute another broad investigation.

## One eventual Windows 10 / Samsung Android 17 procedure

**Do not perform these steps now.** This procedure becomes usable only after all
five qualification items above and explicit owner authorization for the exact APK.

1. Obtain the approved packet privately: source commit/tree, module
   `org.pdva.memorydiagnostic`, versionCode `1`, versionName `0.1-diagnostic`,
   release variant, target API 37, exact signed APK filename/byte length/SHA-256,
   signer certificate SHA-256, valid-signature receipt, independent signed-byte
   equality and security-review receipts. All identities must name the same final
   artifact. This PR supplies **no approved APK hash or signer**. Reject an unsigned
   development output or the different `org.pdva.gate0` harness.
2. On the qualified Windows 10 endpoint, compare the complete received file's
   hash with the approved packet using PowerShell `Get-FileHash -Algorithm SHA256
   -LiteralPath 'path-to-approved-apk'`. Have the independent verifier confirm
   signer/signature; a matching filename or hash alone is insufficient. Keep the
   packet and result outside public GitHub/chat surfaces.
3. Confirm the approved Samsung phone is stock/nonrooted Android 17. Transfer only
   that approved file over the reviewed private route (ordinary USB file transfer
   may be used if approved; no USB debugging or ADB). Open it in Samsung My Files
   and use the normal package installer. Allow installation from that specific
   source only if the reviewed packet permits the normal per-source setting.
   If Samsung policy, Auto Blocker, Play Protect or another protection blocks it,
   stop and ask the reviewer; do not disable protection or use privileged installs.
4. Open **PDVA Memory Diagnostic**, confirm **Ready**, then tap **Run one test**
   exactly once. **Admitted** means both mapping calls and cleanup returned;
   **Unsupported** means the API/ABI/bitness/page scope was not met; **Denied**
   records errno 1 or 13; **ResourceFailure** records errno 12; **Unknown** covers
   other/unexpected errors, interruption and incomplete cleanup. None proves
   full virtual-phone feasibility or identifies SELinux as the cause.
5. Privately transcribe only the six displayed fields and the approved artifact
   identity. Do not collect screenshots containing status-bar/account information,
   device IDs, paths or logs. If hung, interrupted, closed or missing a complete
   result, report Unknown and stop; do not clear data, reinstall or rerun to retry.
6. After preserving the small result with the reviewer, uninstall through normal
   Samsung Settings > Apps, delete the transferred APK when retention permits,
   and revoke any temporary per-source install permission. For incomplete cleanup,
   stop/close the app and follow the reviewer's cleanup instructions; do not assume
   this supplies proof that every kernel cleanup succeeded. No host VPN changes,
   root, ROM change, production ADB grant or phone configuration is performed now.

Publication: exactly one evidence PR, native chat attachment, one association
check, then STOP. No CI/review/comment/bot/mergeability polling after publication.
