// SY Nodes by Stable Yogi: Link Fixer SY. Checks the open workflow for broken wires and repairs them on a button press (or on open).
// The rules are in sy_link_fixer_logic.js and match nodes/sy_link_fixer.py. The node runs nothing on the server.
// Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, widgetValue } from "./sy_ui_kit.js";
import { findProblems, applyFixes, summaryLines } from "./sy_link_fixer_logic.js";

const TYPE = "SYLinkFixer";
const FONT = "'DM Sans', sans-serif";

function wires(graph) {
  const l = graph.links;
  if (!l) return null;
  return l;
}

function dropLinkFromTable(graph, id) {
  const l = wires(graph);
  if (!l) return;
  if (typeof l.delete === "function") l.delete(id);
  else delete l[id];
}

// The same three operations as apply_fixes in the Python copy, on the live graph. A wire is removed from the table and from every
// socket that names it. A socket that holds a different wire is never touched.
export function applyOps(graph, problems) {
  let done = 0;
  // node ids are numbers in some ComfyUI frontends and text in others, so match them as text
  const byId = new Map((graph._nodes || []).map((n) => [String(n.id), n]));
  for (const p of problems) {
    const f = p.fix;
    if (!f) continue;
    try {
      if (f.op === "removeLink") {
        dropLinkFromTable(graph, f.id);
        for (const n of byId.values()) {
          for (const inp of n.inputs || []) if (inp.link === f.id) inp.link = null;
          for (const outp of n.outputs || []) if (outp.links) outp.links = outp.links.filter((x) => x !== f.id);
        }
      } else if (f.op === "clearInput") {
        const n = byId.get(String(f.node));
        if (n && n.inputs && n.inputs[f.slot]) n.inputs[f.slot].link = null;
      } else if (f.op === "dropOutputLink") {
        const n = byId.get(String(f.node));
        const o = n && n.outputs && n.outputs[f.slot];
        if (o && o.links) o.links = o.links.filter((x) => x !== f.id);
      } else {
        continue;
      }
      done++;
    } catch (e) {
      console.warn("[SY] link fixer: one repair failed", f, e);
    }
  }
  return done;
}

export function checkGraph(graph) {
  return findProblems(graph.serialize());
}

export function repairGraph(graph) {
  let total = 0;
  for (let pass = 0; pass < 3; pass++) {
    const fixable = checkGraph(graph).filter((p) => p.fix);
    if (!fixable.length) break;
    total += applyOps(graph, fixable);
  }
  graph.setDirtyCanvas?.(true, true);
  app.canvas?.setDirty?.(true, true);
  return total;
}

function setup(node) {
  const root = document.createElement("div");
  root.style.cssText = "display:flex;flex-direction:column;gap:6px;padding:4px;box-sizing:border-box;width:100%;font:12px " + FONT + ";color:" + tk("white");
  const row = document.createElement("div");
  row.style.cssText = "display:flex;gap:6px";
  const out = document.createElement("div");
  out.style.cssText = "font:11px " + FONT + ";color:" + tk("text_2") + ";white-space:pre-wrap;word-break:break-word";
  out.textContent = "Press Check wires to look for broken wires.";

  const show = (head, problems) => {
    const lines = summaryLines(problems, 12);
    out.textContent = head + (lines.length ? "\n" + lines.join("\n") : "");
    const want = 150 + Math.min(lines.length, 13) * 16;
    if (node.size && node.size[1] < want) node.setSize?.([Math.max(node.size[0], 380), want]);
  };
  const check = () => {
    const ps = checkGraph(node.graph || app.graph);
    show(ps.length ? ps.length + " problem(s) found." : "No broken wires found.", ps);
    return ps;
  };
  const repair = () => {
    const g = node.graph || app.graph;
    const done = repairGraph(g);
    const left = checkGraph(g);
    show("Repaired " + done + " thing(s). " + (left.length ? left.length + " left (these are only reported)." : "Nothing left."), left);
    return done;
  };
  const b1 = button("Check wires", "ghost", "Looks for broken wires and lists them. Changes nothing.");
  const b2 = button("Repair broken wires", "gold", "Removes the broken wires and the memories of them. Unlike kinds of data are only reported.");
  for (const [b, fn] of [[b1, check], [b2, repair]]) {
    b.onclick = (e) => {
      e.stopPropagation();
      try {
        fn();
      } catch (err) {
        out.textContent = "The check failed: " + (err && err.message ? err.message : String(err));
        console.warn("[SY] link fixer", err);
      }
    };
  }
  // A saved workflow file is checked as it is, before ComfyUI has loaded (and quietly healed) it.
  const picker = document.createElement("input");
  picker.type = "file";
  picker.accept = ".json,application/json";
  picker.style.display = "none";
  const b3 = button("Repair a workflow file...", "ghost", "Pick a saved workflow (.json). It is checked as it is on disk, and you can open a repaired copy. The file itself is never changed.");
  const b4 = button("Open repaired copy", "green", "Opens the repaired copy of the file you picked as a new workflow.");
  b4.style.display = "none";
  let repaired = null;
  picker.onchange = async () => {
    const file = picker.files && picker.files[0];
    picker.value = "";
    b4.style.display = "none";
    repaired = null;
    if (!file) return;
    try {
      let data;
      try {
        data = JSON.parse(await file.text());
      } catch (_) {
        out.textContent = "That file is not a workflow (it is not valid JSON).";
        return;
      }
      if (!data || !Array.isArray(data.nodes)) {
        out.textContent = "That file is not a saved workflow (no nodes list). A workflow saved in API format cannot be checked.";
        return;
      }
      const ps = findProblems(data);
      const { data: fixed, done } = applyFixes(data, ps);
      show((ps.length ? ps.length + " problem(s) found in " + file.name + ". " + done + " can be repaired." : "No broken wires found in " + file.name + "."), ps);
      if (done > 0) {
        repaired = { data: fixed, name: file.name.replace(/\.json$/i, "") + "_repaired" };
        b4.style.display = "";
      }
    } catch (err) {
      out.textContent = "The check failed: " + (err && err.message ? err.message : String(err));
      console.warn("[SY] link fixer file check", err);
    }
  };
  b3.onclick = (e) => {
    e.stopPropagation();
    picker.click();
  };
  b4.onclick = async (e) => {
    e.stopPropagation();
    if (!repaired) return;
    try {
      await app.loadGraphData(repaired.data, true, true, repaired.name);
    } catch (err) {
      out.textContent = "Could not open the repaired copy: " + (err && err.message ? err.message : String(err));
      console.warn("[SY] link fixer open copy", err);
    }
  };
  row.append(b1, b2);
  const row2 = document.createElement("div");
  row2.style.cssText = "display:flex;gap:6px";
  row2.append(b3, b4, picker);
  root.append(row, row2, out);
  const w = node.addDOMWidget("sy_link_fixer_panel", "custom", root, { serialize: false });
  w.computeSize = (width) => [width, 140];
  node._syLinkFixer = { check, repair };
}

app.registerExtension({
  name: "sy.link_fixer",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] link fixer panel not added", e);
      }
      return r;
    };
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configured ? configured.apply(this, arguments) : undefined;
      // a workflow is being opened: wait until every node and wire is in place, then repair once if asked to
      setTimeout(() => {
        try {
          if (this.graph && widgetValue(this, "repair_on_open", false) === true && this._syLinkFixer) this._syLinkFixer.repair();
        } catch (e) {
          console.warn("[SY] link fixer: repair on open failed", e);
        }
      }, 1200);
      return r;
    };
  },
});
