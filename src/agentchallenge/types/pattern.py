"""Number pattern completion — randomly generated arithmetic sequences."""

import random
from typing import Tuple
from ..templates import PATTERN_TEMPLATES, reply_inst


def _is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def _next_prime(n):
    c = n + 1
    while not _is_prime(c):
        c += 1
    return c


class PatternChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        pattern_type = random.choice([
            "add", "multiply", "add_growing", "squares", "triangular",
            "fibonacci_like", "triangular_numbers", "primes", "decreasing"
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

        elif pattern_type == "triangular":
            start = random.randint(1, 10)
            step_inc = random.randint(2, 4)
            seq = [start]
            current_step = step_inc
            for _ in range(4):
                seq.append(seq[-1] + current_step)
                current_step += step_inc
            answer = seq[-1] + current_step

        elif pattern_type == "fibonacci_like":
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            seq = [a, b]
            for _ in range(3):
                seq.append(seq[-1] + seq[-2])
            answer = seq[-1] + seq[-2]

        elif pattern_type == "triangular_numbers":
            start_n = random.randint(1, 4)
            seq = [(start_n + i) * (start_n + i + 1) // 2 for i in range(5)]
            answer = (start_n + 5) * (start_n + 6) // 2

        elif pattern_type == "primes":
            # Generate a sequence of consecutive primes
            start_prime = random.choice([2, 3, 5, 7, 11, 13])
            seq = [start_prime]
            for _ in range(4):
                seq.append(_next_prime(seq[-1]))
            answer = _next_prime(seq[-1])

        else:  # decreasing
            start = random.randint(80, 150)
            step = random.randint(3, 12)
            seq = [start - step * i for i in range(5)]
            answer = seq[-1] - step

        seq_str = ", ".join(str(n) for n in seq)
        template = random.choice(PATTERN_TEMPLATES)
        prompt = template(seq_str) + " " + reply_inst()
        return prompt, str(answer)
