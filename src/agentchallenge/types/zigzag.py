"""Zigzag cipher challenge — read a string in zigzag (rail fence) pattern."""

import random
import string
from typing import Tuple
from ..templates import reply_inst


def _random_word(min_len=6, max_len=10):
    return ''.join(random.choices(string.ascii_uppercase, k=random.randint(min_len, max_len)))


def _zigzag_encode(text: str, rows: int) -> str:
    """Encode text using rail fence cipher with given number of rows."""
    if rows <= 1 or rows >= len(text):
        return text
    rails = [[] for _ in range(rows)]
    row, direction = 0, 1
    for ch in text:
        rails[row].append(ch)
        if row == 0:
            direction = 1
        elif row == rows - 1:
            direction = -1
        row += direction
    return ''.join(''.join(rail) for rail in rails)


class ZigzagChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "encode_2rows", "encode_3rows", "encode_2rows_v2",
            "encode_3rows_v2", "encode_2rows_v3",
        ])

        if variant in ("encode_2rows", "encode_2rows_v2", "encode_2rows_v3"):
            word = _random_word(6, 10)
            rows = 2
        else:
            word = _random_word(7, 12)
            rows = 3

        result = _zigzag_encode(word, rows)

        if variant == "encode_2rows":
            templates = [
                lambda w, r: f'Write "{w}" in a zigzag pattern with {r} rows, then read each row left to right.',
                lambda w, r: f'Apply the rail fence cipher to "{w}" with {r} rails. What is the result?',
                lambda w, r: f'Encode "{w}" using a zigzag pattern with {r} rows (read rows left to right).',
                lambda w, r: f'Place the letters of "{w}" in a zigzag across {r} rows, then read row by row.',
                lambda w, r: f'Using a {r}-row zigzag pattern, rearrange "{w}" by reading each row left to right.',
            ]
        elif variant == "encode_2rows_v2":
            templates = [
                lambda w, r: f'The string "{w}" is written in a zigzag across {r} rows. Reading row by row gives what?',
                lambda w, r: f'Distribute "{w}" across {r} rows in zigzag fashion. What string do you get reading rows sequentially?',
                lambda w, r: f'Rail fence cipher: encode "{w}" with {r} rails. What is the output?',
                lambda w, r: f'Zigzag "{w}" over {r} rows and concatenate the rows.',
                lambda w, r: f'Write "{w}" alternating between {r} rows, then read all rows left to right.',
            ]
        elif variant == "encode_2rows_v3":
            templates = [
                lambda w, r: f'Apply a {r}-row zigzag encoding to "{w}". Give the encoded string.',
                lambda w, r: f'Rearrange "{w}" using a rail fence with {r} rails. What do you get?',
                lambda w, r: f'Place characters of "{w}" in a {r}-row zigzag and read across.',
                lambda w, r: f'Encode "{w}" with a zigzag cipher using {r} rows.',
                lambda w, r: f'For the string "{w}", perform a {r}-row rail fence cipher encode.',
            ]
        elif variant == "encode_3rows":
            templates = [
                lambda w, r: f'Write "{w}" in a zigzag pattern with {r} rows, then read each row left to right.',
                lambda w, r: f'Apply the rail fence cipher to "{w}" with {r} rails. What is the result?',
                lambda w, r: f'Encode "{w}" using a zigzag pattern with {r} rows (read rows left to right).',
                lambda w, r: f'Place the letters of "{w}" in a zigzag across {r} rows, then read row by row.',
                lambda w, r: f'Using a {r}-row zigzag pattern, rearrange "{w}" by reading each row left to right.',
            ]
        else:  # encode_3rows_v2
            templates = [
                lambda w, r: f'Rail fence cipher: encode "{w}" using {r} rows. Give the result.',
                lambda w, r: f'Distribute "{w}" in a zigzag across {r} rows, then concatenate each row.',
                lambda w, r: f'Apply a {r}-row rail fence encode to "{w}". What string do you get?',
                lambda w, r: f'Write "{w}" zigzagging across {r} rows and read off each row.',
                lambda w, r: f'Perform a zigzag cipher on "{w}" with {r} rows. What is the encoded text?',
            ]

        prompt = random.choice(templates)(word, rows) + " " + reply_inst()
        return prompt, result.lower()
