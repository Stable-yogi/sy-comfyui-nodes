import assert from "node:assert/strict";
import { findBookmark, sharedKeys, centreOffset, clampZoom, isJumpKey, MIN_ZOOM, MAX_ZOOM } from "../js/sy_bookmark_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

const bms = [{ id: 7, key: "2" }, { id: 3, key: "2" }, { id: 5, key: "1" }];
eq(findBookmark(bms, "1").id, 5);
eq(findBookmark(bms, "2").id, 3);
eq(findBookmark(bms, "9"), null); eq(findBookmark([], "1"), null); eq(findBookmark(null, "1"), null);
eq(findBookmark([{ id: 10, key: "4" }, { id: 9, key: "4" }], 4).id, 9);
eq(findBookmark([{ id: "b", key: "4" }, { id: 2, key: "4" }], "4").id, 2);
eq(sharedKeys(bms), ["2"]); eq(sharedKeys([]), []);
eq(sharedKeys([{ id: 1, key: "3" }, { id: 2, key: "3" }, { id: 3, key: "3" }, { id: 4, key: "1" }, { id: 5, key: "1" }]), ["1", "3"]);
eq(clampZoom(1), 1); eq(clampZoom(0.01), MIN_ZOOM); eq(clampZoom(50), MAX_ZOOM); eq(clampZoom("x"), 1); eq(clampZoom(null), 1); eq(clampZoom(undefined), 1); eq(clampZoom(NaN), 1);
eq(centreOffset([300, 200], [100, 50], 1, 1000, 600), [150, 75]);
const o2 = centreOffset([300, 200], [100, 50], 2, 1000, 600);
eq([(350 + o2[0]) * 2, (225 + o2[1]) * 2], [500, 300]);
// key presses
const press = (key, extra = {}) => isJumpKey({ key, target: { tagName: "CANVAS" }, ...extra });
eq(press("3"), "3"); eq(press("0"), null); eq(press("a"), null);
eq(press("3", { ctrlKey: true }), null); eq(press("3", { altKey: true }), null); eq(press("3", { metaKey: true }), null); eq(press("3", { shiftKey: true }), null);
eq(isJumpKey({ key: "3", target: { tagName: "INPUT" } }), null);
eq(isJumpKey({ key: "3", target: { tagName: "textarea" } }), null);
eq(isJumpKey({ key: "3", target: { tagName: "DIV", isContentEditable: true } }), null);
eq(isJumpKey(null), null);
console.log("bookmark logic checks:", n);
