# Control Justification Record (CJR)

**CJR-ID:** CJR-EMPump-003-ServicePort
**Status:** Approved
**Version:** 1.0

## 1. Device identification

| Field | Value |
|---|---|
| Device name and model | ExampleMed Volumetric Infusion Pump v3.2 |
| Manufacturer | ExampleMed Inc. |
| Device class (FDA) | Class II |
| Device archetype | Archetype 2 (embedded RTOS legacy) |
| MDS² reference | ExampleMed-IP3.2-MDS2-2024 |
| Asset inventory IDs | Asset register: pump-vlan-volumetric-ip32 |
| Deployment count | 240 units |
| Linked STRIDE-HC threat model | `stride-hc-templates/examples/infusion-pump.md` |
| Current MDRS score and tier | 8.175 → CRITICAL |

## 2. Standard control and constraint

### 2.1 Standard control that cannot be applied

Per-technician MFA-protected authentication for service-port (RS-232) access, with audit logging of session activity.

### 2.2 Constraint preventing standard control

**Service-mode password disclosed in technical manual or leaked.** The service-port credential for the v3.2 pump is documented in vendor manuals that have been disclosed publicly through historical product-recall correspondence and via third-party repair documentation.

### 2.3 Constraint detail

The RS-232 service-port credential (4-digit PIN) is documented in:
- ExampleMed Inc. service manual (general circulation among contracted biomedical staff).
- Multiple third-party repair sites which mirror the manual.
- Historical 2018 product-recall correspondence which made the credential available via FDA freedom-of-information requests.

The vendor cannot rotate the credential in deployed firmware (rotation requires firmware update under FDA clearance). Vendor advisory ExampleMed-2024-04 acknowledges the disclosure and recommends "physical access control commensurate with the criticality of the device".

The constraint is permanent in the deployed firmware and represents the highest-risk physical-access exposure on this pump fleet.

## 3. Threat addressed

### 3.1 STRIDE-HC mapping

- **R** — Repudiation (unattributed service-mode access)
- **T** — Tampering (configuration tampering via service port)
- **E** — Elevation of Privilege (service-mode credential abuse)

### 3.2 Threat scenario summary

**Physical/insider-attacker scenarios:**
- Unauthorised service-mode access by individual with physical proximity, using publicly available credential.
- Configuration tampering of pump parameters via service port.
- Vendor-impersonation social engineering using disclosed credential and forged work order.
- Exfiltration of pump configuration data to USB via service tool.

This is the principal residual risk scenario after CJR-EMPump-001-MFA (Pattern A upstream PAM) addresses the network-side access path. Pattern A does not protect the physical service port; this CJR documents the Pattern C compensating control that does.

### 3.3 Initial risk assessment (pre-control)

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood | High | Credential publicly disclosed; required attacker capability is low (physical proximity + service tool). |
| Severity | High | Service-mode access enables therapy parameter modification, configuration tampering, and reset operations. |
| Detectability | Difficult | Pump generates no service-port event log; detection depends on human observation or upstream correlation. |

## 4. Compensating control(s) selected

### 4.1 Control description

**Pattern C — Inline hardware MFA shim at the RS-232 service port.** A small vendor-neutral hardware device sits inline between technician tooling and the pump's RS-232 service port. The shim:

- Presents a TOTP authentication challenge before passing any traffic to the pump.
- Records the entire serial session to non-volatile storage with timestamp, technician identity (resolved from TOTP factor binding), and full bidirectional traffic.
- Enforces tamper-evident sealing; tampering with the shim itself triggers a network-reachable alert.
- Falls back to disabled traffic on power loss or controller fault — an authenticated technician may bypass via a documented break-glass procedure escalated to InfoSec on-call.

The Pattern C device is currently a **research artifact** with a software-first reference design published in this repository (`mfa-shim/`). The deployment described in this CJR is at a single ICU pilot site (12 pumps) per the FDA-aware piloting plan documented in `mfa-shim/FDA-CONSIDERATIONS.md`.

This is **not** a cleared medical device; it is a security accessory deployed under the institutional research and quality improvement programme. Production-grade hardware procurement is on the 2027 plan.

In addition to Pattern C, this CJR documents the supporting policy controls:

- **Tamper-evident seal** on the service-port cover plate; monthly inspection logged.
- **Vendor-escort policy**: every vendor service activity must be accompanied by clinical engineering staff.
- **Pre-visit work order**: documented in change management with scope and identified service tooling.
- **Service activity audit reconciliation**: monthly reconciliation of vendor visits with PAM session records and pump shim logs.
- **Video surveillance** at pump location, retained 90 days.

### 4.2 Reference to Compensating Controls Playbook

Paper §3.3 Table 3, "Service-mode password disclosed" constraint. Pattern C described in §3.4.

### 4.3 How the control addresses the threat

- The publicly-disclosed credential alone is insufficient for service-mode access; the shim's TOTP gate must also be passed.
- TOTP factor is bound to individual technician identity, restoring per-user attribution and addressing Repudiation.
- Session recording at the shim provides evidentiary capability for post-hoc analysis of service activity.
- The supporting policy controls reduce the population of actors with even the opportunity to attempt the attack.

### 4.4 Why this control is appropriate

- **Equivalent or superior protection.** The shim provides authentication and audit at the physical port — capabilities the pump itself does not have. The combined posture is approximately equivalent to a device with native MFA and audit logging.
- **Independence.** The control is implemented in a separate hardware element; its security properties do not depend on the pump.
- **Proportionality.** Pump is at CRITICAL MDRS tier; the control is the strongest physical-access control reasonably achievable given the constraint.
- **Auditability.** Shim session logs, badge correlation, video, vendor-escort records — multiple corroborating sources support audit.

### 4.5 Implementation references

- Pattern C reference design: `mfa-shim/prototype/`
- Pilot deployment: 12 pumps in ICU bed positions 1A-12A (separate inventory record)
- TOTP factor binding: technician identity attested via clinical engineering badge system
- Session log retention: 90 days online at the shim, exported nightly to SIEM with 7-year archive
- Tamper-evident seal: serialised seal applied at deployment; monthly inspection logged in EAM
- Break-glass procedure: BG-PUMP-001 (clinical engineering on-call notification + InfoSec on-call concurrent)
- Video surveillance: ICU camera coverage records device locations; 90-day retention

## 5. Residual risk evaluation (ISO 14971 cl.8)

### 5.1 Risk after control deployment

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood (residual) | Low | TOTP factor required in addition to disclosed PIN; population of actors with both proximity and TOTP is small and audited. |
| Severity (residual) | High | Unchanged — the harm potential if compromise occurs remains the same. |
| Detectability (residual) | Easy | Shim logs every session; video surveillance provides corroboration; audit reconciliation surfaces discrepancies. |

### 5.2 Residual risk acceptability

**Acceptable for the pilot deployment** under the legacy device research programme criteria (LMD-RISK-2026-001 and the research-artifact addendum LMD-RISK-2026-001A). The pilot is time-bounded (12 months) with quarterly review.

For broader deployment, the control's status as a research artifact rather than a cleared medical device is the governing constraint. See `mfa-shim/FDA-CONSIDERATIONS.md` for the regulatory analysis of broader deployment paths.

### 5.3 Risk acceptance authority

CISO (K. Williams), Director of Clinical Engineering (M. Robinson), and Chief Medical Information Officer (Dr T. Aiyer) jointly, dated 2026-04-10. Pilot scope is signed off by the institutional research and quality improvement committee.

## 6. Effectiveness rating

**Medium for the pilot deployment.** Pattern C addresses the primary disclosed-credential exposure but is itself a research-grade artifact. Validation:

- Test harness scenario `test-harness/attacker/05-eop-default-credential.py` confirms Pattern C prevents service-port credential abuse when the shim is operational and tamper-evident sealing is intact.
- Pilot operations review at 90 days will assess shim reliability, technician compliance with TOTP workflow, and any clinical-workflow impact.

A re-rating to High is contingent on (a) production hardware procurement and (b) FDA regulatory analysis confirming that inline insertion does not constitute a device modification requiring re-clearance.

## 7. Normative references

- ISO 14971:2019, cl.7.4 (Risk control measures)
- ISO 14971:2019, cl.8 (Residual risk evaluation)
- AAMI TIR57:2016, §6.3
- AAMI TIR97, §6.2 and §7 (Postmarket residual risk)
- HIPAA Security Rule, 45 CFR §164.310(b) (Workstation use — physical safeguards)
- HIPAA Security Rule, 45 CFR §164.312(d) (Person/entity authentication)
- HIPAA Security Rule, 45 CFR §164.312(b) (Audit controls)
- FDA 2023 Cybersecurity Guidance, §VII.A.4 and §VII.B (Postmarket compensating measures)
- NIST SP 800-82r3, IA-2, PE-3 (Physical access control)
- NIST SP 800-153 (Wireless local area network security)
- HSCC HIC-MaLTS (2023), Practice 5.4 (Physical security)

## 8. Approval and review

| Field | Value |
|---|---|
| Author | S. Patel, Senior Clinical Engineer |
| Reviewer (Clinical Engineering) | M. Robinson |
| Reviewer (InfoSec) | J. Chen |
| Approver (CISO) | K. Williams |
| Approver (Director of Clinical Engineering) | M. Robinson |
| Approver (CMIO) | Dr T. Aiyer |
| Approval date | 2026-04-10 |
| Effective date | 2026-05-15 (after pilot site preparation) |
| Next scheduled review | 2026-08-15 (90-day pilot review), then quarterly |
| Trigger conditions for early review | Shim component failure; tamper-evident seal violation; vendor advisory; FDA clarification on inline-device classification |

## 9. Linked records

| Record type | Reference |
|---|---|
| STRIDE-HC threat model | stride-hc-templates/examples/infusion-pump.md |
| MDS² disclosure | ExampleMed-IP3.2-MDS2-2024 |
| Pattern C reference design | mfa-shim/ |
| FDA regulatory analysis | mfa-shim/FDA-CONSIDERATIONS.md |
| Pilot operations review (90-day) | scheduled 2026-08-15 |
| Related CJRs | CJR-EMPump-001-MFA (Pattern A network-side), CJR-EMPump-002-Encryption |
| Test harness output | test-harness/results/empump-v32-2026-q1.csv |

## 10. Change log

| Version | Date | Author | Change summary |
|---|---|---|---|
| 1.0 | 2026-04-10 | S. Patel | Initial CJR for service-port PIN exposure on ExampleMed Volumetric Infusion Pump v3.2; introduces Pattern C compensating control under research-artifact pilot |
