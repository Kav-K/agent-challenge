"""Caesar cipher challenge — decode with a variable shift (not just ROT13)."""

import random
from typing import Tuple

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
        shift = random.choice([3, 5, 7, 11])
        encoded = _caesar_encode(word, shift)
        prompt = (
            f"Decode this Caesar cipher (each letter is shifted {shift} positions forward in the alphabet): {encoded}\n"
            f"Shift each letter {shift} positions BACKWARD to decode. Reply with ONLY the decoded word, nothing else."
        )
        return prompt, word.lower()
