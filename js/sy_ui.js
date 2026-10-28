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
    };
  },
});
