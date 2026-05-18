# Convenience targets for the legacy medical device security frameworks repo.
# Run `make help` to see what's available.

.PHONY: help test test-mdrs test-mfa-shim test-all serve clean venv harness harness-down

help:
	@echo "Targets:"
	@echo "  make test          Run all 52 unit tests (MDRS + MFA shim)"
	@echo "  make test-mdrs     Run MDRS calculator tests only (15)"
	@echo "  make test-mfa-shim Run MFA shim prototype tests only (37)"
	@echo "  make serve         Serve the repo at http://localhost:8000 (Python http.server)"
	@echo "  make venv          Create .venv and install MFA shim requirements"
	@echo "  make harness       Bring up the test harness baseline (Docker Compose)"
	@echo "  make harness-down  Tear down the test harness"
	@echo "  make clean         Remove caches, venv, and Docker volumes"

test: test-mdrs test-mfa-shim

test-mdrs:
	@echo "=== MDRS calculator tests ==="
	cd mdrs-calculator && node tests/run-tests.js

test-mfa-shim:
	@echo "=== MFA shim prototype tests ==="
	cd mfa-shim/prototype && python -m pytest tests/ -v

test-all: test
	@echo "All 52 tests passed."

venv:
	python -m venv .venv
	@echo "Activate with:"
	@echo "  source .venv/bin/activate          # Linux / macOS"
	@echo "  source .venv/Scripts/activate      # Git Bash on Windows"
	@echo "Then: pip install -r requirements.txt"

serve:
	@echo "Serving repo at http://localhost:8000"
	@echo "  Calculator:        http://localhost:8000/mdrs-calculator/"
	@echo "  STRIDE-HC builder: http://localhost:8000/stride-hc-templates/"
	@echo "  CJR builder:       http://localhost:8000/cjr-templates/"
	@echo "  Test harness:      http://localhost:8000/test-harness/"
	@echo "  MFA shim demo:     http://localhost:8000/mfa-shim/"
	python -m http.server 8000

harness:
	cd test-harness && docker compose up -d

harness-down:
	cd test-harness && docker compose down -v

clean:
	@echo "Removing caches and venv..."
	rm -rf .venv mfa-shim/prototype/.venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	@echo "Done."
