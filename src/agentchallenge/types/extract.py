"""Letter extraction challenge — extract every Nth letter from a string."""

import random
from typing import Tuple

HIDDEN_WORDS = [
    "HELLO", "WORLD", "AGENT", "CLOUD", "TOKEN",
    "SMART", "BRAIN", "POWER", "GUARD", "PIXEL",
    "FLAME", "STONE", "RIVER", "EAGLE", "MAGIC",
    "LIGHT", "OCEAN", "PULSE", "FORGE", "QUEST",
]

FILLER_LETTERS = "BCDFGHJKLMNPQRSTVWXYZ"


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
        word = random.choice(HIDDEN_WORDS)
        n = random.choice([2, 3])

        mixed = _interleave(word, n)

        ordinal = {2: "2nd", 3: "3rd"}[n]
        prompt = (
            f"Extract every {ordinal} letter from this string, starting from the 1st character: {mixed}\n"
            f"Reply with ONLY the extracted letters as one word, nothing else."
        )
        return prompt, word.lower()
