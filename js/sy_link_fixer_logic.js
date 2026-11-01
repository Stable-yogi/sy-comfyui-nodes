// SY Nodes by Stable Yogi: pure rules for Link Fixer SY. No page code in here, so it can be tested with node.
// They match nodes/sy_link_fixer.py (same problems for the same workflow).
export const TEXT = {
  node_missing: "A wire points to a node that is not there",
  slot_range: "A wire points to a socket the node does not have",
  orphan: "A wire that its target socket does not know about",
  input_dangling: "A socket remembers a wire that does not exist",
  input_wrong_link: "A socket remembers a wire that goes somewhere else",
  output_dangling: "An output remembers a wire that does not exist",
  output_wrong_link: "An output remembers a wire that starts somewhere else",
  type_mismatch: "The two ends carry different kinds of data (only reported, never changed)",
};

const isInt = (v) => typeof v === "number" && Number.isInteger(v);

// Wires from a saved workflow (array form [id, fromNode, fromSlot, toNode, toSlot, type] or object form) as a Map id -> object.
export function normLinks(links) {
  const out = new Map();
  let list = links;
  if (list && !Array.isArray(list) && typeof list === "object") list = list instanceof Map ? [...list.values()] : Object.values(list);
  for (const l of list || []) {
    let d = null;
    if (Array.isArray(l) && l.length >= 5) {
      d = { id: l[0], origin_id: l[1], origin_slot: l[2], target_id: l[3], target_slot: l[4], type: l.length > 5 ? l[5] : null };
    } else if (l && typeof l === "object" && ["id", "origin_id", "origin_slot", "target_id", "target_slot"].every((k) => k in l)) {
      d = { id: l.id, origin_id: l.origin_id, origin_slot: l.origin_slot, target_id: l.target_id, target_slot: l.target_slot, type: l.type ?? null };
    }
    if (d && isInt(d.id)) out.set(d.id, d);
  }
  return out;
}

const typeSet = (t) => new Set(String(t ?? "").split(",").map((x) => x.trim().toUpperCase()).filter(Boolean));

// True only when both ends name a kind of data and the kinds share nothing. "*" and empty fit everything.
export function typesClash(a, b) {
  const A = typeSet(a), B = typeSet(b);
  if (!A.size || !B.size || A.has("*") || B.has("*")) return false;
  for (const x of A) if (B.has(x)) return false;
  return true;
}

// wf: {nodes, links}. Returns [{kind, link, node, slot, text, fix}]; fix is null for a problem that is only reported.
export function findProblems(wf) {
  const nodes = new Map();
  for (const n of (wf && wf.nodes) || []) if (n && typeof n === "object") nodes.set(n.id, n);
  const links = normLinks(wf && wf.links);
  const out = [];
  const seen = new Set();
  const add = (kind, link, node, slot, fix) => {
    if (fix) {
      const key = JSON.stringify(Object.keys(fix).sort().map((k) => [k, fix[k]]));
      if (seen.has(key)) return;
      seen.add(key);
    }
    out.push({ kind, link: link ?? null, node: node ?? null, slot: slot ?? null, text: TEXT[kind], fix: fix || null });
  };
  for (const lid of [...links.keys()].sort((a, b) => a - b)) {
    const L = links.get(lid);
    const o = nodes.get(L.origin_id), t = nodes.get(L.target_id);
    const fix = { op: "removeLink", id: lid };
    if (!o || !t) { add("node_missing", lid, null, null, fix); continue; }
    const outs = o.outputs || [], ins = t.inputs || [];
    const os = L.origin_slot, ts = L.target_slot;
    if (!(isInt(os) && os >= 0 && os < outs.length) || !(isInt(ts) && ts >= 0 && ts < ins.length)) { add("slot_range", lid, null, null, fix); continue; }
    if (ins[ts].link !== lid) { add("orphan", lid, t.id, ts, fix); continue; }
    if (typesClash(outs[os].type, ins[ts].type)) add("type_mismatch", lid, t.id, ts, null);
  }
  const ids = [...nodes.keys()].sort((a, b) => (typeof a === typeof b ? (a < b ? -1 : a > b ? 1 : 0) : String(typeof a) < String(typeof b) ? -1 : 1));
  for (const nid of ids) {
    const n = nodes.get(nid);
    (n.inputs || []).forEach((inp, si) => {
      const lk = inp.link;
      if (lk === null || lk === undefined) return;
      const L = links.get(lk);
      if (!L) add("input_dangling", null, nid, si, { op: "clearInput", node: nid, slot: si });
      else if (L.target_id !== nid || L.target_slot !== si) add("input_wrong_link", lk, nid, si, { op: "clearInput", node: nid, slot: si });
    });
    (n.outputs || []).forEach((outp, si) => {
      for (const lk of outp.links || []) {
        const L = links.get(lk);
        if (!L) add("output_dangling", lk, nid, si, { op: "dropOutputLink", node: nid, slot: si, id: lk });
        else if (L.origin_id !== nid || L.origin_slot !== si) add("output_wrong_link", lk, nid, si, { op: "dropOutputLink", node: nid, slot: si, id: lk });
      }
    });
  }
  return out;
}

// Repairs a COPY of the workflow data (the original is never changed). Returns {data, done}.
export function applyFixes(wf, problems) {
  const data = JSON.parse(JSON.stringify(wf));
  const list = problems || findProblems(data);
  const nodes = new Map();
  for (const n of data.nodes || []) if (n && typeof n === "object") nodes.set(n.id, n);
  let done = 0;
  for (const p of list) {
    const f = p.fix;
    if (!f) continue;
    if (f.op === "removeLink") {
      const lid = f.id;
      if (Array.isArray(data.links)) {
        data.links = data.links.filter((l) => !((Array.isArray(l) && l.length && l[0] === lid) || (l && !Array.isArray(l) && l.id === lid)));
      } else if (data.links && typeof data.links === "object") {
        delete data.links[lid];
      }
      for (const n of nodes.values()) {
        for (const inp of n.inputs || []) if (inp.link === lid) inp.link = null;
        for (const outp of n.outputs || []) if (outp.links) outp.links = outp.links.filter((x) => x !== lid);
      }
    } else if (f.op === "clearInput") {
      const ins = (nodes.get(f.node) || {}).inputs || [];
      if (nodes.has(f.node) && f.slot >= 0 && f.slot < ins.length) ins[f.slot].link = null;
    } else if (f.op === "dropOutputLink") {
      const outs = (nodes.get(f.node) || {}).outputs || [];
      if (nodes.has(f.node) && f.slot >= 0 && f.slot < outs.length && outs[f.slot].links) outs[f.slot].links = outs[f.slot].links.filter((x) => x !== f.id);
    } else {
      continue;
    }
    done++;
  }
  return { data, done };
}

// One line per problem for the panel, at most `max` lines (the rest are counted).
export function summaryLines(problems, max = 12) {
  const lines = problems.slice(0, max).map((p) => {
    const where = p.node !== null ? " (node " + p.node + ", socket " + (Number(p.slot) + 1) + ")" : p.link !== null ? " (wire " + p.link + ")" : "";
    return p.text + where;
  });
  if (problems.length > max) lines.push("...and " + (problems.length - max) + " more");
  return lines;
}
