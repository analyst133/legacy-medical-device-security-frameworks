#!/usr/bin/env python3
"""
PAM upstream gateway — Pattern A reference implementation.

The PAM gateway:
  1. Listens on TCP/8080 (the same port as the device management interface)
  2. Authenticates incoming requests against an in-memory user database with TOTP
  3. Forwards authenticated requests to the protected target with the vault-stored
     hardcoded device credential
  4. Records every session

In the harness, scenarios that target the device's mgmt interface directly
(by IP) bypass this gateway. The compose configuration is responsible for
ensuring that the only path from the attacker container to the device's mgmt
interface goes through the PAM. In a production deployment this is enforced
via network ACLs at the device's VLAN.

This is a teaching reference, not a production PAM. It demonstrates the
principle that the device's hardcoded credential is held server-side and never
disclosed to the user.
"""

import base64
import logging
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [pam] %(message)s")
log = logging.getLogger("pam")

VAULT_CREDENTIAL = os.environ.get("VAULT_CREDENTIAL", "service:Vendor1234")
PROTECTED_TARGET = os.environ.get("PROTECTED_TARGET", "172.28.10.20")
PROTECTED_PORT = int(os.environ.get("PROTECTED_PORT", "8080"))

# Demonstration user database. Each user has a TOTP-equivalent factor (here
# simplified to a static second factor for demonstration; the MFA shim artifact
# implements proper TOTP).
USER_DB = {
    "alice@example.com": {"password": "AlicePassword!1", "factor": "111111"},
    "bob@example.com": {"password": "BobPassword!1", "factor": "222222"},
}


class PamHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        log.info("%s - %s", self.client_address[0], fmt % args)

    def _check_user_auth(self):
        """
        Two-factor: HTTP Basic for password, X-Auth-Factor for second factor.
        """
        auth = self.headers.get("Authorization", "")
        factor = self.headers.get("X-Auth-Factor", "")
        if not auth.startswith("Basic "):
            return None
        try:
            user, _, pwd = base64.b64decode(auth[6:]).decode().partition(":")
        except Exception:
            return None
        rec = USER_DB.get(user)
        if not rec:
            return None
        if rec["password"] != pwd:
            return None
        if rec["factor"] != factor:
            return None
        return user

    def _proxy(self, user: str):
        # Build a request to the protected target using the VAULT credential
        target_token = base64.b64encode(VAULT_CREDENTIAL.encode()).decode()
        target_url = f"http://{PROTECTED_TARGET}:{PROTECTED_PORT}{self.path}"

        body = None
        if self.command == "POST":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)

        req = urllib.request.Request(
            target_url,
            data=body,
            method=self.command,
            headers={
                "Authorization": f"Basic {target_token}",
                "Content-Type": self.headers.get("Content-Type", "application/json"),
            },
        )
        log.info("PAM session: user=%s method=%s path=%s", user, self.command, self.path)

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                response_body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(response_body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            log.warning("Proxy error: %s", e)
            self.send_response(502)
            self.end_headers()

    def do_GET(self):
        user = self._check_user_auth()
        if user is None:
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\"PAM\"")
            self.end_headers()
            self.wfile.write(b"PAM authentication required")
            return
        self._proxy(user)

    def do_POST(self):
        user = self._check_user_auth()
        if user is None:
            self.send_response(401)
            self.send_header("WWW-Authenticate", "Basic realm=\"PAM\"")
            self.end_headers()
            self.wfile.write(b"PAM authentication required")
            return
        self._proxy(user)


def main():
    log.info("PAM upstream listening on TCP/8080; protected target %s:%d", PROTECTED_TARGET, PROTECTED_PORT)
    HTTPServer(("0.0.0.0", 8080), PamHandler).serve_forever()


if __name__ == "__main__":
    main()
