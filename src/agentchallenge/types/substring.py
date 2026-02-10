"""Substring challenge — extract substrings or find positions."""

import random
import string
from typing import Tuple
from ..templates import reply_inst


def _random_word(min_len=8, max_len=14):
    return ''.join(random.choices(string.ascii_uppercase, k=random.randint(min_len, max_len)))


class SubstringChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "extract_range", "extract_range_v2", "find_position",
            "first_n", "last_n",
        ])

        word = _random_word()

        if variant == "extract_range":
            # 1-indexed range
            max_start = len(word) - 3
            start = random.randint(1, max(1, max_start))
            end = min(start + random.randint(2, 4), len(word))
            substr = word[start - 1:end]
            templates = [
                lambda w, s, e: f'What are characters {s} through {e} of "{w}"? (1-indexed)',
                lambda w, s, e: f'Extract characters at positions {s} to {e} from "{w}".',
                lambda w, s, e: f'In the string "{w}", give me the substring from position {s} to {e} (inclusive, 1-indexed).',
                lambda w, s, e: f'From "{w}", what is the substring spanning positions {s}–{e}?',
                lambda w, s, e: f'Take characters {s} through {e} of the string "{w}".',
            ]
            prompt = random.choice(templates)(word, start, end) + " " + reply_inst()
            answer = substr.lower()

        elif variant == "extract_range_v2":
            max_start = len(word) - 2
            start = random.randint(2, max(2, max_start))
            end = min(start + random.randint(1, 3), len(word))
            substr = word[start - 1:end]
            templates = [
                lambda w, s, e: f'From "{w}", extract the characters from position {s} to position {e}.',
                lambda w, s, e: f'Give me characters at positions {s} through {e} in "{w}" (1-indexed).',
                lambda w, s, e: f'What substring do you get from positions {s} to {e} of "{w}"?',
                lambda w, s, e: f'Pull out characters {s}–{e} from the string "{w}".',
                lambda w, s, e: f'Read positions {s} through {e} of "{w}" and write what you see.',
            ]
            prompt = random.choice(templates)(word, start, end) + " " + reply_inst()
            answer = substr.lower()

        elif variant == "find_position":
            target = random.choice(word)
            pos = word.index(target) + 1  # 1-indexed
            templates = [
                lambda w, t: f'At what position (1-indexed) does the letter "{t}" first appear in "{w}"?',
                lambda w, t: f'Find the position of the first occurrence of "{t}" in "{w}" (1-indexed).',
                lambda w, t: f'In "{w}", at what 1-indexed position is the first "{t}"?',
                lambda w, t: f'What is the 1-indexed position of the first "{t}" in the string "{w}"?',
                lambda w, t: f'Where does "{t}" first appear in "{w}"? Give the 1-indexed position.',
            ]
            prompt = random.choice(templates)(word, target) + " " + reply_inst()
            answer = str(pos)

        elif variant == "first_n":
            n = random.randint(2, min(5, len(word)))
            substr = word[:n]
            templates = [
                lambda w, k: f'What are the first {k} characters of "{w}"?',
                lambda w, k: f'Give me the first {k} letters of the string "{w}".',
                lambda w, k: f'Extract the opening {k} characters from "{w}".',
                lambda w, k: f'Take the first {k} characters of "{w}". What do you get?',
                lambda w, k: f'Read the first {k} characters of "{w}".',
            ]
            prompt = random.choice(templates)(word, n) + " " + reply_inst()
            answer = substr.lower()

        else:  # last_n
            n = random.randint(2, min(5, len(word)))
            substr = word[-n:]
            templates = [
                lambda w, k: f'What are the last {k} characters of "{w}"?',
                lambda w, k: f'Give me the final {k} letters of the string "{w}".',
                lambda w, k: f'Extract the last {k} characters from "{w}".',
                lambda w, k: f'What do the last {k} characters of "{w}" spell?',
                lambda w, k: f'Read the ending {k} characters of "{w}".',
            ]
            prompt = random.choice(templates)(word, n) + " " + reply_inst()
            answer = substr.lower()

        return prompt, answer
