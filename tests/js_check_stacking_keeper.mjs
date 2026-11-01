import assert from "node:assert/strict";
import * as L from "../js/sy_stacking_keeper_logic.js";

let n = 0;
const ok = (c, m) => { assert.ok(c, m); n++; };
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

// reading a saved stacking
eq(L.parseOrder("[3, 1, 2]"), ["3", "1", "2"]);
eq(L.parseOrder("[]"), []); eq(L.parseOrder(""), []); eq(L.parseOrder(null), []);
eq(L.parseOrder("{bad"), []); eq(L.parseOrder('{"a": 1}'), []); eq(L.parseOrder("7"), []);
eq(L.parseOrder('[1, "2", 3.5, true, null, [4], 5, "", "  "]'), ["1", "2", "5"]);
eq(L.parseOrder('[1, 2, 1, "2", 3]'), ["1", "2", "3"]);
eq(L.parseOrder([4, "x"]), ["4", "x"]);
ok(L.parseOrder(JSON.stringify(Array.from({ length: 30000 }, (_, i) => i + 1))).length === L.MAX_IDS);
// merging with the nodes that exist now
eq(L.mergeOrder(["3", "1", "2"], [1, 2, 3]), ["3", "1", "2"]);
eq(L.mergeOrder(["3", "1", "2"], ["1", "3"]), ["3", "1"]);
eq(L.mergeOrder(["3", "1"], [1, 2, 3, 7]), ["3", "1", "2", "7"]);
eq(L.mergeOrder([], [5, 2, 9, 10]), ["2", "5", "9", "10"]);
eq(L.mergeOrder([], ["b", 2, "a"]), ["2", "a", "b"]);
eq(L.mergeOrder(["1", "2"], []), []);
// raise and lower
eq(L.raiseToFront(["1", "2", "3"], 1), ["2", "3", "1"]); eq(L.raiseToFront(["1", "2", "3"], "3"), ["1", "2", "3"]); eq(L.raiseToFront(["1", "2"], 9), ["1", "2", "9"]);
eq(L.sendToBack(["1", "2", "3"], 3), ["3", "1", "2"]); eq(L.sendToBack(["1", "2", "3"], "1"), ["1", "2", "3"]); eq(L.sendToBack(["1", "2"], 9), ["9", "1", "2"]);
// first stacking of a node added by hand
eq(L.startOrder(["1", "2", "3", "4"], ["3", "1"]), ["2", "4", "3", "1"]);
eq(L.startOrder([1, 2], []), ["1", "2"]);
eq(L.startOrder([1, 2], ["9", 2]), ["1", "2"]);
// a round trip through the saved text
const order = L.raiseToFront(L.sendToBack(["1", "2", "3", "4"], 4), 2);
eq(L.mergeOrder(L.parseOrder(JSON.stringify(order)), [1, 2, 3, 4]), ["4", "1", "3", "2"]);

console.log("stacking keeper logic checks:", n);
