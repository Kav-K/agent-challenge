"""Sorting challenges — sort letters or numbers."""

import random
import string
from typing import Tuple


class SortingChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        variant = random.choice(["sort_letters", "sort_numbers", "sort_reverse"])

        if variant == "sort_letters":
            length = random.randint(5, 8)
            letters = ''.join(random.choices(string.ascii_uppercase, k=length))
            sorted_letters = ''.join(sorted(letters))
            prompt = (
                f"Sort these letters in alphabetical order: {letters}\n"
                f"Reply with ONLY the sorted letters as one word, nothing else."
            )
            return prompt, sorted_letters.lower()

        elif variant == "sort_numbers":
            count = random.randint(5, 7)
            nums = [random.randint(1, 99) for _ in range(count)]
            # Ensure no duplicates
            nums = list(set(nums))
            while len(nums) < count:
                nums.append(random.randint(1, 99))
                nums = list(set(nums))
            sorted_nums = sorted(nums)
            prompt = (
                f"Sort these numbers from smallest to largest: {', '.join(str(n) for n in nums)}\n"
                f"Reply with ONLY the sorted numbers separated by commas, nothing else."
            )
            return prompt, ', '.join(str(n) for n in sorted_nums)

        else:  # sort_reverse
            length = random.randint(5, 7)
            letters = ''.join(random.choices(string.ascii_uppercase, k=length))
            sorted_letters = ''.join(sorted(letters, reverse=True))
            prompt = (
                f"Sort these letters in REVERSE alphabetical order (Z first, A last): {letters}\n"
                f"Reply with ONLY the sorted letters as one word, nothing else."
            )
            return prompt, sorted_letters.lower()
