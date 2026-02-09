"""Letter position sum — sum alphabetical positions of letters in a random string."""

import random
import string
from typing import Tuple


def _random_short_word() -> str:
    """Generate a random 3-4 letter uppercase word."""
    length = random.randint(3, 4)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class LetterPositionChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        word = _random_short_word()
        total = sum(ord(c) - ord('A') + 1 for c in word)
        prompt = (
            f"If A=1, B=2, C=3, ... Z=26, what is the sum of the letter values in \"{word}\"? "
            f"Reply with ONLY the number, nothing else."
        )
        return prompt, str(total)
