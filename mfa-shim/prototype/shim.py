#!/usr/bin/env python3
"""
Pattern C MFA shim daemon.

Wires together the TOTP gate, session recorder, and tamper detector. Manages
the technician-side and device-side serial endpoints and runs the state
machine described in ARCHITECTURE.md.

This daemon runs against either:
  - A pair of virtual serial endpoints (for development and CI). Use socat:
      socat -d -d PTY,link=/tmp/shim-tech,raw,echo=0 PTY,link=/tmp/shim-dev,raw,echo=0
  - Real serial hardware (for hardware port deployments).

For production hardware deployment see hardware/README.md.
"""

from __future__ import annotations

import argparse
import enum
import logging
import os
import pathlib
import signal
import sys
import threading
import time
from typing import Optional

import yaml

from totp_gate import TotpGate, TechnicianRecord, AuthResult
from session_recorder import SessionRecorder, NoopSiemTransport, Direction
from tamper_detector import TamperDetector, TamperEvent

log = logging.getLogger("shim.daemon")


class State(enum.Enum):
    IDLE = "IDLE"
    CHALLENGE = "CHALLENGE"
    OPEN = "OPEN"
    LOCKED = "LOCKED"
    EMERGENCY_STOP = "EMERGENCY_STOP"


# ────────────── Serial endpoint abstractions ──────────────

class SerialEndpoint:
    """
    Wrapper around a serial-like file. We don't import pyserial in the
    prototype default path because tests can substitute pipes; pyserial is
    used when the configured device path is a /dev/tty* or /dev/serial/*.
    """

    def __init__(self, path: str, baudrate: int):
        self.path = path
        self.baudrate = baudrate
        self._handle = None
        self._is_pyserial = False

    def open(self):
        if self.path.startswith(("/dev/tty", "/dev/serial")) and os.path.exists(self.path):
            import serial  # pyserial — imported lazily so prototype tests don't need it
            self._handle = serial.Serial(self.path, baudrate=self.baudrate, timeout=0.1)
            self._is_pyserial = True
        else:
            # Treat as a regular file (e.g., a PTY created by socat or a Unix pipe)
            self._handle = open(self.path, "r+b", buffering=0)

    def read(self, n: int) -> bytes:
        if self._is_pyserial:
            return self._handle.read(n) or b""
        # Best-effort non-blocking read for file-like
        try:
            return self._handle.read(n) or b""
        except (BlockingIOError, OSError):
            return b""

    def write(self, data: bytes) -> None:
        if self._handle is None:
            return
        self._handle.write(data)
        if self._is_pyserial:
            self._handle.flush()

    def close(self):
        if self._handle is not None:
            self._handle.close()
            self._handle = None


# ────────────── Daemon ──────────────

class ShimDaemon:
    def __init__(self, config: dict):
        self._config = config

        # State
        self._state_lock = threading.Lock()
        self._state = State.IDLE

        # Identity
        self._shim_id = config["shim"]["id"]

        # Components
        users = {
            tech["technician_id"]: TechnicianRecord(
                technician_id=tech["technician_id"],
                totp_secret=tech["totp_secret"],
                enrolment_date=tech.get("enrolment_date", ""),
                notes=tech.get("notes", ""),
            )
            for tech in config["technicians"]
        }
        totp_cfg = config.get("totp", {})
        self._gate = TotpGate(
            users,
            period=totp_cfg.get("period", 30),
            digits=totp_cfg.get("digits", 6),
            window=totp_cfg.get("window", 1),
            max_failures=totp_cfg.get("max_failures", 5),
            lockout_seconds=totp_cfg.get("lockout_seconds", 300),
        )

        storage_root = config["storage"]["root"]
        pathlib.Path(storage_root).mkdir(parents=True, exist_ok=True)
        self._recorder = SessionRecorder(
            storage_root=storage_root,
            shim_id=self._shim_id,
            siem=NoopSiemTransport(),
        )

        self._tamper = TamperDetector(
            shim_id=self._shim_id,
            sensors=[],
            heartbeat_emit=self._on_heartbeat,
            tamper_emit=self._on_tamper,
            emergency_stop=self._emergency_stop,
            heartbeat_period=config.get("tamper", {}).get("heartbeat_period", 60.0),
        )

        # Serial endpoints
        self._tech_endpoint = SerialEndpoint(
            config["serial"]["technician_side_path"],
            config["serial"].get("baudrate", 9600),
        )
        self._device_endpoint = SerialEndpoint(
            config["serial"]["device_side_path"],
            config["serial"].get("baudrate", 9600),
        )

        # Session
        self._session_id: Optional[str] = None

        # Stop
        self._stop = threading.Event()

    # ────────────── Lifecycle ──────────────

    def run(self):
        log.info("Shim %s starting", self._shim_id)
        self._tech_endpoint.open()
        self._device_endpoint.open()
        self._tamper.start()

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        try:
            self._main_loop()
        finally:
            self._tamper.stop()
            self._tech_endpoint.close()
            self._device_endpoint.close()
            log.info("Shim shutdown complete")

    def _handle_signal(self, signum, frame):
        log.info("signal received: %d", signum)
        self._stop.set()

    def _main_loop(self):
        log.info("Entering IDLE; awaiting technician connection")
        self._send_tech(b"\r\nShim MFA gate. Authenticate as: <technician_id> <totp_code>\r\n> ")
        self._set_state(State.CHALLENGE)

        buffer = bytearray()
        while not self._stop.is_set():
            state = self._get_state()
            if state == State.EMERGENCY_STOP:
                log.error("Emergency stop active; exiting main loop")
                return

            chunk = self._tech_endpoint.read(256)
            if chunk:
                buffer.extend(chunk)
                if state == State.OPEN:
                    # Forward to device, record
                    self._device_endpoint.write(chunk)
                    if self._session_id:
                        self._recorder.append_traffic(self._session_id, Direction.INBOUND, chunk)

                elif state == State.CHALLENGE:
                    if b"\n" in buffer:
                        line, _, rest = buffer.partition(b"\n")
                        buffer = bytearray(rest)
                        self._handle_challenge(line.decode("utf-8", errors="replace").strip())

            # Device → tech (only when OPEN)
            if state == State.OPEN:
                dchunk = self._device_endpoint.read(256)
                if dchunk:
                    self._tech_endpoint.write(dchunk)
                    if self._session_id:
                        self._recorder.append_traffic(self._session_id, Direction.OUTBOUND, dchunk)

            if not chunk:
                time.sleep(0.05)

    # ────────────── Challenge handling ──────────────

    def _handle_challenge(self, line: str):
        parts = line.split()
        if len(parts) < 2:
            self._send_tech(b"\r\nFormat: <technician_id> <totp_code>\r\n> ")
            return

        technician_id, code = parts[0], parts[1]
        outcome = self._gate.authenticate(technician_id, code)

        if outcome.authenticated:
            self._open_session(outcome.technician_id)
        else:
            msg = f"\r\nAuth fail: {outcome.result.value} ({outcome.detail})\r\n> "
            self._send_tech(msg.encode("utf-8"))
            if outcome.result == AuthResult.LOCKED_OUT:
                # Stay in CHALLENGE — operator can retry once lockout expires
                # In production hardware, escalate via SIEM
                pass

    def _open_session(self, technician_id: str):
        try:
            session_id = self._recorder.start_session(technician_id=technician_id)
        except RuntimeError as e:
            log.error("could not open session: %s", e)
            self._send_tech(b"\r\nInternal error opening session\r\n> ")
            return

        self._session_id = session_id
        self._set_state(State.OPEN)
        self._send_tech(
            f"\r\nAuthenticated as {technician_id}; session {session_id}\r\n"
            f"Pass-through enabled. Disconnect to end session.\r\n".encode("utf-8")
        )
        log.info("session opened: technician=%s session_id=%s", technician_id, session_id)

    # ────────────── Tamper / heartbeat callbacks ──────────────

    def _on_heartbeat(self, record):
        # In production this forwards to SIEM. Here we just log.
        log.debug("heartbeat: shim=%s state=%s boot=%d",
                  record.shim_id, record.state, record.boot_count)

    def _on_tamper(self, event: TamperEvent, detail: dict):
        log.error("TAMPER alert: %s detail=%s", event.value, detail)

    def _emergency_stop(self, reason: str):
        log.error("emergency stop triggered: %s", reason)
        if self._session_id:
            try:
                self._recorder.force_close_on_emergency(reason)
            except Exception as e:
                log.error("failed to close session on emergency: %s", e)
            self._session_id = None
        self._set_state(State.EMERGENCY_STOP)
        self._send_tech(f"\r\nEMERGENCY STOP: {reason}\r\n".encode("utf-8"))
        self._stop.set()

    # ────────────── State ──────────────

    def _get_state(self) -> State:
        with self._state_lock:
            return self._state

    def _set_state(self, state: State):
        with self._state_lock:
            previous = self._state
            self._state = state
        if previous != state:
            log.info("state %s → %s", previous.value, state.value)

    def _send_tech(self, data: bytes):
        try:
            self._tech_endpoint.write(data)
        except Exception as e:
            log.warning("tech-side write failed: %s", e)


# ────────────── CLI ──────────────

def main():
    parser = argparse.ArgumentParser(description="Pattern C MFA Shim Daemon")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    with open(args.config) as f:
        config = yaml.safe_load(f)

    daemon = ShimDaemon(config)
    daemon.run()


if __name__ == "__main__":
    main()
