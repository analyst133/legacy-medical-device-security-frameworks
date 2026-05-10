# Test Harness Roadmap

This document tracks planned and possible extensions to the harness. Status reflects current state of this repository.

## Near-term (next quarter)

- [ ] **Real IPS in the data path.** Replace the IPS sentinel with a transparent eBPF or veth-based redirect that actually intercepts traffic. Suricata or Snort would be the natural choice.
- [ ] **Real network segmentation profile.** Provide an alternate `docker-compose-segmented.yml` placing the attacker on a separate Docker network with no route to the protected target. Eliminates the operator-disconnect step.
- [ ] **Matrix-aware result aggregation.** A `aggregate-results.py` script consuming multiple per-profile run CSVs and emitting a single matrix CSV plus a Markdown summary.
- [ ] **Sample-size guidance.** Statistical considerations document with worked examples for sizing repeated matrix runs.

## Medium-term (within 12 months)

- [ ] **Archetype 1 device emulator.** A second target representing a Windows-style legacy workstation (PACS, modality console). Different attack surface; different controls (application allowlisting, EDR).
- [ ] **Behavioural monitoring control profile.** A control that does not block but produces detection-quality logs, supporting Framework V evaluation.
- [ ] **Detailed scenario expansion.** Add at least two scenarios per STRIDE-HC category, including chained scenarios.
- [ ] **TLS/IPSec wrapping control.** A control profile that demonstrates encrypting cleartext traffic via a transparent proxy or IPSec tunnel.
- [ ] **Realistic baseline traffic volumes.** Workstation emulator currently generates ~5 messages/minute; production environments would have orders-of-magnitude more. Add a load-generation mode.

## Longer-term and exploratory

- [ ] **Hardware-in-the-loop integration.** Connect a real Pattern C MFA shim hardware prototype to a real RS-232 endpoint of an emulated or training-grade device, evaluating the physical-attacker scenarios that the software harness cannot test.
- [ ] **Multi-device topology.** A larger compose with 5-10 emulated devices, demonstrating lateral-movement scenarios and zone-based segmentation effectiveness.
- [ ] **Vendor-protocol emulators.** Add emulators for proprietary protocols common to specific device classes (e.g., DICOM modality protocols, specific vendor CAN bus signalling).
- [ ] **MITRE ATT&CK for ICS scenario mapping.** Map all scenarios to MITRE ATT&CK for ICS techniques in addition to STRIDE-HC categories.
- [ ] **Continuous integration.** GitHub Actions workflow that runs the harness on each PR and verifies the expected matrix is reproduced.

## Out of scope

- Tools that target specific commercial medical devices.
- Distribution of leaked credentials or exploit payloads for any specific commercial product.
- Anything that would convert the harness from a research tool into an operational attack platform.

## How to suggest additions

Open an issue with the `harness/extension` label, describing:

- The capability or scenario that would be added
- The threat model relevance (STRIDE-HC mapping)
- Implementation approach
- Expected difficulty and timeframe
