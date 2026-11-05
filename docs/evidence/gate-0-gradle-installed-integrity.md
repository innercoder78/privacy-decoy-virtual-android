# Extracted Gradle distribution integrity before execution

Date: **2026-11-05, America/Fortaleza**. Base main:
`e0e9f4fbbeb9687ff28af0bf13cafae2dd878dda` (merged PR #58).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**

## Question, source and bounded result

The [independent build assessment](gate-0-independent-linux-build.md) identified
a concrete cached-directory weakness. At the exact base above,
[android/build.py lines 27–42](https://github.com/innercoder78/privacy-decoy-virtual-android/blob/e0e9f4fbbeb9687ff28af0bf13cafae2dd878dda/android/build.py#L27-L42)
hashes the distribution ZIP, then skips extraction when `home.is_dir()` is true
and invokes its launcher without comparing installed bytes. Bootstrap history
traces this behavior to `07242e8` (initial isolated-worker harness adoption).
This is source evidence of a gap, not evidence of a compromised installation.

The changed [bootstrap](../../android/build.py) independently compares installed
paths, types, sizes and SHA-256 content with a manifest derived from the pinned
ZIP before reaching `subprocess.call`. It validates fresh extraction and every
reuse. The bounded property is demonstrated with offline synthetic distributions;
it does not qualify an independent host, runner, complete toolchain or APK.
Traceability: PDVA-REQ-010, 036–042, 048, 051 and 054; no requirement is amended.

## Preflight and preservation

Live fetch confirmed the exact main above. GitHub open-PR search returned zero:
there were no open heads/bases/diffs/files/checks/jobs/logs/reviews/comments/threads
to reconcile. The merged PR #58 record and diff were inspected. GitHub's
[status endpoint](https://www.githubstatus.com/api/v2/status.json) reported
`none`, All Systems Operational, updated `2026-11-05T19:24:39.232Z`.
This is a preflight observation, not evidence of this PR's CI execution.

Reviewed governing requirements, governance, acceptance/provenance rules, three
ADRs, bootstrap/preflight and independent-build/Java diagnostic evidence, adoption
and dependency records, Gradle settings/properties/module configuration and all
three workflows. Existing Gradle 9.6.0 and SHA-256
`bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01`
remain unchanged, as do AGP, repository policy and dependency verification XML.
No binary, external package, tool adoption or license change is introduced.
New code and fixtures are original task-authored Python standard-library source;
fixtures contain invented non-executable bytes, not copied distribution code.
Maintenance remains with the repository's build-bootstrap maintainers.

The original checkout contained three pre-existing evidence edits on older main.
They remain untouched. A new branch/worktree based on live main isolates this
change. Existing branches, worktrees, stashes, ignored assets and private evidence
are preserved; no private inventory or backup qualification is claimed.
No Android CLI product, native research binary, phone, ADB, emulator, VM, guest,
signer or companion APK was invoked. No security settings were changed.

## Mechanism and failure behavior

1. Check path ancestors and file types using `lstat`; reject symlinks, Windows
   reparse points and non-regular or multiply linked files. Open with no-follow
   and nonblocking flags where available, compare descriptor identity and metadata
   before/after reading, then recheck the path. Windows path/descriptor differences
   in synthetic executable bits and ctime semantics are compared appropriately.
2. Read the ZIP into a bytes snapshot, verify its pinned SHA-256, then parse that
   same snapshot. This removes the hash-then-reopen archive substitution window.
3. Before extraction, reject unsafe/nonportable paths, NUL truncation, wrong root,
   traversal, drive/stream syntax, reserved names, duplicate/case-alias paths,
   file/directory conflicts, encrypted entries and non-regular archive types.
   Read every entry to check CRC/local headers and truncation. Require both launchers.
4. If the home is absent, create directories and files exclusively. Never merge
   into an existing home. Set the new Linux launcher executable; do not chmod or
   otherwise repair an existing installation. Validate the entire tree afterward.
5. Traverse every installed entry, rejecting extras (including empty directories),
   wrong types, missing entries, changed bytes or length. Only a complete match
   reaches the existing Windows/Linux invocation and argument forwarding.

Download and archive destinations also use exclusive creation. A failed download,
partial extraction, mismatch or competing creation remains on disk, with no
automatic delete, overwrite, reset or repair. Successful downloads retain their
`.download` evidence file. Reusing a complete valid installation requires no writes
to its files. Operators must investigate failures separately; this change supplies
no cleanup or repair operation.

## Executed controls and results

Environment: existing Windows x64, bundled CPython **3.12.14**; no new interpreter
installed. Run from the candidate worktree:

```text
python .github/scripts/test-gradle-distribution.py
python .github/scripts/validate-foundation.py
python .github/scripts/validate-harness.py
python .github/scripts/test-repository-validation.py
python .github/scripts/test-desktop-readiness.py
python .github/scripts/test-offline-image-inspect.py
python .github/scripts/test-frame-copy.py
git diff --check
```

The PATH Python alias was unavailable; commands used the existing bundled
interpreter. **20/20 Gradle controls passed, zero skips.** Cases cover fresh and
cached acceptance; both modified launchers and a same-size modified library;
truncation; missing/extra files and empty directories; file/directory substitution;
home replaced by a file; hard links; a real Windows junction (Linux uses a real
directory symlink); archive symlink metadata; ten unsafe path forms; duplicate,
case and parent conflicts; hash mismatch on fresh and cached paths; malformed ZIP;
corrupt member CRC; corruption during initial extraction retained and rejected on
reuse; mocked download acceptance and bad-hash preservation; existing partial
download preservation; and opened-file identity substitution. Launch is mocked in
every bootstrap test; all expected rejection paths assert no invocation.

**Original-weakness mutation:** first change the cached launcher while keeping the
verified ZIP intact and require content-mismatch rejection. Then replace only
`validate_installation` with a no-op. The same assertion must fail specifically
with `RuntimeError not raised`, and exactly one mocked launch must be observed.
This detects restored cached-directory trust. Compilation failures, unrelated
exceptions, generic exit codes and skips cannot satisfy the control.

Initial development runs exposed Windows stat differences and Windows ZipInfo's
normalization of backslash fixtures. These were failures, not successful negative
controls. The final fixture patches raw ZIP headers so the malformed path actually
exists on disk; final tests require the intended rejection reason.

Repository regressions: **148 passed, four pre-existing Windows skips (152 total)**.
Readiness: **28 passed**. Offline-image: **45 passed**. Frame-copy: **four passed**.
Readiness and image tests initially failed on sandbox fixture-directory access;
their unchanged suites passed on an approved execution retry. No assertion was
weakened. Harness source-manifest validation passed; foundation and link/mode/
whitespace/public-data checks are recorded at final review below.

A supplementary read-only check of the already present real ZIP verified the
unchanged pin and accepted its manifest: **six directories, 701 files**. No new
download, extraction or execution of real Gradle occurred. No genuine Android
build/JVM/lint, APK assembly/signing or native Linux test was run here; these are
unobserved, not passed. The existing execution lock is unchanged.

## Limits, workflow applicability and next proof

This is a point-in-time content/type check, not an execution sandbox. Ancestor
checks, exclusive creation and descriptor checks reduce accidental/concurrent
replacement, but do not make path traversal/extraction atomic against a malicious
same-user or privileged writer. Such a writer can race parent checks, change a
file after it was checked, or substitute a launcher/library between validation and
the interpreter/JVM opening it. Directory enumeration is not an atomic snapshot.
Use independently controlled, quiescent storage and exclusive administrative
custody; no claim of protection from a compromised host is made. Descriptor-race
fixtures demonstrate rejection logic, not exhaustive adversarial race freedom.

The full ZIP plus one decompressed member occupies memory; work is proportional
to archive and installed bytes on every invocation. This deliberately favors
checking over cache speed. The known pinned ZIP passes the conservative ASCII
name policy. ACLs, ownership, alternate data streams, xattrs, exact Unix permission
bits, Gradle user-home init scripts/caches, JDK/SDK and external dependencies are
outside this manifest's content claim. Symlink/junction-based installation paths
are intentionally rejected. Actual Linux behavior awaits CI execution evidence.

Foundation now runs the cheap offline suite on both existing Linux and Windows
jobs with normal failure propagation. Only the new test's exact path is added to
the foundation source allowlist. No existing assertion, workflow trigger, checkout
pin, permission, timeout or signing setting is changed. Existing Android workflow
path filters select these changes; QEMU research filters do not. Publication can
automatically schedule existing Android research checks; no manual dispatch or
companion build is requested. New PR checks remain **unobserved** at the mandated
publication stop; no polling or mergeability claim follows.

PR #56's unconditional lock, Java diagnostic **NO-GO**, ADR-0003 **Option A**, strict
whole-signed-APK equality and all **fifteen historical failures** remain unchanged.
The next prerequisite is an owner-appointed independent provisioning custodian
and reviewer supplying authenticated immutable acquisition and installed-file
manifests, administrative independence, CLI-free SDK acquisition/rights and private
signing custody. A genuinely new method must address the signed-byte blocker
before another artifact experiment. This correction supplies one control for that
packet; it does not qualify the packet or authorize a phone test.

Final review: six regular text files only, no binary/dependency/mode changes;
complete diff, provenance, local links, privacy and whitespace reviewed. Foundation
validation covers 158 files, 99 Markdown files, 54 requirements and three ADRs.
Publish one focused evidence PR, attach it natively to this chat and check
association once, then stop. Gate 0 remains **Unresolved**, Gates A–G **Not reached**,
physical testing **NOT READY — STOP**.
