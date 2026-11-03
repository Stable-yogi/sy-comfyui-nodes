import assert from "node:assert/strict";
import {
  COLOURS, MAX_BOXES, MAX_LABEL, rgb, nextColour, parseBoxes, serialiseBoxes, snapTo, fitBox, viewFor, toPanel, toPicture,
  hitTest, boxFromDrag, moveBox, resizeBox, describe,
} from "../js/sy_layout_draw_logic.js";

let n = 0;
const eq = (a, b) => { assert.deepEqual(a, b); n++; };

// colours
eq(COLOURS.length, 10);
eq(rgb("red"), "rgb(230,50,50)"); eq(rgb("blue", 0.3), "rgba(60,110,230,0.3)"); eq(rgb("nope"), "rgb(230,50,50)");
eq(nextColour("red"), "orange"); eq(nextColour("black"), "red"); eq(nextColour("?"), "red");

// parse / serialise
eq(parseBoxes(""), []); eq(parseBoxes(null), []); eq(parseBoxes("[]"), []); eq(parseBoxes("{bad"), []); eq(parseBoxes('{"a":1}'), []);
eq(parseBoxes('[{"x":1.4,"y":2.6,"w":10,"h":20,"label":"a","colour":"green"}]'), [{ x: 1, y: 3, w: 10, h: 20, label: "a", colour: "green" }]);
eq(parseBoxes('[{"x":0,"y":0,"w":5,"h":5},{"x":0,"y":0,"w":5,"h":5,"color":"pink"}]').map((b) => b.colour), ["red", "pink"]);
eq(parseBoxes('[1,null,{"x":"a","y":0,"w":1,"h":1},{"x":0,"y":0,"w":0,"h":1},{"x":0,"y":0,"w":2,"h":2}]').length, 1);
eq(parseBoxes('[{"x":0,"y":0,"w":2,"h":2,"label":"' + "z".repeat(200) + '"}]')[0].label.length, MAX_LABEL);
eq(parseBoxes(JSON.stringify(Array.from({ length: 80 }, () => ({ x: 0, y: 0, w: 1, h: 1 })))).length, MAX_BOXES);
const sample = [{ x: 1, y: 2, w: 3, h: 4, label: "L", colour: "cyan" }];
eq(parseBoxes(serialiseBoxes(sample)), sample);
eq(serialiseBoxes([]), "[]");

// snap and fit
eq(snapTo(13, 8), 16); eq(snapTo(12, 8), 16); eq(snapTo(11, 8), 8); eq(snapTo(13.4, 1), 13); eq(snapTo(5, 0), 5);
eq(fitBox({ x: -5, y: 990, w: 50, h: 50, label: "", colour: "red" }, 100, 100), { x: 0, y: 50, w: 50, h: 50, label: "", colour: "red" });
eq(fitBox({ x: 0, y: 0, w: 9999, h: 0, label: "", colour: "red" }, 100, 80).w, 100);
eq(fitBox({ x: 0, y: 0, w: 5, h: 0, label: "", colour: "red" }, 100, 80).h, 1);

// view maths: 1000x500 picture in a 316x200 panel, pad 6 -> scale 0.304
const v = viewFor(1000, 500, 316, 200);
eq(Math.round(v.scale * 1000) / 1000, 0.304);
eq(v.ox, 6); eq(v.oy, 24);
const [sx, sy] = toPanel(v, 100, 100);
const [bx, by] = toPicture(v, sx, sy);
eq([Math.round(bx), Math.round(by)], [100, 100]);
assert.ok(viewFor(10, 10, 4, 4).scale > 0); n++;

// hit test: box 100..300 x 100..200, scale 0.304
const boxes = [
  { x: 100, y: 100, w: 200, h: 100, label: "a", colour: "red" },
  { x: 150, y: 120, w: 50, h: 50, label: "b", colour: "blue" },
];
const at = (px, py) => toPanel(v, px, py);
eq(hitTest(boxes, v, ...at(100, 100)), { index: 0, part: "tl" });
eq(hitTest(boxes, v, ...at(300, 100)), { index: 0, part: "tr" });
eq(hitTest(boxes, v, ...at(100, 200)), { index: 0, part: "bl" });
eq(hitTest(boxes, v, ...at(300, 200)), { index: 0, part: "br" });
eq(hitTest(boxes, v, ...at(250, 180)), { index: 0, part: "body" });
eq(hitTest(boxes, v, ...at(170, 140)), { index: 1, part: "body" });      // the top box wins where two overlap
eq(hitTest(boxes, v, ...at(700, 400)), null);
eq(hitTest([], v, 10, 10), null);

// drag to create: any direction, clamped, snapped
eq(boxFromDrag(10, 20, 110, 70, 200, 200, 1, "x", "red"), { x: 10, y: 20, w: 100, h: 50, label: "x", colour: "red" });
eq(boxFromDrag(110, 70, 10, 20, 200, 200, 1, "x", "red"), { x: 10, y: 20, w: 100, h: 50, label: "x", colour: "red" });
eq(boxFromDrag(-50, -50, 500, 500, 200, 100, 1, "", "red"), { x: 0, y: 0, w: 200, h: 100, label: "", colour: "red" });
eq(boxFromDrag(13, 13, 61, 61, 200, 200, 8, "", "red"), { x: 16, y: 16, w: 48, h: 48, label: "", colour: "red" });
eq(boxFromDrag(50, 50, 50, 50, 200, 200, 1, "", "red").w, 1);

// move: stays inside
const s = { x: 10, y: 10, w: 50, h: 50, label: "m", colour: "green" };
eq(moveBox(s, 20, 5, 200, 200, 1), { ...s, x: 30, y: 15 });
eq(moveBox(s, -100, -100, 200, 200, 1), { ...s, x: 0, y: 0 });
eq(moveBox(s, 500, 500, 200, 100, 1), { ...s, x: 150, y: 50 });
eq(moveBox(s, 7, 0, 200, 200, 8).x, 16);

// resize: the opposite corner stays put
eq(resizeBox(s, "br", 100, 120, 200, 200, 1), { x: 10, y: 10, w: 90, h: 110, label: "m", colour: "green" });
eq(resizeBox(s, "tl", 0, 0, 200, 200, 1), { x: 0, y: 0, w: 60, h: 60, label: "m", colour: "green" });
eq(resizeBox(s, "tr", 90, 0, 200, 200, 1), { x: 10, y: 0, w: 80, h: 60, label: "m", colour: "green" });
eq(resizeBox(s, "bl", 0, 90, 200, 200, 1), { x: 0, y: 10, w: 60, h: 80, label: "m", colour: "green" });
eq(resizeBox(s, "br", 5, 5, 200, 200, 1).x, 5);                          // dragged past the other corner: it flips, no negative size
assert.ok(resizeBox(s, "br", 10, 10, 200, 200, 1).w >= 1); n++;

// text
eq(describe(s), "m: 50 x 50 at 10, 10"); eq(describe({ x: 1, y: 2, w: 3, h: 4, label: "", colour: "red" }), "3 x 4 at 1, 2");
console.log("layout draw logic checks:", n);
