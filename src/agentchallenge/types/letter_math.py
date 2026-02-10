"""Letter math — arithmetic using letter positions (A=1, B=2... Z=26)."""

import random
import string
from typing import Tuple
from ..prompt_builder import build_prompt


def _pos(letter):
    return ord(letter.upper()) - ord('A') + 1


class LetterMathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "sum_letters",
            "subtract_letters",
            "multiply_two",
            "sum_word",
            "product_then_mod",
        ])

        if variant == "sum_letters":
            # Sum 3-4 letter values
            count = random.randint(3, 4)
            letters = random.sample(string.ascii_uppercase, count)
            total = sum(_pos(l) for l in letters)
            letters_str = ', '.join(letters)
            desc = f"Add the letter values of {letters_str}."
            answer = str(total)

        elif variant == "subtract_letters":
            # Higher letter minus lower letter
            l1 = random.choice(string.ascii_uppercase[12:])  # M-Z
            l2 = random.choice(string.ascii_uppercase[:12])   # A-L
            diff = _pos(l1) - _pos(l2)
            desc = f"Subtract the value of {l2} from the value of {l1}."
            answer = str(diff)

        elif variant == "multiply_two":
            l1 = random.choice(string.ascii_uppercase[:10])  # A-J (1-10)
            l2 = random.choice(string.ascii_uppercase[:10])
            product = _pos(l1) * _pos(l2)
            desc = f"Multiply the value of {l1} by the value of {l2}."
            answer = str(product)

        elif variant == "sum_word":
            # Sum all letter values in a short word
            length = random.randint(4, 6)
            word = ''.join(random.choices(string.ascii_uppercase, k=length))
            total = sum(_pos(c) for c in word)
            desc = f"Sum the letter values of all characters in \"{word}\"."
            answer = str(total)

        elif variant == "product_then_mod":
            l1 = random.choice(string.ascii_uppercase[:8])  # A-H
            l2 = random.choice(string.ascii_uppercase[:8])
            product = _pos(l1) * _pos(l2)
            mod = random.randint(5, 10)
            answer = str(product % mod)
            desc = f"Multiply the value of {l1} by {l2}, then find the remainder when divided by {mod}."

        # Prepend letter-value context
        prefix = random.choice([
            "Using A=1, B=2, ... Z=26: ",
            "Letter positions: A=1 through Z=26. ",
            "Given that each letter has a numeric value (A=1, B=2, ... Z=26): ",
            "With A=1, B=2, C=3, ..., Z=26: ",
        ])
        prompt = build_prompt(prefix + desc)
        return prompt, answer
