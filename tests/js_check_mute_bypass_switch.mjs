import assert from "node:assert/strict";
import { modeNumber, parseIds, addIds, removeId, planPair, targetsLabel } from "../js/sy_mute_bypass_switch_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };
eq(modeNumber(true, "mute"), 0); eq(modeNumber(true, "bypass"), 0); eq(modeNumber(false, "mute"), 2); eq(modeNumber(false, "bypass"), 4);
eq(modeNumber(false, " Bypass "), 4); eq(modeNumber(false, "nonsense"), 2); eq(modeNumber(false, undefined), 2);
eq(parseIds('[3, "7", 3, -1, 2.5, true, null, "x", " 9 "]'), [3, 7, 9]); eq(parseIds("not json"), []); eq(parseIds('{"a":1}'), []); eq(parseIds(null), []); eq(parseIds([1, 2]), [1, 2]); eq(parseIds(""), []);
eq(addIds("[1]", [2, 1, 5], 5), [1, 2]); eq(addIds("bad", [4]), [4]); eq(addIds("[1]", null), [1]); eq(addIds("[1]", new Set([6])), [1, 6]);
eq(removeId("[1,2,3]", 2), [1, 3]); eq(removeId("[1]", 9), [1]);
const sw = [{ id: 1, pair: "Look", on: true }, { id: 2, pair: " look ", on: true }, { id: 3, pair: "other", on: true }, { id: 4, pair: "", on: true }, { id: 5, pair: "LOOK", on: false }];
eq(planPair(sw, 1), [2]); eq(planPair(sw, 5), []); eq(planPair(sw, 3), []); eq(planPair(sw, 4), []); eq(planPair(sw, 99), []); eq(planPair([], 1), []); eq(planPair(null, 1), []);
eq(targetsLabel(0, 0), "No nodes chosen yet"); eq(targetsLabel(1, 0), "1 node"); eq(targetsLabel(3, 2), "3 nodes, 2 missing"); eq(targetsLabel(0, 2), "0 nodes, 2 missing");
eq(addIds("[1]", [2, 5], "5"), [1, 2]); // a frontend that gives node ids as text
console.log("mute bypass switch logic checks:", n);
