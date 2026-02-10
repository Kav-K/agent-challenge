"""Base conversion chain — convert between number bases with arithmetic."""

import random
from typing import Tuple
from ..prompt_builder import build_prompt


class BaseConversionChainChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "bin_add_back",
            "hex_subtract",
            "bin_multiply",
            "dec_to_hex_chain",
        ])

        if variant == "bin_add_back":
            # Convert binary to decimal, add N, convert back to binary
            dec = random.randint(10, 50)
            binary = bin(dec)[2:]
            add_val = random.randint(5, 30)
            result = dec + add_val
            answer = bin(result)[2:]
            desc = f"Convert binary {binary} to decimal, add {add_val}, then convert the result back to binary."

        elif variant == "hex_subtract":
            # Convert hex to decimal, subtract N
            dec = random.randint(30, 200)
            hex_val = hex(dec)[2:].upper()
            sub_val = random.randint(5, dec - 1)
            answer = str(dec - sub_val)
            desc = f"Convert hexadecimal {hex_val} to decimal, then subtract {sub_val}."

        elif variant == "bin_multiply":
            # Convert binary to decimal, multiply by N
            dec = random.randint(5, 20)
            binary = bin(dec)[2:]
            mult = random.randint(2, 8)
            answer = str(dec * mult)
            desc = f"Convert binary {binary} to decimal, then multiply by {mult}."

        elif variant == "dec_to_hex_chain":
            # Multiply two numbers, convert to hex
            a = random.randint(5, 15)
            b = random.randint(5, 15)
            result = a * b
            answer = hex(result)[2:]
            desc = f"Multiply {a} by {b}, then convert the result to hexadecimal (lowercase)."

        prompt = build_prompt(desc)
        return prompt, answer.lower()
