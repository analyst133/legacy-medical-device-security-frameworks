#!/usr/bin/env python3
"""
Scenario 03 — Cleartext HL7 sniffing (Information Disclosure, I category).

Listens on the network for cleartext HL7 traffic between workstation and pump.
In a real environment this would use scapy or libpcap; in this harness we use
tcpdump to capture frames briefly and check whether HL7 patient identifiers
are observable.

Compensating controls expected to mitigate:
  - Network segmentation: attacker not on same VLAN
  - IPSec encapsulation: not modelled in this basic harness
  - Protocol-aware proxy with TLS: not modelled in basic config
"""

import os
import re
import subprocess
import time

STRIDE_HC = "I"
SCENARIO_NAME = "03-info-disclosure-cleartext-hl7"

TARGET_HOST = os.environ.get("TARGET_HOST", "172.28.10.20")
HL7_PORT = int(os.environ.get("TARGET_HL7_PORT", "2575"))


def run() -> dict:
    # Capture for 12 seconds (workstation should send at least one HL7 message)
    print(f"[03] Capturing HL7 traffic on port {HL7_PORT} for 12 seconds")
    try:
        result = subprocess.run(
            [
                "tcpdump",
                "-i", "any",
                "-A",                 # ASCII payload
                "-s", "0",            # full packets
                "-n",                 # no name resolution
                "-c", "20",           # at most 20 packets
                f"port {HL7_PORT}",
            ],
            capture_output=True, timeout=15, text=True,
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired as e:
        output = (e.stdout or "") + (e.stderr or "")
    except Exception as e:
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "ERROR",
            "detail": f"tcpdump invocation failed: {e}",
        }

    # Look for HL7 segments — MSH header, PID segment with patient identifier
    has_msh = "MSH|" in output
    pid_match = re.search(r"PID\|\|\|(\d+)", output)
    patient_mrn = pid_match.group(1) if pid_match else None

    if has_msh and patient_mrn:
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "SUCCESS",
            "detail": f"HL7 PHI captured in cleartext; patient MRN observed: {patient_mrn}",
        }
    if has_msh:
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "PARTIAL",
            "detail": "HL7 frame structure visible but no PID segment captured in this window",
        }

    return {
        "scenario": SCENARIO_NAME,
        "stride_hc": STRIDE_HC,
        "outcome": "BLOCKED",
        "detail": "No HL7 traffic visible on attacker's network position",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
