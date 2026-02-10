"""String length challenge — count characters in a randomly generated string."""

import random
import string
from typing import Tuple
from ..templates import reply_inst


def _random_word(min_len=4, max_len=10):
    return ''.join(random.choices(string.ascii_uppercase, k=random.randint(min_len, max_len)))


def _random_phrase():
    """Generate a phrase with spaces."""
    words = [_random_word(3, 6) for _ in range(random.randint(2, 4))]
    return ' '.join(words)


class StringLengthChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "count_all", "count_all_v2", "count_no_spaces",
            "count_specific", "count_specific_v2",
        ])

        if variant == "count_all":
            word = _random_word(4, 12)
            templates = [
                lambda w: f'How many characters are in "{w}"?',
                lambda w: f'Count the characters in the string "{w}".',
                lambda w: f'What is the length of "{w}"?',
                lambda w: f'How long is the string "{w}" in characters?',
                lambda w: f'Tell me how many characters "{w}" contains.',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = str(len(word))

        elif variant == "count_all_v2":
            word = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(5, 12)))
            templates = [
                lambda w: f'How many characters (letters and digits) are in "{w}"?',
                lambda w: f'What is the total character count of "{w}"?',
                lambda w: f'Count every character in "{w}".',
                lambda w: f'Determine the length of "{w}".',
                lambda w: f'"{w}" has how many characters?',
            ]
            prompt = random.choice(templates)(word) + " " + reply_inst()
            answer = str(len(word))

        elif variant == "count_no_spaces":
            phrase = _random_phrase()
            no_spaces = len(phrase.replace(' ', ''))
            templates = [
                lambda p: f'How many characters are in "{p}", not counting spaces?',
                lambda p: f'Count the non-space characters in "{p}".',
                lambda p: f'In "{p}", how many characters are there excluding spaces?',
                lambda p: f'Ignoring spaces, what is the character count of "{p}"?',
                lambda p: f'How many letters are in "{p}" if you skip spaces?',
            ]
            prompt = random.choice(templates)(phrase) + " " + reply_inst()
            answer = str(no_spaces)

        elif variant == "count_specific":
            word = _random_word(8, 14)
            target = random.choice(word)
            count = word.count(target)
            templates = [
                lambda w, t: f'How many times does the letter "{t}" appear in "{w}"?',
                lambda w, t: f'Count the occurrences of "{t}" in "{w}".',
                lambda w, t: f'In the string "{w}", how many "{t}" characters are there?',
                lambda w, t: f'Find the number of "{t}" letters in "{w}".',
                lambda w, t: f'How often does "{t}" show up in "{w}"?',
            ]
            prompt = random.choice(templates)(word, target) + " " + reply_inst()
            answer = str(count)

        else:  # count_specific_v2
            word = ''.join(random.choices(string.ascii_uppercase, k=random.randint(8, 15)))
            target = random.choice(list(set(word)))
            count = word.count(target)
            templates = [
                lambda w, t: f'Scan "{w}" and count every "{t}".',
                lambda w, t: f'What is the frequency of "{t}" in the string "{w}"?',
                lambda w, t: f'Tell me the count of "{t}" in "{w}".',
                lambda w, t: f'How many "{t}" letters can you find in "{w}"?',
                lambda w, t: f'Tally the "{t}" characters in "{w}".',
            ]
            prompt = random.choice(templates)(word, target) + " " + reply_inst()
            answer = str(count)

        return prompt, answer
