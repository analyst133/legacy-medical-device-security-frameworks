# Archetype 2 Scenario Library — Embedded RTOS Legacy

Reusable threat scenarios for medical devices built on real-time operating systems (VxWorks, QNX, ThreadX, INTEGRITY, FreeRTOS, eCos) or fully proprietary embedded firmware. Examples include large-volume infusion pumps, ventilators, anaesthesia machines, physiological monitors, point-of-care analysers, and many implantable device programmers.

The defining characteristic of Archetype 2 is the absence of a general-purpose OS shell and consequently the absence of host-based control surfaces. There is no place to install an EDR agent, no syslog daemon, often no per-user account model, and frequently no facility for cryptographic key storage. The dominant attack surface is the protocol parser itself, and compensating controls are exclusively network-adjacent and physical.

## How to use this library

Draw scenarios from the relevant category and adapt to your specific device. The Archetype 2 mitigations are deliberately limited compared with Archetype 1 — accept that some risks must be addressed exclusively at the network or physical perimeter.

## S — Spoofing

### Network attacker

- ARP cache poisoning to redirect device-to-host traffic
- Forged HL7 v2 messages from spoofed nursing station or clinical information system
- Forged proprietary protocol traffic (vendor-specific binary protocols often have weak or no integrity protection)
- Rogue device on shared VLAN impersonating peer device
- DHCP spoofing causing device to use attacker-controlled gateway

### Physical / insider attacker

- Substituted device with cloned identifier (asset tag, serial number) during scheduled service
- Vendor-impersonation social engineering at device location (badge, uniform, work order forgery)
- Cloned RFID/NFC/proximity token used for paired-display authentication
- Bluetooth pairing impersonation against paired peripherals
- Identical-model device swap concealing tampering

## T — Tampering

### Network attacker

- Unauthorised firmware push from compromised vendor update channel
- Configuration tampering via unauthenticated management interface (HTTP, Telnet, SNMP v1/v2)
- Protocol parser exploitation (URGENT/11, Ripple20, AMNESIA:33, NUMBER:JACK, NAME:WRECK)
- TFTP/FTP boot configuration manipulation
- Malformed HL7 or DICOM message causing memory corruption

### Physical / insider attacker

- Firmware injection via USB-A, RS-232, or proprietary service connector
- Configuration tamper via local console or service-mode PIN (often documented in leaked manuals)
- Removable media replacement (CompactFlash, MicroSD, EEPROM) during maintenance window
- Direct EEPROM/JTAG access via physical disassembly (rare; targeted)
- Service-mode firmware downgrade to vulnerable version

## R — Repudiation

### Network attacker

- Configuration changes via shared service account with no per-user attribution
- Untraceable data access via cleartext protocol with no per-session log
- Use of vendor service tooling that does not generate device-side audit records

### Physical / insider attacker

- Service-mode access by unidentified technician (badge worn, work order falsified)
- Bedside parameter changes by user logged in to nursing station with shared credential
- PHI capture by mobile-phone photography of device display
- Vendor service activity outside scheduled work-order window

## I — Information Disclosure

### Network attacker

- Cleartext HL7 v2 carrying patient identifier, medication, dose, and timing
- Cleartext DICOM with patient PHI (less common in pure Archetype 2 but seen in modality-attached devices)
- Vendor-proprietary protocol carrying PHI without encryption
- Unprotected data export via management interface or service tool
- Memory readout via debug interface

### Physical / insider attacker

- Mobile-phone photography of PHI on device display in shared environments
- Bulk PHI export to USB at service port using service tool
- Eavesdropping on Bluetooth or BLE pairing or active sessions
- NFC sniffing in proximity to NFC-equipped devices
- Acoustic eavesdropping (rare; documented for some pumps)

## D — Denial of Service

### Network attacker

- Network flooding disrupting real-time HL7 / DICOM communication
- Targeted protocol-parser crash (URGENT/11-class IPnet stack vulnerabilities in VxWorks)
- Resource exhaustion via malformed message stream
- ARP storm or broadcast amplification on shared segment
- TCP RST injection terminating active session

### Physical / insider attacker

- Power or network cable disconnection at device location
- Physical destruction or theft (documented in agency-staff and visitor incidents)
- Service-mode reset rendering device unavailable mid-therapy
- Battery removal causing reboot in transportable devices
- Tampering with peripheral cabling (sensors, connectors) causing device to fault into safe-mode

## E — Elevation of Privilege

### Network attacker

- Default credential exploitation via management interface (Telnet, HTTP, SNMP)
- Vendor backdoor account exploitation (documented in many leaked manuals)
- Protocol parser exploitation enabling code execution
- SNMP v1/v2 community string brute-force
- Telnet credential brute-force where account lockout is absent

### Physical / insider attacker

- Service-mode credential abuse via physical service port (RS-232, USB)
- Vendor service-tool privilege abuse (vendor laptop has documented elevated privileges)
- Unauthorised access to administrative menus via undocumented key sequence (frequently disclosed in leaked service manuals)
- Direct hardware access (JTAG, UART headers exposed on PCB)
- Boot media replacement (MicroSD, EEPROM) with attacker-prepared image

## Cross-cutting compensating-control patterns

For Archetype 2, the following compensating controls have broad applicability:

- **Strict network microsegmentation** (S, T, I, D, E): the dominant defence; place each Archetype 2 device in a dedicated VLAN with deny-all default ACL
- **Inline IPS with healthcare protocol parsing** (S, T, D, E): virtual patches for URGENT/11-class CVEs; HL7/DICOM parser hardening
- **HL7/DICOM protocol-aware proxy gateway** (S, T, R, I): provides authentication, audit, encryption wrapping, and DLP that the device cannot
- **IPSec encapsulation of cleartext streams** (I): encrypts data in transit on the network
- **Pattern A — upstream PAM gateway** (S, R, E): user authenticates with MFA upstream; gateway connects with hardcoded device credential from vault
- **Pattern C — inline hardware MFA shim at service port** (R, T, E): the only effective control against physical service-port abuse for devices with hardcoded service-mode credentials
- **Tamper-evident sealing** (T, R): physical seal on service-port covers, periodically inspected
- **Physical port blockers** (T, I): epoxy or locking inserts on unused USB and service ports
- **Vendor-escort policy** (S, R, E): mandatory clinical engineering accompaniment for all vendor service activities
- **Behavioural monitoring** (all): UEBA on protocol traffic, passive fingerprinting, physical-access correlation; for Archetype 2 this is often the only detection capability
- **Backup device staging** (D): mitigates theft, destruction, and service-mode-reset DoS

## When Archetype 2 protections are insufficient

Archetype 2 has structural limitations that compensating controls cannot fully overcome:

- **No host attestation** — substitution attacks must rely on passive fingerprinting and tamper-evident sealing, neither of which provides cryptographic assurance
- **No granular audit** — repudiation residual risk persists despite network-level logging
- **No dynamic patching** — protocol-parser CVEs may have months-to-years between disclosure and vendor patch; virtual patching narrows but does not close the window
- **Limited cryptographic key handling** — many devices have no facility for organisation-issued certificates, restricting authenticated communication options
- **Vendor-controlled security floor** — meaningful protocol or authentication improvements require vendor firmware update, often subject to FDA clearance dependencies

These structural limitations argue for **defence-in-depth at the network and physical layers**, **behavioural monitoring as a first-class control rather than a backstop**, and **manufacturer engagement under FDA 524B postmarket cybersecurity obligations** to drive longer-term improvements.
