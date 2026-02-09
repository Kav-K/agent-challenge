"""
Challenge types that LLMs can solve through reasoning alone.

Each type generates a (prompt, answer) pair where:
- The prompt is a clear text instruction
- The answer is deterministic and verifiable
- An LLM can solve it without running any code
"""

import random
from typing import Optional, Tuple

from .reverse import ReverseStringChallenge
from .math_challenge import MathChallenge
from .letter_position import LetterPositionChallenge
from .rot13 import Rot13Challenge
from .pattern import PatternChallenge
from .extract import ExtractChallenge
from .word_math import WordMathChallenge

# Registry of all challenge types
CHALLENGE_TYPES = {
    "reverse_string": ReverseStringChallenge,
    "simple_math": MathChallenge,
    "letter_position": LetterPositionChallenge,
    "rot13": Rot13Challenge,
    "pattern": PatternChallenge,
    "extract_letters": ExtractChallenge,
    "word_math": WordMathChallenge,
}

# Difficulty presets
DIFFICULTY_MAP = {
    "easy": ["reverse_string", "simple_math", "pattern"],
    "medium": ["reverse_string", "simple_math", "rot13", "letter_position", "extract_letters", "pattern"],
    "hard": list(CHALLENGE_TYPES.keys()),
}


def generate_challenge(
    difficulty: str = "easy",
    specific_type: Optional[str] = None,
    allowed_types: Optional[list] = None,
) -> Tuple[str, str, str]:
    """
    Generate a random challenge.

    Returns:
        Tuple of (challenge_type_name, prompt_text, correct_answer)
    """
    if specific_type:
        if specific_type not in CHALLENGE_TYPES:
            raise ValueError(f"Unknown challenge type: {specific_type}. Available: {list(CHALLENGE_TYPES.keys())}")
        type_name = specific_type
    else:
        if allowed_types:
            pool = [t for t in allowed_types if t in CHALLENGE_TYPES]
        else:
            pool = DIFFICULTY_MAP.get(difficulty, DIFFICULTY_MAP["easy"])
        type_name = random.choice(pool)

    challenge_cls = CHALLENGE_TYPES[type_name]
    prompt, answer = challenge_cls.generate()
    return type_name, prompt, answer
