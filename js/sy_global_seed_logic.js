// SY Nodes by Stable Yogi: Global Seed SY, plain rules. The same rules are in nodes/sy_global_seed.py.
export const MAX_SEED = 2 ** 53 - 1; // the biggest whole number a browser keeps exact
export const MODES = ["fixed", "random", "increment", "decrement"];
const SEED_NAMES = ["seed", "noise_seed", "rng_seed"];

export function isSeedName(name) {
  return SEED_NAMES.includes(String(name || "").trim().toLowerCase());
}

export function clampSeed(value) {
  const n = Math.floor(Number(value));
  if (!Number.isFinite(n) || n < 0) return 0;
  return Math.min(n, MAX_SEED);
}

// The seed for the NEXT run. rnd is a number from 0 up to (not including) 1; pass Math.random().
export function nextSeed(seed, mode, rnd) {
  const s = clampSeed(seed);
  const m = String(mode || "").trim().toLowerCase();
  if (m === "random") return Math.min(MAX_SEED, Math.floor((Number(rnd) || 0) * (MAX_SEED + 1)));
  if (m === "increment") return s >= MAX_SEED ? 0 : s + 1;
  if (m === "decrement") return s <= 0 ? MAX_SEED : s - 1;
  return s; // fixed, or an unknown word
}

// A target seed box can be smaller than ours. A bigger seed is folded into its range, a smaller one is kept.
export function fitSeed(seed, max) {
  const s = clampSeed(seed);
  const top = Number(max);
  if (!Number.isFinite(top) || top < 0 || s <= top) return s;
  return s % (Math.floor(top) + 1);
}

export function parseWords(text) {
  return String(text || "").split(",").map((w) => w.trim().toLowerCase()).filter(Boolean);
}

// True when the node title holds one of the skip words.
export function skipByTitle(title, words) {
  const t = String(title || "").toLowerCase();
  return (words || []).some((w) => w && t.includes(w));
}

export function summary(count) {
  return count === 0 ? "No seed boxes found" : count === 1 ? "1 seed box set" : count + " seed boxes set";
}
