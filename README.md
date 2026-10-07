# Privacy Decoy Virtual Android (PDVA)

PDVA investigates a complete interactive virtual Android phone presented from an
ordinary Android application. The initial guest target is **Android 17 / API 37**,
with one controlled guest-image line and an unrooted normal guest. Normal host
operation must work on supported stock, non-rooted Android without system
privileges, platform signing, OEM integration, or production ADB.

**Foundation only. Gate 0: Unresolved.** No VM engine is selected, no VM or Android
runtime is implemented, and no guest image is included. Full interactive Android
feasibility and the actual enforcing guest/host security boundary are unproven.
No devices are claimed supported. Documentation does not pass a feasibility gate.

The first question is whether an ordinary distributable third-party app can
obtain a credible, legitimately shippable execution mechanism for the required
guest. The [Gate 0 evidence](docs/evidence/gate-0-platform-authority.md) records
scoped negative findings for restricted Android virtualization paths while
leaving pure user-space emulation and other legitimate mechanisms Unknown.

Google account sign-in, Play Store installation and supported updates inside the
guest are [compatibility objectives](docs/google-compatibility.md), not established
capabilities. PDVA does not implement a production host-side `VpnService` or occupy
the host VPN slot under the current contract. Inheritance of an external host
VPN's route requires independent [networking evidence](docs/networking.md).

PDVA is a new product lineage, not Phase III of
[Privacy Decoy](https://github.com/innercoder78/Privacy-Decoy).
The predecessor is [historical reference only](docs/reference/privacy-decoy-history/README.md);
its findings neither prove nor disprove PDVA's full-guest direction.

## Canonical reading map

| Subject | Canonical record |
|---|---|
| Product obligations and change authority | [Requirements](docs/requirements.md), [governance](docs/governance.md) |
| Accepted direction, without engine selection | [ADR-0001](docs/decisions/ADR-0001-full-interactive-virtual-android-direction.md) |
| Research progression and STOP outcomes | [Feasibility gates](docs/feasibility-gates.md), [roadmap](docs/roadmap.md) |
| Evidence and claim discipline | [Acceptance criteria](docs/acceptance-evidence-criteria.md), [evidence index](docs/evidence/README.md) |
| Conceptual system and enforcing authorities | [Architecture](docs/architecture.md), [security boundaries](docs/security-boundaries.md), [threat model](docs/threat-model.md) |
| Policy, platform and experience | [Persona/privacy](docs/persona-privacy-policy.md), [platform support](docs/platform-support.md), [UX](docs/ux.md) |
| Guest distribution and maintenance | [Guest-image lifecycle](docs/guest-image-lifecycle.md), [source/provenance policy](docs/source-provenance-policy.md), [reference catalog](docs/source-reference-catalog.md) |
| Validation and contributions | [Testing](docs/testing.md), [contributing](.github/CONTRIBUTING.md), [Android scope](android/README.md) |

Run `python .github/scripts/validate-foundation.py` for repository foundation
checks. This standard-library check does not build Android, run a VM, or prove
security. Next technical work remains Gate 0 research.
