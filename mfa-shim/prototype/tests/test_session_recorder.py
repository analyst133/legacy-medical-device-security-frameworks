"""
Unit tests for the session recorder.
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from session_recorder import SessionRecorder, NoopSiemTransport, Direction


class FakeSiem:
    def __init__(self):
        self.records = []

    def forward(self, record):
        self.records.append(record)
        return True


@pytest.fixture
def recorder_with_siem():
    with tempfile.TemporaryDirectory() as tmp:
        siem = FakeSiem()
        rec = SessionRecorder(storage_root=tmp, shim_id="test-shim-001", siem=siem)
        try:
            yield rec, siem, tmp
        finally:
            if rec.has_open_session:
                rec.force_close_on_emergency("test_teardown")


def test_start_and_end_session(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem

    session_id = rec.start_session(technician_id="alice")
    assert session_id is not None
    assert "alice" in session_id
    assert rec.has_open_session

    meta = rec.end_session(session_id, reason="technician_disconnect")

    assert not rec.has_open_session
    assert meta.terminal_reason == "technician_disconnect"
    assert meta.ended_at is not None and meta.ended_at >= meta.started_at


def test_session_file_contains_header_and_footer(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem

    session_id = rec.start_session(technician_id="bob")
    rec.end_session(session_id, reason="done")

    session_files = list((rec._sessions_dir).glob("*.session"))
    assert len(session_files) == 1
    lines = session_files[0].read_text().splitlines()
    assert len(lines) >= 2

    header = json.loads(lines[0])
    footer = json.loads(lines[-1])

    assert header["type"] == "session_header"
    assert header["technician_id"] == "bob"

    assert footer["type"] == "session_footer"
    assert footer["terminal_reason"] == "done"


def test_traffic_appended_with_correct_direction(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem

    session_id = rec.start_session(technician_id="carol")
    rec.append_traffic(session_id, Direction.INBOUND, b"hello-pump")
    rec.append_traffic(session_id, Direction.OUTBOUND, b"hello-tech")
    meta = rec.end_session(session_id, reason="done")

    assert meta.bytes_inbound == len(b"hello-pump")
    assert meta.bytes_outbound == len(b"hello-tech")

    session_file = list((rec._sessions_dir).glob("*.session"))[0]
    lines = [json.loads(l) for l in session_file.read_text().splitlines()]
    traffic = [l for l in lines if l.get("type") == "traffic"]
    assert len(traffic) == 2
    assert traffic[0]["direction"] == "in"
    assert bytes.fromhex(traffic[0]["data_hex"]) == b"hello-pump"
    assert traffic[1]["direction"] == "out"
    assert bytes.fromhex(traffic[1]["data_hex"]) == b"hello-tech"


def test_cannot_open_two_sessions(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem

    rec.start_session(technician_id="alice")
    with pytest.raises(RuntimeError):
        rec.start_session(technician_id="bob")


def test_cannot_append_to_unknown_session(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem

    session_id = rec.start_session(technician_id="alice")
    with pytest.raises(RuntimeError):
        rec.append_traffic("not-a-session", Direction.INBOUND, b"x")
    rec.end_session(session_id, reason="done")


def test_force_close_on_emergency(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem

    rec.start_session(technician_id="alice")
    assert rec.has_open_session

    meta = rec.force_close_on_emergency("tamper:case_opened")
    assert meta is not None
    assert meta.terminal_reason == "tamper:case_opened"
    assert not rec.has_open_session


def test_force_close_when_no_session_returns_none(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem
    assert rec.force_close_on_emergency("anything") is None


def test_siem_records_session_lifecycle(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem

    session_id = rec.start_session(technician_id="alice")
    rec.append_event(session_id, {"event": "auth_success", "factor": "totp"})
    rec.end_session(session_id, reason="done")

    events = [r.get("event") for r in siem.records]
    assert "session_start" in events
    assert "auth_success" in events
    assert "session_end" in events


def test_append_event_outside_session_raises(recorder_with_siem):
    rec, siem, tmp = recorder_with_siem
    with pytest.raises(RuntimeError):
        rec.append_event("nope", {"event": "x"})


def test_default_noop_siem_does_not_raise():
    with tempfile.TemporaryDirectory() as tmp:
        rec = SessionRecorder(storage_root=tmp, shim_id="x")
        sid = rec.start_session(technician_id="alice")
        rec.append_traffic(sid, Direction.INBOUND, b"data")
        rec.end_session(sid, reason="done")
