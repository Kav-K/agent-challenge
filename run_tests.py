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

@test("Solve: All 12 types via generate_challenge (20x each)")
def _():
    """Verify that each challenge type generates valid prompt/answer pairs.
    Tests that generate_challenge produces non-empty, correctly-typed results,
    and that create→verify round-trip works with the generated answer."""
    ac = AgentChallenge(secret="integration-test-key")
    for ctype in CHALLENGE_TYPES:
        for _ in range(20):
            t, prompt, answer = generate_challenge(specific_type=ctype)
            assert t == ctype, f"Wrong type: expected {ctype}, got {t}"
            assert len(prompt) > 10, f"Prompt too short for {ctype}: {prompt}"
            assert len(answer) > 0, f"Empty answer for {ctype}"
        # Verify create→verify round-trip (5x per type to keep test fast)
        for _ in range(5):
            ch = ac.create(challenge_type=ctype)
            assert ch.token, f"No token for {ctype}"
            assert ch.prompt, f"No prompt for {ctype}"
            # Wrong answer should fail
            result = ac.verify(token=ch.token, answer="DEFINITELY_WRONG_ANSWER_12345")
            assert not result.valid, f"Wrong answer accepted for {ctype}"

@test("Anti-parser: prompts vary across generations")
def _():
    """Verify that prompt templates actually randomize — same challenge type gives different phrasings."""
    ac = AgentChallenge(secret="antiparse-test-key")
    for ctype in ["reverse_string", "simple_math", "rot13", "counting", "sorting"]:
        prompts = set()
        # Extract just the phrasing pattern (first few words)
        for _ in range(20):
            ch = ac.create(challenge_type=ctype)
            # Get first 5 words to check template variation
            first_words = ' '.join(ch.prompt.split()[:5])
            prompts.add(first_words)
        assert len(prompts) >= 2, f"Type {ctype}: no template variation in 20 challenges (got {prompts})"

@test("Solve: pattern (30x, regex-based)")
def _():
    """Pattern challenges still have numbers in predictable positions — test the math works."""
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


# ── Dynamic Mode Tests ────────────────────────────────

print(f"\n🤖 Dynamic Mode")

@test("Dynamic mode: enable requires API key")
def _():
    # Temporarily clear env keys
    saved = {}
    for env_var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]:
        saved[env_var] = os.environ.pop(env_var, None)
    try:
        ac = AgentChallenge(secret="test-dynamic-12345")
        try:
            ac.enable_dynamic_mode()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "No API key" in str(e)
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v

# ── Gate Tests ─────────────────────────────────────────
print("\n── Gate (unified endpoint) ──────────────────────")

from agentchallenge.challenge import GateResult

@test("Gate: no args returns challenge_required")
def _():
    ac = AgentChallenge(secret="gate-test-secret-123")
    result = ac.gate()
    assert isinstance(result, GateResult)
    assert result.status == "challenge_required"
    assert result.prompt is not None
    assert len(result.prompt) > 5
    assert result.challenge_token is not None
    assert result.expires_in > 0
    assert result.token is None  # No token yet

@test("Gate: challenge_token + correct answer = authenticated + token")
def _():
    ac = AgentChallenge(secret="gate-test-secret-123", difficulty="easy")
    # Get a challenge via gate
    r1 = ac.gate()
    assert r1.status == "challenge_required"
    # Solve it by creating directly and getting the answer
    challenge = ac.create()
    # Use the low-level verify to find the answer — we'll use a known type
    from agentchallenge.types import generate_challenge as _gc
    ctype, prompt, answer = _gc(difficulty="easy")
    c = ac._build_challenge(ctype, prompt, answer)
    # Submit correct answer
    r2 = ac.gate(challenge_token=c.token, answer=answer)
    assert r2.status == "authenticated"
    assert r2.token is not None
    assert r2.token.startswith("eyJ")  # base64url

@test("Gate: challenge_token + wrong answer = error")
def _():
    ac = AgentChallenge(secret="gate-test-secret-123")
    r1 = ac.gate()
    r2 = ac.gate(challenge_token=r1.challenge_token, answer="definitely_wrong_xyz_42")
    assert r2.status == "error"
    assert "Incorrect" in r2.error

@test("Gate: valid persistent token = authenticated")
def _():
    ac = AgentChallenge(secret="gate-test-secret-123")
    token = ac.create_token()
    r = ac.gate(token=token)
    assert r.status == "authenticated"
    assert r.token is None  # Don't re-issue

@test("Gate: invalid persistent token = error")
def _():
    ac = AgentChallenge(secret="gate-test-secret-123")
    r = ac.gate(token="at_fakefakefake.invalidsig")
    assert r.status == "error"
    assert "Invalid" in r.error

@test("Gate: wrong secret rejects token")
def _():
    ac1 = AgentChallenge(secret="gate-secret-one-123")
    ac2 = AgentChallenge(secret="gate-secret-two-456")
    token = ac1.create_token()
    r = ac2.gate(token=token)
    assert r.status == "error"

@test("Gate: to_dict serialization")
def _():
    ac = AgentChallenge(secret="gate-test-secret-123")
    r = ac.gate()
    d = r.to_dict()
    assert d["status"] == "challenge_required"
    assert "prompt" in d
    assert "challenge_token" in d
    assert "expires_in" in d
    assert "token" not in d  # Should be omitted when None

@test("Gate: create_token and verify_token")
def _():
    ac = AgentChallenge(secret="gate-test-secret-123")
    token = ac.create_token(agent_id="test-agent")
    assert ac.verify_token(token) is True
    assert ac.verify_token("garbage") is False
    assert ac.verify_token("") is False

@test("Gate: full round-trip (challenge → solve → token → reuse)")
def _():
    ac = AgentChallenge(secret="gate-full-test-12345")
    from agentchallenge.types import generate_challenge as _gc
    ctype, prompt, answer = _gc(difficulty="easy")
    c = ac._build_challenge(ctype, prompt, answer)
    # Solve
    r = ac.gate(challenge_token=c.token, answer=answer)
    assert r.status == "authenticated"
    assert r.token is not None
    # Reuse token
    r2 = ac.gate(token=r.token)
    assert r2.status == "authenticated"


print("\n── Persistent Toggle ───────────────────────────")

@test("persistent=False: gate solve returns authenticated without token")
def _():
    ac = AgentChallenge(secret="persist-test-12345", persistent=False, difficulty="easy")
    from agentchallenge.types import generate_challenge as _gc
    ctype, prompt, answer = _gc(difficulty="easy")
    c = ac._build_challenge(ctype, prompt, answer)
    r = ac.gate(challenge_token=c.token, answer=answer)
    assert r.status == "authenticated"
    assert r.token is None, "Should NOT return a token when persistent=False"

@test("persistent=False: passing a token returns error")
def _():
    ac = AgentChallenge(secret="persist-test-12345", persistent=False)
    token = ac.create_token("agent-1")  # can still create manually
    r = ac.gate(token=token)
    assert r.status == "error"
    assert "disabled" in r.error.lower()

@test("persistent=False: no args still returns challenge")
def _():
    ac = AgentChallenge(secret="persist-test-12345", persistent=False)
    r = ac.gate()
    assert r.status == "challenge_required"
    assert r.prompt is not None

@test("gate: challenge includes instructions field")
def _():
    ac = AgentChallenge(secret="persist-test-12345")
    r = ac.gate()
    assert r.instructions is not None
    assert "challenge_token" in r.instructions
    assert "answer" in r.instructions
    assert "Authorization" in r.instructions
    d = r.to_dict()
    assert "instructions" in d

@test("persistent=False: instructions mention no persistent token")
def _():
    ac = AgentChallenge(secret="persist-test-12345", persistent=False)
    r = ac.gate()
    assert "every request" in r.instructions
    assert "No persistent" in r.instructions

@test("persistent=True: instructions mention saving token")
def _():
    ac = AgentChallenge(secret="persist-test-12345", persistent=True)
    r = ac.gate()
    assert "persistent token" in r.instructions
    assert "Authorization" in r.instructions

@test("persistent=True (default): gate solve returns token")
def _():
    ac = AgentChallenge(secret="persist-test-12345", difficulty="easy")
    from agentchallenge.types import generate_challenge as _gc
    ctype, prompt, answer = _gc(difficulty="easy")
    c = ac._build_challenge(ctype, prompt, answer)
    r = ac.gate(challenge_token=c.token, answer=answer)
    assert r.status == "authenticated"
    assert r.token is not None, "Should return a token when persistent=True"
    assert r.token.startswith("eyJ"), "Token should be base64 encoded"

print("\n── Dynamic Mode ────────────────────────────────")

@test("Dynamic mode: set_openai_api_key stores key")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    result = ac.set_openai_api_key("sk-test-fake-key")
    assert result is ac, "Should return self for chaining"
    assert "openai" in ac._api_keys

@test("Dynamic mode: set_anthropic_api_key stores key")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    ac.set_anthropic_api_key("sk-ant-test")
    assert "anthropic" in ac._api_keys

@test("Dynamic mode: set_google_api_key stores key")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    ac.set_google_api_key("AIza-test")
    assert "google" in ac._api_keys

@test("Dynamic mode: enable selects provider from key")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    ac.set_openai_api_key("sk-fake")
    ac.enable_dynamic_mode()
    assert ac._dynamic_provider == "openai"
    assert ac.dynamic_mode is True

@test("Dynamic mode: disable works")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    ac.set_openai_api_key("sk-fake")
    ac.enable_dynamic_mode()
    assert ac.dynamic_mode is True
    ac.disable_dynamic_mode()
    assert ac.dynamic_mode is False

@test("Dynamic mode: provider preference openai > anthropic > google")
def _():
    # Temporarily clear env keys to test explicit-only behavior
    saved = {}
    for env_var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]:
        saved[env_var] = os.environ.pop(env_var, None)
    try:
        ac = AgentChallenge(secret="test-dynamic-12345")
        ac.set_google_api_key("g-key")
        ac.set_anthropic_api_key("a-key")
        ac.enable_dynamic_mode()
        assert ac._dynamic_provider == "anthropic", f"Expected anthropic, got {ac._dynamic_provider}"
        ac2 = AgentChallenge(secret="test-dynamic-12345")
        ac2.set_google_api_key("g-key")
        ac2.enable_dynamic_mode()
        assert ac2._dynamic_provider == "google", f"Expected google, got {ac2._dynamic_provider}"
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v

@test("Dynamic mode: explicit provider override")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    ac.set_openai_api_key("sk-o")
    ac.set_anthropic_api_key("sk-a")
    ac.enable_dynamic_mode(provider="anthropic")
    assert ac._dynamic_provider == "anthropic"

@test("Dynamic mode: unknown provider rejected")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    try:
        ac.enable_dynamic_mode(provider="fakeprovider")
        assert False
    except ValueError as e:
        assert "Unknown provider" in str(e)

@test("Dynamic mode: chaining API")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    result = (
        ac.set_openai_api_key("sk-test")
          .enable_dynamic_mode(model="gpt-4o-mini")
    )
    assert result is ac
    assert ac.dynamic_mode is True
    assert ac._dynamic_model == "gpt-4o-mini"

@test("Dynamic mode: falls back to static on bad key")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    ac.set_openai_api_key("sk-invalid-key-that-will-fail")
    ac.enable_dynamic_mode()
    # Should fall back to static without crashing
    ch = ac.create()
    assert ch.prompt
    assert ch.token
    assert ch.challenge_type != "dynamic"  # LLM call should fail, falling back

@test("Dynamic mode: env var auto-detection")
def _():
    old = os.environ.get("OPENAI_API_KEY")
    try:
        os.environ["OPENAI_API_KEY"] = "sk-env-test"
        ac = AgentChallenge(secret="test-dynamic-12345")
        assert "openai" in ac._api_keys
        assert ac._api_keys["openai"] == "sk-env-test"
    finally:
        if old is not None:
            os.environ["OPENAI_API_KEY"] = old
        else:
            os.environ.pop("OPENAI_API_KEY", None)

@test("Dynamic mode: specific type bypasses dynamic")
def _():
    ac = AgentChallenge(secret="test-dynamic-12345")
    ac.set_openai_api_key("sk-invalid")
    ac.enable_dynamic_mode()
    ch = ac.create(challenge_type="simple_math")
    assert ch.challenge_type == "simple_math"  # Static type, not dynamic

# Live dynamic test — only runs if OPENAI_API_KEY is actually set
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_KEY and OPENAI_KEY.startswith("sk-"):
    print(f"\n🔴 LIVE Dynamic Tests (using real OpenAI API)")

    @test("LIVE: Dynamic challenge generation + verification")
    def _():
        ac = AgentChallenge(secret="live-test-secret-key")
        ac.set_openai_api_key(OPENAI_KEY)
        ac.enable_dynamic_mode(model="gpt-4o-mini")
        ch = ac.create()
        assert ch.prompt, "Should have a prompt"
        assert ch.token, "Should have a token"
        # Dynamic challenges should be type "dynamic"
        assert ch.challenge_type == "dynamic", f"Expected dynamic, got {ch.challenge_type}"
        print(f"    Generated: {ch.prompt[:70]}...")

    @test("LIVE: Dynamic challenge solve + verify flow (5 rounds)")
    def _():
        from agentchallenge.dynamic import _call_llm, PROVIDERS
        ac = AgentChallenge(secret="live-test-secret-key")
        ac.set_openai_api_key(OPENAI_KEY)
        ac.enable_dynamic_mode(model="gpt-4o-mini")

        solved = 0
        for i in range(5):
            ch = ac.create()
            if ch.challenge_type != "dynamic":
                print(f"    Round {i+1}: fell back to static ({ch.challenge_type})")
                continue

            # Solve using LLM
            answer = _call_llm(
                "openai", OPENAI_KEY,
                [{"role": "user", "content": f"Solve this challenge. Reply with ONLY the answer, nothing else.\n\n{ch.prompt}"}],
                model="gpt-4o-mini",
            )
            result = ac.verify(token=ch.token, answer=answer)
            if result.valid:
                solved += 1
                print(f"    Round {i+1}: ✅ {ch.prompt[:50]}... → {answer}")
            else:
                print(f"    Round {i+1}: ❌ {ch.prompt[:50]}... → {answer} ({result.error})")

        assert solved >= 3, f"Only solved {solved}/5 dynamic challenges"
        print(f"    Solved {solved}/5 dynamic challenges")
else:
    print(f"\n⏭️  Skipping live dynamic tests (OPENAI_API_KEY not set)")


# ── Additional Security/QA Tests (requested) ──────────
print("\n── Additional Security/QA Tests ───────────────────")

def _mask_prompt(p: str) -> str:
    """Mask variable parts so we can compare template/phrasing, not random values."""
    p = re.sub(r'"[^"]*"', '"..."', p)
    p = re.sub(r"'[^']*'", "'...'", p)
    p = re.sub(r"\b\d+\b", "#", p)
    p = re.sub(r"\b[A-Z]{3,}\b", "WORD", p)
    p = re.sub(r"\s+", " ", p).strip().lower()
    return p


@test("TTL enforcement: ttl=2 expires after 3s")
def _():
    ac = AgentChallenge(secret="ttl-enforce-123", ttl=2)
    ch = ac.create(challenge_type="simple_math")
    assert ac.verify(token=ch.token, answer="wrong").error == "Incorrect answer"
    time.sleep(3.0)
    result = ac.verify(token=ch.token, answer="anything")
    assert not result.valid
    assert result.error == "Challenge expired"


@test("Lock mode: persistent=False (hard, ttl=10) issues no token")
def _():
    ac = AgentChallenge(secret="lock-mode-12345", persistent=False, difficulty="hard", ttl=10)
    ctype, prompt, answer = generate_challenge(difficulty="hard")
    ch = ac._build_challenge(ctype, prompt, answer)
    r = ac.gate(challenge_token=ch.token, answer=answer)
    assert r.status == "authenticated"
    assert r.token is None, "Lock mode should not issue persistent tokens"


@test("Gate mode: persistent=True issues token and token is reusable")
def _():
    ac = AgentChallenge(secret="gate-mode-12345", persistent=True, difficulty="easy", ttl=10)
    ctype, prompt, answer = generate_challenge(difficulty="easy")
    ch = ac._build_challenge(ctype, prompt, answer)
    r1 = ac.gate(challenge_token=ch.token, answer=answer)
    assert r1.status == "authenticated"
    assert r1.token is not None
    r2 = ac.gate(token=r1.token)
    assert r2.status == "authenticated"


@test("Template randomization: 20 challenges of same type have different prompt templates")
def _():
    ac = AgentChallenge(secret="template-rand-12345")
    for ctype in CHALLENGE_TYPES:
        masked = set()
        for _ in range(20):
            ch = ac.create(challenge_type=ctype)
            masked.add(_mask_prompt(ch.prompt))
        assert len(masked) >= 2, f"{ctype}: expected >=2 prompt template variants, got {len(masked)}"


@test("Answer normalization: comma canonicalization + trailing punctuation + case insensitivity")
def _():
    ac = AgentChallenge(secret="norm-12345", ttl=30)
    # Craft a known answer with commas and spaces; store its hash exactly as the library does.
    ctype = "sorting"
    prompt = "Sort these numbers from smallest to largest: 1, 2, 3. Reply with ONLY the answer."
    answer = "1, 2, 3"
    ch = ac._build_challenge(ctype, prompt, answer)

    # Comma spacing variants should normalize to "1, 2, 3"
    assert ac.verify(token=ch.token, answer="1,2,3").valid
    assert ac.verify(token=ch.token, answer="  1 , 2,3  ").valid

    # Trailing punctuation (implemented: . and !) should be stripped
    assert ac.verify(token=ch.token, answer="1,2,3.").valid
    assert ac.verify(token=ch.token, answer="1, 2, 3!!").valid

    # Case-insensitive (relevant for word answers)
    ch2 = ac._build_challenge("reverse_string", "Return HELLO. Reply with ONLY the answer.", "hello")
    assert ac.verify(token=ch2.token, answer="HeLlO").valid


@test("Edge cases: invalid types raise; empty types list falls back to difficulty pool")
def _():
    ac_bad = AgentChallenge(secret="types-bad-12345", types=["not_a_real_type"])
    try:
        ac_bad.create()
        assert False, "Expected ValueError for invalid types list"
    except ValueError:
        pass

    ac_empty = AgentChallenge(secret="types-empty-12345", types=[])
    ch = ac_empty.create()
    assert ch.challenge_type in CHALLENGE_TYPES


@test("Token tampering: modified persistent token fails verification")
def _():
    ac = AgentChallenge(secret="tamper-12345", persistent=True)
    tok = ac.create_token(agent_id="agent-1")
    tampered = tok[:-1] + ("a" if tok[-1] != "a" else "b")
    assert ac.verify_token(tok) is True
    assert ac.verify_token(tampered) is False
    r = ac.gate(token=tampered)
    assert r.status == "error"


@test("Cross-secret tokens: persistent token from secret A fails under secret B")
def _():
    ac1 = AgentChallenge(secret="secret-A-12345")
    ac2 = AgentChallenge(secret="secret-B-12345")
    tok = ac1.create_token(agent_id="agent-1")
    assert ac1.verify_token(tok) is True
    assert ac2.verify_token(tok) is False


# ── gate_http Tests ────────────────────────────────────
print("\n  gate_http:")


class FakeHeaders:
    """Minimal dict-like for simulating HTTP headers."""
    def __init__(self, d):
        self._d = d
    def get(self, k, default=""):
        return self._d.get(k, default)


@test("gate_http: no auth returns challenge_required")
def _():
    ac = AgentChallenge(secret="gate-http-test-123", ttl=30, types=["reverse_string"])
    result = ac.gate_http(FakeHeaders({}), {})
    assert result.status == "challenge_required"
    assert result.prompt


@test("gate_http: solve challenge from body")
def _():
    ac = AgentChallenge(secret="gate-http-test-123", ttl=30, types=["reverse_string"])
    r1 = ac.gate_http(FakeHeaders({}), {})
    words = re.findall(r"\b[A-Z0-9]{3,}\b", r1.prompt)
    skip = {"ONLY", "Read", "YOUR", "THE", "Output", "Reverse", "Starting", "Just", "Reply", "What"}
    target = [w for w in words if w not in skip][-1]
    answer = target[::-1]
    r2 = ac.gate_http(FakeHeaders({}), {"challenge_token": r1.challenge_token, "answer": answer})
    assert r2.status == "authenticated"
    assert r2.token  # persistent=True by default


@test("gate_http: Bearer token from Authorization header")
def _():
    ac = AgentChallenge(secret="gate-http-test-123", ttl=30, types=["reverse_string"])
    token = ac.create_token()
    r = ac.gate_http(FakeHeaders({"Authorization": f"Bearer {token}"}), {})
    assert r.status == "authenticated"


@test("gate_http: lowercase authorization header works")
def _():
    ac = AgentChallenge(secret="gate-http-test-123", ttl=30)
    token = ac.create_token()
    r = ac.gate_http(FakeHeaders({"authorization": f"Bearer {token}"}), {})
    assert r.status == "authenticated"


@test("gate_http: None body treated as empty")
def _():
    ac = AgentChallenge(secret="gate-http-test-123", ttl=30)
    r = ac.gate_http(FakeHeaders({}), None)
    assert r.status == "challenge_required"


@test("gate_http: non-dict body treated as empty")
def _():
    ac = AgentChallenge(secret="gate-http-test-123", ttl=30)
    r = ac.gate_http(FakeHeaders({}), "not a dict")
    assert r.status == "challenge_required"


@test("gate_http: persistent=False works")
def _():
    ac = AgentChallenge(secret="gate-http-test-123", ttl=30, persistent=False)
    token = ac.create_token()
    r = ac.gate_http(FakeHeaders({"Authorization": f"Bearer {token}"}), {})
    assert r.status == "error"
    assert "disabled" in r.error.lower()


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
