# STRIDE-HC Threat Model: [Device name]

> **Template**: replace bracketed text and italicised guidance with device-specific content. Delete unused subsections.

## 1. Device profile

| Field | Value |
|---|---|
| Device name and model | _e.g., ExampleMed Volumetric Infusion Pump v3.2_ |
| Manufacturer | _e.g., ExampleMed Inc._ |
| Device class (FDA / EU MDR) | _e.g., Class II_ |
| UMDNS / GMDN code | _e.g., 16495 / 35143_ |
| MDS² reference | _attach manufacturer disclosure form_ |
| **Archetype** | _Archetype 1 (general-purpose-OS legacy) **or** Archetype 2 (embedded RTOS legacy)_ |
| Operating system / firmware | _e.g., VxWorks 6.9 (EOL); proprietary firmware v3.2_ |
| Networking | _e.g., 100Mbit Ethernet, HL7 v2 over TCP/2575, no TLS_ |
| Authentication | _e.g., Hardcoded service-mode credential; no per-user login_ |
| Patching | _Manufacturer no longer issues patches; FDA clearance limits modification_ |
| Audit logging | _None on device; only at upstream nursing station_ |
| Physical interfaces | _RS-232 service port; USB-A (firmware update); Bluetooth (paired display)_ |
| Deployment count | _e.g., 240 units across the facility_ |
| Clinical use | _Continuous medication infusion; ICU and oncology_ |

## 2. STRIDE-HC threat scenarios

For each category, list network-attacker and physical/insider-attacker scenarios. Some categories may have more scenarios than others. Mark each scenario with the archetype it applies to (A1, A2, or both).

### S — Spoofing (CAW = 1.2)

**Network-attacker scenarios:**
- _ARP cache poisoning to redirect device traffic_ (A1, A2)
- _Forged HL7 / DICOM messages from spoofed source_ (A1, A2)
- _Rogue device impersonation on shared VLAN_ (A1, A2)

**Physical / insider-attacker scenarios:**
- _Substituted device with cloned identifier_ (A1, A2)
- _Vendor-impersonation social engineering at device location_ (A1, A2)
- _Cloned RFID/NFC token used for proximity authentication_ (A1, A2)

**Detection methods (Framework V):**
- _Passive device fingerprinting (network sensor with longitudinal store)_
- _Badge-correlation analytics_
- _Network UEBA peer-set anomaly_

**Compensating controls (Framework I):**
- _802.1X port-based access control with MAB allowlist_
- _Tamper-evident asset tags with serialised identifier_
- _Vendor-escort policy with badge correlation_

---

### T — Tampering (CAW = 1.1)

**Network-attacker scenarios:**
- _Unauthorised firmware push from compromised vendor channel_
- _Configuration tampering via management interface_
- _Malicious software via Archetype 1 OS vulnerability_ (A1)

**Physical / insider-attacker scenarios:**
- _Firmware injection via USB or service port_
- _Configuration tamper via local console or service-mode PIN_
- _Physical replacement of removable storage_

**Detection methods (Framework V):**
- _File integrity monitoring (network-adjacent for A2)_
- _Configuration version comparison via management API_
- _Tamper-evident seal inspection (monthly cadence)_

**Compensating controls (Framework I):**
- _Write-protect switches; immutable boot media_
- _USB port disablement (logical or physical)_
- _Inline MFA shim (Pattern C) at service port_
- _Tamper-evident sealing with serialised seals_

---

### R — Repudiation (CAW = 0.9)

**Network-attacker scenarios:**
- _Unattributable configuration changes via shared service account_
- _Untraceable data access via cleartext protocol_

**Physical / insider-attacker scenarios:**
- _Service-mode access by unidentified technician_
- _Bedside changes to therapy parameters by unidentified clinician_
- _PHI capture by mobile-phone photography_

**Detection methods (Framework V):**
- _Network PCAP with retention_
- _Syslog proxy capturing device-adjacent events_
- _Physical badge access logs correlated to device location_
- _UEBA behavioural baseline_

**Compensating controls (Framework I):**
- _Network-layer logging pipeline (compensates for absent device logging)_
- _PAW with individual auth upstream (Pattern A)_
- _Session recording at MFA shim (Pattern C)_
- _Badge-to-device correlation analytics_

---

### I — Information Disclosure (CAW = 1.2)

**Network-attacker scenarios:**
- _PHI interception on shared network segment (cleartext HL7 v2, DICOM)_
- _Memory scraping via OS vulnerability_ (A1)
- _Unprotected data export via management interface_

**Physical / insider-attacker scenarios:**
- _PHI display photographed in shared environment_
- _Bulk PHI export to USB at service port_
- _Eavesdropping on proximity wireless (BLE / NFC)_

**Detection methods (Framework V):**
- _Protocol-aware IDS flagging cleartext PHI_
- _Display privacy filter audit_
- _WIDS for proximity wireless_
- _DLP at network gateway_

**Compensating controls (Framework I):**
- _VLAN isolation_
- _IPSec tunnel encapsulating cleartext_
- _Display privacy filters_
- _PHI minimisation at gateway_
- _Service-port USB disablement_

---

### D — Denial of Service (CAW = 1.5)

**Network-attacker scenarios:**
- _Network flooding disrupts real-time monitoring_
- _Targeted protocol-parser crash (URGENT/11-class)_
- _Resource exhaustion via malformed messages_

**Physical / insider-attacker scenarios:**
- _Power or network cable disconnection at device location_
- _Physical destruction or theft_
- _Service-mode reset rendering device unavailable_

**Detection methods (Framework V):**
- _Network rate limiting upstream_
- _Availability monitoring with alerting_
- _Device location video surveillance_
- _Environmental monitoring (Framework V side-channel)_

**Compensating controls (Framework I):**
- _Dedicated VLAN with QoS priority_
- _Rate limiting; redundant network paths_
- _Uptime SLAs with vendor_
- _Physical access controls; backup device staging_

---

### E — Elevation of Privilege (CAW = 1.1)

**Network-attacker scenarios:**
- _Default credential exploitation via network management interface_
- _OS CVE exploitation for local root_ (A1)
- _Lateral movement to adjacent clinical systems_

**Physical / insider-attacker scenarios:**
- _Service-mode credential abuse via physical port_
- _Vendor-service-tool privilege abuse_
- _Unauthorised access to administrative menus via undocumented key sequence_

**Detection methods (Framework V):**
- _IDS/IPS with legacy OS exploit signatures_
- _Privilege escalation monitoring_
- _Behavioural analytics for anomaly_
- _Service-port session recording_

**Compensating controls (Framework I):**
- _Virtual patching via IPS_
- _Application allowlisting (Archetype 1)_
- _Network microsegmentation_
- _Inline MFA shim (Pattern C)_
- _PAM upstream (Pattern A)_

## 3. Mapping to MDRS

This threat model informs the device's MDRS Compensating Control Deficit (CCD) score. The **CCD** dimension counts STRIDE-HC categories with effective compensating controls:

- **CCD = 1–2**: Comprehensive controls across all six STRIDE categories, validated annually.
- **CCD = 3–4**: Comprehensive controls, not formally tested.
- **CCD = 5–6**: Controls in 3–4 STRIDE categories.
- **CCD = 7–8**: Partial controls (1–2 STRIDE categories covered).
- **CCD = 9–10**: No compensating controls.

For this device, the CCD score is `[fill in]` because:

- _Spoofing: [covered / partial / not covered] — because [reason]_
- _Tampering: [covered / partial / not covered] — because [reason]_
- _Repudiation: [covered / partial / not covered] — because [reason]_
- _Information Disclosure: [covered / partial / not covered] — because [reason]_
- _Denial of Service: [covered / partial / not covered] — because [reason]_
- _Elevation of Privilege: [covered / partial / not covered] — because [reason]_

## 4. Document control

| Field | Value |
|---|---|
| Author | _Clinical engineering / information security_ |
| Reviewer | _CISO and Director of Clinical Engineering_ |
| Approval | _Joint sign-off_ |
| Approval date | _YYYY-MM-DD_ |
| Next review | _YYYY-MM-DD (annual or after material event)_ |
| Linked CJRs | _List of Control Justification Records_ |
| MDRS score (current) | _e.g., 8.175 → CRITICAL_ |
