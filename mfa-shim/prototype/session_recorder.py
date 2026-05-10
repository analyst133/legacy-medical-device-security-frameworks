"""
Session recorder — records authenticated service-port sessions to local storage.

Each session produces a single .session file containing:
  - Header (technician id, start time, shim id, configuration snapshot)
  - Inbound and outbound traffic chunks with monotonic ordering and timestamps
  - Footer (end time, byte counts, terminal reason)

The recorder is non-blocking on the data path: traffic chunks are appended
under a short lock and flushed on session close.

SIEM forwarding is implemented as a queue; transport is left abstract so that
deployments can plug in their own destination (TLS syslog, HTTPS POST,
vendor-specific connector). The default transport is no-op.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import enum
import json
import logging
import os
import pathlib
import threading
import time
from typing import Optional, Protocol

log = logging.getLogger("shim.recorder")


class Direction(enum.Enum):
    INBOUND = "in"     # technician → device
    OUTBOUND = "out"   # device → technician
    META = "meta"      # synthetic event (auth, tamper, error)


class SiemTransport(Protocol):
    """Plug-in interface for SIEM forwarding. The default no-op transport
    is sufficient for the prototype. Production deployments substitute an
    actual TLS syslog or HTTPS connector."""
    def forward(self, record: dict) -> bool: ...


class NoopSiemTransport:
    def forward(self, record: dict) -> bool:
        return True


@dataclasses.dataclass
class SessionMeta:
    session_id: str
    technician_id: str
    shim_id: str
    started_at: float                     # epoch
    ended_at: Optional[float] = None
    bytes_inbound: int = 0
    bytes_outbound: int = 0
    terminal_reason: Optional[str] = None


class SessionRecorder:
    """
    Manages one open session at a time. The shim daemon should call:
      recorder.start_session(token, technician_id) → session_id
      recorder.append_traffic(session_id, direction, chunk)
      recorder.end_session(session_id, reason)
    """

    def __init__(
        self,
        storage_root: str,
        shim_id: str,
        siem: Optional[SiemTransport] = None,
    ) -> None:
        self._root = pathlib.Path(storage_root)
        self._sessions_dir = self._root / "sessions"
        self._sessions_dir.mkdir(parents=True, exist_ok=True)

        self._shim_id = shim_id
        self._siem = siem or NoopSiemTransport()

        self._lock = threading.Lock()
        self._open: Optional[SessionMeta] = None
        self._open_handle = None

    # ────────────── Public API ──────────────

    def start_session(self, technician_id: str) -> str:
        """Open a new session. Returns the session_id."""
        with self._lock:
            if self._open is not None:
                raise RuntimeError(f"session {self._open.session_id} already open")

            now = time.time()
            ts_iso = dt.datetime.fromtimestamp(now, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
            session_id = f"{ts_iso}.{self._shim_id}.{technician_id}"
            path = self._sessions_dir / f"{session_id}.session"

            handle = open(path, "ab", buffering=0)
            meta = SessionMeta(
                session_id=session_id,
                technician_id=technician_id,
                shim_id=self._shim_id,
                started_at=now,
            )

            header = {
                "type": "session_header",
                "session_id": session_id,
                "technician_id": technician_id,
                "shim_id": self._shim_id,
                "started_at_epoch": now,
                "started_at_iso": dt.datetime.fromtimestamp(now, tz=dt.timezone.utc).isoformat(),
                "version": "1.0",
            }
            handle.write((json.dumps(header) + "\n").encode("utf-8"))

            self._open = meta
            self._open_handle = handle

            self._siem.forward({"event": "session_start", **header})
            log.info("session started: %s", session_id)
            return session_id

    def append_traffic(
        self,
        session_id: str,
        direction: Direction,
        chunk: bytes,
    ) -> None:
        """Append bidirectional traffic. Non-blocking on the data path."""
        with self._lock:
            if self._open is None or self._open.session_id != session_id:
                raise RuntimeError(f"session {session_id} is not open")
            record = {
                "type": "traffic",
                "direction": direction.value,
                "len": len(chunk),
                "monotonic": time.monotonic(),
                "epoch": time.time(),
                # Hex preserves binary data without expensive base64 in the data path.
                "data_hex": chunk.hex(),
            }
            self._open_handle.write((json.dumps(record) + "\n").encode("utf-8"))

            if direction == Direction.INBOUND:
                self._open.bytes_inbound += len(chunk)
            elif direction == Direction.OUTBOUND:
                self._open.bytes_outbound += len(chunk)

    def append_event(self, session_id: str, event: dict) -> None:
        """Append a synthetic meta-event (e.g., auth, tamper alert)."""
        with self._lock:
            if self._open is None or self._open.session_id != session_id:
                raise RuntimeError(f"session {session_id} is not open")
            record = {
                "type": "meta",
                "epoch": time.time(),
                **event,
            }
            self._open_handle.write((json.dumps(record) + "\n").encode("utf-8"))
            self._siem.forward({"session_id": session_id, **record})

    def end_session(self, session_id: str, reason: str) -> SessionMeta:
        """Close the session, flush, and forward the summary to SIEM."""
        with self._lock:
            if self._open is None or self._open.session_id != session_id:
                raise RuntimeError(f"session {session_id} is not open")

            now = time.time()
            self._open.ended_at = now
            self._open.terminal_reason = reason

            footer = {
                "type": "session_footer",
                "ended_at_epoch": now,
                "ended_at_iso": dt.datetime.fromtimestamp(now, tz=dt.timezone.utc).isoformat(),
                "duration_seconds": now - self._open.started_at,
                "bytes_inbound": self._open.bytes_inbound,
                "bytes_outbound": self._open.bytes_outbound,
                "terminal_reason": reason,
            }
            self._open_handle.write((json.dumps(footer) + "\n").encode("utf-8"))
            self._open_handle.close()

            meta = self._open
            self._open = None
            self._open_handle = None

            self._siem.forward({
                "event": "session_end",
                "session_id": session_id,
                "technician_id": meta.technician_id,
                "shim_id": meta.shim_id,
                "duration_seconds": footer["duration_seconds"],
                "bytes_inbound": meta.bytes_inbound,
                "bytes_outbound": meta.bytes_outbound,
                "terminal_reason": reason,
            })
            log.info("session ended: %s reason=%s in=%d out=%d",
                     session_id, reason, meta.bytes_inbound, meta.bytes_outbound)
            return meta

    @property
    def has_open_session(self) -> bool:
        with self._lock:
            return self._open is not None

    def force_close_on_emergency(self, reason: str) -> Optional[SessionMeta]:
        """Used by tamper detector to force-close the current session."""
        with self._lock:
            if self._open is None:
                return None
            session_id = self._open.session_id
        return self.end_session(session_id, reason)
