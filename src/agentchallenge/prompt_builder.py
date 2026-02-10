"""
Dynamic prompt assembly — creates combinatorially explosive prompt variations.

Instead of fixed template lambdas, this module assembles prompts from 
interchangeable word pools and structural patterns. This makes regex-based
scripted solvers infeasible even with full source code access.

Combinatorial space per challenge: ~10,000+ unique phrasings.
"""

import random
import string
import time


# ── Word Pools ────────────────────────────────────────

VERBS_REVERSE = [
    "Reverse", "Flip", "Mirror", "Invert", "Spell backwards",
    "Write in reverse order", "Read backwards", "Turn around",
]

VERBS_COMPUTE = [
    "Calculate", "Compute", "Find", "Determine", "Work out",
    "Figure out", "Evaluate", "Solve for", "What is",
]

VERBS_DECODE = [
    "Decode", "Decipher", "Decrypt", "Unscramble", "Reveal",
    "Uncover", "Crack", "Translate back",
]

VERBS_EXTRACT = [
    "Extract", "Pull out", "Pick", "Select", "Grab",
    "Take", "Isolate", "Get",
]

VERBS_COUNT = [
    "Count", "Tally", "How many", "Find the number of",
    "Determine how many", "Total up the",
]

VERBS_SORT = [
    "Sort", "Arrange", "Order", "Organize", "Rearrange",
    "Put in order", "Alphabetize", "Sequence",
]

VERBS_CONVERT = [
    "Convert", "Transform", "Change", "Translate", "Express",
    "Rewrite", "Represent",
]

CONNECTORS = [
    "then", "and then", "next", "after that",
    "followed by", "subsequently", "once done",
    "with that result", "taking the output",
]

RESULT_REFS = [
    "the result", "what you get", "the output",
    "your answer", "the value you computed",
    "the intermediate result", "that",
]

# ── Structural Wrappers ──────────────────────────────

WRAPPERS = [
    "{task}",
    "Your task: {task}",
    "Instruction: {task}",
    "Complete this: {task}",
    "Please {task_lower}",
    "I need you to {task_lower}",
    "Can you {task_lower}",
    "Here's a puzzle: {task}",
    "Challenge: {task}",
    "Quick task — {task_lower}",
]

# ── Decoy Injections ─────────────────────────────────
# Irrelevant strings that regex parsers must filter out.
# These appear between the instruction and the data.

def _rand_hex():
    return ''.join(random.choices('0123456789abcdef', k=random.randint(6, 12)))

def _rand_time():
    return f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

DECOY_GENERATORS = [
    lambda: "",  # No decoy (50% of the time, duplicate for weight)
    lambda: "",
    lambda: "",
    lambda: f" (Session {_rand_hex()})",
    lambda: f" [ref:{_rand_hex()}]",
    lambda: f" — task #{random.randint(1000, 9999)}",
    lambda: f" (timestamp: {_rand_time()})",
    lambda: f" [attempt {random.randint(1, 5)}]",
]


# ── Reply Instructions ────────────────────────────────

REPLY_PARTS_A = [
    "Reply with", "Respond with", "Give me", "Output",
    "Write", "Return", "Answer with", "Send back",
    "Provide", "Type",
]

REPLY_PARTS_B = [
    "ONLY the answer", "just the answer", "nothing but the answer",
    "the answer alone", "only the final result", "just the result",
    "a single value only", "the answer, nothing more",
]

REPLY_PARTS_C = [
    ".", ", nothing else.", "— no explanation.",
    ". No extra text.", ". Keep it brief.",
    ". That's it.", ". Just that.",
]

def dynamic_reply_inst():
    """Generate a reply instruction from combinatorial parts."""
    a = random.choice(REPLY_PARTS_A)
    b = random.choice(REPLY_PARTS_B)
    c = random.choice(REPLY_PARTS_C)
    return f"{a} {b}{c}"


# ── Prompt Assembly ───────────────────────────────────

def build_prompt(task_text: str) -> str:
    """
    Wrap a task description in dynamic structural variation.
    
    Takes a plain task like "Reverse the string HELLO" and wraps it
    with random structural elements, decoys, and reply instructions.
    
    Returns a complete prompt string.
    """
    # Apply wrapper
    wrapper = random.choice(WRAPPERS)
    if "{task_lower}" in wrapper:
        prompt = wrapper.replace("{task_lower}", task_text[0].lower() + task_text[1:] if task_text else task_text)
    else:
        prompt = wrapper.replace("{task}", task_text)
    
    # Inject decoy
    decoy = random.choice(DECOY_GENERATORS)()
    
    # Add reply instruction
    reply = dynamic_reply_inst()
    
    # Randomize assembly order
    order = random.choice(["normal", "reply_first"])
    if order == "reply_first" and random.random() < 0.3:
        return f"{reply} {prompt}{decoy}"
    else:
        return f"{prompt}{decoy} {reply}"


def verb(category: str) -> str:
    """Get a random verb for the given category."""
    pools = {
        "reverse": VERBS_REVERSE,
        "compute": VERBS_COMPUTE,
        "decode": VERBS_DECODE,
        "extract": VERBS_EXTRACT,
        "count": VERBS_COUNT,
        "sort": VERBS_SORT,
        "convert": VERBS_CONVERT,
    }
    return random.choice(pools.get(category, VERBS_COMPUTE))


def connector() -> str:
    """Get a random connector word."""
    return random.choice(CONNECTORS)


def result_ref() -> str:
    """Get a random way to refer to an intermediate result."""
    return random.choice(RESULT_REFS)
