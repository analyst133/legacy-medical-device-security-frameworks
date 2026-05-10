# Archetype 1 Scenario Library — General-purpose-OS Legacy

Reusable threat scenarios for medical devices built on legacy general-purpose operating systems (Windows XP, Windows 7, Windows Server 2008/R2, older Linux distributions, macOS pre-10.13). Examples include PACS workstations, imaging modality consoles, laboratory analysers, pharmacy automation, and certain ultrasound and patient-monitoring central stations.

The defining characteristic of Archetype 1 is the presence of a general-purpose OS shell that admits host-based controls (application allowlisting, EDR, host-based firewall, file integrity monitoring) but suffers from the absence of vendor-supported security patches.

## How to use this library

When authoring a STRIDE-HC threat model for an Archetype 1 device, draw scenarios from the relevant category below and adapt them to your specific device. Add device-specific scenarios as needed; this library is illustrative, not exhaustive.

## S — Spoofing

### Network attacker

- ARP cache poisoning on shared VLAN to redirect device traffic
- Compromised peer system forging legitimate-looking traffic (HL7, DICOM, vendor protocol)
- Rogue DHCP serving devices with attacker-controlled gateway
- Spoofed time source (NTP) causing certificate/log timestamp manipulation
- Domain controller compromise enabling ticket forgery (Golden Ticket)
- mDNS/LLMNR spoofing for credential capture

### Physical / insider attacker

- Local logon with shared credentials (technologist, "lab user", "vendor service")
- Unattended workstation hijack during user break or shift change
- USB HID-class device (BadUSB / Rubber Ducky-class) emulating keyboard for credential injection
- Bluetooth or Wi-Fi pairing impersonation to keyboard/mouse
- Service-mode access using vendor-disclosed credential pair

## T — Tampering

### Network attacker

- Exploitation of known unpatched OS CVE for code execution (e.g., EternalBlue/MS17-010 on Win7)
- Configuration tampering via weakly-protected SMB share or remote registry
- Tampering with DICOM imagery in transit (CT-GAN-class attacks per Mirsky et al. 2019)
- Compromised software update channel pushing unsigned binaries
- DLL hijacking via writable system directory or PATH manipulation

### Physical / insider attacker

- Malware introduction via USB drive during legitimate image import workflow
- Malware introduction via CD/DVD or external optical drive
- Configuration tamper via local administrator login (especially when LAPS not deployed)
- DLL replacement via local file write (vendor application directories often world-writable)
- Removable storage replacement (MicroSD card in handheld devices)

## R — Repudiation

### Network attacker

- Anonymous protocol-level transfers without strong source authentication (DICOM AE-Title without TLS, HL7 v2 without ACK chains)
- Use of compromised credentials with no second-factor record
- Log deletion or rotation manipulation post-compromise

### Physical / insider attacker

- Use of shared workstation credentials with no per-user attribution
- PHI capture via mobile-phone photography of display
- DVD/USB export by unidentified user with shared session
- Vendor service activity outside scheduled work-order window

## I — Information Disclosure

### Network attacker

- Cleartext DICOM, HL7, or vendor-proprietary protocol carries PHI on shared segment
- Memory scraping via Windows OS vulnerability for reading active session data
- Unprotected SMB share or file system permission allowing PHI export
- Exploitation of vendor application export features without audit

### Physical / insider attacker

- Mobile-phone photography of PHI on display
- Bulk PHI export to USB or optical media during legitimate session
- Shoulder-surfing in shared reading rooms or open clinical areas
- Print-to-network exfiltration via networked printers

## D — Denial of Service

### Network attacker

- Ransomware encrypting local data store (PACS cache, application data, OS files)
- Targeted SMB or RDP exploit causing OS crash (BSOD)
- Network flooding overwhelming legitimate traffic
- Resource exhaustion via crafted application input
- Malware-induced infinite loop or memory exhaustion

### Physical / insider attacker

- Power or network cable disconnection at workstation
- Display destruction or input-device theft
- Local malware introduction via USB causing system instability
- Boot order tampering causing failure-to-boot

## E — Elevation of Privilege

### Network attacker

- Windows local privilege escalation CVE exploitation post-foothold (numerous documented for Win7/8/Server 2008)
- Token impersonation following service account compromise
- Lateral movement to peer systems via Pass-the-Hash, NTLM relay
- Kerberoasting against service principals

### Physical / insider attacker

- Local administrator credential abuse (especially where LAPS is not deployed)
- Boot from USB or external media to bypass disk encryption
- Direct memory access (DMA) attacks via Thunderbolt/PCIe (rare; targeted)
- Exploitation of physical reset switches or jumpers
- "Sticky keys" or accessibility-tool replacement at the login screen

## Cross-cutting compensating-control patterns

For Archetype 1, the following compensating controls have broad applicability across categories:

- **Application allowlisting** (Tampering, DoS, Elevation): blocks unsigned/unauthorised binaries, including ransomware payloads
- **EDR with behavioural detection** (Tampering, DoS, Elevation, Repudiation): detects post-foothold activity even when initial vector is missed
- **Microsoft LAPS or equivalent** (Spoofing, Repudiation, Elevation): randomises local admin passwords
- **PAM/PAW for administrative functions** (Spoofing, Repudiation, Elevation): individual MFA upstream of shared credentials
- **Network IPS with virtual patching** (all): mitigates unpatched OS and application CVEs
- **USB device control via EDR** (Tampering, Information Disclosure): allowlists approved media; blocks BadUSB-class devices
- **DICOM/HL7 protocol-aware proxy** (Spoofing, Tampering, Information Disclosure): provides authentication, integrity verification, audit, and DLP
- **Session recording for shared accounts** (Repudiation): provides post-hoc attribution where individual auth not feasible

## When Archetype 1 protections are insufficient

There are scenarios where Archetype 1 host-based protections cannot fully address the threat, and the threat must be mitigated at the network or physical layer:

- Cleartext protocols on shared network → must be mitigated at network (VLAN isolation, IPSec wrapping, or protocol gateway)
- Physical theft or destruction → physical access control, surveillance, backup staging
- Legitimate-but-malicious user actions (insider threat) → behavioural monitoring, separation of duties, periodic access review
- Hardware-level supply chain compromise → asset receiving inspection, fingerprinting, hardware root of trust where available
