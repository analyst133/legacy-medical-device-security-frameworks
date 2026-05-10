# Pattern C MFA Shim — Design

This document describes the security design of the inline service-port MFA shim. It is intended for designers building production hardware following this pattern, and for security reviewers evaluating the design.

## Design goals

The shim addresses the **physical-attacker** threat surface on legacy medical devices with hardcoded service-port credentials, while imposing minimal disruption on legitimate vendor field-service workflows.

Specifically:

1. **Authenticate the technician** with a factor independent of the device's hardcoded credential.
2. **Provide per-user attribution** for every service session.
3. **Record session content** for post-hoc analysis.
4. **Detect tampering** with the shim itself.
5. **Fail safe** — disable traffic on any error condition rather than fall through to unprotected pass-through.
6. **Preserve break-glass capability** for genuine emergencies.

## Non-goals

- The shim is **not** a replacement for the device's authentication. The device's hardcoded credential remains in place; the shim adds a layer above it.
- The shim does **not** modify any traffic that has been authenticated. It is a gate, not a translator. Vendor service tooling continues to use the credential it always used.
- The shim does **not** provide cryptographic protection of the underlying serial protocol. If the device's service-port protocol is unencrypted, it remains so. The shim's protection is at the access-control layer, not the transport layer.

## Threat model for the shim itself

The shim, being a security boundary device, has its own threat model:

| Threat | Mitigation |
|---|---|
| Adversary bypasses the shim by physical removal | Tamper-evident sealing; heartbeat alerting; cable management that makes shim difficult to remove unobserved |
| Adversary observes TOTP secret during enrolment | Enrolment performed in controlled environment with single-use HSM-backed channel |
| Adversary clones the shim with a different secret | Asset tagging with serialised tamper-evident sticker; hardware unique ID stored in central inventory |
| Adversary tampers with shim firmware | Secure boot (production hardware); firmware update only via signed bundle; integrity attestation at boot |
| Adversary records TOTP code from one session and replays | TOTP windowing standard (30 s window, 1 step tolerance); replay detection in shim state |
| Adversary performs DoS by holding the shim in challenge state | Rate limiting on challenge attempts; lockout after N failures; alerting |
| Adversary captures session recording | Recording encrypted at rest; key managed by central recording infrastructure |
| Loss of network → no SIEM forwarding | Local recording continues; forward-on-restoration; alarm if local storage exhausted |
| Power loss | Fail-safe to disabled traffic; battery-backed RTC for accurate timestamping |

## Authentication design

### TOTP factor

The technician's second factor is a Time-Based One-Time Password (TOTP), per RFC 6238. The shim accepts the same TOTP secrets used by the organisation's broader MFA infrastructure (Duo, Microsoft Authenticator, Google Authenticator, hardware tokens supporting OATH-TOTP).

Specifications:

- Algorithm: HMAC-SHA1 (RFC 4226 compatible) with optional HMAC-SHA256 in production hardware
- Period: 30 seconds (standard)
- Digits: 6
- Window tolerance: ±1 step (60 seconds total) to accommodate clock drift
- Replay protection: shim records last-accepted code per user for the current period; rejects re-use within the period

### Identity

The technician identity is bound to the TOTP secret at enrolment. The shim's local identity database maps `technician_id → totp_secret`. Authentication produces a session attributed to that technician, recorded in the session log.

### Session lifecycle

```
[Technician connects]
       │
       ▼
[Shim presents challenge prompt over the technician-side serial]
       │
       │  Technician enters: <technician_id> <totp_code>
       ▼
[Shim verifies TOTP]
       │
       ├── Success ──► [Shim opens passthrough; starts session recording]
       │                       │
       │                       ▼
       │              [Bidirectional traffic flows; recorded in real time]
       │                       │
       │                       │  Idle timeout reached, technician disconnects, or
       │                       │  tamper alert fires
       │                       ▼
       │              [Shim closes passthrough; flushes recording; alerts SIEM]
       │
       └── Failure ──► [Reject; record failed attempt; rate-limit subsequent attempts]
```

## Session recording design

Session recordings capture:

- Timestamp (UTC, with high-resolution monotonic clock for ordering)
- Technician identity (resolved from authenticated TOTP)
- Session start, end, and duration
- Bidirectional serial traffic, byte-for-byte
- Any error or alert raised during the session

Recordings are written to local non-volatile storage (eMMC / SD card with wear-levelling on production hardware) and additionally streamed to the SIEM when network is available.

Storage budget: 90 days of online recordings sized for a typical service-tool session footprint (~5 MB per session, ~100 sessions per shim per year).

## Tamper detection

A heartbeat protocol runs between the shim and the central monitoring system:

- Shim emits a signed heartbeat every 60 seconds containing serial number, uptime, and current state.
- Central system flags any shim that misses three consecutive heartbeats.
- Power loss at the shim emits a final "shutting down" message if possible (capacitor-backed) and logs an "unexpected absence" otherwise.
- Physical tampering (case opening, cable interception, magnetic-field anomaly on production hardware) emits an immediate alert.

In the absence of network, the shim caches heartbeats locally and forwards on restoration.

## Break-glass procedure

For genuine clinical emergencies where the TOTP factor is unavailable:

1. Technician notifies clinical engineering on-call.
2. Clinical engineering on-call notifies InfoSec on-call (concurrent, not sequential).
3. InfoSec on-call generates a break-glass code from the central MFA service. The code is a one-time, time-limited factor with elevated audit metadata.
4. Technician enters the break-glass code; shim accepts it once, with elevated logging.
5. Within 24 hours, both clinical engineering and InfoSec leadership review the break-glass usage.

The break-glass procedure is documented operationally in BG-PUMP-001 (organisation-specific). The shim's role is to accept the break-glass code, mark the session with elevated metadata, and ensure both parallel notifications are emitted.

## Failure modes

The shim's behaviour in failure modes is deliberate:

| Failure | Behaviour |
|---|---|
| Power loss | Traffic disabled; on restore, returns to challenge state |
| Storage exhausted | Refuses new sessions; alerts SIEM; existing in-progress session continues with degraded recording |
| Network loss | Continues to gate sessions and record locally; forwards on restoration; alerts on extended outage |
| TOTP service-time skew | Window tolerance ±1 step; if drift exceeds, requires re-enrolment |
| Tamper alert | Disables traffic; requires physical inspection and re-enabling |
| Firmware integrity violation | Refuses to boot; alerts via out-of-band channel if possible |

Notice that no failure mode falls back to unprotected pass-through. This is intentional — it is the **opposite** of the typical fail-open posture of network firewalls — because the shim's purpose is access control, and the device behind it is fail-operational on its own (the device continues to function for clinical use without the shim; only the *service-port path* is gated).

## Security properties claimed

The shim aims to provide:

- **Authentication**: every service session is attributed to an enrolled technician.
- **Audit**: every service session is recorded for post-hoc analysis.
- **Tamper-evidence**: physical tampering with the shim is detected and alerted.
- **Replay resistance**: TOTP replay within the period is detected.
- **Defence in depth**: the shim's protection is independent of and complementary to the device's hardcoded credential.

The shim does **not** provide:

- Confidentiality of the serial protocol (out of scope)
- Integrity of the serial protocol (out of scope; the shim does not modify traffic)
- Protection against an adversary with **both** physical access to the shim **and** a valid technician's TOTP secret (assumed to be a trusted insider; the audit trail provides post-hoc attribution but does not prevent the action)

## Design alternatives considered

- **In-band authentication via the device itself**: rejected because it requires the device firmware to be modified, which is precisely the constraint Pattern C addresses.
- **Smart-card-based authentication**: appealing but introduces card-management overhead and depends on the technician's tooling supporting card readers, which most vendor service tools do not.
- **Bluetooth or NFC second factor**: rejected for the same reason — adds a wireless attack surface and requires shim-side wireless capability.
- **Out-of-band approval (technician requests, central system approves)**: appealing for production deployments; treated as a future enhancement rather than baseline.
- **No tamper detection**: rejected. Without tamper detection the shim's audit trail is unverifiable.

The TOTP design is chosen because (a) the secrets are widely supported by existing MFA infrastructure, (b) the protocol is offline-capable, and (c) the threat model — physical proximity for service activity — is well-served by a code-based factor.
