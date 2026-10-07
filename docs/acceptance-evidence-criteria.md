# Acceptance and evidence criteria

Requirements are obligations, not implementation evidence. Each claim must link
to a reproducible record and its exact supported scope. Do not use an aggregate
privacy or safety score.

| Evidence term | Meaning and limit |
|---|---|
| Verified platform fact | Officially specified platform behavior independently checked against an authoritative source; scope it by version and access class. It is not a test of every OEM. |
| Repository observation | What an exact repository commit or live metadata query contains; no runtime result implied. |
| Source-code observation | A behavior or restriction visible in identified source; build configuration and runtime applicability remain separate. |
| Direct observation | A measured event in an identified experiment, with artifacts, controls and environment. |
| Upstream claim | A statement made by an upstream project; not independently established PDVA behavior. |
| Inference | Reasoned conclusion from cited facts; state the reasoning and its limits. |
| Hypothesis | Falsifiable proposition awaiting evidence. |
| Assumption | Explicit precondition temporarily used in analysis; identify consequences if false. |
| Unknown | Missing, inaccessible, insufficient or conflicting evidence; never a success default. |
| Unsupported | Intentional product disposition supported by evidence or policy, with an explicit scope; not a synonym for Unknown. |

Gate states are separate: **Unresolved**, **Passed for exact scope**, **Failed for
exact scope**, and **Not reached**. A candidate's scoped negative result is not
automatically the whole gate's failure. A passing test harness may correctly
report a failed architectural hypothesis.

Every evidence record must include date, question, requirement/gate, source and
immutable ref or tested artifact hash, procedure, environment, build type,
host/device and OEM where relevant, ABI, expected falsifier, actual observation,
positive/negative controls, evidence type, limitations, supported conclusion and
excluded conclusions. Record source retrieval failures and conflicting versions.
Preserve negative findings and mark later corrections explicitly.

Compatibility success is not security success. Guest boot or app launch proves
only that event. Failure to observe a leak does not prove containment. Static
absence does not prove safety. A benchmark without provenance or independent
observation cannot support a boundary claim. Documentation never passes a gate.

Before strong production isolation claims, require stock non-rooted physical
devices, release-equivalent builds, the declared OEM/ABI/version matrix, adversarial
and failure evidence, reproducible supply-chain identity, and independent security
review. Research emulators, Cuttlefish, root and userdebug evidence retain their
research labels. A changed engine, image, host policy, bridge or dependency
invalidates affected conclusions until revalidated.

Use synthetic accounts/data and redacted, bounded evidence. Public evidence must
contain no real private accounts, host identifiers, Persona secrets, credentials,
signing keys, sensitive raw captures or confidential local paths. Review all
artifacts and logs before publication. See [testing](testing.md) and
[gate definitions](feasibility-gates.md).
