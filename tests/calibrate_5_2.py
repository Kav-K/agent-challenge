#!/usr/bin/env python3
"""Quick calibration of gpt-5.2 against all 25 challenge types (10 attempts each)."""
import os, sys, json, time, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agentchallenge import AgentChallenge
from agentchallenge.types import CHALLENGE_TYPES, DIFFICULTY_MAP

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
ATTEMPTS = 5
MODEL = "gpt-5.2"
ALL_TYPES = sorted(CHALLENGE_TYPES.keys())

def call_openai(model, prompt):
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are solving a challenge. Reply with ONLY the answer, nothing else. No explanation, no quotes, no formatting."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0, "max_completion_tokens": 200,
    })
    try:
        r = subprocess.run(
            ["curl", "-s", "-m", "20", "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OPENAI_KEY}",
             "-H", "Content-Type: application/json", "-d", payload],
            capture_output=True, text=True, timeout=25
        )
        data = json.loads(r.stdout)
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ERROR: {e}"

print(f"\n{'='*60}")
print(f"  MODEL: {MODEL} ({ATTEMPTS} attempts per type)")
print(f"{'='*60}")

results = {}
for ctype in ALL_TYPES:
    correct = 0
    for i in range(ATTEMPTS):
        ac = AgentChallenge(secret=f"cal52-{ctype}-{i}-key", types=[ctype])
        ch = ac.create()
        answer = call_openai(MODEL, ch.prompt)
        result = ac.verify(ch.token, answer)
        if result.valid:
            correct += 1
        time.sleep(0.1)

    pct = correct / ATTEMPTS * 100
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    status = "✅" if pct == 100 else "⚠️" if pct >= 80 else "❌"
    print(f"  {status} {ctype:25s} {bar} {correct}/{ATTEMPTS} ({pct:.0f}%)")
    results[ctype] = {"correct": correct, "total": ATTEMPTS, "pct": pct}

# Summary by tier
print(f"\n{'='*60}")
print(f"  TIER SUMMARY")
print(f"{'='*60}")
for tier_name, tier_types in DIFFICULTY_MAP.items():
    tier_results = [results.get(t, {}).get("pct", 0) for t in tier_types if t in results]
    avg = sum(tier_results) / len(tier_results) if tier_results else 0
    all_100 = all(p == 100 for p in tier_results)
    print(f"  {tier_name:10s}: avg {avg:.0f}%  {'✅ ALL 100%' if all_100 else ''}")

# Write results
out = os.path.join(os.path.dirname(__file__), "calibration_gpt52.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  Saved to {out}")
