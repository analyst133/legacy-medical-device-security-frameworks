# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Interactive **MDRS calculator** improvements: a guided assessment mode (default for new users) alongside the existing direct-slider mode; explicit owners / timeline / review-cadence panel keyed to the resulting tier; scores-assigned table in the result card.
- Interactive **STRIDE-HC threat model builder** at [`/stride-hc-templates/`](./stride-hc-templates/) — pick an archetype, tick scenarios from the relevant library, download a filled `.md` and `.yaml` matching the existing template / schema.
- Interactive **CJR builder** at [`/cjr-templates/`](./cjr-templates/) — guided 10-section form with a load-example button for the no-MFA infusion-pump worked case.
- **Test harness Results Explorer** at [`/test-harness/`](./test-harness/) — visualises `sample-results.csv` as a (scenario × control profile) heatmap; supports user-uploaded CSV.
- **MFA shim demo page** at [`/mfa-shim/`](./mfa-shim/) with a working in-browser RFC 6238 TOTP gate that mirrors `prototype/totp_gate.py` behaviour for window tolerance, replay protection, and per-user lockout.
- Top-level [`WALKTHROUGH.md`](./WALKTHROUGH.md) — cross-artifact tour using a worked infusion-pump example traced through MDRS → STRIDE-HC → CJR → test harness → MFA shim.
- [`stride-hc-templates/WALKTHROUGH.md`](./stride-hc-templates/WALKTHROUGH.md) — 30-minute first-time-user tutorial for building a STRIDE-HC threat model from scratch.
- [`cjr-templates/WALKTHROUGH.md`](./cjr-templates/WALKTHROUGH.md) — 30-minute first-time-author tutorial walking through all 10 sections of a CJR.
- [`SETUP.md`](./SETUP.md) — step-by-step install walkthrough with Linux / macOS / Windows commands side-by-side at every step.
- Top-level [`requirements.txt`](./requirements.txt) — aggregator that pulls in `mfa-shim/prototype/requirements.txt`.
- "Where the output goes" section in `stride-hc-templates/README.md` covering FDA, ISO 14971, AAMI TIR57, CJR, and MDRS handoffs.
- Live-page links from every artifact README; Quick Start table in the top-level README.

### Changed

- **Visual design** of all five live pages refreshed to a publication-grade aesthetic: Michigan Blue (`#00274C`) + Maize (`#FFCB05`) palette on white, Fraunces serif headings + Geist sans body + JetBrains Mono numerics (loaded from Google Fonts), brand-mark logo (Michigan-Blue square with Maize diamond) on each page.
- Citing section in `README.md` updated to include the Zenodo concept DOI and v1.0.0 versioned DOI bibtex.
- Long live-page URLs converted to descriptive hyperlinks (`[Open the live X →](...)`) across all READMEs.

### Fixed

- **MFA shim test fixture leak on Windows**: `test_session_recorder.py` left a session file open after `test_cannot_open_two_sessions`, causing pytest tempdir cleanup to fail with `WinError 32`. The fixture now force-closes any open session in `finally`.
- **Stale "(forthcoming)" reference** to `SECURITY.md` in `CONTRIBUTING.md` removed — the file has shipped since v1.0.0.
- **XSS surface in test-harness results explorer**: CSV-sourced strings (`control_profile`, `stride_hc`, `scenario`, `outcome`, `timestamp`) are now routed through `escapeHtml()` before `innerHTML` interpolation in the matrix header, scenario rows, and detail panel. Verified against malicious payloads.

## [1.0.0] — 2026-05-10

### Initial release

Five companion artifacts for the paper *"A Practical Cybersecurity Framework for Legacy Medical Devices"*:

- **MDRS Calculator** — reference implementation of the Medical Device Risk Score (paper §5) with irreversibility-driven tier floor and CCD promoter. Pure HTML/JS, zero build dependencies. 15/15 unit tests passing; paper Table 7 presets reproduce to the third decimal place.
- **STRIDE-HC Templates** — threat-modelling templates for legacy medical devices (paper §4), with Archetype 1 and Archetype 2 scenario libraries and two worked examples (infusion pump, PACS workstation).
- **CJR Templates** — Control Justification Record templates aligned to HIPAA Security Rule, ISO 14971 cl.7–8, AAMI TIR57, AAMI TIR97, and FDA 2023 §524B postmarket cybersecurity guidance. Three worked examples.
- **Test Harness** — Dockerised multi-container test environment for empirical evaluation of compensating-control effectiveness. Five STRIDE-mapped attack scenarios (ARP poisoning, firmware injection, cleartext HL7 sniff, protocol-flood DoS, default-credential EoP) against three control profiles (IPS, PAM upstream, network segmentation).
- **MFA Shim (Pattern C) Reference Design** — software reference implementation of the inline service-port multi-factor authentication shim (paper §3.4). Python prototype with TOTP gate, session recorder, and tamper detector. 37/37 unit tests passing.

### Released under

- Apache License 2.0
- Archived on Zenodo with concept DOI [10.5281/zenodo.20113684](https://doi.org/10.5281/zenodo.20113684)
- v1.0.0 versioned DOI [10.5281/zenodo.20113685](https://doi.org/10.5281/zenodo.20113685)
- Tagged v1.0.0 at commit [`a79d905`](https://github.com/analyst133/legacy-medical-device-security-frameworks/commit/a79d905)

### Test status

- **15/15** MDRS calculator unit tests passing (Node.js)
- **37/37** MFA shim prototype unit tests passing (pytest)
- **52/52 total**
