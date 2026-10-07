# Feasibility gates

Gate 0 is **Unresolved**. Gates A–G are **Not reached**. No document, CI check,
source citation or owner direction is a technical gate pass.

## Gate 0 — ordinary-app execution authority

Can at least one candidate give an ordinary distributable third-party Android app
on supported stock non-rooted devices a credible, legitimately shippable mechanism
and authority for the complete interactive virtual Android environment, with a
defensible prospective guest/host boundary? "Android supports virtualization" is
not an answer.

Each candidate record must separately establish:

1. Production access class: ordinary installed app, preinstalled, privileged/system,
   platform-signed, development/test grant, shell/ADB, root, custom ROM, OEM/vendor,
   or another explicitly identified class.
2. Required API, Binder/service, permission, device node, binary, SELinux domain,
   kernel facility and helper authority.
3. Authority to configure the guest PDVA needs, not just a restricted workload VM.
4. Operation on production `user` builds without prohibited privileges or setup.
5. Host version, ABI, hardware, OEM and virtualization-feature dependencies.
6. Legitimate distribution/invocation, exact source, license, provenance,
   dependency/binary inventory and trusted computing base (TCB) implications.
7. Ordinary-app CPU/JIT/executable behavior, memory, lifetime/background, thermal,
   battery and storage constraints.
8. Evidence quality, exact negative findings, unsupported portions and Unknowns.

A pass needs reviewed evidence for a concrete allowed candidate and the smallest
falsifiable ordinary-app authority proof, with remaining Gate A/B questions stated.
No privileged demonstration can satisfy this gate. The
[candidate record](evidence/gate-0-platform-authority.md) has scoped negatives for
restricted platform paths. [Follow-up research](evidence/gate-0-userspace-vmm-sources.md)
makes QEMU/TCG a credible lead hypothesis, with [a defined isolated-worker experiment](evidence/gate-0-isolated-qemu-proof.md),
but execution and containment remain Unknown. A tiny Linux boot cannot pass Gate 0;
the complete interactive guest path and defensible prospective boundary remain
review obligations. Overall failure
would require evidence closing the viable alternatives, not only AVF exclusion.

## Subsequent gates

| Gate | Required result | Minimum falsification/acceptance evidence | Current state |
|---|---|---|---|
| A — complete Android 17 guest | SystemServer, Zygote, Activities, package manager, launcher/System UI, normal lifecycle, WebView, graphics, input, audio, storage, networking and guest services | Exact reproducible guest build and component/lifecycle observations; headless Microdroid or a Linux shell does not qualify. Core guest work must run without proprietary Google software. | Not reached |
| B — security boundary | Actual authority containing hostile guest and guest-native code, TCB and every guest/host interface | Authority inventory, escape/native/syscall/host-data probes, malformed interface and revocation tests, independent review before production claims | Not reached |
| C — interactive usability | Useful display/graphics, touch, IME, audio, storage, rotation, full-screen behavior, safe escape, suspend/resume and recovery | Startup/latency/resource budgets declared before tests; host interruptions, process death, performance, thermals, battery and resource pressure on devices | Not reached |
| D — networking | Required host route and external VPN behavior, safe change/loss handling, no silent physical fallback | Producer attribution and independent packets across all declared protocols, lifecycle and VPN policies; include leak-positive controls | Not reached |
| E — Google Play | Defensible account, Play Store, genuine Play installation/update model | Separate technical behavior, rights, user-local acquisition, certification and integrity results; honest incompatible-app outcomes | Not reached |
| F — image lifecycle | Source/build identity, signing, updates, migration, rollback, snapshots, recovery and maintenance | Reproducible artifacts, tamper/rollback/corruption tests, vulnerability response and named maintenance owner | Not reached |
| G — physical-device matrix | Declared stock non-rooted device/OEM/ABI/hardware scope for release | Release-equivalent virtualization, graphics, lifecycle, networking and performance evidence; production claims require independent security review | Not reached |

Gate 0 precedes Gate A implementation. Subsequent work is authorized only as the
preceding foundational evidence permits, with dependencies recorded in its
proposal. Gate A boot success does not authorize a security claim. Supply-chain
review applies before any experiment adopts code or artifacts even though complete
image-lifecycle qualification is Gate F. Physical evidence may expose a failure
early; it is not postponed merely because Gate G is listed last.

A failed foundational gate requires **STOP**, explicit owner-approved **NARROW**,
or owner-approved **REDESIGN** through an ADR. Record excluded capabilities and
invalidate affected evidence. Never weaken a boundary to keep the roadmap moving.
