"""Simple arithmetic challenge — add or subtract small numbers."""

import random
from typing import Tuple


class MathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        # Pick operation
        op = random.choice(["+", "-", "+", "+"])  # Bias toward addition

        if op == "+":
            a = random.randint(10, 500)
            b = random.randint(10, 500)
            answer = a + b
            symbol = "+"
        else:
            a = random.randint(100, 999)
            b = random.randint(10, a - 1)  # Ensure positive result
            answer = a - b
            symbol = "-"

        prompt = f"What is {a} {symbol} {b}? Reply with ONLY the number, nothing else."
        return prompt, str(answer)
