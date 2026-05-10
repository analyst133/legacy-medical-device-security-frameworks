#!/usr/bin/env python3
"""
Scenario 01 — ARP cache poisoning (Spoofing, S category).

Simulates ARP cache poisoning to redirect device traffic. In a real environment
this would use scapy to send forged ARP responses; in this harness we report
outcome based on whether ARP traffic to the target is reachable.

Compensating controls expected to mitigate:
  - Network segmentation: target on different subnet, no Layer 2 adjacency
  - IPS with ARP-anomaly signature: not modelled in our basic IPS sidecar
  - Static ARP entries: not modelled

This scenario is intentionally simplified — its purpose is to exercise the
matrix execution flow, not to be a fully featured ARP attack.
"""

import os
import socket
import subprocess

STRIDE_HC = "S"
SCENARIO_NAME = "01-spoofing-arp-poisoning"

TARGET_HOST = os.environ.get("TARGET_HOST", "172.28.10.20")


def is_target_reachable() -> bool:
    try:
        with socket.create_connection((TARGET_HOST, 8080), timeout=2):
            return True
    except (OSError, socket.timeout):
        return False


def run() -> dict:
    print(f"[01] Probing target Layer 3 reachability to {TARGET_HOST}")
    reachable = is_target_reachable()

    # In a real attack we'd send forged ARP and confirm cache poisoning.
    # Here we infer the control posture from reachability — segmentation drops
    # traffic at the IP layer, which is a stricter form of the same defence.

    if not reachable:
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "BLOCKED",
            "detail": "Target unreachable — segmentation or IPS blocked the path",
        }

    # Attempt the ARP step (best-effort; we don't have scapy in the slim image)
    try:
        result = subprocess.run(
            ["ip", "neigh", "show", TARGET_HOST],
            capture_output=True, timeout=5, text=True,
        )
        arp_entry = result.stdout.strip()
    except Exception as e:
        arp_entry = f"(error: {e})"

    return {
        "scenario": SCENARIO_NAME,
        "stride_hc": STRIDE_HC,
        "outcome": "REACHABLE",
        "detail": f"L3 reachable; ARP entry: {arp_entry or 'none'}",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
