"""Multi-step math — chain 2-3 arithmetic operations."""

import random
from typing import Tuple
from ..prompt_builder import build_prompt


def _digit_sum(n):
    return sum(int(d) for d in str(abs(n)))


class MultiStepMathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "multiply_then_add",
            "add_then_digit_sum",
            "multiply_then_digit_sum",
            "divide_then_multiply",
            "expression_then_modulo",
            "two_expressions_add",
        ])

        if variant == "multiply_then_add":
            a, b = random.randint(11, 25), random.randint(11, 25)
            c = random.randint(10, 50)
            answer = a * b + c
            desc = f"Calculate {a} × {b}, then add {c} to the result."

        elif variant == "add_then_digit_sum":
            a = random.randint(100, 500)
            b = random.randint(100, 500)
            total = a + b
            answer = _digit_sum(total)
            desc = f"Add {a} and {b}, then find the digit sum of the result."

        elif variant == "multiply_then_digit_sum":
            a = random.randint(12, 30)
            b = random.randint(12, 30)
            product = a * b
            answer = _digit_sum(product)
            desc = f"Multiply {a} by {b}, then find the digit sum of the result."

        elif variant == "divide_then_multiply":
            # Ensure clean division
            divisor = random.randint(3, 12)
            quotient = random.randint(5, 25)
            dividend = divisor * quotient
            multiplier = random.randint(2, 9)
            answer = quotient * multiplier
            desc = f"Divide {dividend} by {divisor}, then multiply the result by {multiplier}."

        elif variant == "expression_then_modulo":
            a = random.randint(15, 50)
            b = random.randint(10, 40)
            mod = random.randint(7, 13)
            total = a + b
            answer = total % mod
            desc = f"Add {a} and {b}, then find the remainder when divided by {mod}."

        elif variant == "two_expressions_add":
            a, b = random.randint(11, 30), random.randint(11, 30)
            c, d = random.randint(10, 50), random.randint(10, 50)
            answer = (a * b) + (c + d)
            desc = f"Calculate ({a} × {b}) + ({c} + {d})."

        prompt = build_prompt(desc)
        return prompt, str(answer)
