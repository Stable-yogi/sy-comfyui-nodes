import assert from "node:assert/strict";
import { findProblems, applyFixes, typesClash, normLinks, summaryLines } from "../js/sy_link_fixer_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };
const good = () => ({
  nodes: [
    { id: 1, inputs: [], outputs: [{ name: "img", type: "IMAGE", links: [5] }, { name: "mdl", type: "MODEL", links: [6] }] },
    { id: 2, inputs: [{ name: "image", type: "IMAGE", link: 5 }], outputs: [] },
    { id: 3, inputs: [{ name: "model", type: "MODEL", link: 6 }], outputs: [] },
  ],
  links: [[5, 1, 0, 2, 0, "IMAGE"], [6, 1, 1, 3, 0, "MODEL"]],
});
const kinds = (wf) => findProblems(wf).map((p) => p.kind).sort();

eq(findProblems(good()), []); eq(findProblems({}), []); eq(findProblems(null), []); eq(findProblems({ nodes: [], links: [] }), []);
let d = good();
d.links = [{ id: 5, origin_id: 1, origin_slot: 0, target_id: 2, target_slot: 0, type: "IMAGE" }, { id: 6, origin_id: 1, origin_slot: 1, target_id: 3, target_slot: 0, type: "MODEL" }];
eq(findProblems(d), []);
eq(normLinks(new Map([[5, { id: 5, origin_id: 1, origin_slot: 0, target_id: 2, target_slot: 0 }]])).size, 1);
// 1 node gone
let w = good(); w.nodes.pop();
assert.ok(kinds(w).includes("node_missing")); n++;
let r = applyFixes(w);
eq(findProblems(r.data), []); assert.ok(r.done >= 1); n++;
// 2 slot out of range
w = good(); w.links[0][4] = 3;
assert.ok(kinds(w).includes("slot_range")); n++;
eq(findProblems(applyFixes(w).data), []);
// 3 dangling input
w = good(); w.nodes[1].inputs[0].link = 999;
assert.ok(kinds(w).includes("input_dangling") && kinds(w).includes("orphan")); n++;
r = applyFixes(w);
eq(findProblems(r.data), []); eq(r.data.nodes[1].inputs[0].link, null);
// 4 dangling output
w = good(); w.nodes[0].outputs[0].links.push(77);
eq(kinds(w), ["output_dangling"]);
r = applyFixes(w);
eq(findProblems(r.data), []); eq(r.data.nodes[0].outputs[0].links, [5]); eq(r.done, 1);
// 5 orphan, empty socket
w = good(); w.nodes[2].inputs[0].link = null;
eq(kinds(w), ["orphan"]);
r = applyFixes(w);
eq(findProblems(r.data), []); eq(r.data.links.map((l) => l[0]), [5]);
// 6 orphan whose socket holds a different valid wire
w = good();
w.nodes.push({ id: 4, inputs: [], outputs: [{ name: "img2", type: "IMAGE", links: [8] }] });
w.links.push([8, 4, 0, 2, 0, "IMAGE"]);
w.nodes[1].inputs[0].link = 8;
eq(kinds(w), ["orphan"]);
r = applyFixes(w);
eq(findProblems(r.data), []); eq(r.data.nodes[1].inputs[0].link, 8); eq(r.data.links.map((l) => l[0]), [6, 8]);
// 7, 8 wrong-link memories
w = good(); w.nodes[2].inputs[0].link = 5;
assert.ok(kinds(w).includes("input_wrong_link")); n++;
w = good(); w.nodes[1].outputs = [{ name: "o", type: "IMAGE", links: [6] }];
assert.ok(kinds(w).includes("output_wrong_link")); n++;
// 9 type mismatch: reported, never fixed
w = good(); w.nodes[1].inputs[0].type = "MASK";
let ps = findProblems(w);
eq(ps.map((p) => p.kind), ["type_mismatch"]); eq(ps[0].fix, null);
r = applyFixes(w);
eq(r.done, 0); eq(r.data, w);
assert.ok(!typesClash("*", "IMAGE") && !typesClash("", "IMAGE") && !typesClash("IMAGE,MASK", "mask") && typesClash("IMAGE", "MASK")); n++;
// the original is never changed
w = good(); w.nodes[0].outputs[0].links.push(77);
const before = JSON.stringify(w);
applyFixes(w);
eq(JSON.stringify(w), before);
// everything at once
w = good(); w.nodes[0].outputs[0].links.push(77); w.nodes[2].inputs[0].link = null; w.links.push([9, 42, 0, 1, 0, "IMAGE"]);
eq(findProblems(applyFixes(w).data), []);
// damaged entries are skipped
w = good(); w.links.push(null, 5, "x", [1, 2], { id: "a" });
eq(findProblems(w), []);
// panel text, at most 12 lines + one counter line
w = good();
for (let i = 0; i < 20; i++) w.nodes[0].outputs[0].links.push(100 + i);
const lines = summaryLines(findProblems(w), 12);
eq(lines.length, 13); eq(lines[12], "...and 8 more");
eq(summaryLines([], 12), []);
console.log("link fixer logic checks:", n);
