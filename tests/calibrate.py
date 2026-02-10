#!/usr/bin/env python3
"""
Calibration script: test every challenge type against multiple models.
Determines empirical solve rates to classify difficulty tiers properly.

Usage: OPENAI_API_KEY=... python3 tests/calibrate.py
"""
import os, sys, json, time, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agentchallenge import AgentChallenge
from agentchallenge.types import CHALLENGE_TYPES, generate_challenge

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
ATTEMPTS_PER_TYPE = 10  # single-shot attempts per type per model

MODELS = ["gpt-4o-mini", "gpt-4o"]

ALL_TYPES = sorted(CHALLENGE_TYPES.keys())

# Agentic types (multi-step) — test separately
AGENTIC_TYPES = [
    "base_conversion_chain", "chained_transform", "letter_math",
    "multi_step_math", "nested_operations", "string_interleave",
    "word_extraction_chain",
]
STATIC_TYPES = [t for t in ALL_TYPES if t not in AGENTIC_TYPES]


def call_openai(model: str, prompt: str) -> str:
    """Call OpenAI API via curl (VPN-safe)."""
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are solving a challenge. Reply with ONLY the answer, nothing else. No explanation, no quotes, no formatting."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 200,
    })
    try:
        r = subprocess.run(
            ["curl", "-s", "-m", "15", "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OPENAI_KEY}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=20
        )
        data = json.loads(r.stdout)
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ERROR: {e}"


def normalize(s: str) -> str:
    """Normalize answer for comparison."""
    s = s.strip().lower()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1].strip()
    # Strip trailing punctuation
    while s and s[-1] in '.!':
        s = s[:-1]
    # Comma canonicalization
    if ',' in s:
        s = ', '.join(p.strip() for p in s.split(','))
    return s


def run_calibration():
    results = {}  # {model: {type: {correct: int, total: int, examples: []}}}

    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"  MODEL: {model}")
        print(f"{'='*60}")
        results[model] = {}

        types_to_test = STATIC_TYPES if model == "gpt-4o-mini" else ALL_TYPES

        for ctype in types_to_test:
            correct = 0
            failures = []
            for i in range(ATTEMPTS_PER_TYPE):
                # Generate with known answer for logging
                type_name, prompt, expected_answer = generate_challenge(specific_type=ctype)
                ac = AgentChallenge(secret=f"cal-{model}-{ctype}-{i}-key", types=[ctype])
                ch = ac.create()
                answer = call_openai(model, ch.prompt)
                result = ac.verify(ch.token, answer)

                if result.valid:
                    correct += 1
                else:
                    failures.append({
                        "prompt": ch.prompt[:80],
                        "expected": "?",
                        "got": answer[:50],
                    })

                # Rate limit: ~3 req/s
                time.sleep(0.35)

            pct = correct / ATTEMPTS_PER_TYPE * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            status = "✅" if pct == 100 else "⚠️" if pct >= 80 else "❌"
            print(f"  {status} {ctype:25s} {bar} {correct}/{ATTEMPTS_PER_TYPE} ({pct:.0f}%)")

            if failures:
                for f in failures[:2]:
                    print(f"     ↳ '{f['got']}' for '{f['prompt']}...'")

            results[model][ctype] = {
                "correct": correct,
                "total": ATTEMPTS_PER_TYPE,
                "pct": pct,
                "failures": failures[:3],
            }

        # Also test agentic types for gpt-4o-mini (5 attempts only, they mostly fail)
        if model == "gpt-4o-mini":
            print(f"\n  --- Agentic types (5 attempts, report only) ---")
            for ctype in AGENTIC_TYPES:
                correct = 0
                for i in range(5):
                    ac = AgentChallenge(secret=f"cal-ag-{ctype}-{i}", types=[ctype])
                    ch = ac.create()
                    answer = call_openai(model, ch.prompt)
                    result = ac.verify(ch.token, answer)
                    if result.valid:
                        correct += 1
                    time.sleep(0.35)
                pct = correct / 5 * 100
                print(f"  {'✅' if pct > 50 else '❌'} {ctype:25s} {correct}/5 ({pct:.0f}%)")
                results[model][ctype] = {"correct": correct, "total": 5, "pct": pct}

    # Summary
    print(f"\n{'='*60}")
    print(f"  CLASSIFICATION MATRIX")
    print(f"{'='*60}")
    print(f"\n  {'Type':25s} {'gpt-4o-mini':>12s} {'gpt-4o':>12s}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")

    for ctype in ALL_TYPES:
        mini = results.get("gpt-4o-mini", {}).get(ctype, {})
        four = results.get("gpt-4o", {}).get(ctype, {})
        mini_pct = f"{mini.get('pct', 0):.0f}%" if mini else "—"
        four_pct = f"{four.get('pct', 0):.0f}%" if four else "—"
        print(f"  {ctype:25s} {mini_pct:>12s} {four_pct:>12s}")

    # Write results to JSON
    out_path = os.path.join(os.path.dirname(__file__), "calibration_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    if not OPENAI_KEY:
        print("Set OPENAI_API_KEY")
        sys.exit(1)
    run_calibration()
