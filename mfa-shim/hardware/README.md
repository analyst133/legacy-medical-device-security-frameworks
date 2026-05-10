# Hardware Port — Pattern C MFA Shim

Notes for porting the Python reference design to production hardware. This document is intended for hardware engineers and device manufacturers building a deployable Pattern C device.

## Why a hardware port matters

The Python reference design demonstrates the security mechanisms but is not a deployable product. A production-grade Pattern C shim must satisfy several requirements that the prototype does not:

- **Tamper-evident enclosure** with case-open detection, ideally with capacitor-backed alerting on power loss.
- **Hardware root of trust** anchoring secure boot and protecting the local credential store.
- **Battery-backed real-time clock** for accurate TOTP windowing in the absence of network time.
- **Industrial RS-232 line drivers / level shifters** to interoperate with diverse vendor service ports without electrical fault.
- **EMC compliance** for clinical environments (IEC 60601-1-2).
- **Operating temperature range** appropriate to clinical settings (0–40 °C minimum, often broader).
- **Storage durability** for session recordings in the presence of unexpected power loss (proper journaling filesystem, eMMC with power-loss protection, or equivalent).

## Candidate platforms

### Raspberry Pi (development and small pilots)

- **Raspberry Pi Zero 2 W** or **Raspberry Pi 4** Compute Module with carrier board.
- Pros: large software ecosystem, well-supported pyserial path, easy integration of the Python prototype.
- Cons: not industrial-grade; no certified secure-boot story without additional measures; case design must be custom.
- Suitable for: pilot deployments at the institutional research level.

Notes on Raspberry Pi port:

- Use the GPIO-attached UART (`/dev/ttyAMA0`) for one side and a USB-serial adapter (`/dev/ttyUSB0`) for the other.
- The GPIO header includes inputs suitable for case-open switches, accelerometer, and Hall-effect sensors. Wire to the GPIO pins and read via `RPi.GPIO` or `gpiozero`.
- Battery-backed RTC: add an Adafruit DS3231 RTC module via I²C (well-supported under Linux as `rtc-ds3231`).
- Storage: use industrial-grade microSD or, preferably, an HAT-attached eMMC module.
- Boot: pi-bootcode-signing (with trustfs/cryptsetup overlay) provides best-effort secure boot.

### ESP32 (potential dedicated-hardware port)

- **ESP32-S3** with sufficient flash and PSRAM.
- Pros: compact, low power, suitable for always-on pen-form-factor; can be entirely embedded inside a tamper-evident case directly attached to the service port.
- Cons: full Python prototype not directly portable; would require translation to MicroPython or C/C++ implementation. Less filesystem capacity for session recordings.
- Suitable for: production hardware with a hardened embedded codebase.

A faithful port to ESP32 would:

- Use ESP-IDF in C, with mbedTLS for HMAC and AES.
- Implement the TOTP algorithm directly per RFC 6238 (algorithmically simple).
- Use SPIFFS or LittleFS for local session recording, with periodic flush to a server.
- Use the ESP32's secure boot and flash encryption for boot integrity.
- Use deep-sleep with case-open interrupt for power-efficient always-on behaviour.

### Custom hardware

- **STM32 or NXP i.MX RT** for a fully purpose-built device.
- Pros: industrial-grade, full control over secure-boot chain, can include hardware secure element (e.g., NXP A1006 or Microchip ATECC608B) for credential storage.
- Cons: longest path to first prototype; requires hardware engineering team.
- Suitable for: a manufacturer or partner taking the design to a market product.

## Hardware-software boundary

The Python reference design has clean abstractions that map well to a hardware port:

| Python protocol | Hardware mapping |
|---|---|
| `SerialEndpoint` | UART driver |
| `TamperSensor` | GPIO interrupts on case-open switch, magnetic sensor, accelerometer |
| `SessionRecorder` | Filesystem on power-protected storage |
| `TotpGate` | RFC 6238 implementation in C/C++ or MicroPython |
| `SiemTransport` | TLS over WiFi/Ethernet (consider mTLS for mutual auth) |

## Tamper-evident enclosure considerations

A production enclosure should:

- Use **screw covers** with serialised tamper-evident stickers.
- Include a **case-open microswitch** on the lid, wired to a hardware GPIO with capacitor-backed alert capability.
- Optionally include a **magnetic field sensor** to detect proximity tooling that might attempt to disable the case-open switch externally.
- Be made of **non-conductive material** to avoid creating accidental ground paths into the medical device's service port.
- Include a **factory-test mode** behind a key/jumper that allows enrolment and provisioning without triggering tamper alerts; this mode must be unavailable in deployed firmware.

## Cabling

The shim sits in-line between the technician's tooling and the medical device's service port. Cabling considerations:

- **Physical robustness**: vendor service tools are unfamiliar with shim presence and may pull cables; strain relief is essential.
- **Connector polarity**: ensure the technician-facing connector is opposite-polarity (or differently keyed) to the device-facing connector to prevent accidental loop-back.
- **Pin-1 indication**: clearly mark which connector goes where, especially if either side is non-standard (some vendor service ports use proprietary pinouts).

## Power

- **Mains-derived power** with a small UPS battery to support graceful shutdown logging on power loss.
- **Power loss should not trigger a tamper alert** — distinguish "expected absence" (graceful shutdown) from "unexpected absence" (likely tamper) via the heartbeat protocol.

## Provisioning and decommissioning

Hardware shims must support:

- **Initial provisioning** in a controlled environment (e.g., a clinical engineering bench): assign serial number, generate device-specific cryptographic identity, enrol initial technicians, set up SIEM transport.
- **Decommissioning**: secure wipe of recordings, secrets, and identity material before disposal or reassignment.
- **Replacement**: rapid swap when a unit fails, without disrupting the TOTP factor of enrolled technicians (because the secret is in the technician's authenticator app, not the shim).

## Manufacturing and supply chain

- **Component sourcing**: prefer parts with long-term availability (industrial-grade RTCs, secure elements with multi-decade roadmaps). Hospital deployment lifecycles are 10+ years.
- **Provenance**: include each shim's hardware identity in a central inventory, signed at manufacturing time.
- **Supply chain integrity**: tamper-evident packaging from manufacturer to deployment.

## Cost and form factor

Estimated bill-of-materials cost ranges:

| Platform | Approx BOM |
|---|---|
| Raspberry Pi-based | $80–150 per unit |
| ESP32-based | $20–40 per unit |
| Custom STM32 with secure element | $40–80 per unit |

Form factor:

- **Raspberry Pi**: roughly 100 × 60 × 30 mm with case; suitable for clip-on mounting.
- **ESP32**: small enough (≈ 50 × 30 × 15 mm) to embed directly into a service-port adapter cable.
- **Custom**: fully customisable; can be made to look like a standard service-cable adapter.

## Roadmap

The repository's roadmap places production hardware procurement on the 2027 plan. In the interim, the Python prototype is suitable for institutional pilot deployments under research-artifact governance (see `../FDA-CONSIDERATIONS.md`).

## Contributing hardware variants

If you build a hardware port, please contribute notes back to this directory:

1. A `<platform>/` subdirectory with build instructions, schematics (if free to publish), and bill-of-materials.
2. Any platform-specific software (firmware images are not required, but configuration notes are appreciated).
3. An entry in this README.

## Licence

Apache-2.0. The patent-grant clause applies, ensuring that contributors cannot subsequently assert patent claims against users of the design. See top-level [`LICENSE`](../../LICENSE).
