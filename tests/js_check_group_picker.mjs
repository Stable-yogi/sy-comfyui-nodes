import assert from "node:assert/strict";
import * as L from "../js/sy_group_picker_logic.js";

let n = 0;
const ok = (c, m) => { assert.ok(c, m); n++; };
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

eq(L.parseWords(" Image, MASK ,, "), ["image", "mask"]); eq(L.parseWords(null), []);
const t = ["Anima", "SDXL Loaders", "Krea 2"];
ok(L.chosenIndex(t, "sdxl loaders") === 1 && L.chosenIndex(t, "  Krea 2 ") === 2);
ok(L.chosenIndex(t, "SDXL") === -1 && L.chosenIndex(t, "") === -1 && L.chosenIndex(t, null) === -1 && L.chosenIndex([], "x") === -1);
ok(L.offModeFor("Save Image", "mute", "image") === L.MODE_BYPASS);
ok(L.offModeFor("KSampler", "mute", "image") === L.MODE_MUTE);
ok(L.offModeFor("KSampler", "bypass", "") === L.MODE_BYPASS);
ok(L.offModeFor(null, "mute", "image") === L.MODE_MUTE && L.offModeFor("x", "bogus", "") === L.MODE_BYPASS);

// geometry: two boxes side by side, one node inside each, one outside, one overlapping both
const box = (x) => [x, 0, 100, 100];
const groups = [{ title: "A", box: box(0) }, { title: "B", box: box(200) }];
const nd = (title, x) => ({ title, pos: [x, 10], size: [20, 20] });
const a1 = nd("a1", 10), b1 = nd("Save Image b", 210), out = nd("outside", 500);
const both = { title: "both", pos: [90, 10], size: [220, 20] }; // middle at 200: inside B only
let r = L.planModes(groups, [a1, b1, out], "A", "mute", "image");
eq(r.map((x) => [x.node.title, x.mode]), [["a1", 0], ["Save Image b", 4]]);
r = L.planModes(groups, [a1, b1, out], "B", "mute", "image");
eq(r.map((x) => [x.node.title, x.mode]), [["a1", 2], ["Save Image b", 0]]);
ok(!r.some((x) => x.node === out), "a node outside every group is never touched");
ok(L.planModes(groups, [a1], "Nope", "mute", "") === null && L.planModes(groups, [a1], "", "mute", "") === null);
// a node in both boxes stays on when its group is chosen
const g2 = [{ title: "A", box: [0, 0, 300, 100] }, { title: "B", box: [100, 0, 300, 100] }];
const mid = nd("mid", 150);
eq(L.planModes(g2, [mid], "A", "mute", "").map((x) => x.mode), [0]);
eq(L.planModes(g2, [mid], "B", "mute", "").map((x) => x.mode), [0]);
// skipped nodes (the picker itself) are left alone
eq(L.planModes(groups, [{ ...a1, skip: true }], "B", "mute", ""), []);
ok(L.insideBox(both, groups[1].box) && !L.insideBox(both, groups[0].box));

console.log("group picker logic checks:", n);
