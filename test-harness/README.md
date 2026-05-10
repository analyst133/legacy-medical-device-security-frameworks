# Test Harness

A Dockerised multi-container test environment for **empirical evaluation of compensating-control effectiveness** against the legacy medical device threat model defined in the paper.

> **Status:** Functional prototype. The harness implements a representative Archetype 2 (embedded RTOS legacy) infusion pump emulator, a clinical workstation, an attacker container with five scenarios mapped to STRIDE-HC categories, and a compose-profile-based controls overlay. It is intended to support the empirical claim made by paper §9.3 and to be extended by contributors with additional device archetypes, scenarios, and controls.

> **Designing or running experiments?** See [`METHODOLOGY.md`](./METHODOLOGY.md) for experimental design, expected outcome matrix, statistical considerations, limitations, and how harness output feeds CJR effectiveness validation and MDRS CCD scoring.

## What the harness is for

Compensating controls in legacy medical device security are typically deployed without quantitative measurement of their effectiveness. The harness addresses this gap by providing a reproducible environment in which:

1. A specific compensating control can be toggled on or off.
2. A specific attack scenario can be executed.
3. The outcome can be observed and recorded.

The result is a `(scenario × control configuration → outcome)` matrix that supports claims about which controls actually mitigate which threats — the kind of evidence that strengthens FDA premarket cybersecurity submissions, ISO 14971 residual risk evaluation, and HDO compensating-control deployment decisions.

## What the harness is *not*

- **Not a penetration testing tool.** The attacker scenarios target an emulated environment, not commercial medical devices.
- **Not a substitute for production validation.** Empirical results from the harness inform but do not replace deployment-context validation in real clinical environments.
- **Not a compliance certification.** The harness is research output. Its results inform compliance evidence but are not in themselves a compliance artifact.

## Architecture

```
┌──────────────────────────┐         ┌────────────────────────────┐
│  Clinical workstation    │         │  Target device (emulated)  │
│  ─────────────────────── │         │  ───────────────────────── │
│  Sends HL7 v2 orders     │ ─────►  │  Archetype 2 infusion pump │
│  TCP/2575                │         │  VxWorks-style RTOS sim    │
│  Issues management cmds  │         │  HL7 listener TCP/2575     │
│  TCP/8080                │ ─────►  │  Mgmt interface TCP/8080   │
│                          │         │  Hardcoded service cred    │
└──────────────────────────┘         └────────────────────────────┘
              ▲                                   ▲
              │                                   │
              │     ┌──────────────────────┐     │
              │     │  Attacker            │     │
              │     │  ──────────────────  │     │
              └─────│  Scenario scripts    │─────┘
                    │  ARP poison, sniff,  │
                    │  flood, exploit      │
                    │  default cred        │
                    └──────────────────────┘
                              ▲
                              │ (in / out per profile)
                              │
                    ┌──────────────────────┐
                    │  Controls (profiles) │
                    │  ──────────────────  │
                    │  IPS virtual patch   │
                    │  PAM upstream        │
                    │  Network segmenta'n  │
                    └──────────────────────┘
```

All four containers run on a shared Docker network. Compose profiles selectively introduce control containers (`--profile ips`, `--profile pam`, `--profile segmentation`) which intercept or modify traffic between attacker and target.

## Quick start

Prerequisites: Docker Engine 24+, Docker Compose v2+, Python 3.10+ (for running scenarios from the host), 4 GB RAM.

```bash
# Bring up baseline (target + workstation + attacker), no controls
docker compose up -d

# Verify target is reachable
curl http://localhost:8080/status

# Run a scenario (default credential exploit)
docker compose exec attacker python scenarios/05-eop-default-credential.py

# Bring up with IPS virtual patching enabled
docker compose --profile ips up -d
docker compose exec attacker python scenarios/05-eop-default-credential.py
# Observe blocked outcome

# Run all scenarios across all control profiles
make matrix
# Results written to results/run-<timestamp>/results.csv
```

## File layout

```
test-harness/
├── README.md
├── METHODOLOGY.md            # How to run experiments, baselining, statistical considerations
├── ROADMAP.md                # Planned extensions
├── docker-compose.yml        # Top-level orchestration
├── Makefile                  # Convenience targets including matrix runs
├── target-device/
│   ├── Dockerfile
│   ├── infusion-pump-emulator.py    # Python emulator of Archetype 2 pump
│   └── README.md
├── clinical-workstation/
│   ├── Dockerfile
│   └── workstation-emulator.py
├── attacker/
│   ├── Dockerfile
│   ├── runner.py             # Orchestrator that runs scenarios and records outcomes
│   └── scenarios/
│       ├── 01-spoofing-arp-poisoning.py
│       ├── 02-tampering-firmware-injection.py
│       ├── 03-info-disclosure-cleartext-hl7.py
│       ├── 04-dos-protocol-flood.py
│       └── 05-eop-default-credential.py
├── controls/
│   ├── README.md
│   ├── ips-virtual-patching.yml
│   ├── pam-upstream.yml
│   ├── network-segmentation.yml
│   └── compose-profiles.md
└── results/
    └── sample-results.csv    # Example results file from a representative run
```

## STRIDE-HC scenario mapping

| Scenario | STRIDE-HC category | Target attack surface |
|---|---|---|
| 01 ARP poisoning | S — Spoofing | Network |
| 02 Firmware injection | T — Tampering | Network (mgmt interface) |
| 03 Cleartext HL7 sniffing | I — Information Disclosure | Network |
| 04 Protocol flood DoS | D — Denial of Service | Network |
| 05 Default-credential exploit | E — Elevation of Privilege | Network (mgmt interface) |

R — Repudiation is addressed by the harness *passively*: every scenario's outcome is logged. The detection-as-control evaluation is in the post-run analysis (which controls produced log evidence sufficient to attribute the activity).

Physical-attacker scenarios are not directly executable in a software harness; testing the Pattern C MFA shim against physical-port abuse requires the hardware reference design. See `mfa-shim/`.

## Controls covered

| Profile | Control | What it does |
|---|---|---|
| (none) | Baseline | No compensating controls active |
| `ips` | IPS virtual patching | Network IPS sidecar drops traffic matching virtual-patch signatures |
| `pam` | PAM upstream (Pattern A) | All management traffic must originate from PAM gateway IP |
| `segmentation` | Network segmentation | Target device on isolated subnet; attacker on different subnet without route |
| `all` | Combined | All three controls active |

The compose profiles are deliberately simple — they demonstrate the testing methodology rather than emulate production security tooling. Production deployments would substitute production controls (Snort/Suricata signatures, CyberArk PSM, real network ACLs) following the same pattern.

## Contributing scenarios and controls

See top-level [`CONTRIBUTING.md`](../CONTRIBUTING.md). For the harness specifically:

- **New scenarios** must include STRIDE-HC mapping, target-archetype applicability, and idempotent execution.
- **New device emulators** should follow the structure of `target-device/infusion-pump-emulator.py`.
- **New controls** should be implementable as a compose profile to enable matrix runs.

## Licence

Apache License 2.0. See top-level [`LICENSE`](../LICENSE).
