# Frequently Asked Questions

Common questions about the framework suite, the artifacts, and how to use them. For first-time setup see [`SETUP.md`](./SETUP.md); for the integration narrative see [`WALKTHROUGH.md`](./WALKTHROUGH.md).

## About the framework

### What does "Archetype" mean? Is it a typo?

It's a deliberate term from paper §4. An archetype groups legacy medical devices into two fundamental classes that share **security-relevant characteristics** — so the same compensating-control logic applies to every device in that class:

| | **Archetype 1** | **Archetype 2** |
|---|---|---|
| Underlying tech | General-purpose OS (Windows XP/7, older Linux) on PC-class hardware | Embedded RTOS (VxWorks, QNX, ThreadX) or proprietary firmware |
| Examples | PACS workstations, imaging modality consoles, lab analysers, pharmacy automation | Infusion pumps, ventilators, patient monitors, dialysis controllers |
| Available controls | Host-based controls are *technically* feasible (EDR, app allowlist, host firewall) | Compensating controls must be **network-adjacent and physical only** — no agent can run on the device |

The split determines which scenario library applies (`stride-hc-templates/scenario-library/archetype-1-scenarios.md` vs `archetype-2-scenarios.md`), which compensating controls are available, and which threats matter most.

### How do STRIDE-HC and CJR fit together?

**STRIDE-HC** is the threat modeller: for one device, it produces a list of specific threat scenarios (network attacker + physical/insider attacker, across six categories) and candidate compensating controls. **CJR** is the justification document: for each compensating control you choose, it explains *what control you used instead of the standard one, why the standard one can't be applied, and how the substitution remains defensible* under HIPAA, ISO 14971, AAMI TIR57, and FDA §524B.

One STRIDE-HC threat model → typically 2–5 CJRs (one per constraint/control pair).

See [`WALKTHROUGH.md`](./WALKTHROUGH.md) for the end-to-end chain MDRS → STRIDE-HC → CJR → test harness → MFA shim with a worked infusion-pump example.

### What does MDRS stand for, and how is it different from CVSS?

**Medical Device Risk Score.** Five dimensions (CIS, ES, DCI, NEF, CCD) → composite → tier (CRITICAL / HIGH / MEDIUM / LOW) per paper §5.

Unlike CVSS:

- MDRS scores a **device** in its clinical context, not a single CVE.
- MDRS has an **irreversibility floor** (life-sustaining devices can't fall below HIGH).
- MDRS has a **Compensating-Control Deficit (CCD) promoter** — devices with poor compensating controls get bumped up a tier.
- MDRS produces an **action timeline** keyed to the tier (24 h / 30 d / 90 d / 12 mo).

CVSS is still useful inside the ES (exploitability) dimension. The two are complementary, not competing.

## About the artifacts

### Do I have to install anything to try the artifacts?

No. Every artifact has a live page that runs in your browser with no install:

- [Open the MDRS calculator](https://analyst133.github.io/legacy-medical-device-security-frameworks/mdrs-calculator/)
- [Open the STRIDE-HC builder](https://analyst133.github.io/legacy-medical-device-security-frameworks/stride-hc-templates/)
- [Open the CJR builder](https://analyst133.github.io/legacy-medical-device-security-frameworks/cjr-templates/)
- [Open the test harness results explorer](https://analyst133.github.io/legacy-medical-device-security-frameworks/test-harness/)
- [Open the MFA shim demo](https://analyst133.github.io/legacy-medical-device-security-frameworks/mfa-shim/)

If you want to run the source locally, see [`SETUP.md`](./SETUP.md).

### Why is the calculator a static HTML page, not a backend app?

Three reasons:

1. **No data leaves your browser.** Hospital security architects can score devices without trusting a remote service with sensitive inventory facts.
2. **No build, no install.** Open `index.html` and it works in any modern browser. Survives the next 10 years of JavaScript framework churn.
3. **Reviewable.** A reviewer reading `calculator.js` (332 lines) can audit the math against paper §5 in 20 minutes. A 50-MB SPA bundle is opaque.

### Why is the MFA shim a software prototype if the deployment target is hardware?

The Python prototype proves the **security mechanisms** (TOTP gate, session recording, tamper detection, lockout, replay protection) work correctly under adversarial conditions. 37 unit tests cover edge cases like concurrent authentication, sensor failure during heartbeat, and admin lockout reset.

The hardware port is a separate exercise — adapter wiring, hardened enclosure, tamper sensors, FDA pre-submission engagement. See [`mfa-shim/hardware/README.md`](./mfa-shim/hardware/README.md) for porting notes and [`mfa-shim/FDA-CONSIDERATIONS.md`](./mfa-shim/FDA-CONSIDERATIONS.md) for the regulatory analysis — read this before any clinical deployment.

### How does the test harness produce empirical control-effectiveness evidence?

Five attack scenarios mapped 1-to-1 to STRIDE-HC categories run against the emulated pump, with three compensating-control profiles toggleable via Docker Compose profiles (`ips`, `pam`, `segmentation`). Each `(scenario × control profile)` combination runs and writes its outcome (`SUCCESS` / `MITIGATED` / `BLOCKED` / `BLOCKED_AUTH` / `BLOCKED_NET` / `ERROR`) to a CSV. A full matrix run takes ~3 minutes; the result is a 5 × 5 grid showing exactly which controls block which threats.

See [`test-harness/METHODOLOGY.md`](./test-harness/METHODOLOGY.md) for experimental design, the expected outcome matrix, and statistical considerations. The [results explorer](https://analyst133.github.io/legacy-medical-device-security-frameworks/test-harness/) visualises the sample CSV as an interactive heatmap.

## Citation and licensing

### How do I cite this work?

Cite the **paper** for the research contribution and the **artifacts** (via Zenodo concept DOI) for the implementation:

```bibtex
@article{mohiuddin2026legacy,
  title     = {A Practical Cybersecurity Framework for Legacy Medical Devices},
  author    = {Mohiuddin, Khaja T. and Bernia, Bradley and Gong, Wenbo},
  journal   = {International Journal of Science and Research Archive},
  volume    = {19},
  number    = {2},
  pages     = {1178--1195},
  year      = {2026},
  month     = {May},
  publisher = {GSC Online Press},
  doi       = {10.30574/ijsra.2026.19.2.1164},
  url       = {https://doi.org/10.30574/ijsra.2026.19.2.1164},
  issn      = {2582-8185}
}

@software{mohiuddin2026legacy_artifacts,
  title   = {Legacy Medical Device Security Frameworks: Companion Artifacts},
  author  = {Mohiuddin, Khaja T. and Bernia, Bradley and Gong, Wenbo},
  year    = {2026},
  doi     = {10.5281/zenodo.20113684},
  url     = {https://doi.org/10.5281/zenodo.20113684},
  version = {v1.0.0}
}
```

The concept DOI (`10.5281/zenodo.20113684`) always resolves to the latest version. The v1.0.0 versioned DOI (`10.5281/zenodo.20113685`) pins to the initial release. A [`CITATION.cff`](./CITATION.cff) file is provided for GitHub's automatic "Cite this repository" feature.

### What licence is the code under? Can I use it commercially?

Apache License 2.0. You can use it commercially, modify it, distribute it, and sublicense it — **subject to** the standard Apache-2.0 conditions: include the licence text, preserve attribution, and don't sue contributors over patents related to the code.

The Apache-2.0 patent grant matters specifically for the Pattern C MFA shim reference design. The design is published as research output; contributors cannot subsequently assert patent claims against users.

### Can I include the artifacts in a medical device submission to FDA?

The artifacts can serve as **evidence** in cybersecurity submissions per §524B — specifically as threat-model deliverables (STRIDE-HC), compensating-control documentation (CJR), and empirical effectiveness evidence (test harness output). The artifacts themselves are **research output, not regulated medical devices**.

Inline insertion of the MFA shim into a cleared device's service port may, under jurisdiction-specific rules, constitute modification requiring regulatory engagement — see [`mfa-shim/FDA-CONSIDERATIONS.md`](./mfa-shim/FDA-CONSIDERATIONS.md) before any clinical deployment.

## Contributing

### Can I contribute scenarios for a new device class?

Yes — see [`CONTRIBUTING.md`](./CONTRIBUTING.md). The most valuable contributions are:

- Additional scenarios in `stride-hc-templates/scenario-library/` for under-covered device classes (ventilators, anaesthesia, MRI consoles, dialysis machines)
- New worked CJR examples in `cjr-templates/examples/`
- New attack scenarios in `test-harness/attacker/scenarios/`
- New device-emulator targets in `test-harness/target-*/`

Each contribution should include the relevant cross-references (which STRIDE-HC category, which playbook pattern, etc.) so the corpus stays internally consistent.

### How do I report a security issue?

See [`SECURITY.md`](./SECURITY.md) — please **do not** open a public issue. Report privately per the procedure documented there. This applies especially to the MFA shim prototype and the test harness.
