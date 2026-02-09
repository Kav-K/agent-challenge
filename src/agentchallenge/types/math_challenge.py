"""Arithmetic challenges — various operations with random numbers."""

import random
from typing import Tuple
from ..templates import MATH_TEMPLATES, reply_inst


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
            template = random.choice(MATH_TEMPLATES["add"])
            prompt = template(a, b)

        elif variant == "subtract":
            a = random.randint(100, 999)
            b = random.randint(10, a - 1)
            answer = a - b
            template = random.choice(MATH_TEMPLATES["subtract"])
            prompt = template(a, b)

        elif variant == "multiply":
            a = random.randint(2, 30)
            b = random.randint(2, 30)
            answer = a * b
            template = random.choice(MATH_TEMPLATES["multiply"])
            prompt = template(a, b)

        elif variant == "add_three":
            a = random.randint(10, 300)
            b = random.randint(10, 300)
            c = random.randint(10, 300)
            answer = a + b + c
            template = random.choice(MATH_TEMPLATES["add_three"])
            prompt = template(a, b, c)

        else:  # subtract_chain
            a = random.randint(500, 999)
            b = random.randint(10, 200)
            c = random.randint(10, min(200, a - b - 1))
            answer = a - b - c
            template = random.choice(MATH_TEMPLATES["subtract_chain"])
            prompt = template(a, b, c)

        prompt += " " + reply_inst()
        return prompt, str(answer)
