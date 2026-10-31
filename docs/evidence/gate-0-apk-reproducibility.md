# Gate 0: independent research APK reproducibility

Date: **2026-10-29, America/Fortaleza**. Scope: PDVA-REQ-036–043, 048,
050–051 and 054. **Gate 0 Unresolved; Gates A–G Not reached. Physical
native-launch readiness NOT READY — STOP.** ADR-0001 Accepted; ADR-0002 Proposed.

## Question and experiment boundary

Do two fresh builds of the same reviewed Android research source, under the same
identified tools and development signing identity, produce identical signed APK
bytes? This record concerns only that bounded artifact-provenance prerequisite.
As of the 2026-10-31 D2 enforcement assessment, fourteen observed hosted pairs
**failed signed-byte equality**. Recent pairs establish matching native outputs, ZIP entries and v2
signatures; only the dependency-info signing-block value differs. The mechanism
uses fresh ephemeral-key and IV randomness in the reviewed implementation; actual
historical plaintext and random values remain Unknown. See the
[bounded source investigation](#dependency-metadata-encryption-source-investigation).
Local fixture success is not an independent APK build result. Historical sections
below retain their prior observations, failed parser runs and now-superseded Unknowns.

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

## Signing-block investigation: native correspondence established

Continuation date: **2026-10-29, America/Fortaleza**. Live canonical main remains
`61c68f87404a1b7e70e0314b73532322ee2de252`; incoming PR #50 head is
`614060c03e891c32dc773844837aa5b21a6ce2f9`, base main, the only open PR.
No reviews, comments or review threads. Actual jobs/logs confirm both applicable
Android runs failed only at strict final signed-APK equality. Foundation run
`40958523488` succeeded: Linux logs record 149 repository, 22 comparator,
28 receipt, 45 image and four frame tests; Windows records 45 image and four
frame tests. These are incoming-head results, not new signing-parser validation.
GitHub Status reported all operational/no incidents, snapshot updated
`2026-10-30T00:04:37.964Z` (still October 29 in America/Fortaleza).

Reviewed all eight existing PR files and 100644 modes, source/signing/toolchain
provenance, dependencies, requirements, both ADRs, governance and evidence.
Local tracked work was clean at the incoming head; 51 branches, one worktree,
no stashes and 25,971 ignored files were inventoried and preserved. No applicable
AGENTS.md was found. No native-host incident disposition or security setting changes.

### Direct observations from the mapped candidate

Both runs built candidate `aa517dfdfe2b72986d67ad65f7f1b34d8494118b`, tree
`5965f746c6093c2bb86a99f3b4f361b6c315798c`, twice with fresh independent build
and dependency directories. Both real JNI compile replay controls passed for
both sources/ABIs in both builds: mapped replay equals the real object; removing
the mapping exposes path differences while non-debug code/relocation sections
remain unchanged. Cross-build object, unstripped and stripped library hashes now
match, including complete build-ID bytes. The prior ARM64 unstripped `.symtab`
difference is absent in these candidate pairs; its historical result is retained.

| Run / job | Complete signed APK A SHA-256 | Complete signed APK B SHA-256 |
|---|---|---|
| [40958523492](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40958523492) / `123744884558` | `9bd9b562d828f0909d24a9489f7a46c48b9fc48bd802d1d795d2989e2486206b` | `36654490d12b14acfc7f242c3295f8cf98d398f8ab1fe7cc3fb32dfaedff5444` |
| [40958514716](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40958514716) / `123744853517` | `dedf7e1ee1b0e11b8ccc40da65eb33be9b0992bead9001c3301aa2bea68772a1` | `878651c4d661f0f24aabc324d662df017c6151eb815b86a9bc1f5046cdeff863` |

Every ZIP entry (content and recorded metadata), local records, central directory
and EOCD match within each pair. Only the complete APK signing-block hash differs.
Each pair has the same externally verified certificate fingerprint and schemes:
v2 true; v1/v3/v3.1/v4 false. This does **not** identify the actual v2 signature
algorithm or distinguish signature bytes from additional signing-block metadata.
No whole-signed-APK equality pass exists. Original ephemeral hosted APKs were not
uploaded or retained for this continuation; their logs contain aggregate block
hashes, not the fields needed to establish the remaining cause.

### Signing source review and hypotheses

The [AOSP v2 format](https://source.android.com/docs/security/features/apksigning/v2)
defines the little-endian block size/magic, length-prefixed ID/value pairs, nested
v2 signer data, algorithm-tagged digests/signatures, certificates, attributes and
public keys. Algorithm IDs distinguish RSA-PSS, RSA-PKCS1-v1_5, ECDSA and DSA.
The format explicitly supports deterministic PKCS1-v1_5 RSA signing. A certificate
fingerprint alone does not identify the selected signature algorithm.

The exact already-adopted official source publications were read without installing
or executing them. Content hashes pin this review:

| Source publication | SHA-256 |
|---|---|
| [apksig 9.4.0 sources](https://dl.google.com/dl/android/maven2/com/android/tools/build/apksig/9.4.0/apksig-9.4.0-sources.jar) | `c7a0f43d1e40fdf39725ac090f5c7bbaeae82d1e0bfd9cf2ee507a70eb5136b5` |
| [signflinger 9.4.0 sources](https://dl.google.com/dl/android/maven2/com/android/signflinger/9.4.0/signflinger-9.4.0-sources.jar) | `6ea6551350faf30f27845283e2961eed980228efaa1899f1839303b648ac50bb` |
| [AGP 9.4.0 sources](https://dl.google.com/dl/android/maven2/com/android/tools/build/gradle/9.4.0/gradle-9.4.0-sources.jar) | `d462c399729eb35241208899f937037e40f2f9157a54fa9c455595ed6ceca091` |

In apksig, `V2SchemeSigner.getSuggestedSignatureAlgorithms` chooses deterministic
PKCS1-v1_5 for RSA, not PSS; the key size determines SHA-256 versus SHA-512.
EC/DSA have distinct choices, and DSA has a deterministic-signing option. This
is source behavior, not evidence of the key/algorithm actually used in our APKs.
`SignatureAlgorithm.java` SHA-256 is
`f30b355e14c2970f91d4e875d08c72e602c628d18214622a4264f1ee9766cc45`;
`V2SchemeVerifier.java` SHA-256 is
`c33606383a44f77189144acbefc777f53b42d48901f5c3cfae36b9ff91bc5799`.
The verifier's nested parsing, algorithm-list comparison and cryptographic
signature checks were reviewed. The existing binary apksig dependency hash is
`7ae2e5980c77d853e3513074ee7c822bbdcdcde1668889d17faa7fe8bc8aa821`
in strict Gradle verification metadata. This source publication review is not an
independent source-to-binary reconstruction.

Signflinger `SignedApk.java` also inserts SDK dependency information under block
ID `0x504b4453`, separately from v2/v3 signatures. Official
[dependency-information documentation](https://developer.android.com/build/dependencies#dependency-info-play)
describes compressed/encrypted metadata in the signing block. Thus signature
randomness, metadata differences, padding and other blocks remain distinguishable
hypotheses; **none is identified as the actual cause yet**. No dependency metadata,
signature scheme or other field is disabled to obtain equality.

All source is reference-only; the new parser is original Python standard-library
code. Existing Apache-2.0 tool notices and SDK terms remain applicable, no package
is added, and no source archive or binary is committed. The repository owner
remains update owner. Builder apksig 9.4.0 is distinct from the SDK build-tools
36.0.0 verifier; installed tool-tree inventories already cover both environments,
and new diagnostics add verifier version, launcher hash and verifier-JAR hash.

### New bounded diagnostics and controls, not a correction

For each genuine independent APK, the existing qualified `apksigner verify`
success still precedes diagnostics. The parser admits at most a 4-MiB signing
block, 64 blocks and 64 entries per nested sequence, checks both outer sizes,
magic, length bounds, duplicate block/algorithm/attribute IDs, required fields,
and digest/signature algorithm-list agreement. It records offsets, lengths and
SHA-256 identities of every block and every parsed v2 field. It also reports
actual numeric algorithm IDs, certificate-chain/public-key identities, attributes
and whether verity padding is all zero. It binds the parsed leaf certificate to
the independent verifier's identity. DER/cryptographic validity is delegated to
the existing qualified verifier, not inferred from structural parsing.

Unknown IDs remain explicitly Unknown and hash-visible; additional schemes or
opaque blocks are inventoried without pretending to decode unsupported contents.
This does not exclude them from final equality. The pair report lists differing
diagnostic field paths; all original signing-block bytes remain in the strict
whole-APK comparison. No confidential field contents, raw keys, certificates,
signatures, keystores or host paths are logged.

A separate disposable copy flips a byte in each v2 signature. The same qualified
verifier must exit with signature-verification failure; zero exit, unrelated
failure or missing execution cannot count as a negative-control pass. The two
original APKs are never overwritten or replaced by those copies. This control
is authorized malformed-signature testing, not a reproducibility correction.

A separate signing-repetition experiment is **not performed**. The reviewed
Signflinger path closes its archive and inserts signatures in place; the current
pipeline retains no separate original unsigned APK for replay. The completed
hosted runners and their original inputs are unavailable. Constructing an unsigned
replacement by removing signatures would violate this task's restriction.
No alternate unsigned packaging pipeline, signing-policy change or key access
is introduced merely to manufacture that control. The two genuine builds still
provide independently generated signed outputs for direct field comparison.

No defensible signing correction can be selected before observing these real
fields. **Exact remaining field/cause: Unknown.** There is currently no established
need for a material policy change. If future evidence requires changing the
approved signing/security contract, explicit owner/ADR disposition is required;
this revision grants none. In particular it neither selects a weaker algorithm
nor introduces a permanent key or disables an existing scheme.

The pinned candidate SOURCE/TREE, Android configuration, original compiler
controls, all workflow triggers/checks and whole-signed-APK acceptance remain
unchanged. Existing failures and native correspondence are preserved. Local
fixtures test parser bounds, missing/duplicate fields, unknown IDs, actual
algorithm decoding, changed signature/key/certificate identity, verifier-control
outcomes and continued rejection of all signing-block differences. They are
structural fixtures only, never real signature validation or APK reproducibility.
Qualified execution of the new diagnostics and negative control remains
**pending/unobserved at publication**. One final push to PR #50, one native
association check, then STOP without new-CI polling.

Local validation actually completed for this revision: 27 comparator/diagnostic
tests; 149 repository tests (four platform skips); 28 desktop-readiness tests;
45 offline-image tests; four frame-copy tests; foundation and harness validators;
and `git diff --check`, all passing. Full intended diff, local links, privacy,
dependency/license scope and 100644 file modes were reviewed. These local tests
do not execute the hosted verifier or prove the new diagnostic result.

Gate 0 **Unresolved**; Gates A-G **Not reached**; Windows incident unresolved;
physical native-launch readiness **NOT READY — STOP**. No phone, USB, ADB,
emulator/guest execution, quarantine restoration or antivirus bypass.

## Parser correction: apksig's empty signed-data element

Continuation date: **2026-10-29, America/Fortaleza**. Live main remains
`61c68f87404a1b7e70e0314b73532322ee2de252`; incoming PR #50 head is
`2b76ab5a939262b98e10c561580899c2dff524a9`, base main, the only open PR.
Comments, reviews and review threads were empty. Existing eight-file diff and
100644 modes, requirements/ADRs, governance, provenance, dependencies, signing
source and evidence were reviewed. Local tracked state was clean; 51 branches,
one worktree, no stashes and 25,971 ignored files were preserved. No applicable
AGENTS.md was found. GitHub Status reported operational/no incidents (snapshot
updated `2026-10-30T00:04:37.964Z`, October 29 in the task timezone).

[Android run 40988011993](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40988011993),
job `123843463808`, and
[Android run 40988005880](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40988005880),
job `123843443920`, both completed independent build A and then stopped with
`APK_REPRODUCIBILITY=STOP: Trailing signing data`. Neither reached independent
build B or the final comparison. These are **two diagnostic-parser failures**,
not two additional compared APK pairs. The seven earlier compared failures and
native correspondence remain intact. External signature verification precedes
the failing parser call in the pinned script. The logs contain no traceback or
raw signed-data bytes, so runtime byte attribution is not independently retained.

Foundation run `40988012006` passed. Actual Linux log: 149 repository tests,
27 comparator tests, 28 receipt tests, 45 image tests and four frame tests.
Windows log: 45 image and four frame tests. The 27 structural fixtures omitted
the pinned emitter's fourth element and therefore did not expose this defect.

### Exact source mismatch and reproduced call boundary

The already-recorded official apksig 9.4.0 source archive was fetched again and
its SHA-256 checked against
`c7a0f43d1e40fdf39725ac090f5c7bbaeae82d1e0bfd9cf2ee507a70eb5136b5`.
In `V2SchemeSigner.generateSignerBlock`, lines 269-277 encode four elements:
digests, certificates, additional attributes, and `new byte[0]`. Its
`ApkSigningBlockUtils.encodeAsSequenceOfLengthPrefixedElements`, lines 762-773,
writes a uint32 length for every element. The empty fourth element therefore
contributes exactly **four zero bytes inside signed data**, covered by the
signature. It is not verity padding or another outer signing-block ID/value pair.

File SHA-256 identities in that source archive:

- `V2SchemeSigner.java`: `b55ae7a6fed23de3bedacc35df169558b432b25059280f6e1a0c88e60a7e8db5`.
- `ApkSigningBlockUtils.java`: `57b724a9299b78bdb4d6580d143382daa6f056be279ce129739a1d47f9f72b16`.
- Signflinger 9.4.0 `SignedApk.java`: `3771acd04812f4b089e28c16b5eb1d84358650986a72a5277d508ffa1337b24e`.

The public v2 overview lists the first three signed-data elements. The pinned
encoder adds this fourth one; its verifier authenticates the complete signed-data
bytes before parsing the first three fields and does not require exhaustion at
that boundary. Signflinger's reviewed integration uses the signing engine's block
and inserts dependency metadata separately. Accepting arbitrary verifier-tolerated
trailing bytes would be unjustified; only this exact emitter form is recognized.
No source is copied and existing dependency/license provenance remains unchanged.

The new source-shaped structural regression was executed **before** the parser
edit. It failed with the same error and a traceback through
`signing_block_snapshot → v2_signers → data.finish()`. The failure is specifically
the signed-data exhaustion check after reading the third field; not `value.finish()`
on the outer v2 sequence, `signer.finish()` after public key, or `item.finish()` on
digest/signature algorithm records. This reproduces the defect from the exact
encoder shape; it is not a retained genuine APK or a new cryptographic proof.

### Narrow correction and falsifiers

At that signed-data boundary only, the parser accepts either the three-field
overview form or one additional exact four-zero-byte empty-field encoding.
It records the latter as `apksig_empty_field` with absolute offset, size four and
SHA-256; absence is explicitly null. The complete signed-data hash still includes
every byte. The name describes the pinned implementation's empty element and
does not assign an undocumented semantic meaning. No bytes are discarded.

`SigningReader.finish()` is unchanged and still runs after this explicit field.
Nonzero lengths/contents, one-to-three-byte truncations, extra bytes, two empty
elements, and misplaced four-zero sequences after the signer sequence, public
key or algorithm record are rejected. Existing oversized-field, duplicate/missing
record, certificate-identity and altered-signature controls remain intact.
The new regression verifies field offsets/hashes and also proves that adding
this recognized field still fails the complete APK comparator when bytes differ.
Both new tests pass after the edit; the complete comparator suite now has 29 tests.

Local validation completed: 29 comparator tests; 149 repository tests with four
platform skips; 28 receipt, 45 offline-image and four frame-copy tests; foundation
and harness validators; and whitespace checks, all passing after the correction.
The focused regression's deliberate pre-fix failure is retained above. Reviewed
final diff, privacy, links, provenance, unchanged dependency/license inventory
and regular 100644 modes. No local native compiler or APK/device execution.

Candidate SOURCE/TREE, JNI mapping, native protections, signing policy/identity,
APK generation, external verifier, signature mutation control, equality acceptance
and all CI coverage remain unchanged. Actual signing-block field difference and
cause remain **Unknown** until parsing finishes on both real independent APKs.
New hosted results are **pending/unobserved**: one final push to existing PR #50,
one native chat-association verification, then STOP without CI/review polling.
Gate 0 **Unresolved**; A-G **Not reached**; Windows incident unresolved;
phone/native-launch readiness **NOT READY — STOP**.

## Dependency-info observation and policy proposal

Continuation: **2026-10-30, America/Fortaleza**. Read-only live preflight confirmed
main `61c68f87404a1b7e70e0314b73532322ee2de252`, existing PR #50 head
`b51d59d5c94f610bc04fba8d8808694f2d68e027`, base main and no other open PRs.
Reviews, comments and review threads were empty. The full eight-file incoming
diff, regular 100644 modes, workflows, governing requirements, ADRs, security
policies, existing provenance/dependency records and history were reviewed.
ADR-0003 was available. Clean tracked main was switched to the existing PR branch;
51 branches, one worktree, no stashes and 25,971 ignored files were preserved.
No applicable AGENTS.md was found. GitHub Status reported all systems operational,
no incidents, snapshot updated `2026-10-30T15:20:37.099Z`.

### Newly observed genuine comparisons

The corrected parser completed on both APKs in each of these exact-head runs:

| Run / job | Complete APK A SHA-256 | Complete APK B SHA-256 |
|---|---|---|
| [40989682770](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40989682770) / `123848788775` | `4bf51bbbc1bf71943b8ac2b9385b92f61cf4c3ad0f283fe6710d040d2aa71d15` | `b8ebac980c01676650a3f3ef96e52dc51a4ff047352a41ba4bc8d5cd29107ebc` |
| [40989678262](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40989678262) / `123848774175` | `39e6d283acc74d26b7fb98d318f3887ac32a279c87221a2732c57828b70e323d` | `2276dd0b020237ba28e4ba37aa5abb3c4cfdfc1f8bdedbb4e2c93627815aa827` |

Both builds in each run use the unchanged SOURCE
`aa517dfdfe2b72986d67ad65f7f1b34d8494118b`, TREE
`5965f746c6093c2bb86a99f3b4f361b6c315798c`, independent worktrees and dependency
homes, with the existing qualified Ubuntu 24.04/JDK/SDK/NDK/CMake inventories.
Build input inventories match within each pair. All APKs are 81,312 bytes.
There is no phone/device/OEM runtime result; JNI ABIs are ARM64 and x86_64.

Direct log observations: all native object/unstripped/stripped library hashes
match within each pair, with retained build IDs and successful mapping controls.
All ZIP entries, their contents/metadata, local records, central directory and
EOCD match. External signature verification succeeds; the decoded v2 algorithm
is `0x0103`, RSA-PKCS1-v1_5-SHA256. The entire v2 block, including signatures,
signed data, key and certificate, matches within each pair; so does verity padding.
The development signer differs across runs, not within a pair; no production
custody conclusion follows.

Both logs report `SIGNING_BLOCK_CHANGED_FIELDS=["/blocks/1/sha256","/sha256"]`.
Block 1 is dependency-info `0x504b4453`, value offset 77,966, length 185 bytes.
The enclosing signing block starts at 76,544 and is 4,096 bytes long.

| Run | Dependency-info A SHA-256 | Dependency-info B SHA-256 |
|---|---|---|
| `40989682770` | `94668f0b748cfc8f060f3346faf522ea72e859560aa5833549c26b83931d4f4c` | `e9edffdb2afab5c1617a87c738f534df5a07ef8c70fdcf33d614780da1082dbb` |
| `40989678262` | `e838a26079a859bda2d3ae2a339d12eec6aa51f0ff2daf24ff74e09b7b710700` | `3a30bcbc1a15b434b86e2f55c70484e270496ba90ee3c222372b165f79419819` |

Each run records `signed_bytes_equal=false`, `changed_regions=["signing_block"]`
and `APK_REPRODUCIBILITY=STOP: APK bytes or signing identity differ`. Actual signer
identity matches; the generic error is triggered by unequal complete bytes.
These are two additional **failed compared pairs**, bringing the total to nine;
the earlier two parser failures remain distinct. Both Android jobs failed honestly.

Positive controls: both genuine independent builds, qualified external verifier,
native/package correspondence and mapping replay completed. Negative controls:
both altered-signature copies per run were rejected by the verifier; 29 structural
comparator tests passed. SDK apksigner version `0.9`, JAR SHA-256
`3716d9311e55d2b0918a2fd9d54ba9e406c5f6abeea700b287f11259bc163dec`.
This verifier is distinct from builder apksig 9.4.0.

[Foundation run 40989682762](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/40989682762)
passed: Linux job `123848788828` logged 149 repository, 29 comparator, 28 receipt,
45 image and four frame tests, plus its existing hosted native/security controls;
Windows job `123848789159` logged 45 image and four frame tests. These are observed
hosted results, not fresh local execution or a passing Android comparison.

### Policy proposal, provenance and limits

The exact field is now established; the encryption/randomness mechanism and
plaintext correspondence remain **Unknown**. No signing-repetition experiment
or causal encryption control was performed. Source review and Android's current
[dependency information documentation](https://developer.android.com/build/dependencies#dependency-info)
describe separate encrypted metadata and recommend retaining it for Play Console
SDK/dependency reporting; that upstream description does not independently prove
the nondeterminism mechanism. Existing source archive/file hashes above remain
the provenance references; no dependency, source code or proprietary binary is added.

[PROPOSED ADR-0003](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md)
recommends retaining host metadata and the unresolved strict claim, compares four
alternatives, and defines owner decisions, evidence distinctions and falsifiers.
Only this ADR, the existing research record and necessary governance/evidence
links change. No signing/build/CI behavior, required acceptance, pinned candidate,
compiler security setting or guest boundary changes. Failed Android CI **blocks
merging PR #50 under existing rules**. ADR acceptance is explicitly pending;
committing or merging documentation cannot supply it.

Reopen implementation only after the explicit owner disposition and separately
scoped authorization described in the ADR. A new non-metadata difference falsifies
the scoped attribution for that new pair; qualified controlled evidence is required
before naming a causal encryption mechanism. No complete signed-byte equality,
production custody, distribution readiness or security result is established.

Local validation for this documentation revision: foundation validator passed
(149 files, 92 Markdown files, 54 requirements, three consecutive ADRs); harness
validator passed; 149 repository tests passed with four platform skips; all 29
comparator/diagnostic tests passed; whitespace check passed. Foundation validation
checks local Markdown targets; ADR status/headings, source links, privacy,
unchanged dependency/license scope and regular file modes were reviewed separately.
The AOSP v2 page timed out twice through the web reader, then returned HTTP 200
through a read-only HTTPS fetch; its signing-block ID/value structure was verified.
No local native compiler, Android build or device runtime was executed. Local
synthetic controls do not constitute a new genuine signed-APK comparison.

Gate 0 **Unresolved**; Gates A-G **Not reached**; Windows incident unresolved;
physical native-launch readiness **NOT READY — STOP**. No phone, USB, ADB,
emulator, guest execution or antivirus bypass. One final documentation commit/push
to existing PR #50, one native association verification, then STOP; subsequent
hosted results remain unobserved for owner review.

## Owner approval of Option A — 2026-10-30

The project owner explicitly approved **Option A** in the existing PDVA
conversation on October 30, 2026: retain dependency metadata in PDVA host APKs,
preserve the existing strict whole-signed-APK reproducibility requirement, and
retain all observed failures and unresolved limitations. This supersedes the
earlier pending disposition for Option A only. The dated research observations
and negative results above are preserved.

[ADR-0003](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md)
records the selected direction while retaining **PROPOSED** status for its
unapproved portions. Approval of the entire final ADR text remains pending.
Options B, C and D are unapproved. A future D evidence contract and any change to
required CI/merge criteria need separate explicit owner approval. No disabling
metadata, signing change, byte exclusion/normalization, CI suppression/skipping,
whole-APK success claim or merge is authorized. PR #50 remains **OPEN and blocked**.

Live preflight confirmed main `61c68f87404a1b7e70e0314b73532322ee2de252` and
PR #50 head `9efb446d2aab901f335a12b4b09ec809a4799af2`, base main, the only
open PR. Reviews/comments/threads were empty. Full incoming ten-file diff and
100644 modes, workflows, requirements/ADRs, provenance/dependency records and
history were reviewed. Clean tracked state, 51 branches, one worktree, no stashes
and 25,971 ignored files were preserved. GitHub Status reported operational/no
incidents (snapshot updated `2026-10-30T16:19:08.314Z`).

The newly inspected exact-head [Android run 41091266035](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41091266035),
job `124185439375`, completed independent builds A and B and failed the strict
comparison. APK A SHA-256 is
`3118fe5789ba4215e9b61deeed4ddffebf684239735c9ccc57504d338915b264`;
APK B SHA-256 is
`fa2cfa56522a62ed07070da1bef2c1c8699795e154a70e1543b0012688705df5`.
It reports no changed ZIP entries, matching signer identity, and only the
dependency-info block value hash plus enclosing signing-block hash changed.
V2 signatures and padding match. The result remains `signed_bytes_equal=false`
and `APK_REPRODUCIBILITY=STOP: APK bytes or signing identity differ`. This is the
tenth failed compared pair, separate from the two earlier parser failures.
The precise field is established; the underlying encryption/nondeterminism
mechanism and plaintext correspondence remain Unknown.

[Foundation run 41091265814](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41091265814)
passed: Linux job `124185439239` logged 149 repository, 29 comparator, 28 receipt,
45 image and four frame tests; Windows job `124185438796` logged 45 image and
four frame tests. These successes do not override the genuine Android failure.
Candidate SOURCE/TREE, dependencies, binaries/provenance, build/signing behavior,
comparator and required coverage are unchanged by this documentation revision.

Local validation for this owner-decision revision: foundation validator passed
(149 files, 92 Markdown files, 54 requirements, three ADRs), harness validator
passed, and 149 repository tests passed with four platform skips. Reviewed the
complete four-document diff, Markdown targets, approval/status wording, unchanged
requirements, privacy, provenance/license scope, 100644 modes and whitespace.
No comparator suite, native compilation, Android build or runtime was executed
locally for this revision; the hosted test counts above are separate observations.

Gate 0 **Unresolved**; Gates A-G **Not reached**; Windows incident unresolved;
physical native-launch readiness **NOT READY — STOP**. No phone, USB, ADB,
emulator/guest execution or antivirus bypass. One final commit/push to existing
PR #50 and one native association verification, then STOP without new-CI polling.

## Dependency-metadata encryption source investigation

Date: **2026-10-30, America/Fortaleza**. Question: can the current retained
dependency-info path reproduce complete signed bytes while preserving its security
properties? Scope: one source-driven investigation under approved Option A,
PDVA-REQ-036–041, 048 and 054. No build/policy/CI implementation is authorized.

### Preflight and latest negative observation

Live main remains `61c68f87404a1b7e70e0314b73532322ee2de252`; incoming PR #50
head `5e1dcb0213e1e4f7ef74e30ff6e9999c539555ee`, base main, only open PR.
Reviews/comments/threads were empty. The full ten-file accumulated diff, commits,
100644 modes, checks/workflows, requirements, ADRs, governance, provenance,
dependency identities and preceding investigation were reviewed. Clean tracked
state, 51 branches, one worktree, no stashes and 25,971 ignored files were preserved.
GitHub Status reported operational/no incidents (snapshot update
`2026-10-30T16:19:08.314Z`). No new APK experiment was requested or run locally.

[Android run 41093594199](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41093594199),
job `124193478821`, completed both independent builds and failed complete equality.
APK A SHA-256: `bf81c47bd03d86aa165d276a9afd7e02b75d324671a2a07f80ef33e19fb83769`;
APK B SHA-256: `2b9f172c20486db9b8584c865d1745e977cd7d05d8e999069fb3324f91c90c64`.
The unchanged candidate SOURCE/TREE is recorded above. The log again reports
`/blocks/1/sha256` and enclosing `/sha256` as the signing diagnostic differences,
and only `signing_block` as a changed APK region. This is the **eleventh failed
compared pair**, separate from the earlier two parser failures. Prior observations
remain unchanged, not retroactively reclassified.

[Foundation run 41093594133](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41093594133)
passed: Linux job `124193477438` logged 149 repository, 29 comparator, 28 receipt,
45 image and four frame tests; Windows job `124193477961` logged 45 image and
four frame tests. Android's preceding build/lint/inspection controls and its 29
synthetic comparator tests passed. Those are hosted observations, not a successful
whole-APK comparison or fresh local execution.

### Immutable sources and provenance

Official Google Maven source archives for AGP, Signflinger and apksig 9.4.0 were
read in memory and their hashes matched the existing ledger above. Additionally,
[builder 9.4.0 sources](https://dl.google.com/dl/android/maven2/com/android/tools/build/builder/9.4.0/builder-9.4.0-sources.jar)
hash to `384e5cfd3aa1292a85145c40f0b4b9f4af6f963c3c93d38ef8c19eff374b159a`.
These are existing build dependencies, not new adoption.

Tink is already pinned as `com.google.crypto.tink:tink:1.7.0`, binary SHA-256
`88970a456a08ba4c66b01b23e5846ca1095cc14e54cb48363e5d2e15a1307308`
in [verification metadata](../../android/gradle/verification-metadata.xml).
Maven Central's source-archive fetch failed TLS certificate verification (expired
certificate); no certificate validation was disabled. The official GitHub
`google/tink` repository redirects to `tink-crypto/tink`; its v1.7.0 annotated
tag `9940095f3081a116fa7a1337ad5ba27a3ccc59fe` resolves to immutable commit
[27b061bb9ed1af1a6f538410bff443290e427e66](https://github.com/tink-crypto/tink/tree/27b061bb9ed1af1a6f538410bff443290e427e66).
Files were retrieved over verified HTTPS from that commit. This establishes
release-source identity, **not an independent source-to-binary reconstruction**.

File SHA-256 ledger (AGP paths are relative to `com/android/build/gradle/`;
Tink Java paths are relative to `java_src/src/main/java/com/google/crypto/tink/`
at the immutable commit above):

| Source file | SHA-256 |
|---|---|
| AGP `internal/tasks/PerModuleReportDependenciesTask.kt` | `3564c644514be25a03b90e90866f8b42346be50ef0cd44218bd842b70a665318` |
| AGP `internal/tasks/SdkDependencyDataGeneratorTask.kt` | `e242e157a0073c26256a1c05d2560b2d910f31cda8aa8e4f7a876c69eedf163f` |
| AGP `internal/tasks/ApplicationTaskManager.kt` | `86a3f4624f2cc0e9c59f199bd42ab2bb8bed05f7a9aa816490cf176972a46d01` |
| AGP `tasks/PackageAndroidArtifact.kt` | `babff9a2066aa7aad6edee3b0ade91c85fcb0335a3f216cf3ce7adc39a82c1d8` |
| AGP `internal/packaging/IncrementalPackagerBuilder.java` | `331c54b1c5ff7f337e05fa994c28a3fb8960b84337f82ec8b4362800078b2ffe` |
| AGP archive `com/android/tools/build/libraries/metadata/AppDependencies.java` | `948812d2830abae85f713de7344f5cf338c1c7048407d53b65da13a99703960c` |
| Builder `com/android/builder/internal/packaging/ApkFlinger.kt` | `c29dbf8e8a755ce8c20f8527e667c852e582d497e8d6c69f35466f63dccc6096` |
| Signflinger `com/android/signflinger/SigningBlockUtils.java` | `6b48fca354da4972a4ff5f12f70a7edca9c48022383172f53c808af1898b0fc5` |
| Tink `hybrid/EciesAeadHkdfPublicKeyManager.java` | `4acf42e5da9a1334d6071fc631946e57529f8b8ffe12bb463701cdf3126c8883` |
| Tink `subtle/EciesAeadHkdfHybridEncrypt.java` | `c551789f40ca54fde0932d6bffa9cc384ffd32b699d2f27aa3b3c173c6be137b` |
| Tink `subtle/EciesHkdfSenderKem.java` | `2a4a7b519defeca4c5724b2c7389d171d4f74dfb8c55cde869f3274e6afb0d8a` |
| Tink `subtle/EllipticCurves.java` | `a3d96df7f18260795b641d228a95f0c543188406b10da3c60da988669f1741d8` |
| Tink `subtle/Hkdf.java` | `a0c29dbe05478baf58469351e6c1637d5b2e4b12397cc4b9f7943c3e47c403e7` |
| Tink `hybrid/RegistryEciesAeadHkdfDemHelper.java` | `5891f72753866cc4f6a9895adfbcc12c4e3c8cb200851b32f63556862cbdcdbf` |
| Tink `aead/AesGcmKeyManager.java` | `1b71a4552dbc4d9bdae42de1f51d7bfee9caebe11dbeb913923d69cab7c687a1` |
| Tink `subtle/AesGcmJce.java` | `9c6e86dd4d8516cc42c24d2ae9ba36dbb75f0ebc2809994e2069ea61c9c1795b` |
| Tink `aead/internal/InsecureNonceAesGcmJce.java` | `a09dcbdbe6e7060297a253b854a4101917515bb2404ed90ad8ca8fd376cb58ab` |
| Tink `subtle/Random.java` | `c7282eba27707158c1db2d4241fc85eb628c5b8da232de7d2e6bcc6941041dee` |
| Tink `hybrid/HybridEncryptWrapper.java` | `b5fe699327cd255d22605ff802fdec6a160ff20fa2662e9358abc0e714c7294a` |
| Tink `CryptoFormat.java` | `3a174200477736cddeed8b76ea060ee5a42ab3b1919d789ae31e617e9a283e13` |

Schema hashes at the same Tink commit: `proto/tink.proto`
`b77fb17296d5ca4cb8d24766d789ee79e19da0b6af1b3a66f45fd971ddecd9d4`;
`proto/ecies_aead_hkdf.proto`
`f4e8eab3d79234665184871542a55d0fdcd95d5594f57b352a16d29c7daceb72`;
`proto/common.proto`
`a77dc0e6087e2aebf4068763bfdbbf41073dbe8bdcc005b3fcf64c2f42ad6a98`;
`proto/aes_gcm.proto`
`4e7fb4958c76849b0a44b902ff4a5adef1f811f55434f9cdf54bce72da42e8f3`.
Previously recorded SignedApk/apksig file hashes still apply. Reviewed sources
carry Apache-2.0 notices; existing protobuf/SDK/component notices remain applicable.
No source archive, copied upstream code, binary, key, dependency or license-policy
change is committed. Source references do not adopt a new runtime.

### Direct source facts: complete production path

1. **Inventory.** `PerModuleReportDependenciesTask` lines 90–224 hashes runtime
   external AAR/JAR artifacts, traverses the resolved graph, records Maven
   coordinates, library edges, repository URLs and module dependencies. File
   repositories are excluded at lines 242–246. It uses iteration/index order;
   no claim that arbitrary graph order is canonical follows. Artifact bytes,
   coordinates, graph/order, repository/order and module name affect plaintext.
   Multiple files for one component select the first after warning. Actual
   historical `dependencies.pb` bytes were not retained in public evidence.
2. **Serialization.** The task builds `AppDependencies` and writes
   `dependencies.pb` using protobuf `writeTo`. Generated serializer lines
   301–315 write repeated fields in their stored order. The same fully ordered
   message gives the same encoding; equal source/tool inventories alone do not
   prove identical report bytes.
3. **Compression.** `SdkDependencyDataGeneratorTask` lines 301–326 reads that
   exact file and applies Java `DeflaterOutputStream`, then encryption. This is
   zlib/DEFLATE, not a timestamp-bearing gzip header. There is no random/time input
   in this wrapper. Byte identity is conditional on identical input and compressor
   implementation, not established by examining equal APK ZIP entries.
4. **Configuration.** A read-only standard-library wire decoder inspected only
   the embedded public configuration's algorithm fields, checked against the four
   Tink schemas. It reported ECIES-AEAD-HKDF public material; enabled primary;
   P-256 (enum 2), HKDF-SHA256 (3), empty salt, point format
   `DO_NOT_USE_CRUNCHY_UNCOMPRESSED` (3), CRUNCHY output prefix (4), and
   `AesGcmKey` format key size 16 bytes. No key coordinates, key ID or key bytes
   were emitted, substituted or used to encrypt. Context is the fixed UTF-8 string
   `SDK_DEPENDENCY_INFO`. These are decoded source parameters, not a new crypto
   execution or decrypted APK report.
5. **Encryption.** AGP calls `HybridEncrypt.encrypt` with compressed data and
   context. Tink's
   [ECIES primitive](https://github.com/tink-crypto/tink/blob/27b061bb9ed1af1a6f538410bff443290e427e66/java_src/src/main/java/com/google/crypto/tink/subtle/EciesAeadHkdfHybridEncrypt.java#L61)
   calls the sender KEM on every encryption. Its
   [sender KEM](https://github.com/tink-crypto/tink/blob/27b061bb9ed1af1a6f538410bff443290e427e66/java_src/src/main/java/com/google/crypto/tink/subtle/EciesHkdfSenderKem.java#L69)
   creates a fresh ephemeral EC key pair, computes ECDH with the configured
   recipient, encodes the ephemeral public point, and derives the 16-byte DEM key
   through HKDF-SHA256 over encoded point plus shared secret, salt and context.
   `EllipticCurves.generateKeyPair` uses JCA `EC`, `initialize(spec)`,
   `generateKeyPair()`; the [JDK 17 API contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/security/KeyPairGenerator.html)
   supplies default SecureRandom when no random argument is given. The particular
   historical provider/entropy state is not identified here.
6. **Nonce and authentication.** The DEM helper replaces template key material
   with the derived key, and AesGcmKeyManager selects
   [AesGcmJce](https://github.com/tink-crypto/tink/blob/27b061bb9ed1af1a6f538410bff443290e427e66/java_src/src/main/java/com/google/crypto/tink/subtle/AesGcmJce.java#L49).
   Every encryption draws 12 bytes from Tink's thread-local, self-seeded
   `SecureRandom`. The underlying transformation is `AES/GCM/NoPadding`,
   AES-128 with a 16-byte authentication tag. IV is prepended to ciphertext/tag.
   ECIES uses empty AEAD associated data; the context is bound through HKDF.
   The helper's initial random template key is overwritten by the derived key;
   it is not an additional serialized random field.
7. **Output and insertion.** The hybrid wrapper prefixes the result with the
   fixed five-byte CRUNCHY identifier. ECIES includes its ephemeral public point
   before IV/ciphertext/tag. PackageAndroidArtifact lines 931–939 reads encrypted
   `sdkDependencyData.pb`; IncrementalPackagerBuilder and ApkFlinger forward those
   bytes to SignedApkOptions. SignedApk lines 253–257 adds them under
   `0x504b4453` separately from apksig's v2/v3 output. SigningBlockUtils rebuilds
   the container/padding through apksig, preserving the supplied value. This path
   does not decrypt, normalize or regenerate the encrypted value at insertion.

### Conclusion, security implications and falsifiers

**Source-established mechanism:** this configured production path consumes fresh
ephemeral-key randomness and fresh GCM-IV randomness on each encryption. Identical
plaintext, recipient configuration and context can legitimately yield different
ciphertext. Randomized outputs are the intended operation, not a compiler path or
v2 RSA-signature defect. Fresh random draws are not a mathematical guarantee that
two outputs can never collide; no universal impossibility claim is made.

**Inference for the recorded APKs:** the source mechanism explains their differing
dependency-info values while application contents, v2 signatures and padding
match. It is a sufficient source-level explanation, not a controlled reconstruction
of those particular ciphertexts. Equal historical plaintext, individual nonce/KEM
bytes, provider entropy and their precise contribution to each observed pair remain
**Unknown**. Whole-value hashes cannot isolate those subfields.

The reviewed AGP task hard-codes this configuration and exposes no deterministic
encryption option. The inspected
[Android dependency-metadata documentation](https://developer.android.com/build/dependencies#dependency-info)
describes retaining metadata or opting out, not a supported deterministic-retention
mode. No documented, source-supported configuration was found that both preserves
this fresh-randomness contract and reliably reproduces whole signed bytes across
genuinely independent builds. This conclusion is scoped to the reviewed versions
and current configuration, not every possible future scheme.

Forcing repeatable ephemeral secrets changes the ECIES security assumptions;
deriving them from public inputs could expose the shared secret. Reusing an
AES-GCM key/IV pair across different plaintexts undermines confidentiality and
authentication. Fixing only the IV would not remove the ephemeral-key variation.
A specially designed deterministic encryption scheme requires separate protocol,
recipient-compatibility and security review; it is not a safe configuration toggle.
No keys were generated, recovered, disclosed, altered or substituted. No crypto
operation, RNG override, ciphertext reuse or byte normalization was performed.

**Disposition: STOP attempts to force byte equality under the current encryption
path.** Retain metadata, strict comparison and its honest failures under approved
Option A. PR #50 stays OPEN and blocked. No Option B/C/D, changed acceptance
contract, required-check change or merge is approved; full ADR acceptance is pending.
No policy question needs improvisation to finish this source-only record.

**Smallest falsifiers / reopening conditions:** a supported upstream API and source
path demonstrating secure deterministic retention would reopen the configuration
assessment. A source/binary mismatch or a different selected primitive invalidates
this source-path attribution. If exact historical causal isolation is later needed,
a separately reviewed diagnostic could hash pre-encryption report/compressed bytes
and separately hash the public output prefix, ephemeral point and IV of both
original outputs, without keys or RNG changes. Different plaintext would refute the
same-plaintext premise for that pair; different point/IV hashes would locate fresh
output variation. This is a proposed falsifier, **not implemented or executed**.
Another full APK pair without those new measurements would add no causal resolution.

No synthetic encryption demo was run: it would only demonstrate general randomized
crypto and could not establish the historical report bytes. The source-parameter
decoder is a diagnostic observation; it does not prove actual Google decryption or
metadata semantics. The existing tests and original failures retain their exact scope.

Local validation for this source-only revision: foundation validator (149 files,
92 Markdown files, 54 requirements, three ADRs), harness validator and 149
repository tests passed, with four platform skips. Source archives/file hashes
and parameter decoding were actually inspected as described above. No local
Tink encryption, independent APK build, native compilation or runtime test ran;
no synthetic crypto result is claimed. Reviewed links/anchors, Option A approval
and remaining PROPOSED status, privacy, existing license/dependency scope and
regular 100644 modes. An extra final blank line found by the initial whitespace
check was removed before publication; the final whitespace check passed.

Gate 0 **Unresolved**; Gates A-G **Not reached**; Windows native-host incident
unresolved; physical native-launch readiness **NOT READY — STOP**. No phone, USB,
ADB, emulator/guest execution or security bypass. One final reviewed publication
and native association check, then STOP without new-CI/review/mergeability polling.

## Option D contract proposal — 2026-10-30

Question: what limited artifact correspondence can be reported independently of
the failed whole-byte assertion, without weakening approved Option A? The focused
[PROPOSED Option D contract in ADR-0003](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md#proposed-option-d-contract-additive-research-correspondence)
is the sole new contract proposal. It specifies an artifact-bound envelope,
per-property scope and controls, failure/Unknown admission, requirement mappings
and exact owner decisions. Recommendation D1 adds research reporting while keeping
the strict assertion and merge block intact. It cannot unblock PR #50. D2 would
require separately reconsidering A's merge prerequisite and is not recommended
or authorized here. Option D and full ADR acceptance remain pending.

Live preflight: main `61c68f87404a1b7e70e0314b73532322ee2de252`, PR #50 head
`82e2eb17f9ab0581000ff92afe7ac68e04c537a6`, base main, only open PR; reviews,
comments and threads empty. Reviewed the full ten-file accumulated diff, commits,
100644 modes, workflows/checks, requirements/ADRs, provenance/dependencies and
existing evidence. Local tracked state was clean; 51 branches, one worktree, no
stashes and 25,971 ignored files were preserved. GitHub Status snapshot updated
`2026-10-30T22:09:55.822Z` listed components operational but an active minor
Dependabot-alert viewing incident; no clean security-alert review is inferred.

Read-only inspection of [Android run 41136876242](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41136876242),
job `124341388131`, found both builds complete and genuine strict equality failure.
APK A SHA-256 `2d8afa90ae0586527058438ed6290a05b3d032a37072c5376410be5e1ca31d81`;
APK B SHA-256 `a73dadbc097dc9b3875e1fe0b3aa7b20b4689ff48137973f6960cbe73db7ce2b`.
No ZIP entries changed; signer identity matched; signing-field differences were
`/blocks/1/sha256` and enclosing `/sha256`, and `signing_block` was the only changed
APK region. This is the twelfth failed pair, not an experiment initiated by this
proposal. The earlier parser failures and encryption investigation remain intact.

[Foundation run 41136876193](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41136876193)
passed: Linux job `124341388102` logged 149 repository, 29 comparator, 28 receipt,
45 image and four frame tests; Windows job `124341388368` logged 45 image and four
frame tests. These observed successes do not override Android's failure. Existing
source hashes, binary-verification identities and license/provenance limits are
reused; no repeated source download, encryption control or new APK build occurred.

Only ADR-0003, this record and its index change. No source, Gradle, signing,
metadata, comparator, tests, workflow, required check, exit code, permission or
security setting changes. Contract controls described in the ADR are proposed
qualification requirements, not newly executed tests or demonstrated D acceptance.
The missing proof is the future reporter's complete binding/control behavior,
not another undifferentiated independent APK comparison.

Local validation for this proposal: foundation validator passed (149 files,
92 Markdown files, 54 requirements, three ADRs), harness validator passed and
149 repository tests passed with four platform skips. Reviewed all three changed
documents, local links/new anchor, requirements and approval wording, privacy,
unchanged dependencies/licenses, regular 100644 modes and whitespace. No comparator
suite, encryption diagnostic, native compiler, Android build or runtime was run
locally for this documentation-only proposal. Hosted counts above are separate.

Gate 0 **Unresolved**; Gates A-G **Not reached**; physical native-launch readiness
**NOT READY — STOP**. No phone, USB, ADB, emulator/guest execution or security
bypass. Publish to existing PR #50, verify native association once, then STOP;
new CI/review/mergeability remains unobserved.

## Research-only merge-policy decision proposal — 2026-10-30

The [decision in ADR-0003](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md#research-only-merge-decision-stop-under-current-authority)
recommends STOP under approved A. D1 adds reporting but cannot unblock PR #50.
A narrowly scoped D2 research-preservation exception could permit a merge with
an openly failed equality assertion only after explicit amendment of A's merge
prerequisite, exact acceptance/control mapping approval and independently reviewed
implementation. It cannot preserve that part of A unchanged. No exception,
workflow change or full ADR acceptance is approved by requesting this proposal.
The ADR is the single decision text; its existing control matrix is not duplicated.

Live preflight reverified main/base `61c68f87404a1b7e70e0314b73532322ee2de252`,
PR #50 head `c6474685be60870b32c9cc4cecdfabfa562c8b43`, twelve commits and the
full ten-file accumulated diff with regular 100644 modes. PR #50 was the only
open PR; reviews, comments and threads were empty. Requirements, ADRs, governance,
security/evidence policies, source investigation, dependency and binary adoption
records were reviewed. Local tracked state was clean; 51 branches, one worktree,
no stashes and 25,971 ignored files were preserved. GitHub Status snapshot updated
`2026-10-30T22:32:14.2Z` reported operational components and the Dependabot incident
in monitoring after mitigation. This is not a vulnerability-free dependency claim.
Classic main protection returned HTTP 404, "Branch not protected"; main branch
rules and repository rulesets returned empty arrays. These observations do not
waive documented merge obligations or authorize using a merge button.

Read-only review of existing [Android run 41138308496](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41138308496),
job `124346137487`, confirmed both independent builds and the thirteenth genuine
failed whole-byte pair at that head. APK A SHA-256
`00e9e9bd2e25929788dd2183632bc3a991a065918a6da8f6cd81937d27a62393`;
APK B SHA-256 `547651c104bba4c4650944eb6bbf284640516af5a4582cc621129e3845dd6191`.
Both sizes were 81,312 bytes. ZIP entries/content, v2 block/signatures and padding
matched; the 185-byte dependency-info values differed and signing_block was the
only changed APK region. Same signer/schemes held. The job ended with the real
STOP for differing APK bytes; its prior checks and 29 comparator tests succeeded.
This inspection initiated no experiment and does not claim historical plaintext
identity or a new runtime encryption falsifier.

[Foundation run 41138308198](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41138308198)
passed at the same head: Linux job `124346136054` logged 149 repository, 29 comparator,
28 receipt, 45 image and four frame tests; Windows job `124346136266` logged 45 image
and four frame tests. These are inspected hosted results, not locally rerun tests,
and neither passes Android nor qualifies production. Prior failures remain intact.

The policy review rejects making the combined Android job optional: it also owns
mandatory security/build obligations. A future owner-approved separation would
need independent enforcement and failure-propagation controls, complete coverage
and honest visible failure, not a passing wrapper around the failed assertion.
No CI, comparator, signing, encryption, dependency, metadata, source or security
setting changes here. The accumulated PR's earlier code still needs full review;
this documentation revision supplies no adoption or merge waiver.

Local validation: foundation validator (149 files, 92 Markdown files, 54 requirements,
three ADRs), harness validator, and 149 repository tests with four platform skips.
Reviewed the three-document diff, local Markdown targets/new anchor, approval/status
wording, requirement consistency, privacy, unchanged licenses/dependencies and
provenance, regular file modes and whitespace. No local comparator/encryption test,
native compiler, Android build or runtime execution was performed for this proposal.

Gate 0 **Unresolved**; Gates A-G **Not reached**; Windows native-host incident
unresolved; physical native-launch readiness **NOT READY — STOP**. No phone, ADB,
USB, emulator, guest execution or security bypass. Publish one documentation commit
to existing PR #50, check native association once, then STOP without observing new
CI, reviews, bots or mergeability.

## D2 enforcement design assessment — 2026-10-31

The sole [concrete assessment in ADR-0003](../decisions/ADR-0003-host-apk-dependency-metadata-and-reproducibility-evidence.md#d2-enforcement-design-assessment--2026-10-31)
maps all Android steps, including mandatory controls inside the final research
process, and evaluates a minimal split against official GitHub semantics.
Recommendation B is **STOP**: required contexts alone admit skipped/neutral
results, and an optional comparison does not enforce completed execution. The
current process combines security/build/parser failure and equality failure in
exit 1. Treating that exit as an accepted research outcome is rejected. A future
trusted execution/evidence validator needs separate design, adoption, independent
qualification and owner authority; no such enforcement is established here.
The ADR provides the proposed replacement owner text, failure matrix and adversarial
qualification plan. It is not D2 approval, changed acceptance criteria or a merge
waiver. A's current merge prerequisite remains binding.

Live preflight: main/base `61c68f87404a1b7e70e0314b73532322ee2de252`, PR #50 head
`aaa52498aca577828acda5b6e5dd9e930f14ba15`, thirteen commits, ten accumulated files,
regular 100644 modes. PR #50 was the only open PR; reviews/comments/threads empty.
Reviewed accumulated comparator/native/workflow changes, governing requirements,
ADRs, security/evidence policy, dependency/adoption records and existing exact-source
encryption evidence. No binaries/dependencies were added or downloaded. Local
tracked state was clean; 51 branches, one worktree, no stashes and 25,971 ignored
files preserved. Main protection returned HTTP 404 "Branch not protected"; active
main rules and repository rulesets were empty. Technical mergeability grants no
authority. GitHub Status updated `2026-10-31T03:53:04.279Z` reported operational
systems and no active incidents; this is not a dependency security assessment.

Existing [Android run 41141493558](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41141493558),
job `124356574428`, attempt 1, pull_request event at that head, completed both
builds and failed strict equality. APK A SHA-256
`220b8e5d7eff242256e9b33f07386104c63e985ecfdd84f1e322332338fd5c04`;
APK B SHA-256 `a7379e60298efc46342c5e2574a11b3f52fd81a6cdbfeadc4d7fc9c24dfbc3b7`.
Both were 81,312 bytes. No ZIP entries changed; only signing_block differed, with
signing diagnostic paths `/blocks/1/sha256` and `/sha256`. Both altered-signature
controls were rejected; 29 comparator tests passed. This is the fourteenth failed
pair, observed read-only, not a newly initiated experiment. Historical parser
failures, negative native results, source findings and plaintext Unknowns remain.

[Foundation run 41141493338](https://github.com/innercoder78/privacy-decoy-virtual-android/actions/runs/41141493338)
passed at that head: Linux job `124356574380` logged 149 repository, 29 comparator,
28 receipt, 45 image and four frame tests; Windows job `124356574046` logged 45 image
and four frame tests. All earlier Android steps succeeded; none overrides its
failed comparison. These hosted observations are distinct from local validation.

Official GitHub documentation independently checked on 2026-10-31 is linked in
the ADR. The assessment is source/API reasoning, not a live enforcement experiment
or independent implementer review. No merge-denial tests, rule changes, external
check producer, workflow split or future control implementation was performed.
The missing qualification is enforcement of execution, identity and negative
outcomes, not another unchanged APK build. An owner-approved isolated enforcement
test would be a new falsifier and needs separate authorization.

Local validation: foundation validator (149 files, 92 Markdown files, 54 requirements,
three ADRs), harness validator and 149 repository tests with four platform skips.
Reviewed three-document scope, local links/new anchor, PROPOSED status and owner
wording, requirements, privacy, provenance/licenses, regular modes and whitespace.
No local comparator, crypto, native compiler, Android build or runtime test.
No implementation, workflow, trigger, required-check, signing or metadata change.

Gate 0 **Unresolved**; Gates A-G **Not reached**; Windows native-host incident
unresolved; physical native-launch readiness **NOT READY — STOP**. One reviewed
documentation publication to existing PR #50 and one native attachment check,
then STOP without new CI, review, comment, bot or mergeability polling.
