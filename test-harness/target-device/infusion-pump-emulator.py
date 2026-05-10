#!/usr/bin/env python3
"""
Archetype 2 Infusion Pump Emulator.

Deliberately reproduces the security characteristics of a real-world Archetype 2
embedded RTOS infusion pump:
  - Cleartext HL7 v2 listener on TCP/2575
  - Cleartext HTTP management interface on TCP/8080
  - Hardcoded service-mode credential
  - No per-user authentication
  - No audit logging on the device itself
  - Simulated protocol-parser fragility (bounded message length)

This is a TEST TARGET for the harness. It is not a representation of any specific
commercial product, and it is not safe to deploy outside the harness's isolated
Docker network.
"""

import json
import logging
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Deliberate: hardcoded credentials reproducing the constraint under test
SERVICE_USER = "service"
SERVICE_PASS = "Vendor1234"

# Deliberate: protocol parser has a fixed buffer that the DoS scenario will exploit
HL7_MAX_MESSAGE = 32 * 1024

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [pump] %(levelname)s %(message)s",
)
log = logging.getLogger("pump")

# Shared mutable state — therapy parameters that scenarios may attempt to modify
state = {
    "model": "ExampleMed Volumetric Infusion Pump v3.2 (emulated)",
    "firmware_version": "3.2.7",
    "running": True,
    "infusion": {
        "patient_mrn": "0000000",
        "drug": "saline",
        "rate_ml_per_hour": 100.0,
        "vtbi_ml": 250.0,
        "infused_ml": 0.0,
    },
    "service_mode_active": False,
    "last_hl7_received": None,
    "uptime_started": time.time(),
}
state_lock = threading.Lock()


# ───────────────────────── HL7 listener (TCP/2575) ─────────────────────────

def hl7_listener():
    """
    Bare-bones HL7 v2 over MLLP-ish listener.
    Accepts cleartext messages and ACKs each one. No authentication.
    Vulnerable to a malformed-message DoS in the protocol parser.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 2575))
    server.listen(8)
    log.info("HL7 listener accepting on TCP/2575 (cleartext, unauthenticated)")

    while state["running"]:
        try:
            client, addr = server.accept()
        except OSError:
            break
        threading.Thread(target=handle_hl7, args=(client, addr), daemon=True).start()


def handle_hl7(client: socket.socket, addr):
    try:
        client.settimeout(10)
        data = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > HL7_MAX_MESSAGE:
                # Simulated protocol-parser DoS: oversize input crashes the listener
                # In a real Archetype 2 device, this would correspond to URGENT/11-class
                # input-handling vulnerabilities causing a device fault.
                log.error("HL7 parser fault: oversize message from %s (%d bytes) — emulating crash and recovery", addr, len(data))
                client.close()
                # Emulate brief unavailability
                time.sleep(2)
                return

            if b"\x1c\x0d" in data:   # MLLP end-of-message
                break

        if not data:
            client.close()
            return

        message = data.decode("ascii", errors="replace")
        log.info("HL7 message received from %s (%d bytes)", addr, len(message))
        with state_lock:
            state["last_hl7_received"] = {
                "timestamp": time.time(),
                "source": f"{addr[0]}:{addr[1]}",
                "snippet": message[:200],
            }

        # ACK
        ack = (
            "\x0bMSH|^~\\&|PUMP|FACILITY|WORKSTATION|FACILITY|"
            f"{int(time.time())}|"
            "|ACK^A01|MSG00001|P|2.5\rMSA|AA|MSG00001\r\x1c\x0d"
        )
        client.sendall(ack.encode("ascii"))
    except Exception as e:
        log.warning("HL7 handler error: %s", e)
    finally:
        client.close()


# ─────────────────── Management HTTP interface (TCP/8080) ───────────────────

class MgmtHandler(BaseHTTPRequestHandler):
    """
    Trivially-authenticated HTTP management interface.
    Reproduces the constraint: hardcoded credential, no MFA, no per-user auth.
    """
    def log_message(self, fmt, *args):
        log.info("mgmt %s - %s", self.client_address[0], fmt % args)

    def _check_auth(self) -> bool:
        # Authorization: Basic <base64(user:pass)>
        import base64
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(auth[6:]).decode("ascii")
            user, _, pwd = decoded.partition(":")
            return user == SERVICE_USER and pwd == SERVICE_PASS
        except Exception:
            return False

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # /status is unauthenticated (typical for legacy devices' "is-alive" endpoint)
        if self.path == "/status":
            with state_lock:
                self._json({
                    "model": state["model"],
                    "firmware_version": state["firmware_version"],
                    "running": state["running"],
                    "uptime_seconds": int(time.time() - state["uptime_started"]),
                })
            return

        if not self._check_auth():
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\"PumpService\"")
            self.end_headers()
            return

        if self.path == "/infusion":
            with state_lock:
                self._json(state["infusion"])
        elif self.path == "/service-mode":
            with state_lock:
                self._json({"active": state["service_mode_active"]})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._check_auth():
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\"PumpService\"")
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        if self.path == "/infusion":
            with state_lock:
                # Deliberately accepts arbitrary parameters — reproduces the
                # constraint that the device has no input validation
                state["infusion"].update(payload)
                log.warning(
                    "infusion parameters modified by %s: %s",
                    self.client_address[0], payload,
                )
            self._json({"ok": True, "infusion": state["infusion"]})
        elif self.path == "/service-mode":
            with state_lock:
                state["service_mode_active"] = bool(payload.get("active", False))
                log.warning(
                    "service mode toggled by %s: active=%s",
                    self.client_address[0], state["service_mode_active"],
                )
            self._json({"ok": True, "active": state["service_mode_active"]})
        elif self.path == "/firmware":
            # Emulated firmware push — accepts and "applies" any payload (constraint)
            with state_lock:
                state["firmware_version"] = payload.get("version", "unknown")
                log.warning(
                    "firmware updated by %s to version %s (emulated; no signature check)",
                    self.client_address[0], state["firmware_version"],
                )
            self._json({"ok": True, "firmware_version": state["firmware_version"]})
        else:
            self.send_response(404)
            self.end_headers()


def mgmt_listener():
    server = HTTPServer(("0.0.0.0", 8080), MgmtHandler)
    log.info("Management interface accepting on TCP/8080 (cleartext, basic auth, hardcoded credential)")
    server.serve_forever()


# ───────────────────────────── main ─────────────────────────────

def main():
    log.info("Starting %s", state["model"])
    threading.Thread(target=hl7_listener, daemon=True).start()
    threading.Thread(target=mgmt_listener, daemon=True).start()
    try:
        while True:
            time.sleep(60)
            with state_lock:
                # Simulated infusion progress
                inf = state["infusion"]
                if inf["infused_ml"] < inf["vtbi_ml"]:
                    inf["infused_ml"] = min(inf["vtbi_ml"], inf["infused_ml"] + (inf["rate_ml_per_hour"] / 60))
    except KeyboardInterrupt:
        log.info("Shutting down")


if __name__ == "__main__":
    main()
