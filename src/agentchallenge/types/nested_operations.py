"""Nested operations challenge — multi-step math with deep nesting and order of operations."""

import random
from typing import Tuple
from ..prompt_builder import build_prompt


class NestedOperationsChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "double_nest", "triple_nest", "mixed_nest",
            "subtract_nest", "divide_nest",
        ])

        if variant == "double_nest":
            # ((a + b) × c) - d
            a = random.randint(5, 20)
            b = random.randint(3, 15)
            c = random.randint(2, 6)
            d = random.randint(1, 30)
            inner = a + b
            answer = inner * c - d
            desc = f"What is (({a} + {b}) × {c}) - {d}?"

        elif variant == "triple_nest":
            # (a × (b + c)) + d
            a = random.randint(2, 8)
            b = random.randint(3, 12)
            c = random.randint(2, 10)
            d = random.randint(5, 30)
            answer = a * (b + c) + d
            desc = f"What is ({a} × ({b} + {c})) + {d}?"

        elif variant == "mixed_nest":
            # ((a × b) + (c × d))
            a = random.randint(3, 12)
            b = random.randint(2, 8)
            c = random.randint(3, 12)
            d = random.randint(2, 8)
            answer = (a * b) + (c * d)
            desc = f"Calculate ({a} × {b}) + ({c} × {d})."

        elif variant == "subtract_nest":
            # (a + b + c) × d - e
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            c = random.randint(2, 10)
            d = random.randint(2, 5)
            e = random.randint(1, 20)
            answer = (a + b + c) * d - e
            desc = f"What is (({a} + {b} + {c}) × {d}) - {e}?"

        else:  # divide_nest
            # Ensure clean division: (a × b) ÷ c + d
            c = random.randint(2, 8)
            quotient = random.randint(3, 15)
            product = c * quotient
            # Find a, b such that a * b = product
            # Pick a factor
            factors = [i for i in range(2, product) if product % i == 0]
            if not factors:
                a, b = 1, product
            else:
                a = random.choice(factors)
                b = product // a
            d = random.randint(5, 25)
            answer = quotient + d
            desc = f"What is ({a} × {b}) ÷ {c} + {d}?"

        prompt = build_prompt(desc)
        return prompt, str(answer)
