"""
Prompt template randomization — makes challenges resistant to regex parsers.

Each challenge type has multiple phrasing variants. Templates are selected
randomly, making it impossible to write a reliable parser.
"""

import random

# ── Reply instructions (appended to every prompt) ─────

REPLY_INSTRUCTIONS = [
    "Reply with ONLY the answer, nothing else.",
    "Respond with just the answer.",
    "Give me only the answer.",
    "Your response should contain nothing but the answer.",
    "Write only the final answer.",
    "Output just the answer, no explanation.",
    "Answer with a single value only.",
    "Just the answer please, nothing more.",
]

def reply_inst():
    return random.choice(REPLY_INSTRUCTIONS)


# ── Reverse string templates ─────────────────────────

REVERSE_TEMPLATES = [
    lambda w: f"Reverse the following string: {w}. {reply_inst()}",
    lambda w: f"Write the characters of {w} in reverse order. {reply_inst()}",
    lambda w: f"Spell {w} backwards. {reply_inst()}",
    lambda w: f"If you flip the string {w} end-to-end, what do you get? {reply_inst()}",
    lambda w: f"Read {w} from right to left and write what you see. {reply_inst()}",
    lambda w: f"Take the word {w} and reverse every character. {reply_inst()}",
    lambda w: f"Starting from the last character to the first, rewrite {w}. {reply_inst()}",
    lambda w: f"What is the result of reversing all characters in {w}? {reply_inst()}",
]

# ── Math templates ────────────────────────────────────

MATH_TEMPLATES = {
    "add": [
        lambda a, b: f"What is {a} + {b}?",
        lambda a, b: f"Calculate the sum of {a} and {b}.",
        lambda a, b: f"Add {a} to {b}. What do you get?",
        lambda a, b: f"If you combine {a} and {b}, what is the total?",
        lambda a, b: f"Compute {a} plus {b}.",
    ],
    "subtract": [
        lambda a, b: f"What is {a} - {b}?",
        lambda a, b: f"Subtract {b} from {a}.",
        lambda a, b: f"If you take {b} away from {a}, what remains?",
        lambda a, b: f"Calculate {a} minus {b}.",
    ],
    "multiply": [
        lambda a, b: f"What is {a} × {b}?",
        lambda a, b: f"Multiply {a} by {b}.",
        lambda a, b: f"Calculate the product of {a} and {b}.",
        lambda a, b: f"What do you get when you multiply {a} times {b}?",
    ],
    "add_three": [
        lambda a, b, c: f"What is {a} + {b} + {c}?",
        lambda a, b, c: f"Add together {a}, {b}, and {c}.",
        lambda a, b, c: f"Find the sum of these three numbers: {a}, {b}, {c}.",
        lambda a, b, c: f"Calculate {a} plus {b} plus {c}.",
    ],
    "subtract_chain": [
        lambda a, b, c: f"What is {a} - {b} - {c}?",
        lambda a, b, c: f"Start with {a}, subtract {b}, then subtract {c}.",
        lambda a, b, c: f"Take {a}, remove {b}, then remove another {c}. What's left?",
    ],
}

# ── Letter position templates ─────────────────────────

LETTER_POS_TEMPLATES = [
    lambda w: f'If A=1, B=2, C=3, ... Z=26, what is the sum of the letter values in "{w}"?',
    lambda w: f'Assign each letter a number (A=1, B=2, through Z=26). Add up the values of all letters in "{w}".',
    lambda w: f'Using the mapping A→1, B→2, C→3, ..., Z→26, calculate the total value of the letters in "{w}".',
    lambda w: f'Each letter has a position in the alphabet (A=1, Z=26). What is the sum of positions for the letters in "{w}"?',
]

# ── ROT13 templates ───────────────────────────────────

ROT13_TEMPLATES = [
    lambda enc: f"Decode this ROT13-encoded string (each letter shifts 13 places back in the alphabet): {enc}",
    lambda enc: f"Apply ROT13 decoding to the text: {enc}",
    lambda enc: f"The following text was encoded with ROT13. Decode it: {enc}",
    lambda enc: f"Shift each letter in {enc} by 13 positions in the alphabet to decode it.",
]

# ── Pattern templates ─────────────────────────────────

PATTERN_TEMPLATES = [
    lambda seq: f"What comes next in this sequence: {seq}, ?",
    lambda seq: f"Find the next number: {seq}, ?",
    lambda seq: f"Continue this pattern: {seq}, ?",
    lambda seq: f"What number follows this sequence: {seq}, ?",
    lambda seq: f"Identify the next value in the series: {seq}, ?",
]

# ── Extract templates ─────────────────────────────────

EXTRACT_TEMPLATES = {
    2: [
        lambda mixed: f"Extract every 2nd letter from this string, starting from the 1st character: {mixed}",
        lambda mixed: f"Take every other character from {mixed}, beginning with the first.",
        lambda mixed: f"From the string {mixed}, pick characters at positions 1, 3, 5, 7... What do you get?",
    ],
    3: [
        lambda mixed: f"Extract every 3rd letter from this string, starting from the 1st character: {mixed}",
        lambda mixed: f"From {mixed}, take the 1st, 4th, 7th, 10th... characters.",
        lambda mixed: f"Pick every third character from {mixed}, starting at position 1.",
    ],
}

# ── Word math templates ───────────────────────────────

WORD_MATH_TEMPLATES = {
    "digit_to_word": [
        lambda a, b: f'What is {a} + {b}? Write the answer as a word (e.g., "twelve"), not a number.',
        lambda a, b: f"Add {a} and {b}. Spell out the answer as an English word.",
        lambda a, b: f"Calculate {a} + {b} and write the result as a word, not a digit.",
    ],
    "char_count": [
        lambda w: f'How many characters are in the string "{w}"?',
        lambda w: f'Count the total number of letters in "{w}".',
        lambda w: f'What is the length of the string "{w}"?',
    ],
    "vowel_count": [
        lambda w: f'How many vowels (A, E, I, O, U) are in "{w}"?',
        lambda w: f'Count the vowels in the string "{w}".',
        lambda w: f'In the text "{w}", how many letters are vowels (A, E, I, O, U)?',
    ],
    "digit_sum": [
        lambda n: f"What is the sum of the digits of {n}?",
        lambda n: f"Add up each individual digit in the number {n}.",
        lambda n: f"Take the number {n} and sum its digits together.",
    ],
}

# ── Caesar templates ──────────────────────────────────

CAESAR_TEMPLATES = [
    lambda enc, s: f"Decode this Caesar cipher (each letter is shifted {s} positions forward in the alphabet): {enc}\nShift each letter {s} positions BACKWARD to decode.",
    lambda enc, s: f"The text {enc} was encrypted with a Caesar shift of {s}. Decrypt it by shifting each letter back by {s}.",
    lambda enc, s: f"Apply a reverse Caesar shift of {s} to decode: {enc}",
    lambda enc, s: f"This message was encoded by shifting each letter forward by {s} in the alphabet: {enc}. What is the original text?",
]

# ── Sorting templates ─────────────────────────────────

SORTING_TEMPLATES = {
    "sort_letters": [
        lambda w: f"Sort these letters in alphabetical order: {w}",
        lambda w: f"Arrange the letters {w} from A to Z.",
        lambda w: f"Put these letters in alphabetical sequence: {w}",
    ],
    "sort_numbers": [
        lambda nums: f"Sort these numbers from smallest to largest: {nums}",
        lambda nums: f"Arrange in ascending order: {nums}",
        lambda nums: f"Put these numbers in order from lowest to highest: {nums}",
    ],
    "sort_reverse": [
        lambda w: f"Sort these letters in REVERSE alphabetical order (Z first, A last): {w}",
        lambda w: f"Arrange the letters {w} from Z to A.",
        lambda w: f"Put these letters in reverse alphabetical order: {w}",
    ],
}

# ── Counting templates ────────────────────────────────

COUNTING_TEMPLATES = {
    "count_letter": [
        lambda t, text: f'How many times does the letter "{t}" appear in "{text}"?',
        lambda t, text: f'Count the occurrences of "{t}" in the string "{text}".',
        lambda t, text: f'In "{text}", how many "{t}" characters are there?',
    ],
    "count_consonants": [
        lambda w: f'How many consonants (non-vowel letters) are in "{w}"?',
        lambda w: f'Count all consonants in the string "{w}".',
        lambda w: f'In "{w}", how many letters are NOT vowels?',
    ],
    "count_digits": [
        lambda t, d: f'How many times does the digit "{t}" appear in "{d}"?',
        lambda t, d: f'Count how often "{t}" occurs in the number string "{d}".',
    ],
    "count_upper": [
        lambda text: f'How many UPPERCASE letters are in "{text}"?',
        lambda text: f'Count the capital letters in "{text}".',
        lambda text: f'In the mixed-case string "{text}", how many characters are uppercase?',
    ],
}

# ── Transform templates ───────────────────────────────

TRANSFORM_TEMPLATES = {
    "remove_vowels": [
        lambda w: f'Remove all vowels (A, E, I, O, U) from "{w}".',
        lambda w: f'Delete every vowel from the string "{w}". What remains?',
        lambda w: f'Strip out A, E, I, O, and U from "{w}".',
    ],
    "remove_consonants": [
        lambda w: f'Remove all consonants from "{w}" and keep only the vowels (A, E, I, O, U).',
        lambda w: f'Extract only the vowels from "{w}".',
        lambda w: f'From the string "{w}", delete every consonant and keep only vowels.',
    ],
    "first_letters": [
        lambda s: f'What do the first letters of each word spell: "{s}"?',
        lambda s: f'Take the initial letter of every word in "{s}" and combine them.',
        lambda s: f'Form an acronym from: "{s}".',
    ],
    "last_letters": [
        lambda s: f'What do the LAST letters of each word spell: "{s}"?',
        lambda s: f'Take the final letter of each word in "{s}" and combine them.',
        lambda s: f'Extract the ending letter from every word in "{s}" and join them.',
    ],
}

# ── Binary templates ──────────────────────────────────

BINARY_TEMPLATES = {
    "binary_to_decimal": [
        lambda b: f"Convert binary {b} to decimal.",
        lambda b: f"What is the decimal value of the binary number {b}?",
        lambda b: f"Express {b} (binary) as a base-10 number.",
    ],
    "decimal_to_binary": [
        lambda n: f"Convert the decimal number {n} to binary.",
        lambda n: f"What is {n} in binary?",
        lambda n: f"Write {n} as a binary number (no 0b prefix).",
    ],
    "digit_sum": [
        lambda n: f"What is the sum of all digits in {n}?",
        lambda n: f"Add each digit of {n} together.",
        lambda n: f"Calculate the digit sum of {n}.",
    ],
}
