# Target Device — Infusion Pump Emulator

Python-based emulator of a representative **Archetype 2 (embedded RTOS legacy)** large-volume infusion pump. The emulator deliberately reproduces the security constraints documented in the paper and the STRIDE-HC threat model:

- Cleartext HL7 v2 listener on TCP/2575
- Cleartext HTTP management interface on TCP/8080
- Hardcoded service-mode credential (`service:Vendor1234`)
- No per-user authentication
- No audit logging on the device itself
- Simulated protocol-parser fragility (oversize HL7 messages cause emulated crash and recovery)

These constraints are the **test surface** for compensating-control evaluation. The emulator is intentionally insecure; do not deploy outside the harness's isolated Docker network.

## Endpoints

| Method | Path | Auth | Behaviour |
|---|---|---|---|
| GET | `/status` | none | Returns model, firmware version, uptime — typical "is alive" probe |
| GET | `/infusion` | basic | Returns current infusion parameters |
| POST | `/infusion` | basic | Updates infusion parameters (no validation — the constraint) |
| GET | `/service-mode` | basic | Returns service-mode state |
| POST | `/service-mode` | basic | Toggles service-mode |
| POST | `/firmware` | basic | Accepts and "applies" any firmware payload (no signature check — the constraint) |

| Port | Service | Notes |
|---|---|---|
| 2575/TCP | HL7 v2 listener | Cleartext, MLLP-ish framing, ACKs every message, no authentication |
| 8080/TCP | HTTP management | Cleartext, HTTP Basic auth with hardcoded credential |

## Why these specific behaviours?

Each behaviour maps to a real-world constraint that real Archetype 2 devices exhibit:

| Emulator behaviour | Real-world analog |
|---|---|
| Hardcoded `service:Vendor1234` | Service-mode credentials documented in vendor manuals; many disclosed publicly |
| No per-user auth | Embedded RTOS devices typically have no account model |
| No audit log | RTOS devices typically have no syslog daemon or persistent log |
| Cleartext HL7 v2 | Most legacy infusion pumps use HL7 v2 over MLLP without TLS |
| Buffer-bounded parser | URGENT/11-class CVEs in VxWorks IPnet stack |
| Arbitrary-payload firmware push | Devices that accept unsigned firmware via management interface |

## Running standalone

```bash
docker build -t harness-target .
docker run -p 8080:8080 -p 2575:2575 harness-target
```

```bash
# Probe
curl http://localhost:8080/status
# {"model": "ExampleMed Volumetric Infusion Pump v3.2 (emulated)", ...}

# Authenticate and read infusion state
curl -u service:Vendor1234 http://localhost:8080/infusion
# {"patient_mrn": "0000000", ...}
```

## Extending

To add new emulators for other device archetypes (e.g., a Windows 7-style PACS workstation), follow this pattern:

1. Create a new directory under `test-harness/`.
2. Provide a Dockerfile, an emulator script, and a README documenting the constraints reproduced.
3. Add the new service to `docker-compose.yml`.
4. Add scenarios under `attacker/scenarios/` if the new emulator exposes new attack surfaces.
