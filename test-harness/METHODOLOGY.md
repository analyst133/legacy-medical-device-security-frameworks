# Test Harness Methodology

This document explains how to design, run, and interpret experiments using the harness. It is intended for researchers, contributors, and any practitioner using the harness to generate evidence for their own compensating-control evaluations.

## Goal

Produce a defensible, reproducible matrix of `(scenario, control profile) → outcome` records that quantifies which compensating controls actually mitigate which threats.

## Experimental design

### Variables

- **Scenario**: a single attack action targeting the emulated device. Each scenario is mapped to a STRIDE-HC category and exercises one or more of the device's documented security constraints.
- **Control profile**: a defined combination of compensating controls toggled on or off via Docker Compose profiles. The defined profiles are: `baseline` (none), `ips`, `pam`, `segmentation`, `all`.
- **Outcome**: one of `SUCCESS`, `MITIGATED`, `BLOCKED`, `BLOCKED_AUTH`, `BLOCKED_HTTP`, `BLOCKED_NET`, `PARTIAL`, `ERROR`.

### Hypotheses

The harness is designed to test specific hypotheses about which control profiles mitigate which scenarios. The expected matrix:

| Scenario | baseline | ips | pam | segmentation | all |
|---|---|---|---|---|---|
| 01 ARP poisoning | REACHABLE | REACHABLE | REACHABLE | BLOCKED | BLOCKED |
| 02 Firmware injection | SUCCESS | BLOCKED_NET | BLOCKED_AUTH | BLOCKED | BLOCKED |
| 03 Cleartext HL7 sniff | SUCCESS | SUCCESS | SUCCESS | BLOCKED | BLOCKED |
| 04 Protocol flood DoS | SUCCESS | MITIGATED | SUCCESS | BLOCKED | BLOCKED |
| 05 Default-cred EoP | SUCCESS | BLOCKED_NET | BLOCKED_AUTH | BLOCKED | BLOCKED |

Empirical results that diverge from this matrix are interesting and warrant investigation — they may indicate a control gap, a scenario implementation issue, or an emulator behaviour mismatch with real-world devices.

## Running an experiment

### Single-cell run

```bash
docker compose --profile pam up -d
docker compose exec attacker python runner.py 05-eop-default-credential.py --control-profile pam
```

### Full matrix

The Makefile (`make matrix`) executes all 5 scenarios across all 5 control profiles, restarting the harness between profiles for clean state. Results are written to `results/run-<timestamp>.csv`.

```bash
make matrix
# Equivalent to:
# for profile in baseline ips pam segmentation all; do
#     docker compose down
#     if [ "$profile" != "baseline" ]; then
#         docker compose --profile $profile up -d
#     else
#         docker compose up -d
#     fi
#     sleep 10  # wait for healthchecks
#     docker compose exec -T attacker python runner.py --all --control-profile $profile
# done
# python aggregate-results.py results/run-*.csv > results/matrix.csv
```

### Repetition for variance

A single matrix run produces a snapshot. For results suitable for reporting, run the matrix at least three times and compute outcome consistency. Variability in the harness is expected to come primarily from timing-sensitive scenarios (DoS recovery window, HL7 capture window).

## Interpretation

### Outcome classification

- **SUCCESS** — the attack achieved its objective (data captured, parameter modified, target downed). Compensating control did not mitigate.
- **MITIGATED** — the attack reached the target but the target's availability or integrity was preserved. Compensating control reduced impact.
- **BLOCKED** — the attack was prevented from reaching the target. Compensating control fully mitigated.
- **BLOCKED_AUTH** — the attack reached the application but failed authentication. PAM Pattern A working as intended.
- **BLOCKED_HTTP** — the application returned an HTTP error other than 401. Indicates rule-based filtering (e.g., IPS).
- **BLOCKED_NET** — connection refused or timed out at network layer. Network segmentation or IPS at the network layer.
- **PARTIAL** — the attack partially succeeded. Investigate the detail field for context.
- **ERROR** — the scenario failed to execute (test failure, not control success). Re-run.

### Statistical considerations

For the binary classification of effective vs not-effective at the per-scenario level, a single matrix run is informative but not sufficient. Repeated runs with consistent outcomes increase confidence. For paper publication or formal evidence, three to five matrix runs with all-consistent outcomes is the suggested floor.

### Multi-scenario interactions

A control profile may mitigate scenario X by side effect even when it is not specifically designed for X. The matrix exposes such interactions — for example, network segmentation mitigates scenario 01 (ARP poisoning) and scenario 03 (HL7 sniff) and scenario 04 (DoS) all at once because all three depend on Layer 2/3 attacker positioning. This is a feature of the analysis: it demonstrates that defence-in-depth at the network layer is broadly effective.

## Limitations

The harness has known limitations that must be considered when interpreting results:

1. **Emulation fidelity.** The pump emulator reproduces specific constraints, not the full behaviour of any specific commercial device. A control that works against the emulator may face additional challenges against a real device with idiosyncratic behaviour.
2. **Scenario simplification.** Each scenario is implemented in 50–150 lines of Python. Real attacks are typically more sophisticated and may chain multiple techniques. The harness scenarios test the basic control posture, not edge cases.
3. **Single-device focus.** The harness emulates one infusion pump. Multi-device interactions (e.g., scenario where attacker pivots from one pump to a peer pump) are not modelled.
4. **No physical-attacker scenarios.** The harness is a software environment. Pattern C MFA shim evaluation requires the hardware reference design (`mfa-shim/`).
5. **Production controls are richer than harness controls.** A real Snort/Suricata IPS, real CyberArk PSM, or real Cisco TrustSec deployment will have more complex behaviours than the harness's stub controls. The harness demonstrates the methodology and the control taxonomy; per-deployment control efficacy must be validated in deployment context.
6. **No false-positive measurement.** The harness does not generate the volume of legitimate traffic needed to measure false-positive rates of the controls. Production deployments should evaluate FP rates against full clinical workloads.

## Extending the harness

### Adding a new scenario

1. Create a new file under `attacker/scenarios/`.
2. Implement `run() -> dict` returning the standard result schema.
3. Include `STRIDE_HC` and `SCENARIO_NAME` module-level constants.
4. Test the scenario standalone.
5. Update the expected-outcome matrix in this document.
6. Submit a PR including matrix run results.

### Adding a new device emulator

1. Create a new top-level subdirectory (e.g., `target-pacs/`).
2. Provide Dockerfile and emulator script following the structure of `target-device/`.
3. Document the constraints reproduced.
4. Update `docker-compose.yml` (optionally as a separate compose file if the architecture differs substantially).
5. Add scenarios specific to the new emulator's attack surfaces.

### Adding a new control profile

1. Create a new directory under `controls/`.
2. Provide Dockerfile and implementation.
3. Add a service to `docker-compose.yml` with `profiles: ["new-control"]`.
4. Document the expected outcome modifications in the matrix.

## Reporting

Results from harness runs can be reported in:

- **CJR effectiveness validation** (paper §3.5) — link harness output to the CJR record
- **STRIDE-HC threat models** as evidence of control coverage
- **MDRS CCD scoring** as evidence supporting reduced CCD values for devices with validated controls
- **Manufacturer security advisories** providing customers with evidence that recommended compensating controls are effective
- **Penetration test reports** as automated supplementary evidence
