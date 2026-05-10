# Walkthrough — How the five artifacts fit together

This walkthrough demonstrates the integration claim of the companion paper: the five artifacts in this repository are designed as a **connected workflow**, not five standalone tools. Each step's output is the next step's input.

We use a hypothetical legacy infusion pump as the running example, because it's the only device that appears across all five artifacts — making the chain visible and verifiable end-to-end. Substitute your own device; the flow is identical.

## The chain in one picture

```
Inventory device     MDRS              STRIDE-HC          CJR              Test harness      MFA shim
─────────────        ─────             ─────────          ───              ────────────      ────────
Fact about device → Risk tier      →  Threat list      → Justified     → Empirical       → Deployed
                                      per-attacker       compensating    evidence           control
                                      per-category       control(s)
                                                                                              ↑
                                                                                              │
                                                          Pattern C is ONE specific control ──┘
                                                          (the other controls come from
                                                           paper §3 Compensating Controls
                                                           Playbook)
```

## The scenario

You're the security lead at a hospital. Clinical engineering surfaces **240 ExampleMed volumetric infusion pumps**, model v3.2, running **VxWorks 6.9** firmware. The vendor confirms: no patches coming, no MFA on the management port, hardcoded service-mode password documented in the service manual. ICU and oncology run these continuously on patients.

What do you do? Five artifacts, five steps.

---

## Step 1 — Triage: how urgent is this? → MDRS Calculator

Open the calculator:

- **Live:** [https://analyst133.github.io/legacy-medical-device-security-frameworks/mdrs-calculator/](https://analyst133.github.io/legacy-medical-device-security-frameworks/mdrs-calculator/)
- **Local:** [`mdrs-calculator/index.html`](./mdrs-calculator/index.html)

The calculator runs in guided mode by default — answer five plain-English multiple-choice questions and it assigns the appropriate score. Or click **Direct entry** to use sliders if you already know the scores. For our infusion pump:

| Dimension | What it asks | Answer for this pump | Score |
|---|---|---|---|
| **CIS** — Clinical Impact Severity | Could a compromise harm a patient? | Yes — wrong dose can kill | **9.0** |
| **ES** — Exploitability | How attackable is it? | Hardcoded password + cleartext mgmt protocol | **7.5** |
| **DCI** — Data Criticality & Integrity | What data does it expose/control? | Live infusion params + PHI | **8.0** |
| **NEF** — Network Exposure Factor | How reachable is it? | Sits on shared clinical VLAN, no segmentation | **8.0** |
| **CCD** — Compensating-Control Deficit | How weak are existing mitigations? | Some IDS, no segmentation, no PAM | **7.0** |

**Composite = 8.175 → CRITICAL.** The irreversibility floor (CIS ≥ 9 → minimum HIGH) confirms this is not a borderline call. The "What to do" panel tells you: *CISO + CMO + clinical engineering director within 24 hours, quarterly review.*

Click **Copy summary** or **Export JSON** in the calculator to capture the result for the next step.

**Output of Step 1:** a tier (CRITICAL) and an executive-defensible composite number (8.175), plus next-step ownership and review cadence.

---

## Step 2 — Model the threats: what specifically could go wrong? → STRIDE-HC Templates

Open: [`stride-hc-templates/examples/infusion-pump.md`](./stride-hc-templates/examples/infusion-pump.md) — the worked example for this exact device archetype (**Archetype 2** = embedded RTOS legacy).

The template walks through all six STRIDE-HC categories — Spoofing, Tampering, Repudiation, Information disclosure, DoS, Elevation of privilege — and for each one asks two questions:

1. What's the **network-attacker** scenario?
2. What's the **physical/insider-attacker** scenario?

The second question is the key STRIDE-HC modification: the physical attacker is treated as a co-equal threat surface, not an afterthought.

For our pump, here are two threats the template surfaces (excerpting from the worked example):

```
T — Tampering (CAW = 1.1)
  Network:  Unauthorised firmware push from compromised vendor channel
  Physical: Firmware injection via USB or service port           ← high-priority
  Detection:  File integrity monitoring (network-adjacent)
  Compensating controls:
    - USB port disablement
    - Inline MFA shim (Pattern C) at service port                ← solution candidate
    - Tamper-evident sealing
```

If you're not starting from the worked example, the **scenario library** at [`stride-hc-templates/scenario-library/archetype-2-scenarios.md`](./stride-hc-templates/scenario-library/archetype-2-scenarios.md) (or [`archetype-1-scenarios.md`](./stride-hc-templates/scenario-library/archetype-1-scenarios.md)) gives you a pre-filled menu so you don't stare at a blank page.

For a first-time tutorial that builds a STRIDE-HC threat model from blank to completed, see [`stride-hc-templates/WALKTHROUGH.md`](./stride-hc-templates/WALKTHROUGH.md).

**Output of Step 2:** a list of specific threat scenarios + a list of candidate compensating controls per threat.

---

## Step 3 — Pick a control: which compensating control do you deploy?

For our pump, the highest-priority threat is **physical-attacker firmware injection at the service port** — because (a) the device is CRITICAL from Step 1, (b) the service port is unauthenticated, and (c) the consequence is uncontrollable infusion behaviour.

The STRIDE-HC template surfaced three candidate controls:

1. USB port disablement — *rejected:* breaks the vendor's authorized service workflow
2. **Inline MFA shim at service port (Pattern C)** — *chosen*
3. Tamper-evident sealing — *retained as a complementary control*

You pick #2 because USB disablement makes scheduled service impossible, and sealing gives detection but not prevention. Sealing is kept as a layered control.

**This decision needs to be documented.** That's Step 4.

---

## Step 4 — Document the decision: prove it's defensible → CJR Templates

Open: [`cjr-templates/examples/cjr-no-mfa-infusion-pump.md`](./cjr-templates/examples/cjr-no-mfa-infusion-pump.md) — the worked Control Justification Record for this exact decision (deploying an MFA shim because the device can't run MFA natively).

A CJR is a regulator-readable, audit-readable document that captures:

1. **The device** — with explicit cross-link to the MDRS tier from Step 1 and the STRIDE-HC model from Step 2
2. **The standard control that cannot be applied** — here, native MFA on the management interface
3. **The constraint** preventing the standard control — vendor will not re-cert firmware with MFA; FDA 510(k) burden too high
4. **The threat being addressed** — mapped to specific STRIDE-HC scenarios by ID (Step 2's output is referenced, not duplicated)
5. **The compensating control deployed** — MFA shim Pattern C
6. **Standards mapping** — HIPAA §164.308, ISO 14971 cl.7, AAMI TIR57, FDA §524B
7. **Sign-offs** — CISO, clinical engineering, regulatory affairs, CMO
8. **Review cadence** — matches the tier from MDRS (quarterly for CRITICAL)

Notice the explicit cross-references in the example file:

```
| Linked STRIDE-HC threat model | stride-hc-templates/examples/infusion-pump.md |
| Current MDRS score and tier   | 8.175 → CRITICAL                              |
```

The CJR is the **evidence artifact** you show an FDA auditor, a HIPAA Security Rule reviewer, or your board. It justifies *why* you chose the compensating control over the standard one and *why* that's appropriate for this device's tier.

**Output of Step 4:** a signed, dated, audit-ready document.

---

## Step 5 — Empirically prove the control works → Test Harness

Open: [`test-harness/README.md`](./test-harness/README.md) and [`test-harness/METHODOLOGY.md`](./test-harness/METHODOLOGY.md).

A CJR is paperwork. Auditors increasingly ask: *"You claim this compensating control works. Show me data."* That's what the test harness is for.

It's a Dockerised multi-container environment:

```
docker compose up

┌─────────────────┐       ┌──────────────────────┐       ┌──────────────┐
│  Attacker       │       │ Compensating control │       │ Pump emulator│
│  (5 scenarios,  │  ───▶ │ (IPS / segmentation /│  ───▶ │ (VxWorks-like│
│   mapped to     │       │  PAM)                │       │  responses)  │
│   STRIDE)       │       └──────────────────────┘       └──────────────┘
│  - ARP poison   │                  │
│  - firmware inj │                  ▼
│  - cleartext HL7│           Results CSV (with-control vs without-control)
│  - DoS flood    │
│  - default cred │
└─────────────────┘
```

The five attack scenarios in [`test-harness/attacker/scenarios/`](./test-harness/attacker/scenarios) map 1-to-1 to the STRIDE-HC letters from Step 2. Each runs twice — once with the compensating control enabled, once without — and writes to [`test-harness/results/sample-results.csv`](./test-harness/results/sample-results.csv).

**Output of Step 5:** a CSV with empirical pass/fail evidence per scenario, which you attach to the CJR as Section 6 evidence ("control effectiveness validated by harness run XYZ on YYYY-MM-DD").

---

## Step 6 — Deploy the actual hardware control → MFA Shim (Pattern C)

Open: [`mfa-shim/README.md`](./mfa-shim/README.md) — reference design, hardware BOM, FDA considerations.

The MFA shim is the only artifact in the suite that's a **specific compensating control**, not a framework. It's the Pattern C from the paper: an inline device that sits between the technician's laptop and the medical device's service port, intercepts the connection, requires the technician to authenticate via TOTP + session binding, then proxies the cleartext service-mode session while recording every byte for forensic accountability.

The reference design at [`mfa-shim/prototype/`](./mfa-shim/prototype/) is the Python implementation with three components:

| File | Role |
|---|---|
| [`totp_gate.py`](./mfa-shim/prototype/totp_gate.py) | The authentication gate (TOTP, window tolerance, lockout, per-user rate limiting) |
| [`session_recorder.py`](./mfa-shim/prototype/session_recorder.py) | Forensic session recording with SIEM forwarding |
| [`tamper_detector.py`](./mfa-shim/prototype/tamper_detector.py) | Tamper sensors + emergency stop |

37 unit tests prove each component behaves correctly under adversarial conditions (replay, lockout bypass, sensor failures, concurrent authentication, etc.). Run them with:

```bash
cd mfa-shim/prototype
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

[`mfa-shim/FDA-CONSIDERATIONS.md`](./mfa-shim/FDA-CONSIDERATIONS.md) addresses the regulatory question of inline-device modification to a cleared medical device — read this before any clinical deployment.

**Output of Step 6:** a deployable reference design with FDA-considered architecture, ready for adaptation by a vendor or HDO building the production version.

---

## How the artifacts cross-reference each other

You can verify the integration claim by following the explicit cross-links inside the worked examples:

- The **CJR** [`cjr-no-mfa-infusion-pump.md`](./cjr-templates/examples/cjr-no-mfa-infusion-pump.md) names its source STRIDE-HC threat model and MDRS tier in Section 1.
- The **STRIDE-HC** worked example references the **CCD** dimension of MDRS in its CAW rationale.
- The **test harness** [`METHODOLOGY.md`](./test-harness/METHODOLOGY.md) labels each scenario with the STRIDE-HC letter it instantiates.
- The **MFA shim** is referenced by name in the STRIDE-HC Tampering category as a Pattern C compensating control.

This is the integration the paper claims: not five tools sharing a directory, but five tools sharing a workflow.

## Where to go next

| If you want to… | Read |
|---|---|
| Build a STRIDE-HC threat model from scratch | [`stride-hc-templates/WALKTHROUGH.md`](./stride-hc-templates/WALKTHROUGH.md) |
| Write a CJR for a new compensating control | [`cjr-templates/WALKTHROUGH.md`](./cjr-templates/WALKTHROUGH.md) — 30-minute first-author tutorial |
| Run the test harness | [`test-harness/README.md`](./test-harness/README.md) |
| Understand the MDRS methodology | [`mdrs-calculator/docs/methodology.md`](./mdrs-calculator/docs/methodology.md) |
| Adapt the MFA shim for production hardware | [`mfa-shim/ARCHITECTURE.md`](./mfa-shim/ARCHITECTURE.md) + [`mfa-shim/FDA-CONSIDERATIONS.md`](./mfa-shim/FDA-CONSIDERATIONS.md) |
| Cite this work | [`README.md`](./README.md) — Citing this work section |
