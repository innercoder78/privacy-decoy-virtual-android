# Security-boundary inventory

All rows describe required properties. **No PDVA boundary is implemented or proven.**
Candidate authorities are hypotheses, not selected mechanisms or grants. Current
evidence for each row is **none for PDVA runtime**; the source evidence at Gate 0
only constrains access to platform mechanisms. A proposed authority must first be
available under the ordinary-app contract and then demonstrate enforcement.

| Surface | Required property | Candidate enforcing authority | Current evidence | Current state | Open question | Gate |
|---|---|---|---|---|---|---|
| Guest memory | Guest cannot read/write host or peer memory | Hypervisor or validated emulator plus host process sandbox | No PDVA runtime | Unknown | What contains hostile instructions and emulator faults? | 0, B |
| Host filesystem | No ambient host/management file access | Host kernel/SELinux, bounded storage bridge | No PDVA runtime | Unknown | Which paths/handles exist at guest start? | B |
| Process isolation | Guest processes cannot acquire host identities or peers | Guest execution model, host process/UID boundary | No PDVA runtime | Unknown | Where do guest threads and subprocesses execute? | B |
| Guest-native code | Native guest code stays behind the same boundary | CPU execution mechanism and device model | No PDVA runtime | Unknown | Can native or generated code escape translation? | B |
| Syscalls | Guest syscalls never become unrestricted host calls | Guest kernel, emulator/hypervisor, host sandbox | No PDVA runtime | Unknown | What owns syscall interpretation? | B |
| Host kernel/devices | Minimal enumerated host attack surface | Kernel/SELinux, device model | Gate 0 excludes direct ordinary-app KVM in inspected policy | Unknown for PDVA boundary | Which host ioctls/drivers remain reachable? | 0, B |
| Binder/services | No arbitrary genuine host service authority | Explicit bridge authorization, host process isolation | No PDVA runtime | Unknown | Can a cached or supplied Binder object bypass policy? | B |
| Shared memory | No cross-instance/management disclosure or mutation | Kernel mappings, copy/ownership protocol | No PDVA runtime | Unknown | Are bounds, ownership and revocation enforceable? | B |
| File descriptors/handles | No inherited or transferred excess authority | Supervisor, kernel, bridge capability checks | No PDVA runtime | Unknown | Can duplicates survive close/restart/revocation? | B |
| Virtual devices | Malformed guest traffic cannot escape | Device model parsing and process sandbox | No PDVA runtime | Unknown | Which emulated devices and passthrough are necessary? | B |
| Management channel | Guest cannot issue owner commands or forge instance identity | Authenticated, authorized, replay-resistant control plane | No PDVA runtime | Unknown | What authenticates callers and epochs? | B |
| Management/Persona/secrets/peers | State outside hostile guest authority | Separate host authority, least-privilege storage | No PDVA runtime | Unknown | Does compromise of the VM process expose master state? | B |
| Network | Only policy-approved route; no silent physical fallback | Network backend and verifiable host route enforcement | Historical failures are not PDVA evidence | Unknown | How can ordinary-app code prevent VPN-loss races? | D |
| Image integrity/update | Authenticate approved image and updates | Cryptographic verification, protected keys, rollback policy | No image or verifier | Unknown | What authenticates boot components and patch state? | F |
| Snapshot state | Restore coherent authenticated state with fresh capabilities | Snapshot format, verifier and policy epochs | No snapshot implementation | Unknown | How are stale credentials and rollback rejected? | B, F |
| Escape resistance | Host remains protected after hostile guest compromise | Complete TCB and independent adversarial review | No PDVA runtime | Unknown | Are all device and bridge paths closed? | B, G |
| Resource exhaustion | Bound CPU/memory/disk/IPC; fail safely | Host limits, supervisor, bridge quotas | Android 17 memory-limit documentation only | Unknown | Can exhaustion induce leak/fail-open recovery? | B, C |
| Display/input | Bounded frames/events, reliable management escape | Graphics/input bridge and ordinary host UI authority | No PDVA runtime | Unknown | Can guest spoof management or capture host input? | B, C |
| Audio | No implicit host microphone authority | Explicit audio bridge/policy | No PDVA runtime | Unknown | Separate playback, capture and lifecycle revocation? | B, C |
| Clipboard | No ambient host clipboard sharing | Explicit directional copy and policy | No PDVA runtime | Unknown | How are unsolicited requests and retained data handled? | B |
| Camera | Only explicit scoped Real or deliberate other mode | Camera bridge, host permission plus PDVA policy | No PDVA runtime | Unknown | What survives revocation or backgrounding? | B |
| Microphone | No recording without controlled disclosure | Capture bridge and revocation | No PDVA runtime | Unknown | Can guest-native code bypass the bridge? | B |
| Sensors/location | Coherent policy data, never host-GPS fallback | Virtual-device/Persona policy | No PDVA runtime | Unknown | Which timing/native/SDK paths reveal genuine state? | B |
| Notifications | Minimized authenticated host presentation | Notification bridge, owner policy | No PDVA runtime | Unknown | Can content/actions impersonate management? | B, C |
| File sharing | Only deliberately selected files/capabilities | Scoped file bridge | No PDVA runtime | Unknown | Can path traversal or URI grants expand scope? | B |
| Storage sharing | No implicit host mount or peer disk access | Virtual block/filesystem model, host sandbox | No PDVA runtime | Unknown | Which mappings exist and how are they revoked? | B, F |
| Other integration | Default absence until explicit review | Appropriate host authority and narrow bridge | No PDVA runtime | Unknown | Accounts, accessibility, IME, autofill, USB/radios and future APIs? | B, C |

No row inherits evidence from guest boot, app compatibility, a VM label or the
predecessor's app mediation results. See [testing](testing.md) for falsification
work and [requirements](requirements.md) for obligations.
