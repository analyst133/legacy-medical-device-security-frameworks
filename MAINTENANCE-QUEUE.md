# 30-Day Maintenance Queue

A pre-planned list of 30 small, genuine improvements to land one per day. Each item is real maintenance — not padding — and each takes 5–15 minutes.

**How to use this file:**

1. Each day, pick the next un-checked item below.
2. Make the change (do it yourself, or open a Claude Code session and say "do day N from MAINTENANCE-QUEUE.md").
3. Commit with the suggested message (or any clearer variant).
4. Tick the box `[x]` so you don't repeat an item.
5. Push.

When the queue runs out (or you've fallen behind), add new items at the bottom — there's no shortage of genuine maintenance work for a research artifact suite.

---

## Week 1 — Foundations

### Day 1 — Add `robots.txt` for Pages crawlability
- [x] **File:** `robots.txt` at repo root
- **Why:** Pages serves the file; search engines (Google Scholar in particular) find the live calculator and walkthroughs.
- **Done:** Landed without the Sitemap reference; that line will be added on the day `sitemap.xml` is created.
- **Commit:** `Add robots.txt for GitHub Pages crawlability`

### Day 2 — Add Dependabot config
- [x] **File:** `.github/dependabot.yml`
- **Why:** GitHub auto-opens PRs when Python deps in `mfa-shim/prototype/requirements.txt` have updates.
- **Done:** Watches `pip` ecosystem weekly + `github-actions` monthly (will auto-activate when first workflow lands).
- **Commit:** `Add Dependabot config for weekly Python dependency updates`

### Day 3 — Add bug-report issue template
- [x] **File:** `.github/ISSUE_TEMPLATE/bug_report.md`
- **Why:** Structured bug reports — which artifact, expected vs actual, OS, browser/Python version.
- **Done:** Template asks reporter to tick which of the five artifacts is affected, capture environment versions, and pre-flags the security-private-reporting path for security-relevant bugs.
- **Commit:** `Add bug report issue template`

### Day 4 — Add feature-request issue template
- [ ] **File:** `.github/ISSUE_TEMPLATE/feature_request.md`
- **Why:** Pair with bug template.
- **Commit:** `Add feature request issue template`

### Day 5 — Add pull request template
- [ ] **File:** `.github/PULL_REQUEST_TEMPLATE.md`
- **Why:** Checklist (tests, walkthroughs updated, CHANGELOG entry, etc.).
- **Commit:** `Add pull request template`

### Day 6 — Add `.python-version` file
- [ ] **File:** `.python-version` at repo root, content: `3.10`
- **Why:** pyenv users automatically get the right Python.
- **Commit:** `Pin Python version with .python-version file`

### Day 7 — Add `.nvmrc` for Node
- [ ] **File:** `.nvmrc` at repo root, content: `18`
- **Why:** nvm users get a consistent Node for MDRS calculator tests.
- **Commit:** `Pin Node version with .nvmrc file`

## Week 2 — Accessibility & UX polish

### Day 8 — Add print stylesheet to MDRS calculator
- [ ] **File:** `mdrs-calculator/styles.css` (append `@media print` block)
- **Why:** Clinical engineers print MDRS results for paper risk files. Currently the dark nav + colored cards waste ink.
- **Effort:** ~10 min
- **Commit:** `Add print stylesheet to MDRS calculator`

### Day 9 — Add ARIA labels to brand-mark logos
- [ ] **Files:** all 5 `index.html` live pages
- **Why:** Screen readers currently announce the brand-mark span as nothing. Add `role="img" aria-label="Site logo"`.
- **Commit:** `Add ARIA labels to brand-mark logos for screen readers`

### Day 10 — Add "skip to main content" link
- [ ] **Files:** all 5 `index.html` live pages
- **Why:** WCAG 2.1 SC 2.4.1. Keyboard users can skip past the nav repeatedly. Small CSS + one HTML element per page.
- **Commit:** `Add "skip to main content" link to live pages (WCAG 2.4.1)`

### Day 11 — Add focus-visible styling
- [ ] **Files:** all 5 `index.html` live pages + `mdrs-calculator/styles.css`
- **Why:** Default browser focus rings are inconsistent. Add `:focus-visible` with a Maize outline matching the brand.
- **Commit:** `Add :focus-visible outline styling for keyboard navigation`

### Day 12 — Add hover/focus polish to chip lists in builders
- [ ] **Files:** `stride-hc-templates/index.html`, `cjr-templates/index.html`
- **Why:** Chip selection currently lacks tactile feedback on keyboard focus.
- **Commit:** `Refine chip-list hover and focus states in builders`

### Day 13 — Improve mobile layout of STRIDE-HC builder
- [ ] **File:** `stride-hc-templates/index.html`
- **Why:** Profile grid and chip lists currently overflow on phones < 380px. Tighten the breakpoint.
- **Commit:** `Improve STRIDE-HC builder layout on narrow mobile viewports`

### Day 14 — Add `loading="lazy"` to any below-the-fold images
- [ ] **Files:** any HTML page with images (mostly the artifact READMEs render via GitHub, but check)
- **Why:** Page performance — only relevant if images are added later. If no images yet, skip and mark done.
- **Commit:** `Add loading="lazy" to images for faster initial render` (or skip if no images)

## Week 3 — Code quality

### Day 15 — Add type hints to `totp_gate.py`
- [ ] **File:** `mfa-shim/prototype/totp_gate.py`
- **Why:** Modern Python. Helps IDEs and reviewers. ~15 min for ~100 lines of code.
- **Commit:** `Add PEP 484 type hints to totp_gate.py`

### Day 16 — Add type hints to `session_recorder.py`
- [ ] **File:** `mfa-shim/prototype/session_recorder.py`
- **Commit:** `Add PEP 484 type hints to session_recorder.py`

### Day 17 — Add type hints to `tamper_detector.py`
- [ ] **File:** `mfa-shim/prototype/tamper_detector.py`
- **Commit:** `Add PEP 484 type hints to tamper_detector.py`

### Day 18 — Add `py.typed` marker
- [ ] **File:** `mfa-shim/prototype/py.typed` (empty)
- **Why:** PEP 561. Tells mypy/pyright that this package ships type info.
- **Commit:** `Mark MFA shim prototype as PEP 561 type-information-providing`

### Day 19 — Improve docstrings in `totp_gate.py`
- [ ] **File:** `mfa-shim/prototype/totp_gate.py`
- **Why:** Add Google-style docstrings with Args/Returns/Raises. Helps readers and Sphinx if you ever add docs gen.
- **Commit:** `Expand docstrings in totp_gate.py to Google style`

### Day 20 — Add `.pre-commit-config.yaml`
- [ ] **File:** `.pre-commit-config.yaml`
- **Why:** Run black, ruff, end-of-file-fixer on commit. Standard Python project hygiene.
- **Commit:** `Add pre-commit config (black, ruff, eof-fixer)`

### Day 21 — Add `pyproject.toml` to MFA shim prototype
- [ ] **File:** `mfa-shim/prototype/pyproject.toml`
- **Why:** Modern Python packaging. Allows `pip install -e .` for development; defines tool configs (black, ruff, mypy) centrally.
- **Commit:** `Add pyproject.toml to MFA shim prototype for modern packaging`

## Week 4 — Tests, content, DX

### Day 22 — Add MDRS test for non-normalised weights
- [ ] **File:** `mdrs-calculator/tests/test-cases.json`
- **Why:** What happens when weights don't sum to 1.0? Currently behaviour is unspecified. Add an explicit test.
- **Commit:** `Add MDRS test for non-normalised weight handling`

### Day 23 — Add MFA shim test for backoff retry
- [ ] **File:** `mfa-shim/prototype/tests/test_session_recorder.py`
- **Why:** Cover the SIEM forward retry behaviour with explicit timing assertion.
- **Commit:** `Add MFA shim test for SIEM forward backoff`

### Day 24 — Add fourth CJR worked example
- [ ] **File:** `cjr-templates/examples/cjr-unpatched-pacs-windows7.md`
- **Why:** Currently only infusion pump + PACS + service PIN examples. Add an Archetype 1 example for "no patches available on Windows 7 PACS workstation."
- **Effort:** ~15 min (skeleton from existing examples)
- **Commit:** `Add CJR example: unpatched Windows 7 PACS workstation`

### Day 25 — Add a fourth MDRS calculator preset
- [ ] **File:** `mdrs-calculator/index.html` (preset button) + `mdrs-calculator/calculator.js` (preset definition)
- **Why:** Currently 3 presets matching paper Table 7. Add a fourth for "ventilator (Archetype 2, life-sustaining)" to extend coverage.
- **Commit:** `Add ventilator preset to MDRS calculator`

### Day 26 — Add `.dockerignore` to test harness
- [ ] **File:** `test-harness/.dockerignore`
- **Why:** Speed up `docker compose build` by excluding `.venv`, `__pycache__`, `results/run-*`, etc.
- **Commit:** `Add .dockerignore to test harness for faster builds`

### Day 27 — Add a STRIDE-HC quick-reference card
- [ ] **File:** `stride-hc-templates/QUICK-REFERENCE.md`
- **Why:** One-page summary of the six categories with CAW weights and example threats. Useful as a tear-off.
- **Commit:** `Add STRIDE-HC quick-reference card`

### Day 28 — Update README test/license/DOI badges
- [ ] **File:** `README.md`
- **Why:** Currently has License, DOI, Python, Docker badges. Add tests-passing badge using shields.io (e.g., `[![tests](https://img.shields.io/badge/tests-52%2F52-brightgreen)]`).
- **Commit:** `Refresh README badges with current status indicators`

### Day 29 — Add reference to NIST CSF 2.0
- [ ] **File:** `cjr-templates/cjr-template.md` (normative references list)
- **Why:** NIST CSF 2.0 was released February 2024; the template should reference it specifically alongside NIST SP 800-82r3.
- **Commit:** `Reference NIST CSF 2.0 (Feb 2024) in CJR normative references`

### Day 30 — Tag v1.0.1 and close out the maintenance batch
- [ ] **Files:** `CHANGELOG.md` (move Unreleased → 1.0.1 section), `CITATION.cff` (version bump)
- **Why:** Closes the queue with a real version bump. Zenodo will mint a new versioned DOI; concept DOI continues to resolve to latest.
- **Commit:** `Release v1.0.1 — maintenance batch (Days 1-29 of MAINTENANCE-QUEUE.md)`
- **Manual follow-up:** On GitHub, create release `v1.0.1` against `main`; Zenodo will mint the new DOI within ~1 minute.

---

## When the queue is empty

Don't manufacture work. The repo is in great shape. After v1.0.1, future commits should be driven by:

- Real issues opened by users
- Real feature requests
- Real paper-revision implications (if reviewers request changes)
- Dependabot PRs (set up Day 2)
- Drift you notice when re-reading the artifacts months later

A repo that gets occasional commits when there's something real to commit is more credible than one with daily filler.
