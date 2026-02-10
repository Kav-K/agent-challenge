"""ASCII value challenge — convert between characters and ASCII codes."""

import random
import string
from typing import Tuple
from ..templates import reply_inst


class AsciiValueChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "char_to_code", "code_to_char", "sum_ascii",
            "char_to_code_v2", "code_to_char_v2",
        ])

        if variant == "char_to_code":
            char = random.choice(string.ascii_uppercase)
            code = ord(char)
            templates = [
                lambda c: f'What is the ASCII code for the letter "{c}"?',
                lambda c: f'Give the ASCII value of "{c}".',
                lambda c: f'What number represents "{c}" in ASCII?',
                lambda c: f'Find the ASCII code of the character "{c}".',
                lambda c: f'In ASCII, what is the numeric value of "{c}"?',
            ]
            prompt = random.choice(templates)(char) + " " + reply_inst()
            answer = str(code)

        elif variant == "char_to_code_v2":
            char = random.choice(string.ascii_lowercase)
            code = ord(char)
            templates = [
                lambda c: f'What is the ASCII code for the lowercase letter "{c}"?',
                lambda c: f'Determine the ASCII value of "{c}".',
                lambda c: f'What numeric ASCII code does the letter "{c}" have?',
                lambda c: f'Convert the character "{c}" to its ASCII number.',
                lambda c: f'Tell me the ASCII decimal value for "{c}".',
            ]
            prompt = random.choice(templates)(char) + " " + reply_inst()
            answer = str(code)

        elif variant == "code_to_char":
            code = random.randint(65, 90)  # A-Z
            char = chr(code)
            templates = [
                lambda n: f'What character has ASCII code {n}?',
                lambda n: f'Which letter corresponds to ASCII value {n}?',
                lambda n: f'Convert ASCII code {n} to its character.',
                lambda n: f'What letter does the ASCII number {n} represent?',
                lambda n: f'In ASCII, what character is code {n}?',
            ]
            prompt = random.choice(templates)(code) + " " + reply_inst()
            answer = char.lower()

        elif variant == "code_to_char_v2":
            code = random.randint(97, 122)  # a-z
            char = chr(code)
            templates = [
                lambda n: f'What lowercase letter has ASCII code {n}?',
                lambda n: f'ASCII code {n} represents which character?',
                lambda n: f'Determine the character for ASCII value {n}.',
                lambda n: f'Which letter is represented by ASCII code {n}?',
                lambda n: f'If the ASCII code is {n}, what is the letter?',
            ]
            prompt = random.choice(templates)(code) + " " + reply_inst()
            answer = char.lower()

        else:  # sum_ascii
            word = ''.join(random.choices(string.ascii_uppercase, k=random.randint(3, 5)))
            total = sum(ord(c) for c in word)
            templates = [
                lambda w: f'What is the sum of the ASCII values of all characters in "{w}"?',
                lambda w: f'Add together the ASCII codes of every letter in "{w}".',
                lambda w: f'Calculate the total ASCII value of the string "{w}".',
                lambda w: f'Find the sum of ASCII codes for each character in "{w}".',
                lambda w: f'Sum up the ASCII values of the letters in "{w}".',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = str(total)

        return prompt, answer
