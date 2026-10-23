# Keystore-to-U-Boot handoff: recovered candidate STOP

Review: **2026-10-23, America/Fortaleza; source-only Windows review.**
[REC-01 provenance and disposition](gate-0-research-recovery.md) applies.
Scope: PDVA-REQ-002–003, 009–015, 034–043 and 054. **Gate 0 Unresolved;
Gates A–G Not reached.** No keys, firmware or Android operations were executed.

**Question:** can protected management state plus messages to guest U-Boot supply
release-trust enforcement when the native worker and its emulated CPU/RAM are
hostile? **STOP this candidate as established by the available evidence.** This
is not universal impossibility of ordinary-app mechanisms or Keystore use.

The [merged firmware baseline](gate-0-android17-uboot.md) and
[ledger](gate-0-android17-uboot-sources.md) already record test keys, fresh unlocked
OEM-lock state and the non-OP-TEE zero-read/no-op-write AVB rollback callbacks.
This recovery adds the following distinctions, rather than repeating that survey.

## Independently checked source, not hardware qualification

1. The public [setMaxUsageCount API](https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder#setMaxUsageCount(int))
   is available since API 31. It limits private/secret-key operations, with
   exhaustion invalidation. Hardware capability varies, including software
   enforcement and hardware support restricted to single use. This is a live API
   reference checked on the review date, not an immutable device specification.
2. At frameworks/base `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`,
   [KeyGenParameterSpec.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/keystore/java/android/security/keystore/KeyGenParameterSpec.java)
   documents that behavior. [KeyProtection.java](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/keystore/java/android/security/keystore/KeyProtection.java)
   marks `setRollbackResistant` hidden and describes permanent key deletion;
   limited capacity is reserved for critical system keys. The Java `public`
   modifier does not establish ordinary public-SDK availability. This review
   does not claim to have tested an access-control rejection on a device.
3. KeyMint [Tag.aidl](https://android.googlesource.com/platform/hardware/interfaces/+/0162af698935100a590b7359581ac8b1b80693e5/security/keymint/aidl/android/hardware/security/keymint/Tag.aidl)
   at `0162af698935100a590b7359581ac8b1b80693e5` separately specifies
   `ROLLBACK_RESISTANCE` for deletion and `USAGE_COUNT_LIMIT` with its enforcement
   security level. At this pin, counts above one are described as not expected
   to have TEE enforcement; single use can also fall back to Keystore enforcement.
   This source contract is not measured capability of an installed device.
4. At U-Boot `3fe9647575890b846172e546201eff7614c8cb59`, freshly retrieved
   [avb_verify.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/common/avb_verify.c)
   and [android_bootloader_transport.c](https://android.googlesource.com/platform/external/u-boot/+/3fe9647575890b846172e546201eff7614c8cb59/boot/android_bootloader_transport.c)
   match the earlier public ledger's decoded-byte hashes. The transport validates
   console operations, transfer lengths and expected command/response/size header;
   that code does not establish cryptographically fresh responder identity.

Procedure: retrieve exact Gitiles files using `?format=TEXT`, base64-decode,
inspect the named declarations/functions and compare the two U-Boot hashes with
the merged ledger. An initial web view of KeyProtection was inaccessible; direct
pinned text retrieval succeeded. No source code was imported into the product.
Source configuration and API comments do not establish hardware availability,
source-to-device correspondence or crash/rollback behavior.

## Architectural inference and reopening condition

**Inference:** a key-use budget and permanent key deletion do not themselves
implement arbitrary named non-rollbackable AVB indices, durable lock state, or
an atomic update/boot/crash/recovery transaction. A proposed construction must
show those additional properties rather than rename the key counter.

Even if trusted management signs or verifies every message, a hostile worker
controlling guest CPU execution and RAM may bypass guest firmware checks. This
is an architectural inference from the stated threat model, **not an observed
exploit**. Keeping management/Persona master/keys/signing/policy and other guest
resources outside the worker remains necessary; it does not certify faithful
guest execution. Independent policy admission, fail-closed Unknown, descriptor,
mapping, copied-data and post-compromise revocation limits still apply.

**Missing:** an ordinary-app-accessible independent execution enforcer, trusted
state continuity, secure update/restore transactions and safe post-compromise
revocation. A remote freshness service is an **unselected hypothesis** with its
own enforcement, privacy, connectivity and recovery obligations.

The smallest falsifier of this STOP is a concrete source-backed independent
authority outside the worker, legitimately reachable by a normal installed app,
which enforces a fresh boot decision and crash/rollback-safe state transitions.
An authenticated response that the compromised CPU can ignore fails this test.
No prohibited privilege, guest secure-world label or general Keystore survey
closes it. Material boot-trust redesign still requires a separate ADR and
explicit owner approval. No replacement design is accepted here.
