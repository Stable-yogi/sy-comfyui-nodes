import assert from "node:assert/strict";
import { MAX_SEED, isSeedName, clampSeed, nextSeed, fitSeed, parseWords, skipByTitle, summary } from "../js/sy_global_seed_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };
eq(clampSeed(-1), 0); eq(clampSeed("x"), 0); eq(clampSeed(2 ** 60), MAX_SEED); eq(clampSeed("42"), 42); eq(clampSeed(7.9), 7); eq(clampSeed(Infinity), 0);
eq(nextSeed(5, "fixed", 0.3), 5); eq(nextSeed(5, "increment"), 6); eq(nextSeed(MAX_SEED, "increment"), 0);
eq(nextSeed(5, "decrement"), 4); eq(nextSeed(0, "decrement"), MAX_SEED); eq(nextSeed(1, "random", 0), 0);
eq(nextSeed(1, "random", 0.5), (MAX_SEED + 1) / 2); eq(nextSeed(1, " Random ", 0.9999999999999999) <= MAX_SEED, true); eq(nextSeed(9, "nonsense"), 9);
eq(fitSeed(10, 20), 10); eq(fitSeed(25, 20), 4); eq(fitSeed(25, "bad"), 25); eq(fitSeed(25, -1), 25);
eq(isSeedName("seed"), true); eq(isSeedName(" Noise_Seed "), true); eq(isSeedName("steps"), false); eq(isSeedName(null), false);
eq(parseWords(" Face, Hands ,,"), ["face", "hands"]); eq(parseWords(null), []);
eq(skipByTitle("Face Detailer", ["face"]), true); eq(skipByTitle("Sampler", ["face"]), false); eq(skipByTitle("x", []), false);
eq(summary(0), "No seed boxes found"); eq(summary(1), "1 seed box set"); eq(summary(4), "4 seed boxes set");
console.log("global seed logic checks:", n);
