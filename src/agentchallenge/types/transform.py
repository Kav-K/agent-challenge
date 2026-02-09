"""String transformation challenges — various text manipulations."""

import random
import string
from typing import Tuple

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
            prompt = (
                f"Remove all vowels (A, E, I, O, U) from \"{word}\".\n"
                f"Reply with ONLY the remaining letters, nothing else."
            )
            return prompt, result.lower()

        elif variant == "remove_consonants":
            length = random.randint(6, 10)
            word = ''.join(random.choices(string.ascii_uppercase, k=length))
            result = ''.join(c for c in word if c in 'AEIOU')
            # Ensure there are some vowels
            if not result:
                return TransformChallenge.generate()
            prompt = (
                f"Remove all consonants from \"{word}\" and keep only the vowels (A, E, I, O, U).\n"
                f"Reply with ONLY the remaining vowels, nothing else."
            )
            return prompt, result.lower()

        elif variant == "first_letters":
            word_count = random.randint(4, 7)
            words = []
            for _ in range(word_count):
                w_len = random.randint(3, 7)
                words.append(''.join(random.choices(string.ascii_lowercase, k=w_len)))
            words = [w.capitalize() for w in words]
            result = ''.join(w[0] for w in words)
            sentence = ' '.join(words)
            prompt = (
                f"What do the first letters of each word spell: \"{sentence}\"?\n"
                f"Reply with ONLY the letters as one word, nothing else."
            )
            return prompt, result.lower()

        elif variant == "last_letters":
            word_count = random.randint(4, 6)
            words = []
            for _ in range(word_count):
                w_len = random.randint(3, 6)
                words.append(''.join(random.choices(string.ascii_lowercase, k=w_len)))
            words = [w.capitalize() for w in words]
            result = ''.join(w[-1] for w in words)
            sentence = ' '.join(words)
            prompt = (
                f"What do the LAST letters of each word spell: \"{sentence}\"?\n"
                f"Reply with ONLY the letters as one word, nothing else."
            )
            return prompt, result.lower()

        else:
            # Fallback: try another variant
            return TransformChallenge.generate()
