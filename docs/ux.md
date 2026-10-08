# Intended virtual-phone experience

The intended experience is "switch into my private virtual phone": an immersive
interactive guest with a clear reliable route back to PDVA management. This is a
research target, not a working feature or protection promise. Ordinary app
authority does not replace the host OS or allow complete suppression/control of
host System UI.

| Research area | Required question |
|---|---|
| Edge-to-edge, immersive view and host system bars | Which presentation is permitted, and how do host gestures/bars remain accessible? |
| Touch/input forwarding and gestures | Are coordinate transforms, focus, multi-touch and gesture ownership correct without host input leakage? |
| IME | Which keyboard handles input, what crosses the guest boundary and how is disclosure communicated? |
| Display sizing/density and rotation | Can guest layout adapt without false device-descriptor/capability claims? |
| Accessibility | Can management and escape remain usable while guest accessibility cannot silently obtain host authority? |
| Safe escape | Can users always return to identifiable PDVA management, including a hung or spoofing guest? |
| Suspend/resume and interruptions | What happens to input, audio, sensors, networking and capabilities on calls, lock screen or focus loss? |
| Multitasking/PiP | Which modes are supported, and what privacy and resource changes are visible? |
| Process death/background limits | Can state be stopped and restored without policy reset, stale credentials or uncontrolled fallback? |
| Restoration | Are image/snapshot integrity, Persona coherence and route policy checked before re-entry? |
| Interactive quality | Measure startup, latency, graphics/audio, storage, memory, thermals and battery against declared budgets on physical devices. |

Clearly distinguish management policy from guest Android permissions. Real
disclosure must be explicit, scoped and visible. Display Unsupported/Unknown
honestly; do not imply a secure session from a boot animation. Guest failures must
return to a safe management state with bounded recovery. Gate C is **Not reached**.

The [proposed provisioning and update states](environment-delivery-and-updates.md#proposed-management-ux)
cover missing environments, downloads, verification, compatible updates, app
prerequisites and recovery. They belong to PDVA management and remain a design
proposal under **PROPOSED** ADR-0002, pending Tony's approval; no UI is implemented.
