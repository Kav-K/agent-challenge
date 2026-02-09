"""Letter extraction challenge — extract every Nth letter from a randomly generated string."""

import random
import string
from typing import Tuple

FILLER_LETTERS = "BCDFGHJKLMNPQRSTVWXYZ"


def _random_hidden_word() -> str:
    """Generate a random 4-6 letter uppercase word."""
    length = random.randint(4, 6)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def _interleave(word: str, n: int) -> str:
    """Insert n-1 random filler letters between each letter of the word."""
    result = []
    for i, ch in enumerate(word):
        result.append(ch)
        if i < len(word) - 1:
            for _ in range(n - 1):
                result.append(random.choice(FILLER_LETTERS))
    return ''.join(result)


class ExtractChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        word = _random_hidden_word()
        n = random.choice([2, 3])
        mixed = _interleave(word, n)
        ordinal = {2: "2nd", 3: "3rd"}[n]
        prompt = (
            f"Extract every {ordinal} letter from this string, starting from the 1st character: {mixed}\n"
            f"Reply with ONLY the extracted letters as one word, nothing else."
        )
        return prompt, word.lower()
