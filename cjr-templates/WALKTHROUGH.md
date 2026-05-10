# CJR Walkthrough — from constraint to approved record in 30 minutes

A first-time-author tutorial. We build a complete Control Justification Record from scratch using the same legacy infusion pump that runs through MDRS, STRIDE-HC, and the top-level walkthrough. The completed CJR you build here matches the worked example at [`examples/cjr-no-mfa-infusion-pump.md`](./examples/cjr-no-mfa-infusion-pump.md) — you can check against it at any step.

**Estimated time:** 30 minutes the first time, 15 minutes once you've done one.

**Audience:** clinical engineers, security architects, regulatory affairs staff, and HDO compliance leads. No prior risk-management formalism required; the template handles the structure and the standards mapping. Your job is to fill in the device-specific facts.

## When you need a CJR

You need one whenever you choose a **compensating control** in place of a standard control that the device cannot support. Examples:

- Device doesn't support MFA → compensate with upstream PAM gateway
- Device transmits cleartext PHI → compensate with VLAN segmentation
- Device has hardcoded service-port credentials → compensate with inline MFA shim
- Device cannot run endpoint detection → compensate with network-side IDS

A CJR is what makes that choice **defensible**: regulator-readable, audit-readable, and traceable. Without one, the compensating-control decision is invisible to ISO 14971 cl.7 (risk control), HIPAA §164.308(a)(1)(ii)(B) (risk management), and FDA §524B postmarket evidence reviews.

## What you need before starting

Have these inputs in front of you:

- **The completed STRIDE-HC threat model** for the device. The CJR is the *resolution document* for one or more threat scenarios that model identified. If you don't have a threat model yet, do [`../stride-hc-templates/WALKTHROUGH.md`](../stride-hc-templates/WALKTHROUGH.md) first.
- **The current MDRS tier** for the device (CRITICAL / HIGH / MEDIUM / LOW). Open [`../mdrs-calculator/`](../mdrs-calculator/) if you don't have one.
- **Vendor documentation** stating the constraint — service manual, MDS² disclosure, vendor advisory, security bulletin. The CJR must cite the source of truth for the constraint.
- **Knowledge of available compensating controls** at your organisation — what PAM platform you run, what IDS/IPS you have, what your VLAN architecture looks like.

Don't have all of these? You can still draft the CJR with "TBD" markers and use the gaps as the next-action list. A CJR with explicit unknowns is more useful than one with assumed values.

---

## Step 1 — Identify the device (Section 1 of the template, ~3 minutes)

Copy [`cjr-template.md`](./cjr-template.md) to a new file. Recommended naming: `cjr-<device-tag>-<sequence>-<constraint>.md`. For our pump compensating for absent MFA: `cjr-empump-001-mfa.md`.

Section 1 is the device identification table. The CJR is the **junction artifact** of the workflow — every other field downstream refers to this section. Get it right and the rest is mechanical.

For our pump, fill in:

| Field | Value | Where this comes from |
|---|---|---|
| Device name and model | ExampleMed Volumetric Infusion Pump v3.2 | Asset register |
| Manufacturer | ExampleMed Inc. | Asset register |
| Device class (FDA) | Class II | Vendor MDS² |
| Device archetype | Archetype 2 (embedded RTOS legacy — VxWorks 6.9) | STRIDE-HC model |
| MDS² reference | ExampleMed-IP3.2-MDS2-2024 | Vendor documentation |
| Asset inventory IDs | Asset register reference: pump-vlan-volumetric-ip32 | Your inventory system |
| Deployment count | 240 units across ICU and oncology | Asset register |
| **Linked STRIDE-HC threat model** | `stride-hc-templates/examples/infusion-pump.md` | Cross-reference to the threat-model file |
| **Current MDRS score and tier** | 8.175 → CRITICAL | Output of the MDRS calculator |

The bottom two rows are the **integration claim of the framework suite**. The CJR doesn't replicate the threat model or the risk score; it cites them. That's what makes the artifacts compose into one workflow rather than five overlapping documents.

**Choose the CJR-ID.** Pattern: `CJR-<device-shortcode>-<sequence>-<constraint-shortcode>`. For our example: `CJR-EMPump-001-MFA`. Other CJRs for the same device get sequential numbers (002, 003) to make it easy to grep across them.

---

## Step 2 — State the standard control and the constraint (Section 2, ~4 minutes)

This is the *what the device cannot do, and why*.

### Section 2.1 — The standard control

State the standard control in **one sentence**, in industry-recognized language. Examples:
- "Multi-factor authentication for administrative access to the device management interface."
- "Encryption of patient data in transit using TLS 1.2 or above."
- "Per-user account authentication with audit logging for all administrative actions."

For our pump: *"Multi-factor authentication for administrative access to the device management interface."*

### Section 2.2 — The constraint

Tick the relevant box from the standard list (the template has a checkbox menu of common constraint types). Add a clear paragraph stating the constraint.

For our pump, you'd tick:
- [x] Multi-factor authentication not supported by device
- [x] Shared or hardcoded credentials (network-side)

And write: *"MFA not supported. The device exposes a management interface on TCP/8080 protected only by a hardcoded service-mode password documented in the vendor service manual. The device firmware does not support per-user accounts, MFA, or third-party authentication delegation."*

### Section 2.3 — The constraint detail

This is the **most important text in the CJR**. An auditor will read this paragraph to decide whether your compensating-control choice is reasonable. Three rules:

1. **Cite the source of truth** — vendor advisory ID, MDS² section, service manual page, support ticket. If the constraint is "vendor says so", name the vendor document.
2. **State the *nature* of the constraint** — technical, regulatory, vendor-policy, FDA-clearance, or some combination. For legacy devices the most common combination is technical-plus-regulatory: the device *could* be modified but FDA clearance burden prevents it.
3. **State why the constraint won't go away soon** — vendor roadmap, FDA clearance status, EOL date. This justifies the compensating-control approach rather than waiting for vendor remediation.

For our pump, the detail paragraph cites vendor advisory ExampleMed-2024-03, explains the FDA 510(k) burden, and states the constraint is both technical (firmware can't be modified) and regulatory (vendor cannot ship without re-clearance). Read [`examples/cjr-no-mfa-infusion-pump.md`](./examples/cjr-no-mfa-infusion-pump.md) Section 2.3 for the full text.

---

## Step 3 — Map the threat to STRIDE-HC scenarios (Section 3, ~5 minutes)

A constraint is not a threat. A constraint *exposes* threats. Section 3 is where you translate the constraint into specific threat scenarios using the STRIDE-HC framework.

### Section 3.1 — STRIDE-HC mapping

Tick the categories the constraint exposes. For our pump's missing MFA, the relevant categories are:

- [x] **S — Spoofing** (legitimate-credential abuse by unauthorised user)
- [x] **R — Repudiation** (no per-user logging on device)
- [x] **E — Elevation of Privilege** (attacker with credential gains administrative control)

Tampering and Information disclosure may also apply downstream (once you have admin access you can tamper or exfiltrate). For the purposes of *this* CJR (which is about MFA specifically), the primary categories are S, R, E. Other consequences are addressed by other CJRs.

### Section 3.2 — The threat scenarios

This is where the STRIDE-HC model pays off. Copy the relevant scenarios from your threat model file. The CJR doesn't invent scenarios; it cites the ones your STRIDE-HC analysis already identified.

For our pump (drawn from [`../stride-hc-templates/examples/infusion-pump.md`](../stride-hc-templates/examples/infusion-pump.md)):

**Network-attacker scenarios:**
- Default credential exploitation via the management interface (credential is documented in publicly available service manuals)
- Lateral movement to peer pumps after credential reuse on a shared service account

**Physical/insider-attacker scenarios:**
- Service-mode credential abuse via service port using the same documented credential
- Vendor-impersonation social engineering using the documented credential

### Section 3.3 — Pre-control risk assessment

Score the threat **as it stands today, without the compensating control**. Three dimensions:

| Dimension | Bands | Pump example |
|---|---|---|
| **Likelihood** | Low / Medium / **High** | High — credential is publicly disclosed, attacker capability required is low |
| **Severity** | Low / Medium / **High** | High — successful exploit modifies therapy parameters on a Class II device — direct patient-safety implication |
| **Detectability** | Easy / Moderate / **Difficult** | Difficult — device has no authentication audit log; detection depends entirely on upstream observation |

Be honest. A High-High-Difficult pre-control assessment is a strong argument for the compensating control. A Low-Low-Easy pre-control assessment suggests the standard control may not actually be needed.

---

## Step 4 — Choose the compensating control and explain why (Section 4, ~8 minutes)

This is the substantive design work. Five subsections.

### Section 4.1 — Describe the control

State the control concretely. Not "PAM"; rather "Pattern A — Upstream PAM (privileged access management) gateway using CyberArk PSM v12.x, brokering all network connections to the pump management interface".

The level of detail should be enough for a reviewer to understand what was actually deployed, but not so much that the CJR becomes the deployment runbook. Save the runbook for Section 4.5.

### Section 4.2 — Reference the Playbook

Cite the entry from paper Tables 2 or 3. For our pump: "Paper §3.2 Table 2, 'MFA not supported' constraint. Pattern A described in §3.4." This makes the CJR's compensating-control choice traceable to the paper's published taxonomy.

### Section 4.3 — How the control addresses each scenario

Walk through **each scenario from Section 3.2** and explain how the control mitigates it. This is the most-scrutinised part of the CJR. Don't hand-wave; be mechanism-specific.

For our pump, four scenarios → four mitigation claims:

1. *Default credential exploit via mgmt interface* → "The hardcoded credential never leaves the vault; network discovery yields nothing useful."
2. *Lateral movement to peer pumps* → "Network ACL on pump VLAN allows TCP/8080 only from PAM gateway IP; lateral movement at this layer becomes impossible."
3. *Service-port credential abuse* → "PAM addresses network side only — physical service-port abuse requires a separate CJR (CJR-EMPump-003-ServicePort), referenced under §9 Linked records."
4. *Vendor-impersonation social engineering* → "PAM requires individual MFA; impersonation now requires compromising both an MFA factor and the user's credentials."

Notice scenario 3's response: *honesty matters*. If your compensating control doesn't fully cover the threat surface, say so and reference the complementary CJR that does. Pretending one CJR covers everything is the most common mistake in this artifact.

### Section 4.4 — Four design principles

For every compensating control choice, the paper requires four justifications:

| Principle | What it asks | Pump example |
|---|---|---|
| **Equivalent or superior protection** | Does the compensating control meet or exceed what the standard control would have provided? | Yes — MFA enforced at PAM gateway provides the same protection as native MFA from the user's perspective |
| **Independence** | Does the control depend on the same missing capability that caused the original constraint? | No — implemented entirely upstream in network architecture; does not depend on any pump capability |
| **Proportionality** | Is the control intensity appropriate to the device's MDRS tier? | Yes — pump is CRITICAL; PAM with MFA is the strongest network-layer control available for this constraint |
| **Auditability** | Are there normative references supporting this selection, and is the control's effect auditable? | Yes — HIPAA §164.312(b), ISO 14971 cl.7.4, AAMI TIR57 §6.3; all sessions logged with full keystroke capture |

A CJR that fails any of these four is a CJR that won't survive audit. If you can't tick all four convincingly, reconsider the control or accept the residual risk explicitly in Section 5.

### Section 4.5 — Implementation references

The operational link to actual deployment. List the technical specifics:

- Product / platform name and version (e.g., "CyberArk PSM v12.x")
- Network configuration (ACL rule, IP ranges, ports)
- Configuration files or change tickets
- MFA factor used (Duo Push, hardware token, etc.)
- Retention policy
- Service-request workflow / change-management process

This section is what a deployment auditor will compare against the actual production configuration. Keep it factual and current.

---

## Step 5 — Residual risk (Section 5, ~3 minutes)

Per ISO 14971 cl.8: even with the control deployed, **some risk remains**. State what.

### Section 5.1 — Re-score the three dimensions

Same dimensions as Section 3.3, this time post-control:

| Dimension | Before | After | Rationale |
|---|---|---|---|
| Likelihood | High | **Low** | Credential no longer network-discoverable; PAM enforces MFA |
| Severity | High | **High** | Unchanged. The control reduces *likelihood*, not the *consequence* if exploit succeeds. |
| Detectability | Difficult | **Easy** | PAM session logging provides full per-user visibility |

Severity often stays unchanged because compensating controls reduce the *probability* of compromise, not the *harm* if compromise occurs. State this explicitly.

### Section 5.2 — Acceptability

Reference your organisation's risk-acceptance criteria. State whether the residual is acceptable and why.

For our pump: residual is acceptable because the organisation's criteria (LMD-RISK-2026-001) require residual likelihood ≤ Low, validated detection capability, and quarterly monitoring review — all of which are met.

If residual is **not** acceptable, the CJR doesn't fail — it triggers Section 5.3 escalation.

### Section 5.3 — Risk acceptance authority

Who signed off on the residual. For above-threshold residual risk, typically:
- **CISO** (or designate) — primary
- **CMO** or service-line chief — concurrence required for clinical-impact-relevant risks
- For device manufacturers: appropriate executive per the organisation's quality management system

---

## Step 6 — Effectiveness rating (Section 6, ~2 minutes)

Three bands: High / Medium / Low. The rating must be **validated**, not asserted.

| Rating | Threshold | Validation method |
|---|---|---|
| **High** | Equivalent protection to the standard control | Penetration testing report + empirical test harness output |
| **Medium** | Partially addresses the threat; residual elevated but manageable | Design review + tabletop exercise |
| **Low** | Minimal mitigation; formal risk acceptance required | Justified acceptance with executive escalation |

For our pump, the rating is High because:
- Annual penetration test (Vendor: Pen Test Co, Report PT-2026-Q1-014) confirmed PAM enforcement effectiveness
- [`../test-harness/`](../test-harness/) scenario `05-eop-default-credential.py` confirms the control prevents credential exploitation when the PAM profile is enabled

**This is where the test harness becomes load-bearing**: it provides empirical evidence that turns an asserted "High" into a validated "High". Run the harness, attach the CSV output, cite the run ID.

---

## Step 7 — Normative references (Section 7, ~3 minutes)

List the standards, guidance, and regulatory provisions that justify the selection. For a CJR addressing missing MFA on a Class II device, the typical reference list is 8–12 entries spanning HIPAA, ISO 14971, AAMI TIR57, AAMI TIR97, FDA §524B, NIST SP 800-82r3, and HSCC HIC-MaLTS. See [`examples/cjr-no-mfa-infusion-pump.md`](./examples/cjr-no-mfa-infusion-pump.md) Section 7 for the full reference list to copy-and-adapt.

**Pattern: reference the *specific clause*, not the whole standard.** "HIPAA Security Rule §164.312(d)" is useful; "HIPAA" is not.

---

## Step 8 — Approval and review (Section 8, ~1 minute)

Fill the approval table. Two reviewers + two approvers + dates is the standard pattern:

| Role | Who |
|---|---|
| Author | The clinical engineer or security architect drafting the CJR |
| Reviewer (Clinical Engineering) | Senior clinical engineer or director |
| Reviewer (InfoSec) | Lead security architect or CISO designate |
| Approver (CISO) | CISO or designate |
| Approver (Director of Clinical Engineering) | Director of clinical engineering |

**Review cadence:**
- Annual (default for all CJRs)
- Plus trigger conditions: vendor security advisory, new firmware CVE, infrastructure change, PAM platform end-of-support, loss of MFA service availability

The trigger conditions are device- and control-specific. Be specific; "any change" triggers nothing because everyone tunes it out.

---

## Step 9 — Linked records (Section 9, ~1 minute)

The pointers to other artifacts in your evidence ecosystem:

| Record type | Purpose |
|---|---|
| STRIDE-HC threat model | The source of threat scenarios (Section 3) |
| MDS² disclosure | The vendor's security capability disclosure |
| Vendor security advisories | If the constraint is documented in a vendor advisory |
| Penetration test report | Validates Section 6 effectiveness rating |
| Test harness output | Empirical validation of Section 6 |
| Predecessor CJR | If this CJR replaces an earlier version |
| Related CJRs | Other constraints for the same device |

For our pump, the related-CJR field lists `CJR-EMPump-002-Encryption` and `CJR-EMPump-003-ServicePort`. **A device with CRITICAL tier usually needs multiple CJRs** because each constraint gets its own. Cross-linking makes the corpus navigable.

---

## Step 10 — Validate before submitting

Checklist:

- [ ] Section 1 cross-references both the STRIDE-HC threat model and the MDRS tier
- [ ] Section 2.3 cites the source-of-truth document for the constraint
- [ ] Section 3.2 scenarios are drawn from your STRIDE-HC model (not invented for the CJR)
- [ ] Section 4.3 walks through *every* scenario from 3.2 individually
- [ ] Section 4.4 ticks all four design principles convincingly
- [ ] Section 5.1 explains why each dimension changed (or didn't) post-control
- [ ] Section 6 cites *validation evidence* (pentest report ID, harness run CSV) — not just an assertion
- [ ] Section 7 references *specific clauses*, not whole standards
- [ ] Section 8 has both clinical engineering and InfoSec sign-off
- [ ] Section 9 links to related CJRs for the same device

**Compare against the worked examples:**
- [`examples/cjr-no-mfa-infusion-pump.md`](./examples/cjr-no-mfa-infusion-pump.md) — Pattern A compensating for missing MFA
- [`examples/cjr-no-encryption-pacs.md`](./examples/cjr-no-encryption-pacs.md) — VLAN segmentation compensating for cleartext PHI
- [`examples/cjr-leaked-service-pin.md`](./examples/cjr-leaked-service-pin.md) — MFA shim compensating for leaked service-port credential

If your CJR is much shorter than these (~150 lines), you've probably under-specified one of the sections.

---

## Common pitfalls

| Pitfall | Why it happens | Fix |
|---|---|---|
| **Constraint paragraph is hand-waving** | Author isn't sure why the device can't do X | Cite the source of truth (vendor doc, MDS², advisory). If you don't know, the answer is "TBD — pending vendor consultation". |
| **Scenarios in §3.2 don't appear in the STRIDE-HC model** | Author skipped the threat model step | Stop. Do [`../stride-hc-templates/WALKTHROUGH.md`](../stride-hc-templates/WALKTHROUGH.md) first. The CJR is the *response* to a threat model, not a substitute for one. |
| **§4.3 says "this control mitigates the threat" generically** | Lack of mechanism-specificity | Walk through each scenario individually. Say *how* the control affects each one. |
| **§4.4 ticks all four principles without explanation** | Pro forma compliance | If you can't write a one-sentence explanation per principle, the control may not actually be appropriate. |
| **§5 marks residual "Low" everywhere** | Optimism | Severity rarely drops post-control. Be honest about what doesn't change. |
| **§6 rates "High" without validation** | Empirical evidence is hard | Run the test harness. Cite the run ID. If you can't validate empirically, the rating should be Medium. |
| **§7 references whole standards** | Author copies a generic list | Reference specific clauses. Auditors check this. |
| **One CJR covers multiple constraints** | Author tries to bundle | One constraint per CJR. Cross-reference related CJRs in §9. |

---

## Where the CJR goes from here

A signed CJR is **input to four downstream consumers**:

| Consumer | What it does with the CJR |
|---|---|
| **HIPAA Security Rule risk analysis** (HDOs) | The CJR is the §164.308(a)(1)(ii)(B) risk-management record for this device-constraint pair |
| **ISO 14971 risk management file** (vendors + HDOs) | The CJR is the cl.7 risk-control measure and cl.8 residual-risk evaluation, in one record |
| **AAMI TIR57 / TIR97** | The CJR populates §6 (security risk control) and TIR97 §6.2 (postmarket security risk control) |
| **FDA §524B premarket / postmarket evidence packs** (vendors) | The CJR is the §VII.A.4 authentication-control evidence and §VII.A.6 residual-risk evaluation |
| **MDRS calculator** ([`../mdrs-calculator/`](../mdrs-calculator/)) | The CJR corpus for a device determines its **CCD** (Compensating-Control Deficit) score; more CJRs covering more constraints lower CCD, which improves the device's tier |

**Storage:** import the markdown into your existing GRC system (Archer, ServiceNow GRC, RiskWatch, internal SharePoint). The markdown form is intentionally simple to support automated import.

**Review cadence:** annual default. Early-trigger conditions per Section 8.

## Going further

- For the **paper-cited methodology** behind CJRs and the Compensating Controls Playbook, see paper §3.
- For the **integrated workflow** showing how CJRs connect to MDRS, STRIDE-HC, the test harness, and the MFA shim, see the top-level [`../WALKTHROUGH.md`](../WALKTHROUGH.md).
- For **tooling integration** — querying your CJR corpus programmatically, generating coverage reports, building audit-specific evidence packs — see the schemas at [`cjr-schema.yaml`](./cjr-schema.yaml) / [`cjr-schema.json`](./cjr-schema.json) and the "For tooling integration" section of [`README.md`](./README.md).
