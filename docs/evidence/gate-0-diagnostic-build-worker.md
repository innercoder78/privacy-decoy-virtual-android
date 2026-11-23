# ADR-0006 build worker assessment

**Inference — STOP before the SDK experiment.** On 2026-11-23 the available
Windows session supplied no identifiable fresh worker with a known build
identity and evidence excluding the incident host's tools, caches and keys.

**Fact/Source — source and controls.** Remote main, fetched main and the
evidence checkout agreed at `02b8545af3415cb99af0af0e9c90a5c3ae5f75b9`.
[ADR-0006](../decisions/ADR-0006-one-attempt-java-memory-diagnostic.md)
binds the diagnostic to `b84af1c7764298b06bc8b356c38b3ef9fd8f0db3`.
Git resolved its tree to `0dfc367c4c87defe7d468946bf3e7cf477cc0282`.
The Android subtree had no diff against main. Both main workflows succeeded.
There were zero open PRs at preflight. Effective main rules required a PR,
strict foundation and offline-image-windows checks, and blocked deletion and
non-fast-forward updates. The classic protection endpoint returned 404.

**Runtime Observation — source admission.** The registered checker with
`--check-source-ref` rejected the ADR-bound pre-registration commit with
`exact-diagnostic-adr`. The same checker accepted the fetched registration
commit. The former lacks the registered ADR. Identical Android files do not
resolve the choice of an authorized full build tree. Preserve both outcomes
for owner disposition before any build. Foundation validation passed under the
worktree owner after Git rejected cross-account access to the evidence checkout.

**Runtime Observation — desktop.** A token inspection identified a local
offline sandbox account at medium integrity, with no Administrators group in
the reported token. Executable lookup resolved Java in the host installation.
The JDK release file reported Eclipse Adoptium 17.0.21. Installed SDK package
properties reported platform API 37.0 revision 2 and Build Tools 36.0.0.
Neither SDK environment variable selected an installation in this process.
No standalone Gradle command resolved. The host compute service was stopped,
and the process query returned no matching running VM worker. Private evidence
and archive directory names were visible. Their contents were left untouched.

**Unknown — worker and inputs.** No prospective Gradle launcher, build token,
provisioning record or cache isolation was identified. The observed shell can
read host tools on the desktop associated with the [unresolved Windows incident](gate-0-native-host-antivirus.md).
A different account name or checkout cannot establish exclusion of affected
state. The service and process checks cannot rule out an offline or remote worker.

**Fact/Source — tool identity.** The bootstrap pins Gradle 9.6.0 and its
distribution digest. The project pins AGP 9.4.0 and carries strict dependency
verification metadata. [Earlier installation checks](gate-0-installed-jdk-sdk-integrity.md)
and [diagnostic checks](gate-0-java-memory-diagnostic.md) cover specific
installations and executions. **Unknown:** authenticated OS, JDK, full SDK,
packager, verifier and complete dependency/cache correspondence on a fresh
worker. Package labels and a locally generated inventory cannot authenticate it.

**Runtime Observation — controls withheld.** No SDK copy, ACL change, alias
or write probe, backup restore, local build, signing or device operation ran.
**Unknown:** denial of content writes, creation, rename, deletion and metadata
changes by the actual build identity across every accessible path. Full
disposable-copy correspondence and separation of generated state are also
unverified. Any successful mutation of the protected fixture would falsify
enforcement. An unexamined alias or failed writable control would leave it
unknown. Neither endpoint hashes nor Android app permissions test Windows
access control. The [prior SDK experiment](gate-0-companion-source-controls.md)
already records the failed SDK-state assertion.

**Unknown — custody.** No verified restore from a separate encrypted backup
or agreed retention deadline, deletion owner and withdrawal procedure was
established for this attempt. Directory presence proves only their existence.

**Inference — next operation.** The owner must first designate one existing
candidate worker and explicitly authorize an offline, read-only inspection
of its provisioning record, intended Gradle identity, mounted inputs and cache
origins. Evidence of shared incident tools, keys or caches rejects that
candidate. Without such a worker the first unsigned build remains blocked.
Any later fixture probe and the build each require separate authority.
