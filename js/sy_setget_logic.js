// SY Nodes by Stable Yogi: Set SY / Get SY, plain rules for the wire names.

export function cleanName(name) {
  return String(name ?? "").trim();
}

// Names that more than one Set node uses (a Get could not tell which one to follow).
export function duplicateNames(names) {
  const seen = new Map();
  for (const raw of names || []) {
    const n = cleanName(raw);
    if (n) seen.set(n, (seen.get(n) || 0) + 1);
  }
  return [...seen.entries()].filter(([, c]) => c > 1).map(([n]) => n).sort();
}

// A Get whose name has no Set (empty names count as missing too).
export function isMissing(getName, setNames) {
  const n = cleanName(getName);
  if (!n) return true;
  return !(setNames || []).some((s) => cleanName(s) === n);
}

// A free wire name: base, then base 2, base 3 ...
export function uniqueName(base, taken) {
  const b = cleanName(base) || "wire";
  const used = new Set((taken || []).map(cleanName));
  if (!used.has(b)) return b;
  let i = 2;
  while (used.has(b + " " + i)) i++;
  return b + " " + i;
}

export function setTitle(name, getCount, duplicate) {
  const n = cleanName(name);
  if (!n) return "Set SY";
  return "Set: " + n + (getCount > 0 ? " (" + getCount + ")" : "") + (duplicate ? " - name used twice" : "");
}

export function getTitle(name, missing) {
  const n = cleanName(name);
  if (!n) return "Get SY";
  return "Get: " + n + (missing ? " - no Set" : "");
}

// How many Get nodes read each name: {name: count}.
export function countGets(getNames) {
  const out = {};
  for (const raw of getNames || []) {
    const n = cleanName(raw);
    if (n) out[n] = (out[n] || 0) + 1;
  }
  return out;
}
