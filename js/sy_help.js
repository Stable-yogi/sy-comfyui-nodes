// SY Nodes by Stable Yogi: searchable help window for every SY node. Alt+H opens it; F1 on a selected SY node opens it on that node.
// All text is set with textContent. The list is built once from /object_info and rebuilt only if the node count changes.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme, setting } from "./sy_core.js";
import { tk, button, overlay } from "./sy_ui_kit.js";

const FONT = "'DM Sans', sans-serif";

// The virtual nodes have no server part, so their help lives here.
const VIRTUAL = [
  { key: "SYSetVar", name: "Set SY", group: "Utility", description: "Puts a value into a named wireless link. Read it anywhere in the workflow with a Get SY node.",
    inputs: [{ name: "value", type: "*", tip: "The value to store." }, { name: "name", type: "TEXT", tip: "The name of the link. Get SY nodes pick this name." }], outputs: [] },
  { key: "SYGetVar", name: "Get SY", group: "Utility", description: "Reads the value stored by the Set SY node with the same name, without drawing a long wire.",
    inputs: [{ name: "name", type: "COMBO", tip: "Pick the name of a Set SY node in this workflow." }], outputs: [{ name: "value", type: "*" }] },
  { key: "SYFastToggle", name: "Fast Toggle SY", group: "Utility", description: "A panel of big on/off switches for nodes or groups. Off means muted or bypassed, as you choose in the Mode box.",
    inputs: [{ name: "Mode", type: "COMBO", tip: "Mute stops the node. Bypass lets the picture pass through it." },
      { name: "+ Add selected nodes", type: "BUTTON", tip: "Adds the nodes selected on the canvas as rows." },
      { name: "+ Add group...", type: "BUTTON", tip: "Pick a group of this workflow to add as a row." },
      { name: "All on / All off / Reverse", type: "BUTTON", tip: "Switch every row at once, or flip each one." },
      { name: "Only one on", type: "CHECKBOX", tip: "Radio behaviour: turning one row on turns the others off." }], outputs: [] },
];

let entries = [];
let builtFor = -1;
let loading = null;

async function ensureIndex() {
  if (loading) return loading;
  loading = (async () => {
    try {
      const res = await api.fetchApi("/object_info");
      const info = await res.json();
      const keys = Object.keys(info).filter((k) => k.startsWith("SY"));
      if (keys.length === builtFor && entries.length) return;
      builtFor = keys.length;
      const list = keys.map((k) => fromInfo(k, info[k]));
      for (const v of VIRTUAL) if (!list.some((e) => e.key === v.key)) list.push(v);
      for (const e of list) e.search = [e.name, e.group, e.description, ...e.inputs.map((i) => i.name)].join(" ").toLowerCase();
      list.sort((a, b) => a.group.localeCompare(b.group) || a.name.localeCompare(b.name));
      entries = list;
    } catch (err) {
      console.warn("[SY] help index", err);
    } finally {
      loading = null;
    }
  })();
  return loading;
}

function typeText(spec) {
  const t = spec?.[0];
  if (Array.isArray(t)) return "COMBO (" + t.slice(0, 6).join(", ") + (t.length > 6 ? ", ..." : "") + ")";
  return String(t ?? "?");
}

function fromInfo(key, d) {
  const inputs = [];
  for (const part of ["required", "optional"]) {
    for (const [name, spec] of Object.entries(d.input?.[part] || {})) {
      inputs.push({ name, type: typeText(spec), tip: String(spec?.[1]?.tooltip || ""), optional: part === "optional" });
    }
  }
  const outs = (d.output || []).map((t, i) => ({ name: (d.output_name || [])[i] || "", type: Array.isArray(t) ? "COMBO" : String(t) }));
  const cat = String(d.category || "SY");
  return { key, name: d.display_name || key, group: cat.split("/")[1] || "SY", description: String(d.description || ""), inputs, outputs: outs };
}

export function filterEntries(list, query) {
  const words = String(query || "").toLowerCase().split(/\s+/).filter(Boolean);
  return list.filter((e) => words.every((w) => e.search.includes(w)));
}

let openWin = null;

async function openHelp(startKey) {
  try {
    if (openWin) {
      openWin.close();
      openWin = null;
    }
    await loadTheme();
    await ensureIndex();
    if (openWin) {
      openWin.close();
      openWin = null;
    }
    const ov = overlay("SY Help", 900);
    openWin = ov;
    const prevClose = ov.close;
    ov.close = () => {
      openWin = null;
      prevClose();
    };
    ov.box.style.width = "min(900px,94vw)";
    const search = document.createElement("input");
    search.type = "search";
    search.placeholder = "Search by name, what it does or an input name...";
    search.setAttribute("aria-label", "Search SY nodes");
    search.style.cssText = "width:100%;box-sizing:border-box;margin-bottom:8px;padding:6px 8px;border-radius:6px;border:1px solid " +
      tk("gold_dim") + ";background:" + tk("abyss") + ";color:" + tk("white") + ";font:14px " + FONT;
    const cols = document.createElement("div");
    cols.style.cssText = "display:flex;gap:12px;min-height:50vh";
    const left = document.createElement("div");
    left.style.cssText = "width:260px;flex:none;overflow:auto;max-height:60vh;display:flex;flex-direction:column;gap:2px";
    const right = document.createElement("div");
    right.style.cssText = "flex:1;min-width:0;overflow:auto;max-height:60vh";
    cols.append(left, right);
    ov.body.append(search, cols);

    let current = startKey || null;

    const showEntry = (e) => {
      right.textContent = "";
      if (!e) {
        const hint = document.createElement("div");
        hint.textContent = "Pick a node on the left.";
        hint.style.color = tk("text_2");
        right.append(hint);
        return;
      }
      const h = document.createElement("div");
      h.textContent = e.name;
      h.style.cssText = "font:700 18px " + FONT + ";color:" + tk("gold");
      const g = document.createElement("div");
      g.textContent = "Group: " + e.group;
      g.style.cssText = "font-size:12px;color:" + tk("text_2") + ";margin-bottom:6px";
      const desc = document.createElement("p");
      desc.textContent = e.description || "No description.";
      desc.style.margin = "0 0 10px";
      right.append(h, g, desc);
      const sect = (title, items, render) => {
        if (!items.length) return;
        const t = document.createElement("div");
        t.textContent = title;
        t.style.cssText = "font:700 11px " + FONT + ";letter-spacing:.06em;color:" + tk("gold") + ";margin:8px 0 4px";
        right.append(t);
        for (const it of items) right.append(render(it));
      };
      sect("INPUTS", e.inputs, (i) => {
        const d = document.createElement("div");
        d.style.cssText = "padding:3px 0;border-bottom:1px solid " + tk("surface_3");
        const n = document.createElement("b");
        n.textContent = i.name;
        const ty = document.createElement("span");
        ty.textContent = "  " + i.type + (i.optional ? "  (optional)" : "");
        ty.style.cssText = "font-size:12px;color:" + tk("text_2");
        const tip = document.createElement("div");
        tip.textContent = i.tip || "";
        tip.style.cssText = "font-size:13px;color:" + tk("text_2");
        d.append(n, ty);
        if (i.tip) d.append(tip);
        return d;
      });
      sect("OUTPUTS", e.outputs, (o) => {
        const d = document.createElement("div");
        d.textContent = (o.name ? o.name + "  " : "") + o.type;
        d.style.padding = "2px 0";
        return d;
      });
      const add = button("Add this node to the canvas", "gold");
      add.style.marginTop = "12px";
      add.onclick = () => addToCanvas(e);
      right.append(add);
    };

    const renderList = () => {
      left.textContent = "";
      const shown = filterEntries(entries, search.value);
      if (!shown.length) {
        const none = document.createElement("div");
        none.textContent = entries.length ? "Nothing matches." : "No SY nodes found. Is the pack loaded?";
        none.style.cssText = "color:" + tk("text_2") + ";padding:6px";
        left.append(none);
      }
      let lastGroup = "";
      for (const e of shown) {
        if (e.group !== lastGroup) {
          lastGroup = e.group;
          const gh = document.createElement("div");
          gh.textContent = e.group.toUpperCase();
          gh.style.cssText = "font:700 11px " + FONT + ";letter-spacing:.06em;color:" + tk("gold") + ";margin:8px 0 2px";
          left.append(gh);
        }
        const b = button(e.name, e.key === current ? "on" : "ghost");
        b.style.textAlign = "left";
        b.onclick = () => {
          current = e.key;
          renderList();
          showEntry(e);
        };
        left.append(b);
      }
    };
    search.addEventListener("input", renderList);
    renderList();
    showEntry(entries.find((e) => e.key === current) || null);
    search.focus();
    if (current) left.querySelector("button")?.scrollIntoView?.({ block: "nearest" });
  } catch (err) {
    console.warn("[SY] help window", err);
  }
}

function addToCanvas(e) {
  try {
    const LG = window.LiteGraph;
    const node = LG.createNode(e.key);
    if (!node) return;
    const c = app.canvas;
    const ds = c.ds;
    const x = -ds.offset[0] + c.canvas.width / ds.scale / 2;
    const y = -ds.offset[1] + c.canvas.height / ds.scale / 2;
    node.pos = [x - (node.size?.[0] || 200) / 2, y - (node.size?.[1] || 80) / 2];
    app.graph.add(node);
    c.setDirty(true, true);
  } catch (err) {
    console.warn("[SY] help: could not add the node", err);
  }
}

function typingInField(ev) {
  const t = ev.target;
  const tag = (t?.tagName || "").toLowerCase();
  return tag === "input" || tag === "textarea" || tag === "select" || t?.isContentEditable === true;
}

function selectedSyType() {
  const sel = Object.values(app.canvas?.selected_nodes || {});
  if (sel.length !== 1) return null;
  const t = sel[0]?.type || "";
  return t.startsWith("SY") ? t : null;
}

app.registerExtension({
  name: "sy.help",
  settings: [
    { id: "SY.HelpShortcut", name: "SY Help shortcut on/off (Alt+H and F1)", type: "boolean", defaultValue: true,
      tooltip: "Alt+H opens the S Y help window. F1 opens it on the selected S Y node." },
  ],
  getCanvasMenuItems() {
    return [null, { content: "SY Help (Alt+H)", callback: () => openHelp() }];
  },
  async setup() {
    window.addEventListener("keydown", (ev) => {
      try {
        if (!setting("SY.HelpShortcut", true)) return;
        if (ev.altKey && !ev.ctrlKey && !ev.metaKey && (ev.key === "h" || ev.key === "H")) {
          ev.preventDefault();
          openHelp();
        } else if (ev.key === "F1" && !typingInField(ev)) {
          const type = selectedSyType();
          if (type) {
            ev.preventDefault();
            openHelp(type);
          }
        }
      } catch (err) {
        console.warn("[SY] help key", err);
      }
    });
  },
});
