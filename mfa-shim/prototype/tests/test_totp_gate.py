"""
Unit tests for the TOTP gate.

Tests use a controllable time source so that we can drive the gate's
windowing, replay protection, and lockout behaviour deterministically.
"""

import sys
import os
import time
import threading
import pytest
import pyotp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from totp_gate import (
    TotpGate, TechnicianRecord, AuthResult,
    generate_totp_secret, provisioning_uri,
)


class FakeClock:
    def __init__(self, now=1_700_000_000.0):
        self._now = now
        self._lock = threading.Lock()

    def __call__(self) -> float:
        with self._lock:
            return self._now

    def advance(self, seconds: float):
        with self._lock:
            self._now += seconds


def make_users(count=2):
    return {
        f"user{i}": TechnicianRecord(
            technician_id=f"user{i}",
            totp_secret=pyotp.random_base32(),
        )
        for i in range(count)
    }


def code_for(record: TechnicianRecord, when: float) -> str:
    return pyotp.TOTP(record.totp_secret).at(int(when))


# ────────────── Basic success / failure ──────────────

def test_authenticate_with_valid_code():
    clock = FakeClock()
    users = make_users(2)
    gate = TotpGate(users, time_source=clock)

    user = users["user0"]
    code = code_for(user, clock())

    outcome = gate.authenticate("user0", code)
    assert outcome.authenticated
    assert outcome.result == AuthResult.OK
    assert outcome.technician_id == "user0"


def test_authenticate_unknown_user():
    clock = FakeClock()
    gate = TotpGate(make_users(2), time_source=clock)

    outcome = gate.authenticate("ghost", "123456")
    assert not outcome.authenticated
    assert outcome.result == AuthResult.BAD_USER


def test_authenticate_bad_code():
    clock = FakeClock()
    users = make_users(2)
    gate = TotpGate(users, time_source=clock)

    outcome = gate.authenticate("user0", "000000")
    assert not outcome.authenticated
    assert outcome.result == AuthResult.BAD_CODE


# ────────────── Window tolerance ──────────────

def test_window_tolerance_minus_one_step():
    """Code generated 30 seconds ago is accepted with window=1."""
    clock = FakeClock(now=1_700_000_000.0)
    users = make_users(1)
    gate = TotpGate(users, window=1, time_source=clock)

    user = users["user0"]
    # Code valid for 30 seconds in the past
    past_code = code_for(user, clock() - 30)

    outcome = gate.authenticate("user0", past_code)
    assert outcome.authenticated, f"expected accept; got {outcome.result.value}: {outcome.detail}"


def test_window_tolerance_plus_one_step():
    """Code generated 30 seconds in the future is accepted (clock skew tolerance)."""
    clock = FakeClock(now=1_700_000_000.0)
    users = make_users(1)
    gate = TotpGate(users, window=1, time_source=clock)

    user = users["user0"]
    future_code = code_for(user, clock() + 30)

    outcome = gate.authenticate("user0", future_code)
    assert outcome.authenticated


def test_window_tolerance_two_steps_rejected():
    """Code from 60 seconds ago is rejected with window=1."""
    clock = FakeClock(now=1_700_000_000.0)
    users = make_users(1)
    gate = TotpGate(users, window=1, time_source=clock)

    user = users["user0"]
    too_old_code = code_for(user, clock() - 60)

    outcome = gate.authenticate("user0", too_old_code)
    assert not outcome.authenticated
    assert outcome.result == AuthResult.BAD_CODE


# ────────────── Replay protection ──────────────

def test_replay_in_same_period_rejected():
    """Reusing a valid code within the same TOTP period is rejected."""
    clock = FakeClock()
    users = make_users(1)
    gate = TotpGate(users, time_source=clock)

    user = users["user0"]
    code = code_for(user, clock())

    first = gate.authenticate("user0", code)
    second = gate.authenticate("user0", code)

    assert first.authenticated
    assert not second.authenticated
    assert second.result == AuthResult.REPLAY


def test_no_replay_after_period_advances():
    """Different code in a new period is accepted."""
    clock = FakeClock()
    users = make_users(1)
    gate = TotpGate(users, time_source=clock)

    user = users["user0"]
    code1 = code_for(user, clock())
    first = gate.authenticate("user0", code1)
    assert first.authenticated

    # Advance two periods
    clock.advance(60)

    code2 = code_for(user, clock())
    second = gate.authenticate("user0", code2)
    assert second.authenticated, f"got {second.result.value}: {second.detail}"


# ────────────── Lockout ──────────────

def test_lockout_after_repeated_failures():
    clock = FakeClock()
    users = make_users(1)
    gate = TotpGate(users, max_failures=3, lockout_seconds=300, time_source=clock)

    # 3 bad attempts
    for _ in range(3):
        outcome = gate.authenticate("user0", "000000")
        assert outcome.result == AuthResult.BAD_CODE

    # 4th attempt is locked out
    outcome = gate.authenticate("user0", "000000")
    assert outcome.result == AuthResult.LOCKED_OUT
    assert gate.is_locked_out("user0")


def test_lockout_blocks_valid_code():
    """A valid code presented during a lockout is also rejected."""
    clock = FakeClock()
    users = make_users(1)
    gate = TotpGate(users, max_failures=3, lockout_seconds=300, time_source=clock)

    # Trigger lockout
    for _ in range(3):
        gate.authenticate("user0", "000000")

    user = users["user0"]
    valid = code_for(user, clock())
    outcome = gate.authenticate("user0", valid)
    assert outcome.result == AuthResult.LOCKED_OUT


def test_lockout_expires():
    """After lockout_seconds elapses, authentication is permitted again."""
    clock = FakeClock()
    users = make_users(1)
    gate = TotpGate(users, max_failures=3, lockout_seconds=300, time_source=clock)

    for _ in range(3):
        gate.authenticate("user0", "000000")

    assert gate.is_locked_out("user0")

    clock.advance(301)
    assert not gate.is_locked_out("user0")

    user = users["user0"]
    code = code_for(user, clock())
    outcome = gate.authenticate("user0", code)
    assert outcome.authenticated


def test_admin_reset_clears_lockout():
    clock = FakeClock()
    users = make_users(1)
    gate = TotpGate(users, max_failures=3, lockout_seconds=300, time_source=clock)

    for _ in range(3):
        gate.authenticate("user0", "000000")

    assert gate.is_locked_out("user0")
    gate.reset_user("user0")
    assert not gate.is_locked_out("user0")


# ────────────── Lockout independence ──────────────

def test_lockout_does_not_affect_other_users():
    """One user's lockout does not affect a different user."""
    clock = FakeClock()
    users = make_users(2)
    gate = TotpGate(users, max_failures=3, lockout_seconds=300, time_source=clock)

    for _ in range(3):
        gate.authenticate("user0", "000000")
    assert gate.is_locked_out("user0")

    # user1 still authenticates fine
    user1_code = code_for(users["user1"], clock())
    outcome = gate.authenticate("user1", user1_code)
    assert outcome.authenticated, f"got {outcome.result.value}"


# ────────────── Helpers ──────────────

def test_generate_totp_secret_is_valid_base32():
    secret = generate_totp_secret()
    # base32 secret must work with pyotp without raising
    totp = pyotp.TOTP(secret)
    code = totp.now()
    assert len(code) == 6
    assert code.isdigit()


def test_provisioning_uri_format():
    secret = generate_totp_secret()
    uri = provisioning_uri("alice@example.org", secret, issuer="ShimMFA")
    assert uri.startswith("otpauth://totp/")
    assert "alice%40example.org" in uri or "alice@example.org" in uri
    assert "secret=" in uri
    assert "ShimMFA" in uri


# ────────────── Concurrency smoke test ──────────────

def test_concurrent_authenticate_thread_safe():
    """Many threads hitting authenticate concurrently must not corrupt state."""
    clock = FakeClock()
    users = make_users(10)
    gate = TotpGate(users, time_source=clock)

    successes = []
    failures = []

    def worker(uid):
        user = users[uid]
        code = code_for(user, clock())
        outcome = gate.authenticate(uid, code)
        (successes if outcome.authenticated else failures).append(uid)

    threads = [threading.Thread(target=worker, args=(f"user{i}",)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All 10 distinct users should authenticate successfully
    assert len(successes) == 10, f"successes={successes} failures={failures}"
