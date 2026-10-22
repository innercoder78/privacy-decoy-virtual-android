# Backend endpoint source ledger

Companion to the [configuration result](gate-0-backend-endpoints.md).
Review: **2026-10-22, America/Fortaleza; Windows x86_64**. Source inspection only;
Gate 0 **Unresolved**, Gates A–G **Not reached**.

## Preflight and scope

Canonical `git fetch origin main` retrieved
`cf828c2107012fbe305fc27364c3863a4135f1cc`, matching the supplied baseline.
Live PR #30 metadata confirms that merge, head
`1d724a957cfa4dd710cc18a9e451f90c4c6ca791` and base
`b25ebeae0b8e0db06903f65a3e5831b765459191`. The initial checkout at that head
has the same tree as live main. Repository-scoped live open-PR search returned
zero entries: no open head/base, complete diff/files, jobs/logs, reviews, comments
or unresolved threads needed reconciliation. No exact-main hosted CI success is
claimed. Existing workflow definitions, checkout pins, permissions, path filters,
build configuration and dependency inventory were inspected.

[GitHub Status](https://www.githubstatus.com/api/v2/summary.json) reported core
Git/PR/Actions services operational and an active minor Projects update-delay
incident. This is not a code/CI failure. Initial sandbox fetch/network access
failed; approved fetch and text retrieval succeeded. A web-view source retrieval
failed, then direct Gitiles retrieval obtained the immutable text. Failure alone
was not used as source evidence.

Initial tracked tree was clean; one worktree, no stashes. Existing branches and
ignored source/build/Gradle/native assets were inventoried and preserved. No
applicable AGENTS.md was found. Research starts on one new branch at verified
main. Historical repository was untouched. A private ignored journal records
intent, outcomes, falsifiers and safe continuation; no private artifact is uploaded.

Governing inputs: both ADRs, requirements, feasibility gates, security boundaries,
roadmap, governance, source-reference catalog and provenance policy. Evidence:
PR #30 assessment/ledger, boot/HAL assessment/ledger, QEMU worker integration,
seccomp, dormant bootstrap, containment, capability revocation, Android lifetime
and lifecycle exceptions. Older fixture/build observations retain their original
scope. No backend compiler or installed-device result is inherited from them.

## Immutable source identities

V = `platform/external/rust/crates/vhost-device-vsock`
`28233ae213b24a9a35f25e9e49bcadee2bf93821`.
D = `platform/external/rust/android-crates-io`
`1f5e95cd6e996995023c9c0f7df0f15a8a43269e`.
Q = `qemu/qemu` `4fc49f46dc95d4a27de2509e7fceb2931e91faeb`.
S = `platform/system/sepolicy` `e066568e98d86db31a9346d30977f3632fa7073c`.

V/D/S build files, main/thread/connection/mapping handlers and policy sources
retain the exact URLs and hashes in the
[PR #30 ledger](gate-0-userspace-communication-sources.md). All 65 retained receipt
rows, including directory metadata and repeated retrievals, were rehashed with
zero mismatches. This is not 65 distinct code files. An initial receipt-path
resolution error affected three QEMU entries; correcting the path handling
verified their bytes, rather than changing expected hashes.

Additional inspected sources and reused D3:

| ID / immutable source | SHA-256 of source bytes |
|---|---|
| [D1: vhost connection.rs](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost/src/vhost_user/connection.rs) | `efdd022c5611caf0b1597405756cf0e049a6ddb0c92fe8aeaca96c87255c25e2` |
| [D2: backend_req_handler.rs](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost/src/vhost_user/backend_req_handler.rs) | `8937fe26018b9589030efa816ffaea38550efa5c4b1a79e7545423058f3c8de6` |
| [D3: vhost-user-backend lib.rs](https://android.googlesource.com/platform/external/rust/android-crates-io/+/1f5e95cd6e996995023c9c0f7df0f15a8a43269e/crates/vhost-user-backend/src/lib.rs) | `d289603d79044227dd9b9d2c6302372126498b1c5c149ac0e808ffa96b1244b0` |
| [V: rxops.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/rxops.rs) | `4b4aa23a1b58ee1394a78c93ccb58992f92364f8ff75bac930a1e2e2a0112e6f` |
| [V: rxqueue.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/rxqueue.rs) | `c1c5a0817368f48d71d2cacee44220019faf96288053d7652d675d89b90eb42d` |
| [V: txbuf.rs](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/src/txbuf.rs) | `59d8cddc3841b0037324be66b484f3be2650e719f06174609411cad25581a111` |
| [V: LICENSE](https://android.googlesource.com/platform/external/rust/crates/vhost-device-vsock/+/28233ae213b24a9a35f25e9e49bcadee2bf93821/LICENSE) | `670c701c040324ddfe29f5c1cf746c4efacea614b71ab25089a320f5b0c4b098` |
| [Q1: chardev/char-socket.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/chardev/char-socket.c) | `fa414b863afc85192e7eda2206e9e0cbce0822d608ddae9560e0e0528e8f7236` |
| [Q2: util/qemu-sockets.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/qemu-sockets.c) | `55c0f53465b7ad0875941faaf5e3b5f8633f2ee32672a8a23cf271340d63271b` |
| [Q3: io/channel-socket.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/io/channel-socket.c) | `24b67f6b8092a34befdbb50133fee9c41cfb6f8e3137aeb7f070272a76111bbf` |
| [Q4: chardev/char-fe.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/chardev/char-fe.c) | `47d98ed0c25f342388cc276dcacbda4faeb9ea7a573c3f07b7bc75081be16b0b` |
| [Q5: backends/hostmem-memfd.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/backends/hostmem-memfd.c) | `76e5c64a8b191d2d73bdadcc310836426b8539571b0237ed16f620216233860f` |
| [Q6: util/memfd.c](https://github.com/qemu/qemu/blob/4fc49f46dc95d4a27de2509e7fceb2931e91faeb/util/memfd.c) | `0e1e5d0f022727c39cebc651789601334e233b585fef490f84283fde72001c67` |

Gitiles TEXT was base64-decoded to bytes. Q's retained checkout is clean at the
exact pin; all six listed files matched `git show <pin>:<path>` after local CRLF
normalization. The hashes above are the immutable Git blob bytes. No upstream
implementation or executable is copied into tracked PDVA files.

## Reproduction, rights and limits

1. Verify V Android.bp/Cargo.toml and D's three Soong modules; keep host-only
   target types and different Cargo/release versions visible. Do not infer an
   Android compiler invocation or resolved transitive graph from these declarations.
2. Trace V main → start_backend_servers → start_backend_server → backend/thread
   constructor. Inspect the complete constructor and guest request handler, not
   only text matches. There is no FD selector in the supplied configuration.
3. Compare D1 owned listener constructor with D2 connected stream constructor and
   D3's public/private fields and methods. Confirm ownership, socket state and
   pathname cleanup differ; these are not interchangeable arguments.
4. Trace Q1 FD parsing/validation → Q2 socket_get_fd/socket_connect → Q3
   getsockname/QIO feature → Q1 tcp_chr_set_msgfds → Q4 dispatch; compare with
   the separate chardev feature advertisement. Inspect the vhost-user write path.
5. Trace Q5/Q6 exact memfd flags/seals, then D set_mem_table/mmap and V queue
   retention. A memory-region range is not an object-level access restriction.
6. Compare S appdomain connected-socket/Binder rules with isolated received-file
   and direct-open restrictions. Do not promote a source allow into a complete
   installed SELinux/DAC or independent cleanup result.

V inspected modules declare Apache-2.0 OR BSD-3-Clause; retrieved LICENSE is
Apache-2.0 and generated Soong metadata selects Apache-2.0. D1/D2 carry Apache-2.0
SPDX headers; D's generated modules identify Apache-2.0. Q retains per-file terms
and the previously recorded GPL/composition obligations; Q6 has a permissive
notice. Source reading is not adoption or a complete redistribution review.
All transitive licenses, corresponding build inputs, vulnerability/maintenance
ownership and distribution approval remain unclosed. No opaque binary, guest
image, new toolchain, workflow, runtime dependency or permission is added.

The existing NDK r28c and Python are available for repository checks, but no
reviewed Rust compiler/Android std or full Soong workspace was located in the
inspected toolchain; Rust tools were absent from PATH and conventional user
toolchain locations. No installation or substitute Cargo build was attempted.
No real backend test was created; manual negative controls in the assessment
are source reasoning and are not labeled executed synthetic/runtime tests.

Validation: foundation passed (122 files, 71 Markdown files, 54 requirements,
two ADRs); harness manifest/source authority validation passed. Repository
regression suite completed 141 tests: **137 passed, four existing Windows skips**.
Skips are not execution evidence. Source receipts and six QEMU blob comparisons
passed as described above. Whitespace, local Markdown targets, text-only scope,
file modes and public-data hygiene were reviewed. No Android rebuild, backend
compile, Linux native test or installed-device execution was performed.

Hosted CI for a new PR remains **pending/unobserved**; publication stops after
one immediate identity and native chat-attachment verification.
