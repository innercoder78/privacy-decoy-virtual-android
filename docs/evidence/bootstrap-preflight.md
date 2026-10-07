# Bootstrap repository preflight

**Observation date: 2026-10-07. Evidence type: repository observation.**
Performed in Codex Desktop local mode before editing PDVA. Public-safe metadata
only; no confidential checkout paths or credentials are recorded.

| Check | Observed starting state |
|---|---|
| Canonical PDVA repository | innercoder78/privacy-decoy-virtual-android; origin fetch/push both its GitHub HTTPS Git URL |
| Local HEAD / branch | `a92bcbd02bc7b37d33d04ef3023118e701bc411e`, `main` tracking origin/main |
| Worktree / stashes | Clean; one existing main worktree; no stashes |
| Local / live remote branches | Only main; no bootstrap or overlapping foundation branch |
| Live PDVA main | `a92bcbd02bc7b37d33d04ef3023118e701bc411e`, unchanged from supplied expectation |
| PDVA open PRs | None; head/base/diff/review/comment/thread inspection therefore not applicable |
| Structure / dependencies | Only `.gitignore` and minimal `README.md`; no dependency declarations/build system/workflow |
| Tracked files / modes | Two regular text files, mode 100644; no tracked binaries, images, packages, signing material or dependency inventory |
| PDVA workflows / exact-main status | Zero workflows, zero check runs, zero commit status contexts. API aggregate `pending` with zero contexts is not a running check. |
| Live historical main | `5320b3b44b38df4b8f3361ecbcb530386ff195e9`, unchanged from supplied expectation; suspension merge of PR #39 |
| Historical open PRs | None |
| Historical local state | Clean, existing `docs/suspend-privacy-decoy` branch at `38ab23fce8e88b66c974afd31f0d33a77c1685d4`; differs from live main |
| Historical authority retrieval | Authoritative commit already existed as a local object; read-only `git show` / `ls-tree` with optional locking disabled and per-command safe-directory override. No fetch, checkout, index/config update or other mutation. |
| GitHub Status | Summary reported All Systems Operational, including Actions, Git Operations and API; no active incident in retrieved summary (updated 2026-10-07T02:49:31.371Z). This is a point-in-time observation. |

The live repository/API state, not supplied expectations, established the branch
base. The bootstrap branch is `docs/bootstrap-foundation`, created from the exact
verified PDVA main above. Initial sandbox networking restrictions were resolved
using authorized read-only queries; they were not interpreted as GitHub downtime.

Historical material is indexed at [its exact source commit](../reference/privacy-decoy-history/README.md).
Platform research is separately recorded in [Gate 0](gate-0-platform-authority.md).
The only bootstrap external execution dependency is the reviewed official
checkout action; see [catalog](../source-reference-catalog.md). No Android runtime,
engine, guest image or product dependency is added. These repository observations
do not establish feasibility or production isolation.
