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
    # Easy: gpt-4o-mini solves 100% single-shot (empirically validated)
    # simple_math 100%, first_last 100%, string_math 100%
    "easy": [
        "simple_math", "first_last", "string_math",
    ],
    # Medium: gpt-4o solves 100%, gpt-4o-mini starts failing (80-90%)
    # binary 100%/80%, pattern 100%/80%, word_math 90%/70%,
    # sorting 90%/50%, ascii_value 80%/90%
    "medium": [
        "binary", "pattern", "word_math", "sorting", "ascii_value",
    ],
    # Hard: gpt-4o fails significantly (<70%), gpt-4o-mini near-zero
    # counting 50%/50%, substring 60%/40%, string_length 50%/60%,
    # reverse_string 80%/60%, transform 70%/50%,
    # rot13 40%/20%, caesar 30%/0%, letter_position 20%/10%,
    # extract_letters 10%/0%, zigzag 0%/0%
    "hard": [
        "counting", "substring", "string_length", "reverse_string",
        "transform", "rot13", "caesar", "letter_position",
        "extract_letters", "zigzag",
    ],
    # Agentic: multi-step chains, blocks both gpt-4o and gpt-4o-mini
    # chained_transform 20%/20%, multi_step_math 50%/40%,
    # base_conversion_chain 80%/40%, word_extraction_chain 20%/0%,
    # letter_math 70%/0%, nested_operations 70%/80%,
    # string_interleave 30%/0%
    "agentic": [
        "chained_transform", "multi_step_math", "base_conversion_chain",
        "word_extraction_chain", "letter_math",
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
