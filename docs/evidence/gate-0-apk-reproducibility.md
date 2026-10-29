# Gate 0: independent research APK reproducibility

Date: **2026-10-29, America/Fortaleza**. Scope: PDVA-REQ-036–043, 048,
050–051 and 054. **Gate 0 Unresolved; Gates A–G Not reached. Physical
native-launch readiness NOT READY — STOP.** ADR-0001 Accepted; ADR-0002 Proposed.

## Question and experiment boundary

Do two fresh builds of the same reviewed Android research source, under the same
identified tools and development signing identity, produce identical signed APK
bytes? This record concerns only that bounded artifact-provenance prerequisite.
At initial experiment publication to the research branch, the hosted pair is
**NOT RUN**; local fixture success is not an independent APK build result.
The final disposition must be recorded before publishing the single evidence PR.

The procedure is original PDVA standard-library code in
[apk-reproducibility.py](../../.github/scripts/apk-reproducibility.py), with
[disposable unsigned controls](../../.github/scripts/test-apk-reproducibility.py).
No app, manifest, extraction policy, native source, Persona, dependency version,
verification metadata, permanent key or production signing policy is changed.

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

Twelve local deterministic test methods cover an explicitly unsigned fixture
positive; mutations to all seven fixture entries (manifest, resources, policy,
DEX and three native paths); each missing entry and an extra entry; timestamp,
compression and order changes; different/missing source and build inputs;
different signer/schemes; incomplete/failed signature output; missing/empty/
truncated/duplicate files; a fake signing-region mutation; malformed/partial/
substituted results; same-file substitution and a nonzero child build command.
Fixtures are not signed, installable, safe or independently compiled APKs.
Their passing assertions demonstrate comparator behavior only.

## Results and limits

Hosted pair: **NOT RUN at initial branch commit**. Whole signed-byte equality,
per-entry actual APK equality and signature correspondence remain **Unknown**
until the actual run is recorded. No synthetic fixture or historical APK is a
substitute. Local comparison controls: 12 passed; source/foundation checks passed.
Full local Gradle/native/APK/device execution is NOT RUN because Windows native
host qualification remains unresolved. Additional regression outcomes and the
hosted result will be recorded before evidence PR publication.

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
