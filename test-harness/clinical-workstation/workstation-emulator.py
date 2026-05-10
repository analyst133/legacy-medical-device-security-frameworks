#!/usr/bin/env python3
"""
Clinical workstation emulator.

Generates baseline HL7 traffic and periodic management-interface health checks,
producing the realistic background traffic that attack scenarios must blend into
(or be detected against).
"""

import logging
import os
import random
import socket
import time
import urllib.request
import urllib.error
import base64

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [workstation] %(levelname)s %(message)s",
)
log = logging.getLogger("workstation")

TARGET_HOST = os.environ.get("TARGET_HOST", "172.28.10.20")
HL7_PORT = int(os.environ.get("TARGET_HL7_PORT", "2575"))
MGMT_PORT = int(os.environ.get("TARGET_MGMT_PORT", "8080"))

SERVICE_USER = "service"
SERVICE_PASS = "Vendor1234"


def send_hl7_message(patient_mrn: str, drug: str) -> bool:
    """Send a synthetic HL7 v2 ADT^A01 message."""
    timestamp = time.strftime("%Y%m%d%H%M%S")
    msg = (
        f"\x0bMSH|^~\\&|EHR|FACILITY|PUMP|FACILITY|{timestamp}||"
        f"ADT^A01|MSG{random.randint(10000, 99999)}|P|2.5\r"
        f"PID|||{patient_mrn}||PATIENT^TEST||19700101|M\r"
        f"OBR|1||||{drug}\r"
        f"\x1c\x0d"
    )
    try:
        with socket.create_connection((TARGET_HOST, HL7_PORT), timeout=5) as s:
            s.sendall(msg.encode("ascii"))
            ack = s.recv(4096)
        return b"MSA|AA" in ack
    except (OSError, socket.timeout) as e:
        log.warning("HL7 send failed: %s", e)
        return False


def health_check() -> bool:
    try:
        req = urllib.request.Request(
            f"http://{TARGET_HOST}:{MGMT_PORT}/status",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, socket.timeout):
        return False


def authenticated_check() -> bool:
    try:
        token = base64.b64encode(f"{SERVICE_USER}:{SERVICE_PASS}".encode()).decode()
        req = urllib.request.Request(
            f"http://{TARGET_HOST}:{MGMT_PORT}/infusion",
            headers={"Authorization": f"Basic {token}"},
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except urllib.error.URLError:
        return False


def main():
    log.info("Workstation starting; target=%s HL7=%d mgmt=%d", TARGET_HOST, HL7_PORT, MGMT_PORT)
    drugs = ["saline", "morphine", "vancomycin", "heparin", "insulin"]

    while True:
        # Steady-state HL7 traffic
        ok = send_hl7_message(
            patient_mrn=f"{random.randint(1000000, 9999999)}",
            drug=random.choice(drugs),
        )
        log.info("HL7 ADT sent — ack=%s", ok)

        # Periodic management probes
        log.info("Status probe — %s", "OK" if health_check() else "DOWN")
        log.info("Authenticated check — %s", "OK" if authenticated_check() else "FAIL")

        time.sleep(random.uniform(8, 15))


if __name__ == "__main__":
    main()
