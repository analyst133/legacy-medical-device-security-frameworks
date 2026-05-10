# STRIDE-HC Threat Model: Generic PACS Imaging Workstation

> Worked example for **Archetype 1 (general-purpose-OS legacy)** — Windows 7-based PACS reading workstation.

## 1. Device profile

| Field | Value |
|---|---|
| Device name and model | Vendor X PACS Reading Station v8.4 |
| Manufacturer | Vendor X |
| Device class (FDA) | Class II (image display application) |
| **Archetype** | **Archetype 1 (general-purpose-OS legacy)** |
| Operating system | Windows 7 Pro x64 (EOL) |
| Networking | Gigabit Ethernet, DICOM (TCP/104 cleartext, TCP/2762 TLS), HL7 v2 to RIS |
| Authentication | Local Windows account with shared technologist credentials |
| Patching | Vendor delivers cumulative patches quarterly; OS no longer receives Microsoft updates |
| Audit logging | Windows Security Event Log; vendor application log |
| Physical interfaces | USB-A (multiple), DVD-RW, optional badge reader |
| Deployment | 38 units across radiology reading rooms and ED imaging review |
| Clinical use | Diagnostic image review and reporting |

## 2. Why Archetype 1 differs from Archetype 2

This example deliberately contrasts with the infusion pump example. Note the differences:

- **Host-based controls feasible.** Application allowlisting, EDR, BitLocker, LAPS, Sysmon — all deployable. Archetype 2 has none of this.
- **Standard authentication methods available** (Windows accounts, Active Directory join, smartcard) — but the *legacy* nature shows up in shared technologist credentials, deferred MFA rollouts, and reading-workflow constraints that prevent always-on MFA prompts during interpretation.
- **Patching exists** but is constrained — vendor cumulative patches lag Microsoft, OS is past Microsoft EOL, and even available patches require validation against the imaging application before deployment.
- **Threat surfaces partially overlap with enterprise IT** — ransomware is a primary D-category concern (uncommon for Archetype 2); local privilege escalation is a real concern (less so for Archetype 2 which has no shell).

These differences drive different compensating-control selections, captured below.

## 3. STRIDE-HC threat scenarios

### S — Spoofing (CAW = 1.2)

**Network-attacker scenarios:**
- ARP cache poisoning to redirect DICOM traffic
- Forged DICOM transfers from spoofed modality
- Compromised RIS server forging HL7 worklist entries

**Physical / insider-attacker scenarios:**
- Rogue user authenticating with shared technologist credentials
- Unattended workstation hijack during break
- USB device emulating keyboard for credential injection

**Detection methods:** UEBA on DICOM source AE-Title; badge-to-workstation correlation.

**Compensating controls:** PAM with individual MFA upstream (Pattern A), session recording, USB device control whitelisting only HID-class on approved list.

**CCD coverage:** Full

---

### T — Tampering (CAW = 1.1)

**Network-attacker scenarios:**
- Malware introduction via Windows 7 vulnerability (e.g., EternalBlue)
- DICOM image manipulation in transit (e.g., CT-GAN-class attacks per Mirsky et al.)
- Configuration tampering via SMB share with weak ACL

**Physical / insider-attacker scenarios:**
- Malware introduction via USB or CD/DVD during image import
- Configuration tamper via local administrator login
- Replacement of DICOM viewer DLL via local file write

**Detection methods:** DICOM-aware proxy with checksum verification; EDR baseline of DLL loads; FIM on critical Windows directories.

**Compensating controls:**
- Application allowlisting (Carbon Black or Tripwire)
- USB media control (only signed organisational media)
- Virtual patching via network IPS for known Windows 7 CVEs
- DICOM TLS enforced

**CCD coverage:** Full

---

### R — Repudiation (CAW = 0.9)

**Network-attacker scenarios:** Anonymous DICOM transfers without strong AE-Title auth; image-export events not attributable to a specific user.

**Physical / insider-attacker scenarios:** Reading session with shared credentials; PHI capture via DVD burn or USB export by unidentified user.

**Detection methods:** Windows Security log forwarded to SIEM; badge tap to workstation correlation; deviation from scheduled radiologist shift flagged.

**Compensating controls:** Individual MFA via PAM (Pattern A); session recording for elevated actions; Sysmon and EDR telemetry to SIEM.

**CCD coverage:** Full

---

### I — Information Disclosure (CAW = 1.2)

**Network-attacker scenarios:** DICOM in transit with cleartext PHI; memory scraping via Windows 7 vuln; unprotected SMB share export.

**Physical / insider-attacker scenarios:** Unattended workstation with PHI visible from corridor; bulk PHI export to USB or DVD; shoulder-surfing.

**Detection methods:** DLP at DICOM proxy; EDR mass-file-access detection.

**Compensating controls:**
- Force DICOM TLS for all modality and PACS server connections; deprecate cleartext port
- Reading rooms physically secured; auto-screen-lock at 5 min idle; display privacy filters
- USB media control; DVD-burn requires admin approval workflow

**CCD coverage:** Full

---

### D — Denial of Service (CAW = 1.5)

**Network-attacker scenarios:** Network flooding disrupts modality-to-PACS flow; ransomware encrypting DICOM cache; targeted Windows 7 SMB exploit crash.

**Physical / insider-attacker scenarios:** Power or network disconnection; display destruction.

**Detection methods:** SIEM alert on unexpected reboot; ransomware behavioural detection (mass file rename / encryption).

**Compensating controls:** Application allowlisting prevents ransomware execution; SMB v1 disabled; backup workstation staged in each reading room; UPS with 30-minute runtime.

**CCD coverage:** Full

---

### E — Elevation of Privilege (CAW = 1.1)

**Network-attacker scenarios:** Windows 7 local privilege escalation post-foothold; lateral movement to PACS server.

**Physical / insider-attacker scenarios:** Local administrator credential abuse; boot from USB to bypass disk encryption.

**Detection methods:** EDR token-manipulation detection; network IDS for post-exploitation tooling.

**Compensating controls:** Application allowlisting; LAPS for local admin rotation; BitLocker enforced; PAM brokering for any admin function.

**CCD coverage:** Full

## 4. MDRS-relevant outputs

All six STRIDE categories have comprehensive controls, validated through annual penetration testing.

→ **CCD = 2**

This feeds the MDRS calculation: with `CIS=5.5, ES=4.0, DCI=6.0, NEF=3.5, CCD=2.0`, the composite is **4.750** → **MEDIUM** tier (paper Table 7).

## 5. Document control

| Field | Value |
|---|---|
| Author | Clinical Engineering / InfoSec / Radiology IT |
| Reviewer | CISO and Radiology Director |
| Approval date | 2026-03-15 |
| Next review | 2027-03-15 |
| Linked CJRs | CJR-PACS-001-Win7Patching, CJR-PACS-002-DICOMTLS, CJR-PACS-003-USBControl |
| Current MDRS | 4.750 → MEDIUM |
