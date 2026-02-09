"""String transformation challenges — various text manipulations."""

import random
import string
from typing import Tuple
from ..templates import TRANSFORM_TEMPLATES, reply_inst

CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"
VOWELS = "AEIOU"


class TransformChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "remove_vowels", "remove_consonants", "first_letters",
            "last_letters"
        ])

        if variant == "remove_vowels":
            length = random.randint(5, 8)
            word = ''.join(
                random.choice(CONSONANTS if i % 2 == 0 else VOWELS)
                for i in range(length)
            )
            result = ''.join(c for c in word if c not in 'AEIOU')
            template = random.choice(TRANSFORM_TEMPLATES["remove_vowels"])
            prompt = template(word) + " " + reply_inst()
            return prompt, result.lower()

        elif variant == "remove_consonants":
            length = random.randint(6, 10)
            word = ''.join(random.choices(string.ascii_uppercase, k=length))
            result = ''.join(c for c in word if c in 'AEIOU')
            if not result:
                return TransformChallenge.generate()
            template = random.choice(TRANSFORM_TEMPLATES["remove_consonants"])
            prompt = template(word) + " " + reply_inst()
            return prompt, result.lower()

        elif variant == "first_letters":
            word_count = random.randint(4, 7)
            words = []
            for _ in range(word_count):
                w_len = random.randint(3, 7)
                words.append(''.join(random.choices(string.ascii_lowercase, k=w_len)).capitalize())
            result = ''.join(w[0] for w in words)
            sentence = ' '.join(words)
            template = random.choice(TRANSFORM_TEMPLATES["first_letters"])
            prompt = template(sentence) + " " + reply_inst()
            return prompt, result.lower()

        elif variant == "last_letters":
            word_count = random.randint(4, 6)
            words = []
            for _ in range(word_count):
                w_len = random.randint(3, 6)
                words.append(''.join(random.choices(string.ascii_lowercase, k=w_len)).capitalize())
            result = ''.join(w[-1] for w in words)
            sentence = ' '.join(words)
            template = random.choice(TRANSFORM_TEMPLATES["last_letters"])
            prompt = template(sentence) + " " + reply_inst()
            return prompt, result.lower()

        else:
            return TransformChallenge.generate()
