# Legacy Medical Device Security Frameworks

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20113684.svg)](https://doi.org/10.5281/zenodo.20113684)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)

Open-source companion artifacts for the paper **"A Practical Cybersecurity Framework for Legacy Medical Devices"**. Five integrated, practitioner-oriented frameworks for healthcare delivery organisations (HDOs) and medical device manufacturers operating under the constraints of legacy clinical environments.

> **Status.** Research artifact suite. Suitable for evaluation, adaptation, and extension. Not a regulated medical device. Do not deploy in clinical production without independent validation appropriate to your environment.

## Why this exists

A substantial fraction of clinical medical devices run end-of-life operating systems or firmware that cannot support standard cybersecurity controls. Existing frameworks (NIST, IEC 62443, FDA guidance, HSCC HIC-MaLTS, AAMI TIR57/TIR97) provide necessary scaffolding but consistently underserve two threat profiles: **(1) the irreversible-consequence risk profile** of life-sustaining devices, and **(2) the physical and insider attacker** with legitimate device proximity. This repository operationalises a five-framework response, grounded in ISO 14971:2019.

## The five artifacts

| # | Artifact | Status | Description |
|---|----------|--------|-------------|
| 1 | [**MDRS Calculator**](./mdrs-calculator/) | Production | Reference implementation of the Medical Device Risk Score with irreversibility-driven tier floor and CCD promoter. Web-based; no build tooling. |
| 2 | [**STRIDE-HC Templates**](./stride-hc-templates/) | Production | Threat-modelling templates for clinical legacy environments. Markdown for humans; YAML/JSON for tooling. Two worked examples covering both device archetypes. |
| 3 | [**CJR Templates**](./cjr-templates/) | Production | Control Justification Record templates aligned to HIPAA Security Rule, ISO 14971 cl.7–8, AAMI TIR57, and FDA 524B postmarket cybersecurity expectations. |
| 4 | [**Test Harness**](./test-harness/) | Functional prototype | Dockerised multi-container test environment for empirical evaluation of compensating-control effectiveness. Includes infusion pump emulator and STRIDE-mapped attack scenarios. |
| 5 | [**MFA Shim (Pattern C)**](./mfa-shim/) | Functional prototype | Software reference design for the inline service-port multi-factor authentication shim addressing the physical-attacker threat surface. Linux daemon with TOTP gating, session recording, and tamper detection. |

## Quick start

**Every artifact has an interactive page in your browser — no install required:**

| Artifact | What it does |
|---|---|
| [**MDRS Calculator**](https://analyst133.github.io/legacy-medical-device-security-frameworks/mdrs-calculator/) | Score a device across five dimensions → tier + next-steps panel |
| [**STRIDE-HC Builder**](https://analyst133.github.io/legacy-medical-device-security-frameworks/stride-hc-templates/) | Pick archetype → tick scenarios → download filled `.md` + `.yaml` |
| [**CJR Builder**](https://analyst133.github.io/legacy-medical-device-security-frameworks/cjr-templates/) | Fill 10 sections → download a defensible Control Justification Record |
| [**Test Harness Results Explorer**](https://analyst133.github.io/legacy-medical-device-security-frameworks/test-harness/) | (Scenario × control) heatmap from a harness CSV — sample auto-loaded |
| [**MFA Shim Demo**](https://analyst133.github.io/legacy-medical-device-security-frameworks/mfa-shim/) | Architecture diagram + working RFC 6238 TOTP gate in the browser |

- **First time here?** Read [`SETUP.md`](./SETUP.md) — step-by-step install for Linux, macOS, and Windows.
- **Want to understand how the artifacts fit together?** Read [`WALKTHROUGH.md`](./WALKTHROUGH.md) — cross-artifact tour using a worked infusion-pump example.

For the full suite locally:

```bash
git clone https://github.com/analyst133/legacy-medical-device-security-frameworks.git
cd legacy-medical-device-security-frameworks

# MDRS calculator (no install required)
open mdrs-calculator/index.html      # macOS
xdg-open mdrs-calculator/index.html  # Linux
start mdrs-calculator/index.html     # Windows

# Run the test harness
cd test-harness && docker compose up

# Run the MFA shim prototype
cd ../mfa-shim/prototype && pip install -r requirements.txt && python -m pytest
```

## Citing this work

This repository is archived on Zenodo. Use the **concept DOI** to cite the artifact suite — it always resolves to the latest version:

- Concept DOI: [10.5281/zenodo.20113684](https://doi.org/10.5281/zenodo.20113684)
- v1.0.0 release: [10.5281/zenodo.20113685](https://doi.org/10.5281/zenodo.20113685)

```bibtex
@software{mohiuddin2026legacy_artifacts,
  title   = {Legacy Medical Device Security Frameworks: Companion Artifacts},
  author  = {Mohiuddin, Khaja T. and Bernia, Bradley and Gong, Wenbo},
  year    = {2026},
  doi     = {10.5281/zenodo.20113684},
  url     = {https://doi.org/10.5281/zenodo.20113684},
  version = {v1.0.0}
}

@article{mohiuddin2026legacy,
  title  = {A Practical Cybersecurity Framework for Legacy Medical Devices},
  author = {Mohiuddin, Khaja T. and Bernia, Bradley and Gong, Wenbo},
  year   = {2026},
  note   = {Submitted}
}
```

A `CITATION.cff` file is provided in the repository root for GitHub's "Cite this repository" feature.

## Standards alignment

The frameworks are explicitly aligned to:

- **ISO 14971:2019** — Medical device risk management lifecycle
- **AAMI TIR57:2016** — Security risk management
- **AAMI TIR97** — Postmarket security for legacy devices
- **ISO/IEC 81001-5-1:2021** — Health software security lifecycle
- **NIST CSF 2.0** (2024) and **NIST SP 800-82r3** (2023)
- **IEC 62443-3-3 / 62443-4-2**
- **HIPAA Security Rule** (45 CFR Part 164)
- **U.S. FDA 2023 cybersecurity guidance** (Section 524B FD&C Act)
- **HSCC HIC-MaLTS** (2023) — complementary
- **MITRE Rubric for Applying CVSS to Medical Devices** (2020)
- **MITRE ATT&CK for ICS** (TA0104, TA0105)

## For HDOs and manufacturers

The frameworks are designed for both audiences:

- **HDOs** use the playbook to structure compensating controls, MDRS to prioritise remediation, the segmentation model to design clinical networks, and the behavioural monitoring framework to operationalise detection.
- **Medical device manufacturers** use STRIDE-HC for FDA premarket threat-model deliverables, MDRS to complement ISO 14971 risk management files, the constraint categories to inform MDS² disclosures, and the compensating-controls catalogue to structure customer security advisories under FDA 524B postmarket obligations.

The Manufacturer–HDO interface (paper §8) treats the artifacts as shared instruments enabling structured dialogue about residual risk and required compensating controls.

## Contributing

Contributions welcome. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for guidance on:

- Adding new constraint entries to the Compensating Controls Playbook
- Submitting STRIDE-HC scenarios for additional device classes
- Extending the test harness to new device archetypes
- Reporting bugs in the MDRS calculator or MFA shim prototype

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md).

## Licence

Apache License 2.0. See [`LICENSE`](./LICENSE).

The patent grant in Apache-2.0 applies in particular to the Pattern C MFA shim reference design, which is published as a research artifact and is intended to remain freely usable in defensive applications.

## Disclaimer

This repository is research output. Nothing here constitutes regulatory advice. The frameworks are aligned to standards but their application in any specific clinical environment is the responsibility of the deploying organisation, in consultation with their regulatory affairs, clinical engineering, and information security functions. Specific compensating-control selections must be validated against the deploying organisation's risk acceptance criteria and documented per applicable regulatory expectations.

The MFA shim reference design is **not** a cleared medical device. Inline insertion of a third-party device into a medical device's service port may, under FDA 21 CFR 820 and the EU MDR, constitute a modification requiring clearance. See [`mfa-shim/FDA-CONSIDERATIONS.md`](./mfa-shim/FDA-CONSIDERATIONS.md).
