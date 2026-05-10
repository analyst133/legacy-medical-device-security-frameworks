# Compensating Controls — Profiles

This directory contains the compensating-control implementations toggled via Docker Compose profiles. Each control corresponds to a category of compensating control documented in the Compensating Controls Playbook (paper §3 Tables 2 and 3).

## Available controls

| Profile | Implementation | Playbook entry |
|---|---|---|
| `ips` | `ips/` — virtual patching sentinel | "No patching possible", "Legacy embedded RTOS" |
| `pam` | `pam/` — Pattern A upstream gateway | "MFA not supported", "Shared/hardcoded credentials" |
| `segmentation` | `segmentation/` — network isolation sentinel | "Legacy general-purpose OS", "Legacy embedded RTOS" |
| `all` | All three combined | Defence-in-depth |

## Why these specific controls?

The three profiles cover the dominant compensating-control patterns identified in the paper:

- **PAM upstream (Pattern A)** is the network-side compensating control for the MFA-not-supported and shared-credential constraints — the most common and most operationally significant constraints in legacy device fleets.
- **IPS / virtual patching** is the standard compensating control for the no-patching constraint, applicable to both archetypes.
- **Network segmentation** is the universal control for legacy device isolation; it is referenced in every constraint entry of the Playbook because it is a foundational control without which the others cannot be deployed effectively.

The harness intentionally does **not** implement application allowlisting or EDR, because the target device emulator is Archetype 2 (no host-based control surface). For an Archetype 1 emulator (planned per `../ROADMAP.md`), application allowlisting and EDR profiles would be added.

## Implementation fidelity

These controls are **teaching reference implementations**, not production controls. Specifically:

- **IPS** is implemented as a sentinel that signals its presence to the runner. Real virtual patching would use Snort or Suricata signatures applied to in-line traffic via eBPF or veth redirect. Adding this is on the roadmap.
- **PAM** is a working HTTP proxy with two-factor authentication that demonstrates the architectural pattern. A production deployment would use CyberArk PSM, BeyondTrust, Delinea, or similar with full session recording, secrets vaulting, just-in-time access, and approval workflows.
- **Segmentation** is implemented as a sentinel pending an alternate compose file that places the attacker on a separate Docker network. The simpler approach for the operator is to manually disconnect the attacker from `harness-pump-net` after `compose up`:

  ```bash
  docker compose --profile segmentation up -d
  docker network disconnect harness-pump-net harness-attacker
  ```

  This achieves true Layer 3 isolation for testing.

## Pattern C is not in this directory

The Pattern C MFA shim (the **physical-attacker** counterpart to Pattern A) is not represented in the harness because physical-port attacks cannot be exercised in a software-only environment. The Pattern C reference design is in `../../mfa-shim/`.

## Adding a new control profile

1. Create a subdirectory here.
2. Provide `Dockerfile` and implementation script.
3. Add a service to `../docker-compose.yml` with `profiles: ["your-profile"]`.
4. Update the expected-outcome matrix in `../METHODOLOGY.md`.
5. Document the control's compensating-control playbook mapping in this README.
