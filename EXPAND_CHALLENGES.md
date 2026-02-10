# Task: Massively Expand Challenge Types

You are working on the agent-challenge library at /opt/agent-challenge/.

## Current State
- 12 challenge types across 3 difficulty tiers (easy/medium/hard)
- Templates in `src/agentchallenge/templates.py` (~104 template lambdas)  
- Type implementations in `src/agentchallenge/types/*.py`
- JS port in `src/agentchallenge.js` (must stay in sync)
- Tests in `run_tests.py` (currently 93/93 passing)

## What To Do

### 1. Add MORE prompt templates to every existing type
Each type currently has 3-8 templates. Add 5-10 MORE to each type in `templates.py`.
Templates should use varied natural language — different sentence structures, phrasings, imperative vs question form.

### 2. Add harder variants within existing types
- **reverse_string**: Add sentence-reversal (reverse word order), partial reversal (reverse first half only)
- **simple_math**: Add 3-operand expressions, mixed operations (add then multiply), modulo
- **pattern**: Add Fibonacci-like, triangular numbers, prime sequences, decreasing sequences
- **counting**: Add "count digits", "count uppercase vs lowercase", "count specific letter"
- **rot13**: Already good, but add more template variety
- **letter_position**: Add "what letter is at position N in the alphabet" (reverse lookup)
- **extract_letters**: Add "every 3rd character", "last N characters", "characters at even positions"
- **sorting**: Add "sort words alphabetically", "sort by string length", "reverse sort"
- **binary**: Add "decimal to binary", "binary addition", "hex to decimal"
- **caesar**: Add variable shift discovery ("the shift is the first digit in the string")
- **word_math**: Add "digit sum", "number of digits", multi-step word problems
- **transform**: Add "swap case", "remove consonants", "interleave two strings", "acronym from sentence"

### 3. Update the JS port
After modifying Python types and templates, you MUST update `src/agentchallenge.js` to match.
The JS port has all challenge generation inline. Search for each type name and add matching logic.

### 4. Run tests
After ALL changes: `PYTHONPATH=src python3 run_tests.py`
All tests must pass. If a test fails, fix it.

Also run: `node --check src/agentchallenge.js` to verify JS syntax.

## Rules
- Do NOT change the public API (gate, gate_http, verify, create, etc.)
- Do NOT change token format or HMAC signing
- Do NOT remove any existing templates — only ADD
- Keep answer normalization working (lowercase, trim, comma canonicalization)
- Every challenge must have exactly one correct answer
- Templates must be diverse enough that regex parsers struggle
- Run the full test suite when done

## File locations
- Templates: `src/agentchallenge/templates.py`
- Types: `src/agentchallenge/types/*.py`  
- JS port: `src/agentchallenge.js`
- Tests: `run_tests.py`
- Run tests: `PYTHONPATH=src python3 run_tests.py`
