<!--
Thanks for the contribution. Fill in the sections below so reviewers can land
your PR quickly. Delete sections that don't apply.
-->

## Summary

<!-- One or two sentences describing what this PR does and why. -->

## Which artifact(s) does this PR affect?

- [ ] **MDRS calculator** (logic, UI, tests, or `methodology.md`)
- [ ] **STRIDE-HC templates** / builder / scenario libraries
- [ ] **CJR templates** / builder / worked examples
- [ ] **Test harness** (Docker, scenarios, controls, METHODOLOGY)
- [ ] **MFA shim prototype** (Python, hardware notes, FDA considerations)
- [ ] **Top-level docs** (`README`, `SETUP`, `WALKTHROUGH`, `FAQ`, `CHANGELOG`)
- [ ] **Repo infrastructure** (`.github`, `Makefile`, `requirements.txt`, configs)

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behaviour for users)
- [ ] Documentation only
- [ ] Repo infrastructure / tooling
- [ ] Other (describe in summary)

## Testing

- [ ] All 52 unit tests pass (`make test`)
- [ ] If MDRS math changed: paper Table 7 presets still reproduce to 3-decimal precision
- [ ] If MFA shim code changed: pytest passes including the Windows tempdir teardown case
- [ ] If live pages changed: opened the affected page in a browser at least once
- [ ] If test harness changed: ran `make matrix` (or the relevant subset) against the new scenario or control
- [ ] New tests added for new behaviour, or N/A with reason

## Documentation

- [ ] `CHANGELOG.md` entry added under `[Unreleased]` in the right section (Added / Changed / Fixed / Security)
- [ ] Relevant walkthrough updated (top-level `WALKTHROUGH.md`, or artifact-specific `WALKTHROUGH.md`)
- [ ] `FAQ.md` entry added if this affects a common reader question
- [ ] Standards / regulatory references updated if the change touches HIPAA / ISO 14971 / AAMI / FDA citations
- [ ] Live page meta tags (Open Graph / Twitter) still accurate if descriptions changed

## Standards / regulatory alignment

<!-- For changes affecting templates or frameworks: which standards or regulatory provisions does
     this preserve, extend, or update? e.g. "Maintains alignment with ISO 14971 cl.7.4 (risk
     control implementation) and adds explicit reference to NIST CSF 2.0 GV.RM-04." -->

## Related issues

<!-- Closes #123, Fixes #456, Relates to #789 -->

## Reviewer checklist

- [ ] Code is readable and consistent with existing style (EditorConfig clean)
- [ ] No new `TODO` / `FIXME` / `XXX` markers introduced
- [ ] No secrets, credentials, or real PHI in the diff (sample data only)
- [ ] No unrelated changes — diff scope matches the summary
- [ ] If author metadata touched: matches `CITATION.cff` ordering

---

> ⚠ **Security-relevant?** If this PR addresses a security vulnerability, please do not publish exploitation details in the PR description until disclosure is coordinated per [`SECURITY.md`](../SECURITY.md).
