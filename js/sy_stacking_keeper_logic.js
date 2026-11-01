// SY Nodes by Stable Yogi: Stacking Keeper SY, plain rules. Same rules as nodes/sy_stacking_keeper.py. No browser needed.
export const MAX_IDS = 20000;

export function parseOrder(text) {
  let data = text;
  if (typeof text === "string") {
    try {
      data = JSON.parse(text);
    } catch {
      return [];
    }
  }
  if (!Array.isArray(data)) return [];
  const seen = new Set();
  const out = [];
  for (const v of data.slice(0, MAX_IDS)) {
    if (typeof v !== "number" && typeof v !== "string") continue;
    if (typeof v === "number" && !Number.isInteger(v)) continue;
    const key = String(v).trim();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(key);
  }
  return out;
}

// ids are kept as text; plain numbers sort by value and come before other text
const sortKey = (a, b) => {
  const na = /^\d+$/.test(a), nb = /^\d+$/.test(b);
  if (na && nb) return Number(a) - Number(b);
  if (na !== nb) return na ? -1 : 1;
  return a < b ? -1 : a > b ? 1 : 0;
};

export function mergeOrder(saved, ids) {
  const present = new Set(ids.map((i) => String(i)));
  const kept = saved.filter((i) => present.has(i));
  const known = new Set(kept);
  const added = [...present].filter((i) => !known.has(i)).sort(sortKey);
  return kept.concat(added);
}

export function raiseToFront(order, id) {
  id = String(id);
  return order.filter((i) => i !== id).concat([id]);
}

export function sendToBack(order, id) {
  id = String(id);
  return [id].concat(order.filter((i) => i !== id));
}

// First stacking of a node that has just been added: the nodes on screen are known back to front,
// the others are put behind them (their place against the visible ones is not known).
export function startOrder(allIds, visibleIds) {
  const all = allIds.map((i) => String(i));
  const vis = visibleIds.map((i) => String(i)).filter((i) => all.includes(i));
  const seen = new Set(vis);
  const rest = all.filter((i) => !seen.has(i)).sort(sortKey);
  return rest.concat(vis);
}
