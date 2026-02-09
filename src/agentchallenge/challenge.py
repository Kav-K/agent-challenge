"""Core challenge creation and verification logic."""

import hashlib
import hmac
import json
import base64
import time
import secrets
import re
import os
import logging
from dataclasses import dataclass, field
from typing import Optional

from .types import CHALLENGE_TYPES, generate_challenge
from .dynamic import generate_dynamic_challenge, PROVIDERS

logger = logging.getLogger("agentchallenge")


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

    ## Static Mode (default)
    Uses 12 built-in challenge types with fully randomized inputs.
    No external API calls needed. Fast, deterministic, free.

    ## Dynamic Mode
    Uses an LLM to generate novel, creative challenges. Each challenge
    is verified by a second LLM call to ensure it has exactly one correct answer.

    ⚠️ Dynamic mode adds 2 LLM API requests per challenge generation
    (one to generate, one to verify). This adds latency and cost to your
    challenge endpoint.

    To enable dynamic mode, set an API key and call enable_dynamic_mode():

        ac = AgentChallenge(secret="your-secret")
        ac.set_openai_api_key("sk-...")  # or set OPENAI_API_KEY env var
        ac.enable_dynamic_mode()

    Supported providers: OpenAI, Anthropic, Google Gemini.

    Args:
        secret: Server secret key for signing tokens (min 8 chars).
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

        # Dynamic mode state
        self._dynamic_enabled = False
        self._dynamic_provider = None
        self._dynamic_model = None
        self._dynamic_verify_model = None
        self._api_keys = {}  # provider_name -> key

        # Auto-detect API keys from environment
        for provider_name, config in PROVIDERS.items():
            env_key = os.environ.get(config["env_key"])
            if env_key:
                self._api_keys[provider_name] = env_key

    # ── API Key Management ────────────────────────────

    def set_openai_api_key(self, key: str) -> "AgentChallenge":
        """Set OpenAI API key for dynamic challenge generation."""
        self._api_keys["openai"] = key
        return self

    def set_anthropic_api_key(self, key: str) -> "AgentChallenge":
        """Set Anthropic API key for dynamic challenge generation."""
        self._api_keys["anthropic"] = key
        return self

    def set_google_api_key(self, key: str) -> "AgentChallenge":
        """Set Google Gemini API key for dynamic challenge generation."""
        self._api_keys["google"] = key
        return self

    # ── Dynamic Mode ──────────────────────────────────

    def enable_dynamic_mode(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        verify_model: Optional[str] = None,
    ) -> "AgentChallenge":
        """
        Enable dynamic LLM-generated challenges.

        ⚠️ This adds 2 LLM API requests per challenge generation
        (one to generate, one to verify). This adds latency (~2-5s)
        and cost to your challenge endpoint.

        Falls back to static challenges if the LLM call fails.

        Args:
            provider: "openai", "anthropic", or "google". Auto-detected from available keys if None.
            model: LLM model to use for generation. Uses provider default if None.
            verify_model: LLM model for verification. Uses same as generation if None.

        Returns:
            self (for chaining)

        Raises:
            ValueError: If no API key is available for the selected provider.
        """
        # Resolve provider
        if provider:
            if provider not in PROVIDERS:
                raise ValueError(f"Unknown provider: {provider}. Choose from: {list(PROVIDERS.keys())}")
            if provider not in self._api_keys:
                raise ValueError(
                    f"No API key set for {provider}. "
                    f"Use set_{provider}_api_key() or set {PROVIDERS[provider]['env_key']} env var."
                )
            self._dynamic_provider = provider
        else:
            # Auto-detect: prefer openai > anthropic > google
            for p in ["openai", "anthropic", "google"]:
                if p in self._api_keys:
                    self._dynamic_provider = p
                    break
            if not self._dynamic_provider:
                raise ValueError(
                    "No API key available. Set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY "
                    "or use set_openai_api_key() / set_anthropic_api_key() / set_google_api_key()"
                )

        self._dynamic_enabled = True
        self._dynamic_model = model
        self._dynamic_verify_model = verify_model

        logger.info(
            f"Dynamic mode enabled: provider={self._dynamic_provider}, "
            f"model={model or PROVIDERS[self._dynamic_provider]['default_model']}"
        )
        return self

    def disable_dynamic_mode(self) -> "AgentChallenge":
        """Disable dynamic mode and return to static challenges only."""
        self._dynamic_enabled = False
        logger.info("Dynamic mode disabled")
        return self

    @property
    def dynamic_mode(self) -> bool:
        """Whether dynamic challenge generation is currently enabled."""
        return self._dynamic_enabled

    # ── Challenge Creation ────────────────────────────

    def create(self, challenge_type: Optional[str] = None) -> Challenge:
        """
        Create a new challenge.

        If dynamic mode is enabled and no specific type is requested,
        attempts to generate a challenge via LLM. Falls back to static
        challenges if the LLM call fails.

        Args:
            challenge_type: Optional specific static challenge type. If set, bypasses dynamic mode.

        Returns:
            Challenge object with prompt, token, and metadata.
        """
        # Dynamic mode: try LLM-generated challenge
        if self._dynamic_enabled and not challenge_type:
            result = generate_dynamic_challenge(
                provider_name=self._dynamic_provider,
                api_key=self._api_keys[self._dynamic_provider],
                model=self._dynamic_model,
                verify_model=self._dynamic_verify_model,
            )
            if result:
                prompt, answer = result
                return self._build_challenge("dynamic", prompt, answer)

        # Static mode (or dynamic fallback)
        ctype, prompt, answer = generate_challenge(
            difficulty=self._difficulty,
            specific_type=challenge_type,
            allowed_types=self._allowed_types,
        )
        return self._build_challenge(ctype, prompt, answer)

    def _build_challenge(self, ctype: str, prompt: str, answer: str) -> Challenge:
        """Build a Challenge object from type, prompt, and answer."""
        challenge_id = "ch_" + secrets.token_hex(12)
        now = time.time()
        payload = {
            "id": challenge_id,
            "type": ctype,
            "answer_hash": _hash_answer(answer),
            "created_at": int(now),
            "expires_at": int(now + self._ttl),
        }
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
