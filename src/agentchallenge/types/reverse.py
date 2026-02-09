"""Reverse string challenge — reverse a randomly generated string."""

import random
import string
from typing import Tuple
from ..templates import REVERSE_TEMPLATES, reply_inst

CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"
VOWELS = "AEIOU"


def _random_pronounceable(length: int) -> str:
    result = []
    for i in range(length):
        if i % 2 == 0:
            result.append(random.choice(CONSONANTS))
        else:
            result.append(random.choice(VOWELS))
    return ''.join(result)


def _random_word() -> str:
    length = random.randint(5, 8)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class ReverseStringChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice(["pronounceable", "random", "mixed"])
        if variant == "pronounceable":
            word = _random_pronounceable(random.randint(5, 9))
        elif variant == "random":
            word = _random_word()
        else:
            length = random.randint(5, 8)
            word = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

        reversed_word = word[::-1]
        template = random.choice(REVERSE_TEMPLATES)
        prompt = template(word) + " " + reply_inst()
        return prompt, reversed_word.lower()
