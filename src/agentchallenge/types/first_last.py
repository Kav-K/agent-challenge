"""First/last character challenge — identify first and/or last characters."""

import random
import string
from typing import Tuple
from ..templates import reply_inst


def _random_word(min_len=5, max_len=10):
    return ''.join(random.choices(string.ascii_uppercase, k=random.randint(min_len, max_len)))


class FirstLastChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "first_only", "last_only", "first_and_last",
            "first_and_last_v2", "first_only_v2",
        ])

        word = _random_word()

        if variant == "first_only":
            templates = [
                lambda w: f'What is the first character of "{w}"?',
                lambda w: f'What letter does "{w}" start with?',
                lambda w: f'Identify the first letter in the string "{w}".',
                lambda w: f'Tell me the opening character of "{w}".',
                lambda w: f'What character begins the string "{w}"?',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = word[0].lower()

        elif variant == "first_only_v2":
            templates = [
                lambda w: f'Name the first letter of "{w}".',
                lambda w: f'Which letter appears first in "{w}"?',
                lambda w: f'Look at "{w}" — what is its first character?',
                lambda w: f'What is the leading character of the string "{w}"?',
                lambda w: f'Give me the first letter in "{w}".',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = word[0].lower()

        elif variant == "last_only":
            templates = [
                lambda w: f'What is the last character of "{w}"?',
                lambda w: f'What letter does "{w}" end with?',
                lambda w: f'Identify the final letter in the string "{w}".',
                lambda w: f'Tell me the closing character of "{w}".',
                lambda w: f'What character ends the string "{w}"?',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = word[-1].lower()

        elif variant == "first_and_last":
            templates = [
                lambda w: f'What are the first and last characters of "{w}"? Give them separated by a comma.',
                lambda w: f'Tell me the first and last letters of "{w}", comma-separated.',
                lambda w: f'For the string "{w}", what are the first and last characters? (comma-separated)',
                lambda w: f'Identify the first and last letters in "{w}" and separate them with a comma.',
                lambda w: f'Give me the opening and closing characters of "{w}", separated by a comma.',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = f"{word[0].lower()}, {word[-1].lower()}"

        else:  # first_and_last_v2
            templates = [
                lambda w: f'Look at "{w}". What are its first and last characters, separated by a comma?',
                lambda w: f'Name the first and last letters of the string "{w}" (comma-separated).',
                lambda w: f'What letter starts and what letter ends "{w}"? Reply with both, comma-separated.',
                lambda w: f'From "{w}", extract the first and last characters, comma-separated.',
                lambda w: f'Tell me the beginning and ending characters of "{w}", separated by a comma.',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = f"{word[0].lower()}, {word[-1].lower()}"

        return prompt, answer
