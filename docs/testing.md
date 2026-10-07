# Testing and validation

Functionality/compatibility and security/enforcement have separate results.
Booting Android, launching an app, successful graphics or a green harness does not
prove isolation. [Acceptance criteria](acceptance-evidence-criteria.md) govern all
claims. This bootstrap runs only foundation validation and no VM experiment.

| Future test family | Required approach |
|---|---|
| Guest functionality | Complete Android component/lifecycle, WebView, services and ordinary app behavior for the exact image; independently test without proprietary Google packages. |
| Escape and native containment | Host filesystem/properties, `/proc`, `/sys`, native code, direct syscalls, guest kernel compromise scenarios and hostile workloads; independently observe host sentinels. |
| Authority transfer | Binder reachability, shared memory, device passthrough, inherited/duplicated descriptors/handles, guest/host IPC and confused deputies. |
| Management | Malformed broker messages, caller/instance authorization, replay, stale tokens, revocation, cross-instance and management-state probes. |
| Network | Bypass, protocols/producers and VPN loss/change from [networking](networking.md); independent packet observation with positive controls, not just API return values. |
| Image/state | Image tampering, signing failure, downgrade, snapshot corruption, incompatible versions, interrupted migration/update and recovery. |
| Resource/lifecycle | CPU/memory/disk/IPC exhaustion, process death, restart, restoration, thermal/battery load and background restrictions without fail-open behavior. |
| UX/integration | Display/input/IME/audio, rotation, interruptions, accessibility, clipboard and file disclosure, safe escape and genuine-data revocation. |

Test matrices must identify host Android/build type/OEM/device/ABI, guest/engine
and dependency revisions, exact artifacts, policy and relevant external services.
Use synthetic fixtures, protected host sentinels and adversarial positive/negative
controls. An absent path or inconclusive observer is Unknown, not access denied.
Emulator and development tooling results remain research only. Strong production
isolation claims require stock non-rooted physical release-equivalent tests and
independent security review across the declared supported matrix.

Never put real private accounts, host identifiers, Persona secrets, credentials,
signing material or raw sensitive captures into public evidence. Redact before
upload and retain enough safe metadata to reproduce the conclusion.

## Foundation validation

Run `python .github/scripts/validate-foundation.py` at repository root and
`git diff --check`. The validator checks tracked and non-ignored new files so it
also works before staging. It verifies roots, local Markdown file targets,
bootstrap text/binary/signing hygiene, requirement definitions/numbering and
historical notices. It does not fetch external links, parse arbitrary Markdown,
validate every anchor, discover every secret, prove license compliance or assess
security claims. Human review must inspect every changed file and the exact-base
diff, modes, source/provenance, scope and assertions.

The lightweight workflow checks every PR so unexpected root files cannot evade
path filters. Future expensive Android/VM suites must be path-aware without hiding
unclassified changes. Check GitHub Status and actual job/step logs before labeling
failures: distinguish code defects from service, runner, billing/quota and zero-step
failures. Never weaken or rerun a check solely to obtain green status.
