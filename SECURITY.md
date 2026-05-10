# Security policy

## Reporting a vulnerability

If you believe you have found a security issue in any artifact in this repository — particularly the MFA shim prototype or test harness — please **do not open a public issue**.

Instead, report privately by emailing the maintainers. Include:

- A description of the issue and its potential impact
- Steps to reproduce
- The specific artifact and version affected
- Any proof-of-concept code (if available)

The maintainers will acknowledge your report within seven days, work with you to understand and validate the issue, and coordinate a public disclosure timeline once a fix or mitigation is available.

## Scope

This security policy applies to:

- The MDRS calculator implementation
- The MFA shim prototype (`mfa-shim/prototype/`)
- The test harness orchestration (`test-harness/`)
- The schemas and templates if they could be exploited via tooling

This security policy does **not** apply to:

- Vulnerabilities in third-party dependencies (please report those upstream)
- Vulnerabilities in any specific commercial medical device (please report those to the manufacturer via Coordinated Vulnerability Disclosure)
- Theoretical issues without practical impact

## Status

This is research output, not a regulated product. Vulnerability reports are addressed on a best-effort basis. There is no service-level agreement.
