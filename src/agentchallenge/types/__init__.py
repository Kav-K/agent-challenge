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
from .chained_transform import ChainedTransformChallenge
from .multi_step_math import MultiStepMathChallenge
from .base_conversion_chain import BaseConversionChainChallenge
from .word_extraction_chain import WordExtractionChainChallenge
from .letter_math import LetterMathChallenge
from .string_length import StringLengthChallenge
from .first_last import FirstLastChallenge
from .ascii_value import AsciiValueChallenge
from .string_math import StringMathChallenge
from .substring import SubstringChallenge
from .zigzag import ZigzagChallenge
from .nested_operations import NestedOperationsChallenge
from .string_interleave import StringInterleaveChallenge

# Registry of all challenge types — 25 types, each with multiple random variants
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
    "chained_transform": ChainedTransformChallenge,
    "multi_step_math": MultiStepMathChallenge,
    "base_conversion_chain": BaseConversionChainChallenge,
    "word_extraction_chain": WordExtractionChainChallenge,
    "letter_math": LetterMathChallenge,
    "string_length": StringLengthChallenge,
    "first_last": FirstLastChallenge,
    "ascii_value": AsciiValueChallenge,
    "string_math": StringMathChallenge,
    "substring": SubstringChallenge,
    "zigzag": ZigzagChallenge,
    "nested_operations": NestedOperationsChallenge,
    "string_interleave": StringInterleaveChallenge,
}

# Difficulty presets
DIFFICULTY_MAP = {
    "easy": [
        "reverse_string", "simple_math", "pattern", "counting",
        "string_length", "first_last",
    ],
    "medium": [
        "reverse_string", "simple_math", "rot13", "letter_position",
        "extract_letters", "pattern", "counting", "sorting", "binary",
        "ascii_value", "string_math",
    ],
    "hard": [
        "caesar", "word_math", "transform", "binary", "sorting",
        "rot13", "extract_letters", "letter_position", "counting",
        "pattern", "reverse_string", "simple_math",
        "substring", "zigzag",
    ],
    "agentic": [
        "chained_transform", "multi_step_math", "base_conversion_chain",
        "word_extraction_chain", "letter_math", "caesar",
        "nested_operations", "string_interleave",
    ],
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
