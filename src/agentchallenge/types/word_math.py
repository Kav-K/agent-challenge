"""Word math challenges — various counting and word-based number puzzles."""

import random
import string as _s
from typing import Tuple
from ..templates import WORD_MATH_TEMPLATES, reply_inst

NUM_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
    18: "eighteen", 19: "nineteen", 20: "twenty",
}


class WordMathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "digit_to_word", "char_count", "vowel_count", "digit_sum"
        ])

        if variant == "digit_to_word":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            total = a + b
            template = random.choice(WORD_MATH_TEMPLATES["digit_to_word"])
            prompt = template(a, b) + " " + reply_inst()
            return prompt, NUM_WORDS[total]

        elif variant == "char_count":
            length = random.randint(4, 8)
            word = ''.join(random.choices(_s.ascii_uppercase, k=length))
            template = random.choice(WORD_MATH_TEMPLATES["char_count"])
            prompt = template(word) + " " + reply_inst()
            return prompt, str(len(word))

        elif variant == "vowel_count":
            length = random.randint(5, 9)
            word = ''.join(random.choices(_s.ascii_uppercase, k=length))
            count = sum(1 for c in word if c in 'AEIOU')
            template = random.choice(WORD_MATH_TEMPLATES["vowel_count"])
            prompt = template(word) + " " + reply_inst()
            return prompt, str(count)

        else:  # digit_sum
            num = random.randint(100, 9999)
            total = sum(int(d) for d in str(num))
            template = random.choice(WORD_MATH_TEMPLATES["digit_sum"])
            prompt = template(num) + " " + reply_inst()
            return prompt, str(total)
