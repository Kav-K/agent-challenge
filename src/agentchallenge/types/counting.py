"""Counting challenges — count specific items in random strings."""

import random
import string
from typing import Tuple
from ..templates import COUNTING_TEMPLATES, reply_inst


class CountingChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "count_letter", "count_consonants", "count_digit_occurrences",
            "count_uppercase"
        ])

        if variant == "count_letter":
            target = random.choice(string.ascii_uppercase)
            length = random.randint(10, 18)
            chars = [target] * random.randint(2, 5)
            others = random.choices([c for c in string.ascii_uppercase if c != target], k=length - len(chars))
            chars.extend(others)
            random.shuffle(chars)
            text = ''.join(chars)
            count = text.count(target)
            template = random.choice(COUNTING_TEMPLATES["count_letter"])
            prompt = template(target, text) + " " + reply_inst()
            return prompt, str(count)

        elif variant == "count_consonants":
            length = random.randint(6, 10)
            text = ''.join(random.choices(string.ascii_uppercase, k=length))
            count = sum(1 for c in text if c not in 'AEIOU')
            template = random.choice(COUNTING_TEMPLATES["count_consonants"])
            prompt = template(text) + " " + reply_inst()
            return prompt, str(count)

        elif variant == "count_digit_occurrences":
            length = random.randint(8, 14)
            digits = ''.join(random.choices(string.digits, k=length))
            target = random.choice(digits)
            count = digits.count(target)
            template = random.choice(COUNTING_TEMPLATES["count_digits"])
            prompt = template(target, digits) + " " + reply_inst()
            return prompt, str(count)

        else:  # count_uppercase in mixed case
            length = random.randint(10, 16)
            text = ''.join(random.choice(string.ascii_letters) for _ in range(length))
            count = sum(1 for c in text if c.isupper())
            template = random.choice(COUNTING_TEMPLATES["count_upper"])
            prompt = template(text) + " " + reply_inst()
            return prompt, str(count)
