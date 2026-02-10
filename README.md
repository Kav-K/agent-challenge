<p align="center">
  <h1 align="center">🧩 agent-challenge</h1>
  <p align="center">
    <strong>Drop-in LLM authentication for any API endpoint.</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/agent-challenge/"><img src="https://img.shields.io/pypi/v/agent-challenge?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://www.npmjs.com/package/agent-challenge"><img src="https://img.shields.io/npm/v/agent-challenge?color=green&label=npm" alt="npm"></a>
    <a href="https://github.com/Kav-K/agent-challenge/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Kav-K/agent-challenge" alt="License"></a>
    <a href="https://challenge.llm.kaveenk.com"><img src="https://img.shields.io/badge/docs-live-brightgreen" alt="Docs"></a>
  </p>
</p>

---

## Why?

You built an API. Now bots are hitting it — not the smart kind, the dumb kind. Automated scripts cycling through endpoints, low-effort crawlers scraping your data, or spammy throwaway clients burning through your resources.

Traditional CAPTCHAs block *everyone* who isn't a human sitting in a browser. API keys work, but they require manual signup, email verification, approval flows — friction that kills adoption for legitimate AI agents.

**agent-challenge** sits in the middle: it blocks automated scripts and low-capability bots while letting any competent LLM walk right through. The challenge requires actual reasoning — reversing strings, solving arithmetic, decoding ciphers — things that a real language model handles instantly but a curl loop or a Python script with `requests.post()` can't fake.

Think of it as a **proof of intelligence** gate:

- ✅ GPT-4, Claude, Gemini, Llama — pass instantly
- ✅ Any capable LLM-powered agent — solves in one shot
- ❌ Automated scripts — can't reason about the prompt
- ❌ Spammy low-effort bots — can't parse randomized templates
- ❌ Dumb wrappers just forwarding requests — no LLM to solve with

It's the ultimate automated-script buster. If the other end of your API can't do basic thinking, it doesn't get in. This is "prove you **ARE** a robot", not "prove you're not a robot"! 

```python
# Before: unprotected endpoint
@app.route("/api/screenshots", methods=["POST"])
def screenshot():
    return take_screenshot(request.json["url"])

# After: agents solve a puzzle once, pass through forever
@app.route("/api/screenshots", methods=["POST"])
def screenshot():
    result = ac.gate_http(request.headers, request.get_json(silent=True))
    if result.status != "authenticated":
        return jsonify(result.to_dict()), 401
    return take_screenshot(request.json["url"])
```

## How It Works

```
Agent                          Your API
  │                               │
  ├──POST /api/your-endpoint────►│
  │                               ├── gate() → no token
  │◄──401 { challenge_required }──┤
  │                               │
  │  LLM reads prompt, answers    │
  │                               │
  ├──POST { answer, token }─────►│
  │                               ├── gate() → correct!
  │◄──200 { token: "eyJpZ..." }───┤
  │                               │
  │  ┌─────────────────────┐      │
  │  │ Saves token forever │      │
  │  └─────────────────────┘      │
  │                               │
  ├──POST + Bearer eyJpZ...─────►│
  │                               ├── gate() → valid token
  │◄──200 { authenticated }───────┤   (instant, no puzzle)
```

One endpoint. Three interactions. Zero database.

## Install

```bash
pip install agent-challenge
```

```bash
npm install agent-challenge
```

## Quick Start

### Python (Flask)

```python
from agentchallenge import AgentChallenge

ac = AgentChallenge(secret="your-secret-key-min-8-chars")

@app.route("/api/data", methods=["POST"])
def protected_endpoint():
    result = ac.gate(
        token=request.headers.get("Authorization", "").removeprefix("Bearer ") or None,
        challenge_token=request.json.get("challenge_token"),
        answer=request.json.get("answer"),
    )
    if result.status != "authenticated":
        return jsonify(result.to_dict()), 401

    # Your logic here — agent is verified
    return jsonify({"data": "secret stuff"})
```

### Node.js (Express)

```javascript
import { AgentChallenge } from 'agent-challenge';

const ac = new AgentChallenge({ secret: 'your-secret-key-min-8-chars' });

app.post('/api/data', (req, res) => {
  const gate = ac.gateSync({
    token: req.headers.authorization?.slice(7),
    challengeToken: req.body?.challenge_token,
    answer: req.body?.answer,
  });
  if (gate.status !== 'authenticated')
    return res.status(401).json(gate);

  // Your logic here — agent is verified
  res.json({ data: 'secret stuff' });
});
```

## The `gate()` API

One function handles everything. Three modes based on what's passed in:

| Arguments | Behavior | Returns |
|-----------|----------|---------|
| *(none)* | Generate a new challenge | `{ status: "challenge_required", prompt, challenge_token }` |
| `challenge_token` + `answer` | Verify answer, issue permanent token | `{ status: "authenticated", token: "eyJpZ..." }` |
| `token` | Validate saved token | `{ status: "authenticated" }` |

```python
# Mode 1: No args → challenge
result = ac.gate()
# → GateResult(status="challenge_required", prompt="Reverse: NOHTYP", ...)

# Mode 2: Answer → permanent token
result = ac.gate(challenge_token="eyJ...", answer="PYTHON")
# → GateResult(status="authenticated", token="eyJpZCI6ImF0Xy...")

# Mode 3: Token → instant pass
result = ac.gate(token="eyJpZCI6ImF0Xy...")
# → GateResult(status="authenticated")
```

### `gate_http()` / `gateHttp()` — Zero-Boilerplate HTTP

Instead of manually extracting the Bearer token from headers and fields from the body, pass them directly:

```python
# Python — works with Flask, Django, FastAPI, or anything with headers + body
result = ac.gate_http(request.headers, request.get_json(silent=True))
```

```javascript
// JavaScript — works with Express, Koa, Fastify, or anything with headers + body
const result = ac.gateHttp(req.headers, req.body);
```

It reads `Authorization: Bearer <token>` from headers and `challenge_token` / `answer` from the body automatically. Same result as `gate()`, less wiring.

## Challenge Types

12 challenge types across 3 difficulty tiers. All use randomized inputs — no fixed word lists.

### Easy
| Type | Example |
|------|---------|
| `reverse_string` | Reverse "PYTHON" → `NOHTYP` |
| `simple_math` | 234 + 567 = `801` |
| `pattern` | 2, 4, 8, 16, ? → `32` |
| `counting` | Count vowels in "CHALLENGE" → `3` |

### Medium
| Type | Example |
|------|---------|
| `rot13` | Decode "URYYB" → `HELLO` |
| `letter_position` | A=1,B=2.. sum of "CAT" → `24` |
| `extract_letters` | Every 2nd char of "HWEOLRLLOD" → `WORLD` |
| `sorting` | Sort [7,2,9,1] ascending → `1,2,7,9` |
| `binary` | Convert 42 to binary → `101010` |

### Hard
| Type | Example |
|------|---------|
| `caesar` | Decrypt "KHOOR" with shift 3 → `HELLO` |
| `word_math` | 7 + 8 as a word → `fifteen` |
| `transform` | Uppercase + reverse "hello" → `OLLEH` |

Each type has 3–8 prompt templates with randomized phrasing, making regex-based solvers impractical.

## Dynamic Challenges (Optional)

Use an LLM to generate novel, never-before-seen challenges:

```python
ac = AgentChallenge(secret="your-secret")

# Set an API key (or use OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY env vars)
ac.set_openai_api_key("sk-...")

# Enable dynamic mode
ac.enable_dynamic_mode()  # Auto-detects provider from available keys
```

Dynamic mode generates a challenge with one LLM call and verifies the answer with another. Falls back to static challenges after 3 failures. Supports OpenAI, Anthropic, and Google Gemini — auto-detected from environment variables.

## Challenge Every Time (No Persistent Tokens)

By default, agents solve once and get a permanent token. To require a challenge on every request:

```python
ac = AgentChallenge(
    secret="your-secret",
    persistent=False,  # No tokens issued — challenge every time
)
```

When `persistent=False`:
- Solving a challenge returns `{ "status": "authenticated" }` with **no token**
- Passing a saved token returns an error
- Every request requires solving a new puzzle

This is useful for high-security endpoints, rate-limited operations, or when you want proof of LLM capability on every call.

## Agent-Only Mode (Block Humans)

Combine a tight time limit with hard difficulty to create endpoints that **only AI agents can access**. A human can't read a caesar cipher, decode it mentally, and type the answer in 10 seconds — but an LLM handles it in under 2.

```python
ac = AgentChallenge(
    secret="your-secret",
    difficulty="hard",      # caesar, word_math, transform
    ttl=10,                 # 10 seconds — impossible for humans
    persistent=False,       # challenge every request
)
```

This is useful for:
- **Agent-to-agent APIs** where human access is unwanted
- **Internal tooling** that should only be called by AI systems
- **Preventing manual API abuse** even by authenticated users with the endpoint URL

The `ttl` parameter controls how long an agent has to solve the challenge after it's issued. At `difficulty="hard"` with `ttl=10`, the challenge requires genuine LLM reasoning (not just string reversal) and must be solved faster than any human could manage.

## Configuration

```python
ac = AgentChallenge(
    secret="your-secret",       # Required — HMAC signing key (min 8 chars)
    difficulty="medium",        # "easy" | "medium" | "hard" (default: "easy")
    ttl=300,                    # Challenge expiry in seconds (default: 300)
    types=["rot13", "caesar"],  # Restrict to specific challenge types
    persistent=True,            # Issue permanent tokens (default: True)
)

# Dynamic mode is enabled separately:
# ac.set_openai_api_key("sk-...")
# ac.enable_dynamic_mode()
```

## Token Architecture

**Stateless. No database. No session store.**

Tokens are HMAC-SHA256 signed JSON payloads:

```
base64url(payload).HMAC-SHA256(payload, secret)
```

Two token types:

| Token | Prefix | Lifetime | Contains |
|-------|--------|----------|----------|
| Challenge | `ch_` | 5 minutes | answer hash, expiry, type |
| Agent | `at_` | Permanent | agent ID, created timestamp |

- Tokens can't be forged — HMAC verification catches any tampering
- Challenge tokens are single-use — answer hash prevents replay
- Agent tokens are permanent — `verify_token()` validates signature only
- No database lookups — everything is in the token itself

## Lower-Level API

If you don't want the `gate()` pattern:

```python
ac = AgentChallenge(secret="your-secret-key")

# Create a challenge
challenge = ac.create()
# challenge.prompt       → "Reverse the following string: NOHTYP"
# challenge.token        → "eyJpZCI6ImNoXz..."
# challenge.to_dict()    → dict for JSON responses

# Verify an answer
result = ac.verify(token=challenge.token, answer="PYTHON")
# result.valid           → True
# result.challenge_type  → "reverse_string"

# Create a persistent agent token directly
token = ac.create_token("agent-name")
# token → "eyJpZCI6ImF0Xy..."  (base64url-encoded signed payload)

# Verify a token
ac.verify_token(token)  # → True
```

## Agent Integration

Agents don't need an SDK. They just call your endpoint normally:

```python
import requests

def call_api(payload):
    endpoint = "https://your-api.com/api/data"
    token = load_saved_token()  # from disk/env

    r = requests.post(endpoint,
        headers={"Authorization": f"Bearer {token}"} if token else {},
        json=payload)

    if r.status_code != 401:
        return r  # success (or other error)

    # Got a challenge — solve it
    data = r.json()
    if data.get("status") != "challenge_required":
        return r

    answer = llm.complete(data["prompt"])  # any LLM
    r = requests.post(endpoint, json={
        "challenge_token": data["challenge_token"],
        "answer": answer, **payload
    })

    if "token" in r.json():
        save_token(r.json()["token"])  # persist for next time

    return r
```

Document this pattern in your API's SKILL.md or agent docs, and any LLM-powered agent can authenticate autonomously.

## Testing

```bash
# Python
PYTHONPATH=src python3 run_tests.py

# JavaScript (syntax check)
node --check src/agentchallenge.js
```

## Live Demo

Try it interactively at **[challenge.llm.kaveenk.com](https://challenge.llm.kaveenk.com)**

## Used By

- **[SnapService](https://snap.llm.kaveenk.com)** — Screenshot-as-a-Service API for AI agents

## License

[MIT](LICENSE)
