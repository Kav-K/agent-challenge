"""
Chained arithmetic: 4-step chain with small numbers.
Multiple operation patterns for variety.
Uses prompt_builder for template randomization (anti-scripting).

GPT-5.2: 100% | GPT-4o: ~30% | Humans: 15-20s without paper

Obfuscation strategy: NOT word replacement (breaks models) but
structural randomization — varied sentence order, connector words,
and the existing prompt_builder anti-scripting system handles
instruction phrasing variety.
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
                f"Add {a} and {b}. Multiply by {c}. Subtract {d}. Find the remainder when divided by {m}.",
                f"What is (({a} + {b}) × {c} - {d}) mod {m}?",
                f"Compute {a} + {b}, multiply the sum by {c}, subtract {d}, remainder mod {m}.",
                f"Sum {a} and {b}, then multiply by {c}, then subtract {d}. What is the remainder after dividing by {m}?",
                f"({a} + {b}) × {c} − {d}. Divide by {m} and give the remainder.",
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
                f"What is (({a} × {b} + {c}) × {d}) mod {m}?",
                f"Compute {a} × {b}, add {c}, multiply by {d}, remainder mod {m}.",
                f"Product of {a} and {b}, plus {c}, times {d}. What is the remainder after dividing by {m}?",
                f"({a} × {b} + {c}) × {d}. Divide by {m} and give the remainder.",
            ]

        elif pattern == "add_square_sub_mod":
            a = random.randint(2, 5)
            b = random.randint(1, 4)
            c = random.randint(1, 8)
            m = random.randint(3, 7)
            result = ((a + b) ** 2 - c) % m
            templates = [
                f"Add {a} and {b}. Square the result. Subtract {c}. Find the remainder when divided by {m}.",
                f"What is (({a} + {b})² - {c}) mod {m}?",
                f"Compute ({a} + {b}) squared, subtract {c}, remainder mod {m}.",
                f"Sum {a} and {b}, square it, subtract {c}. Remainder after dividing by {m}?",
                f"({a} + {b})² − {c}. Divide by {m} and give the remainder.",
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
                f"What is ({a} × {b} - {c} + {d}) mod {m}?",
                f"Compute {a} × {b}, subtract {c}, add {d}, remainder mod {m}.",
                f"Product of {a} and {b}, minus {c}, plus {d}. Remainder after dividing by {m}?",
                f"{a} × {b} − {c} + {d}. Divide by {m} and give the remainder.",
            ]

        prompt = random.choice(templates) + " " + reply_inst()
        return prompt, str(result)
