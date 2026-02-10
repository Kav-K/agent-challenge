"""
Chained arithmetic: 4-step chain with small numbers.
Multiple operation patterns for variety. Pure arithmetic only —
world-knowledge patterns removed after testing showed GPT-5.2
drops to ~90% when recalling facts (not 100%).

GPT-5.2: 100% | GPT-4o: ~30% | Humans: 15-20s without paper
"""
import random
from typing import Tuple
from ..templates import reply_inst


class ChainedArithmeticChallenge:
    PATTERNS = [
        "add_mul_sub_mod",
        "mul_add_mul_mod",
        "add_square_sub_mod",
        "mul_sub_add_mod",
    ]

    @staticmethod
    def generate() -> Tuple[str, str]:
        pattern = random.choice(ChainedArithmeticChallenge.PATTERNS)

        if pattern == "add_mul_sub_mod":
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            c = random.randint(2, 5)
            d = random.randint(1, 9)
            m = random.randint(3, 7)
            result = ((a + b) * c - d) % m
            templates = [
                f"Compute ({a} + {b}), multiply by {c}, subtract {d}, then find the remainder when divided by {m}.",
                f"Add {a} and {b}. Multiply the result by {c}. Subtract {d}. What is the remainder when divided by {m}?",
                f"What is (({a} + {b}) × {c} - {d}) mod {m}?",
            ]

        elif pattern == "mul_add_mul_mod":
            a = random.randint(2, 7)
            b = random.randint(2, 5)
            c = random.randint(3, 9)
            d = random.randint(2, 4)
            m = random.randint(3, 7)
            result = ((a * b + c) * d) % m
            templates = [
                f"Multiply {a} by {b}. Add {c}. Multiply by {d}. Find the remainder when divided by {m}.",
                f"Compute {a} × {b}, add {c}, multiply that by {d}, then take mod {m}.",
            ]

        elif pattern == "add_square_sub_mod":
            a = random.randint(2, 5)
            b = random.randint(1, 4)
            c = random.randint(1, 8)
            m = random.randint(3, 7)
            result = ((a + b) ** 2 - c) % m
            templates = [
                f"Add {a} and {b}. Square the result. Subtract {c}. Find the remainder when divided by {m}.",
                f"Compute ({a} + {b})², subtract {c}, then find the remainder mod {m}.",
            ]

        else:  # mul_sub_add_mod
            a = random.randint(3, 9)
            b = random.randint(2, 5)
            c = random.randint(1, min(a * b - 1, 9))
            d = random.randint(2, 9)
            m = random.randint(3, 7)
            result = (a * b - c + d) % m
            templates = [
                f"Multiply {a} by {b}. Subtract {c}. Add {d}. Find the remainder when divided by {m}.",
                f"Compute {a} × {b} - {c} + {d}, then take mod {m}.",
            ]

        prompt = random.choice(templates) + " " + reply_inst()
        return prompt, str(result)
