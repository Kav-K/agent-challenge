"""Reverse string challenge — reverse a randomly generated string."""

import random
import string
from typing import Tuple

# Large pool + random generation ensures no fixed answer set
CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"
VOWELS = "AEIOU"


def _random_pronounceable(length: int) -> str:
    """Generate a random pronounceable-ish string."""
    result = []
    for i in range(length):
        if i % 2 == 0:
            result.append(random.choice(CONSONANTS))
        else:
            result.append(random.choice(VOWELS))
    return ''.join(result)


def _random_word() -> str:
    """Generate a random string of 5-8 uppercase letters."""
    length = random.randint(5, 8)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class ReverseStringChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        # Mix of approaches for variety
        variant = random.choice(["pronounceable", "random", "mixed"])
        if variant == "pronounceable":
            word = _random_pronounceable(random.randint(5, 9))
        elif variant == "random":
            word = _random_word()
        else:
            # Mix letters and digits
            length = random.randint(5, 8)
            word = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

        reversed_word = word[::-1]
        prompt = f"Reverse the following string (reply with ONLY the reversed text, nothing else): {word}"
        return prompt, reversed_word.lower()
