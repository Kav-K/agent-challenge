"""String interleave challenge — interleave two strings character by character."""

import random
import string
from typing import Tuple
from ..prompt_builder import build_prompt


def _random_word(length):
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class StringInterleaveChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "basic_interleave", "interleave_reverse", "interleave_extract",
            "basic_interleave_v2", "interleave_extract_v2",
        ])

        length = random.randint(3, 5)
        w1 = _random_word(length)
        w2 = _random_word(length)

        if variant == "basic_interleave":
            interleaved = ''.join(a + b for a, b in zip(w1, w2))
            desc = f'Interleave "{w1}" and "{w2}" character by character (first from "{w1}", then from "{w2}", alternating).'
            prompt = build_prompt(desc)
            return prompt, interleaved.lower()

        elif variant == "basic_interleave_v2":
            interleaved = ''.join(a + b for a, b in zip(w1, w2))
            desc = f'Merge "{w1}" and "{w2}" by alternating characters: take one from "{w1}", one from "{w2}", and repeat.'
            prompt = build_prompt(desc)
            return prompt, interleaved.lower()

        elif variant == "interleave_reverse":
            interleaved = ''.join(a + b for a, b in zip(w1, w2))
            reversed_result = interleaved[::-1]
            desc = f'Interleave "{w1}" and "{w2}" character by character, then reverse the result.'
            prompt = build_prompt(desc)
            return prompt, reversed_result.lower()

        elif variant == "interleave_extract":
            # Interleave then extract every 2nd char (should give back w1)
            interleaved = ''.join(a + b for a, b in zip(w1, w2))
            # Extract odd positions (0, 2, 4...) = w1 characters
            extracted = interleaved[::2]
            desc = f'Interleave "{w1}" and "{w2}" character by character, then extract every 2nd character starting from position 1 (positions 1, 3, 5...).'
            prompt = build_prompt(desc)
            return prompt, extracted.lower()

        else:  # interleave_extract_v2
            interleaved = ''.join(a + b for a, b in zip(w1, w2))
            # Extract even positions (1, 3, 5...) = w2 characters
            extracted = interleaved[1::2]
            desc = f'Interleave "{w1}" and "{w2}" character by character, then take only the characters at even positions (positions 2, 4, 6...).'
            prompt = build_prompt(desc)
            return prompt, extracted.lower()
