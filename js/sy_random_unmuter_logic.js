// SY Nodes by Stable Yogi: pure rules for Random Unmuter SY. No page code in here, so it can be tested with node.
// They match nodes/sy_random_unmuter.py (same answers for the same input).
export const MAX_SEED = 2 ** 31 - 1;

export function splitWords(text) {
  const out = [];
  for (const raw of String(text ?? "").split(",")) {
    const w = raw.trim().toLowerCase();
    if (w && !out.includes(w)) out.push(w);
  }
  return out;
}

// Positions of the titles that contain ANY word of the filter. An empty filter matches nothing.
export function matchTitles(titles, filter) {
  const words = splitWords(filter);
  if (!words.length) return [];
  const out = [];
  (titles || []).forEach((t, i) => {
    const s = String(t ?? "").toLowerCase();
    if (words.some((w) => s.includes(w))) out.push(i);
  });
  return out;
}

// A fixed 32-bit mix of seed and counter.
export function mix32(seed, counter) {
  let h = Math.imul(Math.trunc(counter) + 1, 0x9e3779b1) >>> 0;
  h = (h ^ (Math.trunc(seed) >>> 0)) >>> 0;
  h = Math.imul((h ^ (h >>> 16)) >>> 0, 0x85ebca6b) >>> 0;
  h = Math.imul((h ^ (h >>> 13)) >>> 0, 0xc2b2ae35) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
}

// Which candidate is ON, or -1 when there are none.
export function pickIndex(count, pick, seed, counter, rand = 0) {
  const n = Math.trunc(count);
  if (!(n > 0)) return -1;
  if (pick === "round_robin") return ((Math.trunc(counter) % n) + n) % n;
  if (Math.trunc(seed) === 0) return Math.min(n - 1, Math.max(0, Math.trunc(Number(rand) * n)));
  return mix32(seed, counter) % n;
}

// The LiteGraph mode number for each candidate: 0 for the chosen one, 2 (mute) or 4 (bypass) for the rest.
export function planModes(count, onIndex, offMode) {
  const off = String(offMode).toLowerCase() === "bypass" ? 4 : 2;
  const out = [];
  for (let i = 0; i < count; i++) out.push(i === onIndex ? 0 : off);
  return out;
}
