"""
Tamper detector — heartbeat emitter and tamper-event reporter.

In production hardware, this module integrates with case-open switches,
magnetic-field sensors, and accelerometers. In the prototype, hardware sensors
are emulated through the TamperSensor protocol so that test code can inject
events deterministically.

Heartbeats are emitted at a configurable interval. Missed heartbeats at the
central monitoring system signal a possibly-tampered shim. Local sensor events
trigger an immediate tamper alert.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
import time
from typing import Callable, Optional, Protocol

log = logging.getLogger("shim.tamper")


class TamperEvent(enum.Enum):
    CASE_OPENED = "case_opened"
    MAGNETIC_ANOMALY = "magnetic_anomaly"
    UNEXPECTED_MOTION = "unexpected_motion"
    BOOT_INTEGRITY_VIOLATED = "boot_integrity_violated"
    HEARTBEAT_MISSED = "heartbeat_missed"   # central-side detection; included here for completeness


class TamperSensor(Protocol):
    """A pluggable interface to physical tamper-detection hardware."""
    def poll(self) -> Optional[TamperEvent]: ...


class NullSensor:
    """Default sensor that never fires — for development and tests where
    sensor events are injected by other means."""
    def poll(self) -> Optional[TamperEvent]:
        return None


@dataclasses.dataclass
class HeartbeatRecord:
    shim_id: str
    monotonic: float
    epoch: float
    state: str
    boot_count: int


class TamperDetector:
    """
    Periodic heartbeat emitter and tamper-event coordinator.

    The detector runs a background thread that polls sensors and emits
    heartbeats. On a tamper event, it invokes the configured emergency_stop
    callback synchronously so the shim daemon can immediately terminate any
    active session.
    """

    def __init__(
        self,
        shim_id: str,
        *,
        sensors: Optional[list[TamperSensor]] = None,
        heartbeat_emit: Callable[[HeartbeatRecord], None],
        tamper_emit: Callable[[TamperEvent, dict], None],
        emergency_stop: Callable[[str], None],
        heartbeat_period: float = 60.0,
        sensor_poll_period: float = 1.0,
        time_source=time.time,
        monotonic_source=time.monotonic,
    ) -> None:
        self._shim_id = shim_id
        self._sensors = list(sensors or [])
        self._heartbeat_emit = heartbeat_emit
        self._tamper_emit = tamper_emit
        self._emergency_stop = emergency_stop
        self._heartbeat_period = heartbeat_period
        self._sensor_poll_period = sensor_poll_period
        self._time = time_source
        self._monotonic = monotonic_source

        self._state = "ok"
        self._boot_count = 0
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    # ────────────── Lifecycle ──────────────

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._boot_count += 1
        self._stop_event.clear()
        self._state = "ok"
        self._thread = threading.Thread(target=self._run, name="shim-tamper", daemon=True)
        self._thread.start()
        log.info("tamper detector started (boot=%d)", self._boot_count)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._thread = None
        log.info("tamper detector stopped")

    # ────────────── Background loop ──────────────

    def _run(self) -> None:
        last_heartbeat = self._monotonic()
        while not self._stop_event.is_set():
            # Sensor poll
            for sensor in self._sensors:
                try:
                    event = sensor.poll()
                except Exception as e:
                    log.warning("sensor error: %s", e)
                    continue
                if event is not None:
                    self.report_tamper(event, source="sensor")

            # Heartbeat
            now = self._monotonic()
            if now - last_heartbeat >= self._heartbeat_period:
                self._emit_heartbeat()
                last_heartbeat = now

            # Wait for next poll
            self._stop_event.wait(self._sensor_poll_period)

    def _emit_heartbeat(self) -> None:
        with self._lock:
            record = HeartbeatRecord(
                shim_id=self._shim_id,
                monotonic=self._monotonic(),
                epoch=self._time(),
                state=self._state,
                boot_count=self._boot_count,
            )
        try:
            self._heartbeat_emit(record)
        except Exception as e:
            log.warning("heartbeat emission error: %s", e)

    # ────────────── Tamper handling ──────────────

    def report_tamper(self, event: TamperEvent, *, source: str = "unknown", **detail) -> None:
        """
        Synchronously handle a tamper event.

        Always:
          1. Records the event.
          2. Invokes emergency_stop, which terminates any active session.
          3. Forwards the event for SIEM.
        Subsequent operation is degraded: sessions cannot be opened until the
        shim is reset by an authorised operator.
        """
        with self._lock:
            previous_state = self._state
            self._state = "tampered"

        log.error("TAMPER: event=%s source=%s state=%s→tampered",
                  event.value, source, previous_state)

        try:
            self._emergency_stop(f"tamper:{event.value}")
        except Exception as e:
            log.error("emergency_stop callback failed: %s", e)

        try:
            self._tamper_emit(event, {
                "shim_id": self._shim_id,
                "source": source,
                "epoch": self._time(),
                "previous_state": previous_state,
                **detail,
            })
        except Exception as e:
            log.error("tamper_emit callback failed: %s", e)

    # ────────────── Reset ──────────────

    def admin_reset(self, *, authorised_by: str, reason: str) -> None:
        """
        Manually reset state from 'tampered' back to 'ok' after physical
        inspection. In production hardware this is gated by a key-based switch
        or attestation; in the prototype it is a programmatic operation
        recorded in the audit log.
        """
        with self._lock:
            previous_state = self._state
            self._state = "ok"
        log.info("admin reset: by=%s reason=%s previous=%s", authorised_by, reason, previous_state)

    @property
    def state(self) -> str:
        with self._lock:
            return self._state
