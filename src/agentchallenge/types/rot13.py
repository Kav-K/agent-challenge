"""ROT13 decode challenge — decode a ROT13-encoded word."""

import random
from typing import Tuple

# Words that produce clear ROT13 results
WORDS = [
    "HELLO", "WORLD", "AGENT", "ROBOT", "CLOUD", "SMART",
    "BRAIN", "LOGIC", "CYBER", "PIXEL", "TOKEN", "BLOCK",
    "MAGIC", "POWER", "SPEED", "LIGHT", "GUARD", "MOUNT",
    "FLAME", "STONE", "OCEAN", "RIVER", "STORM", "EAGLE",
    "BRAVE", "LANCE", "QUEST", "FORGE", "DROID", "PULSE",
]


def _rot13(text: str) -> str:
    result = []
    for c in text:
        if 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
        elif 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
        else:
            result.append(c)
    return ''.join(result)


class Rot13Challenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        word = random.choice(WORDS)
        encoded = _rot13(word)
        prompt = (
            f"Decode this ROT13-encoded string (each letter shifts 13 places back in the alphabet): {encoded}\n"
            f"Reply with ONLY the decoded word, nothing else."
        )
        return prompt, word.lower()
