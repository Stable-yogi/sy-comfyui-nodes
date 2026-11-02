import assert from "node:assert/strict";
import { cleanName, duplicateNames, isMissing, uniqueName, setTitle, getTitle, countGets } from "../js/sy_setget_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };
eq(cleanName("  a "), "a"); eq(cleanName(null), ""); eq(cleanName(5), "5");
eq(duplicateNames(["a", "b", " a ", "", null, "c", "b"]), ["a", "b"]); eq(duplicateNames([]), []); eq(duplicateNames(null), []);
eq(isMissing("a", ["a", "b"]), false); eq(isMissing(" a ", [" a"]), false); eq(isMissing("z", ["a"]), true); eq(isMissing("", ["a"]), true); eq(isMissing("a", null), true);
eq(uniqueName("wire", ["wire", "wire 2"]), "wire 3"); eq(uniqueName("x", []), "x"); eq(uniqueName("", ["wire"]), "wire 2"); eq(uniqueName(null, null), "wire");
eq(setTitle("", 0, false), "Set SY"); eq(setTitle("a", 0, false), "Set: a"); eq(setTitle("a", 3, false), "Set: a (3)"); eq(setTitle("a", 1, true), "Set: a (1) - name used twice");
eq(getTitle("", true), "Get SY"); eq(getTitle("a", false), "Get: a"); eq(getTitle("a", true), "Get: a - no Set");
eq(countGets(["a", " a", "b", "", null]), { a: 2, b: 1 }); eq(countGets(null), {});
console.log("set/get logic checks:", n);
