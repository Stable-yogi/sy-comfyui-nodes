// SY Nodes by Stable Yogi: pure rules for Layout Box Draw SY. No page code in here, so it can be tested with node.
// The box list is the same JSON that nodes/sy_layout_box_draw.py reads.
export const COLOURS = ["red", "orange", "yellow", "green", "cyan", "blue", "purple", "pink", "white", "black"];
export const RGB = {
  red: [230, 50, 50], orange: [240, 140, 30], yellow: [240, 220, 50], green: [60, 190, 90], cyan: [50, 200, 210],
  blue: [60, 110, 230], purple: [150, 90, 220], pink: [235, 100, 170], white: [245, 245, 245], black: [15, 15, 15],
};
export const MAX_BOXES = 64;
export const MAX_LABEL = 80;
export const MIN_BOX = 4;       // a drag smaller than this (in picture pixels) is a click, not a box
export const HANDLE = 8;        // corner handle size on the panel, in panel pixels

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const whole = (v) => Math.round(Number.isFinite(v) ? v : 0);

export function rgb(colour, alpha) {
  const c = RGB[colour] || RGB.red;
  return alpha === undefined ? "rgb(" + c.join(",") + ")" : "rgba(" + c.join(",") + "," + alpha + ")";
}

export function nextColour(colour) {
  const i = COLOURS.indexOf(colour);
  return COLOURS[(i + 1) % COLOURS.length];
}

// Read the boxes widget text. Anything that cannot be read gives []. Never throws.
export function parseBoxes(text) {
  let data;
  try {
    data = JSON.parse(String(text ?? "").trim() || "[]");
  } catch (e) {
    return [];
  }
  if (!Array.isArray(data)) return [];
  const out = [];
  for (const it of data) {
    if (!it || typeof it !== "object") continue;
    const x = Number(it.x), y = Number(it.y), w = Number(it.w), h = Number(it.h);
    if (![x, y, w, h].every(Number.isFinite) || w <= 0 || h <= 0) continue;
    const colour = COLOURS.includes(it.colour) ? it.colour : COLOURS.includes(it.color) ? it.color : COLOURS[out.length % COLOURS.length];
    out.push({ x: whole(x), y: whole(y), w: Math.max(1, whole(w)), h: Math.max(1, whole(h)), label: String(it.label ?? "").slice(0, MAX_LABEL), colour });
    if (out.length >= MAX_BOXES) break;
  }
  return out;
}

export function serialiseBoxes(boxes) {
  return JSON.stringify(boxes.map((b) => ({ x: b.x, y: b.y, w: b.w, h: b.h, label: b.label, colour: b.colour })));
}

// Snap a number to a multiple (1 or less = off).
export function snapTo(v, step) {
  const s = Math.max(1, whole(step));
  return s <= 1 ? whole(v) : Math.round(v / s) * s;
}

// Keep a box inside the picture and at least 1 pixel big.
export function fitBox(b, cw, ch) {
  const w = clamp(whole(b.w), 1, cw), h = clamp(whole(b.h), 1, ch);
  return { ...b, w, h, x: clamp(whole(b.x), 0, cw - w), y: clamp(whole(b.y), 0, ch - h) };
}

// Picture pixels <-> panel pixels. The picture is shown as large as fits in the panel, keeping its shape.
export function viewFor(cw, ch, panelW, panelH, pad = 6) {
  const scale = Math.max(1e-6, Math.min((panelW - 2 * pad) / cw, (panelH - 2 * pad) / ch));
  return { scale, ox: Math.round((panelW - cw * scale) / 2), oy: Math.round((panelH - ch * scale) / 2), cw, ch };
}
export const toPanel = (view, px, py) => [view.ox + px * view.scale, view.oy + py * view.scale];
export const toPicture = (view, sx, sy) => [(sx - view.ox) / view.scale, (sy - view.oy) / view.scale];

// What is under the pointer: {index, part} where part is "tl" "tr" "bl" "br" (a corner handle) or "body"; null for empty space.
// The topmost (last) box wins.
export function hitTest(boxes, view, sx, sy) {
  const [px, py] = toPicture(view, sx, sy);
  for (let i = boxes.length - 1; i >= 0; i--) {
    const b = boxes[i];
    const reach = Math.max(1, Math.min(HANDLE / view.scale, b.w / 3, b.h / 3));   // small boxes keep a body to grab
    const nearX = (cx) => Math.abs(px - cx) <= reach;
    const nearY = (cy) => Math.abs(py - cy) <= reach;
    if (nearY(b.y) && nearX(b.x)) return { index: i, part: "tl" };
    if (nearY(b.y) && nearX(b.x + b.w)) return { index: i, part: "tr" };
    if (nearY(b.y + b.h) && nearX(b.x)) return { index: i, part: "bl" };
    if (nearY(b.y + b.h) && nearX(b.x + b.w)) return { index: i, part: "br" };
    if (px >= b.x && px <= b.x + b.w && py >= b.y && py <= b.y + b.h) return { index: i, part: "body" };
  }
  return null;
}

// A box from two corner points (picture pixels), in any direction, kept inside the picture and snapped.
export function boxFromDrag(x0, y0, x1, y1, cw, ch, snap, label, colour) {
  const ax = clamp(Math.min(x0, x1), 0, cw), bx = clamp(Math.max(x0, x1), 0, cw);
  const ay = clamp(Math.min(y0, y1), 0, ch), by = clamp(Math.max(y0, y1), 0, ch);
  const sx = snapTo(ax, snap), ex = snapTo(bx, snap), sy = snapTo(ay, snap), ey = snapTo(by, snap);
  return fitBox({ x: sx, y: sy, w: Math.max(1, ex - sx), h: Math.max(1, ey - sy), label: label || "", colour }, cw, ch);
}

// Move a box by a distance (picture pixels) from where it started; it stays inside the picture.
export function moveBox(start, dx, dy, cw, ch, snap) {
  return fitBox({ ...start, x: snapTo(start.x + dx, snap), y: snapTo(start.y + dy, snap) }, cw, ch);
}

// Resize by dragging one corner to a picture point; the opposite corner stays still.
export function resizeBox(start, part, px, py, cw, ch, snap) {
  const fixedX = part === "tl" || part === "bl" ? start.x + start.w : start.x;
  const fixedY = part === "tl" || part === "tr" ? start.y + start.h : start.y;
  const b = boxFromDrag(fixedX, fixedY, px, py, cw, ch, snap, start.label, start.colour);
  return b;
}

// Short text for a tooltip or the readout under the panel.
export function describe(b) {
  return (b.label ? b.label + ": " : "") + b.w + " x " + b.h + " at " + b.x + ", " + b.y;
}
