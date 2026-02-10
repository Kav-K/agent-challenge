/**
 * agent-challenge v0.6.0 (JavaScript/Node.js port)
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

function isPrime(n) {
  if (n < 2) return false;
  if (n < 4) return true;
  if (n % 2 === 0 || n % 3 === 0) return false;
  let i = 5;
  while (i * i <= n) {
    if (n % i === 0 || n % (i + 2) === 0) return false;
    i += 6;
  }
  return true;
}

function nextPrime(n) {
  let c = n + 1;
  while (!isPrime(c)) c++;
  return c;
}

const NUM_WORDS = {
  0:'zero',1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',
  11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',16:'sixteen',17:'seventeen',18:'eighteen',
  19:'nineteen',20:'twenty'
};

const SIMPLE_WORDS = [
  'apple','banana','cherry','date','fig','grape','kiwi','lemon',
  'mango','orange','peach','plum','quince','rose','sage','thyme',
  'basil','cedar','daisy','elm','fern','holly','iris','jade',
  'lake','moon','nest','oak','pine','rain','snow','tide',
  'wave','zinc','arch','bell','cave','dusk','echo','fork',
];

function sampleN(arr, n) {
  const copy = [...arr];
  const result = [];
  for (let i = 0; i < n && copy.length > 0; i++) {
    const idx = randInt(0, copy.length - 1);
    result.push(copy.splice(idx, 1)[0]);
  }
  return result;
}

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
      w => `Reverse this text exactly as written: ${w}.`,
      w => `Give ${w} backwards, character by character.`,
      w => `Write ${w} in reverse (last character first).`,
      w => `Reverse the order of characters in the string ${w}.`,
      w => `Mirror ${w} so the first character becomes the last.`,
      w => `Rewrite the string ${w} from the end to the beginning.`,
      w => `What does ${w} look like when you read it in reverse?`,
      w => `Flip ${w} around — last letter first, first letter last.`,
    ];
    return { prompt: pick(templates)(word) + ' ' + ri(), answer: word.split('').reverse().join('').toLowerCase() };
  },

  simple_math() {
    const op = pick(['+', '+', '-', '×', '++', '--', 'mixed', 'mod']);
    let prompt, answer;
    if (op === '+') {
      const a = randInt(10, 999), b = randInt(10, 999); answer = a + b;
      prompt = pick([
        `What is ${a} + ${b}?`, `Calculate the sum of ${a} and ${b}.`, `Add ${a} to ${b}. What do you get?`,
        `If you combine ${a} and ${b}, what is the total?`, `Compute ${a} plus ${b}.`,
        `Find the result of adding ${a} and ${b} together.`, `Sum up ${a} and ${b}.`,
        `How much is ${a} added to ${b}?`, `${a} + ${b} = ?`,
        `Tell me what ${a} plus ${b} equals.`, `What do you get if you add ${a} and ${b}?`,
        `Determine the value of ${a} + ${b}.`, `Please compute the sum: ${a} + ${b}.`,
      ]);
    } else if (op === '-') {
      const a = randInt(100, 999), b = randInt(10, a - 1); answer = a - b;
      prompt = pick([
        `What is ${a} - ${b}?`, `Subtract ${b} from ${a}.`, `If you take ${b} away from ${a}, what remains?`,
        `Calculate ${a} minus ${b}.`,
        `Find the difference between ${a} and ${b}.`, `${a} - ${b} = ?`,
        `How much is ${a} minus ${b}?`, `Remove ${b} from ${a}. What is left?`,
        `Compute the result of ${a} minus ${b}.`, `What remains when ${b} is subtracted from ${a}?`,
        `Determine ${a} - ${b}.`, `Take ${b} from ${a} and tell me the result.`,
      ]);
    } else if (op === '×') {
      const a = randInt(2, 30), b = randInt(2, 30); answer = a * b;
      prompt = pick([
        `What is ${a} × ${b}?`, `Multiply ${a} by ${b}.`, `Calculate the product of ${a} and ${b}.`,
        `What do you get when you multiply ${a} times ${b}?`,
        `${a} × ${b} = ?`, `Find the product of ${a} and ${b}.`,
        `How much is ${a} multiplied by ${b}?`, `What is ${a} times ${b}?`,
        `Compute ${a} * ${b}.`, `Tell me what ${a} times ${b} equals.`,
        `If you multiply ${a} and ${b}, what is the result?`, `Determine the value of ${a} × ${b}.`,
      ]);
    } else if (op === '++') {
      const a = randInt(10, 300), b = randInt(10, 300), c = randInt(10, 300); answer = a + b + c;
      prompt = pick([
        `What is ${a} + ${b} + ${c}?`, `Add together ${a}, ${b}, and ${c}.`,
        `Find the sum of these three numbers: ${a}, ${b}, ${c}.`, `Calculate ${a} plus ${b} plus ${c}.`,
        `Sum ${a}, ${b}, and ${c}.`, `${a} + ${b} + ${c} = ?`,
        `What is the total of ${a}, ${b}, and ${c}?`, `Combine ${a}, ${b}, and ${c}. What do you get?`,
        `How much do ${a}, ${b}, and ${c} add up to?`, `Compute the sum of ${a}, ${b}, and ${c}.`,
        `If you add ${a}, ${b}, and ${c}, what is the result?`, `Tell me the sum: ${a} + ${b} + ${c}.`,
      ]);
    } else if (op === '--') {
      const a = randInt(500, 999), b = randInt(10, 200), c = randInt(10, Math.min(200, a - b - 1)); answer = a - b - c;
      prompt = pick([
        `What is ${a} - ${b} - ${c}?`, `Start with ${a}, subtract ${b}, then subtract ${c}.`,
        `Take ${a}, remove ${b}, then remove another ${c}. What's left?`,
        `${a} - ${b} - ${c} = ?`, `Calculate ${a} minus ${b} minus ${c}.`,
        `From ${a}, subtract first ${b} then ${c}.`, `Begin with ${a}. Deduct ${b} and then ${c}. What remains?`,
        `Compute ${a} - ${b} - ${c}.`, `What do you get when you subtract ${b} and ${c} from ${a}?`,
        `Find the result: ${a} minus ${b} minus ${c}.`, `If you take away ${b} and ${c} from ${a}, what's left?`,
      ]);
    } else if (op === 'mixed') {
      const a = randInt(50, 500), b = randInt(10, 300), c = randInt(10, Math.min(a + b - 1, 300)); answer = a + b - c;
      prompt = pick([
        `What is ${a} + ${b} - ${c}?`, `Calculate ${a} plus ${b} minus ${c}.`,
        `Add ${a} and ${b}, then subtract ${c}. What do you get?`, `Compute the result of ${a} + ${b} - ${c}.`,
        `${a} + ${b} - ${c} = ?`, `Start with ${a}, add ${b}, and subtract ${c}.`,
        `Find the value of ${a} plus ${b} minus ${c}.`, `What remains if you combine ${a} and ${b}, then take away ${c}?`,
      ]);
    } else { // mod
      const b = randInt(3, 20), a = randInt(b + 1, 200); answer = a % b;
      prompt = pick([
        `What is ${a} mod ${b}? (the remainder when ${a} is divided by ${b})`,
        `Calculate the remainder of ${a} divided by ${b}.`,
        `What is the remainder when ${a} is divided by ${b}?`,
        `Compute ${a} % ${b} (modulo operation).`,
        `Find the remainder: ${a} ÷ ${b}.`,
        `If you divide ${a} by ${b}, what is the remainder?`,
        `Determine ${a} modulo ${b}.`,
        `${a} mod ${b} = ?`,
      ]);
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
      w => `Given A=1, B=2, ..., Z=26, compute the sum of all letter values in "${w}".`,
      w => `Map each letter to its alphabet position (A=1 through Z=26) and find the total for "${w}".`,
      w => `What is the alphabet position sum for the letters in "${w}"? (A=1, B=2, ..., Z=26)`,
      w => `For the string "${w}", convert each letter to its position number (A=1, B=2, ...) and add them all up.`,
      w => `Calculate the total alphabetical value of "${w}" where A=1, B=2, C=3, and so on.`,
      w => `Sum the positions of all letters in "${w}" using the scheme A=1, B=2, ..., Z=26.`,
      w => `In "${w}", each letter has a value equal to its position in the alphabet. What is the total?`,
      w => `Add together the alphabetic positions of every letter in "${w}" (A=1, Z=26).`,
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
      e => `This string has been ROT13-encoded: ${e}. What is the decoded version?`,
      e => `Reverse the ROT13 encoding of: ${e}`,
      e => `Decode ${e} using the ROT13 cipher (rotate each letter by 13).`,
      e => `The text ${e} was scrambled with ROT13. Unscramble it.`,
      e => `Apply the ROT13 algorithm to decipher this: ${e}`,
      e => `What does ${e} say when you undo the ROT13 encoding?`,
      e => `Each letter in ${e} was shifted 13 places forward. Shift them back to decode.`,
      e => `ROT13 decrypt this string: ${e}`,
    ];
    return { prompt: pick(templates)(encoded) + ' ' + ri(), answer: word.toLowerCase() };
  },

  pattern() {
    const ptype = pick(['add', 'multiply', 'add_growing', 'squares', 'triangular', 'fibonacci_like', 'triangular_numbers', 'primes', 'decreasing']);
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
    } else if (ptype === 'add_growing') {
      const start = randInt(1, 20), is_ = randInt(1, 5);
      display = [start]; for (let i = 0; i < 4; i++) display.push(display[display.length-1] + is_ + i);
      answer = display[4] + is_ + 4;
    } else if (ptype === 'fibonacci_like') {
      const a = randInt(1, 5), b = randInt(1, 5);
      display = [a, b];
      for (let i = 0; i < 3; i++) display.push(display[display.length-1] + display[display.length-2]);
      answer = display[4] + display[3];
    } else if (ptype === 'triangular_numbers') {
      const sn = randInt(1, 4);
      display = Array.from({length: 5}, (_, i) => (sn + i) * (sn + i + 1) / 2);
      answer = (sn + 5) * (sn + 6) / 2;
    } else if (ptype === 'primes') {
      const sp = pick([2, 3, 5, 7, 11, 13]);
      display = [sp];
      for (let i = 0; i < 4; i++) display.push(nextPrime(display[display.length-1]));
      answer = nextPrime(display[4]);
    } else { // decreasing
      const start = randInt(80, 150), step = randInt(3, 12);
      display = Array.from({length: 5}, (_, i) => start - step * i);
      answer = display[4] - step;
    }
    const seq = display.join(', ');
    const templates = [
      s => `What comes next in this sequence: ${s}, ?`,
      s => `Find the next number: ${s}, ?`,
      s => `Continue this pattern: ${s}, ?`,
      s => `What number follows this sequence: ${s}, ?`,
      s => `Identify the next value in the series: ${s}, ?`,
      s => `Determine the next number in the pattern: ${s}, ?`,
      s => `What is the next term in this sequence: ${s}, ?`,
      s => `Extend this series by one: ${s}, ?`,
      s => `The sequence goes: ${s}. What comes next?`,
      s => `Look at this pattern: ${s}. What is the next value?`,
      s => `Given the series ${s}, find the number that follows.`,
      s => `Here is a number sequence: ${s}. What should the next number be?`,
      s => `Predict the next element: ${s}, ?`,
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
      m => `Read only the odd-positioned characters in ${m} (1st, 3rd, 5th...).`,
      m => `From ${m}, extract characters at positions 1, 3, 5, 7, and so on.`,
      m => `Skip every other letter in ${m}, starting by keeping the first character.`,
      m => `Take the 1st, 3rd, 5th, 7th... characters from ${m}.`,
      m => `What do you get when you select every second character from ${m}, starting with the first?`,
      m => `Pick out alternating characters from ${m}, beginning with the first one.`,
      m => `In ${m}, keep only the characters at odd positions (1, 3, 5, ...).`,
      m => `Extract characters at indices 0, 2, 4, 6... from the string ${m}.`,
    ];
    const templates3 = [
      m => `Extract every 3rd letter from this string, starting from the 1st character: ${m}`,
      m => `From ${m}, take the 1st, 4th, 7th, 10th... characters.`,
      m => `Pick every third character from ${m}, starting at position 1.`,
      m => `From the string ${m}, select the character at position 1, then every 3rd character after that.`,
      m => `In ${m}, extract the 1st character, then skip 2 and take the next, repeating this pattern.`,
      m => `Read characters at positions 1, 4, 7, 10... from ${m}.`,
      m => `Take every third letter from ${m}, beginning with the very first one.`,
      m => `What word do you get by selecting the 1st, 4th, 7th, 10th... letters from ${m}?`,
      m => `Skip two characters, keep one — starting from position 1 in ${m}.`,
      m => `From ${m}, pick out characters at indices 0, 3, 6, 9...`,
      m => `Extract every 3rd character from ${m} starting at the beginning.`,
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
        (x,y) => `What is the sum of ${x} and ${y}? Respond using the English word for the number.`,
        (x,y) => `Compute ${x} plus ${y} and express the answer as a word.`,
        (x,y) => `${x} + ${y} = ? Write the answer as a word (like "seven"), not a numeral.`,
        (x,y) => `Add ${x} to ${y}. Give the answer spelled out in English.`,
        (x,y) => `Find ${x} + ${y} and write the result as an English number word.`,
        (x,y) => `What word represents the sum of ${x} and ${y}?`,
        (x,y) => `Sum ${x} and ${y}. Spell the answer as a word instead of a digit.`,
        (x,y) => `Tell me ${x} plus ${y} using the English word for the number.`,
      ]);
      return { prompt: t(a, b) + ' ' + ri(), answer: NUM_WORDS[a + b] };
    } else if (v === 'char_count') {
      const w = randChars(UPPER, randInt(4, 8));
      const t = pick([
        x => `How many characters are in the string "${x}"?`,
        x => `Count the total number of letters in "${x}".`,
        x => `What is the length of the string "${x}"?`,
        x => `How many letters does "${x}" contain?`,
        x => `Determine the character count of "${x}".`,
        x => `What is the total number of characters in "${x}"?`,
        x => `Count all the characters in the string "${x}".`,
        x => `How long is the string "${x}"? Give the number of characters.`,
        x => `Tell me how many letters are in "${x}".`,
        x => `Find the length of "${x}" in characters.`,
        x => `"${x}" — how many characters is that?`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: String(w.length) };
    } else if (v === 'vowel_count') {
      const w = randChars(UPPER, randInt(5, 9));
      const t = pick([
        x => `How many vowels (A, E, I, O, U) are in "${x}"?`,
        x => `Count the vowels in the string "${x}".`,
        x => `In the text "${x}", how many letters are vowels (A, E, I, O, U)?`,
        x => `How many of the letters in "${x}" are vowels?`,
        x => `Find the number of vowels (A, E, I, O, U) in "${x}".`,
        x => `Count how many times A, E, I, O, or U appears in "${x}".`,
        x => `What is the vowel count for the string "${x}"?`,
        x => `In "${x}", tally up all the vowels (A, E, I, O, U).`,
        x => `How many vowel letters does "${x}" contain?`,
        x => `Tell me the number of vowels in "${x}".`,
        x => `Scan "${x}" and count every A, E, I, O, and U.`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: String([...w].filter(c => 'AEIOU'.includes(c)).length) };
    } else {
      const num = randInt(100, 9999);
      const t = pick([
        n => `What is the sum of the digits of ${n}?`,
        n => `Add up each individual digit in the number ${n}.`,
        n => `Take the number ${n} and sum its digits together.`,
        n => `Calculate the digit sum of ${n}.`,
        n => `What do you get when you add all the digits of ${n}?`,
        n => `Sum every digit in the number ${n}.`,
        n => `Find the total when you add each digit of ${n} individually.`,
        n => `Break ${n} into its individual digits and add them up.`,
        n => `What is the result of summing all digits in ${n}?`,
        n => `Compute the digit sum: take ${n} and add up each digit.`,
        n => `For the number ${n}, find the sum of its digits.`,
      ]);
      return { prompt: t(num) + ' ' + ri(), answer: String([...String(num)].reduce((s, d) => s + Number(d), 0)) };
    }
  },

  caesar() {
    const word = pronounceable(randInt(4, 7));
    const shift = randInt(1, 13);
    const encoded = caesarEncode(word, shift);
    const templates = [
      (e,s) => `Decode this Caesar cipher (each letter is shifted ${s} positions forward in the alphabet): ${e}\nShift each letter ${s} positions BACKWARD to decode.`,
      (e,s) => `The text ${e} was encrypted with a Caesar shift of ${s}. Decrypt it by shifting each letter back by ${s}.`,
      (e,s) => `Apply a reverse Caesar shift of ${s} to decode: ${e}`,
      (e,s) => `This message was encoded by shifting each letter forward by ${s} in the alphabet: ${e}. What is the original text?`,
      (e,s) => `Decrypt the Caesar cipher ${e} by shifting each letter ${s} positions backward.`,
      (e,s) => `Each letter in ${e} was shifted forward by ${s}. Reverse the shift to decode.`,
      (e,s) => `The cipher text is ${e}, encoded with a shift of ${s}. What was the original message?`,
      (e,s) => `Undo a Caesar shift of ${s} on this text: ${e}`,
      (e,s) => `Caesar decode ${e} with shift=${s}. Move each letter ${s} places back in the alphabet.`,
      (e,s) => `Given the Caesar-encrypted text ${e} (shift ${s}), determine the plaintext.`,
      (e,s) => `Decipher this by reversing a ${s}-position Caesar shift: ${e}`,
      (e,s) => `Shift every letter in ${e} backward by ${s} positions to reveal the original word.`,
    ];
    return { prompt: pick(templates)(encoded, shift) + ' ' + ri(), answer: word.toLowerCase() };
  },

  sorting() {
    const v = pick(['sort_letters', 'sort_numbers', 'sort_reverse', 'sort_words', 'sort_numbers_reverse']);
    if (v === 'sort_letters') {
      const w = randChars(UPPER, randInt(5, 8));
      const t = pick([
        x => `Sort these letters in alphabetical order: ${x}`,
        x => `Arrange the letters ${x} from A to Z.`,
        x => `Put these letters in alphabetical sequence: ${x}`,
        x => `Alphabetize the letters: ${x}`,
        x => `Reorder ${x} so the letters go from A to Z.`,
        x => `What does ${x} look like when the letters are sorted alphabetically?`,
        x => `Arrange the characters ${x} in alphabetical order.`,
        x => `Sort ${x} from first to last in the alphabet.`,
        x => `Order these letters alphabetically: ${x}`,
        x => `Take the letters ${x} and sort them A→Z.`,
        x => `Rearrange ${x} into alphabetical order.`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: [...w].sort().join('').toLowerCase() };
    } else if (v === 'sort_numbers') {
      const nums = []; const seen = new Set();
      const count = randInt(5, 7);
      while (nums.length < count) { const n = randInt(1, 99); if (!seen.has(n)) { nums.push(n); seen.add(n); } }
      const t = pick([
        x => `Sort these numbers from smallest to largest: ${x}`,
        x => `Arrange in ascending order: ${x}`,
        x => `Put these numbers in order from lowest to highest: ${x}`,
        x => `Order these numbers from least to greatest: ${x}`,
        x => `Sort in ascending order: ${x}`,
        x => `Rearrange these numbers from smallest to biggest: ${x}`,
        x => `What is the ascending order of: ${x}?`,
        x => `List these numbers sorted from low to high: ${x}`,
        x => `Arrange ${x} in increasing order.`,
        x => `Put ${x} in numerical order (smallest first).`,
        x => `Sort from minimum to maximum: ${x}`,
      ]);
      return { prompt: t(nums.join(', ')) + ' ' + ri(), answer: [...nums].sort((a, b) => a - b).join(', ') };
    } else if (v === 'sort_reverse') {
      const w = randChars(UPPER, randInt(5, 7));
      const t = pick([
        x => `Sort these letters in REVERSE alphabetical order (Z first, A last): ${x}`,
        x => `Arrange the letters ${x} from Z to A.`,
        x => `Put these letters in reverse alphabetical order: ${x}`,
        x => `Sort ${x} in descending alphabetical order.`,
        x => `Order the letters ${x} from Z to A.`,
        x => `Rearrange ${x} in reverse alphabetical order (Z first).`,
        x => `What does ${x} look like sorted from Z to A?`,
        x => `Take the letters ${x} and sort them Z→A.`,
        x => `Arrange ${x} in reverse (Z before A).`,
        x => `Sort these letters backwards through the alphabet: ${x}`,
        x => `Put ${x} in descending alphabetical order.`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: [...w].sort().reverse().join('').toLowerCase() };
    } else if (v === 'sort_words') {
      const count = randInt(4, 6);
      const words = sampleN(SIMPLE_WORDS, count);
      const sorted = [...words].sort();
      const t = pick([
        x => `Sort these words alphabetically: ${x}`,
        x => `Arrange these words in alphabetical order: ${x}`,
        x => `Put these words in order from A to Z: ${x}`,
        x => `Alphabetize the following words: ${x}`,
        x => `What is the alphabetical order of: ${x}?`,
        x => `Reorder these words alphabetically: ${x}`,
        x => `List these words sorted A→Z: ${x}`,
        x => `Sort from first to last alphabetically: ${x}`,
      ]);
      return { prompt: t(words.join(', ')) + ' ' + ri(), answer: sorted.join(', ') };
    } else { // sort_numbers_reverse
      const nums = []; const seen = new Set();
      const count = randInt(5, 7);
      while (nums.length < count) { const n = randInt(1, 99); if (!seen.has(n)) { nums.push(n); seen.add(n); } }
      const t = pick([
        x => `Sort these numbers from largest to smallest: ${x}`,
        x => `Arrange in descending order: ${x}`,
        x => `Put these numbers in order from highest to lowest: ${x}`,
        x => `Order these numbers from greatest to least: ${x}`,
        x => `Sort in descending order: ${x}`,
        x => `Rearrange these numbers from biggest to smallest: ${x}`,
        x => `List these numbers from high to low: ${x}`,
        x => `Sort from maximum to minimum: ${x}`,
      ]);
      return { prompt: t(nums.join(', ')) + ' ' + ri(), answer: [...nums].sort((a, b) => b - a).join(', ') };
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
        (tg,tx) => `How often does "${tg}" show up in "${tx}"?`,
        (tg,tx) => `Find the number of times "${tg}" appears in "${tx}".`,
        (tg,tx) => `Scan the string "${tx}" and count every "${tg}".`,
        (tg,tx) => `What is the frequency of the letter "${tg}" in "${tx}"?`,
        (tg,tx) => `Count all instances of "${tg}" within "${tx}".`,
        (tg,tx) => `How many "${tg}" letters can you find in "${tx}"?`,
        (tg,tx) => `Tell me the count of "${tg}" in the string "${tx}".`,
        (tg,tx) => `In the string "${tx}", tally up every occurrence of "${tg}".`,
      ]);
      return { prompt: t(target, text) + ' ' + ri(), answer: String(text.split(target).length - 1) };
    } else if (v === 'count_consonants') {
      const w = randChars(UPPER, randInt(6, 10));
      const t = pick([
        x => `How many consonants (non-vowel letters) are in "${x}"?`,
        x => `Count all consonants in the string "${x}".`,
        x => `In "${x}", how many letters are NOT vowels?`,
        x => `What is the consonant count for "${x}"?`,
        x => `How many non-vowel letters does "${x}" contain?`,
        x => `Find the number of consonants in "${x}".`,
        x => `Tally the consonants in the string "${x}".`,
        x => `Count the letters in "${x}" that are not A, E, I, O, or U.`,
        x => `In "${x}", how many consonant characters are there?`,
        x => `Determine the number of consonants in "${x}".`,
        x => `How many letters in "${x}" are consonants (not vowels)?`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: String([...w].filter(c => !'AEIOU'.includes(c)).length) };
    } else if (v === 'count_digits') {
      const d = randChars(DIGITS, randInt(8, 14)), target = d[randInt(0, d.length - 1)];
      const t = pick([
        (tg,dd) => `How many times does the digit "${tg}" appear in "${dd}"?`,
        (tg,dd) => `Count how often "${tg}" occurs in the number string "${dd}".`,
        (tg,dd) => `In the string "${dd}", how many "${tg}" digits are there?`,
        (tg,dd) => `Find the count of digit "${tg}" in "${dd}".`,
        (tg,dd) => `Scan "${dd}" and tell me how many times "${tg}" appears.`,
        (tg,dd) => `What is the frequency of "${tg}" in the number string "${dd}"?`,
        (tg,dd) => `Count all occurrences of the digit "${tg}" in "${dd}".`,
        (tg,dd) => `How often does the digit "${tg}" show up in "${dd}"?`,
        (tg,dd) => `In "${dd}", tally every "${tg}".`,
        (tg,dd) => `Determine how many "${tg}" digits are in "${dd}".`,
      ]);
      return { prompt: t(target, d) + ' ' + ri(), answer: String(d.split(target).length - 1) };
    } else {
      const text = randChars(LETTERS_ALL, randInt(10, 16));
      const t = pick([
        x => `How many UPPERCASE letters are in "${x}"?`,
        x => `Count the capital letters in "${x}".`,
        x => `In the mixed-case string "${x}", how many characters are uppercase?`,
        x => `Find the number of uppercase characters in "${x}".`,
        x => `How many capital letters does "${x}" contain?`,
        x => `Tally all the uppercase letters in "${x}".`,
        x => `What is the uppercase letter count for "${x}"?`,
        x => `In "${x}", count every character that is a capital letter.`,
        x => `How many of the letters in "${x}" are uppercase?`,
        x => `Scan "${x}" and count the uppercase letters.`,
        x => `Tell me the number of capital letters in "${x}".`,
      ]);
      return { prompt: t(text) + ' ' + ri(), answer: String([...text].filter(c => c >= 'A' && c <= 'Z').length) };
    }
  },

  transform() {
    const v = pick(['remove_vowels', 'remove_consonants', 'first_letters', 'last_letters', 'swap_case']);
    if (v === 'remove_vowels') {
      const w = pronounceable(randInt(5, 8));
      const t = pick([
        x => `Remove all vowels (A, E, I, O, U) from "${x}".`,
        x => `Delete every vowel from the string "${x}". What remains?`,
        x => `Strip out A, E, I, O, and U from "${x}".`,
        x => `Take "${x}" and remove all vowels.`,
        x => `What do you get when you remove A, E, I, O, U from "${x}"?`,
        x => `From "${x}", delete every A, E, I, O, and U.`,
        x => `Eliminate all vowels from the string "${x}".`,
        x => `Remove each vowel (A, E, I, O, U) from "${x}" and write what is left.`,
        x => `Drop all the vowels from "${x}".`,
        x => `What remains of "${x}" after removing all vowels?`,
        x => `Strip every vowel from "${x}" and give the result.`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: [...w].filter(c => !'AEIOU'.includes(c)).join('').toLowerCase() };
    } else if (v === 'remove_consonants') {
      let w = randChars(UPPER, randInt(6, 10));
      const vowels = [...w].filter(c => 'AEIOU'.includes(c)).join('');
      if (!vowels) return CHALLENGE_TYPES.transform();
      const t = pick([
        x => `Remove all consonants from "${x}" and keep only the vowels (A, E, I, O, U).`,
        x => `Extract only the vowels from "${x}".`,
        x => `From the string "${x}", delete every consonant and keep only vowels.`,
        x => `Keep only the vowels in "${x}" and discard all consonants.`,
        x => `What vowels appear in "${x}"? List them in order.`,
        x => `Strip out all consonants from "${x}", keeping only A, E, I, O, U.`,
        x => `From "${x}", remove every letter that is not a vowel.`,
        x => `Extract the vowels from "${x}" in the order they appear.`,
        x => `Delete all non-vowel letters from "${x}".`,
        x => `After removing consonants from "${x}", what letters remain?`,
        x => `Filter "${x}" to keep only vowels (A, E, I, O, U).`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: vowels.toLowerCase() };
    } else if (v === 'first_letters') {
      const words = Array.from({length: randInt(4, 7)}, () => { let w = randChars('abcdefghijklmnopqrstuvwxyz', randInt(3, 7)); return w[0].toUpperCase() + w.slice(1); });
      const s = words.join(' ');
      const t = pick([
        x => `What do the first letters of each word spell: "${x}"?`,
        x => `Take the initial letter of every word in "${x}" and combine them.`,
        x => `Form an acronym from: "${x}".`,
        x => `Create an acronym by taking the first letter of each word in "${x}".`,
        x => `What word do the initial letters of "${x}" spell?`,
        x => `Extract the first letter of each word in "${x}" and join them.`,
        x => `Take the opening letter from every word in "${x}" and combine them.`,
        x => `If you take the first letter of each word in "${x}", what do you get?`,
        x => `Form a word from the initial letters of: "${x}".`,
        x => `Read the first character of each word in "${x}" and string them together.`,
        x => `What is the acronym for "${x}"?`,
      ]);
      return { prompt: t(s) + ' ' + ri(), answer: words.map(w => w[0]).join('').toLowerCase() };
    } else if (v === 'last_letters') {
      const words = Array.from({length: randInt(4, 6)}, () => { let w = randChars('abcdefghijklmnopqrstuvwxyz', randInt(3, 6)); return w[0].toUpperCase() + w.slice(1); });
      const s = words.join(' ');
      const t = pick([
        x => `What do the LAST letters of each word spell: "${x}"?`,
        x => `Take the final letter of each word in "${x}" and combine them.`,
        x => `Extract the ending letter from every word in "${x}" and join them.`,
        x => `What word do the last letters of each word in "${x}" spell?`,
        x => `Read the final character of each word in "${x}" and combine them.`,
        x => `If you take the last letter of every word in "${x}", what do you get?`,
        x => `From "${x}", pick the ending letter of each word and join them together.`,
        x => `Collect the last letter of every word in "${x}" and form a string.`,
        x => `Extract the terminal letter from each word in "${x}" and concatenate them.`,
        x => `What do you get when you take the final letter of each word in "${x}"?`,
        x => `Take the closing letter of every word in "${x}" and put them together.`,
      ]);
      return { prompt: t(s) + ' ' + ri(), answer: words.map(w => w[w.length - 1]).join('').toLowerCase() };
    } else { // swap_case
      const w = randChars(LETTERS_ALL, randInt(5, 9));
      const swapped = [...w].map(c => c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase()).join('');
      const t = pick([
        x => `Swap the case of every letter in "${x}" (uppercase becomes lowercase, lowercase becomes uppercase).`,
        x => `Invert the case of each character in "${x}".`,
        x => `Toggle uppercase and lowercase for every letter in "${x}".`,
        x => `Change all uppercase letters to lowercase and vice versa in "${x}".`,
        x => `What does "${x}" look like with swapped case?`,
        x => `Flip the case of each letter in "${x}".`,
        x => `For "${x}", convert uppercase to lowercase and lowercase to uppercase.`,
        x => `Apply a case swap to every character in "${x}".`,
      ]);
      return { prompt: t(w) + ' ' + ri(), answer: swapped.toLowerCase() };
    }
  },

  binary() {
    const v = pick(['binary_to_decimal', 'decimal_to_binary', 'digit_sum', 'hex_to_decimal']);
    if (v === 'binary_to_decimal') {
      const num = randInt(1, 63), b = num.toString(2);
      const t = pick([
        x => `Convert binary ${x} to decimal.`,
        x => `What is the decimal value of the binary number ${x}?`,
        x => `Express ${x} (binary) as a base-10 number.`,
        x => `Translate the binary number ${x} into decimal.`,
        x => `What decimal number does the binary ${x} represent?`,
        x => `Convert ${x} from binary to base 10.`,
        x => `Binary ${x} equals what in decimal?`,
        x => `Find the decimal equivalent of binary ${x}.`,
        x => `If ${x} is a binary number, what is it in decimal?`,
        x => `Decode the binary number ${x} into its decimal form.`,
        x => `What base-10 number is represented by ${x} in binary?`,
      ]);
      return { prompt: t(b) + ' ' + ri(), answer: String(num) };
    } else if (v === 'decimal_to_binary') {
      const num = randInt(1, 31);
      const t = pick([
        n => `Convert the decimal number ${n} to binary.`,
        n => `What is ${n} in binary?`,
        n => `Write ${n} as a binary number (no 0b prefix).`,
        n => `Express ${n} in binary form.`,
        n => `Translate ${n} from decimal to binary.`,
        n => `What does the number ${n} look like in binary?`,
        n => `Convert ${n} to base 2.`,
        n => `Write the binary representation of ${n}.`,
        n => `Find the binary equivalent of the decimal number ${n}.`,
        n => `If you convert ${n} to binary, what do you get?`,
        n => `Represent ${n} as a binary number.`,
      ]);
      return { prompt: t(num) + ' ' + ri(), answer: num.toString(2) };
    } else if (v === 'hex_to_decimal') {
      const num = randInt(10, 255);
      const hex = num.toString(16).toUpperCase();
      const t = pick([
        h => `Convert hexadecimal ${h} to decimal.`,
        h => `What is the decimal value of hex ${h}?`,
        h => `Express ${h} (hexadecimal) as a base-10 number.`,
        h => `Translate hex ${h} into decimal.`,
        h => `What decimal number does the hexadecimal value ${h} represent?`,
        h => `Convert ${h} from hex to decimal.`,
        h => `Find the base-10 equivalent of hexadecimal ${h}.`,
        h => `If ${h} is a hexadecimal number, what is its decimal value?`,
      ]);
      return { prompt: t(hex) + ' ' + ri(), answer: String(num) };
    } else {
      const num = randInt(1000, 99999);
      const t = pick([
        n => `What is the sum of all digits in ${n}?`,
        n => `Add each digit of ${n} together.`,
        n => `Calculate the digit sum of ${n}.`,
        n => `Sum the individual digits of ${n}.`,
        n => `Break ${n} into its digits and find their total.`,
        n => `What do you get when you add up every digit in ${n}?`,
        n => `Compute the sum of each digit in the number ${n}.`,
        n => `Find the digit sum of ${n}.`,
        n => `For the number ${n}, add its digits together.`,
        n => `What is the total of all individual digits in ${n}?`,
        n => `Add together each digit that makes up ${n}.`,
      ]);
      return { prompt: t(num) + ' ' + ri(), answer: String([...String(num)].reduce((s, d) => s + Number(d), 0)) };
    }
  },
};

// ── Agentic-tier challenge types (multi-step, chain operations) ──

// ROT13 helper
function _rot13str(s) {
  return s.replace(/[a-zA-Z]/g, c => {
    const base = c <= 'Z' ? 65 : 97;
    return String.fromCharCode((c.charCodeAt(0) - base + 13) % 26 + base);
  });
}

const VOWELS_SET = new Set('AEIOUaeiou');
const CONSONANTS_SET = new Set('BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz');

const CHAINED_OPS = [
  { desc: w => `Take the string "${w}", reverse it, then apply ROT13 to the result.`, ops: [s => [...s].reverse().join(''), _rot13str] },
  { desc: w => `Apply ROT13 to "${w}", then reverse the result.`, ops: [_rot13str, s => [...s].reverse().join('')] },
  { desc: w => `Reverse "${w}", then remove all vowels (A, E, I, O, U) from the result.`, ops: [s => [...s].reverse().join(''), s => [...s].filter(c => !VOWELS_SET.has(c)).join('')] },
  { desc: w => `Take "${w}", extract every 2nd character (positions 1, 3, 5...), then reverse that.`, ops: [s => [...s].filter((_, i) => i % 2 === 0).join(''), s => [...s].reverse().join('')] },
  { desc: w => `Remove all vowels from "${w}", then reverse what's left.`, ops: [s => [...s].filter(c => !VOWELS_SET.has(c)).join(''), s => [...s].reverse().join('')] },
  { desc: w => `Take "${w}", swap uppercase and lowercase, then apply ROT13.`, ops: [s => [...s].map(c => c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase()).join(''), _rot13str] },
  { desc: w => `Reverse "${w}", then extract every 2nd character (positions 1, 3, 5...).`, ops: [s => [...s].reverse().join(''), s => [...s].filter((_, i) => i % 2 === 0).join('')] },
  { desc: w => `Apply ROT13 to "${w}", then remove all consonants, keeping only vowels.`, ops: [_rot13str, s => [...s].filter(c => !CONSONANTS_SET.has(c)).join('')] },
  { desc: w => `Take "${w}", remove all vowels, then apply ROT13 to the remaining letters.`, ops: [s => [...s].filter(c => !VOWELS_SET.has(c)).join(''), _rot13str] },
  { desc: w => `Reverse "${w}", swap the case of each letter, then extract every 2nd character.`, ops: [s => [...s].reverse().join(''), s => [...s].map(c => c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase()).join(''), s => [...s].filter((_, i) => i % 2 === 0).join('')] },
];

CHALLENGE_TYPES.chained_transform = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const len = randInt(7, 10);
  const word = Array.from({ length: len }, () => chars[randInt(0, chars.length - 1)]).join('');
  const chain = pick(CHAINED_OPS);
  let result = word;
  for (const op of chain.ops) result = op(result);
  return { prompt: chain.desc(word) + ' ' + ri(), answer: result.toLowerCase() };
};

CHALLENGE_TYPES.multi_step_math = () => {
  const variant = pick(['mult_add', 'add_digitsum', 'mult_digitsum', 'div_mult', 'expr_mod', 'two_expr']);
  const digitSum = n => [...String(Math.abs(n))].reduce((s, d) => s + Number(d), 0);
  let desc, ans;
  if (variant === 'mult_add') {
    const a = randInt(11, 25), b = randInt(11, 25), c = randInt(10, 50);
    ans = a * b + c; desc = `Calculate ${a} × ${b}, then add ${c} to the result.`;
  } else if (variant === 'add_digitsum') {
    const a = randInt(100, 500), b = randInt(100, 500);
    ans = digitSum(a + b); desc = `Add ${a} and ${b}, then find the digit sum of the result.`;
  } else if (variant === 'mult_digitsum') {
    const a = randInt(12, 30), b = randInt(12, 30);
    ans = digitSum(a * b); desc = `Multiply ${a} by ${b}, then find the digit sum of the result.`;
  } else if (variant === 'div_mult') {
    const div = randInt(3, 12), quot = randInt(5, 25), mult = randInt(2, 9);
    ans = quot * mult; desc = `Divide ${div * quot} by ${div}, then multiply the result by ${mult}.`;
  } else if (variant === 'expr_mod') {
    const a = randInt(15, 50), b = randInt(10, 40), m = randInt(7, 13);
    ans = (a + b) % m; desc = `Add ${a} and ${b}, then find the remainder when divided by ${m}.`;
  } else {
    const a = randInt(11, 30), b = randInt(11, 30), c = randInt(10, 50), d = randInt(10, 50);
    ans = (a * b) + (c + d); desc = `Calculate (${a} × ${b}) + (${c} + ${d}).`;
  }
  const t = pick([d => d, d => `Solve this step by step: ${d}`, d => `Work through this: ${d}`, d => `Compute: ${d}`]);
  return { prompt: t(desc) + ' ' + ri(), answer: String(ans) };
};

CHALLENGE_TYPES.base_conversion_chain = () => {
  const variant = pick(['bin_add', 'hex_sub', 'bin_mult', 'dec_hex']);
  let desc, ans;
  if (variant === 'bin_add') {
    const dec = randInt(10, 50), add = randInt(5, 30);
    ans = (dec + add).toString(2); desc = `Convert binary ${dec.toString(2)} to decimal, add ${add}, then convert the result back to binary.`;
  } else if (variant === 'hex_sub') {
    const dec = randInt(30, 200), sub = randInt(5, dec - 1);
    ans = String(dec - sub); desc = `Convert hexadecimal ${dec.toString(16).toUpperCase()} to decimal, then subtract ${sub}.`;
  } else if (variant === 'bin_mult') {
    const dec = randInt(5, 20), mult = randInt(2, 8);
    ans = String(dec * mult); desc = `Convert binary ${dec.toString(2)} to decimal, then multiply by ${mult}.`;
  } else {
    const a = randInt(5, 15), b = randInt(5, 15);
    ans = (a * b).toString(16); desc = `Multiply ${a} by ${b}, then convert the result to hexadecimal (lowercase).`;
  }
  const t = pick([d => d, d => `Work through this: ${d}`, d => `Solve step by step: ${d}`]);
  return { prompt: t(desc) + ' ' + ri(), answer: ans.toLowerCase() };
};

CHALLENGE_TYPES.word_extraction_chain = () => {
  const cvowels = 'aeiou', ccons = 'bcdfghjklmnprstvwxyz';
  function rword() {
    const len = randInt(4, 8);
    return Array.from({ length: len }, (_, i) => i % 2 === 0 ? ccons[randInt(0, ccons.length - 1)] : cvowels[randInt(0, cvowels.length - 1)]).join('').replace(/^./, c => c.toUpperCase());
  }
  const nw = randInt(5, 7);
  const words = Array.from({ length: nw }, rword);
  const sentence = words.join(' ');
  const variant = pick(['first_sort', 'last_reverse', 'nth_join', 'first_reverse', 'count_vowels']);
  let desc, ans;
  if (variant === 'first_sort') {
    const letters = words.map(w => w[0].toLowerCase()).sort();
    ans = letters.join(', '); desc = `Take the first letter of each word in "${sentence}", then sort them alphabetically.`;
  } else if (variant === 'last_reverse') {
    const letters = words.map(w => w[w.length - 1].toLowerCase()).reverse();
    ans = letters.join(', '); desc = `Take the last letter of each word in "${sentence}", then list them in reverse order.`;
  } else if (variant === 'nth_join') {
    const letters = words.filter(w => w.length >= 2).map(w => w[1].toLowerCase());
    ans = letters.join(''); desc = `Extract the 2nd letter from each word in "${sentence}" and join them together into one string.`;
  } else if (variant === 'first_reverse') {
    const letters = words.map(w => w[0].toLowerCase()).reverse();
    ans = letters.join(''); desc = `Take the first letter of each word in "${sentence}" and write them in reverse order as a single string.`;
  } else {
    const counts = words.map(w => [...w.toLowerCase()].filter(c => 'aeiou'.includes(c)).length);
    ans = counts.join(', '); desc = `Count the number of vowels in each word of "${sentence}" and list the counts separated by commas.`;
  }
  const t = pick([d => d, d => `Follow these steps: ${d}`, d => `Work through this: ${d}`]);
  return { prompt: t(desc) + ' ' + ri(), answer: ans.toLowerCase() };
};

CHALLENGE_TYPES.letter_math = () => {
  const pos = c => c.toUpperCase().charCodeAt(0) - 64;
  const AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const variant = pick(['sum', 'sub', 'mult', 'sum_word', 'prod_mod']);
  let desc, ans;
  if (variant === 'sum') {
    const n = randInt(3, 4);
    const letters = [];
    while (letters.length < n) { const l = AZ[randInt(0, 25)]; if (!letters.includes(l)) letters.push(l); }
    ans = String(letters.reduce((s, l) => s + pos(l), 0));
    desc = `Add the letter values of ${letters.join(', ')}.`;
  } else if (variant === 'sub') {
    const l1 = AZ[randInt(12, 25)], l2 = AZ[randInt(0, 11)];
    ans = String(pos(l1) - pos(l2)); desc = `Subtract the value of ${l2} from the value of ${l1}.`;
  } else if (variant === 'mult') {
    const l1 = AZ[randInt(0, 9)], l2 = AZ[randInt(0, 9)];
    ans = String(pos(l1) * pos(l2)); desc = `Multiply the value of ${l1} by the value of ${l2}.`;
  } else if (variant === 'sum_word') {
    const len = randInt(4, 6);
    const word = Array.from({ length: len }, () => AZ[randInt(0, 25)]).join('');
    ans = String([...word].reduce((s, c) => s + pos(c), 0));
    desc = `Sum the letter values of all characters in "${word}".`;
  } else {
    const l1 = AZ[randInt(0, 7)], l2 = AZ[randInt(0, 7)], m = randInt(5, 10);
    ans = String((pos(l1) * pos(l2)) % m);
    desc = `Multiply the value of ${l1} by ${l2}, then find the remainder when divided by ${m}.`;
  }
  const t = pick([d => d, d => `Using A=1, B=2, ... Z=26: ${d}`, d => `Letter positions: A=1 through Z=26. ${d}`]);
  return { prompt: t(desc) + ' ' + ri(), answer: ans };
};

const DIFFICULTY_MAP = {
  easy: ['reverse_string', 'simple_math', 'pattern', 'counting'],
  medium: ['reverse_string', 'simple_math', 'rot13', 'letter_position', 'extract_letters', 'pattern', 'counting', 'sorting', 'binary'],
  hard: ['caesar', 'word_math', 'transform', 'binary', 'sorting', 'rot13', 'extract_letters', 'letter_position', 'counting', 'pattern', 'reverse_string', 'simple_math'],
  agentic: ['chained_transform', 'multi_step_math', 'base_conversion_chain', 'word_extraction_chain', 'letter_math', 'caesar'],
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
  // HMAC-SHA256 hex is always exactly 64 chars; reject anything else
  if (!/^[0-9a-f]{64}$/.test(sig)) throw new Error('Invalid token signature');
  const expected = hmacSign(data, secret);
  if (!crypto.timingSafeEqual(Buffer.from(sig, 'hex'), Buffer.from(expected, 'hex'))) throw new Error('Invalid token signature');
  return JSON.parse(Buffer.from(data, 'base64url').toString());
}
function hashAnswer(answer) { return crypto.createHash('sha256').update(answer, 'utf8').digest('hex'); }
function normalizeAnswer(answer) {
  if (typeof answer !== 'string') return '';
  let s = answer.trim().toLowerCase();
  if (s.length >= 2 && s[0] === s[s.length - 1] && (s[0] === '"' || s[0] === "'")) s = s.slice(1, -1).trim();
  // Strip trailing punctuation (periods, exclamation marks)
  s = s.replace(/[.!]+$/, '').trim();
  // Canonicalize comma-separated lists: "1,2,3" and "1, 2, 3" → "1, 2, 3"
  if (s.includes(',')) s = s.split(',').map(p => p.trim()).join(', ');
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
   * @param {number} [opts.ttl=300] - Challenge TTL in seconds. Set low (10-15s) to block humans entirely.
   * @param {string[]} [opts.types] - Optional list of allowed challenge types
   * @param {boolean} [opts.persistent=true] - Issue persistent tokens (false = challenge every time)
   */
  constructor({ secret, difficulty = 'easy', ttl = 300, types = null, persistent = true } = {}) {
    if (!secret || secret.length < 8) throw new Error('Secret must be at least 8 characters');
    this._secret = secret;
    this._difficulty = difficulty;
    this._ttl = ttl;
    this._types = types;
    this._persistent = persistent;

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
    const pool = this._types
      ? this._types.filter(t => CHALLENGE_TYPES[t])
      : (DIFFICULTY_MAP[this._difficulty] || DIFFICULTY_MAP.easy);
    if (!pool.length) throw new Error('No valid challenge types configured');
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
    const pool = this._types
      ? this._types.filter(t => CHALLENGE_TYPES[t])
      : (DIFFICULTY_MAP[this._difficulty] || DIFFICULTY_MAP.easy);
    if (!pool.length) throw new Error('No valid challenge types configured');
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

  // ── Gate (unified challenge/auth endpoint) ─────────

  /**
   * Unified challenge gate. Call from a single endpoint.
   *
   * Three modes:
   *   1. token → verify persistent token → { status: "authenticated" }
   *   2. challengeToken + answer → verify → issue persistent token
   *   3. Nothing → issue a new challenge
   *
   * @param {Object} opts
   * @param {string} [opts.token] - Persistent agent token
   * @param {string} [opts.challengeToken] - Challenge token from previous gate()
   * @param {string} [opts.answer] - Agent's answer
   * @returns {{ status: string, prompt?: string, challenge_token?: string, expires_in?: number, token?: string, error?: string }}
   */
  gateSync({ token, challengeToken, answer } = {}) {
    // Mode 1: Persistent token
    if (token) {
      if (!this._persistent) return { status: 'error', error: 'Persistent tokens are disabled' };
      if (this.verifyToken(token)) return { status: 'authenticated' };
      return { status: 'error', error: 'Invalid token' };
    }

    // Mode 2: Submitting answer
    if (challengeToken && answer) {
      const result = this.verify(challengeToken, answer);
      if (result.valid) {
        if (this._persistent) {
          const newToken = this.createToken();
          return { status: 'authenticated', token: newToken };
        }
        return { status: 'authenticated' };
      }
      return { status: 'error', error: result.error || 'Incorrect answer' };
    }

    // Mode 3: Issue challenge
    const challenge = this.createSync();
    const instructions = this._persistent
      ? 'This endpoint requires verification. You are being asked a reasoning challenge to confirm you are a capable AI agent. Read the \'prompt\' field and determine the answer. Then re-send your request to this same endpoint with the following fields included in the JSON body: \'challenge_token\' (the exact value from this response) and \'answer\' (your answer to the prompt as a string). You may include any other fields in the request body alongside these two — they will be passed through. Once verified, you will receive a persistent token in the response. On future requests, include it as an Authorization header: \'Authorization: Bearer <token>\'. You will not be challenged again.'
      : 'This endpoint requires verification. You are being asked a reasoning challenge to confirm you are a capable AI agent. Read the \'prompt\' field and determine the answer. Then re-send your request to this same endpoint with the following fields included in the JSON body: \'challenge_token\' (the exact value from this response) and \'answer\' (your answer to the prompt as a string). You may include any other fields in the request body alongside these two — they will be passed through. Note: this endpoint requires a challenge on every request. No persistent token will be issued.';
    return {
      status: 'challenge_required',
      prompt: challenge.prompt,
      challenge_token: challenge.token,
      expires_in: Math.max(0, challenge.expires_at - Math.floor(Date.now() / 1000)),
      instructions,
    };
  }

  /**
   * Async version of gate (supports dynamic mode).
   */
  async gate({ token, challengeToken, answer } = {}) {
    if (token) {
      if (!this._persistent) return { status: 'error', error: 'Persistent tokens are disabled' };
      if (this.verifyToken(token)) return { status: 'authenticated' };
      return { status: 'error', error: 'Invalid token' };
    }
    if (challengeToken && answer) {
      const result = this.verify(challengeToken, answer);
      if (result.valid) {
        if (this._persistent) return { status: 'authenticated', token: this.createToken() };
        return { status: 'authenticated' };
      }
      return { status: 'error', error: result.error || 'Incorrect answer' };
    }
    const challenge = await this.create();
    const instructions = this._persistent
      ? 'This endpoint requires verification. You are being asked a reasoning challenge to confirm you are a capable AI agent. Read the \'prompt\' field and determine the answer. Then re-send your request to this same endpoint with the following fields included in the JSON body: \'challenge_token\' (the exact value from this response) and \'answer\' (your answer to the prompt as a string). You may include any other fields in the request body alongside these two — they will be passed through. Once verified, you will receive a persistent token in the response. On future requests, include it as an Authorization header: \'Authorization: Bearer <token>\'. You will not be challenged again.'
      : 'This endpoint requires verification. You are being asked a reasoning challenge to confirm you are a capable AI agent. Read the \'prompt\' field and determine the answer. Then re-send your request to this same endpoint with the following fields included in the JSON body: \'challenge_token\' (the exact value from this response) and \'answer\' (your answer to the prompt as a string). You may include any other fields in the request body alongside these two — they will be passed through. Note: this endpoint requires a challenge on every request. No persistent token will be issued.';
    return {
      status: 'challenge_required',
      prompt: challenge.prompt,
      challenge_token: challenge.token,
      expires_in: Math.max(0, challenge.expires_at - Math.floor(Date.now() / 1000)),
      instructions,
    };
  }

  /**
   * Like gateSync(), but extracts token/challengeToken/answer from HTTP request parts.
   * Works with Express, Koa, Fastify, or any framework that gives you headers + body.
   *
   * @param {object} headers - Request headers object (reads 'authorization')
   * @param {object} [body] - Parsed JSON body (reads 'challenge_token' and 'answer')
   * @returns {object} Gate result — same shape as gateSync()
   *
   * @example
   * // Express
   * app.post('/api/secure', (req, res) => {
   *   const result = ac.gateHttp(req.headers, req.body);
   *   if (result.status !== 'authenticated') return res.status(401).json(result);
   *   // your logic
   * });
   */
  gateHttp(headers, body) {
    let token = null;
    const auth = headers?.authorization || headers?.Authorization || '';
    if (auth.toLowerCase().startsWith('bearer ')) {
      token = auth.slice(7).trim() || null;
    }
    const b = (body && typeof body === 'object') ? body : {};
    return this.gateSync({
      token,
      challengeToken: b.challenge_token,
      answer: b.answer,
    });
  }

  // ── Persistent Tokens ─────────────────────────────

  /**
   * Create a persistent agent token (long-lived, HMAC-signed).
   * Issued after an agent solves a challenge. Stateless.
   */
  createToken(agentId) {
    const id = 'at_' + crypto.randomBytes(16).toString('hex');
    const payload = { id, type: 'agent_token', created_at: Math.floor(Date.now() / 1000) };
    if (agentId) payload.agent_id = agentId;
    return encodeToken(payload, this._secret);
  }

  /**
   * Verify a persistent agent token.
   * @returns {boolean}
   */
  verifyToken(token) {
    try {
      const payload = decodeToken(token, this._secret);
      return payload.type === 'agent_token';
    } catch { return false; }
  }
}

export { CHALLENGE_TYPES, DIFFICULTY_MAP, _callLLM };
