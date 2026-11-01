import assert from "node:assert/strict";
import { cleanLabel, labelLines, labelLook, labelHeight, MAX_TEXT, MIN_SIZE, MAX_SIZE, COLOURS } from "../js/sy_label_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

eq(cleanLabel("Hi", 36, "gold", "left"), { text: "Hi", size: 36, colour: "gold", align: "left" });
eq(cleanLabel(null).text, "");
eq(cleanLabel("x", 5).size, MIN_SIZE); eq(cleanLabel("x", 999).size, MAX_SIZE);
eq(cleanLabel("x", "abc").size, 36); eq(cleanLabel("x", undefined).size, 36);
eq(cleanLabel("x", 40, "pink", "middle"), { text: "x", size: 40, colour: "gold", align: "left" });
eq(cleanLabel("x".repeat(5000)).text.length, MAX_TEXT);
eq(labelLines("\n\nOne\nTwo\n\n"), ["One", "Two"]);
eq(labelLines(""), []); eq(labelLines(null), []); eq(labelLines("  \n "), []);
eq(labelLines("a\r\nb"), ["a", "b"]); eq(labelLines("a\n\nb"), ["a", "", "b"]);
eq(labelLook("A\nB", 40, "grey", "centre"), { lines: ["A", "B"], px: 40, token: "text_2", textAlign: "center" });
eq(labelLook("A", 40, "red", "right").textAlign, "right");
eq(labelHeight({ lines: ["a", "b"], px: 40 }), 2 * 50 + 12);
eq(labelHeight({ lines: [], px: 40 }), 50 + 12);
for (const c of COLOURS) eq(typeof labelLook("x", 20, c, "left").token, "string");
console.log("label logic checks:", n);
