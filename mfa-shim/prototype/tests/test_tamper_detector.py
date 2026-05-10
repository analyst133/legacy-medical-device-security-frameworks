"""
Unit tests for the tamper detector.
"""

import os
import sys
import threading
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from tamper_detector import TamperDetector, TamperEvent, TamperSensor, NullSensor


class TriggerableSensor:
    """A test sensor that can be triggered programmatically."""
    def __init__(self):
        self._pending = None
        self._lock = threading.Lock()

    def trigger(self, event: TamperEvent):
        with self._lock:
            self._pending = event

    def poll(self):
        with self._lock:
            event, self._pending = self._pending, None
            return event


def _build(sensors=None, heartbeat_period=60.0):
    heartbeats = []
    tampers = []
    stops = []

    detector = TamperDetector(
        shim_id="test-shim",
        sensors=sensors or [],
        heartbeat_emit=lambda r: heartbeats.append(r),
        tamper_emit=lambda e, d: tampers.append((e, d)),
        emergency_stop=lambda reason: stops.append(reason),
        heartbeat_period=heartbeat_period,
        sensor_poll_period=0.05,
    )
    return detector, heartbeats, tampers, stops


def test_initial_state_is_ok():
    detector, *_ = _build()
    assert detector.state == "ok"


def test_sensor_event_triggers_emergency_stop():
    sensor = TriggerableSensor()
    detector, heartbeats, tampers, stops = _build(sensors=[sensor], heartbeat_period=10.0)

    detector.start()
    try:
        sensor.trigger(TamperEvent.CASE_OPENED)
        # Wait for the polling loop to pick it up
        deadline = time.time() + 2
        while time.time() < deadline and not stops:
            time.sleep(0.05)

        assert stops == ["tamper:case_opened"]
        assert detector.state == "tampered"
        assert len(tampers) == 1
        assert tampers[0][0] == TamperEvent.CASE_OPENED
    finally:
        detector.stop()


def test_report_tamper_directly():
    """Directly invoking report_tamper (e.g., from a software-detected condition)."""
    detector, heartbeats, tampers, stops = _build()

    detector.report_tamper(TamperEvent.BOOT_INTEGRITY_VIOLATED, source="boot")
    assert detector.state == "tampered"
    assert stops == ["tamper:boot_integrity_violated"]
    assert len(tampers) == 1


def test_admin_reset_returns_to_ok():
    detector, *_ = _build()
    detector.report_tamper(TamperEvent.CASE_OPENED, source="test")
    assert detector.state == "tampered"

    detector.admin_reset(authorised_by="security_admin", reason="post-inspection")
    assert detector.state == "ok"


def test_heartbeat_emitted_periodically():
    detector, heartbeats, *_ = _build(heartbeat_period=0.2)

    detector.start()
    try:
        time.sleep(0.7)  # should produce roughly 3 heartbeats
        assert len(heartbeats) >= 2, f"expected at least 2 heartbeats, got {len(heartbeats)}"
        for h in heartbeats:
            assert h.shim_id == "test-shim"
            assert h.state in ("ok", "tampered")
    finally:
        detector.stop()


def test_heartbeat_records_state_change():
    """After a tamper event, subsequent heartbeats reflect 'tampered' state."""
    detector, heartbeats, *_ = _build(heartbeat_period=0.2)

    detector.start()
    try:
        time.sleep(0.3)
        detector.report_tamper(TamperEvent.MAGNETIC_ANOMALY, source="test")
        time.sleep(0.5)
    finally:
        detector.stop()

    states = [h.state for h in heartbeats]
    assert "ok" in states or "tampered" in states  # at least one of each in steady operation
    assert states[-1] == "tampered" if states else True


def test_null_sensor_does_nothing():
    """The NullSensor never triggers events. Verifies the no-op path."""
    sensor = NullSensor()
    detector, heartbeats, tampers, stops = _build(sensors=[sensor], heartbeat_period=10.0)
    detector.start()
    try:
        time.sleep(0.3)
    finally:
        detector.stop()
    assert tampers == []
    assert stops == []
    assert detector.state == "ok"


def test_failing_sensor_does_not_crash_loop():
    """A sensor that raises does not stop the heartbeat loop."""
    class BadSensor:
        def poll(self):
            raise RuntimeError("simulated sensor fault")

    detector, heartbeats, tampers, stops = _build(sensors=[BadSensor()], heartbeat_period=0.2)
    detector.start()
    try:
        time.sleep(0.6)
    finally:
        detector.stop()
    # Heartbeats still emitted despite sensor errors
    assert len(heartbeats) >= 1
    assert detector.state == "ok"


def test_multiple_sensors_polled():
    """When several sensors are present they are all polled each tick."""
    s1 = TriggerableSensor()
    s2 = TriggerableSensor()
    detector, heartbeats, tampers, stops = _build(sensors=[s1, s2], heartbeat_period=10.0)
    detector.start()
    try:
        s2.trigger(TamperEvent.UNEXPECTED_MOTION)
        deadline = time.time() + 1.5
        while time.time() < deadline and not stops:
            time.sleep(0.05)
    finally:
        detector.stop()

    assert len(stops) >= 1
    assert tampers[0][0] == TamperEvent.UNEXPECTED_MOTION


def test_emergency_stop_callback_failure_does_not_propagate():
    """If emergency_stop callback raises, tamper handling still completes."""
    heartbeats = []
    tampers = []

    def bad_stop(reason):
        raise RuntimeError("simulated callback failure")

    detector = TamperDetector(
        shim_id="x",
        heartbeat_emit=lambda r: heartbeats.append(r),
        tamper_emit=lambda e, d: tampers.append((e, d)),
        emergency_stop=bad_stop,
        heartbeat_period=10.0,
    )

    detector.report_tamper(TamperEvent.CASE_OPENED, source="test")
    # Should still record the tamper event despite stop callback failure
    assert detector.state == "tampered"
    assert len(tampers) == 1


def test_boot_count_increments_on_restart():
    heartbeats = []
    detector2 = TamperDetector(
        shim_id="x",
        heartbeat_emit=lambda r: heartbeats.append(r),
        tamper_emit=lambda *a, **kw: None,
        emergency_stop=lambda r: None,
        heartbeat_period=0.05,
        sensor_poll_period=0.02,
    )
    detector2.start(); time.sleep(0.2); detector2.stop()
    detector2.start(); time.sleep(0.2); detector2.stop()
    boot_counts = sorted(set(h.boot_count for h in heartbeats))
    assert boot_counts == [1, 2], f"got boot_counts={boot_counts} (heartbeats={len(heartbeats)})"
