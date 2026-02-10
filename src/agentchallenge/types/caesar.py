"""Caesar cipher challenge — decode with a variable shift (not just ROT13)."""

import random
from typing import Tuple
from ..templates import CAESAR_TEMPLATES, reply_inst

CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"
VOWELS = "AEIOU"


def _caesar_encode(text: str, shift: int) -> str:
    return ''.join(
        chr((ord(c) - ord('A') + shift) % 26 + ord('A')) if c.isalpha() else c
        for c in text.upper()
    )


def _random_pronounceable(length: int) -> str:
    result = []
    for i in range(length):
        result.append(random.choice(CONSONANTS if i % 2 == 0 else VOWELS))
    return ''.join(result)


class CaesarChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        word = _random_pronounceable(random.randint(4, 7))
        shift = random.randint(1, 13)
        encoded = _caesar_encode(word, shift)
        template = random.choice(CAESAR_TEMPLATES)
        prompt = template(encoded, shift) + " " + reply_inst()
        return prompt, word.lower()
