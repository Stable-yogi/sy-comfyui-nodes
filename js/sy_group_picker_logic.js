// SY Nodes by Stable Yogi: Group Picker SY, plain rules. Same rules as nodes/sy_group_picker.py. No browser needed.
export const MODE_ALWAYS = 0;
export const MODE_MUTE = 2;
export const MODE_BYPASS = 4;

export function parseWords(text) {
  return String(text ?? "").split(",").map((w) => w.trim().toLowerCase()).filter(Boolean);
}

export function chosenIndex(titles, choice) {
  const want = String(choice ?? "").trim().toLowerCase();
  if (!want) return -1;
  return titles.findIndex((t) => String(t).trim().toLowerCase() === want);
}

export function offModeFor(title, offMode, bypassWords) {
  const low = String(title ?? "").toLowerCase();
  if (parseWords(bypassWords).some((w) => low.includes(w))) return MODE_BYPASS;
  return offMode === "mute" ? MODE_MUTE : MODE_BYPASS;
}

// true when the middle of the box (x, y, w, h) lies inside the group box
export function insideBox(node, box) {
  const cx = node.pos[0] + node.size[0] / 2;
  const cy = node.pos[1] + node.size[1] / 2;
  return cx >= box[0] && cx <= box[0] + box[2] && cy >= box[1] && cy <= box[1] + box[3];
}

// groups: [{title, box}], nodes: [{title, pos, size, skip}]. Returns [{node, mode}] or null when no group has that name.
// A node inside the chosen group is always on, even when it also sits inside another listed group.
// A node outside every listed group is not in the result, so it is never touched.
export function planModes(groups, nodes, choice, offMode, bypassWords) {
  const k = chosenIndex(groups.map((g) => g.title), choice);
  if (k < 0) return null;
  const out = [];
  for (const n of nodes) {
    if (n.skip) continue;
    const inChosen = insideBox(n, groups[k].box);
    if (inChosen) {
      out.push({ node: n, mode: MODE_ALWAYS });
    } else if (groups.some((g, i) => i !== k && insideBox(n, g.box))) {
      out.push({ node: n, mode: offModeFor(n.title, offMode, bypassWords) });
    }
  }
  return out;
}
