# Control Justification Record (CJR)

**CJR-ID:** [unique identifier, e.g., CJR-EMPump-001-MFA]
**Status:** [Draft / Approved / Under Review / Retired]
**Version:** 1.0

> **Template**: replace bracketed text with device- and control-specific content. This template is suitable for direct use in HIPAA Security Rule risk analysis, ISO 14971 risk management files, AAMI TIR57 security risk records, and FDA 524B postmarket evidence packs.

## 1. Device identification

| Field | Value |
|---|---|
| Device name and model | [e.g., ExampleMed Volumetric Infusion Pump v3.2] |
| Manufacturer | [e.g., ExampleMed Inc.] |
| Device class (FDA / EU MDR) | [e.g., Class II] |
| Device archetype | [Archetype 1 (general-purpose-OS legacy) / Archetype 2 (embedded RTOS legacy)] |
| MDS² reference | [Manufacturer Disclosure Statement document ID] |
| Asset inventory IDs | [list of asset tags or serial numbers, or "see linked register"] |
| Deployment count | [N units] |
| Linked STRIDE-HC threat model | [reference to threat-model document] |
| Current MDRS score and tier | [e.g., 8.175 → CRITICAL] |

## 2. Standard control and constraint

### 2.1 Standard control that cannot be applied

[State the standard control that would normally be deployed — for example, "Multi-factor authentication for administrative access".]

### 2.2 Constraint preventing standard control

[State the specific constraint. Choose from the Playbook constraint categories or extend with device-specific constraints. Examples:]

- [ ] Multi-factor authentication not supported by device
- [ ] No encryption of data in transit supported
- [ ] No patching possible (vendor end-of-life or FDA clearance constraint)
- [ ] Shared or hardcoded credentials (network-side)
- [ ] No audit logging capability
- [ ] Legacy general-purpose OS (Archetype 1)
- [ ] Legacy embedded RTOS (Archetype 2)
- [ ] Hardcoded service-port credential (RS-232, USB, proprietary)
- [ ] USB and removable media interfaces
- [ ] PHI display in shared / observable environment
- [ ] Device substitution risk
- [ ] Vendor field-service unsupervised access
- [ ] Service-mode password disclosed in technical manual or leaked
- [ ] Proximity wireless on legacy device
- [ ] Other: [describe]

### 2.3 Constraint detail

[Describe the constraint precisely. State why the standard control cannot be applied — technical limitation, regulatory constraint, vendor policy, FDA clearance dependency, or operational impact. Cite vendor documentation, MDS² statement, or technical analysis.]

## 3. Threat addressed

### 3.1 STRIDE-HC mapping

[Identify which STRIDE-HC categories this constraint exposes. Multiple categories may apply.]

- [ ] **S** — Spoofing
- [ ] **T** — Tampering
- [ ] **R** — Repudiation
- [ ] **I** — Information Disclosure
- [ ] **D** — Denial of Service
- [ ] **E** — Elevation of Privilege

### 3.2 Threat scenario summary

[State the specific threat scenarios that the constraint exposes, drawing from the STRIDE-HC threat model and scenario library. Include both network-attacker and physical/insider-attacker scenarios where applicable.]

### 3.3 Initial risk assessment (pre-control)

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood | [Low / Medium / High] | [reasoning] |
| Severity | [Low / Medium / High] | [reasoning, referencing harm types per ISO 14971 cl.5] |
| Detectability | [Easy / Moderate / Difficult] | [reasoning] |

## 4. Compensating control(s) selected

### 4.1 Control description

[Describe the compensating control(s) selected. Be specific: name the technology, configuration, and operational practices that constitute the control.]

### 4.2 Reference to Compensating Controls Playbook

[Cite the relevant entry or entries from paper Tables 2 (network exposure) or 3 (physical access).]

### 4.3 How the control addresses the threat

[Explain the mechanism by which the compensating control mitigates the identified threat scenarios. Address each scenario from §3.2 explicitly.]

### 4.4 Why this control is appropriate

[Per the Playbook design principles:]

- **Equivalent or superior protection**: [demonstrate that the compensating control addresses the threat at least as well as the standard control would have]
- **Independence**: [confirm that the compensating control does not depend on the same missing capability that caused the original constraint]
- **Proportionality**: [confirm that control intensity is appropriate to the device's MDRS tier]
- **Auditability**: [identify the normative reference(s) supporting this selection]

### 4.5 Implementation references

[List the specific technical references — IPS signatures, PAM configuration, vendor part numbers, software versions, configuration files, network diagrams. This section is the operational link to actual deployment.]

## 5. Residual risk evaluation (ISO 14971 cl.8)

### 5.1 Risk after control deployment

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood (residual) | [Low / Medium / High] | [reasoning, referencing the specific control mechanism] |
| Severity (residual) | [Low / Medium / High] | [usually unchanged unless control changes consequence space] |
| Detectability (residual) | [Easy / Moderate / Difficult] | [referencing detection capability provided by the control or by Framework V monitoring] |

### 5.2 Residual risk acceptability

[State whether residual risk is **acceptable** under the organisation's risk acceptance criteria, with reasoning. If acceptable, identify the criteria reference. If not acceptable, identify additional measures required.]

### 5.3 Risk acceptance authority

[For residual risks above defined acceptance thresholds, identify the executive who has accepted the risk in writing — typically CISO, with concurrence from Chief Medical Officer for clinical-impact-relevant risks.]

## 6. Effectiveness rating

[Per paper §3.5, assign a Control Effectiveness Rating:]

- [ ] **High** — Equivalent protection to the standard control; validated through penetration testing or empirical harness evaluation.
- [ ] **Medium** — Partially addresses the threat; residual risk elevated but manageable.
- [ ] **Low** — Minimal mitigation; formal risk acceptance per ISO 14971 cl.8 and executive escalation required.

**Validation evidence:** [cite the validation method — penetration test report, harness output, design review minutes]

## 7. Normative references

[Cite the standards, guidance, and regulatory provisions that justify this selection. Format as a list. Examples:]

- ISO 14971:2019, clause 7 (Risk control measures)
- ISO 14971:2019, clause 8 (Evaluation of overall residual risk)
- AAMI TIR57:2016, section 6 (Security risk control)
- AAMI TIR97, section 6 (Postmarket security risk control)
- HIPAA Security Rule, 45 CFR §164.308(a)(1)(ii)(B) (Risk management)
- HIPAA Security Rule, 45 CFR §164.310(b) (Workstation use)
- FDA 2023 Cybersecurity Guidance, §VII (Postmarket cybersecurity)
- NIST SP 800-82r3, [specific control identifier]
- IEC 62443-3-3, [specific security level requirement]
- HSCC HIC-MaLTS (2023), [specific section]

## 8. Approval and review

| Field | Value |
|---|---|
| Author | [Name, role, e.g., Senior Clinical Engineer] |
| Reviewer (Clinical Engineering) | [Name, role] |
| Reviewer (InfoSec) | [Name, role] |
| Approver (CISO) | [Name] |
| Approver (Director of Clinical Engineering) | [Name] |
| Approval date | [YYYY-MM-DD] |
| Effective date | [YYYY-MM-DD] |
| Next scheduled review | [YYYY-MM-DD — annual, or earlier if triggered] |
| Trigger conditions for early review | [Vendor security advisory; new CVE for device firmware; material network architecture change; loss of compensating-control supplier; significant clinical workflow change] |

## 9. Linked records

| Record type | Reference |
|---|---|
| STRIDE-HC threat model | [filename or system reference] |
| MDS² disclosure | [reference] |
| Vendor security advisories | [reference if applicable] |
| Penetration test report | [reference if applicable] |
| Test harness output | [reference if applicable] |
| Predecessor CJR (if revised) | [CJR-ID, version] |
| Related CJRs (other constraints, same device) | [list of CJR-IDs] |

## 10. Change log

| Version | Date | Author | Change summary |
|---|---|---|---|
| 1.0 | YYYY-MM-DD | [author] | Initial CJR for [constraint] on [device] |
