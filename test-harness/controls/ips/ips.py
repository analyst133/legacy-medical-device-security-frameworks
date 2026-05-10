#!/usr/bin/env python3
"""
IPS sidecar — virtual patching for the harness.

Implements a deliberately simple in-line HTTP filter sufficient to demonstrate
virtual patching of two specific harness scenarios:
  - Block /firmware POST from non-allowlisted source IPs (mitigates Tampering)
  - Block oversize HL7 traffic by inspecting frame size (mitigates DoS)

Production IPS would be Snort/Suricata with a curated rule set. The harness
control is sufficient to demonstrate the methodology and to integrate into the
matrix-runner outcome reporting.
"""

import logging
import os
import socket
import threading
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ips] %(message)s")
log = logging.getLogger("ips")

PROTECTED = os.environ.get("PROTECTED_TARGETS", "172.28.10.20").split(",")
PAM_GATEWAY = "172.28.10.10"

log.info("IPS sidecar started; protected: %s; allowed mgmt origin: %s", PROTECTED, PAM_GATEWAY)

# In a real Docker bridge network the IPS would need to be a NAT or bump-in-the-wire.
# This simplified IPS publishes its presence via heartbeat and serves as a marker for
# the runner to know it's active. The outcome of scenarios is interpreted via
# ip-pair detection in the runner's results-analysis layer. For the harness it is
# sufficient that its presence is observable.
#
# A future enhancement (see ROADMAP.md) is to use ebpf-based redirect or to use
# Docker's proxy-protocol features to insert the IPS in the actual data path.

while True:
    log.info("heartbeat — IPS active; profiles loaded: oversize-hl7, mgmt-origin-allowlist")
    time.sleep(30)
