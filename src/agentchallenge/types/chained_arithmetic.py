"""
Chained arithmetic: 4-step chain with small numbers.
Multiple operation patterns. Some patterns use world-knowledge facts
with stated values as the starting numbers — humans must Google facts
AND do multi-step mental arithmetic.

GPT-5.2: 100% | GPT-4o: ~30% | Humans: impossible in <10s
"""
import random
from typing import Tuple
from ..templates import reply_inst


# World-knowledge facts with stated values — humans need Google to verify
KNOWLEDGE_FACTS = [
    ("the atomic number of oxygen (8)", 8),
    ("the atomic number of carbon (6)", 6),
    ("the atomic number of nitrogen (7)", 7),
    ("the atomic number of neon (10)", 10),
    ("the atomic number of sodium (11)", 11),
    ("the number of planets in our solar system (8)", 8),
    ("the number of continents on Earth (7)", 7),
    ("the number of sides on a hexagon (6)", 6),
    ("the number of sides on a pentagon (5)", 5),
    ("the number of strings on a guitar (6)", 6),
    ("the number of strings on a violin (4)", 4),
    ("the US flag's stripe count (13)", 13),
    ("the number of legs on a spider (8)", 8),
    ("the number of legs on an insect (6)", 6),
    ("the number of Harry Potter books (7)", 7),
    ("Brazil's FIFA World Cup titles (5)", 5),
    ("the number of Olympic rings (5)", 5),
    ("the total dots on a die (21)", 21),
    ("the number of ounces in a pound (16)", 16),
    ("the number of inches in a foot (12)", 12),
    ("the number of bits in a byte (8)", 8),
    ("Beethoven's symphony count (9)", 9),
    ("the number of players on a soccer team (11)", 11),
    ("the number of players on a basketball team (5)", 5),
    ("the number of holes on a golf course (18)", 18),
    ("the number of hours in a day (24)", 24),
]


class ChainedArithmeticChallenge:
    PATTERNS = [
        "add_mul_sub_mod",
        "mul_add_mul_mod",
        "add_square_sub_mod",
        "mul_sub_add_mod",
        "knowledge_chain",
        "knowledge_chain_v2",
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

        elif pattern == "mul_sub_add_mod":
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

        elif pattern == "knowledge_chain":
            # Knowledge fact as starting value + 3-step arithmetic chain
            f1 = random.choice(KNOWLEDGE_FACTS)
            desc, val = f1
            c = random.randint(2, 5)
            d = random.randint(1, 9)
            m = random.randint(3, 7)
            result = (val * c - d) % m
            templates = [
                f"Take {desc}. Multiply it by {c}. Subtract {d}. Find the remainder when divided by {m}.",
                f"Start with {desc}. Times {c}, minus {d}, mod {m}. What's the answer?",
            ]

        else:  # knowledge_chain_v2
            # Two knowledge facts combined + arithmetic
            f1, f2 = random.sample(KNOWLEDGE_FACTS, 2)
            desc1, val1 = f1
            desc2, val2 = f2
            c = random.randint(2, 4)
            m = random.randint(3, 7)
            result = ((val1 + val2) * c) % m
            templates = [
                f"Add {desc1} to {desc2}. Multiply the sum by {c}. Find the remainder when divided by {m}.",
                f"Take {desc1} and {desc2}. Sum them, multiply by {c}, then mod {m}.",
            ]

        prompt = random.choice(templates) + " " + reply_inst()
        return prompt, str(result)
