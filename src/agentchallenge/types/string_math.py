"""String math challenge — combine string properties with arithmetic."""

import random
import string
from typing import Tuple
from ..templates import reply_inst


def _random_word(min_len=3, max_len=7):
    return ''.join(random.choices(string.ascii_uppercase, k=random.randint(min_len, max_len)))


class StringMathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "multiply_lengths", "add_lengths", "subtract_lengths",
            "length_times_number", "two_lengths_add_const",
        ])

        if variant == "multiply_lengths":
            w1 = _random_word()
            w2 = _random_word()
            l1, l2 = len(w1), len(w2)
            answer = l1 * l2
            templates = [
                lambda a, b, la, lb: f'The string "{a}" has {la} letters and "{b}" has {lb} letters. What is {la} × {lb}?',
                lambda a, b, la, lb: f'"{a}" is {la} characters long, "{b}" is {lb} characters long. Multiply those two lengths.',
                lambda a, b, la, lb: f'Count the letters in "{a}" ({la}) and "{b}" ({lb}), then multiply the counts.',
                lambda a, b, la, lb: f'Find the product of the lengths of "{a}" ({la} chars) and "{b}" ({lb} chars).',
                lambda a, b, la, lb: f'If "{a}" has {la} letters and "{b}" has {lb}, what is {la} times {lb}?',
            ]
            prompt = random.choice(templates)(w1, w2, l1, l2) + " " + reply_inst()
            return prompt, str(answer)

        elif variant == "add_lengths":
            w1 = _random_word()
            w2 = _random_word()
            l1, l2 = len(w1), len(w2)
            answer = l1 + l2
            templates = [
                lambda a, b, la, lb: f'"{a}" has {la} letters and "{b}" has {lb} letters. What is {la} + {lb}?',
                lambda a, b, la, lb: f'Add the lengths of "{a}" ({la}) and "{b}" ({lb}).',
                lambda a, b, la, lb: f'How many characters do "{a}" and "{b}" have combined? ({la} + {lb})',
                lambda a, b, la, lb: f'Sum the character counts: "{a}" has {la}, "{b}" has {lb}.',
                lambda a, b, la, lb: f'What is the total letter count of "{a}" ({la}) plus "{b}" ({lb})?',
            ]
            prompt = random.choice(templates)(w1, w2, l1, l2) + " " + reply_inst()
            return prompt, str(answer)

        elif variant == "subtract_lengths":
            # Ensure w1 is longer
            w1 = _random_word(5, 8)
            w2 = _random_word(3, 4)
            l1, l2 = len(w1), len(w2)
            answer = l1 - l2
            templates = [
                lambda a, b, la, lb: f'"{a}" has {la} letters and "{b}" has {lb} letters. What is {la} - {lb}?',
                lambda a, b, la, lb: f'Subtract the length of "{b}" ({lb}) from the length of "{a}" ({la}).',
                lambda a, b, la, lb: f'How many more characters does "{a}" ({la}) have than "{b}" ({lb})?',
                lambda a, b, la, lb: f'Find the difference between the lengths of "{a}" ({la}) and "{b}" ({lb}).',
                lambda a, b, la, lb: f'"{a}" is {la} characters long, "{b}" is {lb}. What is {la} minus {lb}?',
            ]
            prompt = random.choice(templates)(w1, w2, l1, l2) + " " + reply_inst()
            return prompt, str(answer)

        elif variant == "length_times_number":
            w = _random_word()
            n = random.randint(2, 9)
            answer = len(w) * n
            templates = [
                lambda word, num, l: f'"{word}" has {l} characters. What is {l} × {num}?',
                lambda word, num, l: f'The string "{word}" is {l} letters long. Multiply that by {num}.',
                lambda word, num, l: f'Take the length of "{word}" ({l}) and multiply by {num}.',
                lambda word, num, l: f'If the string "{word}" has {l} characters, what is {l} times {num}?',
                lambda word, num, l: f'How much is the length of "{word}" ({l}) multiplied by {num}?',
            ]
            prompt = random.choice(templates)(w, n, len(w)) + " " + reply_inst()
            return prompt, str(answer)

        else:  # two_lengths_add_const
            w1 = _random_word()
            w2 = _random_word()
            c = random.randint(1, 20)
            l1, l2 = len(w1), len(w2)
            answer = l1 + l2 + c
            templates = [
                lambda a, b, la, lb, k: f'Add the lengths of "{a}" ({la}) and "{b}" ({lb}), then add {k}.',
                lambda a, b, la, lb, k: f'"{a}" has {la} chars, "{b}" has {lb} chars. Compute {la} + {lb} + {k}.',
                lambda a, b, la, lb, k: f'Find the total: length of "{a}" ({la}) + length of "{b}" ({lb}) + {k}.',
                lambda a, b, la, lb, k: f'Sum the character counts of "{a}" and "{b}" ({la} + {lb}), then add {k} more.',
                lambda a, b, la, lb, k: f'What is {la} + {lb} + {k}? (lengths of "{a}" and "{b}" plus {k})',
            ]
            prompt = random.choice(templates)(w1, w2, l1, l2, c) + " " + reply_inst()
            return prompt, str(answer)
