# MFA Shim — Pattern C Reference Design

Software reference design for the **inline service-port multi-factor authentication shim** introduced in paper §3.4 as Pattern C.

**Interactive demo with live TOTP gate in your browser — no install:**
**[https://analyst133.github.io/legacy-medical-device-security-frameworks/mfa-shim/](https://analyst133.github.io/legacy-medical-device-security-frameworks/mfa-shim/)** — architecture diagram, session-flow walkthrough, and a working RFC 6238 TOTP gate you can authenticate against.

> **Status:** Functional prototype. The Python implementation under `prototype/` demonstrates the security mechanisms (TOTP gate, session recording, tamper detection) at a level sufficient to validate the design and to support pilot deployments at the institutional research level. Production hardware procurement and FDA regulatory analysis are out of scope for this artifact and are flagged in `FDA-CONSIDERATIONS.md`.

## Why Pattern C exists

Patterns A (upstream PAM) and B (network-gated reachability) protect the **network-side** management interface of legacy medical devices. They do nothing for the **physical service port** — the RS-232, USB, or proprietary connector that vendor field engineers use, which typically has its own hardcoded credentials documented in service manuals.

For Archetype 2 devices in particular, the physical service port is a serious threat surface: the credentials are publicly disclosed, there is no audit logging, and there is no way to retrofit the device with MFA. To the authors' knowledge, **no commercially available product** addresses this threat directly. Pattern C fills that gap.

## How Pattern C works

A small in-line hardware element sits between the technician's tooling and the device's service port. It:

1. **Authenticates the technician** via a TOTP-equivalent challenge before passing any traffic.
2. **Records the entire session** — bidirectional traffic, timestamps, technician identity — to non-volatile storage and, when network reachable, to a SIEM.
3. **Detects tampering** with itself via a heartbeat protocol; tampering triggers a network-reachable alert.
4. **Falls safe on power loss** — traffic is disabled by default.
5. **Provides break-glass** — an authenticated emergency bypass procedure with elevated audit and on-call notification.

## What this directory contains

```
mfa-shim/
├── README.md                          # This file
├── DESIGN.md                          # Design rationale and security properties
├── ARCHITECTURE.md                    # System architecture, threat model, components
├── FDA-CONSIDERATIONS.md              # Regulatory analysis: when does insertion modify the device?
├── prototype/
│   ├── README.md                      # How to run the prototype
│   ├── shim.py                        # Main daemon
│   ├── totp_gate.py                   # TOTP authentication module
│   ├── session_recorder.py            # Session recording to disk and SIEM
│   ├── tamper_detector.py             # Heartbeat-based tamper detection
│   ├── config.example.yaml            # Configuration template
│   ├── requirements.txt               # Python dependencies (pyotp, pyyaml, pyserial)
│   └── tests/
│       ├── test_totp_gate.py          # pytest unit tests
│       ├── test_session_recorder.py
│       └── test_tamper_detector.py
└── hardware/
    └── README.md                      # Notes on porting to Raspberry Pi / ESP32 / custom hardware
```

## Quick start

```bash
cd mfa-shim/prototype
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the unit tests
python -m pytest tests/ -v

# Generate a TOTP secret for a technician
python -c "import pyotp; print(pyotp.random_base32())"

# Copy the config template and customise
cp config.example.yaml config.yaml

# Run the shim against a virtual serial pair
# (Requires socat on Linux: socat PTY,link=/tmp/shim-host PTY,link=/tmp/shim-device)
python shim.py --config config.yaml
```

The prototype runs against virtual serial ports for development. Hardware deployment with real RS-232 endpoints requires the hardware port — see `hardware/README.md`.

## Where this fits in the wider repo

| Question | Answer |
|---|---|
| When would I deploy this? | When a legacy device has a physical service port with hardcoded credentials that cannot be eliminated by Pattern A (network-side controls). |
| What CJR documents this control? | `cjr-templates/examples/cjr-leaked-service-pin.md` |
| What threat model entries are addressed? | STRIDE-HC categories T (Tampering), R (Repudiation), E (Elevation of Privilege) — physical-attacker scenarios |
| What MDRS dimension is affected? | CCD (Compensating Control Deficit) — adds coverage for physical-attacker EoP and Tampering, reducing CCD by 1–2 points typically |

## Status and limitations

This is a **research artifact**, not a regulated product or ready-to-deploy operational tool. Specific limitations:

- Software-only prototype; production hardware not provided.
- Has not been validated in any clinical environment.
- Has not received FDA clearance, EU MDR conformity assessment, or any other regulatory approval.
- Inline insertion of any device into a medical device's service port may, depending on jurisdiction and specifics, constitute a modification requiring the operator to engage with regulatory authorities. See `FDA-CONSIDERATIONS.md` before any deployment.
- The authors have published this design specifically to spur production-quality, regulatory-cleared implementations and to make the architectural pattern publicly available under Apache-2.0 (with patent grant) so that no party can monopolise it.

## Licence

Apache License 2.0. See top-level [`LICENSE`](../LICENSE).

The Apache-2.0 patent grant clause applies in particular to this artifact: the design is published as research output, the code is licensed permissively, and the patent grant ensures that contributors cannot subsequently assert patent claims against users of the design.
