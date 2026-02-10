<p align="center">
  <h1 align="center">🧩 agent-challenge</h1>
  <p align="center">
    <strong>Drop-in LLM authentication for any API endpoint.</strong>
  </p>
  <p align="center">
    <a href="https://www.npmjs.com/package/agent-challenge"><img src="https://img.shields.io/npm/v/agent-challenge?color=green&label=npm" alt="npm"></a>
    <a href="https://pypi.org/project/agent-challenge/"><img src="https://img.shields.io/pypi/v/agent-challenge?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://github.com/Kav-K/agent-challenge/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Kav-K/agent-challenge" alt="License"></a>
    <a href="https://challenge.llm.kaveenk.com"><img src="https://img.shields.io/badge/docs-live-brightgreen" alt="Docs"></a>
  </p>
</p>

> **📖 Full documentation, live demo, and interactive examples: [challenge.llm.kaveenk.com](https://challenge.llm.kaveenk.com)**

---

## Why?

You built an API. Now bots are hitting it — not the smart kind, the dumb kind. Automated scripts cycling through endpoints, low-effort crawlers scraping your data, spammy throwaway clients burning through your resources.

Traditional CAPTCHAs block *everyone* who isn't a human in a browser. API keys require manual signup and approval flows. **agent-challenge** sits in the middle: it blocks automated scripts and low-capability bots while letting any competent LLM walk right through.

The challenge requires actual reasoning — reversing strings, solving arithmetic, decoding ciphers. A real language model handles it instantly. A curl loop can't.

- ✅ GPT-4, Claude, Gemini, Llama — pass instantly
- ❌ Automated scripts, spammy bots, dumb wrappers — blocked

It's the ultimate automated-script buster. If the other end can't think, it doesn't get in.

## Install

```bash
npm install agent-challenge
```

## Quick Start

```javascript
import { AgentChallenge } from 'agent-challenge';

const ac = new AgentChallenge({ secret: 'your-secret-key-min-8-chars' });

// Drop this into any existing route — one line handles everything
app.post('/api/your-endpoint', (req, res) => {
  const result = ac.gateHttp(req.headers, req.body);
  if (result.status !== 'authenticated')
    return res.status(401).json(result);

  // Your existing logic — unchanged
  res.json({ data: 'protected stuff' });
});
```

That's it. Agents solve a reasoning puzzle once, get a permanent token, and pass through instantly on every future request.

## How It Works

```
Agent                          Your API
  │                               │
  ├──POST /api/your-endpoint────►│
  │                               ├── gateSync() → no token
  │◄──401 { challenge_required }──┤
  │                               │
  │  LLM reads prompt, answers    │
  │                               │
  ├──POST { answer, token }─────►│
  │                               ├── gateSync() → correct!
  │◄──200 { token: "eyJpZ..." }───┤
  │                               │
  │  Saves token permanently      │
  │                               │
  ├──POST + Bearer eyJpZ...─────►│
  │                               ├── gateSync() → valid token
  │◄──200 { authenticated }───────┤   (instant, no puzzle)
```

## The `gateSync()` API

One function, three modes:

| Arguments | What happens | Response |
|-----------|-------------|----------|
| *(none)* | New challenge | `{ status: "challenge_required", prompt, challenge_token }` |
| `challengeToken` + `answer` | Verify → issue token | `{ status: "authenticated", token: "eyJpZ..." }` |
| `token` | Validate saved token | `{ status: "authenticated" }` |

## Challenge Every Time (No Persistent Tokens)

Want agents to solve a challenge on every request? Disable persistent tokens:

```javascript
const ac = new AgentChallenge({
  secret: 'your-secret',
  persistent: false,  // No tokens issued — challenge every time
});
```

When `persistent: false`:
- Solving a challenge returns `{ status: "authenticated" }` with **no token**
- Passing a saved token returns an error
- Every request requires solving a new puzzle

## Agent-Only Mode (Block Humans)

Tight time limit + hard difficulty = only AI agents can pass:

```javascript
const ac = new AgentChallenge({
  secret: 'your-secret',
  difficulty: 'hard',     // caesar, word_math, transform
  ttl: 10,                // 10 seconds — humans can't
  persistent: false,      // challenge every request
});
```

A human can't decode a caesar cipher in 10 seconds. An LLM does it in under 2.

## Configuration

```javascript
const ac = new AgentChallenge({
  secret: 'your-secret',       // Required — HMAC signing key (min 8 chars)
  difficulty: 'medium',        // 'easy' | 'medium' | 'hard' (default: 'easy')
  ttl: 300,                    // Challenge expiry in seconds (default: 300)
  types: ['rot13', 'caesar'],  // Restrict to specific types (optional)
  persistent: true,            // Issue permanent tokens (default: true)
});
```

## 12 Challenge Types

All use randomized inputs — no fixed word lists.

| Difficulty | Types |
|-----------|-------|
| **Easy** | `reverse_string`, `simple_math`, `pattern`, `counting` |
| **Medium** | `rot13`, `letter_position`, `extract_letters`, `sorting`, `binary` |
| **Hard** | `caesar`, `word_math`, `transform` |

Each type has 3–8 prompt templates with randomized phrasing.

## Lower-Level API

```javascript
const ac = new AgentChallenge({ secret: 'your-secret-key' });

// Create a challenge manually
const challenge = ac.createSync();
// challenge.prompt  → "Reverse the following string: NOHTYP"
// challenge.token   → "eyJ..."

// Verify an answer
const result = ac.verify(challenge.token, 'PYTHON');
// result.valid → true

// Create/verify persistent tokens directly
const token = ac.createToken('agent-name');
ac.verifyToken(token); // → true
```

## Stateless Architecture

No database. Tokens are HMAC-SHA256 signed JSON:

```
base64url(payload).HMAC-SHA256(payload, secret)
```

- **Challenge tokens** (`ch_`): 5-minute TTL, contain answer hash
- **Agent tokens** (`at_`): Permanent, contain agent ID + timestamp
- Can't be forged — HMAC catches tampering
- No server-side storage needed

## Also Available for Python

```bash
pip install agent-challenge
```

```python
from agentchallenge import AgentChallenge

ac = AgentChallenge(secret="your-secret-key")
result = ac.gate(
    token=request.headers.get("Authorization", "").removeprefix("Bearer ") or None,
    challenge_token=request.json.get("challenge_token"),
    answer=request.json.get("answer"),
)
```

## Docs & Demo

**[challenge.llm.kaveenk.com](https://challenge.llm.kaveenk.com)** — Interactive docs with live demo

## License

[MIT](LICENSE)
