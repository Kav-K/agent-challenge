"""
Chained arithmetic: 4-step chain with small numbers.
(a + b) * c - d, then modulo m.

GPT-5.2: 100% | GPT-4o: 30% | GPT-4o-mini: ~10%
"""
import random
from typing import Tuple
from ..templates import reply_inst


class ChainedArithmeticChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        c = random.randint(2, 5)
        d = random.randint(1, 9)
        m = random.randint(3, 7)
        result = ((a + b) * c - d) % m

        templates = [
            lambda: f"Compute ({a} + {b}), multiply by {c}, subtract {d}, then find the remainder when divided by {m}.",
            lambda: f"Add {a} and {b}. Multiply the result by {c}. Subtract {d}. What is the remainder when divided by {m}?",
            lambda: f"What is (({a} + {b}) × {c} - {d}) mod {m}?",
            lambda: f"Calculate {a} plus {b}, times {c}, minus {d}. Find the remainder after dividing by {m}.",
            lambda: f"Start with {a} + {b}. Multiply by {c}. Take away {d}. Divide by {m} and give the remainder.",
        ]
        prompt = random.choice(templates)() + " " + reply_inst()
        return prompt, str(result)
