"""
Knowledge + arithmetic: world-knowledge facts with stated values + single operation + modulo.

Humans can't solve without searching the facts.
GPT-5.2: 100% | GPT-4o: ~85-93%

Hard tier — the knowledge layer blocks humans, the modulo blocks weaker models.
"""
import random
from typing import Tuple
from ..templates import reply_inst


FACTS = [
    ("The atomic number of oxygen is {v}", 8),
    ("The atomic number of carbon is {v}", 6),
    ("The atomic number of nitrogen is {v}", 7),
    ("The atomic number of neon is {v}", 10),
    ("The atomic number of sodium is {v}", 11),
    ("The atomic number of iron is {v}", 26),
    ("The atomic number of copper is {v}", 29),
    ("The atomic number of gold is {v}", 79),
    ("The atomic number of silver is {v}", 47),
    ("There are {v} planets in our solar system", 8),
    ("There are {v} continents on Earth", 7),
    ("A hexagon has {v} sides", 6),
    ("A pentagon has {v} sides", 5),
    ("A standard guitar has {v} strings", 6),
    ("A violin has {v} strings", 4),
    ("The English alphabet has {v} letters", 26),
    ("An adult human has {v} teeth", 32),
    ("The US flag has {v} stripes", 13),
    ("A spider has {v} legs", 8),
    ("An insect has {v} legs", 6),
    ("There are {v} Harry Potter books in the main series", 7),
    ("Brazil has won {v} FIFA World Cups", 5),
    ("The Olympic flag has {v} rings", 5),
    ("A standard die has {v} total dots across all faces", 21),
    ("There are {v} ounces in a pound", 16),
    ("There are {v} inches in a foot", 12),
    ("A byte has {v} bits", 8),
    ("Beethoven composed {v} symphonies", 9),
    ("A soccer team fields {v} players", 11),
    ("A basketball team has {v} players on court", 5),
    ("A golf course has {v} holes", 18),
    ("A standard deck has {v} cards", 52),
    ("A marathon is approximately {v} miles", 26),
    ("A chess board has {v} squares", 64),
    ("There are {v} hours in a day", 24),
    ("A human cell has {v} chromosomes", 46),
    ("A piano has {v} keys", 88),
]


class KnowledgeMathChallenge:
    @staticmethod
    def generate() -> Tuple[str, str]:
        f1, f2 = random.sample(FACTS, 2)
        tmpl1, val1 = f1
        tmpl2, val2 = f2
        sent1 = tmpl1.format(v=val1)
        sent2 = tmpl2.format(v=val2)
        m = random.randint(3, 9)

        ops = []
        if val1 + val2 < 200:
            ops.append("add")
        if val1 * val2 < 5000:
            ops.append("mul")
        if val1 != val2:
            ops.append("sub")

        op = random.choice(ops)

        if op == "add":
            intermediate = val1 + val2
            op_text = random.choice([
                "Add these two numbers",
                "Sum these two numbers",
                "Add them together",
            ])
        elif op == "mul":
            intermediate = val1 * val2
            op_text = random.choice([
                "Multiply these two numbers",
                "Find the product of these two numbers",
            ])
        else:
            if val1 >= val2:
                intermediate = val1 - val2
                op_text = "Subtract the second from the first"
            else:
                intermediate = val2 - val1
                op_text = "Subtract the first from the second"

        result = intermediate % m
        prompt = f"{sent1} and {sent2}. {op_text}, then find the remainder when divided by {m}. {reply_inst()}"
        return prompt, str(result)
