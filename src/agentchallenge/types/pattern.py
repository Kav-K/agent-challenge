"""Number pattern completion challenge — complete a simple arithmetic sequence."""

import random
from typing import Tuple


class PatternChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        pattern_type = random.choice(["add", "multiply", "add_growing"])

        if pattern_type == "add":
            # Constant addition: 3, 7, 11, 15, ?
            start = random.randint(1, 20)
            step = random.randint(2, 10)
            seq = [start + step * i for i in range(5)]
            answer = seq[-1] + step
            display = seq

        elif pattern_type == "multiply":
            # Powers of N: 2, 4, 8, 16, ?
            base = random.choice([2, 3])
            seq = [base ** i for i in range(1, 6)]
            answer = base ** 6
            display = seq

        else:
            # Growing addition: 1, 2, 4, 7, 11, ? (add 1, add 2, add 3...)
            seq = [random.randint(1, 5)]
            for i in range(1, 5):
                seq.append(seq[-1] + i)
            answer = seq[-1] + 5
            display = seq

        seq_str = ", ".join(str(n) for n in display)
        prompt = f"What comes next in this sequence: {seq_str}, ? Reply with ONLY the number, nothing else."
        return prompt, str(answer)
