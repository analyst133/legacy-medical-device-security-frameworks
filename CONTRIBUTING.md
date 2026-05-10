# Contributing

Thank you for your interest in contributing to the Legacy Medical Device Security Frameworks repository. This document explains how to contribute effectively across the five artifacts.

## Scope of contribution

Contributions are welcome in any of the following areas. Each artifact has slightly different needs.

### MDRS calculator (`mdrs-calculator/`)
- Bug fixes in the scoring logic, tier-floor rules, or CCD promoter
- Additional preset device profiles (with citations)
- Improvements to accessibility or mobile UX
- Internationalisation (string externalisation; locales beyond en-GB)
- Test cases that increase coverage of edge conditions

### STRIDE-HC templates (`stride-hc-templates/`)
- New worked examples for additional device classes
- New entries in the scenario library, particularly for under-represented device types
- Enhancements to the YAML/JSON schema that improve tooling integration
- Mappings from STRIDE-HC categories to other taxonomies (MITRE ATT&CK for ICS, OWASP IoT)

### CJR templates (`cjr-templates/`)
- New CJR examples for additional constraint–control pairs
- Refinements to schema fields based on practitioner feedback
- Mapping spreadsheets between CJR fields and HIPAA / ISO 14971 / FDA 524B documentation requirements

### Test harness (`test-harness/`)
- Additional attack scenarios mapped to STRIDE-HC categories
- Additional device emulators (Archetype 1: general-purpose-OS legacy)
- Additional control-overlay profiles for compose-based experimentation
- Improvements to result reporting (CSV schema, visualisation)

### MFA shim (`mfa-shim/`)
- Bug fixes and test coverage improvements
- Hardware port notes (Raspberry Pi, ESP32, custom hardware)
- Threat-model documentation for the shim itself
- Performance benchmarking under realistic clinical workloads

## Out-of-scope contributions

The following are intentionally out of scope and will be politely declined:

- Production deployment guides for clinical environments — that is the responsibility of the deploying organisation
- Vendor-specific reverse-engineering of any commercial medical device
- Anything that could be construed as exploit development against a specific identifiable product
- Additions that would convert the MFA shim prototype into a regulated medical device without appropriate FDA / EU MDR engagement

## Workflow

1. **Open an issue first.** For substantive contributions, please open an issue describing the proposed change before writing code or content. This avoids duplication and catches scope mismatches early.
2. **Fork the repository** and create a feature branch (`feat/your-change` or `fix/your-bug`).
3. **Make focused changes.** A pull request that touches only one artifact is much easier to review than one spanning multiple artifacts.
4. **Add or update tests** where applicable (calculator, MFA shim).
5. **Add or update documentation** in the relevant `README.md`.
6. **Open a pull request** with a clear description, referencing any related issues.

## Commit message format

```
artifact: short description

Longer description if needed, wrapped at 72 characters.
References issue #N if applicable.
```

Example: `mdrs-calculator: add edge-case test for CCD=8 with CIS=10`.

## Code style

- **Python**: PEP 8, type hints where they aid clarity. Black formatter recommended.
- **JavaScript**: Plain ES modules, no transpilation. Two-space indent.
- **Markdown**: One sentence per line in source for diff clarity. No trailing whitespace.
- **YAML**: Two-space indent. Quoted strings only where required for ambiguity.

## Documentation conventions

- All written content uses **UK English** (consistent with the companion paper).
- All references to standards use the formal title at first use (e.g., "ISO 14971:2019" not "14971").
- Avoid acronyms that are not defined in the paper or in the artifact-specific README. Common acronyms (e.g., FDA, HIPAA, NIST) may be used without expansion.

## Reporting security issues

If you believe you have found a security issue in any artifact (particularly the MFA shim prototype or test harness), please **do not** open a public issue. Instead, report privately by following the procedure documented in [`SECURITY.md`](./SECURITY.md).

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Recognition

All contributors are listed in the repository's GitHub contributors page. Substantive contributions to specific artifacts are additionally acknowledged in the artifact-level `README.md`.

## Licence

By contributing, you agree that your contributions will be licensed under the Apache License, Version 2.0, the same as the rest of this repository.
