"""Reverse string challenge — reverse a given word or phrase."""

import random
from typing import Tuple

# Common words that are clear when reversed
WORDS = [
    "PYTHON", "SECURITY", "NETWORK", "FIREWALL", "TERMINAL",
    "CHALLENGE", "KEYBOARD", "MONITOR", "GATEWAY", "PROTOCOL",
    "DATABASE", "ENCRYPT", "BROWSER", "DIGITAL", "CAPTURE",
    "RUNTIME", "STORAGE", "MACHINE", "COMPILE", "PACKAGE",
    "SCANNER", "HACKER", "SERVER", "CLIENT", "ROUTER",
    "SYSTEM", "ACCESS", "DEFEND", "ATTACK", "SHIELD",
    "BINARY", "KERNEL", "DOCKER", "STREAM", "BRIDGE",
    "SOCKET", "BUFFER", "CIPHER", "DEPLOY", "TOGGLE",
    "ANCHOR", "BEACON", "MATRIX", "PORTAL", "VECTOR",
    "CARBON", "FALCON", "GARDEN", "HARBOR", "JACKET",
]


class ReverseStringChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        word = random.choice(WORDS)
        reversed_word = word[::-1]
        prompt = f"Reverse the following string (reply with ONLY the reversed text, nothing else): {word}"
        return prompt, reversed_word.lower()
