import assert from "node:assert/strict";
import { splitWords, matchTitles, mix32, pickIndex, planModes } from "../js/sy_random_unmuter_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

eq(splitWords(" Cat, dog ,,CAT,Bird"), ["cat", "dog", "bird"]);
eq(splitWords(""), []); eq(splitWords(null), []); eq(splitWords(" , ,"), []);
const titles = ["Load Cat LoRA", "Load DOG lora", "Sampler", "bird", null];
eq(matchTitles(titles, "cat,dog"), [0, 1]);
eq(matchTitles(titles, "BIRD"), [3]);
eq(matchTitles(titles, ""), []); eq(matchTitles(titles, " ,"), []);
eq(matchTitles(titles, "zzz"), []); eq(matchTitles([], "cat"), []); eq(matchTitles(null, "cat"), []);
// the same fixed vectors as the Python test
const vec = [[1, 0], [1, 1], [12345, 7], [2147483647, 99]];
eq(vec.map((a) => mix32(...a)), [2980047484, 232174035, 1765200083, 594735504]);
eq(vec.map((a) => pickIndex(5, "random", a[0], a[1])), [4, 0, 3, 4]);
eq(pickIndex(0, "random", 0, 0), -1); eq(pickIndex(-3, "round_robin", 0, 0), -1); eq(pickIndex(NaN, "random", 1, 1), -1);
eq([0, 1, 2, 3, 4, 5, 6].map((c) => pickIndex(3, "round_robin", 0, c)), [0, 1, 2, 0, 1, 2, 0]);
eq(pickIndex(4, "random", 0, 0, 0), 0); eq(pickIndex(4, "random", 0, 0, 0.5), 2);
eq(pickIndex(4, "random", 0, 0, 0.9999), 3); eq(pickIndex(4, "random", 0, 0, 1), 3);
eq(pickIndex(1, "random", 77, 5), 0); eq(pickIndex(1, "round_robin", 0, 5), 0);
const seen = new Set();
for (let c = 0; c < 200; c++) seen.add(pickIndex(6, "random", 9, c));
eq([...seen].sort(), [0, 1, 2, 3, 4, 5]);
eq(planModes(3, 1, "Mute"), [2, 0, 2]);
eq(planModes(3, 0, "Bypass"), [0, 4, 4]); eq(planModes(2, -1, "bypass"), [4, 4]); eq(planModes(0, -1, "Mute"), []);
console.log("random unmuter logic checks:", n);
