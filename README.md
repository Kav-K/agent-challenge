# agent-challenge

LLM-solvable challenge-response authentication for AI agent APIs.

Traditional CAPTCHAs block agents. Proof-of-work wastes compute. **agent-challenge** uses reasoning puzzles that any LLM can solve through thinking alone — no scripts, no hashing, no external tools.

## Install

```bash
pip install agent-challenge
```

## Server Side

```python
from agentchallenge import AgentChallenge

# Create an instance with your secret
ac = AgentChallenge(secret="your-server-secret-key")

# Generate a challenge
challenge = ac.create()
# challenge.prompt = "Reverse the following string: NOHTYP"
# challenge.token  = "eyJpZCI6ImNoXz..."  (signed, stateless)

# Send challenge.prompt and challenge.token to the agent via your API

# When the agent responds with their answer:
result = ac.verify(token=challenge.token, answer="PYTHON")
if result.valid:
    print("Agent verified! ✅")
else:
    print(f"Failed: {result.error}")
```

## Agent Side

The agent just reads the prompt and answers it. That's it.

```
Server: "Reverse the following string: NOHTYP"
Agent:  "PYTHON"

Server: "What is 234 + 567?"
Agent:  "801"

Server: "Decode this ROT13-encoded string: URYYB"
Agent:  "HELLO"
```

No SDK needed on the agent side. No computation. Just reasoning.

## Challenge Types

| Type | Example | Difficulty |
|------|---------|------------|
| `reverse_string` | Reverse "PYTHON" → "NOHTYP" | Easy |
| `simple_math` | 234 + 567 = ? | Easy |
| `pattern` | 2, 4, 8, 16, ? → 32 | Easy |
| `rot13` | Decode "URYYB" → "HELLO" | Medium |
| `letter_position` | Sum of A=1,B=2.. in "CAT" → 24 | Medium |
| `extract_letters` | Every 2nd char of "HWEOLRLLOD" | Medium |
| `word_math` | 7 + 8 as a word → "fifteen" | Hard |

## Configuration

```python
ac = AgentChallenge(
    secret="your-secret",     # Required (min 8 chars)
    difficulty="easy",         # "easy", "medium", or "hard"
    ttl=300,                   # Challenge expiry in seconds
    types=["reverse_string"],  # Restrict to specific types
)
```

## API

### `AgentChallenge(secret, difficulty, ttl, types)`

Create an instance. The secret is used for HMAC-signing tokens.

### `ac.create(challenge_type=None) → Challenge`

Generate a challenge. Returns:
- `challenge.id` — unique challenge ID
- `challenge.prompt` — text to send to the agent
- `challenge.token` — signed token for stateless verification
- `challenge.expires_at` — expiry timestamp
- `challenge.to_dict()` — serialize for JSON API responses

### `ac.verify(token, answer) → VerifyResult`

Verify an agent's answer. Returns:
- `result.valid` — boolean
- `result.error` — error message if invalid
- `result.challenge_type` — which type was used
- `result.elapsed_ms` — verification time

## Stateless Design

No database required. Challenge data is HMAC-signed into tokens:
1. Server creates challenge → signs answer hash into token
2. Agent receives prompt + token
3. Agent sends back answer + token
4. Server verifies HMAC signature, checks expiry, compares answer hash

Tokens can't be forged or tampered with. Each contains its own expiry.

## JavaScript Port

A JavaScript/Node.js version is included at `src/agentchallenge.js`:

```javascript
import { AgentChallenge } from './agentchallenge.js';

const ac = new AgentChallenge({ secret: 'your-secret' });
const challenge = ac.create();
const result = ac.verify(challenge.token, 'agent answer');
```

## Testing

```bash
PYTHONPATH=src python3 run_tests.py
```

47 tests covering initialization, creation, verification, normalization, tokens, all 7 challenge types, integration flows, difficulty distribution, performance, and cross-secret isolation.

## License

MIT
