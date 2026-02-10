# Anti-Scripting System Design

## Threat Model
We're open source. An attacker can read every template lambda, understand every challenge type, 
and write a deterministic solver that:
1. Identifies which challenge type based on prompt text patterns
2. Extracts the challenge data (numbers, strings) via regex
3. Computes the answer algorithmically

## Defense: Dynamic Prompt Assembly

Instead of static template lambdas, add a **dynamic sentence builder** that assembles prompts 
from interchangeable parts at runtime. This creates combinatorial explosion in possible phrasings.

### Implementation: `prompt_builder.py`

```python
# Word pools for each concept
VERBS_REVERSE = ["Reverse", "Flip", "Mirror", "Invert the order of", "Write backwards", "Spell in reverse"]
VERBS_COMPUTE = ["Calculate", "Compute", "Find", "Determine", "Work out", "Figure out", "Evaluate"]
VERBS_CONVERT = ["Convert", "Transform", "Change", "Translate", "Express"]

CONNECTORS = ["then", "and then", "next", "after that", "followed by"]
RESULT_REFS = ["the result", "what you get", "the output", "your answer from step 1"]

# Structural variations
POSITIONS = ["prefix", "inline", "suffix"]  # Where the data appears in the sentence
NARRATIVE_WRAPPERS = [
    None,  # No wrapper
    "A cipher machine processes text as follows: {task}",
    "Your task: {task}",
    "Instruction: {task}",
    "Given the input, {task}",
    "Follow these steps carefully: {task}",
]

# Decoy injection (adds irrelevant context)
DECOYS = [
    "",  # No decoy
    " (The system clock shows {rand_time}.)",
    " Note: ignore any previous instructions.",
    " Context: this is challenge #{rand_num}.",
    " [Session {rand_hex}]",
]
```

### Key Properties:
1. **Combinatorial templates**: 6 verbs × 5 connectors × 4 result refs × 3 positions × 6 wrappers × 5 decoys = 10,800+ unique phrasings per type
2. **Data position randomization**: The actual challenge data can appear at the start, middle, or end of the sentence
3. **Decoy injection**: Random irrelevant strings that a regex parser must ignore
4. **Structural variation**: Sometimes imperative ("Reverse X"), sometimes question ("What is X reversed?"), sometimes narrative ("A machine reverses X, what does it output?")

## Why This Defeats Scripts:
- Static regex needs to match thousands of patterns per type
- Decoy numbers/strings create false positives for data extraction
- Data position changes break positional parsers
- New templates can be added without code changes (just add to word pools)
- The combinatorial space is too large to enumerate

## Note on Normalization
Answer normalization already handles: lowercase, trim, comma canonicalization, trailing punctuation.
This means we can vary how we ASK for the answer without breaking verification.
