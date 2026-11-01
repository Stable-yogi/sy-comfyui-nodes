// SY Nodes by Stable Yogi: pure rules for Mute/Bypass Switch SY. No page code in here, so it can be tested with node.
// They match nodes/sy_mute_bypass_switch.py (same answers for the same input).
export const MODE_ON = 0;
export const MODE_MUTE = 2;
export const MODE_BYPASS = 4;

// The LiteGraph mode number: 0 runs, 2 is muted, 4 is bypassed. Anything but "bypass" means mute.
export function modeNumber(on, offMode) {
  if (on) return MODE_ON;
  return String(offMode).trim().toLowerCase() === "bypass" ? MODE_BYPASS : MODE_MUTE;
}

// Node ids from a saved list such as [3, "7"]. Whole numbers only, no duplicates, broken input gives [].
export function parseIds(text) {
  let data = text;
  if (typeof text === "string") {
    try {
      data = JSON.parse(text);
    } catch (_) {
      return [];
    }
  }
  if (!Array.isArray(data)) return [];
  const out = [];
  for (const v of data) {
    let i = null;
    if (typeof v === "number" && Number.isInteger(v) && v >= 0) i = v;
    else if (typeof v === "string" && /^\s*[0-9]+\s*$/.test(v)) i = Number(v.trim());
    if (i !== null && !out.includes(i)) out.push(i);
  }
  return out;
}

// The saved list plus new node ids. The switch itself is never added, duplicates are skipped.
export function addIds(current, newIds, ownId = null) {
  const out = parseIds(current);
  for (const i of parseIds(Array.from(newIds || []))) if (String(i) !== String(ownId) && !out.includes(i)) out.push(i);
  return out;
}

export function removeId(current, id) {
  return parseIds(current).filter((x) => x !== id);
}

const pairName = (p) => String(p ?? "").trim().toLowerCase();

// switches: [{id, pair, on}]. When the changed switch is ON and has a pair name, every OTHER switch that is on with the same
// pair name (spaces and capitals ignored) must go OFF. Returns those ids. Turning one off changes only itself.
export function planPair(switches, changedId) {
  const me = (switches || []).find((s) => s && s.id === changedId);
  if (!me || !me.on) return [];
  const name = pairName(me.pair);
  if (!name) return [];
  return switches.filter((s) => s && s.id !== changedId && s.on && pairName(s.pair) === name).map((s) => s.id);
}

// The text on the targets button.
export function targetsLabel(found, missing) {
  if (!found && !missing) return "No nodes chosen yet";
  return found + (found === 1 ? " node" : " nodes") + (missing ? ", " + missing + " missing" : "");
}
