// SY Nodes by Stable Yogi: colour coding, SY mark and the SY Nodes side panel.
// Reads colours from sy_theme.json (the one colour file). No network, no eval, no storage of secrets.
import { app } from "../../scripts/app.js";

const EXT = "sy.ui";
const PREFIX = "SY";
const SETTING_COLOR = "SY.ColorMode";
const SETTING_MARK = "SY.ShowMark";

let theme = null;

async function loadTheme() {
  if (theme) return theme;
  try {
    const res = await fetch(new URL("./sy_theme.json", import.meta.url));
    theme = await res.json();
  } catch (err) {
    console.warn("[SY] colour file not loaded, using plain colours", err);
    theme = { tokens: {}, groups: {} };
  }
  return theme;
}

function setting(id, fallback) {
  try {
    const v = app.extensionManager?.setting?.get(id) ?? app.ui?.settings?.getSettingValue(id);
    return v === undefined || v === null ? fallback : v;
  } catch (_) {
    return fallback;
  }
}

function groupOf(nodeData) {
  // category looks like "SY/Text"
  const cat = (nodeData && nodeData.category) || "";
  const parts = cat.split("/");
  return parts[0] === PREFIX && parts[1] ? parts[1] : "";
}

function paint(node, nodeData) {
  const mode = setting(SETTING_COLOR, "Group colours");
  if (mode === "Off" || !theme) return;
  const g = theme.groups[groupOf(nodeData)];
  if (!g) return;
  if (mode === "Gold only") {
    node.color = theme.tokens.gold_dim;
    node.bgcolor = theme.tokens.surface;
  } else {
    node.color = g.color;
    node.bgcolor = g.bgcolor;
  }
}

function paintNote(node) {
  const w = node.widgets && node.widgets.find((x) => x.name === "style");
  if (!w) return;
  const apply = () => {
    const st = theme?.note_styles?.[w.value];
    if (!st || setting(SETTING_COLOR, "Group colours") === "Off") return;
    node.color = st.color;
    node.bgcolor = st.bgcolor;
    node.setDirtyCanvas?.(true, true);
  };
  const cb = w.callback;
  w.callback = function () {
    if (cb) cb.apply(this, arguments);
    apply();
  };
  apply();
  const cfg = node.onConfigure;
  node.onConfigure = function () {
    if (cfg) cfg.apply(this, arguments);
    apply();
  };
}

function addMark(node) {
  const orig = node.onDrawForeground;
  node.onDrawForeground = function (ctx) {
    if (orig) orig.apply(this, arguments);
    if (!setting(SETTING_MARK, true) || this.flags?.collapsed) return;
    const h = (window.LiteGraph && LiteGraph.NODE_TITLE_HEIGHT) || 30;
    ctx.save();
    ctx.font = "bold 11px sans-serif";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.fillStyle = theme?.tokens?.gold || "#d4a537";
    ctx.fillText("SY", this.size[0] - 8, -h / 2);
    ctx.restore();
  };
}

// ---- side panel: every SY node, grouped, searchable, click to add --------------------------
function listSyNodes() {
  const out = [];
  const types = (window.LiteGraph && LiteGraph.registered_node_types) || {};
  for (const [type, ctor] of Object.entries(types)) {
    if (!type.startsWith(PREFIX)) continue;
    const d = ctor.nodeData;
    if (!d || groupOf(d) === "") continue;
    out.push({
      type,
      name: d.display_name || type,
      group: groupOf(d),
      help: d.description || "",
    });
  }
  return out.sort((a, b) => a.group.localeCompare(b.group) || a.name.localeCompare(b.name));
}

function addNodeToCanvas(type) {
  const node = LiteGraph.createNode(type);
  if (!node) return;
  const c = app.canvas;
  const [w, h] = [c.canvas.width, c.canvas.height];
  const scale = c.ds.scale || 1;
  node.pos = [(w / 2 - c.ds.offset[0] * scale) / scale - 80, (h / 2 - c.ds.offset[1] * scale) / scale - 40];
  app.graph.add(node);
  app.graph.setDirtyCanvas(true, true);
}

function renderPanel(el) {
  el.innerHTML = "";
  el.style.cssText = "padding:10px;font-family:'DM Sans',sans-serif;color:" + (theme?.tokens?.text || "#f2f3f5");
  const title = document.createElement("div");
  title.textContent = "SY Nodes";
  title.style.cssText = "font-weight:700;font-size:16px;margin-bottom:2px;color:" + (theme?.tokens?.gold || "#d4a537");
  const sub = document.createElement("div");
  sub.textContent = "Click a node to put it on the canvas. Hover a node for help.";
  sub.style.cssText = "font-size:12px;opacity:.75;margin-bottom:8px";
  const search = document.createElement("input");
  search.type = "search";
  search.placeholder = "Search SY nodes";
  search.style.cssText = "width:100%;box-sizing:border-box;margin-bottom:8px;padding:6px;border-radius:6px;border:1px solid " +
    (theme?.tokens?.gold_dim || "#8b6914") + ";background:" + (theme?.tokens?.abyss || "#1e1f22") + ";color:inherit";
  const list = document.createElement("div");
  el.append(title, sub, search, list);

  const all = listSyNodes();
  const draw = () => {
    const q = search.value.trim().toLowerCase();
    list.innerHTML = "";
    let last = "";
    for (const n of all) {
      if (q && !(n.name + " " + n.help + " " + n.group).toLowerCase().includes(q)) continue;
      if (n.group !== last) {
        last = n.group;
        const head = document.createElement("div");
        head.textContent = n.group;
        head.style.cssText = "margin:10px 0 4px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.7";
        list.append(head);
      }
      const row = document.createElement("button");
      row.type = "button";
      const g = theme?.groups?.[n.group];
      row.style.cssText = "display:block;width:100%;text-align:left;margin-bottom:4px;padding:6px 8px;border-radius:6px;cursor:pointer;" +
        "border:0;border-left:6px solid " + (g?.color || "#8b6914") + ";background:" + (theme?.tokens?.surface || "#2b2d31") + ";color:inherit";
      const nm = document.createElement("div");
      nm.textContent = n.name;
      nm.style.fontWeight = "600";
      const hp = document.createElement("div");
      hp.textContent = n.help;
      hp.style.cssText = "font-size:11px;opacity:.7;margin-top:2px";
      row.append(nm, hp);
      row.title = n.help;
      row.addEventListener("click", () => addNodeToCanvas(n.type));
      list.append(row);
    }
    if (!list.children.length) list.textContent = "No SY node matches.";
  };
  search.addEventListener("input", draw);
  draw();
}


// ---- help window (Alt+H): search every SY node, full help, add to canvas ---------------------
let helpEl = null;

function helpFor(type) {
  const ctor = LiteGraph.registered_node_types?.[type];
  const d = ctor?.nodeData;
  const rows = [];
  for (const kind of ["required", "optional"]) {
    for (const [name, spec] of Object.entries(d?.input?.[kind] || {})) {
      const opt = Array.isArray(spec) ? spec[1] || {} : {};
      rows.push({ name, kind, tip: opt.tooltip || "" });
    }
  }
  return { name: d?.display_name || type, desc: d?.description || "", rows };
}

function closeHelp() {
  if (helpEl) {
    helpEl.remove();
    helpEl = null;
  }
}

function openHelp(focusType) {
  if (helpEl && !focusType) return closeHelp();
  closeHelp();
  const t = theme?.tokens || {};
  helpEl = document.createElement("div");
  helpEl.id = "sy-help";
  helpEl.setAttribute("role", "dialog");
  helpEl.setAttribute("aria-label", "SY Nodes help");
  helpEl.style.cssText = "position:fixed;top:70px;right:20px;width:420px;max-height:75vh;overflow:auto;z-index:9999;" +
    "padding:12px;border-radius:10px;font-family:'DM Sans',sans-serif;box-shadow:0 8px 30px rgba(0,0,0,.5);" +
    "background:" + (t.void || "#1a1b1e") + ";color:" + (t.text || "#f2f3f5") + ";border:1px solid " + (t.gold_dim || "#8b6914");
  const bar = document.createElement("div");
  bar.style.cssText = "display:flex;justify-content:space-between;align-items:center;margin-bottom:8px";
  const h = document.createElement("b");
  h.textContent = "SY Nodes help";
  h.style.color = t.gold || "#d4a537";
  const x = document.createElement("button");
  x.textContent = "Close";
  x.setAttribute("aria-label", "Close help");
  x.style.cssText = "cursor:pointer;border-radius:6px;border:1px solid " + (t.gold_dim || "#8b6914") + ";background:transparent;color:inherit;padding:2px 8px";
  x.onclick = closeHelp;
  bar.append(h, x);
  const q = document.createElement("input");
  q.type = "search";
  q.placeholder = "Search (name, words, group)";
  q.style.cssText = "width:100%;box-sizing:border-box;margin-bottom:8px;padding:6px;border-radius:6px;border:1px solid " + (t.gold_dim || "#8b6914") + ";background:" + (t.abyss || "#1e1f22") + ";color:inherit";
  const body = document.createElement("div");
  helpEl.append(bar, q, body);
  document.body.append(helpEl);
  helpEl.addEventListener("keydown", (e) => { if (e.key === "Escape") closeHelp(); });

  const all = listSyNodes();
  const draw = () => {
    const needle = q.value.trim().toLowerCase();
    body.innerHTML = "";
    for (const n of all) {
      const info = helpFor(n.type);
      const hay = (info.name + " " + info.desc + " " + n.group + " " + info.rows.map((r) => r.name + " " + r.tip).join(" ")).toLowerCase();
      if (needle && !hay.includes(needle)) continue;
      const card = document.createElement("details");
      if (n.type === focusType || (needle && body.children.length < 2)) card.open = true;
      card.style.cssText = "margin-bottom:6px;padding:6px 8px;border-radius:6px;border-left:6px solid " + (theme?.groups?.[n.group]?.color || "#8b6914") + ";background:" + (t.surface || "#2b2d31");
      const sum = document.createElement("summary");
      sum.textContent = info.name + "  (" + n.group + ")";
      sum.style.cssText = "cursor:pointer;font-weight:600";
      const d = document.createElement("div");
      d.textContent = info.desc;
      d.style.cssText = "font-size:12px;opacity:.85;margin:6px 0";
      card.append(sum, d);
      for (const r of info.rows) {
        const li = document.createElement("div");
        li.style.cssText = "font-size:12px;margin-left:8px";
        li.textContent = r.name + (r.kind === "optional" ? " (optional)" : "") + (r.tip ? ": " + r.tip : "");
        card.append(li);
      }
      const add = document.createElement("button");
      add.textContent = "Add to canvas";
      add.style.cssText = "margin-top:6px;cursor:pointer;border-radius:6px;border:1px solid " + (t.gold_dim || "#8b6914") + ";background:transparent;color:" + (t.gold || "#d4a537") + ";padding:2px 8px";
      add.onclick = () => addNodeToCanvas(n.type);
      card.append(add);
      body.append(card);
    }
    if (!body.children.length) body.textContent = "No SY node matches.";
  };
  q.addEventListener("input", draw);
  draw();
  q.focus();
  if (focusType) helpEl.querySelector("details[open]")?.scrollIntoView?.({ block: "nearest" });
}

// ---- group switch: mute / bypass / enable every node inside a group -------------------------
function setGroupMode(group, mode) {
  try { group.recomputeInsideNodes?.(); } catch (_) { /* older frontends */ }
  let nodes = group._children ? [...group._children].filter((c) => c.mode !== undefined) : group._nodes || [];
  if (!nodes.length) {
    // fallback: every node whose box sits inside the group box (works when the frontend list is empty)
    const [gx, gy] = [group.pos[0], group.pos[1]];
    const [gw, gh] = [group.size[0], group.size[1]];
    nodes = (app.graph._nodes || []).filter((n) => n.pos[0] >= gx && n.pos[1] >= gy &&
      n.pos[0] + n.size[0] <= gx + gw && n.pos[1] + n.size[1] <= gy + gh);
  }
  for (const n of nodes) n.mode = mode;
  app.graph.setDirtyCanvas(true, true);
  return nodes.length;
}

function groupAt(canvas) {
  const pos = canvas?.graph_mouse;
  return pos ? app.graph.getGroupOnPos?.(pos[0], pos[1]) : null;
}

app.registerExtension({
  name: EXT,
  settings: [
    {
      id: SETTING_COLOR,
      name: "SY nodes: colour coding",
      type: "combo",
      options: ["Group colours", "Gold only", "Off"],
      defaultValue: "Group colours",
      tooltip: "Group colours: each SY group has its own title colour. Gold only: all SY nodes share one. Off: ComfyUI default.",
    },
    {
      id: SETTING_MARK,
      name: "SY nodes: show the SY mark in the title",
      type: "boolean",
      defaultValue: true,
      tooltip: "A small gold SY in the top right of every SY node, so you can see which nodes are ours.",
    },
  ],
  commands: [
    { id: "SY.ToggleHelp", icon: "pi pi-question-circle", label: "SY Nodes: open or close help", function: () => openHelp() },
  ],
  keybindings: [
    { commandId: "SY.ToggleHelp", combo: { key: "h", alt: true } },
  ],
  getNodeMenuItems(node) {
    if (!node?.type?.startsWith(PREFIX) || !LiteGraph.registered_node_types?.[node.type]?.nodeData) return [];
    return [null, { content: "SY help for this node", callback: () => openHelp(node.type) }];
  },
  getCanvasMenuItems(canvas) {
    const g = groupAt(canvas);
    if (!g) return [];
    return [
      null,
      { content: "SY: mute group", callback: () => setGroupMode(g, 2) },
      { content: "SY: bypass group", callback: () => setGroupMode(g, 4) },
      { content: "SY: enable group", callback: () => setGroupMode(g, 0) },
    ];
  },
  async setup() {
    await loadTheme();
    try {
      app.extensionManager?.registerSidebarTab?.({
        id: "sy-nodes",
        icon: "pi pi-th-large",
        title: "SY Nodes",
        tooltip: "All Stable Yogi nodes",
        type: "custom",
        render: (el) => renderPanel(el),
      });
    } catch (err) {
      console.warn("[SY] side panel not available in this ComfyUI version", err);
    }
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (!nodeData?.name?.startsWith(PREFIX) || groupOf(nodeData) === "") return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      if (created) created.apply(this, arguments);
      paint(this, nodeData);
      addMark(this);
      if (nodeData.name === "SYNote") paintNote(this);
    };
  },
});
