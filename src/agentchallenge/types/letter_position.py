"""Letter position sum — sum alphabetical positions of letters in a random string."""

import random
import string
from typing import Tuple
from ..templates import LETTER_POS_TEMPLATES, reply_inst


def _random_short_word() -> str:
    length = random.randint(3, 4)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class LetterPositionChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        word = _random_short_word()
        total = sum(ord(c) - ord('A') + 1 for c in word)
        template = random.choice(LETTER_POS_TEMPLATES)
        prompt = template(word) + " " + reply_inst()
        return prompt, str(total)
