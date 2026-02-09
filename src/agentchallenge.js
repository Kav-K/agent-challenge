/**
 * agent-challenge (JavaScript/Node.js port)
 *
 * LLM-solvable challenge-response authentication for AI agent APIs.
 * Challenges are puzzles any LLM can solve through reasoning alone —
 * no scripts, no computational power, no external tools needed.
 *
 * Usage:
 *   import { AgentChallenge } from './agentchallenge.js';
 *   const ac = new AgentChallenge({ secret: 'your-server-secret' });
 *   const challenge = ac.create();
 *   // Send challenge.prompt + challenge.token to agent
 *   const result = ac.verify(challenge.token, agentAnswer);
 */

import crypto from 'crypto';

// ── Challenge Types ──────────────────────────────────

const WORDS = [
  'PYTHON', 'SECURITY', 'NETWORK', 'FIREWALL', 'TERMINAL',
  'CHALLENGE', 'KEYBOARD', 'MONITOR', 'GATEWAY', 'PROTOCOL',
  'DATABASE', 'ENCRYPT', 'BROWSER', 'DIGITAL', 'CAPTURE',
  'RUNTIME', 'STORAGE', 'MACHINE', 'COMPILE', 'PACKAGE',
  'SCANNER', 'HACKER', 'SERVER', 'CLIENT', 'ROUTER',
  'SYSTEM', 'ACCESS', 'DEFEND', 'ATTACK', 'SHIELD',
  'BINARY', 'KERNEL', 'DOCKER', 'STREAM', 'BRIDGE',
  'SOCKET', 'BUFFER', 'CIPHER', 'DEPLOY', 'TOGGLE',
  'ANCHOR', 'BEACON', 'MATRIX', 'PORTAL', 'VECTOR',
];

const SHORT_WORDS = [
  'CAT', 'DOG', 'SUN', 'KEY', 'BOX', 'HAT', 'PEN', 'CUP',
  'BAG', 'MAP', 'JAM', 'NET', 'OWL', 'FOX', 'HUB', 'BIT',
  'LOG', 'PIN', 'TAG', 'ZIP', 'ACE', 'AXE', 'BUG', 'COG',
];

const HIDDEN_WORDS = [
  'HELLO', 'WORLD', 'AGENT', 'CLOUD', 'TOKEN',
  'SMART', 'BRAIN', 'POWER', 'GUARD', 'PIXEL',
  'FLAME', 'STONE', 'RIVER', 'EAGLE', 'MAGIC',
];

const ROT13_WORDS = [
  'HELLO', 'WORLD', 'AGENT', 'ROBOT', 'CLOUD', 'SMART',
  'BRAIN', 'LOGIC', 'CYBER', 'PIXEL', 'TOKEN', 'BLOCK',
  'MAGIC', 'POWER', 'SPEED', 'LIGHT', 'GUARD', 'MOUNT',
];

const NUM_WORDS = {
  0:'zero',1:'one',2:'two',3:'three',4:'four',5:'five',
  6:'six',7:'seven',8:'eight',9:'nine',10:'ten',
  11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',
  15:'fifteen',16:'sixteen',17:'seventeen',18:'eighteen',
  19:'nineteen',20:'twenty'
};

const FILLER = 'BCDFGHJKLMNPQRSTVWXYZ';

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

function rot13(text) {
  return text.replace(/[A-Za-z]/g, c => {
    const base = c <= 'Z' ? 65 : 97;
    return String.fromCharCode(((c.charCodeAt(0) - base + 13) % 26) + base);
  });
}

const CHALLENGE_TYPES = {
  reverse_string() {
    const word = pick(WORDS);
    return {
      prompt: `Reverse the following string (reply with ONLY the reversed text, nothing else): ${word}`,
      answer: word.split('').reverse().join('').toLowerCase(),
    };
  },

  simple_math() {
    const op = pick(['+', '+', '+', '-']);
    let a, b, answer;
    if (op === '+') {
      a = randInt(10, 500); b = randInt(10, 500); answer = a + b;
    } else {
      a = randInt(100, 999); b = randInt(10, a - 1); answer = a - b;
    }
    return {
      prompt: `What is ${a} ${op} ${b}? Reply with ONLY the number, nothing else.`,
      answer: String(answer),
    };
  },

  letter_position() {
    const word = pick(SHORT_WORDS);
    const total = [...word].reduce((s, c) => s + (c.charCodeAt(0) - 64), 0);
    return {
      prompt: `If A=1, B=2, C=3, ... Z=26, what is the sum of the letter values in the word "${word}"? Reply with ONLY the number, nothing else.`,
      answer: String(total),
    };
  },

  rot13() {
    const word = pick(ROT13_WORDS);
    const encoded = rot13(word);
    return {
      prompt: `Decode this ROT13-encoded string (each letter shifts 13 places back in the alphabet): ${encoded}\nReply with ONLY the decoded word, nothing else.`,
      answer: word.toLowerCase(),
    };
  },

  pattern() {
    const ptype = pick(['add', 'multiply', 'add_growing']);
    let display, answer;

    if (ptype === 'add') {
      const start = randInt(1, 20), step = randInt(2, 10);
      display = Array.from({length: 5}, (_, i) => start + step * i);
      answer = display[4] + step;
    } else if (ptype === 'multiply') {
      const base = pick([2, 3]);
      display = Array.from({length: 5}, (_, i) => base ** (i + 1));
      answer = base ** 6;
    } else {
      display = [randInt(1, 5)];
      for (let i = 1; i < 5; i++) display.push(display[i-1] + i);
      answer = display[4] + 5;
    }

    return {
      prompt: `What comes next in this sequence: ${display.join(', ')}, ? Reply with ONLY the number, nothing else.`,
      answer: String(answer),
    };
  },

  extract_letters() {
    const word = pick(HIDDEN_WORDS);
    const n = pick([2, 3]);
    let mixed = '';
    for (let i = 0; i < word.length; i++) {
      mixed += word[i];
      if (i < word.length - 1) {
        for (let j = 0; j < n - 1; j++) mixed += FILLER[randInt(0, FILLER.length - 1)];
      }
    }
    const ordinal = n === 2 ? '2nd' : '3rd';
    return {
      prompt: `Extract every ${ordinal} letter from this string, starting from the 1st character: ${mixed}\nReply with ONLY the extracted letters as one word, nothing else.`,
      answer: word.toLowerCase(),
    };
  },

  word_math() {
    const variant = pick(['digit_to_word', 'word_count', 'char_count']);

    if (variant === 'digit_to_word') {
      const a = randInt(1, 10), b = randInt(1, 10);
      return {
        prompt: `What is ${a} + ${b}? Write the answer as a word (e.g., "twelve"), not a number. Reply with ONLY the word, nothing else.`,
        answer: NUM_WORDS[a + b],
      };
    } else if (variant === 'word_count') {
      const sentences = [
        ['The quick brown fox jumps', 5], ['A robot walked into a bar', 6],
        ['She sells sea shells by the shore', 7], ['I think therefore I am', 5],
        ['To be or not to be', 6], ['All that glitters is not gold', 6],
        ['The cat sat on the mat', 6], ['One small step for a man', 6],
        ['Every cloud has a silver lining', 6], ['Time flies like an arrow', 5],
      ];
      const [sentence, count] = pick(sentences);
      return {
        prompt: `How many words are in this sentence: "${sentence}"? Reply with ONLY the number, nothing else.`,
        answer: String(count),
      };
    } else {
      const words = ['PYTHON', 'CYBER', 'ROBOT', 'AGENT', 'CLOUD', 'MAGIC', 'POWER', 'LIGHT', 'OCEAN', 'GUARD'];
      const word = pick(words);
      return {
        prompt: `How many letters are in the word "${word}"? Reply with ONLY the number, nothing else.`,
        answer: String(word.length),
      };
    }
  },
};

const DIFFICULTY_MAP = {
  easy: ['reverse_string', 'simple_math', 'pattern'],
  medium: ['reverse_string', 'simple_math', 'rot13', 'letter_position', 'extract_letters', 'pattern'],
  hard: Object.keys(CHALLENGE_TYPES),
};


// ── Token Helpers ────────────────────────────────────

function hmacSign(data, secret) {
  return crypto.createHmac('sha256', secret).update(data).digest('hex');
}

function encodeToken(payload, secret) {
  const data = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const sig = hmacSign(data, secret);
  return `${data}.${sig}`;
}

function decodeToken(token, secret) {
  if (!token || !token.includes('.')) throw new Error('Invalid token format');
  const idx = token.lastIndexOf('.');
  const data = token.slice(0, idx);
  const sig = token.slice(idx + 1);

  const expected = hmacSign(data, secret);
  if (!crypto.timingSafeEqual(Buffer.from(sig, 'hex'), Buffer.from(expected, 'hex'))) {
    throw new Error('Invalid token signature');
  }

  return JSON.parse(Buffer.from(data, 'base64url').toString());
}

function hashAnswer(answer) {
  return crypto.createHash('sha256').update(answer, 'utf8').digest('hex');
}

function normalizeAnswer(answer) {
  if (typeof answer !== 'string') return '';
  let s = answer.trim().toLowerCase();
  if (s.length >= 2 && s[0] === s[s.length - 1] && (s[0] === '"' || s[0] === "'")) {
    s = s.slice(1, -1).trim();
  }
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
    // Pick type
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

    const payload = {
      id,
      type: typeName,
      answer_hash: hashAnswer(answer),
      created_at: now,
      expires_at: now + this._ttl,
    };

    const token = encodeToken(payload, this._secret);

    return {
      id,
      prompt,
      token,
      expires_at: now + this._ttl,
      challenge_type: typeName,
      toDict() {
        return {
          id, prompt, token,
          expires_in: Math.max(0, payload.expires_at - Math.floor(Date.now() / 1000)),
          type: 'reasoning',
        };
      },
    };
  }

  verify(token, answer) {
    const start = Date.now();

    let payload;
    try {
      payload = decodeToken(token, this._secret);
    } catch (e) {
      return { valid: false, error: e.message };
    }

    if (Math.floor(Date.now() / 1000) > payload.expires_at) {
      return { valid: false, error: 'Challenge expired' };
    }

    const normalized = normalizeAnswer(answer);
    if (!normalized) return { valid: false, error: 'Empty answer' };

    if (hashAnswer(normalized) === payload.answer_hash) {
      return {
        valid: true,
        challenge_type: payload.type,
        elapsed_ms: Date.now() - start,
      };
    }

    return { valid: false, error: 'Incorrect answer', challenge_type: payload.type };
  }
}

export { CHALLENGE_TYPES, DIFFICULTY_MAP };
