"""Binary/number conversion challenges."""

import random
from typing import Tuple
from ..templates import BINARY_TEMPLATES, reply_inst


class BinaryChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "binary_to_decimal", "decimal_to_binary", "digit_sum_large",
            "hex_to_decimal"
        ])

        if variant == "binary_to_decimal":
            num = random.randint(1, 63)
            binary = bin(num)[2:]
            template = random.choice(BINARY_TEMPLATES["binary_to_decimal"])
            prompt = template(binary) + " " + reply_inst()
            return prompt, str(num)

        elif variant == "decimal_to_binary":
            num = random.randint(1, 31)
            binary = bin(num)[2:]
            template = random.choice(BINARY_TEMPLATES["decimal_to_binary"])
            prompt = template(num) + " " + reply_inst()
            return prompt, binary

        elif variant == "hex_to_decimal":
            num = random.randint(10, 255)
            hex_str = hex(num)[2:].upper()
            template = random.choice(BINARY_TEMPLATES["hex_to_decimal"])
            prompt = template(hex_str) + " " + reply_inst()
            return prompt, str(num)

        else:  # digit_sum_large
            num = random.randint(1000, 99999)
            total = sum(int(d) for d in str(num))
            template = random.choice(BINARY_TEMPLATES["digit_sum"])
            prompt = template(num) + " " + reply_inst()
            return prompt, str(total)
