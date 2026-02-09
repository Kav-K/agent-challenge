/**
 * agent-challenge v0.2.0 (JavaScript/Node.js port)
 *
 * LLM-solvable challenge-response authentication for AI agent APIs.
 * 12 static challenge types with fully randomized inputs.
 * Optional dynamic mode: LLM-generated challenges with self-verification.
 *
 * ⚠️ Dynamic mode adds 2 LLM API requests per challenge generation.
 */

import crypto from 'crypto';
import { request as httpsRequest } from 'https';

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

// ── Reply instruction templates (randomized per challenge) ───

const REPLY_INSTRUCTIONS = [
  "Reply with ONLY the answer, nothing else.",
  "Respond with just the answer.",
  "Give me only the answer.",
  "Your response should contain nothing but the answer.",
  "Write only the final answer.",
  "Output just the answer, no explanation.",
  "Answer with a single value only.",
  "Just the answer please, nothing more.",
];
function ri() { return pick(REPLY_INSTRUCTIONS); }

// ── Challenge Types (with randomized prompt templates) ───

const CHALLENGE_TYPES = {
  reverse_string() {
    const variant = pick(['pronounceable', 'random', 'mixed']);
    let word;
    if (variant === 'pronounceable') word = pronounceable(randInt(5, 9));
    else if (variant === 'random') word = randChars(UPPER, randInt(5, 8));
    else word = randChars(UPPER + DIGITS, randInt(5, 8));
    const templates = [
      w => `Reverse the following string: ${w}.`,
      w => `Write the characters of ${w} in reverse order.`,
      w => `Spell ${w} backwards.`,
      w => `If you flip the string ${w} end-to-end, what do you get?`,
      w => `Read ${w} from right to left and write what you see.`,
      w => `Take the word ${w} and reverse every character.`,
      w => `Starting from the last character to the first, rewrite ${w}.`,
      w => `What is the result of reversing all characters in ${w}?`,
    ];
    return { prompt: pick(templates)(word) + ' ' + ri(), answer: word.split('').reverse().join('').toLowerCase() };
  },

  simple_math() {
    const op = pick(['+', '+', '-', '×', '++', '--']);
    let prompt, answer;
    if (op === '+') {
      const a = randInt(10, 999), b = randInt(10, 999); answer = a + b;
      prompt = pick([`What is ${a} + ${b}?`, `Calculate the sum of ${a} and ${b}.`, `Add ${a} to ${b}. What do you get?`, `If you combine ${a} and ${b}, what is the total?`]);
    } else if (op === '-') {
      const a = randInt(100, 999), b = randInt(10, a - 1); answer = a - b;
      prompt = pick([`What is ${a} - ${b}?`, `Subtract ${b} from ${a}.`, `If you take ${b} away from ${a}, what remains?`, `Calculate ${a} minus ${b}.`]);
    } else if (op === '×') {
      const a = randInt(2, 30), b = randInt(2, 30); answer = a * b;
      prompt = pick([`What is ${a} × ${b}?`, `Multiply ${a} by ${b}.`, `Calculate the product of ${a} and ${b}.`, `What do you get when you multiply ${a} times ${b}?`]);
    } else if (op === '++') {
      const a = randInt(10, 300), b = randInt(10, 300), c = randInt(10, 300); answer = a + b + c;
      prompt = pick([`What is ${a} + ${b} + ${c}?`, `Add together ${a}, ${b}, and ${c}.`, `Find the sum of these three numbers: ${a}, ${b}, ${c}.`]);
    } else {
      const a = randInt(500, 999), b = randInt(10, 200), c = randInt(10, Math.min(200, a - b - 1)); answer = a - b - c;
      prompt = pick([`What is ${a} - ${b} - ${c}?`, `Start with ${a}, subtract ${b}, then subtract ${c}.`, `Take ${a}, remove ${b}, then remove another ${c}. What's left?`]);
    }
    return { prompt: prompt + ' ' + ri(), answer: String(answer) };
  },

  letter_position() {
    const word = randChars(UPPER, randInt(3, 4));
    const total = [...word].reduce((s, c) => s + (c.charCodeAt(0) - 64), 0);
    const templates = [
      w => `If A=1, B=2, C=3, ... Z=26, what is the sum of the letter values in "${w}"?`,
      w => `Assign each letter a number (A=1, B=2, through Z=26). Add up the values of all letters in "${w}".`,
      w => `Using the mapping A→1, B→2, C→3, ..., Z→26, calculate the total value of the letters in "${w}".`,
      w => `Each letter has a position in the alphabet (A=1, Z=26). What is the sum of positions for the letters in "${w}"?`,
    ];
    return { prompt: pick(templates)(word) + ' ' + ri(), answer: String(total) };
  },

  rot13() {
    const word = pronounceable(randInt(4, 7));
    const encoded = rot13(word);
    const templates = [
      e => `Decode this ROT13-encoded string (each letter shifts 13 places back in the alphabet): ${e}`,
      e => `Apply ROT13 decoding to the text: ${e}`,
      e => `The following text was encoded with ROT13. Decode it: ${e}`,
      e => `Shift each letter in ${e} by 13 positions in the alphabet to decode it.`,
    ];
    return { prompt: pick(templates)(encoded) + ' ' + ri(), answer: word.toLowerCase() };
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
    const seq = display.join(', ');
    const templates = [
      s => `What comes next in this sequence: ${s}, ?`,
      s => `Find the next number: ${s}, ?`,
      s => `Continue this pattern: ${s}, ?`,
      s => `What number follows this sequence: ${s}, ?`,
      s => `Identify the next value in the series: ${s}, ?`,
    ];
    return { prompt: pick(templates)(seq) + ' ' + ri(), answer: String(answer) };
  },

  extract_letters() {
    const word = randChars(UPPER, randInt(4, 6));
    const n = pick([2, 3]);
    let mixed = '';
    for (let i = 0; i < word.length; i++) {
      mixed += word[i];
      if (i < word.length - 1) for (let j = 0; j < n - 1; j++) mixed += CONSONANTS[randInt(0, CONSONANTS.length - 1)];
    }
    const templates2 = [
      m => `Extract every 2nd letter from this string, starting from the 1st character: ${m}`,
      m => `Take every other character from ${m}, beginning with the first.`,
      m => `From the string ${m}, pick characters at positions 1, 3, 5, 7... What do you get?`,
    ];
    const templates3 = [
      m => `Extract every 3rd letter from this string, starting from the 1st character: ${m}`,
      m => `From ${m}, take the 1st, 4th, 7th, 10th... characters.`,
      m => `Pick every third character from ${m}, starting at position 1.`,
    ];
    return { prompt: pick(n === 2 ? templates2 : templates3)(mixed) + ' ' + ri(), answer: word.toLowerCase() };
  },

  word_math() {
    const v = pick(['digit_to_word', 'char_count', 'vowel_count', 'digit_sum']);
    if (v === 'digit_to_word') {
      const a = randInt(1, 10), b = randInt(1, 10);
      const t = pick([
        (x,y) => `What is ${x} + ${y}? Write the answer as a word (e.g., "twelve"), not a number.`,
        (x,y) => `Add ${x} and ${y}. Spell out the answer as an English word.`,
        (x,y) => `Calculate ${x} + ${y} and write the result as a word, not a digit.`,
      ]);
      return { prompt: t(a, b) + ' ' + ri(), answer: NUM_WORDS[a + b] };
    } else if (v === 'char_count') {
      const w = randChars(UPPER, randInt(4, 8));
      const t = pick([
        x => `How many characters are in the string "${x}"?`,
        x => `Count the total number of letters in "${x}".`,
        x => `What is the length of the string "${x}"?`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: String(w.length) };
    } else if (v === 'vowel_count') {
      const w = randChars(UPPER, randInt(5, 9));
      const t = pick([
        x => `How many vowels (A, E, I, O, U) are in "${x}"?`,
        x => `Count the vowels in the string "${x}".`,
        x => `In the text "${x}", how many letters are vowels (A, E, I, O, U)?`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: String([...w].filter(c => 'AEIOU'.includes(c)).length) };
    } else {
      const num = randInt(100, 9999);
      const t = pick([
        n => `What is the sum of the digits of ${n}?`,
        n => `Add up each individual digit in the number ${n}.`,
        n => `Take the number ${n} and sum its digits together.`,
      ]);
      return { prompt: t(num) + ' ' + ri(), answer: String([...String(num)].reduce((s, d) => s + Number(d), 0)) };
    }
  },

  caesar() {
    const word = pronounceable(randInt(4, 7));
    const shift = pick([3, 5, 7, 11]);
    const encoded = caesarEncode(word, shift);
    const templates = [
      (e,s) => `Decode this Caesar cipher (each letter is shifted ${s} positions forward in the alphabet): ${e}\nShift each letter ${s} positions BACKWARD to decode.`,
      (e,s) => `The text ${e} was encrypted with a Caesar shift of ${s}. Decrypt it by shifting each letter back by ${s}.`,
      (e,s) => `Apply a reverse Caesar shift of ${s} to decode: ${e}`,
      (e,s) => `This message was encoded by shifting each letter forward by ${s} in the alphabet: ${e}. What is the original text?`,
    ];
    return { prompt: pick(templates)(encoded, shift) + ' ' + ri(), answer: word.toLowerCase() };
  },

  sorting() {
    const v = pick(['sort_letters', 'sort_numbers', 'sort_reverse']);
    if (v === 'sort_letters') {
      const w = randChars(UPPER, randInt(5, 8));
      const t = pick([x => `Sort these letters in alphabetical order: ${x}`, x => `Arrange the letters ${x} from A to Z.`, x => `Put these letters in alphabetical sequence: ${x}`]);
      return { prompt: t(w) + ' ' + ri(), answer: [...w].sort().join('').toLowerCase() };
    } else if (v === 'sort_numbers') {
      const nums = []; const seen = new Set();
      while (nums.length < randInt(5, 7)) { const n = randInt(1, 99); if (!seen.has(n)) { nums.push(n); seen.add(n); } }
      const t = pick([x => `Sort these numbers from smallest to largest: ${x}`, x => `Arrange in ascending order: ${x}`, x => `Put these numbers in order from lowest to highest: ${x}`]);
      return { prompt: t(nums.join(', ')) + ' ' + ri(), answer: [...nums].sort((a, b) => a - b).join(', ') };
    } else {
      const w = randChars(UPPER, randInt(5, 7));
      const t = pick([x => `Sort these letters in REVERSE alphabetical order (Z first, A last): ${x}`, x => `Arrange the letters ${x} from Z to A.`, x => `Put these letters in reverse alphabetical order: ${x}`]);
      return { prompt: t(w) + ' ' + ri(), answer: [...w].sort().reverse().join('').toLowerCase() };
    }
  },

  counting() {
    const v = pick(['count_letter', 'count_consonants', 'count_digits', 'count_upper']);
    if (v === 'count_letter') {
      const target = UPPER[randInt(0, 25)], len = randInt(10, 18);
      let chars = Array(randInt(2, 5)).fill(target);
      while (chars.length < len) chars.push(UPPER[randInt(0, 25)]);
      chars = chars.sort(() => Math.random() - 0.5);
      const text = chars.join('');
      const t = pick([
        (tg,tx) => `How many times does the letter "${tg}" appear in "${tx}"?`,
        (tg,tx) => `Count the occurrences of "${tg}" in the string "${tx}".`,
        (tg,tx) => `In "${tx}", how many "${tg}" characters are there?`,
      ]);
      return { prompt: t(target, text) + ' ' + ri(), answer: String(text.split(target).length - 1) };
    } else if (v === 'count_consonants') {
      const w = randChars(UPPER, randInt(6, 10));
      const t = pick([x => `How many consonants (non-vowel letters) are in "${x}"?`, x => `Count all consonants in the string "${x}".`, x => `In "${x}", how many letters are NOT vowels?`]);
      return { prompt: t(w) + ' ' + ri(), answer: String([...w].filter(c => !'AEIOU'.includes(c)).length) };
    } else if (v === 'count_digits') {
      const d = randChars(DIGITS, randInt(8, 14)), target = d[randInt(0, d.length - 1)];
      const t = pick([(tg,dd) => `How many times does the digit "${tg}" appear in "${dd}"?`, (tg,dd) => `Count how often "${tg}" occurs in the number string "${dd}".`]);
      return { prompt: t(target, d) + ' ' + ri(), answer: String(d.split(target).length - 1) };
    } else {
      const text = randChars(LETTERS_ALL, randInt(10, 16));
      const t = pick([x => `How many UPPERCASE letters are in "${x}"?`, x => `Count the capital letters in "${x}".`, x => `In the mixed-case string "${x}", how many characters are uppercase?`]);
      return { prompt: t(text) + ' ' + ri(), answer: String([...text].filter(c => c >= 'A' && c <= 'Z').length) };
    }
  },

  transform() {
    const v = pick(['remove_vowels', 'remove_consonants', 'first_letters', 'last_letters']);
    if (v === 'remove_vowels') {
      const w = pronounceable(randInt(5, 8));
      const t = pick([x => `Remove all vowels (A, E, I, O, U) from "${x}".`, x => `Delete every vowel from the string "${x}". What remains?`, x => `Strip out A, E, I, O, and U from "${x}".`]);
      return { prompt: t(w) + ' ' + ri(), answer: [...w].filter(c => !'AEIOU'.includes(c)).join('').toLowerCase() };
    } else if (v === 'remove_consonants') {
      let w = randChars(UPPER, randInt(6, 10));
      const vowels = [...w].filter(c => 'AEIOU'.includes(c)).join('');
      if (!vowels) return CHALLENGE_TYPES.transform();
      const t = pick([x => `Remove all consonants from "${x}" and keep only the vowels (A, E, I, O, U).`, x => `Extract only the vowels from "${x}".`, x => `From the string "${x}", delete every consonant and keep only vowels.`]);
      return { prompt: t(w) + ' ' + ri(), answer: vowels.toLowerCase() };
    } else if (v === 'first_letters') {
      const words = Array.from({length: randInt(4, 7)}, () => { let w = randChars('abcdefghijklmnopqrstuvwxyz', randInt(3, 7)); return w[0].toUpperCase() + w.slice(1); });
      const s = words.join(' ');
      const t = pick([x => `What do the first letters of each word spell: "${x}"?`, x => `Take the initial letter of every word in "${x}" and combine them.`, x => `Form an acronym from: "${x}".`]);
      return { prompt: t(s) + ' ' + ri(), answer: words.map(w => w[0]).join('').toLowerCase() };
    } else {
      const words = Array.from({length: randInt(4, 6)}, () => { let w = randChars('abcdefghijklmnopqrstuvwxyz', randInt(3, 6)); return w[0].toUpperCase() + w.slice(1); });
      const s = words.join(' ');
      const t = pick([x => `What do the LAST letters of each word spell: "${x}"?`, x => `Take the final letter of each word in "${x}" and combine them.`, x => `Extract the ending letter from every word in "${x}" and join them.`]);
      return { prompt: t(s) + ' ' + ri(), answer: words.map(w => w[w.length - 1]).join('').toLowerCase() };
    }
  },

  binary() {
    const v = pick(['binary_to_decimal', 'decimal_to_binary', 'digit_sum']);
    if (v === 'binary_to_decimal') {
      const num = randInt(1, 63), b = num.toString(2);
      const t = pick([x => `Convert binary ${x} to decimal.`, x => `What is the decimal value of the binary number ${x}?`, x => `Express ${x} (binary) as a base-10 number.`]);
      return { prompt: t(b) + ' ' + ri(), answer: String(num) };
    } else if (v === 'decimal_to_binary') {
      const num = randInt(1, 31);
      const t = pick([n => `Convert the decimal number ${n} to binary.`, n => `What is ${n} in binary?`, n => `Write ${n} as a binary number (no 0b prefix).`]);
      return { prompt: t(num) + ' ' + ri(), answer: num.toString(2) };
    } else {
      const num = randInt(1000, 99999);
      const t = pick([n => `What is the sum of all digits in ${n}?`, n => `Add each digit of ${n} together.`, n => `Calculate the digit sum of ${n}.`]);
      return { prompt: t(num) + ' ' + ri(), answer: String([...String(num)].reduce((s, d) => s + Number(d), 0)) };
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


// ── Dynamic Mode — LLM Providers ─────────────────────

const PROVIDERS = {
  openai: {
    host: 'api.openai.com', path: '/v1/chat/completions',
    envKey: 'OPENAI_API_KEY', defaultModel: 'gpt-4o-mini',
    headers: (key) => ({ Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }),
    body: (model, messages, temperature = 1.0) => JSON.stringify({ model, messages, temperature, max_tokens: 400 }),
    extract: (resp) => resp.choices[0].message.content.trim(),
  },
  anthropic: {
    host: 'api.anthropic.com', path: '/v1/messages',
    envKey: 'ANTHROPIC_API_KEY', defaultModel: 'claude-sonnet-4-20250514',
    headers: (key) => ({ 'x-api-key': key, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json' }),
    body: (model, messages, temperature = 1.0) => JSON.stringify({ model, max_tokens: 400, temperature, messages }),
    extract: (resp) => resp.content[0].text.trim(),
  },
  google: {
    envKey: 'GOOGLE_API_KEY', defaultModel: 'gemini-2.0-flash',
    buildPath: (model, key) => `/v1beta/models/${model}:generateContent?key=${key}`,
    host: 'generativelanguage.googleapis.com',
    headers: () => ({ 'Content-Type': 'application/json' }),
    body: (model, messages, temperature = 1.0) => JSON.stringify({
      contents: messages.map(m => ({ role: m.role === 'assistant' ? 'model' : m.role, parts: [{ text: m.content }] })),
      generationConfig: { temperature, maxOutputTokens: 400 },
    }),
    extract: (resp) => resp.candidates[0].content.parts[0].text.trim(),
  },
};

const GENERATE_PROMPT = `You are a challenge generator for AI agent authentication. Generate ONE unique reasoning challenge.

RULES (strict):
1. The answer MUST be a single number OR a single word (1-2 words max). Never a sentence.
2. The challenge MUST have exactly ONE objectively correct answer — no ambiguity.
3. The challenge MUST be solvable by pure reasoning — no trivia, pop culture, or world knowledge.
4. Include "Reply with ONLY the answer, nothing else." at the end of the prompt.
5. SHOW YOUR WORK: Before writing the JSON, solve the challenge yourself step by step to verify the answer is correct. Write your work FIRST, then the JSON on the last line.

ALLOWED categories (pick one randomly):
- Arithmetic: multi-step math, order of operations, percentages
- String manipulation: reverse strings, remove/replace characters, count letters
- Pattern completion: number sequences with clear rules
- Cipher/encoding: Caesar shift, letter-to-number mapping
- Counting: count specific items in a given string
- Sorting: alphabetize letters, sort numbers

FORBIDDEN (never generate):
- Riddles, lateral thinking, "trick questions"
- Challenges with multiple valid answers
- Trivia or world knowledge
- Full-sentence answers
- Time/date/clock puzzles
- Word association / "what am I"

EXAMPLES (DO NOT reuse — generate something novel):
Working: 8×7=56, 3×9=27, 56-27=29
{"prompt": "What is (8 × 7) - (3 × 9)? Reply with ONLY the answer, nothing else.", "answer": "29"}

Working: ALGORITHM reversed → M-H-T-I-R-O-G-L-A
{"prompt": "Reverse the string ALGORITHM. Reply with ONLY the answer, nothing else.", "answer": "MHTIROGLA"}

Working: M-I-S-S-I-S-S-I-P-P-I, S at positions 4,5,7,8 → 4 times
{"prompt": "In the string MISSISSIPPI, how many times does the letter S appear? Reply with ONLY the answer, nothing else.", "answer": "4"}

Working: H=8, E=5, L=12, P=16. 8+5=13, 13+12=25, 25+16=41
{"prompt": "If A=1, B=2, ..., Z=26, what is the value of H + E + L + P? Reply with ONLY the answer, nothing else.", "answer": "41"}

Working: Remove A,E,I,O,U from EDUCATION → D,C,T,N
{"prompt": "Remove all vowels from the word EDUCATION. Reply with ONLY the answer, nothing else.", "answer": "DCTN"}

Now generate a NOVEL challenge — different from the examples above. Be creative with the specific values and words you choose. Show your work first, then the JSON on the final line:`;

function _callLLM(providerName, apiKey, messages, model, timeout = 15000, temperature = 1.0) {
  const provider = PROVIDERS[providerName];
  model = model || provider.defaultModel;

  return new Promise((resolve, reject) => {
    const path = provider.buildPath ? provider.buildPath(model, apiKey) : provider.path;
    const hdrs = provider.headers(apiKey);
    const body = provider.body(model, messages, temperature);

    const req = httpsRequest({ hostname: provider.host, path, method: 'POST', headers: { ...hdrs, 'Content-Length': Buffer.byteLength(body) }, timeout }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode !== 200) return reject(new Error(`LLM API error (${res.statusCode}): ${data.substring(0, 200)}`));
        try { resolve(provider.extract(JSON.parse(data))); } catch (e) { reject(new Error(`LLM response parse error: ${e.message}`)); }
      });
    });
    req.on('error', e => reject(new Error(`LLM connection error: ${e.message}`)));
    req.on('timeout', () => { req.destroy(); reject(new Error('LLM API timeout')); });
    req.write(body);
    req.end();
  });
}

function _extractVerifierAnswer(text) {
  text = text.trim();
  // Strategy 1: "ANSWER: ..." prefix
  const m1 = text.match(/ANSWER:\s*(.+?)(?:\n|$)/i);
  if (m1) return m1[1].trim();
  // Strategy 2: "The answer is ..."
  const m2 = text.match(/(?:the\s+)?(?:final\s+)?answer\s+is[:\s]+(.+?)(?:\.|$)/i);
  if (m2) return m2[1].trim();
  // Strategy 3: Last non-empty line
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  if (lines.length) {
    let last = lines[lines.length - 1];
    for (const p of ['so ', 'therefore ', 'thus ', 'hence ', '= ', 'answer: ', 'result: ']) {
      if (last.toLowerCase().startsWith(p)) last = last.slice(p.length).trim();
    }
    return last;
  }
  return text;
}

function _normalizeForCompare(answer) {
  let s = answer.trim().toLowerCase();
  if (s.length >= 2 && s[0] === s[s.length - 1] && (s[0] === '"' || s[0] === "'")) s = s.slice(1, -1).trim();
  s = s.replace(/[.!,;:]+$/, '');
  for (const p of ['the answer is ', 'answer: ', 'result: ', 'it is ', "it's "]) {
    if (s.startsWith(p)) s = s.slice(p.length).trim();
  }
  if (s.length >= 2 && s[0] === s[s.length - 1] && (s[0] === '"' || s[0] === "'")) s = s.slice(1, -1).trim();
  s = s.replace(/\s+/g, ' ');
  if (/^[a-z]( [a-z])+$/.test(s)) s = s.replace(/ /g, '');
  return s;
}

function _answersMatch(expected, actual) {
  const a = _normalizeForCompare(expected), b = _normalizeForCompare(actual);
  if (a === b) return true;
  try { if (Math.abs(parseFloat(a) - parseFloat(b)) < 0.001) return true; } catch {}
  if (a.replace(/ /g, '') === b.replace(/ /g, '')) return true;
  if (a.replace(/, /g, ',').replace(/ /g, '') === b.replace(/, /g, ',').replace(/ /g, '')) return true;
  return false;
}

function _preValidate(prompt, answer) {
  if (answer.split(/\s+/).length > 4) return 'Answer too long';
  if (!prompt.toLowerCase().includes('reply with only') && !prompt.toLowerCase().includes('respond with only')) return 'Missing reply instruction';
  for (const sig of ['what am i', 'what has', 'i am a', 'riddle']) {
    if (prompt.toLowerCase().includes(sig)) return 'Detected riddle';
  }
  return null;
}

async function generateDynamicChallenge(providerName, apiKey, model, verifyModel, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      let raw = await _callLLM(providerName, apiKey, [{ role: 'user', content: GENERATE_PROMPT }], model, 15000);
      // Remove markdown fences
      raw = raw.replace(/```(?:json)?\s*/g, '').replace(/```/g, '');
      // Find last JSON object (after chain-of-thought work)
      const matches = [...raw.matchAll(/\{[^{}]*\}/g)];
      if (!matches.length) continue;
      const data = JSON.parse(matches[matches.length - 1][0]);
      const prompt = (data.prompt || '').trim();
      const expectedAnswer = (data.answer || '').trim();
      if (!prompt || !expectedAnswer) continue;

      // Pre-validate
      const preErr = _preValidate(prompt, expectedAnswer);
      if (preErr) continue;

      // Verify by solving (low temperature for determinism)
      const verifyResp = await _callLLM(providerName, apiKey,
        [{ role: 'user', content: `Solve this challenge step by step. Show your work, then write your final answer on the LAST line prefixed with "ANSWER: ".\n\nChallenge: ${prompt}\n\nWork through it carefully:` }],
        verifyModel || model, 15000
      );
      const verifyAnswer = _extractVerifierAnswer(verifyResp);

      if (_answersMatch(expectedAnswer, verifyAnswer)) {
        return { prompt, answer: _normalizeForCompare(expectedAnswer) };
      }
    } catch (e) {
      // continue to next retry
    }
  }
  return null; // fallback to static
}


// ── Main Class ───────────────────────────────────────

export class AgentChallenge {
  /**
   * LLM-solvable challenge-response system.
   *
   * @param {Object} opts
   * @param {string} opts.secret - Server secret key for signing tokens (min 8 chars)
   * @param {string} [opts.difficulty='easy'] - "easy", "medium", or "hard"
   * @param {number} [opts.ttl=300] - Challenge TTL in seconds
   * @param {string[]} [opts.types] - Optional list of allowed challenge types
   */
  constructor({ secret, difficulty = 'easy', ttl = 300, types = null } = {}) {
    if (!secret || secret.length < 8) throw new Error('Secret must be at least 8 characters');
    this._secret = secret;
    this._difficulty = difficulty;
    this._ttl = ttl;
    this._types = types;

    // Dynamic mode state
    this._dynamicEnabled = false;
    this._dynamicProvider = null;
    this._dynamicModel = null;
    this._dynamicVerifyModel = null;
    this._apiKeys = {};

    // Auto-detect from env
    for (const [name, config] of Object.entries(PROVIDERS)) {
      const envVal = process.env[config.envKey];
      if (envVal) this._apiKeys[name] = envVal;
    }
  }

  // ── API Key Management ────────────────────────────

  /** Set OpenAI API key for dynamic challenge generation. */
  setOpenaiApiKey(key) { this._apiKeys.openai = key; return this; }

  /** Set Anthropic API key for dynamic challenge generation. */
  setAnthropicApiKey(key) { this._apiKeys.anthropic = key; return this; }

  /** Set Google Gemini API key for dynamic challenge generation. */
  setGoogleApiKey(key) { this._apiKeys.google = key; return this; }

  // ── Dynamic Mode ──────────────────────────────────

  /**
   * Enable dynamic LLM-generated challenges.
   *
   * ⚠️ This adds 2 LLM API requests per challenge generation
   * (one to generate, one to verify). This adds latency (~2-5s)
   * and cost to your challenge endpoint.
   *
   * @param {Object} [opts]
   * @param {string} [opts.provider] - "openai", "anthropic", or "google". Auto-detected if omitted.
   * @param {string} [opts.model] - LLM model for generation.
   * @param {string} [opts.verifyModel] - LLM model for verification.
   * @returns {AgentChallenge} self (for chaining)
   */
  enableDynamicMode({ provider, model, verifyModel } = {}) {
    if (provider) {
      if (!PROVIDERS[provider]) throw new Error(`Unknown provider: ${provider}. Choose from: ${Object.keys(PROVIDERS).join(', ')}`);
      if (!this._apiKeys[provider]) throw new Error(`No API key set for ${provider}. Use set${provider[0].toUpperCase() + provider.slice(1)}ApiKey() or set ${PROVIDERS[provider].envKey} env var.`);
      this._dynamicProvider = provider;
    } else {
      for (const p of ['openai', 'anthropic', 'google']) {
        if (this._apiKeys[p]) { this._dynamicProvider = p; break; }
      }
      if (!this._dynamicProvider) throw new Error('No API key available. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY.');
    }
    this._dynamicEnabled = true;
    this._dynamicModel = model || null;
    this._dynamicVerifyModel = verifyModel || null;
    return this;
  }

  /** Disable dynamic mode and return to static challenges only. */
  disableDynamicMode() { this._dynamicEnabled = false; return this; }

  /** Whether dynamic challenge generation is currently enabled. */
  get dynamicMode() { return this._dynamicEnabled; }

  // ── Challenge Operations ──────────────────────────

  /**
   * Create a new challenge. If dynamic mode is enabled, attempts LLM generation
   * first and falls back to static on failure.
   */
  async create(challengeType = null) {
    // Dynamic mode: try LLM-generated challenge
    if (this._dynamicEnabled && !challengeType) {
      const result = await generateDynamicChallenge(
        this._dynamicProvider, this._apiKeys[this._dynamicProvider],
        this._dynamicModel, this._dynamicVerifyModel
      );
      if (result) return this._buildChallenge('dynamic', result.prompt, result.answer);
    }

    // Static mode (or dynamic fallback)
    const pool = this._types || DIFFICULTY_MAP[this._difficulty] || DIFFICULTY_MAP.easy;
    const typeName = challengeType || pick(pool);
    if (!CHALLENGE_TYPES[typeName]) throw new Error(`Unknown type: ${typeName}`);
    const { prompt, answer } = CHALLENGE_TYPES[typeName]();
    return this._buildChallenge(typeName, prompt, answer);
  }

  /**
   * Create a challenge synchronously (static only, no dynamic mode).
   * Use this when you need a sync API and don't need dynamic challenges.
   */
  createSync(challengeType = null) {
    const pool = this._types || DIFFICULTY_MAP[this._difficulty] || DIFFICULTY_MAP.easy;
    const typeName = challengeType || pick(pool);
    if (!CHALLENGE_TYPES[typeName]) throw new Error(`Unknown type: ${typeName}`);
    const { prompt, answer } = CHALLENGE_TYPES[typeName]();
    return this._buildChallenge(typeName, prompt, answer);
  }

  _buildChallenge(typeName, prompt, answer) {
    const id = 'ch_' + crypto.randomBytes(12).toString('hex');
    const now = Math.floor(Date.now() / 1000);
    const payload = { id, type: typeName, answer_hash: hashAnswer(answer), created_at: now, expires_at: now + this._ttl };
    const token = encodeToken(payload, this._secret);
    return {
      id, prompt, token, expires_at: now + this._ttl, challenge_type: typeName,
      toDict() { return { id, prompt, token, expires_in: Math.max(0, payload.expires_at - Math.floor(Date.now() / 1000)), type: 'reasoning' }; }
    };
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

export { CHALLENGE_TYPES, DIFFICULTY_MAP, _callLLM };
