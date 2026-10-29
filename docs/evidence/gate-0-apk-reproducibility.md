# Gate 0: independent research APK reproducibility

Date: **2026-10-29, America/Fortaleza**. Scope: PDVA-REQ-036–043, 048,
050–051 and 054. **Gate 0 Unresolved; Gates A–G Not reached. Physical
native-launch readiness NOT READY — STOP.** ADR-0001 Accepted; ADR-0002 Proposed.

## Question and experiment boundary

Do two fresh builds of the same reviewed Android research source, under the same
identified tools and development signing identity, produce identical signed APK
bytes? This record concerns only that bounded artifact-provenance prerequisite.
All five observed hosted pairs **failed signed-byte equality**: both JNI shared
libraries differ despite equal declared inputs and the same verified signer.
Local fixture success is not an independent APK build result. The latest
continuation below introduces a narrowly scoped debug-path mapping candidate,
pinned by immutable commit/tree. Its new hosted results are **unobserved**;
causation and successful correction remain unproved. Historical sections below
retain the prior procedures and negative results.

The procedure is original PDVA standard-library code in
[apk-reproducibility.py](../../.github/scripts/apk-reproducibility.py), with
[disposable unsigned controls](../../.github/scripts/test-apk-reproducibility.py).
The candidate changes JNI CMake debug-path options only; no C/Java application
source, manifest, extraction policy, Persona, dependency version, verification
metadata, permanent key or production signing policy changes.

## Live preflight

Canonical main, independently verified through the GitHub commit API, is
`61c68f87404a1b7e70e0314b73532322ee2de252`, tree
`452cc52b115f7d0c5d8cb63be1f092f189d4b26d`. PR #49 is merged at that SHA,
from head `9738775b9036953667d7537a2a9ac295219d7f1c` against base
`6d0d5b7f0df93c0cf08289987cdf46155da64a05`. The connector open-PR search and
REST open-PR inventory both returned zero: open heads/bases, complete diffs,
files/modes, checks/jobs/logs, reviews/comments/threads and dependencies are an
empty set. No existing relevant PR required reuse.

Exact-main [Android run 40903682967](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40903682967),
job `123552516460`, succeeded. Its actual checkout, execution and inspection logs
were read, not just its green conclusion. It built debug, release and development
instrumentation, exercised protocol/lint, cross-built and statically inspected
the dormant bootstrap, inspected both APKs, passed five compiled-policy test
methods and completed the private offline receipt step. The single baseline
release SHA-256 was `a5d504f583e2c04d3e9dbff42a8ec0e6a10c18e8305044a3fed039da30303f4b`.
This historical single APK is not one of the new pair.

Exact-main [foundation run 40903683277](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40903683277)
also succeeded. Jobs `123552518985` and `123552519167` and their execution logs
were inspected. Linux records 149 repository tests, 28 desktop receipt tests,
45 image tests, four frame tests, seven native wait controls plus assertion
failure, modeled bootstrap and existing Linux lifetime/seccomp/revocation
controls. Windows records 45 image and four frame tests. These are historical
exact-main receipts, not fresh local native execution. QEMU is path-filtered out.
[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported all
systems operational, no incidents, update `2026-10-29T15:04:55.814Z`.

One registered local worktree, clean tracked state, no stashes; local and remote
branches and ignored build/tool/cache/artifact directories were inventoried and
preserved. No applicable AGENTS.md was found. Initial network and branch writes
were blocked by the sandbox; approved scoped operations succeeded. No reset,
clean, restore, stash pop, force push, quarantine restoration or exclusion.
Read requirements, gates, acceptance criteria, roadmap, governance, threat model,
security boundaries, both ADRs, source/catalog/adoption/dependency records,
contribution instructions and all three workflows. Reviewed Android build,
validation, packaging, signing configuration and offline receipt infrastructure;
relevant history includes PR #48's compiled-policy correction and PR #49's
one-way admission correction. The [readiness audit](gate-0-native-launch-readiness-audit.md),
[desktop record](gate-0-desktop-readiness.md), [incident](gate-0-native-host-antivirus.md)
and [integrated decision](gate-0-integrated-feasibility-decision.md) remain binding
limitations. No generic lifecycle or guest research is reopened.

## Independent-build procedure and input qualification

The existing Android workflow initially had only PR and main-push triggers.
Its push filter is extended to the exact research branch so this experiment can
run before PR publication. Existing triggers, permissions, validation steps,
25-minute timeout and negative controls remain; full history makes the fixed
reviewed commit available. No dispatch, extra action, upload or setup dependency.
Foundation additionally runs the new standard-library controls.

The pair deliberately builds the immutable **reviewed main above**, not a claim
that the newly authored comparison tool has already received independent review.
The orchestration commit is separately identifiable from its Actions run.
Two fresh detached worktrees share Git object storage only. Each must initially
have empty tracked/untracked/ignored status. Each has its own Android project,
build, CMake/native, generated resource/class, Gradle distribution and fresh
GRADLE_USER_HOME. No existing local APK or compilation output is copied.

Each invokes the unchanged bootstrap with `--no-build-cache`,
`--no-configuration-cache`, `--rerun-tasks`, `--dependency-verification=strict`
and `:gate0-harness:assembleRelease`; the bootstrap already uses `--no-daemon`.
A nonzero command, missing artifact, absent successful-build marker or FROM-CACHE
output stops comparison. The ordinary initial workflow build still performs
all previous debug/release/instrumentation/JVM/lint controls.

| Input | Exact experiment selection |
|---|---|
| Gradle | 9.6.0; distribution SHA-256 `bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01` verified by unchanged bootstrap separately in each tree |
| AGP | 9.4.0; strict existing Maven verification metadata |
| JDK | Existing runner Temurin 17.0.21+9; exact version guard, no new download |
| SDK | API 37, `platforms;android-37.0`, revision 2 |
| Build tools | 36.0.0, including existing aapt2 and apksigner |
| NDK | 28.2.13676358 / r28c |
| CMake | 3.22.1, including packaged Ninja |
| SDK command tools | Existing runner revision 12.0; exact guard despite directory named latest |
| Verification metadata | SHA-256 `4a5cd035a8b79f7a78beba61d7261b72454fd72554d4cdb210f0598898ef697a`; never rewritten |
| Configuration | Unchanged release: nondebuggable, no minification, minSdk 30, compile/target 37, ARM64 and x86_64 JNI plus ARM64 fixed dynamic PIE |
| Signing | Existing `signingConfigs.debug`, same ephemeral hosted runner home; no key installed or exported; public certificate digest and schemes checked independently on each result |

JDK, platform, build-tools, NDK, CMake and command-tools installed file inventories
are hashed before and after the pair, using SHA-256 over canonical JSON of sorted
relative file names and content SHA-256. Only counts and aggregate digests are
published. Each independently populated Maven files-2.1 inventory must match;
its relative coordinates and bytes are hashed the same way. Configuration files
and verification metadata are separately hashed. Shared SDK/JDK installation
does not mean shared compilation results. No dependency cache is reused here.
In principle, verified immutable dependency downloads could be shared with
separate build/transformation/output state; cache integrity alone would not prove
independence. This experiment avoids that extra assumption.

Existing [adoption licenses and limits](gate-0-isolated-worker-adoption.md) apply:
Gradle/AGP Apache-2.0 and component notices; JDK GPLv2 with Classpath Exception;
SDK terms and package notices; NDK LLVM exceptions/Bionic and other notices;
CMake BSD-3-Clause, Ninja Apache-2.0; Python PSF; checkout MIT. Apksigner is
already included in the adopted build-tools package: verification only, no new
signing tool or key-generation policy. The 185-component/322-artifact
[dependency ledger](gate-0-isolated-worker-dependencies.md) remains the existing
review baseline; independently resolved inventory equality is not a new license
audit. No third-party source is copied and no general repository license inferred.

## Comparison and controls

Each APK first passes the existing offline inspector, binding its exact source
and tree to compiled manifest/extraction rules, full native/ELF inventory and
the three corresponding stripped native build-output files. SDK apksigner
`verify --verbose --print-certs` must succeed; the parser requires one public
certificate digest and verified v2, retaining every reported signing scheme.
Certificate identity and signature validity are separate from key custody/trust.

The comparator hashes **every byte of each whole APK**, including signing
structures, and enumerates **every ZIP entry in stored order**. It records names,
uncompressed/compressed sizes, methods, CRC, timestamps, flags, offsets, extras,
comments, version/system/attribute metadata and each decompressed payload hash.
CRC checks, duplicate/empty/malformed/oversized inputs and unsupported ZIP64 or
multidisk layouts fail closed. It also hashes raw local-record, signing-block,
central-directory and EOCD regions. There is no timestamp normalization,
repacking, entry sorting in the artifact, stripping or favorable content subset.
Sorting difference names for the report does not change entry-order comparison.

All DEX, manifest, resource and native payloads therefore participate. Raw region
differences distinguish signing/layout changes from entry-content changes;
public signer/scheme differences are separately reported. A content-only result
explicitly omits ZIP metadata/compression/layout and signing structures; it never
passes signed-byte equality. The result is recomputed from the two actual files
before acceptance, rejecting partial/substituted result objects. Same path twice,
different source/tools/dependencies/configuration or missing input records fail.

Fourteen local deterministic test methods cover an explicitly unsigned fixture
positive; mutations to all seven fixture entries (manifest, resources, policy,
DEX and three native paths); each missing entry and an extra entry; timestamp,
compression and order changes; different/missing source and build inputs;
different signer/schemes; incomplete/failed signature output; missing/empty/
truncated/duplicate files; a fake signing-region mutation; malformed/partial/
substituted results; same-file substitution and a nonzero child build command.
Fixtures are not signed, installable, safe or independently compiled APKs.
Their passing assertions demonstrate comparator behavior only.
Two diagnostic controls check exact half-open differing-byte ranges, explicit
4096-range reporting limits, and ELF section labeling/hash differences. A fixture
initially omitted the leading dot in its expected section name; that fixture
assertion was corrected. No APK expectation or equality rule was changed.

## First-pair input and entry receipts

These are sanitized receipts from the first actual pair, not retained local APKs.
Directory digests use the algorithm above; the hosted runner remains trusted.

| Installed input | Files | Aggregate SHA-256 |
|---|---:|---|
| jdk | 455 | `20a3d2223c1974c59b1a343c8e358632ce4364580e7146e9af24001be0471528` |
| sdk | 11385 | `cfa092c4396b3c42bacc8505d6a218f2eb9623eea91ddaaa952f7cab76d9fe22` |
| build_tools | 169 | `1376d7e1fbeebd3b3d34e264c8f227f1ff1ec326191917646b7280a33a8b1a4d` |
| ndk | 8450 | `9fbbec3a802492282c982b0993e07b9be7481c9a3157782f80ae05d335de049c` |
| cmake | 2991 | `1a9cfb7d3a7b1e0f22a36ea78e777ccb805809dd16510115700c3fdf3966136e` |
| command_tools | 104 | `837cbe279c3e8b4f12f03e29c1ab638f9d40fbec2305ef2f487bcf6422f75c9b` |

| Configuration input | SHA-256 |
|---|---|
| `android/build.gradle` | `0537c547218629772f95b8cc26803dfeca0e85b6d7ace78f42fd4af02dfc1162` |
| `android/build.py` | `f6f38e7f4e23d6b3e8d93821fd08337de5efb230458ff35229d5432f316ea195` |
| `android/gate0-harness/build.gradle` | `6b017555eeeee8b5c965b858bff62b45d35cd6f7c6815002b2bf68605fa364f5` |
| `android/gradle.properties` | `977e0f33ccf4d27e6ecf39d0c03735ab869811f57f87efdc26de687cdab47a64` |
| `android/settings.gradle` | `dc68f0f06b52c4281068ce600646e45b977b662ffbb9bb43601662df9524040b` |

The complete entry order is below. All timestamps are `(1981,1,1,1,1,2)`;
no entry is omitted. Method 0 is stored, 8 is deflate. Sizes and offsets are
observations, never normalization inputs. A slash separates A and B where different.

| Entry | Size | Method | Compressed size A/B | Local offset A/B | Content SHA-256 A/B |
|---|---:|---:|---|---|---|
| `META-INF/com/android/build/gradle/app-metadata.properties` | 56 | 8 | 52 | 0 | `c007795180ce28378cc6f417b976dcb2af35df84ca806fd2847b5ec70a1270db` |
| `META-INF/version-control-info.textproto` | 46 | 8 | 48 | 139 | `38d377afa76b6364e5bf551cf4ffec1a881a46102a0047f523fbf148e0df6928` |
| `classes.dex` | 57168 | 0 | 57168 | 256 | `5f817be640dff54cb0a74af4341a01d68bcb3c90e12ad9d17d45acd3be49614d` |
| `lib/arm64-v8a/libpdva_launch.so` | 6928 | 8 | 2616 | 57468 | `d9406a4334186cfb31f636b0d28e3860121498af04144fabdb3e415fd82d7b51` |
| `lib/arm64-v8a/libsubstrate.so` | 20200 | 8 | 8534 / 8533 | 60145 | `ff74fc3027a719bef5d656de782faf348443e4de70d8da0ca2bde95e5e11070d` / `bf00549f5fdfef56bc7e72f6c8c4486679b389afd9ed6d65c9af3861c645d277` |
| `lib/x86_64/libsubstrate.so` | 13936 | 8 | 5179 | 68738 / 68737 | `f70363d8c9c088215674244d69dc93559ea1fd2055e4e3f1567b0e80ef66bb69` / `1b41f529e25f708d2b86ce7910a40b4e03e8f8f6c8ed4cd676b92a405cdd4b16` |
| `AndroidManifest.xml` | 2720 | 8 | 992 | 73973 / 73972 | `dad6a373c30982db4b0bf1db9243689e734d4cff94b605c786857c64ef28f3fd` |
| `res/4j.xml` | 2292 | 8 | 440 | 75014 / 75013 | `6ec8b1ce5ec70df6f8fa78a0a814192d13d9a4a6de850be1b65d9239fd6d4b33` |
| `resources.arsc` | 1004 | 0 | 1004 | 75494 / 75493 | `b352e390ff1571ade84978bce3e4a524238c646045ce51f2d5b17eea232be2eb` |

The same-source offline inspector identity is SHA-256
`367d2474fe4b9e77ba346fd2059685b33ff6a21579fffe4bbab2a8c7e34146e8`
for validate-harness.py; analyzer launcher
`c3277b8f17d26159c6496740114b5ed639d221107d94f47ff8a2ed4a5ea29026`;
aapt2 `1a6a396b9cd071f7040071fdd108718cb98c3c9f4960044f373b288993d19eb7`.
Both inspections resolve `0x7f020000` to `res/4j.xml`, policy
`all-domains-excluded-v1`, source rule SHA-256
`b0e88f2e1ffb1c8de5783db430a938f0bb86987ded7aca3b5cf77590247ae09d`.

## Results and limits

First experiment: orchestration commit `42bc7e5435629952f48d6635d6713ba113f12b12`,
[run 40907833663](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40907833663),
job `123567353042`, Ubuntu image `20261025.353.1`. Both fresh release builds
completed; both existing offline inspections and apksigner verification passed.
The comparison correctly exited 1 on the differing APKs. All preceding Android
build/JVM/lint/static/compiled-policy/receipt steps and 12 comparison controls
passed. This is an observed negative experiment, not infrastructure failure.

| First pair | Whole signed APK SHA-256 (both 81,312 bytes) |
|---|---|
| A | `e865a49b4759fd6e00b8e5115c0b3e2471e8852e4ed2b7fb4e21aa97e6b8bac8` |
| B | `17eaf77645e24a2520b18068146ba08b27f22e7cba4f4631deb6806413845021` |

Nine entries in the same order, identical timestamps and methods. All entry
contents match except `lib/arm64-v8a/libsubstrate.so` (20,200 bytes) and
`lib/x86_64/libsubstrate.so` (13,936 bytes). ARM64 compressed size is 8,534 versus
8,533, shifting later local-header offsets. Native CRCs differ; raw local records,
signing block and central directory differ, while EOCD matches. This is **not
solely a signing-key or ZIP-timestamp difference**. Manifest/resource entries
have identical contents despite shifted offsets. No all-entry content equality
claim is supported.

Both signatures verify using v2; v1, v3, v3.1 and v4 report false. The common
public certificate SHA-256 is
`2f9045aeeb87303a7b371fa691bf26045c1406f1817bebb55e058e39c8cb6dbb`.
The independently populated Maven inventory is 323 files in each, aggregate
SHA-256 `d8e8ff7857784e9872a777dc7017b423e5232e4d0ae9bf894684f8f14d869d4a`.
That count describes this resolved cache, not a change to the historical
322-artifact adoption ledger or verification metadata.

Diagnostic continuation: orchestration commit
`f791b7688efd477d75aa13fa2537097c5bcee19f`,
[run 40909232979](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40909232979),
job `123572331323`, same Ubuntu image. Both independent release builds completed;
both offline inspections and signature verifications passed. Input inventory
digests/configuration/metadata equal each other and the first pair's receipts.
The pair again **failed signed-byte and all-entry content equality**, with the
same two native entry names differing. All earlier Android steps passed, including
68 attempt assertions, 71 protocol/report assertions, lint, dormant native static
inspection (10,280 BPF vectors and five semantic mutants), five compiled-policy
test methods, private receipt and all **14** comparison controls.

| Diagnostic pair | Whole signed APK SHA-256 (both 81,312 bytes) |
|---|---|
| A | `598fe4d34dbcf1a541d73cb4ade7d21f7a95d03bcb497a78c98ae346b85833d0` |
| B | `f64ad60020aebf589537338a495f8d56ce2144232c9a9ba8931aaa2b5be5171a` |

The common certificate for this pair is
`bdfdda84ec5bbe2f95391e9eafade1dc25ff67255a1d5adb973ac72756063d16`;
v2 verifies, v1/v3/v3.1/v4 are false. It differs from the first runner's
development certificate, as expected for separate ephemeral runner homes.
**No cross-run signed-byte equality is asserted.** Within each principal pair,
the signing identity and schemes are identical, so differing keys do not explain
either pair's failure. No permanent signing key was supplied or exported.

| Native entry | A SHA-256 | B SHA-256 | Complete differing byte offsets |
|---|---|---|---|
| ARM64 `libsubstrate.so` | `5e8ae778ea8ab99f5c40cf528bfc9a09fcca4feb5f4b0a8836aaf377b60f0d71` | `6550c1d8b75f1945efa9eb61c2c41ee5d045e5b1d256f2025e8398e8a970aa7f` | `[792,812)`: 20 bytes |
| x86_64 `libsubstrate.so` | `293647128a50e4b37a5e3b53b50936f0815bcb244cbe33e4e838ce71a0ccc3ad` | `e40564cd50e4e393a2f0264aa7b24cb0bc1dc6ef42781383985995a177cd7eb9` | `[736,756)`: 20 bytes |

Offsets are zero-based and half-open in the **decompressed native entry**, not
the APK. Both range reports are complete (one range each, no truncation). The
first concrete native byte difference is offset 792 in the ARM64 library.
The ranges fall entirely within `.note.gnu.build-id`: ARM64 section `[776,812)`;
x86_64 section `[720,756)`. All other bytes in both native entries match,
including headers/gaps and other file-backed ELF sections, based on the complete
byte comparison, not merely section-name matching. Only that named section's
hash differs in each ELF section inventory. The 36-byte section hashes are:

| Section | A SHA-256 | B SHA-256 |
|---|---|---|
| ARM64 `.note.gnu.build-id` | `483ab1afc6f84464fb1c85b1999c6feeb718a808ff41ed0152de3d34b643c226` | `0d6902d42e438c78432a8022adeb45b039764b45b99bf359b9c3918e7940ed58` |
| x86_64 `.note.gnu.build-id` | `ac00075d5b691ddfeb742230bf45808ec23385c8aa627706246617526e10f1bb` | `31cadc0f7568f940cba978152a8b9e70ceab88e9c19d5965ae751964cc9d9657` |

All seven other entry hashes equal the first-pair table, including DEX, compiled
manifest/table/policy, both metadata entries and the fixed ARM64 dynamic PIE.
All nine entry names/order/timestamps/methods match within this pair. ARM64 JNI
compressed size is 8,533 in both; x86_64 is 5,181 versus 5,180. Manifest offsets
are 73,974 versus 73,973; policy 75,015 versus 75,014; resource table 75,495 versus
75,494. Raw local records, central directory and signing blocks differ; EOCD
matches. The resulting signatures therefore protect different package bytes.

Classification: **different tool-generated native build-ID bytes**, plus ZIP
CRC/compression/layout and APK signing-block differences. The observation does
not identify the complete cause of the differing build IDs. Different absolute
build roots are a deliberate independence boundary and a plausible input to
native debug/link identity; that explanation remains a hypothesis, not a proven
causal trace. No build ID, debug input, signature or ZIP field was removed or
rewritten to obtain equality. Neither failed job is converted to green.

Narrow verified correspondence is all seven unchanged entry contents and all
bytes of the JNI entries **outside the two explicitly identified 20-byte
ranges**. This excludes those identity bytes, ZIP representation and signing
structures; it is not complete native, content-level APK or signed-APK equality.
Signature validity also supplies no trusted release identity/custody result.

Existing artifacts were neither downloaded nor substituted. Local repository
regressions: 149 total,
145 passed and four existing Windows skips (host C, two symlink cases and POSIX
executable modes). Desktop receipt: 28 passed; image: 45 passed; frame: four
passed. Foundation/manifest/whitespace passed. Local Python is 3.12.14.
Full local Gradle/native/APK/device execution is NOT RUN because Windows native
host qualification remains unresolved. Hosted native/static/build results do
not clear that incident.

Final validation also checks all seven intended text files, new regular 100644
modes, full diff from verified main, generated-file exclusion, local Markdown
targets, whitespace, original source/licensing, tool provenance and public-data
hygiene. Android sources and verification metadata have no diff. Ignored assets
are preserved. Foundation and Android apply to the PR; QEMU does not. The final
evidence-only commit does not change tested comparison code or build inputs;
its post-publication checks are **unobserved**, as required by the stop boundary.

Local commands actually executed (using the existing bundled Python, no install):

```text
python .github/scripts/test-apk-reproducibility.py
python .github/scripts/validate-foundation.py
python .github/scripts/validate-harness.py
python .github/scripts/test-repository-validation.py
python .github/scripts/test-desktop-readiness.py
python .github/scripts/test-offline-image-inspect.py
python .github/scripts/test-frame-copy.py
git diff --check
```

## Smallest next proof

The artifact prerequisite is **not closed**. The next focused proof is an exact
causal trace from native compile/link/debug inputs to the differing build-ID
bytes, followed, only after review of any necessary build-input correction, by
another complete independent signed-byte comparison with the same signer inside
each pair. Keep build IDs and all security-relevant package contents intact.
Do not substitute stripping, repacking or changed expected hashes. A deterministic
build-ID result alone would still require whole-APK equality and the existing
offline/signature controls. This is a research reopening condition, not an
authorization for an unreviewed compiler flag, signing-policy change or phone run.

Even matching builds would establish only reproducible packaging in the stated
controlled environment and bounded source/dependency-to-output correspondence.
Both builds trust the same runner, compiler, dependencies and development key.
They cannot prove those trustworthy or establish permanent release-key custody,
incident clearance, stock-device installability/execution, independent current
worker inventory/closure, FD/map/Binder revocation, hostile-worker containment,
full interactive Android 17, Play/Google redistribution, Persona or VPN safety.
No gate advances and no physical work is authorized.

Only necessary source/tests/CI and this original record/index are intended for
the single PR. No APK, signing material, private cache, raw machine record,
private path, Persona data or incident sample is uploaded. Temporary hosted
artifacts have no independent private backup promise; old recovery gaps remain.
After publication, attach the same PR natively, verify its identity/association
once, and STOP without CI/bot/review/mergeability polling. Publication or required
association failure means **UNPRESERVED pending recovery of the same PR or its
association**, never authorization for a duplicate PR.

## PR #50 continuation: intermediate evidence, not a correction

Live preflight on 2026-10-29 confirmed canonical main remains
`61c68f87404a1b7e70e0314b73532322ee2de252`, and PR #50 remains the only open
PR, based on main, at `90e26acd89b368843f2212896173e63dec1f0df6`.
Reviews, comments and review threads were empty; GitHub Status reported all
systems operational. The local branch matched that head, with no tracked or
untracked changes, one registered worktree and no stashes. Existing ignored
build/toolchain/cache assets and historical branches were preserved. The full
seven-file PR diff and 100644 modes, requirements, two ADRs, provenance and
existing gate/security evidence were reviewed. No dependencies or licenses change.

The exact-head [Android run 40910857669](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40910857669),
job `123578110735`, failed the real independent comparison after successful
build/lint, inspection, signature and comparator regression steps. This is a
third observed pair, not a replacement for either earlier failure:

| Artifact | SHA-256 |
|---|---|
| Complete signed APK A | `e9ddb200f2d62061522dbc9060140f860162debc16b932e9d9247a1cae904f5d` |
| Complete signed APK B | `ab9637ec664be3d0f66321f74e43d250487efba138ecd68817a5310dfbb4ca7f` |

ARM64 differs at 20 bytes `[792,812)`; x86_64 differs at 19 bytes
`[736,748)` and `[749,756)`. One coincident byte inside the 20-byte x86_64
build-ID descriptor explains the count; this does not establish a different
descriptor size. The observed differences remain within `.note.gnu.build-id`.
Exact-head foundation run `40910857630` succeeded. Its Linux job log confirms
149 repository tests, 14 comparator tests, 28 receipt tests, 45 image tests and
four frame tests, plus the existing native/model/Linux research controls.
These are historical results for the incoming head, not validation of this revision.

**Cause: Unknown. Whole signed APK equality: not established.** No retained
hosted object/unstripped identities were available in those logs. A plausible
debug-path contribution is not a proven causal explanation.

Source review of the unchanged JNI CMake target confirms both C sources,
stack-protector-strong and RELRO/NOW. Retained local generated commands show
debug information in a RelWithDebInfo build, but are older Windows artifacts,
not proof of the hosted commands. They were read only; no native Windows tools
were run. At the recorded LLVM base
`3b5e7c83a6e226d5bd7ed2e9b67449b64812074c`,
[LLD Writer.cpp](https://github.com/llvm/llvm-project/blob/3b5e7c83a6e226d5bd7ed2e9b67449b64812074c/lld/ELF/Writer.cpp#L2822-L2886)
hashes the output buffer, including section contents, before writing the ID.
Its `Sha1` selection uses a 20-byte BLAKE3 construction with chunk hashing;
the option name must not be mistaken for a literal SHA-1 algorithm here.
This source mechanism can account for an ID surviving later debug stripping,
but does not identify the differing input in our builds. The NDK's recorded
Android patch layer remains relevant; this base-source review alone is not
binary/source equivalence proof. No upstream code was copied or new tool adopted.

This revision adds read-only diagnostics to each real independent build before
the unchanged complete comparison. It records original command/database/cache/
Ninja-rule hashes, labelled command tokens, object and unstripped/stripped ELF
hashes and section identities, and whether checkout/build paths occur in original
bytes (including which debug sections contain checkout paths). Missing or
ambiguous compile databases, unexpected source sets and missing unstripped
libraries stop the experiment. The build-ID section must survive stripping
unchanged, and stripped JNI bytes must exactly match their packaged entry.
Those checks are correspondence assertions, never whole-APK equality assertions.
The existing pinned package inventories cover Clang/LLD/strip/CMake/Ninja inputs.
The diagnostics observe strip outputs; they do not independently prove the
precise strip invocation or exclude every other linker input as the cause.

Actual command strings remain in ephemeral private runner files. Public display
labels replace known checkout/SDK roots; unknown path-bearing tokens are hashed.
This display redaction does not alter any original hash, ELF, APK or comparator
input. Neither raw logs, keys nor APKs are uploaded. No debug-prefix-map or other
compiler/linker adjustment is applied. There is no causal replay or corrected
independent-build result in this revision. A future investigation must inspect
the new real intermediates and use controlled input changes before proposing a fix.

The temporary branch-specific push trigger is deliberately retained alongside
PR/main coverage: no failing applicable experiment is hidden or disabled. Both
independent worktrees, empty build/cache conditions, same signer within each pair,
offline policy checks and strict final signed-byte assertion remain mandatory.
There is no continue-on-error, expected-failure conversion or output normalization.

Local validation for this continuation uses the existing bundled Python only:
19 comparator/diagnostic tests, including positive correspondence and negative
build-ID, package-byte and missing-input controls; foundation and harness
validators; repository-validation, desktop-readiness, offline-image and frame-copy
suites; and `git diff --check`. All passed: repository 149 tests (four platform
skips), receipt 28, offline image 45 and frame copy four. The first sandboxed
receipt/image attempts stalled creating temporary fixture directories; a bounded
trace located the receipt stall in `tempfile.mkdtemp`. Those two test processes
were stopped and both unchanged suites passed with authorized filesystem access.
Synthetic fixtures validate diagnostics only and are never substituted for the
two real APKs. No native compiler, device or Android runtime was executed locally.

The user explicitly kept the strict publication stop boundary: publish diagnostics
on this existing PR and leave **new CI results unobserved**. No intermediate push
or post-publication CI polling is authorized in this continuation. The original
negative results remain authoritative; this revision cannot be called a fix or
recommended for merge with the applicable check failed. After publication and
one native chat-association verification, STOP.

Windows native-host security incident: unresolved. Gate 0: **Unresolved**;
Gates A-G: **Not reached**; physical native-launch readiness: **NOT READY — STOP**.
No phone, USB, ADB, Android execution, quarantine restoration or security bypass.

## Debug-path mapping candidate on PR #50

Continuation date: **2026-10-29, America/Fortaleza**. Canonical main remains
`61c68f87404a1b7e70e0314b73532322ee2de252`. Live PR #50 head was
`6a2e6d883e44ce0781514cd4a980f41c170cb36b`, base main, the only open PR.
Reviews, comments and threads were empty. Both applicable Android jobs genuinely
ran and failed the independent signed-APK comparison; preceding build/lint,
native/bootstrap/APK-policy/signature/receipt and 19 comparator checks succeeded.
Foundation run `40953197411` succeeded: actual logs record 149 repository,
19 comparator, 28 receipt, 45 image and four frame tests on Linux; Windows records
45 image and four frame tests. No new candidate results are inferred from these.
GitHub Status reported operational components/no incidents, snapshot updated
`2026-10-29T20:39:47.555Z`. Full existing diff/files/100644 modes, requirements,
ADRs, build source/provenance/dependencies and evidence were re-reviewed. Local
tracked state was clean; one worktree, no stashes and 25,971 ignored files were
inventoried. Unrelated branches, caches and artifacts remain preserved.

### Confirmed diagnostic observations

| Incoming-head run / job | Signed APK A SHA-256 | Signed APK B SHA-256 |
|---|---|---|
| [40953197416](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40953197416) / `123726426168` | `a7867392cddf1ec32056cc0665d95817ed26801f0428e0462d8222a20d619904` | `f827653df1bfd4429278f7dfeadeb38f556ff2d031e32a8a587466ffa43b56a9` |
| [40953187201](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40953187201) / `123726391924` | `fe0584c09f423d2f64bad6475a3a27809ad8540ebe517de500704d832b674360` | `86bfe1f68d2b281abe7be12b4895c448e69a6d21662d5a31af95ab832538b7fd` |

Both still built historical main, not a mapped candidate. In each ABI, both
`probe.c` and `launch.c` object section comparisons differ only in `.debug_str`
and `.debug_line`; checkout paths occur in those sections. Ordinary code section
hashes match. Commands show `-g -O2 -DNDEBUG -fPIC`, stack-protector-strong and
FORTIFY, with no prefix maps. Unstripped libraries differ in `.debug_info`,
`.debug_str`, `.debug_line` and `.note.gnu.build-id`. Additionally, run
`40953187201` has an ARM64 unstripped `.symtab` difference; its cause is **Unknown**
and must not be erased by the debug-path hypothesis. Both runs confirm unchanged
build-ID section hashes across stripping and exact stripped/package bytes.
The full signed APK pairs differ. These are observations, not causal replay.

### Reviewed source mechanism and minimal candidate

At the adopted LLVM base `3b5e7c83a6e226d5bd7ed2e9b67449b64812074c`,
[Clang option definitions](https://github.com/llvm/llvm-project/blob/3b5e7c83a6e226d5bd7ed2e9b67449b64812074c/clang/include/clang/Driver/Options.td)
and [driver forwarding](https://github.com/llvm/llvm-project/blob/3b5e7c83a6e226d5bd7ed2e9b67449b64812074c/clang/lib/Driver/ToolChains/Clang.cpp)
support `-fdebug-prefix-map=old=new` for debug information. The broader
`-ffile-prefix-map` also changes predefined file macros; it is unnecessary for
the observed debug-only object differences and is not selected.
[CGDebugInfo](https://github.com/llvm/llvm-project/blob/3b5e7c83a6e226d5bd7ed2e9b67449b64812074c/clang/lib/CodeGen/CGDebugInfo.cpp)
applies prefix maps to source paths and the compilation directory, including
`DW_AT_comp_dir`. It can split directory and filename strings, so diagnostics
must not require one contiguous full synthetic source filename.
The [upstream CodeGen tests](https://github.com/llvm/llvm-project/blob/3b5e7c83a6e226d5bd7ed2e9b67449b64812074c/clang/test/CodeGen/debug-prefix-map.c)
cover compilation-directory mapping, absolute/relative replacements and ordering;
[driver tests](https://github.com/llvm/llvm-project/blob/3b5e7c83a6e226d5bd7ed2e9b67449b64812074c/clang/test/Driver/debug-prefix-map.c)
cover option forwarding/rejection. These tests were source-reviewed, not executed
locally. Raw web retrieval failed for two source files; exact GitHub contents API
retrieval succeeded. The LLD source cited above was rechecked: the output buffer
participates in build-ID generation, so debug inputs can affect the retained ID.

The recorded Android [patch ledger](https://android.googlesource.com/toolchain/llvm_android/+/e727bfb014bd436f581a66a450c939a6983a1fc3/patches/PATCHES.json)
was searched for debug/prefix/reproducibility titles. Older debug-related entries
have upper revision bounds below r530567; that title search is not a complete
patch-content audit or independent reconstruction of the shipped compiler.
Actual behavior remains subject to the qualified NDK controls below. No upstream
source is copied. Existing LLVM Apache-2.0-with-exceptions, CMake BSD-3-Clause,
Ninja Apache-2.0 and SDK/package notices remain the adoption basis; no new
dependency or license assumption is introduced. Repository owner remains maintainer.

The four-line CMake addition sets target-private compile options:

```cmake
# Keep full debug information, with stable identities for source and build paths.
target_compile_options(substrate PRIVATE
    "-fdebug-prefix-map=${CMAKE_CURRENT_SOURCE_DIR}=/pdva/jni/src"
    "-fdebug-prefix-map=${CMAKE_CURRENT_BINARY_DIR}=/pdva/jni/build")
```

CMake documents [current source](https://cmake.org/cmake/help/v3.22/variable/CMAKE_CURRENT_SOURCE_DIR.html)
and [current binary](https://cmake.org/cmake/help/v3.22/variable/CMAKE_CURRENT_BINARY_DIR.html)
directories as full paths. These two disjoint locations cover the JNI source/
headers and per-ABI generated build location, without incorporating runner roots
or the CMake build-directory hash into their synthetic identities. Debug information
is generated normally with mapped names; it is not removed or rewritten later.
Debuggers may need source-location substitution to find a developer's checkout.
No `-g` removal, build-ID flag change, stack-protection change, linker change,
RELRO/NOW change, ABI change or output-byte normalization is present.

**Immutable candidate source commit:** `aa517dfdfe2b72986d67ad65f7f1b34d8494118b`.
**Candidate tree:** `5965f746c6093c2bb86a99f3b4f361b6c315798c`.
That commit changes only the four CMake lines from incoming head `6a2e6d8`.
The subsequent comparator/evidence commit sets `SOURCE`/`TREE` to these exact
identities and adds CMakeLists.txt to the explicit configuration digest inventory.
Thus both new independent APK builds will use the candidate, not historical main.
The workflow step label is corrected accordingly; its commands, coverage,
branch-specific trigger, failure behavior and other checks remain enabled.

### Controls and current result boundary

For each real source/ABI/build, the hosted diagnostic now requires the exact two
mapping options, retained debug generation and stack protection. It replays that
actual compile command with only `-o` redirected into a fresh private control
directory. A second replay removes only the two mapping arguments. Compiler
identity, cwd, source, target and every other argument remain fixed; no shell
command evaluation is used. Commands with extra dependency-file outputs are
rejected rather than allowed to overwrite independent build state.

The positive replay must byte-match the independently built mapped object. Both
must retain nonempty debug information and code. The unmapped control must differ
and expose checkout/build paths; mapped bytes must exclude those paths and retain
the synthetic compilation directory. All sections other than debug sections and
their `.rel.debug*`/`.rela.debug*` relocation sections must match, including code
and code relocations. This limited section test checks whether debug mapping
changes generated code; it is **not** APK acceptance. Missing mapping, compiler
failure, missing/empty output, changed code/relocations or a vacuous negative
control stops the run. These separate outputs never replace either genuine APK,
JNI object, unstripped library or stripped/package output.

Existing build-ID-preservation and stripped/package checks remain mandatory.
The final comparator still checks every complete signed APK byte, with identical
verified signer/schemes within the pair. Build IDs, debug sections, signatures,
DEX, resources and ZIP metadata are not patched or ignored for that assertion.
No continue-on-error, expected-failure conversion or zero-step pass is added.

Local standard-library tests exercise the replay argument boundary, missing/
changed maps, disabled debug/stack protection, failed compiler propagation,
fresh-output requirement, changed code/code-relocation rejection, debug-relocation
handling and existing APK/signer/strip correspondence controls. Fixture success
is only tooling validation. No Windows native compiler or Android execution is
used; real qualified compiler replay, Android build/lint/APK checks and complete
candidate APK equality are **pending/unobserved at publication**.

This is a source-supported candidate correction, not proven causation or a proven
reproducibility fix. The remaining `.symtab` observation and any future unequal
APK must stay negative/Unknown. The user authorized exactly one final push of
both commits to existing PR #50, one native association verification and STOP;
no new-CI polling or intermediate iteration. Local validation passed: 22
comparator/control tests; 149 repository tests (four platform skips); 28 receipt,
45 offline-image and four frame-copy tests; foundation and harness validators;
and whitespace checks. Full intended diff, regular 100644 modes, links, privacy,
unchanged dependency/license inventory and exact candidate Android-tree
correspondence were reviewed. All historical failures remain above for comparison.
Gate 0 **Unresolved**; A-G **Not reached**; incident unresolved;
physical native-launch readiness **NOT READY — STOP**.
