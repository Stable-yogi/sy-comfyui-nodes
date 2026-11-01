// SY Nodes by Stable Yogi: pure logic for Fast Toggle SY. No page code in here, so it can be tested with node.
export const MODE_ON = 0;
export const MODE_MUTE = 2;
export const MODE_BYPASS = 4;
export const MODES = ["Mute", "Bypass"];

// The LiteGraph mode number for a switch state. offMode is "Mute" or "Bypass".
export function modeFor(on, offMode) {
  if (on) return MODE_ON;
  return String(offMode).toLowerCase() === "bypass" ? MODE_BYPASS : MODE_MUTE;
}

// A target counts as on only when it runs normally.
export function isOnMode(mode) {
  return (mode ?? MODE_ON) === MODE_ON;
}

export function normaliseOffMode(value) {
  return String(value).toLowerCase() === "bypass" ? "Bypass" : "Mute";
}

// Is the middle of a node inside a box [x, y, width, height]? Node is {pos:[x,y], size:[w,h]}.
export function nodeInsideBox(node, box) {
  if (!node || !box || !node.pos || !node.size || box.length < 4) return false;
  const cx = node.pos[0] + node.size[0] / 2;
  const cy = node.pos[1] + node.size[1] / 2;
  return cx >= box[0] && cx <= box[0] + box[2] && cy >= box[1] && cy <= box[1] + box[3];
}

export function nodesInsideBox(nodes, box) {
  return (nodes || []).filter((n) => nodeInsideBox(n, box));
}

// Read the saved list. Anything broken is dropped, never thrown.
// A node id is a whole number, or a numeric text such as "12" (some ComfyUI frontends hand out text ids).
// Numeric text becomes a number so the same node never appears twice.
export function normId(v) {
  if (Number.isInteger(v) && v >= 0) return v;
  if (typeof v === "string" && /^[0-9]+$/.test(v.trim())) return Number(v.trim());
  return null;
}

export function parseTargets(text) {
  let data;
  try {
    data = typeof text === "string" ? JSON.parse(text) : text;
  } catch (_) {
    return [];
  }
  if (!Array.isArray(data)) return [];
  const out = [];
  for (const t of data) {
    if (!t || typeof t !== "object") continue;
    const id = t.kind === "node" ? normId(t.id) : null;
    if (t.kind === "node" && id !== null) {
      if (!out.some((o) => o.kind === "node" && o.id === id)) out.push({ kind: "node", id });
    } else if (t.kind === "group" && typeof t.title === "string" && t.title.trim() !== "") {
      if (!out.some((o) => o.kind === "group" && o.title === t.title)) out.push({ kind: "group", title: t.title });
    }
  }
  return out;
}

export function serializeTargets(list) {
  return JSON.stringify(parseTargets(list));
}

export function addTarget(list, target) {
  const cur = parseTargets(list);
  const [one] = parseTargets([target]);
  if (!one) return cur;
  if (cur.some((o) => o.kind === one.kind && (one.kind === "node" ? o.id === one.id : o.title === one.title))) return cur;
  return [...cur, one];
}

export function removeTarget(list, index) {
  const cur = parseTargets(list);
  if (!Number.isInteger(index) || index < 0 || index >= cur.length) return cur;
  return cur.filter((_, i) => i !== index);
}

// Move one row by -1 (up) or +1 (down). Out of range leaves the list as it is.
export function moveTarget(list, index, delta) {
  const cur = parseTargets(list);
  const to = index + delta;
  if (!Number.isInteger(index) || index < 0 || index >= cur.length || to < 0 || to >= cur.length) return cur;
  const copy = cur.slice();
  const [item] = copy.splice(index, 1);
  copy.splice(to, 0, item);
  return copy;
}

// States are an array of booleans (true = on). Radio rule: turning one on turns all others off.
// Turning one off changes only that one. Returns a new array.
export function radioApply(states, index, wantOn) {
  if (!wantOn) return states.map((s, i) => (i === index ? false : s));
  return states.map((_, i) => i === index);
}

// When radio mode is switched on while several are on: keep only the first one that is on.
export function radioClean(states) {
  const first = states.indexOf(true);
  return states.map((_, i) => i === first);
}

export function allOn(states) {
  return states.map(() => true);
}

export function allOff(states) {
  return states.map(() => false);
}

export function reverse(states) {
  return states.map((s) => !s);
}

// A group counts as on when every node inside runs normally. An empty group counts as off.
export function groupIsOn(modes) {
  return modes.length > 0 && modes.every((m) => isOnMode(m));
}
