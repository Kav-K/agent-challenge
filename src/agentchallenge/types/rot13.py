"""ROT13 decode challenge — decode a ROT13-encoded random string."""

import random
from typing import Tuple
from ..templates import ROT13_TEMPLATES, reply_inst

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
        word = _random_pronounceable(length)
        encoded = _rot13(word)
        template = random.choice(ROT13_TEMPLATES)
        prompt = template(encoded) + " " + reply_inst()
        return prompt, word.lower()
