# Installed Java diagnostic JDK and SDK byte integrity

Date: **2026-11-08, America/Fortaleza**. Reviewed main:
`3be5edb5d4e00949c10a7175c7a407105253b966` (merged PR #68).
**Gate 0 Unresolved; Gates A–G Not reached; physical testing NOT READY — STOP.**
Scope: one read-only prerequisite for the existing Java memory diagnostic,
under PDVA-REQ-036–042, 048, 051 and 054. No requirement is marked satisfied.

## Question and bounded result

Can the existing Temurin JDK 17, Android SDK Platform 37 and Build Tools 36.0.0
installed regular-file bytes be inventoried privately and subsequently compared,
without confusing local consistency with independent toolchain authentication?

[The verifier](../../android/installed_tools.py) inventories the three explicitly
selected package roots and compares their complete regular-file contents and
directory membership with a previously saved manifest. Metadata and required
tool paths are checked as well as hashed. The result is a point-in-time byte
comparison, never execution permission or upstream authentication.

**Trust disposition: UNTRUSTED.** Generating an inventory and comparing it with
the same installation cannot make it APPROVED. The schema admits only UNTRUSTED;
changing that field to APPROVED fails. There is no approve command, caller-supplied
trust flag, automatic baseline update or locally generated approval receipt.
Exit zero means only that the requested inventory/comparison operation completed.
The comparison message explicitly says independent approval is not established.
Consumers must not interpret it as build admission.

An **APPROVED baseline requires a separate independent authentication and review
process** binding authenticated upstream acquisition, exact package bytes, source
and tool identities, validity/revocation policy, administrative custody and security
disposition. No such authority or authenticated baseline exists in this task.
This implementation deliberately does not invent an approval service, accept an
unauthenticated sidecar as approval, or claim to test that missing process.
Independent baseline authentication remains **Unknown / STOP**. A later approved
integration needs separate review; this standalone utility does not alter Gradle
startup or the diagnostic's build/test invocation.

## Live preflight and sources

GitHub's live main matched the SHA above; PR #68 was merged. Connector search and
the CLI both returned **zero open PRs**. Consequently there were no open heads,
bases, complete diffs/file modes, commits, checks/jobs/logs, reviews, comments or
review threads to reconcile. Existing branches, five registered worktrees,
ignored/private assets and the initially clean checkout were preserved; no stash
existed. No nonempty applicable AGENTS.md was found.

[Base foundation run 42448785390](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/42448785390)
completed successfully. Check records, both job/step records and the combined
logs were inspected: `foundation` job `128633323675` and `offline-image-windows`
job `128633323588` succeeded on the exact main SHA. Android/QEMU had no run for
this documentation-only merge, not a passing result. The commit-workflow connector
returned no runs (its PR-event filter does not establish push-run absence); the
CLI supplied the actual push-run records. Initial sandbox GitHub socket access
failed; the read-only CLI query succeeded on the approved retry.
[GitHub Status](https://www.githubstatus.com/api/v2/status.json) reported
`none`, All Systems Operational, page update `2026-11-08T04:24:33.822Z`.

Reviewed the requirements, four ADRs and their precise dispositions, governance,
acceptance/provenance rules, execution lock, Windows incident, independent-build
packet, Java diagnostic and dependency-metadata evidence, build-tool adoption,
185-component/322-artifact dependency inventory, and all three workflows.
Relevant implementation/history:

- [PR #59](https://github.com/innercoder78/privacy-decoy-virtual-android/pull/59),
  head `9070c47334621909319805eef5d0744079fb3ecd`, and the current
  [Gradle bootstrap](../../android/build.py): pinned-archive installed-tree
  verification covers Gradle, explicitly excluding JDK/SDK. The new utility reuses
  its existing `checked_stat`, `check_parents` and `read_regular` functions.
- [Diagnostic tests](../../.github/scripts/test-memory-diagnostic.py), introduced
  by `6d16de0`, cover source/JVM/package behavior, not a complete installed-tool
  inventory. No existing applicable JDK/SDK comparator was found.
- [Diagnostic record](gate-0-java-memory-diagnostic.md) and
  [PR #68 evidence](gate-0-diagnostic-dependency-metadata.md) identify the existing
  installed tools used here. Metadata claims are observations, not newly
  authenticated upstream identities. No upstream source or binary was downloaded.

New verifier/tests are original Python standard-library source; filesystem helper
reuse is from this repository. No external dependency, tool adoption, bundled
binary, license change or redistribution is introduced. Existing Temurin
GPLv2/Classpath Exception, SDK terms and component notices retain their limits.
Maintenance remains with the repository build-tool maintainers. Complete
Gradle/AGP/transitive closure is outside these three package roots.

## Mechanism and use

Select absolute roots for the JDK, the `platforms;android-37.0` package and
`build-tools;36.0.0` package. A private manifest must be outside those roots.
Using the existing interpreter, without invoking any JDK or SDK executable:

```text
python android/installed_tools.py inventory --jdk <absolute-jdk> --platform <absolute-platform> --build-tools <absolute-build-tools> --manifest <new-private-manifest>
python android/installed_tools.py compare --jdk <absolute-jdk> --platform <absolute-platform> --build-tools <absolute-build-tools> --manifest <private-manifest>
```

The inventory is created exclusively; an existing destination is not overwritten.
It contains relative package paths, file sizes/SHA-256 values, directory entries,
host family and observation time, with a fixed UNTRUSTED label. No absolute input
root is serialized. **Relative filenames and hashes are still private evidence**;
do not attach the manifest or raw receipt to GitHub. Errors from filesystem/data
validation produce a fixed sanitized failure message and exit one.

Traversal refuses symlinks, Windows reparse points, hard-linked/nonregular files,
unsafe relative names and case aliases, using the existing checked-read helper.
The helper checks ancestors, opened descriptor identity and post-read metadata.
Directories are checked before/after enumeration. All entries, including empty
directories, must match; no mutable-file exclusions are provided.

Required nonempty identities include JDK `release`, java/javac/jar and modules;
SDK platform `android.jar`, `source.properties` and `package.xml`; Build Tools
aapt2, aidl, zipalign, d8 launcher/JAR and package metadata. All other files in
these roots are also hashed. JDK metadata must claim Eclipse Adoptium Temurin 17,
JDK image, the selected Windows/Linux family and x86_64. Platform properties must
claim API 37.0, revision 2, extension 22 and preview 0; Build Tools must claim
36.0.0. Both XML package IDs and revisions must agree. Exact remaining metadata
and executable/library bytes are bound by the full comparison. This is identity
consistency, not verification of executable semantics or vendor signatures.

Strict JSON rejects duplicate keys, unsupported schemas/trust claims, malformed
entries, missing parents and ambiguous paths. A local observation older than
30 days or dated in the future is refused. This conservative freshness limit is
not an independently approved expiry policy. A dishonest clock or rewritten
UNTRUSTED timestamp is not authenticated; neither can confer approval.

## Actual local experiment and controls

Environment: **Windows 10 x86_64, build 19045**, existing bundled **CPython
3.12.14**, installed **Temurin 17.0.21+9**, Android Studio SDK **Platform 37.0,
revision 2, extension 22, preview 0**, **Build Tools 36.0.0**. Installed metadata
was read directly; executables were never invoked. Initial conventional user-SDK
location lookup was absent; the retained PR #68 setup identified the actual
installation. No installation, PATH or persistent environment change occurred.

The new ignored private work directory holds the initial manifest, complete
disposable copies and detailed receipt. Original installations were read only.
Full copies first had to match the original manifest before mutation. Destructive
changes were limited to those new copies. Each negative control required its
specific rejection, not any arbitrary exception or nonzero exit.

| Genuine local control | Observation |
|---|---|
| Original installation compared with saved inventory | MATCH, explicitly UNTRUSTED; no independent provenance inference |
| Complete disposable copies compared with original inventory | MATCH, still UNTRUSTED |
| Change one byte of copied platform JAR without changing length | Installed inventory mismatch |
| Remove required copied platform JAR from its expected path | Required tool identity absent |
| Add unexpected copied-package file | Installed inventory mismatch |
| Change copied API metadata from 37.0 to 38.0 | Unexpected platform identity |
| Supply duplicate-key JSON | Duplicate JSON key |
| Supply baseline dated 31 days earlier | Stale or future baseline |
| Change local trust label to APPROVED | Unsupported manifest or trust claim |
| Add real Windows junction to copied package | Unsafe filesystem type; target remains empty |
| Restore disposable mutations and recompare | MATCH, still UNTRUSTED |
| Recompare original installed tools after controls | MATCH; original package bytes unchanged |

[Synthetic suite](../../.github/scripts/test-installed-tools.py): **16 tests
passed, zero skips**. Additional controls cover future dates, unexpected empty
directories, XML identity, malformed JSON/schema/path forms, hard links, host
mismatch, exclusive manifest output and sanitized CLI errors. Fixtures use
invented non-executable bytes; these are detector tests, not real tool results.
Three semantic controls replace live scanning with cached inventory, bypass trust
validation, or extend freshness to 365 days: the corresponding rejection assertion
must fail specifically with `ValueError not raised`. Unrelated errors cannot pass.

The first sandboxed synthetic run had **one infrastructure ERROR**: junction
creation timed out. That run was not a pass. The unchanged rejection assertion
passed with an actual junction outside that sandbox restriction; no elevated OS
privilege or security-setting change was used. CLI controls were then added and
the full 16-test suite passed. Real-package junction setup used the same ordinary
user capability on disposable data.

Applicable local regressions: repository suite **148 passed / four existing
Windows skips (152 total)**; Gradle-distribution **38**, readiness **28**,
offline-image **45** and frame-copy **four** tests passed; harness manifest validation and diagnostic source policy
with RWX/INTERNET mutations passed. These execute Python/fixtures only. No native
harness, Java process, Gradle build or Android command was run for this task.

## Limits, retention and next independent proof

This is not an atomic filesystem snapshot or a defense against a compromised
host, same-user concurrent writer or privileged administrator. Parent/path checks
and hashes can be raced; files can change after comparison and before later use.
One complete file is held in memory while hashing. ACLs, owner identity, alternate
streams, xattrs, exact executable permissions, runtime loader/search-path behavior,
external SDK/JDK components and caches are not covered. Linux is supported only
for the conservative regular-file layout; real Linux installed-package validation
and the new hosted jobs are **NOT RUN / UNOBSERVED**, not passes.

Authenticated upstream acquisition, independent administration, security
disposition for the existing Windows incident, complete Gradle/AGP/transitive
closure, signing custody and strict whole-signed-APK reproducibility remain
**unproved**. Independent approved-baseline authentication and its genuine positive
control are **NOT RUN**. No signing, key handling, APK installation, device/USB/ADB,
Android CLI, reinstall, download-to-complete-test, native/guest/VM harness execution,
metadata opt-out, random-number control, ciphertext reuse or APK normalization
occurred. ADR-0003 Option A, ADR-0004 Option A, all fifteen historical equality
failures, the research lock and every existing required check remain intact.

Falsifiers: a changed/missing/extra file, invalid metadata, malformed/stale baseline
or redirected path accepted by the comparator invalidates the respective control.
Any local match promoted to independent approval invalidates the trust boundary.
Changing tools, package revisions, helper implementation or trust policy requires
fresh review and controls. A passing manifest cannot clear the Windows incident.

**Independent backup UNVERIFIED; private evidence UNPRESERVED.** Detailed local
receipts remain in the existing private work area; ignored storage is not backup.
No backup destination was invented. Any operation requiring independently backed-up
private evidence stays stopped. Public changes contain no complete private
inventory, private path/hash, user identifier, sensitive receipt or tool binary.

Next proof: an owner-appointed independent custodian/reviewer must authenticate
acquisition and the complete selected baseline under qualified private retention,
establish independent administration and security disposition, and separately
qualify the wider build/signing/reproducibility packet. This utility contributes
only the tested comparison control to that packet.

The six-file change includes verifier, tests, two exact foundation allowlist
entries, execution of the new cheap suite in both existing foundation jobs, this
evidence and its index entry. Existing checks, triggers, permissions, checkout pin
and failure propagation remain. Android path filters select these source/workflow
changes; QEMU filters do not. New-head CI is **UNOBSERVED at publication**.
Final foundation validation passed: **180 files, 109 Markdown files, 54
requirements, four ADRs**. Full diff, regular 100644 text modes, unchanged
dependencies/public source identities, local links, whitespace and privacy were
reviewed. No private inventory or receipt is included in the six-file change.
Publish exactly one focused evidence PR, attach it natively to this chat, verify
association once, then STOP without polling CI/reviews/comments/bots/mergeability.
