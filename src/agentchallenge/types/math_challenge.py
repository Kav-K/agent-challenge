"""Arithmetic challenges — various operations with random numbers."""

import random
from typing import Tuple


class MathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "add", "add", "subtract", "multiply", "add_three", "subtract_chain"
        ])

        if variant == "add":
            a = random.randint(10, 999)
            b = random.randint(10, 999)
            answer = a + b
            prompt = f"What is {a} + {b}? Reply with ONLY the number, nothing else."

        elif variant == "subtract":
            a = random.randint(100, 999)
            b = random.randint(10, a - 1)
            answer = a - b
            prompt = f"What is {a} - {b}? Reply with ONLY the number, nothing else."

        elif variant == "multiply":
            a = random.randint(2, 30)
            b = random.randint(2, 30)
            answer = a * b
            prompt = f"What is {a} × {b}? Reply with ONLY the number, nothing else."

        elif variant == "add_three":
            a = random.randint(10, 300)
            b = random.randint(10, 300)
            c = random.randint(10, 300)
            answer = a + b + c
            prompt = f"What is {a} + {b} + {c}? Reply with ONLY the number, nothing else."

        else:  # subtract_chain
            a = random.randint(500, 999)
            b = random.randint(10, 200)
            c = random.randint(10, min(200, a - b - 1))
            answer = a - b - c
            prompt = f"What is {a} - {b} - {c}? Reply with ONLY the number, nothing else."

        return prompt, str(answer)
