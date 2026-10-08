# Source-reference catalog

References are organized by technical role. They are not engine selections,
runtime dependencies or security endorsements. No third-party runtime or guest image is adopted. The repository-owned Gate 0
native probe and its build tools are scoped separately below. Retrieval/review date: **2026-10-07**.

| Role | Exact upstream / evidence identity | Current treatment |
|---|---|---|
| Platform VM APIs, guest configuration and Microdroid | AOSP platform/packages/modules/Virtualization; main `175a51b30123fa6b02b541f1969665708f7ec2c3`, Android 17 r1 `22f1c9ee92b146e10c8f5e71338618f77ab1631e` | Source/documentary references only; [immutable file ledger](evidence/gate-0-platform-authority.md) |
| Host access enforcement | AOSP platform/system/sepolicy; main `4571ddd9440721fec583c906a337de949a77749e`, Android 17 r1 `e066568e98d86db31a9346d30977f3632fa7073c` | Read-only policy evidence, no policy imported or modified |
| Platform lifecycle, memory and execution constraints | Official Android Developer/AOSP documents D1–D7 in [Gate 0](evidence/gate-0-platform-authority.md) | Live-document facts scoped by date; not candidate execution proof |
| Historical methods and negative findings | Privacy Decoy `5320b3b44b38df4b8f3361ecbcb530386ff195e9` | [Classified reference](reference/privacy-decoy-history/reuse-classification.md), no code/history imported |
| User-space CPU execution / machine model | QEMU/Podroid/QubeVM/Linxr/Limbo snapshots and alternatives in the [immutable research ledger](evidence/gate-0-userspace-vmm-sources.md) | QEMU/TCG is the lead hypothesis only; research pins are not dependency adoption or engine selection |
| Isolated-worker authority and optional native service | Android 17/current SELinux and release framework refs in the [research ledger](evidence/gate-0-userspace-vmm-sources.md) | Documentary support for the next experiment; no physical/JIT/containment result |
| Android virtual hardware and software rendering | Android 17 Cuttlefish exact files in the [research ledger](evidence/gate-0-userspace-vmm-sources.md) | Guest/device-model reference only, not an ordinary-app Gate 0 solution |
| Closed-source virtual Android products | [Black-box metadata and study plan](evidence/gate-0-black-box-comparisons.md) | Behavior/UX comparisons only; independent guest-kernel boundary Unknown |
| Image build/kernel/update tooling | No toolchain or guest component adopted | Exact source/license/reproducibility review required before future use |
| Foundation validator | Repository-owned Python standard-library script | No pip, npm, Gradle or Android dependency |
| CI source checkout | Official [actions/checkout](https://github.com/actions/checkout/tree/3d3c42e5aac5ba805825da76410c181273ba90b1), full commit `3d3c42e5aac5ba805825da76410c181273ba90b1`, tag v7.0.1 | Explicitly adopted solely for foundation CI as detailed below |

## Checkout action adoption record

The official GitHub API independently resolved `actions/checkout` tag `v7.0.1`
to commit `3d3c42e5aac5ba805825da76410c181273ba90b1`. Commit metadata reports
verified signing and the v7.0.1 preparation change. Inspected
[action metadata](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/action.yml)
uses Node 24 and upstream bundled `dist/index.js` for main/post execution;
the upstream [license](https://github.com/actions/checkout/blob/3d3c42e5aac5ba805825da76410c181273ba90b1/LICENSE)
is MIT. This review establishes identity and limited CI use, not a complete audit
of every transitive bundled component or reproducible upstream distribution.

The workflow explicitly adopts this official immutable action pin, with
`contents: read`, `persist-credentials: false`, `clean: false`, no secrets supplied,
no submodules/LFS, no runtime dependency and a five-minute job timeout. It uses
`pull_request`, not privileged `pull_request_target`. The workflow checks out the
exact PR head (or push SHA) and prints the tested commit. The hosted Ubuntu 24.04
runner provides Git/Python/Node infrastructure, whose image can change and must
be identified from job logs when diagnosing failures. No action code/binary is
vendored into PDVA or added to a product TCB. The repository maintainer owns pin
updates and review of upstream security changes before updating; no automatic
floating tag adoption is permitted.

The action pin was also observed in the historical workflow, but independently
re-verified rather than trusted by copying. Full runtime/component adoption in
future remains subject to the stricter [source policy](source-provenance-policy.md).

## Gate 0 research build adoption

The [isolated-worker adoption record](evidence/gate-0-isolated-worker-adoption.md)
explicitly scopes AGP/Gradle/JDK/SDK/NDK/CMake and the existing checkout action to
the pre-QEMU research harness. Its [transitive build inventory](evidence/gate-0-isolated-worker-dependencies.md)
and exact hashes distinguish build trust from the zero-Maven-dependency app.
This supersedes only the bootstrap absence of Android build tooling; it selects
no VM engine or guest component and changes no gate state.
