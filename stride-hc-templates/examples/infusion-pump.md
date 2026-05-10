# STRIDE-HC Threat Model: ExampleMed Volumetric Infusion Pump v3.2

> Worked example for paper §4.5 — large-volume infusion pump representative of **Archetype 2 (embedded RTOS legacy)**.

## 1. Device profile

| Field | Value |
|---|---|
| Device name and model | ExampleMed Volumetric Infusion Pump v3.2 |
| Manufacturer | ExampleMed Inc. |
| Device class (FDA) | Class II |
| UMDNS code | 16495 |
| GMDN code | 35143 |
| MDS² reference | ExampleMed-IP3.2-MDS2-2024 |
| **Archetype** | **Archetype 2 (embedded RTOS legacy)** |
| Operating system | VxWorks 6.9 (EOL — no further patches) |
| Networking | 100Mbit Ethernet, HL7 v2 over TCP/2575, no TLS |
| Authentication | Hardcoded service-mode credential; no per-user login |
| Patching | Manufacturer no longer issues patches; FDA clearance limits modification |
| Audit logging | None on device; only at upstream nursing station |
| Physical interfaces | RS-232 service port; USB-A (firmware update); Bluetooth (paired display) |
| Deployment | 240 units across ICU and oncology |
| Clinical use | Continuous medication infusion |

## 2. STRIDE-HC threat scenarios

### S — Spoofing (CAW = 1.2)

**Network-attacker scenarios:**
- ARP cache poisoning to redirect device traffic
- Forged HL7 messages from spoofed nursing station
- Rogue device impersonation on shared VLAN

**Physical / insider-attacker scenarios:**
- Substituted device with cloned identifier (during scheduled service window)
- Vendor-impersonation social engineering at device location
- Cloned RFID/NFC token used for proximity authentication of paired display

**Detection methods (Framework V):**
- Passive device fingerprinting (network sensor with longitudinal store)
- Badge-correlation analytics (vendor service activity vs. work order)
- Network UEBA peer-set anomaly

**Compensating controls (Framework I):**
- 802.1X port-based access control with MAC allowlisting
- Tamper-evident asset tags with serialised identifier
- Vendor-escort policy with mandatory clinical engineering accompaniment

**CCD coverage assessment:** Partial — physical fingerprinting and badge correlation cover most scenarios; vendor impersonation requires improved staff training.

---

### T — Tampering (CAW = 1.1)

**Network-attacker scenarios:**
- Unauthorised firmware push from compromised vendor channel
- Configuration tampering via unauthenticated management interface

**Physical / insider-attacker scenarios:**
- Firmware injection via USB-A during service
- Configuration tamper via RS-232 service port using leaked service-mode PIN
- Physical replacement of vendor-supplied SD card during maintenance

**Detection methods (Framework V):**
- Network-adjacent file integrity inferred via configuration management traffic
- Configuration version comparison via management API
- Tamper-evident seal inspection (monthly cadence)

**Compensating controls (Framework I):**
- Logical USB disablement via vendor service mode
- Physical port blockers (epoxy) on unused ports
- Inline MFA shim (Pattern C) at RS-232 service port — gated by TOTP
- Tamper-evident sealing with serialised seals on service-port covers

**CCD coverage assessment:** Partial — Pattern C addresses primary physical vector; firmware push is mitigated by IPS but not eliminated.

---

### R — Repudiation (CAW = 0.9)

**Network-attacker scenarios:**
- Unattributable configuration changes via shared service account
- Untraceable data access via cleartext HL7

**Physical / insider-attacker scenarios:**
- Service-mode access by unidentified technician
- Bedside infusion-rate changes by unidentified clinician
- PHI capture by mobile-phone photography

**Detection methods (Framework V):**
- Network PCAP with 90-day retention
- Syslog proxy capturing HL7 transactions
- Physical badge access logs correlated to device location and service activity
- UEBA behavioural baseline of clinical interaction patterns

**Compensating controls (Framework I):**
- Network-level logging pipeline (compensates for absent device logging)
- PAW with individual auth upstream (Pattern A) for any administrative function
- Session recording at the Pattern C MFA shim
- Badge-to-device correlation analytics

**CCD coverage assessment:** Partial — strong network and physical correlation, but bedside parameter changes outside service mode remain attributable only to "the assigned nurse" rather than to a specific user action.

---

### I — Information Disclosure (CAW = 1.2)

**Network-attacker scenarios:**
- PHI interception on shared network segment (cleartext HL7 v2 carries patient identifier and dose data)
- Unprotected data export via management interface

**Physical / insider-attacker scenarios:**
- PHI display photographed in shared environment (multi-occupancy room)
- Bulk PHI export to USB at service port
- Eavesdropping on Bluetooth pairing with paired display

**Detection methods (Framework V):**
- Protocol-aware IDS flagging cleartext PHI in HL7 traffic
- Display privacy filter audit
- WIDS for proximity wireless interaction
- DLP at network gateway

**Compensating controls (Framework I):**
- IPSec tunnel encapsulating cleartext HL7 to nursing station
- VLAN isolation on dedicated infusion-pump VLAN
- Privacy filters on displays in multi-occupancy rooms
- PHI minimisation: pump display configured to show only patient initials and last 4 digits of MRN
- Service-port USB disablement via vendor service mode

**CCD coverage assessment:** Full — comprehensive controls validated annually via penetration test; protocol-aware IDS deployed.

---

### D — Denial of Service (CAW = 1.5)

**Network-attacker scenarios:**
- Network flooding disrupts HL7 communication, interrupting dose updates
- Targeted protocol-parser crash (URGENT/11-class CVE in VxWorks IPnet stack)
- Resource exhaustion via malformed HL7 messages

**Physical / insider-attacker scenarios:**
- Power or network cable disconnection at device location
- Physical destruction or theft (rare but documented in agency-staff incidents)
- Service-mode reset rendering pump unavailable mid-therapy

**Detection methods (Framework V):**
- Availability monitoring with alerting (sub-30-second alarm)
- Device location video surveillance
- Environmental monitoring (power consumption anomaly via building management system)

**Compensating controls (Framework I):**
- Dedicated VLAN with QoS priority (highest tier in five-zone segmentation)
- Rate limiting upstream of pump VLAN
- Redundant network paths
- Uptime SLA contracted with ExampleMed Inc.
- Backup pump staging in each unit
- Physical access controls on patient room

**CCD coverage assessment:** Partial — strong network-side controls; physical destruction is mitigated by surveillance and backup staging but not prevented.

---

### E — Elevation of Privilege (CAW = 1.1)

**Network-attacker scenarios:**
- Default credential exploitation via management interface (mitigated by Pattern A)
- Lateral movement to nursing station via compromised pump

**Physical / insider-attacker scenarios:**
- Service-mode credential abuse via RS-232 (mitigated by Pattern C)
- Vendor-service-tool privilege abuse (vendor laptop has documented elevated privileges)
- Unauthorised access to administrative menus via undocumented key sequence (disclosed in leaked service manual)

**Detection methods (Framework V):**
- IDS/IPS with VxWorks IPnet stack signatures
- Privilege escalation monitoring at upstream PAM
- Behavioural analytics for HL7 anomaly indicating exploited pump
- Service-port session recording

**Compensating controls (Framework I):**
- Virtual patching via IPS for known VxWorks CVEs
- Network microsegmentation (Zone 0 dedicated VLAN)
- Inline MFA shim (Pattern C) at service port — addresses physical EoP
- PAM upstream (Pattern A) — addresses network EoP
- Vendor service activity supervised by clinical engineering

**CCD coverage assessment:** Partial — Patterns A and C jointly cover primary EoP vectors; vendor tooling remains a residual risk requiring contractual SLA improvements.

## 3. MDRS-relevant outputs

Coverage summary for CCD calculation:

| Category | Coverage |
|---|---|
| S | Partial |
| T | Partial |
| R | Partial |
| I | Full |
| D | Partial |
| E | Partial |

**Five categories partial, one full** → CCD score in the 7–8 band → **CCD = 7**.

This feeds the MDRS calculation: with `CIS=9.0, ES=7.5, DCI=8.0, NEF=8.0, CCD=7.0`, the composite is **8.175** → **CRITICAL** tier (paper Table 7).

## 4. Document control

| Field | Value |
|---|---|
| Author | Clinical Engineering / InfoSec joint authoring |
| Reviewer | CISO and Director of Clinical Engineering |
| Approval date | 2026-04-10 |
| Next review | 2027-04-10 |
| Linked CJRs | CJR-EMPump-001-MFA, CJR-EMPump-002-Encryption, CJR-EMPump-003-ServicePort |
| Current MDRS | 8.175 → CRITICAL |
