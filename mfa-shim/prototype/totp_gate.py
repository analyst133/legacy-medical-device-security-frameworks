"""
TOTP gate — RFC 6238 Time-Based One-Time Password authentication for the shim.

Wraps pyotp with shim-specific concerns:
  - Replay protection within a TOTP period
  - Window tolerance (default ±1 step / 60 seconds total)
  - Per-user lockout after repeated failures
  - Attempt audit (always logged regardless of outcome)

Designed to be unit-testable without serial hardware. See tests/test_totp_gate.py.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
import time
from typing import Mapping, Optional

import pyotp

log = logging.getLogger("shim.totp")


class AuthResult(enum.Enum):
    OK = "OK"
    BAD_USER = "BAD_USER"
    BAD_CODE = "BAD_CODE"
    REPLAY = "REPLAY"
    LOCKED_OUT = "LOCKED_OUT"


@dataclasses.dataclass
class AuthOutcome:
    result: AuthResult
    technician_id: Optional[str] = None
    period: Optional[int] = None
    detail: str = ""

    @property
    def authenticated(self) -> bool:
        return self.result == AuthResult.OK


@dataclasses.dataclass
class TechnicianRecord:
    technician_id: str
    totp_secret: str           # base32-encoded TOTP secret (RFC 6238)
    enrolment_date: str = ""   # ISO 8601 date
    notes: str = ""


class TotpGate:
    """
    Authentication gate for shim service-port access.

    The gate is stateful for replay protection and lockout tracking, and is
    deliberately thread-safe so that the shim daemon can call into it from
    its serial-handling thread.
    """

    def __init__(
        self,
        users: Mapping[str, TechnicianRecord],
        *,
        period: int = 30,
        digits: int = 6,
        window: int = 1,                    # ±1 step tolerance
        max_failures: int = 5,
        lockout_seconds: int = 300,
        time_source=time.time,
    ) -> None:
        self._users = dict(users)
        self._period = period
        self._digits = digits
        self._window = window
        self._max_failures = max_failures
        self._lockout_seconds = lockout_seconds
        self._time = time_source

        # State: replay cache and failure tracking
        self._lock = threading.Lock()
        self._used_codes: dict[tuple[str, int], None] = {}
        self._failure_counts: dict[str, list[float]] = {}
        self._lockouts: dict[str, float] = {}

    # ────────────── Public API ──────────────

    def authenticate(self, technician_id: str, code: str) -> AuthOutcome:
        """
        Verify a TOTP code for a technician.

        Returns an AuthOutcome that is .authenticated only on success.
        Always emits a structured audit log line regardless of outcome.
        """
        now = self._time()
        with self._lock:
            # 1. Lockout check
            locked_until = self._lockouts.get(technician_id, 0.0)
            if locked_until > now:
                outcome = AuthOutcome(
                    result=AuthResult.LOCKED_OUT,
                    technician_id=technician_id,
                    detail=f"locked_out for {int(locked_until - now)}s more",
                )
                log.warning("auth lockout: user=%s remaining=%ds", technician_id, int(locked_until - now))
                return outcome

            # 2. User check
            user = self._users.get(technician_id)
            if user is None:
                self._record_failure(technician_id, now)
                outcome = AuthOutcome(
                    result=AuthResult.BAD_USER,
                    technician_id=technician_id,
                    detail="unknown technician",
                )
                log.warning("auth fail BAD_USER: user=%s", technician_id)
                return outcome

            # 3. TOTP verification with window tolerance
            totp = pyotp.TOTP(user.totp_secret, digits=self._digits, interval=self._period)

            current_period = int(now // self._period)
            matched_period: Optional[int] = None

            for offset in range(-self._window, self._window + 1):
                candidate_t = now + (offset * self._period)
                if totp.at(int(candidate_t)) == code:
                    matched_period = current_period + offset
                    break

            if matched_period is None:
                self._record_failure(technician_id, now)
                outcome = AuthOutcome(
                    result=AuthResult.BAD_CODE,
                    technician_id=technician_id,
                    period=current_period,
                    detail="code does not verify within window",
                )
                log.warning("auth fail BAD_CODE: user=%s period=%d", technician_id, current_period)
                return outcome

            # 4. Replay protection
            replay_key = (technician_id, matched_period)
            if replay_key in self._used_codes:
                outcome = AuthOutcome(
                    result=AuthResult.REPLAY,
                    technician_id=technician_id,
                    period=matched_period,
                    detail="code already used in this period",
                )
                log.warning("auth fail REPLAY: user=%s period=%d", technician_id, matched_period)
                return outcome

            # 5. Success
            self._used_codes[replay_key] = None
            self._failure_counts.pop(technician_id, None)
            self._lockouts.pop(technician_id, None)
            self._garbage_collect(now)

            outcome = AuthOutcome(
                result=AuthResult.OK,
                technician_id=technician_id,
                period=matched_period,
                detail="authenticated",
            )
            log.info("auth ok: user=%s period=%d", technician_id, matched_period)
            return outcome

    def is_locked_out(self, technician_id: str) -> bool:
        with self._lock:
            return self._lockouts.get(technician_id, 0.0) > self._time()

    def reset_user(self, technician_id: str) -> None:
        """Admin reset for a locked-out user."""
        with self._lock:
            self._failure_counts.pop(technician_id, None)
            self._lockouts.pop(technician_id, None)
            log.info("admin reset: user=%s", technician_id)

    # ────────────── Internal ──────────────

    def _record_failure(self, technician_id: str, now: float) -> None:
        # Caller must hold lock
        bucket = self._failure_counts.setdefault(technician_id, [])
        bucket.append(now)
        # Keep only failures within rolling window equal to lockout_seconds
        cutoff = now - self._lockout_seconds
        bucket[:] = [t for t in bucket if t > cutoff]
        if len(bucket) >= self._max_failures:
            self._lockouts[technician_id] = now + self._lockout_seconds
            log.warning(
                "user locked out: user=%s failures=%d window=%ds",
                technician_id, len(bucket), self._lockout_seconds,
            )

    def _garbage_collect(self, now: float) -> None:
        # Caller must hold lock. Drop replay-cache entries older than 2 windows.
        cutoff_period = int(now // self._period) - 2 * self._window - 1
        stale = [k for k in self._used_codes if k[1] < cutoff_period]
        for k in stale:
            del self._used_codes[k]


# ────────────── Convenience helpers ──────────────

def generate_totp_secret() -> str:
    """Generate a fresh base32 TOTP secret for technician enrolment."""
    return pyotp.random_base32()


def provisioning_uri(technician_id: str, secret: str, issuer: str = "ShimMFA") -> str:
    """
    Return an otpauth:// URI suitable for QR-code enrolment in any standard
    TOTP authenticator app (Duo, Google Authenticator, Microsoft Authenticator,
    Authy, etc.).
    """
    return pyotp.TOTP(secret).provisioning_uri(name=technician_id, issuer_name=issuer)
