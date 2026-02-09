"""Number pattern completion — randomly generated arithmetic sequences."""

import random
from typing import Tuple


class PatternChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        pattern_type = random.choice([
            "add", "multiply", "add_growing", "squares", "triangular"
        ])

        if pattern_type == "add":
            start = random.randint(1, 50)
            step = random.randint(2, 15)
            seq = [start + step * i for i in range(5)]
            answer = seq[-1] + step

        elif pattern_type == "multiply":
            base = random.choice([2, 3, 4, 5])
            start_exp = random.randint(0, 2)
            seq = [base ** (start_exp + i) for i in range(5)]
            answer = base ** (start_exp + 5)

        elif pattern_type == "add_growing":
            start = random.randint(1, 20)
            initial_step = random.randint(1, 5)
            seq = [start]
            for i in range(4):
                seq.append(seq[-1] + initial_step + i)
            answer = seq[-1] + initial_step + 4

        elif pattern_type == "squares":
            offset = random.randint(0, 10)
            start_n = random.randint(1, 5)
            seq = [(start_n + i) ** 2 + offset for i in range(5)]
            answer = (start_n + 5) ** 2 + offset

        else:  # triangular
            start = random.randint(1, 10)
            step_inc = random.randint(2, 4)
            seq = [start]
            current_step = step_inc
            for _ in range(4):
                seq.append(seq[-1] + current_step)
                current_step += step_inc
            answer = seq[-1] + current_step

        display = seq
        seq_str = ", ".join(str(n) for n in display)
        prompt = f"What comes next in this sequence: {seq_str}, ? Reply with ONLY the number, nothing else."
        return prompt, str(answer)
