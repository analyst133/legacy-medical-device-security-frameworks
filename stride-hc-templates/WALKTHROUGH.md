# STRIDE-HC Walkthrough — from blank page to completed threat model

A first-time-user tutorial. We build a complete STRIDE-HC threat model from scratch using a hypothetical legacy infusion pump as the running example. By the end you'll have a populated `stride-hc-template.md` file that you can compare against the worked example in [`examples/infusion-pump.md`](./examples/infusion-pump.md).

**Estimated time:** 30 minutes for a first attempt, 10–15 minutes once you've done one.

**Audience:** anyone who can read the paper. No prior threat-modelling experience required; this walkthrough explains what STRIDE-HC asks for and how to answer it for legacy clinical devices.

## What you need before starting

Have these facts about the device in front of you:

- Model + manufacturer + FDA device class
- Operating system or firmware identifier (e.g., "Windows 7 SP1" or "VxWorks 6.9")
- Network interfaces and protocols (HL7, DICOM, FHIR, proprietary, etc.)
- Authentication scheme (per-user? shared service password? hardcoded?)
- Physical interfaces (USB, RS-232, network port locations, Bluetooth, wireless)
- Patching status (current? EOL? vendor-restricted?)
- Audit logging (does the device log? where? retained how long?)
- Deployment context (how many, which clinical settings, supervised or unattended?)

If you don't know some of these, that's fine — fill in "unknown" and treat closing the gap as a Phase 0 deliverable. A STRIDE-HC threat model with explicit "unknown" fields is more useful than one with assumptions baked in.

---

## Step 1 — Determine the device archetype (2 minutes)

STRIDE-HC distinguishes two archetypes because the feasible compensating controls differ substantially.

| If the device runs… | Archetype | Typical examples |
|---|---|---|
| Windows / Linux / general-purpose Unix on standard PC-class hardware | **Archetype 1** | PACS workstations, imaging modality consoles (CT, MRI), laboratory analysers, pharmacy automation, radiotherapy planning stations |
| Embedded RTOS (VxWorks, QNX, ThreadX, FreeRTOS, etc.) or proprietary firmware | **Archetype 2** | Infusion pumps, ventilators, physiological monitors, anaesthesia machines, dialysis controllers |

**How to decide if you're not sure:**

- Does the device have a user-visible operating system (desktop, taskbar, file browser)? → Archetype 1
- Can you install third-party software on it (in principle, even if forbidden by vendor)? → Archetype 1
- Is the entire UI a manufacturer-built application running on bare hardware? → Archetype 2
- Does it boot in <10 seconds with no boot menu or splash screen? → Archetype 2
- Hybrid case (an Archetype 1 OS underneath, sealed by a kiosk shell)? Treat as Archetype 1 for compensating-control purposes — host-based controls are technically feasible even if vendor warranty forbids them.

**For our example pump:** runs VxWorks 6.9, no user-visible OS, monolithic firmware image — **Archetype 2**.

The archetype determines which **scenario library** you draw from:
- Archetype 1 → [`scenario-library/archetype-1-scenarios.md`](./scenario-library/archetype-1-scenarios.md)
- Archetype 2 → [`scenario-library/archetype-2-scenarios.md`](./scenario-library/archetype-2-scenarios.md)

---

## Step 2 — Copy the template, fill the device profile (5 minutes)

Copy [`stride-hc-template.md`](./stride-hc-template.md) to a new file named for your device. Recommended naming: `<class>-<model>-<inventory-tag>.md`. For our pump: `infusion-pump-empump-volumetric-v32.md`.

Open the new file. Section 1 is the device profile table. Every field has italicized inline guidance that you replace with real values. For our pump:

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

This becomes the **shared context** that every later section refers to. Get it right; everything else flows from it.

**Tip:** the MDS² disclosure form (if the vendor provides one) answers most of these fields directly. If the device pre-dates MDS² or the vendor didn't issue one, contact vendor support for the equivalent answers — vendors are increasingly under FDA §524B pressure to provide them retroactively.

---

## Step 3 — Work through the six STRIDE-HC categories (15 minutes)

This is the substantive work. For each STRIDE letter, you answer **two attacker questions** and document **two response questions**.

### The four-block pattern (applies to every category)

```
### X — Category name (CAW = w)

**Network-attacker scenarios:**
- Scenario 1
- Scenario 2
- ...

**Physical / insider-attacker scenarios:**     ← STRIDE-HC's key addition
- Scenario 1
- Scenario 2
- ...

**Detection methods (Framework V):**
- Method 1
- Method 2
- ...

**Compensating controls (Framework I):**
- Control 1
- Control 2
- ...

**CCD coverage assessment:** <how well do the controls cover the scenarios>
```

### You don't have to invent scenarios from scratch

Open your archetype's scenario library and copy the relevant scenarios into each category. The library lists common scenarios per category for legacy clinical devices. Your job is:

1. **Copy** the scenarios that apply to your device.
2. **Cut** the ones that don't (e.g., "Bluetooth pairing attack" doesn't apply if your device has no Bluetooth).
3. **Add** device-specific scenarios the library doesn't cover.

### Walking through each letter — example for our pump

#### S — Spoofing (CAW = 1.2)

Ask: how could an attacker pretend to be someone or something legitimate?

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

#### T — Tampering (CAW = 1.1)

Ask: how could an attacker modify the device, its firmware, its configuration, or data in transit?

This is often the **highest-stakes category** for legacy medical devices because the consequence of successful tampering is direct patient harm (wrong dose, wrong therapy delivery, wrong sensor calibration).

Look especially at:
- **Firmware update paths** — USB, network, service-mode commands. Each is a tampering surface.
- **Configuration interfaces** — service web UIs, RS-232 console, vendor utilities.
- **Storage media** — SD cards, internal flash, removable media.

For our pump:

**Network-attacker scenarios:**
- Unauthorised firmware push from compromised vendor distribution channel
- Configuration tampering via management interface (TCP/8080)

**Physical / insider-attacker scenarios:**
- Firmware injection via USB or RS-232 service port
- Configuration tamper via local console using documented service-mode PIN
- Physical replacement of internal storage card

**Detection methods (Framework V):**
- File integrity monitoring (network-adjacent — device itself can't run agents)
- Configuration version comparison via vendor management API
- Tamper-evident seal inspection (monthly cadence)

**Compensating controls (Framework I):**
- USB port logical or physical disablement
- **Inline MFA shim (Pattern C) at service port** — see [`../mfa-shim/`](../mfa-shim/)
- Tamper-evident sealing with serialised seals
- Firmware version monitoring + alerting on unexpected change

**CCD coverage assessment:** Strong if MFA shim deployed; weak without it because the documented service-mode PIN is a low-bar attacker capability.

#### R — Repudiation (CAW = 0.9)

Ask: could an action on the device be later disowned by the actor who performed it?

For our pump: no per-user authentication means all configuration changes appear as "service-mode user", impossible to attribute. This is a **repudiation-by-default** condition.

**Network-attacker scenarios:**
- Unattributable configuration changes via shared service account
- HL7 message origin disputed (no signing)

**Physical / insider-attacker scenarios:**
- Service-mode action attributable only by physical witness (door log, badge swipe)
- Disputed dose change between staff shifts

**Detection methods:**
- Upstream session recording (which the MFA shim provides)
- Door access correlation
- Camera correlation in high-risk areas

**Compensating controls:**
- Inline MFA shim with TOTP-bound session recording → produces per-user attribution
- Vendor-escort policy with logged escort identity
- Badge-correlation requirement for service work orders

**CCD coverage assessment:** Solved if MFA shim deployed; unsolvable without compensating control because the device cannot be modified to support per-user auth.

#### I — Information disclosure (CAW = 1.2)

Ask: could data flowing through, stored on, or displayed by the device be observed by an unauthorized party?

For our pump:
- HL7 traffic is cleartext on TCP/2575 — anyone with VLAN access can read PHI
- Service-port traffic is cleartext — anyone with physical access during service can read everything

**Network-attacker scenarios:**
- Passive HL7 capture on clinical VLAN (yields drug/patient data)
- Service-port traffic capture during vendor work

**Physical / insider-attacker scenarios:**
- Shoulder-surfing the pump display during dosing rounds
- Photographing the service-mode menu

**Detection methods:**
- Network sensor for unexpected cleartext PHI flows
- Camera correlation in service-window timeframes

**Compensating controls:**
- Inline encryption gateway upstream of pump (if feasible)
- VLAN segmentation to limit cleartext exposure
- Service-window privacy screens
- Inline MFA shim with session recording (deters insider capture)

#### D — Denial of Service (CAW = 1.5 — highest weight)

CAW is 1.5 because in clinical settings, DoS is not an inconvenience — it can be patient harm. A pump that stops infusing during chemotherapy is a harm event.

**Network-attacker scenarios:**
- Protocol flood (HL7 connection exhaustion)
- ICMP flood
- Power-supply attack (network-controlled UPS)

**Physical / insider-attacker scenarios:**
- Cable removal
- Power cord removal
- Service-mode crash induction

**Detection methods:**
- Network traffic baselining + flood detection
- Device availability monitoring (pings, health-check API)
- Power monitoring on critical-care branches

**Compensating controls:**
- Rate-limiting at upstream switch
- Redundant network paths
- Battery backup with monitored capacity
- Physical cable lock + tamper-evident covering

#### E — Elevation of privilege (CAW = 1.1)

Ask: could an attacker gain higher-privileged access than they started with?

**Network-attacker scenarios:**
- Default-credential login from clinical VLAN
- Service-mode privilege escalation via documented PIN
- Vendor management protocol abuse

**Physical / insider-attacker scenarios:**
- Service-port login using documented PIN
- Maintenance-mode boot via physical button
- Firmware downgrade to known-vulnerable version

**Detection methods:**
- Authentication attempt logging (upstream of device, since device doesn't log)
- Privileged session recording (MFA shim)
- Firmware version surveillance

**Compensating controls:**
- MFA shim with per-user enforcement
- Privileged access management (PAM) for vendor accounts
- Service-port physical lock + escort policy

---

## Step 4 — Set Clinical Availability Weights (1 minute)

CAW values reflect the **clinical consequence multiplier** for each category. The defaults are:

| Category | CAW | Why |
|---|---|---|
| Denial of Service | **1.5** | DoS = potential patient harm in clinical settings |
| Spoofing | 1.2 | Wrong-attribution scenarios drive wrong-care decisions |
| Information disclosure | 1.2 | PHI exposure is a HIPAA reportable event |
| Tampering | 1.1 | High consequence but moderated by detection feasibility |
| Elevation of privilege | 1.1 | Sets up other categories rather than being the harm event itself |
| Repudiation | 0.9 | Lowest because it amplifies other harms rather than causing them |

**Use the defaults unless** you have a device-specific reason to adjust. Examples of valid adjustments:
- For a **passive imaging modality** (no active therapy): DoS may drop to 1.3
- For a **research data device** (no live patient care): all weights may drop ~0.2
- For an **implanted-device programmer** that talks to live implants: Tampering may rise to 1.3

Document the rationale next to the weight if you change a default.

---

## Step 5 — Validate your work (3 minutes)

Walk through this checklist before declaring the threat model complete:

- [ ] Device profile table is fully populated (no italicized placeholders left)
- [ ] All six STRIDE letters have at least one network-attacker scenario AND at least one physical/insider scenario
- [ ] Every scenario has at least one detection method
- [ ] Every scenario maps to at least one compensating control
- [ ] Categories where the residual risk is unacceptable have a corresponding **CJR draft started** in [`../cjr-templates/`](../cjr-templates/)
- [ ] The CCD coverage assessment is honest — don't claim "Strong" if the controls are aspirational
- [ ] CAW values are either the defaults or have inline rationale for the deviation

**Compare against the worked example:** [`examples/infusion-pump.md`](./examples/infusion-pump.md) for Archetype 2, or [`examples/pacs-workstation.md`](./examples/pacs-workstation.md) for Archetype 1. Your completed model should resemble these in structure and density. If your file is much shorter than the worked examples, you've probably under-specified scenarios.

---

## Step 6 — Where the output goes

A completed STRIDE-HC threat model is not the deliverable — it's an **input to four downstream artifacts**:

| Downstream artifact | What the STRIDE-HC model provides | Where to send it |
|---|---|---|
| **FDA §524B premarket submission** (vendors) | The threat-model deliverable required by 2023 cybersecurity guidance | Attach as Appendix to your premarket submission |
| **ISO 14971 risk management file** (vendors + HDOs) | Hazard identification (cl.5) and risk estimation (cl.6) records | Attach as the security-hazard section of your risk management file |
| **AAMI TIR57 security risk records** | The security risk identification activities required by TIR57 | Reference by ID in your TIR57 records |
| **CJR documents** ([`../cjr-templates/`](../cjr-templates/)) | The threat each compensating control is justified against | Each STRIDE-HC scenario you cannot fully mitigate produces a CJR; cross-reference the STRIDE-HC scenario ID inside the CJR |
| **MDRS calculator** ([`../mdrs-calculator/`](../mdrs-calculator/)) | Empirical input to the CCD (Compensating-Control Deficit) score | When you re-run MDRS after deploying controls, your CCD score should improve to reflect the new coverage |

**Review cadence** for the threat model itself:
- After any **firmware update** by the vendor
- After any **network architecture change** affecting the device
- After any **incident** involving the device or a peer device
- Otherwise, **annually** for production-deployed legacy devices

**Sign-offs** typically required:
- Clinical engineering or biomedical engineering — for clinical accuracy
- InfoSec / CISO office — for threat-model technical correctness
- Quality / regulatory affairs — for standards alignment (FDA, ISO 14971, AAMI)
- For HDOs: also clinical leadership (CMO or service line chief) for any DoS scenarios involving life-sustaining devices

---

## Common pitfalls

| Pitfall | Why it happens | Fix |
|---|---|---|
| All scenarios are network-attacker | Authors come from IT security, not clinical engineering | Force yourself to list at least one physical scenario per category before moving on |
| Compensating controls are aspirational | "We could deploy 802.1X" without a plan | Each control gets a CJR; the CJR forces you to confirm feasibility, cost, and timeline |
| CCD coverage marked "Strong" everywhere | Wishful thinking | Run the test harness ([`../test-harness/`](../test-harness/)) to get empirical CCD evidence |
| Same scenario copied under multiple categories | Confusion about which STRIDE letter applies | Pick the letter that captures the *attacker's primary intent*; cross-reference if needed but don't duplicate |
| CAW values changed without rationale | Following a non-clinical security template | Use defaults; deviations must have inline rationale |

---

## Going further

- For the **paper-cited methodology** behind STRIDE-HC and the CAW values, see paper §4.
- For the **integrated workflow** showing how STRIDE-HC connects to MDRS, CJR, the test harness, and the MFA shim, see the top-level [`../WALKTHROUGH.md`](../WALKTHROUGH.md).
- For **tooling integration** — querying your threat models programmatically — see the schemas at [`stride-hc-schema.yaml`](./stride-hc-schema.yaml) / [`stride-hc-schema.json`](./stride-hc-schema.json) and the "For tooling integration" section of [`README.md`](./README.md).
