# Control Justification Record (CJR)

**CJR-ID:** CJR-PACS-002-DICOMTLS
**Status:** Approved
**Version:** 1.0

## 1. Device identification

| Field | Value |
|---|---|
| Device name and model | Vendor X PACS Reading Station v8.4 |
| Manufacturer | Vendor X |
| Device class (FDA) | Class II (image display application) |
| Device archetype | Archetype 1 (general-purpose-OS legacy — Windows 7 Pro) |
| MDS² reference | VendorX-PACS-RS-v8.4-MDS2-2023 |
| Asset inventory IDs | Asset register: pacs-reading-fleet-v84 |
| Deployment count | 38 reading stations |
| Linked STRIDE-HC threat model | `stride-hc-templates/examples/pacs-workstation.md` |
| Current MDRS score and tier | 4.750 → MEDIUM |

## 2. Standard control and constraint

### 2.1 Standard control that cannot be applied

TLS encryption for all DICOM communication between modalities and the PACS reading station, and between the reading station and PACS server.

### 2.2 Constraint preventing standard control

**No encryption (data in transit)** — partial constraint. The reading station supports DICOM TLS in principle but the constraint applies to legacy modalities (CT, MR, X-ray) deployed in the facility that do not support TLS, and to legacy reporting workflows that depend on cleartext DICOM port 104.

### 2.3 Constraint detail

Three of seven imaging modality classes deployed in the facility do not support DICOM TLS:

- Two CT scanners (Vendor Y, model deployed 2014) — TLS not in firmware.
- One MR system (Vendor Z, model deployed 2013) — TLS available only in vendor's premium service tier, not licensed.
- Two general radiology rooms (Vendor X, deployed 2015) — TLS in firmware but configuration tooling unavailable to facility (vendor service-only).

The reading station itself supports TLS, but enforcing TLS-only would prevent image reception from these modalities, halting clinical operations. Vendor engagement is in progress for each constraint, but resolution timelines extend beyond the 90-day MEDIUM-tier remediation window.

## 3. Threat addressed

### 3.1 STRIDE-HC mapping

- **I** — Information Disclosure (PHI in cleartext on the network)
- **T** — Tampering (image manipulation in transit, e.g., CT-GAN-class attacks per Mirsky et al. 2019)

### 3.2 Threat scenario summary

**Network-attacker scenarios:**
- PHI interception on shared imaging network segment via passive monitoring on a compromised host.
- Image manipulation in transit using deep-learning techniques to inject or remove diagnostic findings.
- ARP cache poisoning to redirect cleartext DICOM through an attacker-controlled host.

### 3.3 Initial risk assessment (pre-control)

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood | Medium | Imaging network is segmented from corporate, but the facility has had vendor-laptop incidents documented in incident review history. |
| Severity | High | PHI breach has regulatory consequences; image manipulation has direct clinical-decision implications. |
| Detectability | Difficult | Cleartext interception leaves no application-layer trace. |

## 4. Compensating control(s) selected

### 4.1 Control description

A combination of network-layer and protocol-layer controls:

1. **Dedicated imaging VLAN with restrictive ACLs.** All modalities and the PACS reading station are placed in a Zone 2 (Diagnostic Imaging) VLAN per the five-zone segmentation model. Inbound and outbound ACLs allow only DICOM source–destination pairs; lateral traffic is blocked.
2. **DICOM-aware proxy gateway.** All DICOM transfers between modalities and the reading station traverse a DICOM-aware proxy that re-encrypts to TLS on the reading-station-facing leg, providing TLS protection on the busiest segment.
3. **Network DLP at zone edge.** A DLP appliance at the Zone 2 to Zone 3 boundary inspects DICOM PHI fields and alerts on anomalous bulk transfers.
4. **TLS deprecation roadmap.** Each non-TLS modality has a documented vendor engagement record, target replacement or upgrade date, and quarterly status review.

### 4.2 Reference to Compensating Controls Playbook

Paper §3.2 Table 2, "No encryption (data in transit)" constraint.

### 4.3 How the control addresses the threat

- VLAN isolation reduces the population of hosts that could mount a passive interception attack from "any host on the corporate network" to "any host on the dedicated imaging VLAN" — in practice, the modalities and reading stations themselves.
- The DICOM proxy provides TLS protection on the segment carrying the highest volume of PHI (proxy → reading station and proxy → PACS server). The cleartext segment (modality → proxy) is co-located within a tightly-controlled zone.
- DLP detection provides defence-in-depth against the bulk-export scenario.
- The roadmap provides a path to constraint resolution rather than indefinite acceptance.

### 4.4 Why this control is appropriate

- **Equivalent or superior protection.** End-to-end TLS would eliminate cleartext PHI on all segments. The compensating combination eliminates it on the longest, busiest segments and minimises exposure on the residual segment.
- **Independence.** The control does not rely on TLS support in the constrained modalities.
- **Proportionality.** PACS reading station is at MEDIUM tier; this combined control is appropriate.
- **Auditability.** DLP logs PHI events; proxy logs all DICOM transactions.

### 4.5 Implementation references

- Imaging VLAN: `vlan-imaging-zone2`, ACL `imaging-zone2-acl`
- DICOM proxy: Vendor Q DICOM Gateway v3.x, deployed in the imaging core
- DLP: Symantec DLP for DICOM, configured for PHI content matching
- TLS deprecation roadmap: tracked in clinical engineering project register; quarterly review by InfoSec / Radiology IT
- Modality work plan:
  - CT-1, CT-2 (Vendor Y): vendor replacement scheduled Q3 2027
  - MR-1 (Vendor Z): premium-tier TLS licence procurement in progress, target Q4 2026
  - GR-1, GR-2 (Vendor X): vendor service engagement Q2 2026

## 5. Residual risk evaluation (ISO 14971 cl.8)

### 5.1 Risk after control deployment

| Dimension | Score | Rationale |
|---|---|---|
| Likelihood (residual) | Low | Cleartext segment is short and well-controlled; network DLP detects anomaly. |
| Severity (residual) | High | Unchanged. |
| Detectability (residual) | Moderate | DLP detects unusual patterns; targeted single-image interception remains difficult to detect. |

### 5.2 Residual risk acceptability

**Acceptable** with two conditions: (1) the deprecation roadmap remains active and is tracked at quarterly InfoSec / Radiology IT joint review; (2) any new modality deployment must support DICOM TLS at procurement. Conditions documented in the procurement standard PROC-IMG-2026-001.

### 5.3 Risk acceptance authority

CISO (K. Williams) with Radiology Director (Dr R. Suzuki) concurrence, dated 2026-03-15.

## 6. Effectiveness rating

**Medium.** Cleartext PHI persists on the modality-to-proxy segment. Penetration test (PT-2026-Q1-009) confirmed that interception in the dedicated imaging VLAN requires existing host compromise; no bypass of the VLAN ACL identified. DLP false-positive rate is acceptable (3.2% over Q1 2026); detection rate for synthetic bulk-export tests was 100%.

## 7. Normative references

- ISO 14971:2019, cl.7.4
- AAMI TIR57:2016, §6.3
- HIPAA Security Rule, 45 CFR §164.312(a)(2)(iv) (Encryption and decryption — addressable)
- HIPAA Security Rule, 45 CFR §164.312(e)(1) (Transmission security)
- FDA 2023 Cybersecurity Guidance, §VII.A.3 (Authenticity, integrity, confidentiality)
- NIST SP 800-111 (Storage encryption)
- DICOM Security Profiles (PS3.15 – Security and System Management Profiles)
- HSCC HIC-MaLTS (2023), Practice 6.4 (Imaging-specific controls)

## 8. Approval and review

| Field | Value |
|---|---|
| Author | A. Nakamura, Senior Network Engineer (Imaging) |
| Reviewer (Clinical Engineering) | M. Robinson |
| Reviewer (InfoSec) | J. Chen |
| Approver (CISO) | K. Williams |
| Approver (Radiology Director) | Dr R. Suzuki |
| Approval date | 2026-03-15 |
| Effective date | 2026-04-01 |
| Next scheduled review | 2026-09-15 (semi-annual due to active deprecation roadmap) |
| Trigger conditions for early review | Modality vendor security advisory; modality replacement; DLP false-positive rate exceeds 5%; new DICOM TLS CVE |

## 9. Linked records

| Record type | Reference |
|---|---|
| STRIDE-HC threat model | stride-hc-templates/examples/pacs-workstation.md |
| MDS² disclosure | VendorX-PACS-RS-v8.4-MDS2-2023 |
| Penetration test report | PT-2026-Q1-009 |
| Procurement standard | PROC-IMG-2026-001 |
| Related CJRs | CJR-PACS-001-Win7Patching, CJR-PACS-003-USBControl |

## 10. Change log

| Version | Date | Author | Change summary |
|---|---|---|---|
| 1.0 | 2026-03-15 | A. Nakamura | Initial CJR for cleartext DICOM constraint on PACS reading fleet |
