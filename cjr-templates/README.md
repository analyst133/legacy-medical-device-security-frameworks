# Control Justification Record (CJR) Templates

Templates for documenting compensating-control selections per paper Section 3.5. CJRs serve as **shared evidence artifacts** across multiple regulatory and standards regimes:

- **HIPAA Security Rule** (45 CFR §164.308): risk analysis and risk management documentation
- **ISO 14971:2019** clause 7 (risk control) and clause 8 (residual risk evaluation)
- **AAMI TIR57:2016**: security risk control activities
- **AAMI TIR97**: postmarket cybersecurity for legacy devices
- **FDA 2023 cybersecurity guidance** (Section 524B FD&C Act): postmarket cybersecurity evidence

A single, well-authored CJR can satisfy documentation requirements across all of these without requiring separate, redundant authoring exercises in each domain.

## What's a CJR for?

When a healthcare delivery organisation (or a manufacturer engaged with a customer) selects a compensating control to substitute for a standard control that the device cannot support, that selection requires explicit, defensible documentation. A CJR captures:

1. **The standard control that cannot be applied** — and why (technical infeasibility, FDA clearance constraint, vendor end-of-life, manufacturer policy).
2. **The compensating control(s) selected** — with reference to the Compensating Controls Playbook (paper Tables 2 and 3).
3. **The threat addressed** — mapped to STRIDE-HC categories.
4. **The residual risk** — evaluated per ISO 14971 clause 8.
5. **Normative references** — the standards and guidance that justify the selection.
6. **Approval authority** — typically CISO and Director of Clinical Engineering jointly.
7. **Review cadence** — annually or after material change.

CJRs are also the primary input to the MDRS Compensating Control Deficit (CCD) score: the inventory of CJRs for a device determines its CCD, which feeds into the device's tier.

## What's in this directory

```
cjr-templates/
├── README.md                          # This file
├── cjr-template.md                    # Markdown template (human-friendly)
├── cjr-schema.yaml                    # YAML schema (illustrative example)
├── cjr-schema.json                    # JSON Schema for validation
└── examples/
    ├── cjr-no-mfa-infusion-pump.md           # Compensating for absent MFA
    ├── cjr-no-encryption-pacs.md             # Compensating for cleartext DICOM
    └── cjr-leaked-service-pin.md             # Compensating for publicly disclosed service credential
```

## How to use

### For HDOs

1. For each device-constraint pair in your inventory, create a CJR using `cjr-template.md` as the base.
2. Reference paper Tables 2 and 3 to identify candidate compensating controls.
3. Capture the residual risk evaluation in the same record — this satisfies the ISO 14971 cl.8 requirement and avoids document duplication.
4. Have the record reviewed and approved by both clinical engineering and information security. Joint sign-off is operationally important: clinical engineering owns clinical safety; InfoSec owns security; legacy device security sits at the intersection.
5. Store CJRs in your existing risk-management documentation system (Archer, ServiceNow GRC, RiskWatch, internal SharePoint). The Markdown form is intentionally simple to facilitate import.
6. Schedule annual review or trigger review on material change (vendor advisory, new vulnerability disclosure, infrastructure change).

### For manufacturers

CJRs can serve manufacturers in two distinct contexts:

1. **As guidance to customers.** Where a manufacturer cannot resolve a constraint in the device itself but can describe operationally validated compensating controls, publishing CJR-format guidance assists customer compliance with HIPAA, ISO 14971, and AAMI TIR57 obligations.
2. **As internal documentation.** When the manufacturer is itself the operator of legacy devices in production environments (manufacturing, R&D, field-service simulation), CJRs document control selection in the same way HDOs use them.

For FDA 524B postmarket evidence, manufacturers may publish a CJR-aligned response to security advisories — describing the compensating controls customers can apply pending vendor patch availability.

### For tooling integration

The YAML schema (`cjr-schema.yaml`) and JSON Schema (`cjr-schema.json`) enable CJRs to be authored, version-controlled, queried, and rendered programmatically. Common workflows:

- **Bulk authoring**: generate skeleton CJRs from device inventory + applicable constraint types.
- **Coverage analysis**: query the CJR corpus to identify devices with incomplete coverage (this directly feeds CCD scoring).
- **Audit support**: filter CJRs by normative reference (HIPAA section, ISO 14971 clause, FDA guidance section) for regulator-specific evidence packs.

## Standards alignment

Each CJR field is mapped to one or more standards regimes. The full mapping is documented in `cjr-template.md`. Summary:

| CJR field | HIPAA | ISO 14971 | AAMI TIR57/97 | FDA 524B |
|---|---|---|---|---|
| Constraint and standard control | §164.308(a)(1)(ii)(A) | cl.5 (hazard ID) | TIR57 §4 | §VII.A.1 |
| Compensating control | §164.308(a)(1)(ii)(B) | cl.7 (risk control) | TIR57 §6 | §VII.A.4 |
| Threat addressed | §164.308(a)(1)(ii)(A) | cl.5–6 | TIR57 §4–5 | §VII.A.1 |
| Residual risk | §164.308(a)(1)(ii)(C) | cl.8 (residual eval) | TIR57 §7; TIR97 §6 | §VII.A.6 |
| Approval | §164.308(a)(2) (assigned security responsibility) | cl.4.2 (mgmt responsibilities) | TIR57 §3 | §VII.A.5 |
| Review cadence | §164.308(a)(8) (evaluation) | cl.10 (postmarket info) | TIR97 §8 | §VII.B (postmarket) |

## Licence

Apache License 2.0. See top-level [`LICENSE`](../LICENSE).
