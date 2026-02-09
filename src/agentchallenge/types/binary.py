"""Binary/number conversion challenges."""

import random
from typing import Tuple


class BinaryChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice(["binary_to_decimal", "decimal_to_binary", "digit_sum_large"])

        if variant == "binary_to_decimal":
            num = random.randint(1, 63)
            binary = bin(num)[2:]
            prompt = (
                f"Convert binary {binary} to decimal. "
                f"Reply with ONLY the decimal number, nothing else."
            )
            return prompt, str(num)

        elif variant == "decimal_to_binary":
            num = random.randint(1, 31)
            binary = bin(num)[2:]
            prompt = (
                f"Convert the decimal number {num} to binary. "
                f"Reply with ONLY the binary digits (no prefix like 0b), nothing else."
            )
            return prompt, binary

        else:  # digit_sum_large
            num = random.randint(1000, 99999)
            total = sum(int(d) for d in str(num))
            prompt = (
                f"What is the sum of all digits in {num}? "
                f"Reply with ONLY the number, nothing else."
            )
            return prompt, str(total)
