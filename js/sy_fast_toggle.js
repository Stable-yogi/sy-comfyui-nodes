// SY Nodes by Stable Yogi: Fast Toggle SY. One panel with big on/off switches for nodes or groups of this workflow.
// Virtual node: it never reaches the server. Off means muted or bypassed (your choice in the Mode box).
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, overlay } from "./sy_ui_kit.js";
import * as L from "./sy_toggle_logic.js";

const TYPE = "SYFastToggle";
const FONT = "'DM Sans', sans-serif";

function graphOf(node) {
  return node.graph || app.graph;
}

function findGroup(graph, title) {
  return (graph?._groups || []).find((g) => g.title === title) || null;
}

function groupBox(g) {
  if (g._bounding && g._bounding.length >= 4) return [g._bounding[0], g._bounding[1], g._bounding[2], g._bounding[3]];
  if (g.pos && g.size) return [g.pos[0], g.pos[1], g.size[0], g.size[1]];
  return null;
}

function groupNodes(graph, g) {
  const box = groupBox(g);
  return box ? L.nodesInsideBox(graph._nodes || [], box) : [];
}

// Resolve one saved row to {label, missing, nodes: [LiteGraph nodes], isOn}
function resolve(graph, t) {
  try {
    if (t.kind === "node") {
      const n = graph.getNodeById(t.id);
      if (!n) return { label: "Node " + t.id, missing: true, nodes: [], isOn: false };
      return { label: n.title || n.type || "Node " + t.id, missing: false, nodes: [n], isOn: L.isOnMode(n.mode) };
    }
    const g = findGroup(graph, t.title);
    if (!g) return { label: t.title, missing: true, nodes: [], isOn: false };
    const nodes = groupNodes(graph, g);
    return { label: t.title, missing: false, group: g, nodes, isOn: L.groupIsOn(nodes.map((n) => n.mode)) };
  } catch (_) {
    return { label: "?", missing: true, nodes: [], isOn: false };
  }
}

function centreOn(box) {
  try {
    const canvas = app.canvas;
    const ds = canvas.ds;
    const cx = box[0] + box[2] / 2;
    const cy = box[1] + box[3] / 2;
    const w = canvas.canvas.width / ds.scale;
    const h = canvas.canvas.height / ds.scale;
    ds.offset[0] = -cx + w / 2;
    ds.offset[1] = -cy + h / 2;
    canvas.setDirty(true, true);
  } catch (err) {
    console.warn("[SY] could not centre the canvas", err);
  }
}

function targetBox(r) {
  if (r.group) return groupBox(r.group);
  const n = r.nodes[0];
  return n ? [n.pos[0], n.pos[1], n.size[0], n.size[1]] : null;
}

function build(node) {
  const root = document.createElement("div");
  root.style.cssText = "display:flex;flex-direction:column;gap:6px;padding:6px;box-sizing:border-box;width:100%;" +
    "font:12px " + FONT + ";color:" + tk("white");
  const head = document.createElement("div");
  head.style.cssText = "display:flex;flex-wrap:wrap;gap:4px;align-items:center";
  const list = document.createElement("div");
  list.style.cssText = "display:flex;flex-direction:column;gap:4px";
  root.append(head, list);

  const props = () => (node.properties = node.properties || {});
  const getTargets = () => L.parseTargets(props().sy_targets);
  const setTargets = (arr) => {
    props().sy_targets = L.serializeTargets(arr);
    render();
  };
  const offMode = () => L.normaliseOffMode(props().sy_mode);
  const radio = () => props().sy_radio === true || props().sy_radio === "true";

  function apply(r, on) {
    const mode = L.modeFor(on, offMode());
    for (const n of r.nodes) n.mode = mode;
  }

  function setOne(index, on) {
    const g = graphOf(node);
    const rows = getTargets().map((t) => resolve(g, t));
    if (radio()) {
      const next = L.radioApply(rows.map((r) => r.isOn), index, on);
      rows.forEach((r, i) => {
        if (!r.missing) apply(r, next[i]);
      });
    } else if (rows[index] && !rows[index].missing) {
      apply(rows[index], on);
    }
    changed();
  }

  function setAll(fn) {
    const g = graphOf(node);
    const rows = getTargets().map((t) => resolve(g, t));
    const next = fn(rows.map((r) => r.isOn));
    const fixed = radio() ? L.radioClean(next) : next;
    rows.forEach((r, i) => {
      if (!r.missing) apply(r, fixed[i]);
    });
    changed();
  }

  function changed() {
    try {
      graphOf(node).change?.();
      app.canvas?.setDirty(true, true);
    } catch (_) { /* the canvas redraws on its own later */ }
    render();
  }

  function small(text, tip, fn) {
    const b = button(text, "ghost", tip);
    b.style.padding = "2px 6px";
    b.onclick = (e) => {
      e.stopPropagation();
      try {
        fn();
      } catch (err) {
        console.warn("[SY] fast toggle", err);
      }
    };
    return b;
  }

  // ---- header (built once)
  const modeLabel = document.createElement("span");
  modeLabel.textContent = "Mode";
  modeLabel.style.color = tk("text_2");
  const modeSel = document.createElement("select");
  for (const m of L.MODES) {
    const o = document.createElement("option");
    o.value = m;
    o.textContent = m;
    modeSel.append(o);
  }
  modeSel.title = "What Off does: Mute stops the node, Bypass lets the picture pass through it.";
  modeSel.style.cssText = "background:" + tk("surface_3") + ";color:" + tk("white") + ";border:0;border-radius:6px;padding:3px";
  modeSel.onchange = () => {
    props().sy_mode = modeSel.value;
    // switch the nodes that are already off to the new off mode
    const g = graphOf(node);
    for (const t of getTargets()) {
      const r = resolve(g, t);
      if (!r.missing) for (const n of r.nodes) if (!L.isOnMode(n.mode)) n.mode = L.modeFor(false, modeSel.value);
    }
    changed();
  };
  const radioLabel = document.createElement("label");
  radioLabel.title = "Only one switch can be on at a time.";
  radioLabel.style.cssText = "display:flex;gap:3px;align-items:center;color:" + tk("text_2");
  const radioBox = document.createElement("input");
  radioBox.type = "checkbox";
  radioBox.onchange = () => {
    props().sy_radio = radioBox.checked;
    if (radioBox.checked) setAll(L.radioClean);
  };
  const radioText = document.createElement("span");
  radioText.textContent = "Only one on";
  radioLabel.append(radioBox, radioText);

  const addSel = small("+ Add selected nodes", "Adds the nodes you have selected on the canvas.", () => {
    const sel = Object.values(app.canvas?.selected_nodes || {}).filter((n) => n && n.id !== node.id);
    let cur = getTargets();
    for (const n of sel) cur = L.addTarget(cur, { kind: "node", id: n.id });
    setTargets(cur);
  });
  const addGrp = small("+ Add group...", "Pick a group from this workflow.", () => {
    const groups = (graphOf(node)._groups || []).map((g) => g.title).filter(Boolean);
    const ov = overlay("Add a group", 360);
    if (!groups.length) {
      const none = document.createElement("div");
      none.textContent = "This workflow has no groups yet.";
      ov.body.append(none);
      return;
    }
    const col = document.createElement("div");
    col.style.cssText = "display:flex;flex-direction:column;gap:4px";
    for (const title of [...new Set(groups)]) {
      const b = button(title, "ghost");
      b.style.textAlign = "left";
      b.onclick = () => {
        setTargets(L.addTarget(getTargets(), { kind: "group", title }));
        ov.close();
      };
      col.append(b);
    }
    ov.body.append(col);
  });
  head.append(
    modeLabel, modeSel, radioLabel, addSel, addGrp,
    small("All on", "Switch every row on.", () => setAll(L.allOn)),
    small("All off", "Switch every row off.", () => setAll(L.allOff)),
    small("Reverse", "Flip every switch.", () => setAll(L.reverse)),
  );

  let lastSig = "";
  function render() {
    try {
      const g = graphOf(node);
      modeSel.value = offMode();
      radioBox.checked = radio();
      const targets = getTargets();
      const rows = targets.map((t) => resolve(g, t));
      const sig = JSON.stringify([targets, rows.map((r) => [r.label, r.missing, r.isOn, r.nodes.length]), offMode(), radio()]);
      if (sig === lastSig) return;
      lastSig = sig;
      list.textContent = "";
      if (!targets.length) {
        const hint = document.createElement("div");
        hint.textContent = "Nothing here yet. Select nodes and press \"+ Add selected nodes\", or add a group.";
        hint.style.cssText = "color:" + tk("text_2") + ";padding:4px";
        list.append(hint);
      }
      rows.forEach((r, i) => {
        const line = document.createElement("div");
        line.style.cssText = "display:flex;gap:6px;align-items:center;padding:3px 4px;border-radius:6px;background:" + tk("surface_2");
        const sw = document.createElement("button");
        sw.type = "button";
        sw.title = r.missing ? "Not found" : r.isOn ? "On. Click to switch off." : "Off. Click to switch on.";
        sw.setAttribute("aria-pressed", String(r.isOn));
        sw.style.cssText = "cursor:pointer;border:0;border-radius:11px;width:40px;height:22px;position:relative;flex:none;background:" +
          (r.isOn ? tk("green_btn") : tk("surface_4"));
        const knob = document.createElement("span");
        knob.style.cssText = "position:absolute;top:3px;width:16px;height:16px;border-radius:8px;background:" + tk("white") +
          ";left:" + (r.isOn ? "21px" : "3px");
        sw.append(knob);
        sw.disabled = r.missing;
        sw.onclick = (e) => {
          e.stopPropagation();
          setOne(i, !r.isOn);
        };
        const name = document.createElement("span");
        name.textContent = (r.group ? "[group] " : "") + r.label + (r.missing ? "  (not found)" : "");
        name.style.cssText = "flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" +
          (r.missing ? "text-decoration:line-through;color:" + tk("text_2") : "");
        const find = small("→", "Show it on the canvas.", () => {
          const box = targetBox(r);
          if (box) centreOn(box);
        });
        find.disabled = r.missing;
        const up = small("▲", "Move up.", () => setTargets(L.moveTarget(getTargets(), i, -1)));
        const down = small("▼", "Move down.", () => setTargets(L.moveTarget(getTargets(), i, 1)));
        const x = small("X", "Remove this row (the node is not changed).", () => setTargets(L.removeTarget(getTargets(), i)));
        line.append(sw, name, find, up, down, x);
        list.append(line);
      });
      const want = Math.max(110, 70 + rows.length * 34);
      if (node.size && node.size[1] < want && !node._sy_user_sized) {
        node.setSize?.([Math.max(node.size[0], 420), want]);
      }
    } catch (err) {
      console.warn("[SY] fast toggle draw", err);
    }
  }
  return { root, render };
}

function register() {
  const LG = window.LiteGraph;
  if (!LG || LG.registered_node_types?.[TYPE]) return;

  class SyFastToggleNode extends LG.LGraphNode {
    constructor() {
      super("Fast Toggle SY");
      this.isVirtualNode = true;
      this.properties = this.properties || {};
      this.properties.sy_targets = this.properties.sy_targets || "[]";
      this.properties.sy_mode = this.properties.sy_mode || "Mute";
      this.properties.sy_radio = this.properties.sy_radio === true;
      this.serialize_widgets = false;
      this.size = [430, 130];
      try {
        const ui = build(this);
        this._sy_ui = ui;
        const w = this.addDOMWidget("sy_toggle_panel", "sy_toggle_panel", ui.root, {
          serialize: false,
          hideOnZoom: false,
          getMinHeight: () => 90,
        });
        if (w) w.serialize = false;
        // keep names and states live: look again twice a second while this node is on the canvas
        this._sy_timer = setInterval(() => {
          if (!this.graph) return;
          ui.render();
        }, 500);
        ui.render();
      } catch (err) {
        console.warn("[SY] fast toggle could not start", err);
      }
    }
    onConfigure() {
      // node ids are checked again on load: rows whose target is gone show as "not found"
      try {
        this.properties.sy_targets = L.serializeTargets(this.properties.sy_targets);
        setTimeout(() => this._sy_ui?.render(), 0);
      } catch (_) { /* leave the list as saved */ }
    }
    onResize() {
      this._sy_user_sized = true;
    }
    onRemoved() {
      if (this._sy_timer) clearInterval(this._sy_timer);
    }
  }
  SyFastToggleNode.title = "Fast Toggle SY";
  SyFastToggleNode.category = "SY/Utility";
  LG.registerNodeType(TYPE, SyFastToggleNode);
}

app.registerExtension({
  name: "sy.fast_toggle",
  async setup() {
    await loadTheme();
    register();
  },
  async nodeCreated(node) {
    if (node.type === TYPE) node.isVirtualNode = true;
  },
});
