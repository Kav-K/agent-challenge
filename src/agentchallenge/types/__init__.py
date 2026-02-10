"""
Challenge types that LLMs can solve through reasoning alone.

Each type generates random inputs so the output space is effectively infinite.
No fixed word lists — every challenge is unique.
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
from .caesar import CaesarChallenge
from .sorting import SortingChallenge
from .counting import CountingChallenge
from .transform import TransformChallenge
from .binary import BinaryChallenge

# Registry of all challenge types — 12 types, each with multiple random variants
CHALLENGE_TYPES = {
    "reverse_string": ReverseStringChallenge,
    "simple_math": MathChallenge,
    "letter_position": LetterPositionChallenge,
    "rot13": Rot13Challenge,
    "pattern": PatternChallenge,
    "extract_letters": ExtractChallenge,
    "word_math": WordMathChallenge,
    "caesar": CaesarChallenge,
    "sorting": SortingChallenge,
    "counting": CountingChallenge,
    "transform": TransformChallenge,
    "binary": BinaryChallenge,
}

# Difficulty presets
DIFFICULTY_MAP = {
    "easy": [
        "reverse_string", "simple_math", "pattern", "counting",
    ],
    "medium": [
        "reverse_string", "simple_math", "rot13", "letter_position",
        "extract_letters", "pattern", "counting", "sorting", "binary",
    ],
    "hard": list(CHALLENGE_TYPES.keys()),
}


def generate_challenge(
    difficulty: str = "easy",
    specific_type: Optional[str] = None,
    allowed_types: Optional[list] = None,
) -> Tuple[str, str, str]:
    """
    Generate a random challenge with fully randomized inputs.

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
            if not pool:
                raise ValueError(
                    f"No valid challenge types in allowed_types. "
                    f"Available: {list(CHALLENGE_TYPES.keys())}"
                )
        else:
            pool = DIFFICULTY_MAP.get(difficulty, DIFFICULTY_MAP["easy"])
        type_name = random.choice(pool)

    challenge_cls = CHALLENGE_TYPES[type_name]
    prompt, answer = challenge_cls.generate()
    return type_name, prompt, answer
