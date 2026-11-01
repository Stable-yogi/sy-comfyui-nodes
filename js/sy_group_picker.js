// SY Nodes by Stable Yogi: Group Picker SY. A list of the groups of the workflow; pick one.
// The nodes of the picked group switch on, the nodes of the other listed groups switch off (mute or bypass).
// The pick is stored in the node, so it is saved with the workflow and put back when the workflow opens.
// The rules are in sy_group_picker_logic.js and match nodes/sy_group_picker.py. Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue, hideWidget } from "./sy_ui_kit.js";
import { chosenIndex, planModes } from "./sy_group_picker_logic.js";

const FONT = "'DM Sans', sans-serif";
const TYPE = "SYGroupPicker";

function boxOf(g) {
  const b = g._bounding;
  if (b && b.length >= 4) return [b[0], b[1], b[2], b[3]];
  return [g.pos[0], g.pos[1], g.size[0], g.size[1]];
}

function groupsOf(node) {
  const needle = String(widgetValue(node, "title_filter", "")).trim().toLowerCase();
  const all = (node.graph?._groups ?? []).filter((g) => String(g.title).toLowerCase().includes(needle));
  return all
    .map((g) => ({ title: String(g.title), box: boxOf(g) }))
    .sort((a, b) => a.box[1] - b.box[1] || a.box[0] - b.box[0]);
}

// Puts the nodes of the picked group on and the nodes of the other listed groups off. Returns the number of nodes changed, or -1.
export function applyChoice(node) {
  const groups = groupsOf(node);
  const nodes = (node.graph?._nodes ?? []).map((n) => ({
    title: n.getTitle ? n.getTitle() : n.title,
    pos: n.pos,
    size: n.size,
    skip: n.type === TYPE,
    ref: n,
  }));
  const plan = planModes(groups, nodes, widgetValue(node, "choice", ""), widgetValue(node, "off_mode", "mute"), widgetValue(node, "bypass_words", ""));
  if (!plan) return -1;
  let changed = 0;
  for (const it of plan) {
    if (it.node.ref.mode !== it.mode) {
      it.node.ref.mode = it.mode;
      changed++;
    }
  }
  if (changed) node.graph?.setDirtyCanvas?.(true, true);
  return changed;
}

function setup(node) {
  const wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-direction:column;gap:4px;width:100%;box-sizing:border-box;padding:2px;font:12px " + FONT + ";color:" + tk("white");
  const status = document.createElement("div");
  status.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2");
  wrap.append(status);
  let rows = [];
  let signature = "";

  const choiceW = () => node.widgets?.find((x) => x.name === "choice");
  hideWidget(choiceW());

  const pick = (title) => {
    const w = choiceW();
    if (!w) return;
    w.value = title;
    w.callback?.(title);
    applyChoice(node);
    refresh();
  };

  const refresh = () => {
    const groups = groupsOf(node);
    const sig = groups.map((g) => g.title).join("|");
    if (sig !== signature) {
      signature = sig;
      for (const r of rows) r.row.remove();
      rows = groups.map((g) => {
        const row = document.createElement("div");
        row.style.cssText = "display:flex;align-items:center;gap:8px;cursor:pointer";
        const ring = document.createElement("div");
        ring.style.cssText = "width:16px;height:16px;border-radius:8px;flex:none;box-sizing:border-box;border:2px solid " + tk("gold_dim") + ";position:relative";
        const dot = document.createElement("div");
        dot.style.cssText = "position:absolute;left:2px;top:2px;width:8px;height:8px;border-radius:4px";
        ring.append(dot);
        const label = document.createElement("span");
        label.style.cssText = "font:600 11px " + FONT + ";overflow:hidden;text-overflow:ellipsis;white-space:nowrap";
        label.textContent = g.title;
        row.append(ring, label);
        row.addEventListener("click", () => pick(g.title));
        wrap.append(row);
        return { row, dot, title: g.title };
      });
      node.__syPickerHeight = 24 * Math.max(1, rows.length) + 28;
      const size = node.computeSize?.();
      if (size && node.size[1] < size[1]) node.setSize([Math.max(node.size[0], 240), size[1]]);
    }
    const choice = String(widgetValue(node, "choice", "") ?? "");
    const k = chosenIndex(groups.map((g) => g.title), choice);
    if (!rows.length) status.textContent = "No groups to show. Make a group, or change the title filter.";
    else if (!choice.trim()) status.textContent = "Pick a group.";
    else if (k < 0) status.textContent = "No group called \"" + choice + "\". Pick one below.";
    else status.textContent = "";
    status.style.display = status.textContent ? "block" : "none";
    rows.forEach((r, i) => {
      r.dot.style.background = i === k ? tk("gold") : "transparent";
      r.row.title = i === k ? "This group is on." : "Click to switch to this group.";
    });
  };

  // changing how nodes are switched off applies the pick again
  for (const name of ["off_mode", "bypass_words"]) {
    const w = node.widgets?.find((x) => x.name === name);
    if (!w) continue;
    const old = w.callback;
    w.callback = function () {
      const r = old ? old.apply(this, arguments) : undefined;
      applyChoice(node);
      return r;
    };
  }

  const w = node.addDOMWidget("sy_group_picker_panel", "custom", wrap, { serialize: false });
  w.computeSize = (width) => [width, node.__syPickerHeight ?? 52];
  node.__syPickerHeight = 52;
  node._syPicker = { refresh, apply: () => applyChoice(node) };
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syPickerSeen) clearInterval(tick);
      return;
    }
    node._syPickerSeen = true;
    try {
      refresh();
    } catch (e) {
      console.warn("[SY] group picker refresh failed", e);
    }
  }, 500);
  refresh();
}

app.registerExtension({
  name: "sy.group_picker",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] group picker panel not added", e);
      }
      return r;
    };
  },
  // a workflow has just opened: put every saved pick back
  afterConfigureGraph() {
    for (const n of app.graph?._nodes ?? []) {
      if (n.type !== TYPE || !widgetValue(n, "apply_on_open", true)) continue;
      try {
        applyChoice(n);
        n._syPicker?.refresh();
      } catch (e) {
        console.warn("[SY] group picker could not apply the saved pick", e);
      }
    }
  },
});
