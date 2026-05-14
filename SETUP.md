# SETUP — Getting started with the repository

A step-by-step setup guide for new users. Every command is shown for **Linux**, **macOS**, and **Windows** (Git Bash + PowerShell variants).

**Most users don't need to install anything** — see Step 0. Install only the artifacts you actually plan to use.

---

## Step 0 — Try it with zero install

**[Open the live MDRS calculator →](https://analyst133.github.io/legacy-medical-device-security-frameworks/mdrs-calculator/)**

This runs in any modern browser — no install, no clone, no setup. Answer the five guided questions or click one of the three paper presets to see the calculator reproduce paper Table 7 exactly.

If you only want the calculator, **stop here**. For everything else, continue.

---

## Step 1 — Prerequisites

You don't need all of these — install only the ones for the artifacts you'll use.

| Tool | Required for | Linux install | macOS install | Windows install |
|---|---|---|---|---|
| **git** | Cloning the repo | `sudo apt install git` (Debian/Ubuntu) / `sudo dnf install git` (Fedora) | `brew install git` | https://git-scm.com/download/win |
| **Node.js 18+** | MDRS calculator unit tests | `sudo apt install nodejs` or use [nvm](https://github.com/nvm-sh/nvm) | `brew install node` | https://nodejs.org/en/download |
| **Python 3.10+** | MFA shim prototype + tests | `sudo apt install python3 python3-venv python3-pip` | `brew install python@3.11` | https://www.python.org/downloads/ |
| **Docker + Docker Compose v2** | Test harness | https://docs.docker.com/engine/install/ | [Docker Desktop](https://www.docker.com/products/docker-desktop) | [Docker Desktop](https://www.docker.com/products/docker-desktop) |

**Verify what you have:**

```bash
git --version
node --version
python --version       # or python3 --version on some Linux distros
docker --version
docker compose version
```

---

## Step 2 — Clone the repo

```bash
git clone https://github.com/analyst133/legacy-medical-device-security-frameworks.git
cd legacy-medical-device-security-frameworks
```

Confirm the file tree:

```bash
ls -la
```

You should see five artifact directories — `mdrs-calculator/`, `stride-hc-templates/`, `cjr-templates/`, `test-harness/`, `mfa-shim/` — plus `README.md`, `WALKTHROUGH.md`, `SETUP.md` (this file), `LICENSE`, `CITATION.cff`, and `requirements.txt`.

---

## Step 3 — MDRS Calculator (no install required)

The calculator is a pure HTML/JavaScript application. Open `index.html` directly:

| Platform | Command |
|---|---|
| **Linux** | `xdg-open mdrs-calculator/index.html` |
| **macOS** | `open mdrs-calculator/index.html` |
| **Windows (Git Bash)** | `start mdrs-calculator/index.html` |
| **Windows (PowerShell)** | `start mdrs-calculator/index.html` |
| **Windows (CMD)** | `start mdrs-calculator\index.html` |

**Verify the math** with the unit-test suite (validates the calculator reproduces paper Section 5 exactly):

```bash
cd mdrs-calculator
node tests/run-tests.js
cd ..
```

Expected output: `15 test(s); 15 passed; 0 failed.`

The first three tests reproduce the paper's worked presets (infusion pump, PACS server, ECG monitor) to the third decimal place.

---

## Step 4 — Templates (no install required)

The STRIDE-HC and CJR templates are plain Markdown / YAML / JSON files. Open them in any editor or read directly on GitHub.

**Recommended reading order for a first-time user:**

```bash
# Worked example first — see what a completed artifact looks like
$EDITOR stride-hc-templates/examples/infusion-pump.md

# Then the blank template you'd fill in for your own device
$EDITOR stride-hc-templates/stride-hc-template.md

# Then the 30-minute first-time-user walkthrough
$EDITOR stride-hc-templates/WALKTHROUGH.md
```

`$EDITOR` is your default editor on Linux/macOS. On Windows, substitute `notepad`, `code` (VS Code), or any markdown viewer.

Same pattern for the CJR templates:

```bash
$EDITOR cjr-templates/examples/cjr-no-mfa-infusion-pump.md
$EDITOR cjr-templates/cjr-template.md
$EDITOR cjr-templates/WALKTHROUGH.md
```

---

## Step 5 — MFA Shim Prototype (Python)

The prototype is portable Python 3.10+ code. **Same source on Linux, macOS, and Windows**; only the venv activation command differs.

### 5.1 Create and activate a virtual environment

Choose **one** of: install everything from the repo root (recommended — uses the aggregator), or install from the prototype directory only.

#### Option A — From the repo root (recommended for first-time setup)

```bash
# Inside the repo root:
python -m venv .venv         # use python3 on some Linux distros if python is Python 2
```

Then activate the venv — **the activation command differs per platform / shell**:

| Platform / shell | Activation command |
|---|---|
| **Linux / macOS** (bash / zsh) | `source .venv/bin/activate` |
| **Windows Git Bash** | `source .venv/Scripts/activate` |
| **Windows PowerShell** | `.venv\Scripts\Activate.ps1` |
| **Windows CMD** | `.venv\Scripts\activate.bat` |

Once activated, your shell prompt should show `(.venv)`. Then install:

```bash
pip install -r requirements.txt
```

This pulls in all Python deps for the repo (currently: `pyotp`, `PyYAML`, `pyserial`, `pytest`).

#### Option B — From the prototype directory

If you only care about the MFA shim and prefer a co-located venv:

```bash
cd mfa-shim/prototype
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# (or one of the Windows activation lines above)
pip install -r requirements.txt
```

### 5.2 Run the unit tests

```bash
cd mfa-shim/prototype             # if not already there
python -m pytest tests/ -v
```

Expected output: `37 passed in <time>s`.

Coverage:
- `test_totp_gate.py` — 16 tests (TOTP authentication, replay protection, lockout, concurrency)
- `test_session_recorder.py` — 10 tests (session lifecycle, SIEM forwarding, force-close on emergency)
- `test_tamper_detector.py` — 11 tests (state transitions, sensor polling, callback isolation)

### 5.3 Run the daemon (optional — requires a virtual serial pair)

The shim daemon proxies traffic between a technician-facing serial port and a device-facing serial port, gating it with TOTP authentication. For development you create a virtual serial pair with `socat`.

| Platform | Virtual serial-pair tool | Install |
|---|---|---|
| **Linux** | `socat` | `sudo apt install socat` |
| **macOS** | `socat` | `brew install socat` |
| **Windows** | `com0com` (alternative — usage differs) | https://com0com.sourceforge.net/ |

Linux / macOS workflow:

```bash
# Terminal 1 — create the virtual serial pair:
socat -d -d PTY,link=/tmp/shim-tech,raw,echo=0 PTY,link=/tmp/shim-dev,raw,echo=0

# Terminal 2 — copy and customize the config:
cd mfa-shim/prototype
cp config.example.yaml config.yaml

# Generate a TOTP secret for one technician:
python -c "import pyotp; print(pyotp.random_base32())"
# Paste the secret into config.yaml under technicians[].totp_secret

# Terminal 2 — run the daemon:
python shim.py --config config.yaml --log-level INFO

# Terminal 3 — connect as if you're a technician with serial tooling:
picocom /tmp/shim-tech         # or:  screen /tmp/shim-tech 9600
```

You should see the challenge prompt. Authenticate as `<user>@<domain> <current-totp-code>` (get the TOTP code from your authenticator app or `python -c "import pyotp; print(pyotp.TOTP('YOUR-SECRET').now())"`). On success, the connection passes through to the device-facing endpoint.

For full enrolment workflow, hardware port notes, and SIEM transport configuration, see [`mfa-shim/prototype/README.md`](mfa-shim/prototype/README.md). For production hardware considerations, see [`mfa-shim/hardware/README.md`](mfa-shim/hardware/README.md). **Before any clinical deployment**, read [`mfa-shim/FDA-CONSIDERATIONS.md`](mfa-shim/FDA-CONSIDERATIONS.md).

---

## Step 6 — Test Harness (Docker)

The harness runs a Dockerised multi-container environment. **Make sure Docker is running first:**

| Platform | Verify Docker is running |
|---|---|
| **Linux** | `systemctl status docker` (or `sudo systemctl start docker` to start it) |
| **macOS** | Open Docker Desktop from Applications; wait for the whale icon to stop animating |
| **Windows** | Open Docker Desktop; wait for the whale icon to show "Docker Desktop is running" |

Then bring up the harness:

```bash
cd test-harness

# Baseline — target + workstation + attacker only, no compensating controls:
docker compose up -d

# Verify the target device is reachable:
curl http://localhost:8080/status

# Run a single scenario (default-credential exploit):
docker compose exec attacker python scenarios/05-eop-default-credential.py

# Run the same scenario with the IPS compensating control enabled:
docker compose down
docker compose --profile ips up -d
docker compose exec attacker python scenarios/05-eop-default-credential.py
# Expected: BLOCKED_NET (control prevents the exploit)

# Run the full matrix — all 5 scenarios across all 5 control profiles:
make matrix
# Results written to results/run-<timestamp>/results.csv

# Tear it down when done:
docker compose down
```

For experimental design, statistical considerations, the expected outcome matrix, and how harness output feeds CJR effectiveness validation + MDRS CCD scoring, see [`test-harness/METHODOLOGY.md`](test-harness/METHODOLOGY.md).

**Linux note:** if `make` isn't installed, run `sudo apt install make` (Debian/Ubuntu) or `sudo dnf install make` (Fedora). Alternatively, read the Makefile and execute the equivalent shell commands directly.

**Windows note:** `make matrix` may not work in PowerShell or CMD because `make` isn't a default Windows tool. Either install it via Chocolatey (`choco install make`), use Git Bash which usually has it, or use WSL2 (which gives you a full Linux environment for the harness).

---

## Step 7 — Read the walkthroughs

You've now installed (or verified) every artifact you wanted. The substantive learning starts now:

| # | Read | Time | What you'll learn |
|---|---|---|---|
| 1 | [`WALKTHROUGH.md`](WALKTHROUGH.md) | 15 min | How the five artifacts compose into one workflow — infusion-pump example traced end-to-end |
| 2 | [`stride-hc-templates/WALKTHROUGH.md`](stride-hc-templates/WALKTHROUGH.md) | 30 min | How to build a threat model from blank to completed |
| 3 | [`cjr-templates/WALKTHROUGH.md`](cjr-templates/WALKTHROUGH.md) | 30 min | How to write a defensible Control Justification Record |
| 4 | [`test-harness/METHODOLOGY.md`](test-harness/METHODOLOGY.md) | 10 min | How to design experiments + interpret results |
| 5 | [`mfa-shim/FDA-CONSIDERATIONS.md`](mfa-shim/FDA-CONSIDERATIONS.md) | 10 min | Regulatory analysis of inline-device modification |

The paper is the authoritative source — these walkthroughs are operational guides for adopting the framework, not a substitute for the paper's reasoning.

---

## Summary table — install time per artifact

| Artifact | Install time | What you get |
|---|---|---|
| MDRS calculator (live) | 0 minutes | Working calculator in your browser |
| MDRS calculator (local + tests) | ~2 minutes | Local copy + 15/15 unit tests passing |
| STRIDE-HC templates | 0 minutes | Markdown files; just read them |
| CJR templates | 0 minutes | Markdown files; just read them |
| MFA shim prototype | ~2 minutes | 37/37 unit tests passing |
| Test harness | ~5 minutes (first Docker image pull) | Empirical control-effectiveness evidence |

**Total fresh setup for someone who wants everything: ~10 minutes** on a machine that already has git, Node.js, Python, and Docker installed. Add 5–20 minutes per tool you need to install from scratch.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `node: command not found` | Node.js not installed | Install per Step 1 |
| `python: command not found` (Linux) | On some Linux distros, the executable is `python3`, not `python` | Use `python3` everywhere, or `alias python=python3` in your shell |
| `pip install` fails with TLS errors | Outdated pip | `python -m pip install --upgrade pip` |
| Pytest hangs or session-recorder test fails on Windows | Older code path; should be fixed in current main | `git pull` and retry; the fixture now force-closes leaked sessions on teardown |
| `docker compose up` says "port already in use" | Another service already bound to port 8080 or 2575 | Stop the other service, or edit `test-harness/docker-compose.yml` to use different host ports |
| `make: command not found` (Windows) | Make isn't a default Windows tool | Install via Chocolatey, use Git Bash, or use WSL2 |
| `socat: command not found` (Windows) | Socat isn't available for Windows | Use `com0com` instead, or do the daemon evaluation in WSL2 |
| `xdg-open` fails on a headless Linux server | No display | Just open `mdrs-calculator/index.html` via the live URL or copy the directory to a machine with a browser |

---

## Cleaning up

When you're done evaluating:

```bash
# MFA shim venv:
deactivate                          # Exit the venv
rm -rf .venv                        # Linux / macOS / Git Bash
Remove-Item -Recurse -Force .venv   # PowerShell

# Test harness:
cd test-harness
docker compose down -v              # -v also removes the named volumes
docker compose --profile ips --profile pam --profile segmentation down -v

# Remove all harness images (optional):
docker image rm $(docker images -q --filter "reference=test-harness*")
```

---

## Need help?

- **Issues / bugs:** open an issue at https://github.com/analyst133/legacy-medical-device-security-frameworks/issues
- **Security concerns:** see [`SECURITY.md`](SECURITY.md)
- **Contributing:** see [`CONTRIBUTING.md`](CONTRIBUTING.md)
- **Citing this work:** see [`README.md`](README.md) — Citing this work section
