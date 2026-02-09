"""Sorting challenges — sort letters or numbers."""

import random
import string
from typing import Tuple
from ..templates import SORTING_TEMPLATES, reply_inst


class SortingChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice(["sort_letters", "sort_numbers", "sort_reverse"])

        if variant == "sort_letters":
            length = random.randint(5, 8)
            letters = ''.join(random.choices(string.ascii_uppercase, k=length))
            sorted_letters = ''.join(sorted(letters))
            template = random.choice(SORTING_TEMPLATES["sort_letters"])
            prompt = template(letters) + " " + reply_inst()
            return prompt, sorted_letters.lower()

        elif variant == "sort_numbers":
            count = random.randint(5, 7)
            nums = list(set(random.randint(1, 99) for _ in range(count + 5)))[:count]
            while len(nums) < count:
                nums.append(random.randint(1, 99))
                nums = list(set(nums))
            sorted_nums = sorted(nums)
            template = random.choice(SORTING_TEMPLATES["sort_numbers"])
            prompt = template(', '.join(str(n) for n in nums)) + " " + reply_inst()
            return prompt, ', '.join(str(n) for n in sorted_nums)

        else:  # sort_reverse
            length = random.randint(5, 7)
            letters = ''.join(random.choices(string.ascii_uppercase, k=length))
            sorted_letters = ''.join(sorted(letters, reverse=True))
            template = random.choice(SORTING_TEMPLATES["sort_reverse"])
            prompt = template(letters) + " " + reply_inst()
            return prompt, sorted_letters.lower()
