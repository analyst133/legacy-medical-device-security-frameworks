# STRIDE-HC Templates

Threat-modelling templates for legacy medical devices, implementing the STRIDE-HC framework defined in [Mohiuddin, Bernia & Gong (2026), §4](https://doi.org/10.30574/ijsra.2026.19.2.1164). The templates support the dual threat model — network attacker and physical/insider attacker — across both legacy device archetypes.

**[Open the interactive STRIDE-HC builder →](https://analyst133.github.io/legacy-medical-device-security-frameworks/stride-hc-templates/)** — no install required.

## What is STRIDE-HC?

STRIDE-HC adapts Microsoft's STRIDE threat-modelling methodology for clinical legacy environments through four modifications:

1. **Each threat category is recontextualised** for clinical legacy device constraints (no patching, no encryption, no audit logging, hardcoded credentials).
2. **Clinical Availability Weights (CAW)** reflect the heightened consequence of Denial of Service in environments where availability supports patient safety.
3. **Mitigations draw from the Compensating Controls Playbook** (paper Section 3, this repository's `cjr-templates/` artifact), maintaining framework coherence.
4. **The physical attacker is modelled as a co-equal threat surface alongside the network attacker** for every STRIDE category.

The templates also distinguish between two **device archetypes** with substantively different threat profiles:

- **Archetype 1**: General-purpose-OS legacy (Windows XP, Windows 7, etc.). Examples: PACS workstations, imaging modality consoles, laboratory analysers, pharmacy automation. Application allowlisting and host-based controls are technically feasible.
- **Archetype 2**: Embedded RTOS legacy (VxWorks, QNX, ThreadX) or proprietary firmware. Examples: large-volume infusion pumps, ventilators, physiological monitors. Compensating controls are exclusively network-adjacent and physical.

## What's in this directory

```
stride-hc-templates/
├── README.md                          # This file
├── stride-hc-template.md              # Markdown template (human-friendly)
├── stride-hc-schema.yaml              # YAML schema (tooling-friendly)
├── stride-hc-schema.json              # JSON schema (validation-friendly)
├── examples/
│   ├── infusion-pump.md               # Archetype 2 worked example
│   ├── infusion-pump.yaml             # Same example in YAML
│   ├── pacs-workstation.md            # Archetype 1 worked example
│   └── pacs-workstation.yaml          # Same example in YAML
└── scenario-library/
    ├── archetype-1-scenarios.md       # Library of common scenarios for general-purpose-OS legacy
    └── archetype-2-scenarios.md       # Library of common scenarios for embedded RTOS legacy
```

## How to use the templates

**First time using these templates? Start with [`WALKTHROUGH.md`](./WALKTHROUGH.md)** — a 30-minute tutorial that takes you from blank page to completed threat model with a worked example. The summary below is a reference for users who have done one already.

### For threat-model authors

1. Identify the device's **archetype** (general-purpose-OS or embedded RTOS) per paper Section 4.2.
2. Copy `stride-hc-template.md` to a new file named for the device (e.g., `infusion-pump-empump-volumetric.md`).
3. Populate the device profile section.
4. For each STRIDE category, draw network-attacker and physical/insider scenarios from the relevant archetype scenario library, adding device-specific scenarios as needed.
5. Identify detection methods drawn from the Framework V monitoring categories (paper Section 7).
6. Map each scenario to compensating controls from paper Section 3 / the CJR templates.
7. Confirm the Clinical Availability Weights (defaults: DoS=1.5, S/I=1.2, T/E=1.1, R=0.9).
8. Deliver the completed model to its downstream consumers — see **Where the output goes** below.

### Where the output goes

A completed STRIDE-HC threat model is an **input to four downstream artifacts**, not a standalone deliverable:

| Downstream | What STRIDE-HC provides | Handoff |
|---|---|---|
| **FDA §524B premarket submission** (vendors) | The threat-model deliverable required by 2023 cybersecurity guidance | Attach as Appendix to your premarket submission |
| **ISO 14971 risk management file** (vendors + HDOs) | Hazard identification (cl.5) and risk estimation (cl.6) records | Attach as the security-hazard section of your risk management file |
| **AAMI TIR57 security risk records** | The security risk identification activities TIR57 requires | Reference by ID in your TIR57 records |
| **CJR documents** ([`../cjr-templates/`](../cjr-templates/)) | The threat each compensating control is justified against | Each STRIDE-HC scenario you cannot fully mitigate produces a CJR; cross-reference the STRIDE-HC scenario ID inside the CJR |
| **MDRS calculator** ([`../mdrs-calculator/`](../mdrs-calculator/)) | Empirical input to the CCD (Compensating-Control Deficit) score | Re-run MDRS after deploying controls; the CCD score should improve |

**Review cadence:**
- After any **firmware update** by the vendor
- After any **network architecture change** affecting the device
- After any **incident** involving the device or a peer device
- Otherwise **annually** for production-deployed legacy devices

**Typical sign-offs:**
- Clinical / biomedical engineering — clinical accuracy
- InfoSec / CISO office — threat-model technical correctness
- Quality / regulatory affairs — standards alignment (FDA, ISO 14971, AAMI)
- For HDOs with life-sustaining devices: also CMO or service-line chief for DoS scenarios

### For tooling integration

The YAML and JSON schemas allow STRIDE-HC threat models to be stored, version-controlled, queried, and rendered programmatically. A typical workflow:

```bash
# Validate a YAML threat model against the schema
yamllint examples/infusion-pump.yaml
# (Pair with a JSON Schema validator for full type checking.)

# Render a YAML threat model as Markdown
# (Renderer not included in this repository; the schema is stable enough for
#  third-party renderers to be straightforward.)
```

The schemas explicitly model the STRIDE category, attacker class (network or physical/insider), scenario, detection method, mitigation, and applicable archetype, enabling downstream queries such as "show all scenarios mitigated by network-layer logging" or "show all Archetype 2 physical-attacker scenarios for category D (DoS)".

## Standards alignment

STRIDE-HC threat models align directly with:

- **ISO 14971:2019 cl.5–6** — hazard identification, risk estimation
- **AAMI TIR57:2016** — security risk identification activities
- **FDA 2023 cybersecurity guidance §524B** — threat-model deliverable expectation in premarket submissions
- **MITRE ATT&CK for ICS** — particularly TA0104 (Inhibit Response Function) and TA0105 (Impair Process Control)
- **OWASP IoT Attack Surface Areas** — for the attack-surface decomposition

## Contributing

Contributions are welcome:

- **Additional worked examples** for under-represented device classes (ventilators, MRI consoles, anaesthesia systems, dialysis machines, etc.)
- **Additional scenarios** for the scenario libraries
- **Mappings to other taxonomies** (MITRE ATT&CK Enterprise, NIST CSF Detect functions)

See top-level [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Licence

Apache License 2.0. See top-level [`LICENSE`](../LICENSE).
