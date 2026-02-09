"""Letter extraction challenge — extract every Nth letter from a randomly generated string."""

import random
import string
from typing import Tuple
from ..templates import EXTRACT_TEMPLATES, reply_inst

FILLER_LETTERS = "BCDFGHJKLMNPQRSTVWXYZ"


def _random_hidden_word() -> str:
    length = random.randint(4, 6)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def _interleave(word: str, n: int) -> str:
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
        templates = EXTRACT_TEMPLATES.get(n, EXTRACT_TEMPLATES[2])
        template = random.choice(templates)
        prompt = template(mixed) + " " + reply_inst()
        return prompt, word.lower()
