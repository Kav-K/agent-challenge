"""Chained transform — apply 2-3 string operations in sequence."""

import random
import string
from typing import Tuple
from ..prompt_builder import build_prompt

CONSONANTS = set("BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz")
VOWELS = set("AEIOUaeiou")


def _rot13(s):
    result = []
    for c in s:
        if 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(c)
    return ''.join(result)


def _remove_vowels(s):
    return ''.join(c for c in s if c not in VOWELS)


def _remove_consonants(s):
    return ''.join(c for c in s if c not in CONSONANTS)


def _every_nth(s, n):
    return ''.join(s[i] for i in range(0, len(s), n))


def _swap_case(s):
    return s.swapcase()


# Each chain: (description_template, operations_list)
# description_template takes the word, returns instruction string
# operations_list is a list of callables to apply in order
CHAINS = [
    {
        "desc": lambda w: f"Take the string \"{w}\", reverse it, then apply ROT13 to the result.",
        "ops": [lambda s: s[::-1], _rot13],
    },
    {
        "desc": lambda w: f"Apply ROT13 to \"{w}\", then reverse the result.",
        "ops": [_rot13, lambda s: s[::-1]],
    },
    {
        "desc": lambda w: f"Reverse \"{w}\", then remove all vowels (A, E, I, O, U) from the result.",
        "ops": [lambda s: s[::-1], _remove_vowels],
    },
    {
        "desc": lambda w: f"Take \"{w}\", extract every 2nd character (positions 1, 3, 5...), then reverse that.",
        "ops": [lambda s: _every_nth(s, 2), lambda s: s[::-1]],
    },
    {
        "desc": lambda w: f"Remove all vowels from \"{w}\", then reverse what's left.",
        "ops": [_remove_vowels, lambda s: s[::-1]],
    },
    {
        "desc": lambda w: f"Take \"{w}\", swap uppercase and lowercase, then apply ROT13.",
        "ops": [_swap_case, _rot13],
    },
    {
        "desc": lambda w: f"Reverse \"{w}\", then extract every 2nd character (positions 1, 3, 5...).",
        "ops": [lambda s: s[::-1], lambda s: _every_nth(s, 2)],
    },
    {
        "desc": lambda w: f"Apply ROT13 to \"{w}\", then remove all consonants, keeping only vowels.",
        "ops": [_rot13, _remove_consonants],
    },
    {
        "desc": lambda w: f"Take \"{w}\", remove all vowels, then apply ROT13 to the remaining letters.",
        "ops": [_remove_vowels, _rot13],
    },
    {
        "desc": lambda w: f"Reverse \"{w}\", swap the case of each letter, then extract every 2nd character.",
        "ops": [lambda s: s[::-1], _swap_case, lambda s: _every_nth(s, 2)],
    },
]


class ChainedTransformChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        # Retry up to 10 times to avoid empty results (e.g. ROT13 + remove consonants on all-consonant input)
        for _ in range(10):
            length = random.randint(7, 10)
            # Mix of upper and lowercase for swap_case chains
            word = ''.join(random.choice(string.ascii_letters) for _ in range(length))

            chain = random.choice(CHAINS)

            result = word
            for op in chain["ops"]:
                result = op(result)

            if result:  # Non-empty result found
                desc = chain["desc"](word)
                prompt = build_prompt(desc)
                return prompt, result.lower()

        # Fallback: simple reverse + ROT13 (always produces non-empty)
        word = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        result = _rot13(word[::-1])
        desc = f'Take the string "{word}", reverse it, then apply ROT13 to the result.'
        prompt = build_prompt(desc)
        return prompt, result.lower()
