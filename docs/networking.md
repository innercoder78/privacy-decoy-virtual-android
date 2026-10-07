# Networking contract

PDVA MUST NOT occupy the host Android VPN slot or implement a production host-side
`VpnService` unless a later explicit owner-approved ADR changes that requirement.
No production backend is selected or implemented.

```text
guest app → guest Android networking → PDVA guest/host network backend
          → host Android networking → active external host VPN when applicable
          → Internet
```

This is the desired conceptual route, not an observed path. The backend's actual
socket producer, UID/process, Binder/helpers, DNS handling and host routing
authority must be identified before claiming external-VPN coverage. VPN presence,
an icon or a default-network callback cannot by itself establish route enforcement.

Do not intentionally bind guest traffic to an underlying/physical network to
bypass a required VPN. When policy requires an external VPN and the route cannot
be established or verified, block traffic rather than silently fall back to
physical egress. Loss, reconnect, provider replacement, split/excluded routes,
queued packets and stale handles need independent evidence; an application-level
timeout does not prove that no packet escaped. How to enforce this under the
ordinary-app contract is **Unknown**.

| Evidence axis | Required coverage before a scoped claim |
|---|---|
| Producers | Guest apps, guest system services, Java/native code, WebView, background and secondary processes, every backend/helper |
| Protocols | Java TCP, native TCP, UDP, DNS including resolver behavior, IPv4, IPv6, QUIC/Cronet |
| Lifecycle | Start, resume, death, reconnect, pending I/O, VPN provider change and VPN loss |
| Route/policy | VPN required/not required, full/split/excluded traffic, denied route, verified external lockdown where relevant; no assumed universal provider behavior |
| Independent observation | Controlled endpoints, packet captures at relevant routes, positive egress controls, producer/session attribution and bounded redacted logs |

A guest VPN app may eventually run inside guest Android, but that is distinct
from the host-VPN inheritance objective. Persona network metadata and geography
do not imply public-IP/geography control. No universal network anonymity claim is
authorized.

The [historical VPN-loss result](reference/privacy-decoy-history/negative-findings.md)
motivates generalized packet evidence and no-silent-fallback discipline. Its
particular broker and test `VpnService` are not PDVA architecture. Gate D remains
**Not reached**; see [testing](testing.md).
