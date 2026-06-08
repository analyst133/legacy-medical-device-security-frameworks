---
name: Bug report
about: Report a bug in one of the artifacts (calculator, builders, test harness, MFA shim, docs)
title: '[Bug] '
labels: ['bug', 'triage']
assignees: ''
---

## Which artifact is affected?

<!-- Tick the one(s) that apply. -->

- [ ] **MDRS calculator** (live page or local tests)
- [ ] **STRIDE-HC builder** / templates
- [ ] **CJR builder** / templates
- [ ] **Test harness** (Docker, attack scenarios, control profiles)
- [ ] **MFA shim prototype** (Python — `totp_gate.py`, `session_recorder.py`, `tamper_detector.py`)
- [ ] **Documentation** (`README`, `SETUP`, `WALKTHROUGH`, `FAQ`, or any artifact `WALKTHROUGH.md`)
- [ ] **Other** (describe below)

## Description

<!-- A clear and concise description of the bug. -->

## Steps to reproduce

1.
2.
3.

## Expected behaviour

<!-- What you expected to happen. -->

## Actual behaviour

<!-- What actually happened. Paste error output, console messages, or attach screenshots. -->

## Environment

- **Operating system:** <!-- e.g. Ubuntu 22.04, macOS 14.4, Windows 11 -->
- **Browser** (for live pages): <!-- e.g. Chrome 124, Firefox 125, Safari 17 -->
- **Python version** (for MFA shim): <!-- e.g. 3.10.4 -->
- **Node.js version** (for MDRS calculator tests): <!-- e.g. 22.19.0 -->
- **Docker version** (for test harness): <!-- e.g. 24.0.6 -->

## Additional context

<!-- Workarounds tried, related issues, links to docs you were following, etc. -->

---

> ⚠ **Security-relevant?** If this bug has security implications (could enable unauthorised access, PHI exposure, privilege escalation, etc.), please **stop** and follow the private reporting procedure in [`SECURITY.md`](../../SECURITY.md) instead of filing a public issue.
