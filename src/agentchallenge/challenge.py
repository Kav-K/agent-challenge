"""Core challenge creation and verification logic."""

import hashlib
import hmac
import json
import base64
import time
import secrets
import re
from dataclasses import dataclass, field
from typing import Optional

from .types import CHALLENGE_TYPES, generate_challenge


@dataclass
class Challenge:
    """A generated challenge to send to an agent."""
    id: str
    prompt: str
    token: str
    expires_at: float
    challenge_type: str

    @property
    def expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> dict:
        """Serialize for JSON API responses."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "token": self.token,
            "expires_in": max(0, int(self.expires_at - time.time())),
            "type": "reasoning",  # Don't leak internal type
        }


@dataclass
class VerifyResult:
    """Result of verifying an agent's answer."""
    valid: bool
    error: Optional[str] = None
    challenge_type: Optional[str] = None
    elapsed_ms: Optional[int] = None


class AgentChallenge:
    """
    LLM-solvable challenge-response system.

    Challenges are puzzles that any LLM can solve through reasoning alone.
    No scripts, no computational power, no external tools needed.

    The system is fully stateless — challenge data is signed into tokens
    using HMAC, so no database is required.

    Args:
        secret: Server secret key for signing tokens (min 16 chars recommended).
        difficulty: "easy", "medium", or "hard". Controls which challenge types are used.
        ttl: Challenge time-to-live in seconds (default 300 = 5 minutes).
        types: Optional list of challenge type names to use. If None, uses difficulty-based selection.
    """

    def __init__(
        self,
        secret: str,
        difficulty: str = "easy",
        ttl: int = 300,
        types: Optional[list] = None,
    ):
        if not secret or len(secret) < 8:
            raise ValueError("Secret must be at least 8 characters")
        self._secret = secret.encode("utf-8") if isinstance(secret, str) else secret
        self._difficulty = difficulty
        self._ttl = ttl
        self._allowed_types = types

    def create(self, challenge_type: Optional[str] = None) -> Challenge:
        """
        Create a new challenge.

        Args:
            challenge_type: Optional specific challenge type. If None, randomly selected.

        Returns:
            Challenge object with prompt, token, and metadata.
        """
        # Generate the challenge
        ctype, prompt, answer = generate_challenge(
            difficulty=self._difficulty,
            specific_type=challenge_type,
            allowed_types=self._allowed_types,
        )

        # Create token payload
        challenge_id = "ch_" + secrets.token_hex(12)
        now = time.time()
        payload = {
            "id": challenge_id,
            "type": ctype,
            "answer_hash": _hash_answer(answer),
            "created_at": int(now),
            "expires_at": int(now + self._ttl),
        }

        # Sign it
        token = _encode_token(payload, self._secret)

        return Challenge(
            id=challenge_id,
            prompt=prompt,
            token=token,
            expires_at=now + self._ttl,
            challenge_type=ctype,
        )

    def verify(self, token: str, answer: str) -> VerifyResult:
        """
        Verify an agent's answer against a challenge token.

        Args:
            token: The challenge token (from challenge.token).
            answer: The agent's answer string.

        Returns:
            VerifyResult with valid=True if correct.
        """
        start = time.time()

        # Decode and verify token signature
        try:
            payload = _decode_token(token, self._secret)
        except TokenError as e:
            return VerifyResult(valid=False, error=str(e))

        # Check expiry
        if time.time() > payload.get("expires_at", 0):
            return VerifyResult(valid=False, error="Challenge expired")

        # Normalize and verify answer
        normalized = _normalize_answer(answer)
        if not normalized:
            return VerifyResult(valid=False, error="Empty answer")

        expected_hash = payload.get("answer_hash", "")
        if _hash_answer(normalized) == expected_hash:
            elapsed = int((time.time() - start) * 1000)
            return VerifyResult(
                valid=True,
                challenge_type=payload.get("type"),
                elapsed_ms=elapsed,
            )

        return VerifyResult(
            valid=False,
            error="Incorrect answer",
            challenge_type=payload.get("type"),
        )


# ── Token encoding ────────────────────────────────────

class TokenError(Exception):
    pass


def _encode_token(payload: dict, secret: bytes) -> str:
    """Encode payload as signed token: base64url(json).signature"""
    data = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(secret, data.encode(), hashlib.sha256).hexdigest()
    return f"{data}.{sig}"


def _decode_token(token: str, secret: bytes) -> dict:
    """Decode and verify a signed token."""
    if not token or "." not in token:
        raise TokenError("Invalid token format")

    parts = token.rsplit(".", 1)
    if len(parts) != 2:
        raise TokenError("Invalid token format")

    data, sig = parts

    # Verify signature
    expected_sig = hmac.new(secret, data.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        raise TokenError("Invalid token signature")

    # Decode payload
    try:
        payload = json.loads(base64.urlsafe_b64decode(data + "=="))
    except (json.JSONDecodeError, Exception):
        raise TokenError("Corrupted token payload")

    return payload


def _hash_answer(answer: str) -> str:
    """Hash a normalized answer for comparison."""
    return hashlib.sha256(answer.encode("utf-8")).hexdigest()


def _normalize_answer(answer: str) -> str:
    """Normalize an answer for comparison: strip, lowercase, collapse whitespace."""
    if not isinstance(answer, str):
        return ""
    # Strip whitespace, lowercase
    s = answer.strip().lower()
    # Remove surrounding quotes if present
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1].strip()
    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s)
    return s
