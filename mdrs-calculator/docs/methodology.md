# MDRS Methodology

This document expands on paper Section 5 with implementation-level detail relevant to the reference calculator. It is intended for practitioners adapting the calculator to their environment, and for researchers conducting sensitivity analysis or empirical re-calibration.

## Why a device-level score?

Existing scoring approaches address adjacent but different needs:

- **CVSS** scores a vulnerability in isolation. It does not weight clinical consequence, compensating-control posture, or device criticality.
- **EPSS** estimates exploitation probability. It is useful as an input to ES but is not a decision instrument.
- **MITRE Rubric for Applying CVSS to Medical Devices (2020)** adapts CVSS environmental modifiers for medical context. It scores vulnerabilities, not devices.
- **MDS²** discloses manufacturer security capabilities. It informs the calculator's CCD score but is not itself a triage instrument.
- **Commercial healthcare security platforms** (Claroty, Medigate, Armis, Asimily, Cynerio, Ordr) produce proprietary device-level scores. The methodologies are not publicly published; reproducibility is limited.

MDRS is a device-level, transparent, reproducible composite designed for triage of legacy devices in clinical environments. Its claim to novelty rests on **two** specific contributions: the **irreversibility-driven tier floor** and the **CCD-driven tier promoter**.

## The two stages

### Stage 1: Weighted composite

```
MDRS_comp = (CIS × w_CIS) + (ES × w_ES) + (DCI × w_DCI) + (NEF × w_NEF) + (CCD × w_CCD)
```

with default weights `(0.35, 0.25, 0.20, 0.15, 0.05)` summing to 1.0. Each dimension is scored on a 1–10 scale per paper Table 5.

### Stage 2: Floor and promoter

After computing the composite and mapping to a base tier, two adjustments are applied in order:

1. **Irreversibility-driven tier floor.** A device with high clinical impact cannot be triaged below a defined floor regardless of its exploitability profile. Specifically:
   - If `CIS ≥ 9` and base tier is below HIGH → tier is set to HIGH.
   - If `7 ≤ CIS < 9` and base tier is below MEDIUM → tier is set to MEDIUM.
   - Otherwise: no change.

2. **CCD-driven tier promoter.** If `CCD ≥ 8` (no or minimal compensating controls), the tier is promoted by one level relative to the post-floor tier, capped at CRITICAL.

Both adjustments may activate. The most extreme combined effect is a device with `CIS ≥ 9` and `CCD ≥ 8`: the floor lifts to HIGH and the promoter lifts to CRITICAL, regardless of any other dimension. This is by design — a life-sustaining device with no compensating controls is the worst-case operational profile.

## Tier mapping

| Tier | Composite range | Action timeline |
|---|---|---|
| CRITICAL | ≥ 8.0 (or promoted from HIGH) | Immediate / 24 hours |
| HIGH | 6.0 ≤ score < 8.0 (or floored from CIS ≥ 9) | 30 days |
| MEDIUM | 3.5 ≤ score < 6.0 (or floored from CIS = 7–8) | 90 days |
| LOW | < 3.5 | 12 months |

Boundaries are defined inclusively at the upper end and exclusively at the lower end, eliminating gaps between adjacent tiers.

## Why these weights?

The weights reflect clinical prioritisation:

- **CIS (35%)** carries the largest weight because clinical consequence is the most material factor in clinical environments, and is also the dimension with explicit irreversibility implications.
- **ES (25%)** captures exploitability, the second most material factor.
- **DCI (20%)** captures operational dependency.
- **NEF (15%)** captures attack surface exposure (network and physical).
- **CCD (5%)** carries the smallest weight as a composite contribution because its operational role is primarily as the tier promoter: practitioners actionably reduce risk by improving compensating controls, which the composite alone could obscure.

The weights are **expert judgement informed by the literature and regulatory guidance**, not empirically derived through structured elicitation. The calculator implements weights as configuration parameters precisely so that organisations and researchers can perform sensitivity analysis and re-calibration.

## Why the floor?

Conventional risk scoring multiplies probability by impact. For a life-sustaining device in active therapy, the harm is irreversible by the time it is detected. Probability-weighted scoring, in this regime, fails to differentiate "low probability of irreversible harm" from "low probability of recoverable harm" — but the operational treatment must differ. The floor is the simplest explicit mechanism to encode this.

The floor is **not** a substitute for the composite. It is a minimum below which a device with high clinical impact cannot be triaged regardless of other factors. Devices may legitimately score above the floor on the basis of the composite alone; the floor only changes outcomes when the composite would have produced an outcome below it.

## Why the promoter?

The CCD score is the most directly practitioner-actionable dimension: improving compensating controls is something a security programme can do. With a 5% composite weight, however, a one-point CCD reduction changes the composite by only 0.05 — typically not enough to change tiers. Without the promoter, a device with no compensating controls and moderate other dimensions could remain in MEDIUM and never escalate to leadership attention.

The promoter inverts the asymmetry. If `CCD ≥ 8`, the tier is escalated by one level. This causes practitioner attention to track the most-tractable risk factor without distorting the composite for devices with effective controls.

## Edge cases

- **All-CRITICAL inputs.** A device with all dimensions at 10 produces composite 10.0 → CRITICAL. The CCD promoter would apply but cannot exceed CRITICAL.
- **Floor with composite already in floor tier.** A device with `CIS = 9, ES = 7, DCI = 7, NEF = 7, CCD = 1` produces composite 7.05 → HIGH. The floor is HIGH; floor is satisfied without modification. The floor does not reduce a higher tier to its floor; it raises a lower tier to its floor.
- **Composite at boundary.** Composite values exactly 8.0, 6.0, or 3.5 fall into the higher tier (inclusive lower bound).
- **Floating-point precision.** Composites are computed in double-precision floating point, then rounded to 3 decimal places before tier mapping. This avoids cases where `6.0 × 5 weights` evaluates as `5.999...` and incorrectly maps to MEDIUM.

## Sensitivity analysis recipes

Practitioners considering re-calibration should consider these analyses:

1. **CIS-weight sensitivity.** Vary `w_CIS` from 0.20 to 0.50 in steps of 0.05; observe how many devices in the inventory cross tier boundaries. If the inventory is well calibrated, most devices should remain in the same tier across this range.
2. **CCD-weight sensitivity.** Vary `w_CCD` from 0.05 to 0.15. The promoter mechanism makes most devices insensitive to this parameter; if many devices change tiers, the inventory may have an unusual distribution worth investigating.
3. **Floor-strictness analysis.** With the floor disabled, how many devices currently scored at or above HIGH would drop below? This quantifies the effect of the irreversibility adjustment for the specific inventory.
4. **Promoter-strictness analysis.** Same analysis for the promoter.

The calculator's JSON export captures all input values and derived results, suitable as input to a sensitivity-analysis script.

## References

See the companion paper for the full reference list. Standards directly relevant to MDRS are:

- ISO 14971:2019 — Medical device risk management
- AAMI TIR57:2016 — Security risk management
- AAMI TIR97 — Postmarket security for legacy devices
- MITRE Rubric for Applying CVSS to Medical Devices (2020)
- IEC 62443-3-2 — Security risk assessment for system design (informs DCI)
