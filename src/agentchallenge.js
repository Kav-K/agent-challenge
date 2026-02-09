/**
 * agent-challenge v0.2.0 (JavaScript/Node.js port)
 *
 * LLM-solvable challenge-response authentication for AI agent APIs.
 * 12 challenge types with fully randomized inputs — no fixed word lists.
 */

import crypto from 'crypto';

// ── Helpers ──────────────────────────────────────────

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

const CONSONANTS = 'BCDFGHJKLMNPQRSTVWXYZ';
const VOWELS = 'AEIOU';
const UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const DIGITS = '0123456789';
const LETTERS_ALL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

function randChars(pool, n) { let s = ''; for (let i = 0; i < n; i++) s += pool[randInt(0, pool.length - 1)]; return s; }
function pronounceable(n) { let s = ''; for (let i = 0; i < n; i++) s += pick(i % 2 === 0 ? CONSONANTS : VOWELS); return s; }

function rot13(text) {
  return text.replace(/[A-Za-z]/g, c => {
    const base = c <= 'Z' ? 65 : 97;
    return String.fromCharCode(((c.charCodeAt(0) - base + 13) % 26) + base);
  });
}

function caesarEncode(text, shift) {
  return text.replace(/[A-Z]/g, c => String.fromCharCode(((c.charCodeAt(0) - 65 + shift) % 26) + 65));
}

const NUM_WORDS = {
  0:'zero',1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',
  11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',16:'sixteen',17:'seventeen',18:'eighteen',
  19:'nineteen',20:'twenty'
};

// ── Challenge Types ──────────────────────────────────

const CHALLENGE_TYPES = {
  reverse_string() {
    const variant = pick(['pronounceable', 'random', 'mixed']);
    let word;
    if (variant === 'pronounceable') word = pronounceable(randInt(5, 9));
    else if (variant === 'random') word = randChars(UPPER, randInt(5, 8));
    else word = randChars(UPPER + DIGITS, randInt(5, 8));
    return { prompt: `Reverse the following string (reply with ONLY the reversed text, nothing else): ${word}`, answer: word.split('').reverse().join('').toLowerCase() };
  },

  simple_math() {
    const op = pick(['+', '+', '-', '×', '++', '--']);
    let prompt, answer;
    if (op === '+') { const a = randInt(10, 999), b = randInt(10, 999); answer = a + b; prompt = `What is ${a} + ${b}?`; }
    else if (op === '-') { const a = randInt(100, 999), b = randInt(10, a - 1); answer = a - b; prompt = `What is ${a} - ${b}?`; }
    else if (op === '×') { const a = randInt(2, 30), b = randInt(2, 30); answer = a * b; prompt = `What is ${a} × ${b}?`; }
    else if (op === '++') { const a = randInt(10, 300), b = randInt(10, 300), c = randInt(10, 300); answer = a + b + c; prompt = `What is ${a} + ${b} + ${c}?`; }
    else { const a = randInt(500, 999), b = randInt(10, 200), c = randInt(10, Math.min(200, a - b - 1)); answer = a - b - c; prompt = `What is ${a} - ${b} - ${c}?`; }
    return { prompt: prompt + ' Reply with ONLY the number, nothing else.', answer: String(answer) };
  },

  letter_position() {
    const word = randChars(UPPER, randInt(3, 4));
    const total = [...word].reduce((s, c) => s + (c.charCodeAt(0) - 64), 0);
    return { prompt: `If A=1, B=2, C=3, ... Z=26, what is the sum of the letter values in "${word}"? Reply with ONLY the number, nothing else.`, answer: String(total) };
  },

  rot13() {
    const word = pronounceable(randInt(4, 7));
    const encoded = rot13(word);
    return { prompt: `Decode this ROT13-encoded string (each letter shifts 13 places back in the alphabet): ${encoded}\nReply with ONLY the decoded word, nothing else.`, answer: word.toLowerCase() };
  },

  pattern() {
    const ptype = pick(['add', 'multiply', 'add_growing', 'squares', 'triangular']);
    let display, answer;
    if (ptype === 'add') {
      const start = randInt(1, 50), step = randInt(2, 15);
      display = Array.from({length: 5}, (_, i) => start + step * i); answer = display[4] + step;
    } else if (ptype === 'multiply') {
      const base = pick([2, 3, 4, 5]), se = randInt(0, 2);
      display = Array.from({length: 5}, (_, i) => base ** (se + i)); answer = base ** (se + 5);
    } else if (ptype === 'squares') {
      const off = randInt(0, 10), sn = randInt(1, 5);
      display = Array.from({length: 5}, (_, i) => (sn + i) ** 2 + off); answer = (sn + 5) ** 2 + off;
    } else if (ptype === 'triangular') {
      const start = randInt(1, 10), si = randInt(2, 4);
      display = [start]; let cs = si;
      for (let j = 0; j < 4; j++) { display.push(display[display.length-1] + cs); cs += si; }
      answer = display[4] + cs;
    } else {
      const start = randInt(1, 20), is_ = randInt(1, 5);
      display = [start]; for (let i = 0; i < 4; i++) display.push(display[display.length-1] + is_ + i);
      answer = display[4] + is_ + 4;
    }
    return { prompt: `What comes next in this sequence: ${display.join(', ')}, ? Reply with ONLY the number, nothing else.`, answer: String(answer) };
  },

  extract_letters() {
    const word = randChars(UPPER, randInt(4, 6));
    const n = pick([2, 3]);
    let mixed = '';
    for (let i = 0; i < word.length; i++) {
      mixed += word[i];
      if (i < word.length - 1) for (let j = 0; j < n - 1; j++) mixed += CONSONANTS[randInt(0, CONSONANTS.length - 1)];
    }
    const ordinal = n === 2 ? '2nd' : '3rd';
    return { prompt: `Extract every ${ordinal} letter from this string, starting from the 1st character: ${mixed}\nReply with ONLY the extracted letters as one word, nothing else.`, answer: word.toLowerCase() };
  },

  word_math() {
    const v = pick(['digit_to_word', 'char_count', 'vowel_count', 'digit_sum']);
    if (v === 'digit_to_word') {
      const a = randInt(1, 10), b = randInt(1, 10);
      return { prompt: `What is ${a} + ${b}? Write the answer as a word (e.g., "twelve"), not a number. Reply with ONLY the word, nothing else.`, answer: NUM_WORDS[a + b] };
    } else if (v === 'char_count') {
      const w = randChars(UPPER, randInt(4, 8));
      return { prompt: `How many letters are in the string "${w}"? Reply with ONLY the number, nothing else.`, answer: String(w.length) };
    } else if (v === 'vowel_count') {
      const w = randChars(UPPER, randInt(5, 9));
      return { prompt: `How many vowels (A, E, I, O, U) are in "${w}"? Reply with ONLY the number, nothing else.`, answer: String([...w].filter(c => 'AEIOU'.includes(c)).length) };
    } else {
      const num = randInt(100, 9999);
      return { prompt: `What is the sum of the digits of ${num}? Reply with ONLY the number, nothing else.`, answer: String([...String(num)].reduce((s, d) => s + Number(d), 0)) };
    }
  },

  caesar() {
    const word = pronounceable(randInt(4, 7));
    const shift = pick([3, 5, 7, 11]);
    const encoded = caesarEncode(word, shift);
    return { prompt: `Decode this Caesar cipher (each letter is shifted ${shift} positions forward in the alphabet): ${encoded}\nShift each letter ${shift} positions BACKWARD to decode. Reply with ONLY the decoded word, nothing else.`, answer: word.toLowerCase() };
  },

  sorting() {
    const v = pick(['sort_letters', 'sort_numbers', 'sort_reverse']);
    if (v === 'sort_letters') {
      const w = randChars(UPPER, randInt(5, 8));
      return { prompt: `Sort these letters in alphabetical order: ${w}\nReply with ONLY the sorted letters as one word, nothing else.`, answer: [...w].sort().join('').toLowerCase() };
    } else if (v === 'sort_numbers') {
      const nums = []; const seen = new Set();
      while (nums.length < randInt(5, 7)) { const n = randInt(1, 99); if (!seen.has(n)) { nums.push(n); seen.add(n); } }
      return { prompt: `Sort these numbers from smallest to largest: ${nums.join(', ')}\nReply with ONLY the sorted numbers separated by commas, nothing else.`, answer: [...nums].sort((a, b) => a - b).join(', ') };
    } else {
      const w = randChars(UPPER, randInt(5, 7));
      return { prompt: `Sort these letters in REVERSE alphabetical order (Z first, A last): ${w}\nReply with ONLY the sorted letters as one word, nothing else.`, answer: [...w].sort().reverse().join('').toLowerCase() };
    }
  },

  counting() {
    const v = pick(['count_letter', 'count_consonants', 'count_digits', 'count_upper']);
    if (v === 'count_letter') {
      const target = UPPER[randInt(0, 25)];
      const len = randInt(10, 18);
      let chars = Array(randInt(2, 5)).fill(target);
      while (chars.length < len) chars.push(UPPER[randInt(0, 25)]);
      chars = chars.sort(() => Math.random() - 0.5);
      const text = chars.join('');
      return { prompt: `How many times does the letter "${target}" appear in "${text}"? Reply with ONLY the number, nothing else.`, answer: String(text.split(target).length - 1) };
    } else if (v === 'count_consonants') {
      const w = randChars(UPPER, randInt(6, 10));
      return { prompt: `How many consonants (non-vowel letters) are in "${w}"? Reply with ONLY the number, nothing else.`, answer: String([...w].filter(c => !'AEIOU'.includes(c)).length) };
    } else if (v === 'count_digits') {
      const d = randChars(DIGITS, randInt(8, 14));
      const target = d[randInt(0, d.length - 1)];
      return { prompt: `How many times does the digit "${target}" appear in "${d}"? Reply with ONLY the number, nothing else.`, answer: String(d.split(target).length - 1) };
    } else {
      const text = randChars(LETTERS_ALL, randInt(10, 16));
      return { prompt: `How many UPPERCASE letters are in "${text}"? Reply with ONLY the number, nothing else.`, answer: String([...text].filter(c => c >= 'A' && c <= 'Z').length) };
    }
  },

  transform() {
    const v = pick(['remove_vowels', 'remove_consonants', 'first_letters', 'last_letters']);
    if (v === 'remove_vowels') {
      const w = pronounceable(randInt(5, 8));
      return { prompt: `Remove all vowels (A, E, I, O, U) from "${w}".\nReply with ONLY the remaining letters, nothing else.`, answer: [...w].filter(c => !'AEIOU'.includes(c)).join('').toLowerCase() };
    } else if (v === 'remove_consonants') {
      let w = randChars(UPPER, randInt(6, 10));
      const vowels = [...w].filter(c => 'AEIOU'.includes(c)).join('');
      if (!vowels) return CHALLENGE_TYPES.transform(); // retry
      return { prompt: `Remove all consonants from "${w}" and keep only the vowels (A, E, I, O, U).\nReply with ONLY the remaining vowels, nothing else.`, answer: vowels.toLowerCase() };
    } else if (v === 'first_letters') {
      const words = Array.from({length: randInt(4, 7)}, () => { let w = randChars('abcdefghijklmnopqrstuvwxyz', randInt(3, 7)); return w[0].toUpperCase() + w.slice(1); });
      return { prompt: `What do the first letters of each word spell: "${words.join(' ')}"?\nReply with ONLY the letters as one word, nothing else.`, answer: words.map(w => w[0]).join('').toLowerCase() };
    } else {
      const words = Array.from({length: randInt(4, 6)}, () => { let w = randChars('abcdefghijklmnopqrstuvwxyz', randInt(3, 6)); return w[0].toUpperCase() + w.slice(1); });
      return { prompt: `What do the LAST letters of each word spell: "${words.join(' ')}"?\nReply with ONLY the letters as one word, nothing else.`, answer: words.map(w => w[w.length - 1]).join('').toLowerCase() };
    }
  },

  binary() {
    const v = pick(['binary_to_decimal', 'decimal_to_binary', 'digit_sum']);
    if (v === 'binary_to_decimal') {
      const num = randInt(1, 63);
      return { prompt: `Convert binary ${num.toString(2)} to decimal. Reply with ONLY the decimal number, nothing else.`, answer: String(num) };
    } else if (v === 'decimal_to_binary') {
      const num = randInt(1, 31);
      return { prompt: `Convert the decimal number ${num} to binary. Reply with ONLY the binary digits (no prefix like 0b), nothing else.`, answer: num.toString(2) };
    } else {
      const num = randInt(1000, 99999);
      return { prompt: `What is the sum of all digits in ${num}? Reply with ONLY the number, nothing else.`, answer: String([...String(num)].reduce((s, d) => s + Number(d), 0)) };
    }
  },
};

const DIFFICULTY_MAP = {
  easy: ['reverse_string', 'simple_math', 'pattern', 'counting'],
  medium: ['reverse_string', 'simple_math', 'rot13', 'letter_position', 'extract_letters', 'pattern', 'counting', 'sorting', 'binary'],
  hard: Object.keys(CHALLENGE_TYPES),
};


// ── Token Helpers ────────────────────────────────────

function hmacSign(data, secret) { return crypto.createHmac('sha256', secret).update(data).digest('hex'); }
function encodeToken(payload, secret) {
  const data = Buffer.from(JSON.stringify(payload)).toString('base64url');
  return `${data}.${hmacSign(data, secret)}`;
}
function decodeToken(token, secret) {
  if (!token || !token.includes('.')) throw new Error('Invalid token format');
  const idx = token.lastIndexOf('.');
  const data = token.slice(0, idx), sig = token.slice(idx + 1);
  const expected = hmacSign(data, secret);
  if (!crypto.timingSafeEqual(Buffer.from(sig, 'hex'), Buffer.from(expected, 'hex'))) throw new Error('Invalid token signature');
  return JSON.parse(Buffer.from(data, 'base64url').toString());
}
function hashAnswer(answer) { return crypto.createHash('sha256').update(answer, 'utf8').digest('hex'); }
function normalizeAnswer(answer) {
  if (typeof answer !== 'string') return '';
  let s = answer.trim().toLowerCase();
  if (s.length >= 2 && s[0] === s[s.length - 1] && (s[0] === '"' || s[0] === "'")) s = s.slice(1, -1).trim();
  return s.replace(/\s+/g, ' ');
}


// ── Main Class ───────────────────────────────────────

export class AgentChallenge {
  constructor({ secret, difficulty = 'easy', ttl = 300, types = null } = {}) {
    if (!secret || secret.length < 8) throw new Error('Secret must be at least 8 characters');
    this._secret = secret;
    this._difficulty = difficulty;
    this._ttl = ttl;
    this._types = types;
  }

  create(challengeType = null) {
    let typeName;
    if (challengeType) {
      if (!CHALLENGE_TYPES[challengeType]) throw new Error(`Unknown type: ${challengeType}`);
      typeName = challengeType;
    } else {
      const pool = this._types || DIFFICULTY_MAP[this._difficulty] || DIFFICULTY_MAP.easy;
      typeName = pick(pool);
    }
    const { prompt, answer } = CHALLENGE_TYPES[typeName]();
    const id = 'ch_' + crypto.randomBytes(12).toString('hex');
    const now = Math.floor(Date.now() / 1000);
    const payload = { id, type: typeName, answer_hash: hashAnswer(answer), created_at: now, expires_at: now + this._ttl };
    const token = encodeToken(payload, this._secret);
    return { id, prompt, token, expires_at: now + this._ttl, challenge_type: typeName, toDict() { return { id, prompt, token, expires_in: Math.max(0, payload.expires_at - Math.floor(Date.now() / 1000)), type: 'reasoning' }; } };
  }

  verify(token, answer) {
    const start = Date.now();
    let payload;
    try { payload = decodeToken(token, this._secret); } catch (e) { return { valid: false, error: e.message }; }
    if (Math.floor(Date.now() / 1000) > payload.expires_at) return { valid: false, error: 'Challenge expired' };
    const normalized = normalizeAnswer(answer);
    if (!normalized) return { valid: false, error: 'Empty answer' };
    if (hashAnswer(normalized) === payload.answer_hash) return { valid: true, challenge_type: payload.type, elapsed_ms: Date.now() - start };
    return { valid: false, error: 'Incorrect answer', challenge_type: payload.type };
  }
}

export { CHALLENGE_TYPES, DIFFICULTY_MAP };
