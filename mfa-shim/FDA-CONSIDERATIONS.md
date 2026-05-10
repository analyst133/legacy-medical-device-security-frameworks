# FDA and Regulatory Considerations for the Pattern C MFA Shim

> **This is not regulatory advice.** This document describes the regulatory questions that any deployment of an inline MFA shim raises, and the considerations that must be addressed in consultation with regulatory affairs counsel and the relevant manufacturer.

## The central question

When an HDO (or a manufacturer) inserts an in-line hardware element between a medical device's service port and the technician's tooling, has the medical device been **modified** in a way that requires re-clearance, change notification, or other regulatory engagement?

The answer is jurisdiction- and case-specific. This document outlines the framework for analysis.

## United States — FDA

### Relevant regulations and guidance

- **21 CFR §820.30** — Design controls (for manufacturer modifications)
- **21 CFR §807** — Premarket notification (510(k))
- **FDA Guidance: Deciding When to Submit a 510(k) for a Change to an Existing Device** (October 2017)
- **FDA Guidance: Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions** (September 2023)
- **Section 524B FD&C Act** — Cybersecurity expectations for cyber devices
- **FDA Guidance: Postmarket Management of Cybersecurity in Medical Devices** (December 2016)

### Analysis framework

For an HDO operator deploying the shim, the FDA's primary jurisdictional concern is whether the deployment changes the device's **intended use** or **fundamental scientific technology**. If the answer is no, the deployment is in the operator's compliance domain (HIPAA, internal risk management) rather than triggering FDA premarket review.

Key questions:

1. **Does the shim modify the device's clinical function?** No — it gates access to the service port, which is not a clinical-function path.
2. **Does the shim change clinical data flow?** No — clinical data flows through different interfaces (HL7, DICOM, vendor protocols on dedicated network ports), not through the service port.
3. **Does the shim affect the device's labelled performance characteristics?** No — performance specifications (rate accuracy, alarm latency, etc.) are not impacted.
4. **Does the shim affect cybersecurity properties of the device?** Yes — favourably. Postmarket cybersecurity guidance (December 2016) explicitly recommends compensating controls for legacy devices.

The deployment most closely resembles the addition of a network compensating control (firewall, IPS, gateway), which is a routine HDO operational practice not requiring FDA engagement.

### Caveats and risk areas

- **Servicing failure during use**: if shim failure can prevent legitimate service activity that is itself safety-critical, the deployment plan must include break-glass and physical-removal procedures. The shim's documentation includes such procedures, but they must be operationally validated.
- **Classification edge case**: if the shim itself is alleged to be a medical device accessory under 21 CFR §890.1 or similar, classification could be required. The argument that it is a security accessory rather than a medical accessory is plausible but not precedential. Regulatory affairs review is recommended before scaled deployment.
- **Manufacturer service warranties**: many manufacturer service contracts contain language voiding warranty if third-party hardware is connected to service ports. This is a contractual rather than regulatory consideration but practically significant.
- **Manufacturer cybersecurity advisories**: if a manufacturer publishes a security advisory recommending specific compensating controls and the shim is among them, the deployment is on stronger ground than a self-initiated deployment.

### Production-deployment path

For production deployment beyond a research or quality-improvement pilot, recommended steps:

1. **Pre-submission (Q-submission) meeting** with FDA CDRH if the deployment plans extend across a fleet of any meaningful size, particularly across multiple facilities.
2. **Manufacturer engagement** for each affected device class. Best case: the manufacturer endorses the shim under their security advisory. Acceptable case: the manufacturer is informed and not opposed. Worst case: manufacturer asserts that the deployment voids service warranty — proceed only with explicit organisational acceptance of that risk.
3. **Risk management file update** (ISO 14971 cl.10) treating the shim as a postmarket risk control measure with corresponding residual risk evaluation.
4. **Quality system process** for shim deployment, monitoring, and decommissioning, integrated with existing clinical engineering work-order processes.

### Pilot deployment criteria

A pilot deployment limited to a small number of devices in a controlled clinical environment (e.g., 10–20 pumps in a single ICU) for a defined evaluation period is the lowest-risk regulatory posture and is what `cjr-templates/examples/cjr-leaked-service-pin.md` documents.

Pilot deployments should:

- Be authorised by the institutional research/quality improvement programme governance
- Have defined entry and exit criteria
- Include manufacturer notification (even if not formal manufacturer endorsement)
- Have a documented removal plan if any safety signal emerges
- Generate evidence (operational, clinical, security) suitable for informing scale-up decisions

## European Union — MDR

### Relevant regulations

- **EU MDR 2017/745** — particularly Articles 14 (distributor obligations), 16 (modifications), 23 (manufacturer of in-vitro diagnostic devices)
- **MDCG 2019-11** — Guidance on qualification and classification of software in MDR
- **Annex I** — General safety and performance requirements, particularly §17.2 (IT environment requirements)

### Analysis

The EU MDR's **Article 16** prohibits any person from making changes to a medical device that "may modify its compliance with the requirements of this regulation" without satisfying the obligations of a manufacturer. This is more stringent than the FDA position.

A reasonable reading: the shim does not modify the device itself; it sits in the technician-tooling-to-device connection. By analogy with network compensating controls (firewalls, gateways), it should not constitute a device modification. However, this analogy is not formally established in MDR jurisprudence.

For EU deployment:

- **Notified body engagement** is recommended before pilot deployment in EU jurisdictions.
- The shim's classification (as security infrastructure rather than as a medical device) should be confirmed in writing.
- The manufacturer's CE-mark documentation should be reviewed for any clauses that constrain inline accessory connection.

### MDCG 2019-16 — Cybersecurity Guidance

The EU's medical device cybersecurity guidance (MDCG 2019-16) explicitly endorses compensating controls for legacy device cybersecurity. The shim is consistent with this guidance in principle. The procedural pathway for deployment is the question that requires notified-body engagement.

## Other jurisdictions

The pattern of analysis above generalises. Key questions in any jurisdiction:

1. Does the regulation distinguish between modification of the device and operation of the device?
2. Does the regulation accommodate compensating controls for legacy devices?
3. Does the regulation require manufacturer involvement in inline accessory deployment?

For Health Canada, the TGA (Australia), the PMDA (Japan), and other regulators, similar consultations should occur before any production deployment.

## What this artifact provides

This repository provides:

1. The **design and reference implementation** of Pattern C, sufficient to support pilot evaluations.
2. **Documentation** sufficient to inform regulatory analysis.
3. An **Apache-2.0 patent grant** ensuring no party can monopolise the design.

This repository does **not** provide:

1. FDA pre-submission documents or 510(k) content.
2. Notified body assessments.
3. Production-grade hardware (the prototype is software-only).
4. Clearance, certification, or any form of regulatory approval.

Any party wishing to deploy the design in production should engage their own regulatory affairs function, the affected device manufacturer(s), and the relevant regulatory authorities before scaled deployment.

## Related resources

- **HSCC HIC-MaLTS (2023)** — explicitly addresses legacy device compensating controls and is generally aligned with the Pattern C approach.
- **AAMI TIR97** — postmarket security for legacy devices, including the explicit treatment of compensating controls and residual risk.
- **MITRE Threat Modeling Playbook for Medical Device Cybersecurity (2020)** — provides framework alignment.

## Disclaimer (re-stated)

The authors of this repository are not regulatory affairs professionals. This document is the authors' best-effort summary of relevant considerations, intended as a starting point for organisational regulatory analysis, not as a substitute for it. Decisions about deployment must be made by the deploying organisation in consultation with their own regulatory, clinical, and security functions.
