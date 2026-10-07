# Platform support

| Dimension | Current disposition |
|---|---|
| Guest baseline | Android 17 / API 37, selected initial target; no image or successful boot |
| Guest line | One controlled supported image line intended; normal guest unrooted |
| Host minimum Android version | **Unknown** until Gate 0 and candidate evidence determine it |
| Host installation | Ordinary distributable user-installed third-party app on stock non-rooted production `user` builds |
| Supported devices/OEMs | **None claimed yet** |
| ABI | ARM64 must be investigated for physical product feasibility; no ABI supported yet |
| Hardware/virtualization features | Candidate-dependent and Unknown; presence of AVF/pKVM is not application authority |
| Distribution | Legitimate packaging/invocation and dependency rights require review; no production package exists |

Normal operation excludes root, Magisk, Xposed, LSPosed, custom ROMs, patched host
kernels, privileged/system installation, platform signing, production ADB,
userdebug/eng builds and OEM-only integration. A guest target does not imply an
equal host minimum or expose hidden APIs.

Emulator, Cuttlefish, userdebug, root, shell grants and development experiments
are research evidence only. Every future supported matrix row must name host
Android/API/build, OEM/model, ABI, RAM, kernel/SELinux and virtualization features,
guest/image/engine revision, release equivalence and evidence date. Graphics,
lifecycle, networking and performance may differ independently. Revalidate after
material updates; an untested device or OEM remains Unknown.

[Gate 0 evidence](evidence/gate-0-platform-authority.md) independently checked
Android 17/API 37 and app memory-limit documentation as well as exact AOSP main
and Android 17 release refs. No physical device was tested in this bootstrap.
