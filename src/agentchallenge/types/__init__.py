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

# Difficulty presets — empirically calibrated against gpt-5.2, gpt-4o, gpt-4o-mini
# Only types where GPT-5.2 achieves 100% are active in the tiers below.
DIFFICULTY_MAP = {
    # Easy: All models solve reliably
    # gpt-5.2: 100% | gpt-4o: 100% | gpt-4o-mini: 80-100%
    "easy": [
        "simple_math", "string_math", "binary", "pattern",
    ],
    # Medium: GPT-5.2 100%, GPT-4o ~90%, GPT-4o-mini struggles
    "medium": [
        "sorting", "word_math",
    ],
    # Hard: GPT-5.2 100%, GPT-4o ~75%, GPT-4o-mini failing
    "hard": [
        "nested_operations", "base_conversion_chain",
    ],
    # Agentic: GPT-5.2 100%, GPT-4o ~55%, GPT-4o-mini near-zero
    "agentic": [
        "string_length", "substring",
    ],
}

# Shelved types — GPT-5.2 < 100%, kept for future use when models improve
# These remain importable and in CHALLENGE_TYPES but are excluded from
# difficulty-based random selection.
SHELVED_TYPES = [
    "first_last",            # gpt-5.2: 80%
    "ascii_value",           # gpt-5.2: 80%
    "counting",              # gpt-5.2: 80%
    "rot13",                 # gpt-5.2: 80%
    "reverse_string",        # gpt-5.2: 60%
    "transform",             # gpt-5.2: 60%
    "letter_math",           # gpt-5.2: 60%
    "multi_step_math",       # gpt-5.2: 40%
    "caesar",                # gpt-5.2: 20%
    "chained_transform",     # gpt-5.2: 20%
    "extract_letters",       # gpt-5.2: 20%
    "word_extraction_chain", # gpt-5.2: 20%
    "letter_position",       # gpt-5.2: 0%
    "string_interleave",     # gpt-5.2: 0%
    "zigzag",                # gpt-5.2: 0%
]


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
