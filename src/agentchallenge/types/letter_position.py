"""Letter position sum challenge — sum the alphabetical positions of letters in a word."""

import random
from typing import Tuple

# Short words (3-5 letters) so the math stays simple
WORDS = [
    "CAT", "DOG", "SUN", "KEY", "BOX", "HAT", "PEN", "CUP",
    "BAG", "MAP", "JAM", "NET", "OWL", "FOX", "HUB", "BIT",
    "LOG", "PIN", "TAG", "ZIP", "ACE", "AXE", "BUG", "COG",
    "DIM", "ELF", "FIG", "GUM", "HOP", "INK", "JOT", "KIT",
]


class LetterPositionChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        word = random.choice(WORDS)
        total = sum(ord(c) - ord('A') + 1 for c in word)
        prompt = (
            f"If A=1, B=2, C=3, ... Z=26, what is the sum of the letter values in the word \"{word}\"? "
            f"Reply with ONLY the number, nothing else."
        )
        return prompt, str(total)
