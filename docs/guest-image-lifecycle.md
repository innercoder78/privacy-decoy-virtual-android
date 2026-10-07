# Guest-image lifecycle

PDVA intends one controlled Android 17 / API 37 guest-image line, normally
unrooted. No image, kernel, ROM, VM disk or guest build system is added. Arbitrary
ROM import, a ROM marketplace, community-image selection, other operating systems
and a version chooser are outside initial scope. Gate F is **Not reached**.

Before trusting or shipping an image, its release record must identify:

| Area | Required record and acceptance work |
|---|---|
| Source/build | Exact upstream sources, AOSP revision, kernel revision, patch set, build configuration, virtual devices, ABI, toolchain and dependency graph |
| Rights/provenance | Component and file-level origin, licenses, notices and redistribution rights; proprietary components separately authorized |
| Reproducibility/identity | Rebuild procedure, reproducibility limits, hashes, cryptographic identity and correspondence between source and shipped artifacts |
| Signing/authentication | Verification chain, key custody outside hostile guest/repository, signing ownership, revocation and compromise response |
| Updates/migration | Authenticated atomic update, supported migration paths, policy/Persona preservation and interrupted-update recovery |
| Rollback | Explicit allowed/disallowed versions and rollback protection; recovery cannot silently reintroduce vulnerable or incompatible state |
| Snapshots | Engine/image/config compatibility, integrity, state confidentiality, stale-token rejection and policy epoch reauthorization before restore |
| Corruption/recovery | Tampered/truncated storage tests, bounded recovery, honest failure, no uncontrolled host-data or network fallback |
| Maintenance | Named owner, vulnerability monitoring/response, security-update cadence, support period and end-of-support disposition |

Source and signatures alone do not prove escape resistance. Verification, update
parsers and snapshot readers are potential TCB components. No opaque binary may
be adopted merely to get a guest boot. [Source policy](source-provenance-policy.md)
applies before experiments; [Gate A](feasibility-gates.md) concerns full guest
functionality and [Gate B](security-boundaries.md) concerns enforcement separately.
