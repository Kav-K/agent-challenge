"""
Power modulo: base^exp mod m with small numbers.

GPT-5.2: 100% | GPT-4o: 80% | GPT-4o-mini: ~50%
"""
import random
from typing import Tuple
from ..templates import reply_inst


class PowerModChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        base = random.randint(2, 5)
        exp = random.randint(3, 6)
        m = random.randint(5, 13)
        answer = (base ** exp) % m

        templates = [
            lambda: f"Compute {base} raised to the power {exp}, then find the remainder when divided by {m}.",
            lambda: f"What is {base}^{exp} mod {m}?",
            lambda: f"Calculate {base} to the {exp}th power. Find the remainder when divided by {m}.",
            lambda: f"Raise {base} to the power of {exp}. What is the remainder after dividing by {m}?",
            lambda: f"Exponentiate: {base}^{exp}. Then take modulo {m}.",
        ]
        prompt = random.choice(templates)() + " " + reply_inst()
        return prompt, str(answer)
