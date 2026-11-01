import assert from "node:assert/strict";
import * as L from "../js/sy_toggle_logic.js";

let n = 0;
const ok = (c, m) => { assert.ok(c, m); n++; };
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

// modes
eq(L.modeFor(true, "Mute"), 0); eq(L.modeFor(true, "Bypass"), 0);
eq(L.modeFor(false, "Mute"), 2); eq(L.modeFor(false, "Bypass"), 4);
eq(L.modeFor(false, "bypass"), 4); eq(L.modeFor(false, undefined), 2); eq(L.modeFor(false, "nonsense"), 2);
ok(L.isOnMode(0)); ok(!L.isOnMode(2)); ok(!L.isOnMode(4)); ok(L.isOnMode(undefined)); ok(!L.isOnMode(1));
eq(L.normaliseOffMode("BYPASS"), "Bypass"); eq(L.normaliseOffMode("x"), "Mute");
// inside box
const box = [100, 100, 200, 200];
ok(L.nodeInsideBox({ pos: [150, 150], size: [50, 50] }, box));
ok(!L.nodeInsideBox({ pos: [400, 400], size: [50, 50] }, box));
ok(!L.nodeInsideBox({ pos: [0, 0], size: [10, 10] }, box));
ok(L.nodeInsideBox({ pos: [90, 150], size: [40, 40] }, box));
ok(!L.nodeInsideBox({ pos: [50, 150], size: [40, 40] }, box));
ok(!L.nodeInsideBox(null, box)); ok(!L.nodeInsideBox({ pos: [1, 1], size: [1, 1] }, null));
ok(!L.nodeInsideBox({ pos: [1, 1], size: [1, 1] }, [1, 2]));
eq(L.nodesInsideBox([{ id: 1, pos: [150, 150], size: [10, 10] }, { id: 2, pos: [0, 0], size: [10, 10] }], box).map((x) => x.id), [1]);
eq(L.nodesInsideBox(null, box), []);
// parse / serialize
eq(L.parseTargets('[{"kind":"node","id":12},{"kind":"group","title":"Upscale"}]'), [{ kind: "node", id: 12 }, { kind: "group", title: "Upscale" }]);
eq(L.parseTargets("not json"), []); eq(L.parseTargets(""), []); eq(L.parseTargets(null), []); eq(L.parseTargets("{}"), []);
eq(L.parseTargets([{ kind: "node", id: "5" }]), [{ kind: "node", id: 5 }]);
eq(L.parseTargets([{ kind: "node", id: -1 }]), []);
eq(L.parseTargets([{ kind: "group", title: "  " }]), []);
eq(L.parseTargets([{ kind: "node", id: 1 }, { kind: "node", id: 1 }]), [{ kind: "node", id: 1 }]);
eq(L.parseTargets([null, 5, { kind: "x" }]), []);
eq(L.parseTargets([{ kind: "node", id: 3, extra: 1 }]), [{ kind: "node", id: 3 }]);
eq(JSON.parse(L.serializeTargets([{ kind: "group", title: "A" }])), [{ kind: "group", title: "A" }]);
eq(L.parseTargets(L.serializeTargets([{ kind: "node", id: 7 }, { kind: "group", title: "G" }])), [{ kind: "node", id: 7 }, { kind: "group", title: "G" }]);
// add / remove / move
eq(L.addTarget([], { kind: "node", id: 1 }), [{ kind: "node", id: 1 }]);
eq(L.addTarget([{ kind: "node", id: 1 }], { kind: "node", id: 1 }), [{ kind: "node", id: 1 }]);
eq(L.addTarget([{ kind: "node", id: 1 }], { kind: "bad" }), [{ kind: "node", id: 1 }]);
eq(L.addTarget([{ kind: "group", title: "A" }], { kind: "group", title: "B" }).length, 2);
eq(L.removeTarget([{ kind: "node", id: 1 }, { kind: "node", id: 2 }], 0), [{ kind: "node", id: 2 }]);
eq(L.removeTarget([{ kind: "node", id: 1 }], 5), [{ kind: "node", id: 1 }]);
const three = [{ kind: "node", id: 1 }, { kind: "node", id: 2 }, { kind: "node", id: 3 }];
eq(L.moveTarget(three, 0, 1).map((t) => t.id), [2, 1, 3]);
eq(L.moveTarget(three, 2, -1).map((t) => t.id), [1, 3, 2]);
eq(L.moveTarget(three, 0, -1).map((t) => t.id), [1, 2, 3]);
eq(L.moveTarget(three, 2, 1).map((t) => t.id), [1, 2, 3]);
eq(L.moveTarget(three, 9, 1).map((t) => t.id), [1, 2, 3]);
// radio + bulk
eq(L.radioApply([true, false, false], 1, true), [false, true, false]);
eq(L.radioApply([false, true, false], 1, false), [false, false, false]);
eq(L.radioApply([true, false, true], 0, false), [false, false, true]);
eq(L.radioApply([false, false], 5, true), [false, false]);
eq(L.radioClean([false, true, true]), [false, true, false]);
eq(L.radioClean([false, false]), [false, false]);
eq(L.allOn([false, true]), [true, true]); eq(L.allOff([true, false]), [false, false]);
eq(L.reverse([true, false, true]), [false, true, false]); eq(L.reverse([]), []);
// group state
ok(L.groupIsOn([0, 0])); ok(!L.groupIsOn([0, 2])); ok(!L.groupIsOn([])); ok(!L.groupIsOn([4]));

// text ids (some frontends) become numbers; no duplicates
eq(L.parseTargets([{ kind: "node", id: "12" }, { kind: "node", id: 12 }]), [{ kind: "node", id: 12 }]);
eq(L.parseTargets([{ kind: "node", id: "abc" }, { kind: "node", id: "-3" }, { kind: "node", id: "" }]), []);
eq(L.addTarget([{ kind: "node", id: 5 }], { kind: "node", id: "5" }), [{ kind: "node", id: 5 }]);
ok(L.normId("7") === 7 && L.normId(" 8 ") === 8 && L.normId(1.5) === null && L.normId(null) === null);

console.log("toggle logic checks:", n);
