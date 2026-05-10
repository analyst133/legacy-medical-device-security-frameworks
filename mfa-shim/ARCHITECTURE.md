# Pattern C MFA Shim — Architecture

System architecture, components, and data flow. Read after `DESIGN.md` for context.

## System diagram

```
                                         ┌────────────────────────────┐
                                         │   Central recording &      │
                                         │   monitoring (SIEM)        │
                                         └──────────────┬─────────────┘
                                                        │
                                       Encrypted        │
                                       session forward  │
                                       Heartbeats       │
                                       Tamper alerts    │
                                                        │
                                                        ▼
┌──────────────────────┐    Tech-facing       ┌────────────────────────┐    Device-facing       ┌────────────────────────┐
│  Vendor service      │ ◄─── serial ───────► │  Pattern C MFA shim    │ ◄─── serial ────────► │  Medical device        │
│  tooling (laptop)    │                      │                        │                        │  (RS-232 service port) │
└──────────────────────┘                      │  ┌─────────────────┐   │                        └────────────────────────┘
                                              │  │ TOTP gate       │   │
                                              │  ├─────────────────┤   │
                                              │  │ Session recorder│   │
                                              │  ├─────────────────┤   │
                                              │  │ Tamper detector │   │
                                              │  ├─────────────────┤   │
                                              │  │ Local storage   │   │
                                              │  └─────────────────┘   │
                                              │                        │
                                              │  Tamper-evident case   │
                                              │  Battery-backed RTC    │
                                              │  Secure boot           │
                                              └────────────────────────┘
```

## Components

### TOTP gate (`prototype/totp_gate.py`)

Implements the user-facing authentication. Receives `(technician_id, totp_code)` and returns `(authenticated_session_token, technician_record)` or `(None, error)`. Stateless apart from the replay-protection cache.

**Inputs**: technician identity, TOTP code, current time
**Outputs**: authenticated session record, or rejection with reason
**State**: in-memory cache of (user, period) → True for replay protection

### Session recorder (`prototype/session_recorder.py`)

Writes session metadata and bidirectional traffic to local storage and, when reachable, to the SIEM. Provides start/stop primitives and continuous append-during-session.

**Inputs**: session token, traffic chunks, terminal events
**Outputs**: durable session record in local storage; SIEM forward on availability
**State**: open file handle for current session; SIEM forward queue

### Tamper detector (`prototype/tamper_detector.py`)

Emits heartbeats on a periodic interval. Production hardware integrates with case-open switch, magnetic-field sensor, and accelerometer; the prototype emulates these with file-based or signal-based triggers for testing.

**Inputs**: time tick, hardware sensor states, configuration
**Outputs**: heartbeat to SIEM; tamper alert to local + SIEM; emergency pass-through disable signal
**State**: heartbeat counter, sensor state cache

### Shim daemon (`prototype/shim.py`)

Top-level orchestrator. Wires the components together, manages the technician-side and device-side serial connections, runs the state machine, and coordinates the components' lifecycles.

**Inputs**: configuration file, two serial endpoints (technician-side, device-side)
**Outputs**: bidirectional traffic forwarding when authenticated; rejection prompts otherwise
**State**: connection state, current session token

## State machine

```
              ┌──────────────┐
              │   IDLE       │   No active session; passthrough disabled
              └──────┬───────┘
                     │
      Technician-side connection detected
                     │
                     ▼
              ┌──────────────┐
              │  CHALLENGE   │   Prompt sent; awaiting credentials; rate-limited
              └──────┬───────┘
                     │
              ┌──────┴──────┐
              │             │
       Auth success    Auth fail (5x in 60s)
              │             │
              ▼             ▼
       ┌───────────┐   ┌──────────┐
       │  OPEN     │   │ LOCKED   │   Lockout; admin reset required
       └─────┬─────┘   └──────────┘
             │
       Recording in progress; passthrough enabled
             │
       ┌─────┴──────┐
       │            │
   Tech disconnect  Tamper detected, idle timeout, or storage exhausted
       │            │
       ▼            ▼
  ┌──────────┐  ┌────────────────┐
  │ FLUSHED  │  │ EMERGENCY_STOP │
  └─────┬────┘  └────────┬───────┘
        │                │
        └────────┬───────┘
                 ▼
              ┌──────────────┐
              │   IDLE       │
              └──────────────┘
```

State transitions are deterministic and logged. A transition to `EMERGENCY_STOP` requires manual intervention to return to `IDLE` (in production hardware, a key-based reset; in the prototype, a configuration command).

## Data flows

### Bidirectional traffic (active session)

```
Technician ─► Shim ─► Recorder.write_inbound ─► Shim ─► Device
Technician ◄─ Shim ◄─ Recorder.write_outbound ◄─ Shim ◄─ Device
```

Recording is on the data path but does not block forwarding — the recorder uses a non-blocking append that is durable on file close.

### Heartbeat (background)

```
TamperDetector.tick() ──► Heartbeat msg ──► Local log + SIEM forward queue
                                     │
                          if SIEM reachable ──► SIEM
                          else cache locally; forward on restore
```

### Tamper alert (asynchronous)

```
Sensor event ──► TamperDetector.alert() ──► Shim.emergency_stop()
                                       └──► Local log + SIEM (highest priority)
```

## Configuration

The shim is configured via a YAML file (see `prototype/config.example.yaml`). Configuration covers:

- Technician identity database (or pointer to external user store)
- TOTP parameters (algorithm, period, digits, window tolerance)
- Serial endpoint paths for technician-side and device-side
- Session timeout and recording size budget
- SIEM endpoint and authentication
- Tamper-detection thresholds and response

Configuration is loaded at startup; runtime changes require restart (deliberate — the shim should not have a live reconfiguration interface that could be abused).

## Storage layout

```
/var/lib/shim/
├── sessions/
│   ├── 2026-04-15T09-22-03.empump-12-tech-001.session
│   ├── ...
├── heartbeats/
│   ├── 2026-04-15.log
│   ├── ...
├── alerts/
│   ├── 2026-04-15T09-25-11.tamper.json
│   └── ...
└── state/
    ├── replay-cache.bin
    └── lockout.json
```

In production hardware, `/var/lib/shim/` is on encrypted storage with a key managed by the central recording infrastructure.

## Network protocols

- **SIEM forward**: TLS 1.2+ with mutual authentication. Format: structured log lines (Common Event Format or vendor-specific).
- **Heartbeat**: same channel as SIEM forward, with lower priority.
- **Time sync**: NTP over the management network. Important for TOTP correctness.

The shim does not run any inbound network listener. Operationally this means it does not need to be reachable from the wider network; it only initiates outbound connections.

## Boot integrity

In the prototype, boot integrity is best-effort (the user is responsible for the OS image). In production hardware:

- Secure boot anchored in hardware root of trust
- Signed firmware with anti-rollback counter
- Boot integrity report included in heartbeat metadata
- TPM or equivalent for secret storage

## Component dependencies

| Component | Depends on |
|---|---|
| `shim.py` | `totp_gate.py`, `session_recorder.py`, `tamper_detector.py`, `pyserial`, `pyyaml` |
| `totp_gate.py` | `pyotp` |
| `session_recorder.py` | (standard library; optional `requests` or `httpx` for SIEM forward) |
| `tamper_detector.py` | (standard library) |

Total runtime dependency footprint is small (3 third-party packages), suitable for embedded targets.

## Performance budget

The shim is on the data path between technician tooling and the device. Latency must be bounded:

- Per-byte forwarding overhead: < 1 ms (recording on a separate thread)
- Authentication latency: < 500 ms (TOTP verification + replay-cache check)
- Heartbeat overhead: negligible (60s period)

For RS-232 service ports running at 9600–115200 baud, these bounds are well within tolerance.
