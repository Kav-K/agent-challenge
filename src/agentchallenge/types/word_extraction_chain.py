"""Word extraction chain — extract from words in a sentence, then transform."""

import random
import string
from typing import Tuple
from ..templates import reply_inst

# Short random words for generating sentences
def _random_word(length=None):
    if length is None:
        length = random.randint(4, 8)
    consonants = "bcdfghjklmnprstvwxyz"
    vowels = "aeiou"
    result = []
    for i in range(length):
        if i % 2 == 0:
            result.append(random.choice(consonants))
        else:
            result.append(random.choice(vowels))
    return ''.join(result).capitalize()


TEMPLATES = [
    lambda desc: f"{desc} {reply_inst()}",
    lambda desc: f"Follow these steps: {desc} {reply_inst()}",
    lambda desc: f"Work through this: {desc} {reply_inst()}",
    lambda desc: f"Complete this task: {desc} {reply_inst()}",
]


class WordExtractionChainChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice([
            "first_letters_sort",
            "last_letters_reverse",
            "nth_letters_join",
            "first_letters_reverse",
            "count_vowels_per_word",
        ])

        num_words = random.randint(5, 7)
        words = [_random_word() for _ in range(num_words)]
        sentence = ' '.join(words)

        if variant == "first_letters_sort":
            letters = [w[0].lower() for w in words]
            answer = ', '.join(sorted(letters))
            desc = f"Take the first letter of each word in \"{sentence}\", then sort them alphabetically."

        elif variant == "last_letters_reverse":
            letters = [w[-1].lower() for w in words]
            answer = ', '.join(reversed(letters))
            desc = f"Take the last letter of each word in \"{sentence}\", then list them in reverse order."

        elif variant == "nth_letters_join":
            n = 2  # 2nd letter
            letters = []
            for w in words:
                if len(w) >= n:
                    letters.append(w[n-1].lower())
            answer = ''.join(letters)
            desc = f"Extract the 2nd letter from each word in \"{sentence}\" and join them together into one string."

        elif variant == "first_letters_reverse":
            letters = [w[0].lower() for w in words]
            answer = ''.join(reversed(letters))
            desc = f"Take the first letter of each word in \"{sentence}\" and write them in reverse order as a single string."

        elif variant == "count_vowels_per_word":
            counts = []
            for w in words:
                count = sum(1 for c in w.lower() if c in 'aeiou')
                counts.append(str(count))
            answer = ', '.join(counts)
            desc = f"Count the number of vowels in each word of \"{sentence}\" and list the counts separated by commas."

        template = random.choice(TEMPLATES)
        prompt = template(desc)
        return prompt, answer.lower()
