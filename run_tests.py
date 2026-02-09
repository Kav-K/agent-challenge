#!/usr/bin/env python3
"""Standalone test runner — no pytest required."""

import sys
import os
import time
import traceback
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agentchallenge import AgentChallenge, Challenge, VerifyResult, CHALLENGE_TYPES
from agentchallenge.challenge import _normalize_answer, _hash_answer, _encode_token, _decode_token, TokenError
from agentchallenge.types import generate_challenge, DIFFICULTY_MAP

passed = 0
failed = 0
errors = []


def test(name):
    """Decorator to register and run a test immediately."""
    def decorator(fn):
        global passed, failed
        try:
            fn()
            passed += 1
            print(f"  ✅ {name}")
        except AssertionError as e:
            failed += 1
            errors.append((name, str(e)))
            print(f"  ❌ {name}: {e}")
        except Exception as e:
            failed += 1
            errors.append((name, traceback.format_exc()))
            print(f"  💥 {name}: {e}")
        return fn
    return decorator


# ── Initialization ────────────────────────────────────
print("\n🔧 Initialization")

@test("Valid init")
def _():
    ac = AgentChallenge(secret="my-secret-key-test")
    assert ac is not None

@test("Short secret rejected")
def _():
    try:
        AgentChallenge(secret="short")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

@test("Empty secret rejected")
def _():
    try:
        AgentChallenge(secret="")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

@test("All difficulty levels work")
def _():
    for d in ["easy", "medium", "hard"]:
        ac = AgentChallenge(secret="test-secret-key-12", difficulty=d)
        ch = ac.create()
        assert ch.prompt, f"Empty prompt for difficulty={d}"

@test("Custom types restriction")
def _():
    ac = AgentChallenge(secret="test-secret-key-12", types=["reverse_string"])
    for _ in range(10):
        ch = ac.create()
        assert ch.challenge_type == "reverse_string"

@test("Custom TTL")
def _():
    ac = AgentChallenge(secret="test-secret-key-12", ttl=60)
    ch = ac.create()
    assert ch.expires_at <= time.time() + 61


# ── Challenge Creation ────────────────────────────────
print("\n📝 Challenge Creation")

@test("Creates valid challenge")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    ch = ac.create()
    assert isinstance(ch, Challenge)
    assert ch.id.startswith("ch_")
    assert len(ch.id) > 10
    assert ch.prompt
    assert ch.token
    assert ch.expires_at > time.time()
    assert ch.challenge_type in CHALLENGE_TYPES

@test("Challenges are unique (20x)")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    challenges = [ac.create() for _ in range(20)]
    ids = [c.id for c in challenges]
    tokens = [c.token for c in challenges]
    assert len(set(ids)) == 20, f"Duplicate IDs found"
    assert len(set(tokens)) == 20, f"Duplicate tokens found"

@test("Specific type selection")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    for type_name in CHALLENGE_TYPES:
        ch = ac.create(challenge_type=type_name)
        assert ch.challenge_type == type_name, f"Wrong type: {ch.challenge_type} != {type_name}"

@test("Unknown type raises ValueError")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    try:
        ac.create(challenge_type="nonexistent_type")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

@test("to_dict serialization")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    ch = ac.create()
    d = ch.to_dict()
    assert "id" in d
    assert "prompt" in d
    assert "token" in d
    assert "expires_in" in d
    assert d["type"] == "reasoning"  # Never leaks internal type

@test("Expired property")
def _():
    ac = AgentChallenge(secret="test-secret-key-12", ttl=1)
    ch = ac.create()
    assert not ch.expired
    time.sleep(1.1)
    assert ch.expired


# ── Verification ──────────────────────────────────────
print("\n✔️  Verification")

@test("Wrong answer rejected")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    ch = ac.create(challenge_type="simple_math")
    result = ac.verify(token=ch.token, answer="definitely_wrong_xyz_123")
    assert not result.valid
    assert result.error == "Incorrect answer"

@test("Empty answer rejected")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    ch = ac.create()
    result = ac.verify(token=ch.token, answer="")
    assert not result.valid
    assert result.error == "Empty answer"

@test("Whitespace answer rejected")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    ch = ac.create()
    result = ac.verify(token=ch.token, answer="   ")
    assert not result.valid
    assert result.error == "Empty answer"

@test("Expired token rejected")
def _():
    ac = AgentChallenge(secret="test-secret-key-12", ttl=1)
    ch = ac.create()
    time.sleep(1.1)
    result = ac.verify(token=ch.token, answer="anything")
    assert not result.valid
    assert result.error == "Challenge expired"

@test("Tampered token rejected")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    ch = ac.create()
    tampered = ch.token[:-1] + ("a" if ch.token[-1] != "a" else "b")
    result = ac.verify(token=tampered, answer="anything")
    assert not result.valid

@test("Invalid token format rejected")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    result = ac.verify(token="not-a-valid-token", answer="anything")
    assert not result.valid

@test("Empty token rejected")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    result = ac.verify(token="", answer="anything")
    assert not result.valid

@test("Different secret rejected")
def _():
    ac1 = AgentChallenge(secret="secret-one-12345")
    ac2 = AgentChallenge(secret="secret-two-12345")
    ch = ac1.create()
    result = ac2.verify(token=ch.token, answer="anything")
    assert not result.valid

@test("VerifyResult has all fields")
def _():
    ac = AgentChallenge(secret="test-secret-key-12")
    ch = ac.create()
    result = ac.verify(token=ch.token, answer="wrong")
    assert isinstance(result, VerifyResult)
    assert hasattr(result, "valid")
    assert hasattr(result, "error")
    assert hasattr(result, "challenge_type")
    assert hasattr(result, "elapsed_ms")


# ── Answer Normalization ──────────────────────────────
print("\n🔤 Answer Normalization")

@test("Case insensitive")
def _():
    assert _normalize_answer("HELLO") == "hello"
    assert _normalize_answer("HeLLo") == "hello"

@test("Strips whitespace")
def _():
    assert _normalize_answer("  hello  ") == "hello"
    assert _normalize_answer("\nhello\n") == "hello"

@test("Strips quotes")
def _():
    assert _normalize_answer('"hello"') == "hello"
    assert _normalize_answer("'hello'") == "hello"

@test("Collapses spaces")
def _():
    assert _normalize_answer("hello   world") == "hello world"

@test("Empty/None returns empty")
def _():
    assert _normalize_answer("") == ""
    assert _normalize_answer(None) == ""
    assert _normalize_answer(123) == ""


# ── Token Encoding ────────────────────────────────────
print("\n🔐 Token Encoding")

@test("Token round trip")
def _():
    secret = b"test-secret-key-here"
    payload = {"foo": "bar", "num": 42}
    token = _encode_token(payload, secret)
    decoded = _decode_token(token, secret)
    assert decoded == payload

@test("Tampered token fails")
def _():
    secret = b"test-secret-key-here"
    token = _encode_token({"data": 1}, secret)
    tampered = token[:-1] + "X"
    try:
        _decode_token(tampered, secret)
        assert False, "Should have raised TokenError"
    except TokenError:
        pass

@test("Wrong secret fails")
def _():
    token = _encode_token({"data": 1}, b"secret-one-test")
    try:
        _decode_token(token, b"secret-two-test")
        assert False, "Should have raised TokenError"
    except TokenError:
        pass


# ── Challenge Types ───────────────────────────────────
print("\n🎲 Challenge Types")

for type_name in CHALLENGE_TYPES:
    @test(f"Type: {type_name} generates valid pairs (20x)")
    def _(tn=type_name):
        cls = CHALLENGE_TYPES[tn]
        for _ in range(20):
            prompt, answer = cls.generate()
            assert isinstance(prompt, str), f"Prompt not string"
            assert isinstance(answer, str), f"Answer not string"
            assert len(prompt) > 10, f"Prompt too short: {prompt}"
            assert len(answer) > 0, f"Answer empty"
            assert answer == answer.lower(), f"Answer not lowercase: {answer}"


# ── Integration: Solve Each Type ──────────────────────
print("\n🧪 Integration: Solve Each Type")

@test("Solve: reverse_string")
def _():
    ac = AgentChallenge(secret="integration-test-key")
    ch = ac.create(challenge_type="reverse_string")
    word = ch.prompt.split(": ")[-1].strip()
    answer = word[::-1]
    result = ac.verify(token=ch.token, answer=answer)
    assert result.valid, f"Failed to verify '{word}' reversed as '{answer}': {result.error}"

@test("Solve: simple_math (30x)")
def _():
    ac = AgentChallenge(secret="integration-test-key")
    for _ in range(30):
        ch = ac.create(challenge_type="simple_math")
        # Match +, -, × and multi-operand (a + b + c, a - b - c)
        nums = [int(n) for n in re.findall(r'\d+', ch.prompt.split('?')[0])]
        if '×' in ch.prompt:
            answer = nums[0] * nums[1]
        elif ch.prompt.count('+') >= 2:
            answer = sum(nums)
        elif ch.prompt.count('-') >= 2:
            answer = nums[0] - sum(nums[1:])
        elif '+' in ch.prompt:
            answer = nums[0] + nums[1]
        else:
            answer = nums[0] - nums[1]
        result = ac.verify(token=ch.token, answer=str(answer))
        assert result.valid, f"Failed: {ch.prompt} -> {answer}: {result.error}"

@test("Solve: rot13 (20x)")
def _():
    from agentchallenge.types.rot13 import _rot13
    ac = AgentChallenge(secret="integration-test-key")
    for _ in range(20):
        ch = ac.create(challenge_type="rot13")
        m = re.search(r":\s*([A-Z]+)", ch.prompt)
        assert m, f"Can't parse: {ch.prompt}"
        answer = _rot13(m.group(1))
        result = ac.verify(token=ch.token, answer=answer)
        assert result.valid, f"Failed ROT13: {result.error}"

@test("Solve: pattern (30x)")
def _():
    ac = AgentChallenge(secret="integration-test-key")
    solved = 0
    for _ in range(30):
        ch = ac.create(challenge_type="pattern")
        nums = [int(n) for n in re.findall(r"\d+", ch.prompt.split("?")[0])]
        diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
        if all(d == diffs[0] for d in diffs):
            answer = nums[-1] + diffs[0]
        elif nums[0] != 0 and len(set(round(nums[i+1]/nums[i], 4) for i in range(len(nums)-1))) == 1:
            answer = int(nums[-1] * (nums[1] / nums[0]))
        else:
            dd = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
            if dd and all(d == dd[0] for d in dd):
                answer = nums[-1] + diffs[-1] + dd[0]
            else:
                continue
        result = ac.verify(token=ch.token, answer=str(answer))
        if result.valid:
            solved += 1
    assert solved >= 20, f"Only solved {solved}/30 patterns"

@test("Solve: letter_position (20x)")
def _():
    ac = AgentChallenge(secret="integration-test-key")
    for _ in range(20):
        ch = ac.create(challenge_type="letter_position")
        m = re.search(r'"([A-Z]+)"', ch.prompt)
        assert m, f"Can't parse: {ch.prompt}"
        word = m.group(1)
        answer = sum(ord(c) - ord('A') + 1 for c in word)
        result = ac.verify(token=ch.token, answer=str(answer))
        assert result.valid, f"Failed letter_position: {word} -> {answer}: {result.error}"

@test("Solve: extract_letters (20x)")
def _():
    ac = AgentChallenge(secret="integration-test-key")
    for _ in range(20):
        ch = ac.create(challenge_type="extract_letters")
        nth = int(re.search(r"every (\d+)", ch.prompt).group(1))
        m = re.search(r"character: ([A-Z]+)", ch.prompt)
        assert m, f"Can't parse: {ch.prompt}"
        mixed = m.group(1)
        extracted = "".join(mixed[i] for i in range(0, len(mixed), nth))
        result = ac.verify(token=ch.token, answer=extracted)
        assert result.valid, f"Failed extract: nth={nth} -> {extracted}: {result.error}"

@test("Solve: word_math char_count")
def _():
    ac = AgentChallenge(secret="integration-test-key")
    # Run until we get a char_count variant
    for _ in range(50):
        ch = ac.create(challenge_type="word_math")
        m = re.search(r'How many letters.*"([A-Z]+)"', ch.prompt)
        if m:
            result = ac.verify(token=ch.token, answer=str(len(m.group(1))))
            assert result.valid, f"Failed char_count: {result.error}"
            return
    # If we didn't get this variant, that's OK


# ── Difficulty Distribution ───────────────────────────
print("\n📊 Difficulty Distribution")

@test("Easy types stay in easy pool")
def _():
    for _ in range(30):
        ctype, _, _ = generate_challenge(difficulty="easy")
        assert ctype in DIFFICULTY_MAP["easy"], f"{ctype} not in easy pool"

@test("Hard covers all types (500 samples)")
def _():
    seen = set()
    for _ in range(500):
        ctype, _, _ = generate_challenge(difficulty="hard")
        seen.add(ctype)
    assert seen == set(CHALLENGE_TYPES.keys()), f"Missing: {set(CHALLENGE_TYPES.keys()) - seen}"


# ── Performance ───────────────────────────────────────
print("\n⚡ Performance")

@test("100 create+verify under 1 second")
def _():
    ac = AgentChallenge(secret="perf-test-secret-key")
    start = time.time()
    for _ in range(100):
        ch = ac.create()
        ac.verify(token=ch.token, answer="test")
    elapsed = time.time() - start
    assert elapsed < 1.0, f"Took {elapsed:.2f}s"


# ── Cross-Secret Isolation ────────────────────────────
print("\n🔒 Cross-Secret Isolation")

@test("Different secrets can't cross-verify")
def _():
    ac1 = AgentChallenge(secret="secret-one-12345")
    ac2 = AgentChallenge(secret="secret-two-67890")
    ch1 = ac1.create()
    ch2 = ac2.create()
    assert not ac1.verify(token=ch2.token, answer="any").valid
    assert not ac2.verify(token=ch1.token, answer="any").valid


# ── Summary ───────────────────────────────────────────
print(f"\n{'='*50}")
print(f"  ✅ Passed: {passed}")
print(f"  ❌ Failed: {failed}")
if errors:
    print(f"\n  Failures:")
    for name, err in errors:
        print(f"    • {name}: {err[:200]}")
print(f"{'='*50}\n")

sys.exit(1 if failed > 0 else 0)
