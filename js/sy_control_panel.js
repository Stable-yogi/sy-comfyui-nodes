// SY Nodes by Stable Yogi: Control Panel SY. One node with many dials. Each row has its own name, kind and range
// (a number, a whole number, a switch, a text, a dropdown with your own list, or a seed) and is one output.
// "Take widgets from nodes" moves the widgets of other nodes into the panel and connects them.
// The rows are stored as a JSON list in the hidden rows widget, so they save in the workflow and reach the server.
// The node works without this file (the server reads rows). Text is always set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, overlay, hideWidget } from "./sy_ui_kit.js";
import * as L from "./sy_control_panel_logic.js";

const NODE_TYPE = "SYControlPanel";
const FONT = "'DM Sans', sans-serif";
const MIN_W = 380;
const panels = new Set();

function el(tag, css, text) {
  const e = document.createElement(tag);
  if (css) e.style.cssText = css;
  if (text !== undefined) e.textContent = text;
  return e;
}

function stopKeys(input) {
  input.addEventListener("keydown", (e) => e.stopPropagation());
  input.addEventListener("keyup", (e) => e.stopPropagation());
}

const fieldCss = () => "box-sizing:border-box;padding:3px 6px;border-radius:5px;border:1px solid " + tk("surface_4") +
  ";background:" + tk("surface") + ";color:" + tk("white") + ";font:12px " + FONT;

function field(value, width, tip) {
  const i = el("input", fieldCss() + ";width:" + width + "px");
  i.type = "text";
  i.value = value;
  if (tip) i.title = tip;
  stopKeys(i);
  return i;
}

function small(text, tip, onClick) {
  const b = button(text, "ghost", tip);
  b.style.padding = "2px 7px";
  b.onclick = onClick;
  return b;
}

// ---- links: read the targets of an output, so rows can move and keep their wires
function getLink(id) {
  const g = app.canvas?.graph ?? app.graph;
  return g.links?.get ? g.links.get(id) : g.links?.[id];
}

function targetsOf(node, slot) {
  const out = node.outputs?.[slot];
  const res = [];
  for (const id of out?.links || []) {
    const l = getLink(id);
    if (l) res.push({ node: (app.canvas?.graph ?? app.graph).getNodeById(l.target_id), slot: l.target_slot });
  }
  return res.filter((t) => t.node);
}

// ---- the editor
function buildEditor(node) {
  const rawW = node.widgets.find((w) => w.name === "rows");
  if (!rawW) return null;
  hideWidget(rawW);

  let rows = L.parseRows(rawW.value);
  const tmp = new Map(); // row -> {open, last}: things that are not saved
  const info = (r) => {
    if (!tmp.has(r)) tmp.set(r, { open: false, last: null });
    return tmp.get(r);
  };
  const root = el("div", "box-sizing:border-box;width:100%;display:flex;flex-direction:column;gap:4px;font:12px " + FONT + ";color:" + tk("white"));
  const head = el("div", "display:flex;flex-wrap:wrap;gap:4px;align-items:center");
  const body = el("div", "display:flex;flex-direction:column;gap:4px");
  root.append(head, body);

  const save = () => {
    rawW.value = JSON.stringify(rows.map(L.cleanRow));
    node.setDirtyCanvas?.(true, true);
  };

  // outputs follow the rows: one slot per row, with the row's name and type
  function syncOutputs(prune) {
    const want = rows.length;
    while ((node.outputs?.length || 0) < want) node.addOutput("out" + ((node.outputs?.length || 0) + 1), "*");
    if (prune) {
      while ((node.outputs?.length || 0) > want) {
        const last = node.outputs.length - 1;
        if (node.outputs[last].links?.length) break;
        node.removeOutput(last);
      }
    }
    rows.forEach((r, i) => {
      const o = node.outputs[i];
      if (!o) return;
      o.name = "out" + (i + 1);
      o.label = L.rowLabel(r, i);
      o.type = L.OUT_TYPES[r.kind];
    });
    node.setDirtyCanvas?.(true, true);
  }

  let domW = null;
  function fit() {
    requestAnimationFrame(() => {
      if (!domW) return;
      const h = Math.max(60, root.offsetHeight + 8);
      domW.computeSize = (w) => [w, h];
      const need = node.computeSize?.() || [MIN_W, h + 40];
      node.setSize([Math.max(node.size[0], MIN_W), Math.max(need[1], 80)]);
      node.setDirtyCanvas?.(true, true);
    });
  }

  const change = (redraw = true) => {
    save();
    if (redraw) render();
  };

  function numberBody(r, line) {
    const d = L.decimalsOf(r.kind === "int" ? 1 : r.step || 0.01);
    const shown = (v) => (r.kind === "int" ? String(Math.round(v)) : String(Number(v.toFixed(Math.max(d, 4)))));
    const wrap = el("div", "display:flex;align-items:center;gap:6px");
    const num = field(shown(r.value), 84, "Type any number. It is never cut to the slider range.");
    const pos = L.sliderPosition(r);
    if (pos !== null) {
      const sl = el("input", "flex:1;min-width:60px;accent-color:" + tk("gold"));
      sl.type = "range";
      sl.min = "0";
      sl.max = "1000";
      sl.value = String(Math.round(pos * 1000));
      sl.title = "Slider from " + r.min + " to " + r.max + ". Typing a number can go beyond it.";
      sl.oninput = () => {
        r.value = L.valueAtPosition(r, Number(sl.value) / 1000);
        num.value = shown(r.value);
        save();
      };
      sl.onpointerdown = (e) => e.stopPropagation();
      wrap.append(sl);
    } else {
      wrap.append(el("div", "flex:1;color:" + tk("text_2") + ";font-size:11px", "no slider: set a lowest and a highest value in the settings"));
    }
    num.onchange = () => {
      const v = L.typedValue(r, num.value);
      if (v === null) {
        num.value = shown(r.value);
        return;
      }
      r.value = v;
      change();
    };
    wrap.append(num);
    line.append(wrap);
  }

  function seedBody(r, line) {
    const wrap = el("div", "display:flex;align-items:center;gap:6px;flex-wrap:wrap");
    const num = field(String(r.value), 150, "The seed. Whole numbers from 0 up.");
    num.onchange = () => {
      const v = L.typedValue(r, num.value);
      if (v === null) {
        num.value = String(r.value);
        return;
      }
      r.value = Math.min(v, L.MAX_SEED);
      change();
    };
    const mode = el("select", fieldCss());
    for (const m of L.SEED_MODES) mode.append(new Option(m, m, false, m === r.mode));
    mode.title = "Fixed keeps the number. Random picks a new one each run. Increment adds 1 each run.";
    mode.onchange = () => {
      r.mode = mode.value;
      change();
    };
    const dice = small("New random", "Put a new random number in the box now", () => {
      r.value = Math.floor(Math.random() * (L.MAX_SEED + 1));
      change();
    });
    wrap.append(num, mode, dice);
    const last = info(r).last;
    if (last !== null && r.mode !== "fixed") wrap.append(el("span", "color:" + tk("text_2"), "last run used " + last));
    line.append(wrap);
  }

  function switchBody(r, line) {
    const b = button(r.value ? "On" : "Off", r.value ? "on" : "ghost", "Click to switch");
    b.style.minWidth = "64px";
    b.onclick = () => {
      r.value = !r.value;
      change();
    };
    line.append(b);
  }

  function textBody(r, line) {
    const t = el("textarea", fieldCss() + ";width:100%;height:46px;resize:vertical");
    t.value = r.value;
    stopKeys(t);
    t.oninput = () => {
      r.value = t.value;
      save();
    };
    line.append(t);
  }

  function dropdownBody(r, line) {
    const s = el("select", fieldCss() + ";width:100%");
    for (const o of r.options) s.append(new Option(o, o, false, o === r.value));
    s.onchange = () => {
      r.value = s.value;
      save();
    };
    line.append(s);
  }

  function settingsBody(r, line) {
    const box = el("div", "display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:4px;border-radius:6px;background:" + tk("surface"));
    const pair = (text, key, tip) => {
      const f = field(r[key] === null ? "" : String(r[key]), 70, tip);
      f.placeholder = "none";
      f.onchange = () => {
        const t = f.value.trim();
        if (!t) r[key] = null;
        else {
          const x = Number(t.replace(",", "."));
          if (!Number.isFinite(x)) {
            f.value = r[key] === null ? "" : String(r[key]);
            return;
          }
          r[key] = key === "step" ? (x > 0 ? x : null) : x;
        }
        if (r.min !== null && r.max !== null && r.max < r.min) r.max = r.min;
        change();
      };
      box.append(el("span", "color:" + tk("text_2"), text), f);
    };
    if (r.kind === "float" || r.kind === "int") {
      pair("lowest", "min", "Slider starts here. Leave empty for no slider.");
      pair("highest", "max", "Slider ends here. You can still type a bigger number.");
      pair("step", "step", "How far one slider notch goes.");
    }
    if (r.kind === "dropdown") {
      const t = el("textarea", fieldCss() + ";width:100%;height:80px;resize:vertical");
      t.value = r.options.join("\n");
      t.placeholder = "One entry per line";
      stopKeys(t);
      t.onchange = () => {
        r.options = L.optionsFromText(t.value);
        if (!r.options.includes(r.value)) r.value = r.options[0] || "";
        change();
      };
      box.append(el("div", "width:100%;color:" + tk("text_2"), "The list (one entry per line):"), t);
    }
    if (r.kind === "switch" || r.kind === "text" || r.kind === "seed") {
      box.append(el("span", "color:" + tk("text_2"), "No more settings for this kind."));
    }
    line.append(box);
  }

  function render() {
    body.textContent = "";
    if (!rows.length) {
      body.append(el("div", "color:" + tk("text_2") + ";padding:6px", "No rows yet. Use Add row, or Take widgets from nodes."));
    }
    rows.forEach((r, i) => {
      const t = info(r);
      const line = el("div", "display:flex;flex-direction:column;gap:4px;box-sizing:border-box;padding:5px 6px;border-radius:7px;" +
        "background:" + tk("surface_2") + ";border:1px solid " + tk("surface_3"));
      const top = el("div", "display:flex;align-items:center;gap:4px");
      const name = field(r.name, 120, "The name of this row. It is also the name of its output.");
      name.placeholder = "Row " + (i + 1);
      name.style.cssText += ";flex:1;min-width:0;font-weight:600";
      name.oninput = () => {
        r.name = name.value;
        if (node.outputs[i]) node.outputs[i].label = L.rowLabel(r, i);
        save();
      };
      const kind = el("select", fieldCss());
      for (const k of L.KINDS) kind.append(new Option(L.KIND_NAMES[k], k, false, k === r.kind));
      kind.title = "What kind of dial this row is";
      kind.onchange = () => {
        const fresh = L.changeKind(r, kind.value);
        rows[i] = fresh;
        tmp.delete(r);
        syncOutputs(false);
        change();
      };
      const gear = small(t.open ? "settings ^" : "settings", "Range, step, list or seed mode", () => {
        t.open = !t.open;
        render();
      });
      const up = small("up", "Move this row up. Its wire goes with it.", () => moveWithLinks(i, i - 1));
      const down = small("down", "Move this row down. Its wire goes with it.", () => moveWithLinks(i, i + 1));
      const del = small("X", "Delete this row and its wire", () => {
        node.removeOutput(i);
        rows.splice(i, 1);
        tmp.delete(r);
        syncOutputs(false);
        change();
      });
      top.append(name, kind, gear, up, down, del);
      line.append(top);
      if (r.kind === "float" || r.kind === "int") numberBody(r, line);
      else if (r.kind === "seed") seedBody(r, line);
      else if (r.kind === "switch") switchBody(r, line);
      else if (r.kind === "text") textBody(r, line);
      else dropdownBody(r, line);
      if (t.open) settingsBody(r, line);
      body.append(line);
    });
    fit();
  }

  // move a row and carry its wires with it
  function moveWithLinks(from, to) {
    if (to < 0 || to >= rows.length || from < 0 || from >= rows.length) return;
    const a = targetsOf(node, from);
    const b = targetsOf(node, to);
    node.disconnectOutput(from);
    node.disconnectOutput(to);
    L.moveRow(rows, from, to);
    syncOutputs(false);
    for (const t of a) node.connect(to, t.node, t.slot);
    for (const t of b) node.connect(from, t.node, t.slot);
    change();
  }

  function addRow(row) {
    if (rows.length >= L.MAX_ROWS) return null;
    rows.push(row);
    syncOutputs(false);
    return rows.length - 1;
  }

  // ---- take the widgets of other nodes into the panel
  function takeWidgets() {
    const graph = app.canvas?.graph ?? app.graph;
    const ov = overlay("Take widgets from nodes", 620);
    const filter = el("input", fieldCss() + ";width:100%;margin-bottom:8px;font-size:14px");
    filter.placeholder = "Type to filter by node or widget name";
    stopKeys(filter);
    const list = el("div", "display:flex;flex-direction:column;gap:2px;margin-bottom:10px");
    const note = el("div", "color:" + tk("text_2") + ";margin-bottom:8px", "Tick the widgets to move into the panel. Each becomes a row and is connected to its node. The widget on the node then follows the panel.");
    ov.body.append(note, filter, list);
    const chosen = new Map(); // key -> {node, widget, input}
    const items = [];
    for (const n of graph._nodes || []) {
      if (n === node || n.type === NODE_TYPE) continue;
      for (const w of n.widgets || []) {
        if (w.hidden || w.type === "hidden" || w.name === "control_after_generate" || w.type === "button") continue;
        const row = L.rowFromWidget({ type: w.type, value: w.value, name: w.name, options: w.options }, w.label || w.name);
        if (!row) continue;
        const input = (n.inputs || []).findIndex((x) => x.widget && x.widget.name === w.name);
        const linked = input >= 0 && n.inputs[input].link != null;
        items.push({ node: n, widget: w, row, input, linked, title: (n.title || n.type) + " (" + n.id + ")" });
      }
    }
    const go = button("Add 0 widgets to the panel", "gold");
    const draw = () => {
      list.textContent = "";
      const q = filter.value.trim().toLowerCase();
      const hits = items.filter((it) => !q || (it.title + " " + it.widget.name).toLowerCase().includes(q));
      if (!items.length) list.append(el("div", "color:" + tk("text_2"), "No other node has a widget that can move into the panel."));
      let lastTitle = "";
      for (const it of hits.slice(0, 400)) {
        if (it.title !== lastTitle) {
          list.append(el("div", "margin-top:6px;font-weight:700;color:" + tk("gold"), it.title));
          lastTitle = it.title;
        }
        const key = it.node.id + "/" + it.widget.name;
        const line = el("label", "display:flex;gap:8px;align-items:center;padding:2px 4px;border-radius:5px;cursor:" + (it.linked ? "default" : "pointer"));
        const cb = el("input");
        cb.type = "checkbox";
        cb.checked = chosen.has(key);
        cb.disabled = it.linked;
        cb.onchange = () => {
          if (cb.checked) chosen.set(key, it);
          else chosen.delete(key);
          go.textContent = "Add " + chosen.size + " widget" + (chosen.size === 1 ? "" : "s") + " to the panel";
        };
        const shown = typeof it.widget.value === "string" && it.widget.value.length > 40 ? it.widget.value.slice(0, 40) + "..." : String(it.widget.value);
        line.append(cb, el("span", "flex:1", it.widget.name + "  =  " + shown + "   (" + L.KIND_NAMES[it.row.kind] + ")"));
        if (it.linked) line.append(el("span", "color:" + tk("text_2"), "already has a wire"));
        list.append(line);
      }
    };
    filter.oninput = draw;
    go.onclick = () => {
      let added = 0;
      let unplugged = 0;
      for (const it of chosen.values()) {
        const base = L.uniqueName(it.widget.label || it.widget.name, rows);
        const row = { ...it.row, name: base };
        const idx = addRow(row);
        if (idx === null) break;
        let slot = (it.node.inputs || []).findIndex((x) => x.widget && x.widget.name === it.widget.name);
        if (slot < 0 && typeof it.node.convertWidgetToInput === "function") {
          try {
            it.node.convertWidgetToInput(it.widget);
          } catch (_) {
            /* an older page: try to find the socket below */
          }
          slot = (it.node.inputs || []).findIndex((x) => x.widget && x.widget.name === it.widget.name);
        }
        if (slot >= 0 && node.connect(idx, it.node, slot)) added++;
        else unplugged++;
      }
      change();
      ov.close();
      if (unplugged) console.warn("[SY] Control Panel: " + unplugged + " widget(s) were added as rows but could not be connected. Wire them by hand.");
      node.setDirtyCanvas?.(true, true);
    };
    ov.body.append(go);
    draw();
    filter.focus();
  }

  function renderHead() {
    head.textContent = "";
    const add = el("select", fieldCss() + ";font-weight:600");
    add.append(new Option("+ Add row...", ""));
    for (const k of L.KINDS) add.append(new Option(L.KIND_NAMES[k], k));
    add.onchange = () => {
      if (!add.value) return;
      const k = add.value;
      add.value = "";
      addRow(L.newRow(k, ""));
      change();
    };
    const take = button("Take widgets from nodes", "gold", "Move widgets of other nodes into this panel and connect them");
    take.onclick = takeWidgets;
    head.append(add, take);
  }

  domW = node.addDOMWidget("sy_control_panel_rows", "sy_control_panel", root, {
    serialize: false,
    hideOnZoom: false,
    getMinHeight: () => 60,
  });
  domW.computeSize = (w) => [w, 90];

  renderHead();
  render();

  node._syPanel = {
    // after a saved workflow was loaded into the node
    reload() {
      rows = L.parseRows(rawW.value);
      tmp.clear();
      syncOutputs(true);
      renderHead();
      render();
    },
    // the server tells which seed each seed row used
    seeds(map) {
      let moved = false;
      for (const [idx, used] of Object.entries(map)) {
        const r = rows[Number(idx)];
        if (!r || r.kind !== "seed") continue;
        info(r).last = used;
        if (r.mode === "random") {
          r.value = used;
          moved = true;
        }
      }
      if (moved) save();
      render();
    },
    start() {
      syncOutputs(true);
    },
  };
  panels.add(node);
  return root;
}

api.addEventListener("executed", ({ detail }) => {
  try {
    const seeds = L.parseSeeds(detail?.output?.sy_seeds);
    if (!Object.keys(seeds).length) return;
    for (const n of panels) if (String(n.id) === String(detail.node)) n._syPanel?.seeds(seeds);
  } catch (e) {
    console.warn("[SY] Control Panel could not show the seeds of the last run:", e);
  }
});

app.registerExtension({
  name: "sy.control_panel",
  async setup() {
    try {
      await loadTheme();
    } catch (_) {
      /* the colours fall back to transparent; the node still works */
    }
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== NODE_TYPE) return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        buildEditor(this);
        this._syPanel?.start();
      } catch (e) {
        console.warn("[SY] Control Panel could not start:", e);
      }
      return r;
    };
    const configure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configure ? configure.apply(this, arguments) : undefined;
      try {
        this._syPanel?.reload();
      } catch (e) {
        console.warn("[SY] Control Panel could not read the saved rows:", e);
      }
      return r;
    };
    const removed = nodeType.prototype.onRemoved;
    nodeType.prototype.onRemoved = function () {
      panels.delete(this);
      return removed ? removed.apply(this, arguments) : undefined;
    };
  },
});
