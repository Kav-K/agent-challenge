"""ROT13 decode challenge — decode a ROT13-encoded random string."""

import random
import string
from typing import Tuple

CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"
VOWELS = "AEIOU"


def _rot13(text: str) -> str:
    result = []
    for c in text:
        if 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
        elif 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
        else:
            result.append(c)
    return ''.join(result)


def _random_pronounceable(length: int) -> str:
    """Generate a random pronounceable-ish uppercase string."""
    result = []
    for i in range(length):
        if i % 2 == 0:
            result.append(random.choice(CONSONANTS))
        else:
            result.append(random.choice(VOWELS))
    return ''.join(result)


class Rot13Challenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        length = random.randint(4, 7)
        # Generate a random word and encode it
        word = _random_pronounceable(length)
        encoded = _rot13(word)
        prompt = (
            f"Decode this ROT13-encoded string (each letter shifts 13 places back in the alphabet): {encoded}\n"
            f"Reply with ONLY the decoded word, nothing else."
        )
        return prompt, word.lower()
