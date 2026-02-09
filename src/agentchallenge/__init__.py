"""
agent-challenge: LLM-solvable challenge-response authentication for AI agent APIs.

Challenges are puzzles that any LLM can solve through reasoning alone —
no scripts, no computational power, no external tools needed.

## Static Mode (default)
    from agentchallenge import AgentChallenge

    ac = AgentChallenge(secret="your-server-secret")
    challenge = ac.create()
    # Send challenge.prompt and challenge.token to the agent

    result = ac.verify(token=challenge.token, answer="agent's answer")
    if result.valid:
        print("Agent verified!")

## Dynamic Mode (LLM-generated challenges)
    ac = AgentChallenge(secret="your-server-secret")
    ac.set_openai_api_key("sk-...")       # or OPENAI_API_KEY env var
    ac.enable_dynamic_mode()              # ⚠️ Adds 2 API calls per challenge

    # Also supports:
    ac.set_anthropic_api_key("sk-ant-...")
    ac.set_google_api_key("AI...")
    ac.enable_dynamic_mode(provider="anthropic", model="claude-sonnet-4-20250514")

    ⚠️ Dynamic mode adds 2 LLM API requests per challenge generation
    (one to generate, one to verify). Falls back to static on failure.
"""

from .challenge import AgentChallenge, Challenge, VerifyResult
from .types import CHALLENGE_TYPES

__version__ = "0.2.0"
__all__ = ["AgentChallenge", "Challenge", "VerifyResult", "CHALLENGE_TYPES"]
