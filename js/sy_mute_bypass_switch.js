// SY Nodes by Stable Yogi: Mute/Bypass Switch SY. One switch for the nodes you choose: on runs them, off mutes or bypasses them.
// The chosen node ids are kept in the node's properties (saved with the workflow). Nothing changes when a workflow opens.
// Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, setWidget, widgetValue } from "./sy_ui_kit.js";
import { modeNumber, parseIds, addIds, planPair, targetsLabel } from "./sy_mute_bypass_switch_logic.js";

const TYPE = "SYMuteBypassSwitch";
const FONT = "'DM Sans', sans-serif";
const PROP = "sy_targets";

const graphOf = () => app.graph || app.canvas?.graph;

function targetsOf(node) {
  return parseIds(node.properties?.[PROP]).filter((i) => String(i) !== String(node.id));
}

function saveTargets(node, ids) {
  node.properties = node.properties || {};
  node.properties[PROP] = JSON.stringify(ids);
}

// Put every chosen node into the mode the switch says. Returns how many were found and how many are missing.
function apply(node) {
  const g = graphOf();
  if (!g) return { found: 0, missing: 0 };
  const mode = modeNumber(!!widgetValue(node, "on", true), widgetValue(node, "off_mode", "mute"));
  let found = 0;
  let missing = 0;
  for (const id of targetsOf(node)) {
    const t = g.getNodeById ? g.getNodeById(id) : null;
    if (!t) {
      missing++;
      continue;
    }
    found++;
    t.mode = mode;
  }
  g.setDirtyCanvas?.(true, true);
  return { found, missing };
}

function allSwitches() {
  const g = graphOf();
  return (g?._nodes || []).filter((n) => n.type === TYPE);
}

// A switch was turned on: other switches in the same pair go off.
function runPair(node) {
  const list = allSwitches().map((n) => ({
    id: n.id,
    pair: widgetValue(n, "pair", ""),
    on: !!widgetValue(n, "on", true),
  }));
  for (const id of planPair(list, node.id)) {
    const other = allSwitches().find((n) => n.id === id);
    if (!other) continue;
    setWidget(other, "on", false);
    apply(other);
    other._syRefresh?.();
  }
}

function setup(node) {
  const root = document.createElement("div");
  root.style.cssText = "display:flex;gap:6px;align-items:center;flex-wrap:wrap;padding:4px;box-sizing:border-box;width:100%;font:12px " + FONT + ";color:" + tk("white");
  const bAdd = button("Add selected nodes", "ghost", "Select nodes on the canvas first, then press this to put them under this switch.");
  const bClear = button("Clear", "ghost", "Forget all chosen nodes. Their current mode stays as it is.");
  const bShow = button("", "ghost", "Select the chosen nodes on the canvas.");
  const refresh = () => {
    const ids = targetsOf(node);
    const g = graphOf();
    const found = g ? ids.filter((i) => g.getNodeById?.(i)).length : ids.length;
    bShow.textContent = targetsLabel(found, ids.length - found);
  };
  bAdd.onclick = (e) => {
    e.stopPropagation();
    const sel = Object.values(app.canvas?.selected_nodes || {}).map((n) => n.id);
    saveTargets(node, addIds(node.properties?.[PROP], sel, node.id));
    apply(node);
    refresh();
  };
  bClear.onclick = (e) => {
    e.stopPropagation();
    saveTargets(node, []);
    refresh();
  };
  bShow.onclick = (e) => {
    e.stopPropagation();
    const g = graphOf();
    const nodes = targetsOf(node).map((i) => g?.getNodeById?.(i)).filter(Boolean);
    if (!nodes.length) return;
    app.canvas?.deselectAll?.();
    for (const n of nodes) app.canvas?.select?.(n);
    app.canvas?.setDirty?.(true, true);
  };
  root.append(bAdd, bClear, bShow);
  const w = node.addDOMWidget("sy_mute_bypass_targets", "custom", root, { serialize: false });
  w.computeSize = (width) => [width, 34];
  node._syRefresh = refresh;
  refresh();

  // react to the switch widgets
  for (const name of ["on", "off_mode"]) {
    const widget = (node.widgets || []).find((x) => x.name === name);
    if (!widget) continue;
    const prev = widget.callback;
    widget.callback = function () {
      const r = prev ? prev.apply(this, arguments) : undefined;
      apply(node);
      if (name === "on" && widgetValue(node, "on", true)) runPair(node);
      refresh();
      return r;
    };
  }
}

app.registerExtension({
  name: "sy.mute_bypass_switch",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
        this.properties = this.properties || {};
        if (this.properties[PROP] === undefined) saveTargets(this, []);
      } catch (e) {
        console.warn("[SY] mute/bypass switch not set up", e);
      }
      return r;
    };
    // after a load the targets exist again: refresh the label only, never change a mode
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configured ? configured.apply(this, arguments) : undefined;
      setTimeout(() => this._syRefresh?.(), 300);
      return r;
    };
  },
});
