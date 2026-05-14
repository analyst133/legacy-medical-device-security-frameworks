# MDRS Calculator

Reference implementation of the **Medical Device Risk Score** with the irreversibility-driven tier floor and Compensating Control Deficit (CCD) tier promoter.

This is the headline artifact of the companion repository for the paper *"A Practical Cybersecurity Framework for Legacy Medical Devices"*.

## Run it

**[Open the live MDRS calculator →](https://analyst133.github.io/legacy-medical-device-security-frameworks/mdrs-calculator/)** — no install required.

Or locally — the calculator is a pure HTML/CSS/JavaScript application with **zero build dependencies**. Open `index.html` in any modern browser:

```bash
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

## What it does

The calculator implements paper Section 5 in full and **guides users through an assessment** rather than asking for raw numbers cold. Two modes:

### Guided assessment mode (default for new users)

Five plain-English multiple-choice questions, one per dimension. Each option is annotated with concrete examples ("life-sustaining devices: ventilators, infusion pumps in active therapy, pacemaker programmers, dialysis"). The calculator assigns the appropriate score (the midpoint of the relevant band) automatically. No numerical familiarity required.

### Direct entry mode (for power users)

Five sliders, each with an expandable **Show scoring guide** that surfaces the full Table 5 rubric inline. Faster for analysts who already know how to map device facts to scores.

### Common to both modes

1. **Five-dimension scoring** (CIS, ES, DCI, NEF, CCD), each on a 1–10 scale.
2. **Weighted composite** per equation (1):

   ```
   MDRS_comp = (CIS × 0.35) + (ES × 0.25) + (DCI × 0.20) + (NEF × 0.15) + (CCD × 0.05)
   ```

3. **Irreversibility-driven tier floor** (the central novel contribution):
   - CIS ≥ 9 → minimum tier HIGH
   - CIS = 7 or 8 → minimum tier MEDIUM
4. **CCD-driven tier promoter**: CCD ≥ 8 promotes the resulting tier by one level (capped at CRITICAL).
5. **Tier mapping** with inclusive lower bounds: ≥ 8.0 CRITICAL, ≥ 6.0 HIGH, ≥ 3.5 MEDIUM, < 3.5 LOW.
6. **"Why this tier?" explainer** describes which adjustments fired and why.
7. **Scores-assigned table** showing which numbers were used in the composite.
8. **"What to do with this score" panel** with concrete next steps tied to the resulting tier (who to convene, what timeline, what documentation, what review cadence).
9. **Configurable weights** for sensitivity analysis.
10. **Three preset profiles** matching paper Table 7.
11. **JSON export** of the full result object.

## Verification

Run the test suite:

```bash
node tests/run-tests.js
```

The current suite includes 15 test cases covering: all three paper presets, irreversibility-floor activation conditions, CCD-promoter activation conditions, floor + promoter combined, ceiling behaviour, and tier boundaries (8.0, 6.0, 3.5).

```
15 test(s); 15 passed; 0 failed.
```

## File layout

```
mdrs-calculator/
├── README.md           # This file
├── index.html          # Calculator UI
├── styles.css          # Visual styling
├── calculator.js       # Scoring logic + DOM wiring (also exports as Node module for tests)
├── tests/
│   ├── run-tests.js    # Node-based test runner
│   └── test-cases.json # Test cases
└── docs/
    └── methodology.md  # Detailed methodology notes
```

## Browser compatibility

Tested on current versions of Firefox, Chrome, Safari, and Edge. No transpilation; uses ES2015+ features (`const`, arrow functions, template literals) which have been universally supported since 2017. No external dependencies; no Internet connection required after the page loads.

## Use in an organisation

The calculator can be:

- **Bookmarked** as a static page on the organisation's intranet.
- **Embedded** in an asset-management or GRC system (it's a single self-contained set of files).
- **Forked** to add organisation-specific scoring guidance, presets, or weight defaults.
- **Used in batch** by importing `calculator.js` as a Node module — see `tests/run-tests.js` for an example of headless usage.

Per the paper's §9.2 limitations: weights are based on expert judgement rather than empirical elicitation. Organisations conducting sensitivity analysis or empirical re-calibration should adjust the weights and the boundary thresholds accordingly, and document the choices in their MDRS configuration record.

## Citing

Please cite the companion paper. See top-level [`CITATION.cff`](../CITATION.cff).

## Licence

Apache License 2.0. See top-level [`LICENSE`](../LICENSE).
