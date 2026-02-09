"""
agent-challenge: LLM-solvable challenge-response authentication for AI agent APIs.

Challenges are puzzles that any LLM can solve through reasoning alone —
no scripts, no computational power, no external tools needed.

Usage (server side):
    from agentchallenge import AgentChallenge

    ac = AgentChallenge(secret="your-server-secret")
    challenge = ac.create()
    # Send challenge.prompt and challenge.token to the agent

    # When agent responds:
    result = ac.verify(token=challenge.token, answer="agent's answer")
    if result.valid:
        print("Agent verified!")

Usage (agent side):
    # Agent receives the prompt text and solves it with reasoning.
    # Example prompt: "Reverse this string: NOHTYP"
    # Agent answers: "PYTHON"
    # That's it. No SDK needed on the agent side.
"""

from .challenge import AgentChallenge, Challenge, VerifyResult
from .types import CHALLENGE_TYPES

__version__ = "0.1.0"
__all__ = ["AgentChallenge", "Challenge", "VerifyResult", "CHALLENGE_TYPES"]
