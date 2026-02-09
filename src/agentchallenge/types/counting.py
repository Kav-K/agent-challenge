"""Counting challenges — count specific items in random strings."""

import random
import string
from typing import Tuple


class CountingChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "count_letter", "count_consonants", "count_digit_occurrences",
            "count_uppercase"
        ])

        if variant == "count_letter":
            # Count a specific letter in a random string
            target = random.choice(string.ascii_uppercase)
            length = random.randint(10, 18)
            chars = [target] * random.randint(2, 5)
            others = random.choices([c for c in string.ascii_uppercase if c != target], k=length - len(chars))
            chars.extend(others)
            random.shuffle(chars)
            text = ''.join(chars)
            count = text.count(target)
            prompt = (
                f"How many times does the letter \"{target}\" appear in \"{text}\"? "
                f"Reply with ONLY the number, nothing else."
            )
            return prompt, str(count)

        elif variant == "count_consonants":
            length = random.randint(6, 10)
            text = ''.join(random.choices(string.ascii_uppercase, k=length))
            count = sum(1 for c in text if c not in 'AEIOU')
            prompt = (
                f"How many consonants (non-vowel letters) are in \"{text}\"? "
                f"Reply with ONLY the number, nothing else."
            )
            return prompt, str(count)

        elif variant == "count_digit_occurrences":
            length = random.randint(8, 14)
            digits = ''.join(random.choices(string.digits, k=length))
            target = random.choice(digits)  # Guarantee it appears
            count = digits.count(target)
            prompt = (
                f"How many times does the digit \"{target}\" appear in \"{digits}\"? "
                f"Reply with ONLY the number, nothing else."
            )
            return prompt, str(count)

        else:  # count_uppercase in mixed case
            length = random.randint(10, 16)
            text = ''.join(random.choice(string.ascii_letters) for _ in range(length))
            count = sum(1 for c in text if c.isupper())
            prompt = (
                f"How many UPPERCASE letters are in \"{text}\"? "
                f"Reply with ONLY the number, nothing else."
            )
            return prompt, str(count)
