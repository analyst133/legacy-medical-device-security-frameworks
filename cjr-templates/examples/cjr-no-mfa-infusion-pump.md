# Control Justification Record (CJR)

**CJR-ID:** CJR-EMPump-001-MFA
**Status:** Approved
**Version:** 1.0

## 1. Device identification

| Field | Value |
|---|---|
| Device name and model | ExampleMed Volumetric Infusion Pump v3.2 |
| Manufacturer | ExampleMed Inc. |
| Device class (FDA) | Class II |
| Device archetype | Archetype 2 (embedded RTOS legacy — VxWorks 6.9) |
| MDS² reference | ExampleMed-IP3.2-MDS2-2024 |
| Asset inventory IDs | Asset register reference: pump-vlan-volumetric-ip32 |
| Deployment count | 240 units across ICU and oncology |
| Linked STRIDE-HC threat model | `stride-hc-templates/examples/infusion-pump.md` |
| Current MDRS score and tier | 8.175 → CRITICAL |

## 2. Standard control and constraint

### 2.1 Standard control that cannot be applied

Multi-factor authentication for administrative access to the device management interface.

### 2.2 Constraint preventing standard control

**MFA not supported.** The device exposes a management interface on TCP/8080 protected only by a hardcoded service-mode password documented in the vendor service manual. The device firmware does not support per-user accounts, MFA, or third-party authentication delegation.

### 2.3 Constraint detail

ExampleMed Inc. has confirmed in vendor advisory ExampleMed-2024-03 that MFA support is not on the firmware roadmap for the v3.2 model due to the FDA clearance constraints associated with introducing user authentication and per-user accounting. Modifying the firmware to support MFA would require submission as a special 510(k) and is not currently planned by the vendor. The vendor recommends compensating with upstream network controls and access management.

The constraint is technical (the device cannot be modified to support MFA) and regulatory (vendor cannot ship a modified firmware without re-clearance).

## 3. Threat addressed

### 3.1 STRIDE-HC mapping

- **S** — Spoofing (legitimate-credential abuse by unauthorised user)
- **R** — Repudiation (no per-user logging on device)
- **E** — Elevation of Privilege (attacker with credential gains administrative control)

### 3.2 Threat scenario summary

**Network-attacker scenarios:**
- Default credential exploitation via the management interface (the credential is documented in publicly available service manuals).
- Lateral movement to peer pumps after credential reuse on a shared service account.

**Physical/insider-attacker scenarios:**
- Service-mode credential abuse via service port using the same documented credential.
- Vendor-impersonation social engineering in which a non-vendor actor claiming to be vendor service uses the documented credential.

### 3.3 Initial risk assessment (pre-control)

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood | High | Public disclosure of service credential places this in the high-likelihood band; required attacker capability is low. |
| Severity | High | Successful exploitation enables therapy parameter modification on a Class II infusion device — direct patient-safety implication. |
| Detectability | Difficult | The device generates no authentication audit log; detection depends entirely on upstream network or physical observation. |

## 4. Compensating control(s) selected

### 4.1 Control description

**Pattern A — Upstream PAM (privileged access management) gateway.** A privileged-access-management appliance brokers all network connections to the pump management interface. Users authenticate to the PAM with individual MFA. PAM retrieves the hardcoded service credential from a vault and connects to the pump on the user's behalf. All sessions are recorded with full keystroke and screen capture.

### 4.2 Reference to Compensating Controls Playbook

Paper §3.2 Table 2, "MFA not supported" constraint. Pattern A described in §3.4.

### 4.3 How the control addresses the threat

- The hardcoded credential never leaves the vault, eliminating network discovery as an attack path.
- The pump management interface is reachable only from the PAM gateway IP via network ACL on the pump VLAN; the credential becomes operationally useless to any actor not authenticated at PAM.
- PAM enforces individual MFA before bridging the connection, restoring per-user attribution that the device lacks.
- Session recording provides post-hoc attribution that addresses the Repudiation residual.

### 4.4 Why this control is appropriate

- **Equivalent or superior protection.** MFA is enforced at the PAM gateway. From the user perspective the authentication experience is equivalent to native MFA on the pump. Network-attacker exploitation of the hardcoded credential is no longer possible without first compromising PAM and a user's MFA factor.
- **Independence.** The control does not depend on any pump capability; it is implemented entirely upstream in network architecture.
- **Proportionality.** The pump's MDRS tier is CRITICAL; PAM with MFA is the strongest network-layer compensating control available for this constraint, appropriate to the tier.
- **Auditability.** All sessions logged at the PAM with full keystroke or screen capture. Logs retained 90 days online, 7 years archived. Compliant with HIPAA §164.312(b) (audit controls), ISO 14971 cl.7.4, AAMI TIR57 §6.3.

### 4.5 Implementation references

- PAM platform: CyberArk PSM v12.x (organisational standard)
- Pump VLAN ACL: inbound permit only from `pam-gateway-ip/32` to TCP/8080 on pump VLAN; deny-all default
- PAM session recording retention: 90 days online, 7 years archived (HIPAA retention)
- MFA factor: Duo Push or hardware token; biometric-based factors not currently used in clinical engineering workflows
- Vault rotation: vault-side rotation of hardcoded credential is not possible (device firmware does not accept rotation); the vault stores the static credential and rotation is reconsidered annually with the vendor
- Service request workflow: PAM access requires approved change request from clinical engineering; emergency break-glass available with elevated audit and 4-hour CISO review

## 5. Residual risk evaluation (ISO 14971 cl.8)

### 5.1 Risk after control deployment

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood (residual) | Low | Credential no longer discoverable via network; physical service-port path addressed by separate CJR (CJR-EMPump-003-ServicePort). |
| Severity (residual) | High | Unchanged. The harm potential if exploitation occurs (mid-therapy parameter change) remains the same; the control reduces likelihood, not severity. |
| Detectability (residual) | Easy | PAM session logging provides full visibility into all administrative sessions, including the user identity and full session content. |

### 5.2 Residual risk acceptability

**Acceptable** under the organisation's risk acceptance criteria for legacy device compensating controls (LMD-RISK-2026-001). The criteria require: residual likelihood ≤ Low, validated detection capability, and quarterly monitoring review. All criteria met.

### 5.3 Risk acceptance authority

CISO (K. Williams), with CMO concurrence under standing approval for the legacy medical device programme. Reference: LMD-RISK-2026-001, dated 2026-02-15.

## 6. Effectiveness rating

**High.** Validated through:

- Annual penetration test (Vendor: Pen Test Co, Report PT-2026-Q1-014) confirmed PAM enforcement is effective; no bypass identified.
- Test harness scenario `test-harness/attacker/05-eop-default-credential.py` confirms compensating control prevents credential discovery and exploitation on the network when the PAM control profile is enabled.

## 7. Normative references

- ISO 14971:2019, cl.7.4 (Implementation of risk control measures)
- ISO 14971:2019, cl.8 (Evaluation of overall residual risk acceptability)
- AAMI TIR57:2016, §6.3 (Security risk control measures)
- AAMI TIR97, §6.2 (Postmarket security risk control)
- HIPAA Security Rule, 45 CFR §164.308(a)(1)(ii)(B) (Risk management)
- HIPAA Security Rule, 45 CFR §164.312(d) (Person or entity authentication)
- HIPAA Security Rule, 45 CFR §164.312(b) (Audit controls)
- FDA 2023 Cybersecurity Guidance, §VII.A.4 (Authentication)
- NIST SP 800-82r3, IA-2 (Identification and Authentication)
- PCI-DSS v4.0, Req 8.4 (Multi-factor authentication)
- HSCC HIC-MaLTS (2023), Practice 5.2 (Privileged access management)

## 8. Approval and review

| Field | Value |
|---|---|
| Author | S. Patel, Senior Clinical Engineer |
| Reviewer (Clinical Engineering) | M. Robinson, Director of Clinical Engineering |
| Reviewer (InfoSec) | J. Chen, Lead Security Architect |
| Approver (CISO) | K. Williams |
| Approver (Director of Clinical Engineering) | M. Robinson |
| Approval date | 2026-04-10 |
| Effective date | 2026-05-01 |
| Next scheduled review | 2027-04-10 |
| Trigger conditions for early review | ExampleMed Inc. security advisory; new VxWorks 6.9 CVE; PAM platform end-of-support; pump VLAN architecture change; loss of MFA service availability |

## 9. Linked records

| Record type | Reference |
|---|---|
| STRIDE-HC threat model | stride-hc-templates/examples/infusion-pump.md |
| MDS² disclosure | ExampleMed-IP3.2-MDS2-2024 |
| Penetration test report | PT-2026-Q1-014 |
| Test harness output | test-harness/results/empump-v32-2026-q1.csv |
| Related CJRs | CJR-EMPump-002-Encryption, CJR-EMPump-003-ServicePort |

## 10. Change log

| Version | Date | Author | Change summary |
|---|---|---|---|
| 1.0 | 2026-04-10 | S. Patel | Initial CJR for MFA constraint on ExampleMed Volumetric Infusion Pump v3.2 |
