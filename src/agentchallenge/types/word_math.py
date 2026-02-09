"""Word math challenge — spell out a number from letter codes or vice versa."""

import random
from typing import Tuple

# Map numbers to words
NUM_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
    18: "eighteen", 19: "nineteen", 20: "twenty",
}


class WordMathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice(["digit_to_word", "word_count", "char_count"])

        if variant == "digit_to_word":
            # "What is 7 + 8 written as a word?"
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            total = a + b
            prompt = (
                f"What is {a} + {b}? Write the answer as a word (e.g., \"twelve\"), not a number. "
                f"Reply with ONLY the word, nothing else."
            )
            return prompt, NUM_WORDS[total]

        elif variant == "word_count":
            # "How many words are in this sentence?"
            sentences = [
                ("The quick brown fox jumps", 5),
                ("A robot walked into a bar", 6),
                ("She sells sea shells by the shore", 7),
                ("I think therefore I am", 5),
                ("To be or not to be", 6),
                ("All that glitters is not gold", 6),
                ("The cat sat on the mat", 6),
                ("One small step for a man", 6),
                ("Every cloud has a silver lining", 6),
                ("Time flies like an arrow", 5),
            ]
            sentence, count = random.choice(sentences)
            prompt = (
                f"How many words are in this sentence: \"{sentence}\"? "
                f"Reply with ONLY the number, nothing else."
            )
            return prompt, str(count)

        else:
            # "How many characters (letters only) in HELLO?"
            words = ["PYTHON", "CYBER", "ROBOT", "AGENT", "CLOUD",
                     "MAGIC", "POWER", "LIGHT", "OCEAN", "GUARD"]
            word = random.choice(words)
            prompt = (
                f"How many letters are in the word \"{word}\"? "
                f"Reply with ONLY the number, nothing else."
            )
            return prompt, str(len(word))
