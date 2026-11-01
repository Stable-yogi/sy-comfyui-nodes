import assert from "node:assert/strict";
import * as L from "../js/sy_control_panel_logic.js";

let n = 0;
const ok = (c, m) => { assert.ok(c, m); n++; };
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

// parse and clean
eq(L.parseRows(""), []); eq(L.parseRows("not json"), []); eq(L.parseRows("{}"), []); eq(L.parseRows(null), []);
let r = L.parseRows('[{"name":"Cfg","kind":"float","value":7.5,"min":1,"max":20,"step":0.5}]')[0];
ok(r.name === "Cfg" && r.kind === "float" && r.value === 7.5 && r.min === 1 && r.max === 20 && r.step === 0.5);
r = L.cleanRow({});
ok(r.kind === "float" && r.value === 0 && r.min === null && r.max === null && r.mode === "fixed" && r.options.length === 0);
ok(L.cleanRow({ kind: "bogus" }).kind === "float");
ok(L.cleanRow({ kind: "switch", value: "yes" }).value === false && L.cleanRow({ kind: "switch", value: true }).value === true);
ok(L.cleanRow({ kind: "text", value: 5 }).value === "");
ok(L.cleanRow({ kind: "int", value: 2.6 }).value === 3);
ok(L.cleanRow({ value: NaN }).value === 0);
ok(L.cleanRow({ min: 5, max: 1 }).max === 5);
ok(L.cleanRow({ step: 0 }).step === null && L.cleanRow({ step: -2 }).step === null);
ok(L.cleanRow({ kind: "seed", mode: "spin" }).mode === "fixed");
eq(L.parseRows(JSON.stringify(Array(40).fill({}))).length, 32);
// label
ok(L.rowLabel({ name: "" }, 2) === "Row 3" && L.rowLabel({ name: "  " }, 0) === "Row 1" && L.rowLabel({ name: "Cfg" }, 0) === "Cfg");
// kinds and types
ok(L.OUT_TYPES.float === "FLOAT" && L.OUT_TYPES.int === "INT" && L.OUT_TYPES.seed === "INT" && L.OUT_TYPES.switch === "BOOLEAN" && L.OUT_TYPES.text === "STRING" && L.OUT_TYPES.dropdown === "COMBO,STRING");
ok(L.KINDS.every((k) => L.KIND_NAMES[k] && L.OUT_TYPES[k]));
// new rows
ok(L.newRow("float", "a").max === 100 && L.newRow("dropdown").options.length === 2 && L.newRow("dropdown").value === "option 1");
ok(L.newRow("switch").value === false && L.newRow("seed").mode === "fixed");
// change kind keeps what fits
let f = L.changeKind({ name: "x", kind: "float", value: 7.6, min: 0, max: 10, step: 0.1, options: [], mode: "fixed" }, "int");
ok(f.kind === "int" && f.value === 8 && f.max === 10 && f.step === 1 && f.name === "x");
f = L.changeKind({ name: "x", kind: "int", value: 4, min: 0, max: 9, step: 1, options: [], mode: "fixed" }, "float");
ok(f.kind === "float" && f.value === 4);
f = L.changeKind({ name: "p", kind: "text", value: "hello", min: null, max: null, step: null, options: [], mode: "fixed" }, "dropdown");
ok(f.kind === "dropdown" && f.value === "hello" && f.options.includes("hello"));
f = L.changeKind({ name: "p", kind: "float", value: 3, min: null, max: null, step: null, options: [], mode: "fixed" }, "text");
ok(f.kind === "text" && f.value === "");
// decimals
ok(L.decimalsOf(1) === 0 && L.decimalsOf(0.01) === 2 && L.decimalsOf(0.25) === 2 && L.decimalsOf(null) === 0 && L.decimalsOf(1e-7) === 7);
// typed values are never cut
const fl = { kind: "float", value: 1, min: 0, max: 10, step: 0.1 };
ok(L.typedValue(fl, "123456.5") === 123456.5 && L.typedValue(fl, "-40") === -40 && L.typedValue(fl, "2,5") === 2.5);
ok(L.typedValue(fl, "abc") === null);
ok(L.typedValue({ kind: "int" }, "-500.4") === -500 && L.typedValue({ kind: "int" }, "7.5") === 8);
ok(L.typedValue({ kind: "seed" }, "-5") === 0 && L.typedValue({ kind: "seed" }, "99") === 99);
// slider
ok(L.sliderPosition({ min: null, max: 10, value: 1 }) === null && L.sliderPosition({ min: 5, max: 5, value: 5 }) === null);
ok(L.sliderPosition({ min: 0, max: 10, value: 5 }) === 0.5);
ok(L.sliderPosition({ min: 0, max: 10, value: 500 }) === 1 && L.sliderPosition({ min: 0, max: 10, value: -9 }) === 0);
ok(L.valueAtPosition({ kind: "float", min: 0, max: 10, step: 0.5, value: 0 }, 0.5) === 5);
ok(L.valueAtPosition({ kind: "int", min: 0, max: 10, step: 1, value: 0 }, 0.34) === 3);
ok(L.valueAtPosition({ kind: "float", min: 0, max: 1, step: 0.01, value: 0 }, 0.333) === 0.33);
ok(L.valueAtPosition({ kind: "float", min: 0, max: 10, step: 0.5, value: 0 }, 2) === 10);
// dropdown text
eq(L.optionsFromText(" a \n\nb\r\na\nc "), ["a", "b", "c"]); eq(L.optionsFromText(null), []);
// widgets of other nodes
let w = L.rowFromWidget({ type: "toggle", value: true, name: "x" }, "Flag");
ok(w.kind === "switch" && w.value === true && w.name === "Flag");
w = L.rowFromWidget({ type: "combo", value: "b", name: "sampler", options: { values: ["a", "b"] } }, "Sampler");
ok(w.kind === "dropdown" && w.value === "b" && w.options.length === 2);
ok(L.rowFromWidget({ type: "combo", value: "", name: "x", options: { values: [] } }, "x") === null);
ok(L.rowFromWidget({ type: "combo", value: "", name: "x", options: { values: () => ["a"] } }, "x") === null);
w = L.rowFromWidget({ type: "number", value: 7, name: "cfg", options: { min: 0, max: 100, step: 5, round: 0.01, precision: 1 } }, "cfg");
ok(w.kind === "float" && w.value === 7 && w.min === 0 && w.max === 100 && w.step === 0.5);
w = L.rowFromWidget({ type: "number", value: 20, name: "steps", options: { min: 1, max: 10000, step: 10, precision: 0 } }, "steps");
ok(w.kind === "int" && w.value === 20 && w.step === 1);
w = L.rowFromWidget({ type: "number", value: 123456789, name: "seed", options: { min: 0, max: 2 ** 53, step: 10, precision: 0 } }, "seed");
ok(w.kind === "seed" && w.value === 123456789 && w.mode === "fixed");
w = L.rowFromWidget({ type: "number", value: 0.5, name: "denoise", options: { min: 0, max: 1, step: 0.1, precision: 2 } }, "denoise");
ok(w.kind === "float" && w.value === 0.5 && w.min === 0 && w.max === 1);
w = L.rowFromWidget({ type: "customtext", value: "hi", name: "text" }, "text");
ok(w.kind === "text" && w.value === "hi");
ok(L.rowFromWidget({ type: "button", value: null, name: "go" }, "go") === null);
ok(L.rowFromWidget({ type: "image", value: "a.png", name: "image" }, "image") === null);
// names
ok(L.uniqueName("cfg", []) === "cfg" && L.uniqueName("cfg", [{ name: "cfg" }]) === "cfg 2" && L.uniqueName("cfg", [{ name: "cfg" }, { name: "cfg 2" }]) === "cfg 3");
ok(L.uniqueName("  ", []) === "Row");
// move
let rows = [{ name: "a" }, { name: "b" }, { name: "c" }];
ok(L.moveRow(rows, 0, 2) && rows.map((x) => x.name).join("") === "bca");
ok(!L.moveRow(rows, 0, 0) && !L.moveRow(rows, -1, 1) && !L.moveRow(rows, 0, 3));
// seeds
eq(L.parseSeeds(['{"0": 123, "2": 45}']), { 0: 123, 2: 45 });
eq(L.parseSeeds(["bad"]), {}); eq(L.parseSeeds(null), {}); eq(L.parseSeeds(['{"x": 1}']), {}); eq(L.parseSeeds(['{"1": "a"}']), {});
ok(L.MAX_SEED === 2 ** 53 - 1 && L.MAX_ROWS === 32);
// a round trip keeps every row
const src = [L.newRow("float", "a"), L.newRow("int", "b"), L.newRow("switch", "c"), L.newRow("text", "d"), L.newRow("dropdown", "e"), L.newRow("seed", "f")];
eq(L.parseRows(JSON.stringify(src)), src);

console.log("control panel logic checks:", n);
