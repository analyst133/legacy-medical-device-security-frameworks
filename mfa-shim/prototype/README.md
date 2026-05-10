# MFA Shim Prototype

Python reference implementation of the Pattern C MFA shim. Demonstrates the security mechanisms (TOTP gate, session recording, tamper detection) at a level suitable for pilot evaluation and as the basis for a hardware port.

## Layout

```
prototype/
├── shim.py                 # Main daemon
├── totp_gate.py            # TOTP authentication (RFC 6238)
├── session_recorder.py     # Local + SIEM session recording
├── tamper_detector.py      # Heartbeat + tamper-event handling
├── config.example.yaml     # Configuration template
├── requirements.txt        # Python dependencies
└── tests/
    ├── test_totp_gate.py
    ├── test_session_recorder.py
    └── test_tamper_detector.py
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running the tests

```bash
python -m pytest tests/ -v
```

Expected output: 37 tests, all passing. The test suite covers:

- TOTP authentication: 16 tests (valid/invalid codes, window tolerance, replay protection, lockout, admin reset, user isolation, helpers, concurrency)
- Session recorder: 10 tests (lifecycle, traffic recording, SIEM forwarding, error paths, force-close)
- Tamper detector: 11 tests (state transitions, heartbeat timing, sensor polling, callback isolation, boot counting)

## Running the daemon

The shim daemon needs two serial endpoints — one technician-facing, one device-facing. For development, create a virtual pair using `socat`:

```bash
# In one terminal:
socat -d -d PTY,link=/tmp/shim-tech,raw,echo=0 PTY,link=/tmp/shim-dev,raw,echo=0
# Outputs the actual /dev/pts/N device names; the shim uses the symlinks /tmp/shim-tech and /tmp/shim-dev.
```

Generate a TOTP secret for a technician and prepare config:

```bash
python -c "import pyotp; print(pyotp.random_base32())"
# Copy that secret into config.yaml under technicians[].totp_secret

cp config.example.yaml config.yaml
# Edit config.yaml as needed
```

Run the daemon:

```bash
python shim.py --config config.yaml --log-level INFO
```

In a third terminal, connect to the technician-facing PTY (e.g., with `picocom /tmp/shim-tech` or `screen /tmp/shim-tech 9600`). You should see the challenge prompt:

```
Shim MFA gate. Authenticate as: <technician_id> <totp_code>
>
```

To authenticate, generate the current TOTP code from your authenticator app (or from `python -c "import pyotp; print(pyotp.TOTP('YOUR-SECRET').now())"`) and submit `alice@example.org 123456`. After success, the prompt becomes a transparent passthrough to the device-facing endpoint.

## Enrolment workflow

1. Authorised operator runs:

   ```bash
   python -c "import pyotp; print(pyotp.random_base32())"
   ```

2. Operator records the secret in the technician identity database (in production: LDAP/AD/enrolment service; in the prototype: `config.yaml`).

3. Technician enrolls in their authenticator app via the otpauth:// URI (or QR code generated from it):

   ```python
   from totp_gate import provisioning_uri
   print(provisioning_uri("alice@example.org", secret, issuer="ShimMFA"))
   ```

4. Technician confirms one successful TOTP code, recorded as enrolment confirmation.

## Running against a real device

The prototype runs against any OS-recognised serial device. To deploy against actual hardware:

1. Identify the technician-side and device-side serial endpoints (usually `/dev/ttyUSB0` and `/dev/ttyAMA0` or similar).
2. Update `config.yaml` with these paths.
3. Run with appropriate privileges to access the serial devices (often `dialout` group on Linux).

Performance note: per-byte forwarding overhead is < 1 ms. For RS-232 service ports running at 9600–115200 baud, this is well within tolerance.

## Caveats

- This is a research artifact. See `../FDA-CONSIDERATIONS.md` before any deployment.
- Production hardware would replace `pyserial` with a tighter integration to the hardware UART and add hardware-backed identity (TPM/secure-element). See `../hardware/README.md`.
- The default SIEM transport is no-op. Production deployments configure the transport.

## Extending

- **New SIEM transport**: implement the `SiemTransport` protocol in `session_recorder.py`. A typical implementation is a small wrapper around `requests.post()` to a TLS endpoint with mutual authentication.
- **Hardware sensors**: implement the `TamperSensor` protocol in `tamper_detector.py`. Production hardware integrates GPIO-attached case-open switches, magnetic-field sensors, and accelerometers.
- **Alternate authentication factors**: the gate is designed around TOTP but the architecture cleanly accommodates alternative second factors (FIDO2, smartcard) via additional gate modules and configuration.
