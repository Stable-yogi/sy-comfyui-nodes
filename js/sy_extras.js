// SY Nodes by Stable Yogi: colour palette (with undo), first-run tour, live System Info bars, browser self check.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme, getTheme, pal, store, save, listSyNodeTypes, reducedMotion } from "./sy_core.js";

const selfcheck = new URLSearchParams(location.search).has("sy_selfcheck");

// ---- colour palette -----------------------------------------------------------------------
let palEl = null;

function closePalette() {
  palEl?.remove();
  palEl = null;
}

function targets(node) {
  const sel = app.canvas?.selected_nodes ? Object.values(app.canvas.selected_nodes) : [];
  return sel.length ? sel : [node];
}

function applyColors(nodes, color, bgcolor) {
  app.graph.beforeChange?.(); // one undo step for the whole change (Ctrl+Z works)
  for (const n of nodes) {
    if (color === null) {
      delete n.color;
      delete n.bgcolor;
    } else {
      n.color = color;
      n.bgcolor = bgcolor;
    }
  }
  app.graph.afterChange?.();
  app.graph.setDirtyCanvas(true, true);
}

function openPalette(node) {
  closePalette();
  const P = pal();
  const th = getTheme();
  palEl = document.createElement("div");
  palEl.setAttribute("role", "dialog");
  palEl.setAttribute("aria-label", "SY colours");
  palEl.style.cssText = "position:fixed;top:120px;left:50%;transform:translateX(-50%);z-index:9999;width:300px;padding:12px;border-radius:10px;" +
    "font-family:'DM Sans',sans-serif;box-shadow:0 8px 30px rgba(0,0,0,.5);background:" + P.void + ";color:" + P.text + ";border:1px solid " + P.gold_dim;
  const nodes = targets(node);
  const head = document.createElement("b");
  head.textContent = "SY colours (" + nodes.length + (nodes.length === 1 ? " node)" : " nodes)");
  head.style.color = P.gold;
  palEl.append(head);

  const sw = (label, color, bg) => {
    const b = document.createElement("button");
    b.type = "button";
    b.title = label;
    b.setAttribute("aria-label", label);
    b.style.cssText = "width:34px;height:34px;margin:3px;border-radius:6px;cursor:pointer;border:2px solid " + P.gold_dim + ";background:linear-gradient(135deg," + color + " 50%," + bg + " 50%)";
    b.onclick = () => applyColors(nodes, color, bg);
    return b;
  };
  const section = (title) => {
    const d = document.createElement("div");
    d.textContent = title;
    d.style.cssText = "margin-top:10px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.7";
    palEl.append(d);
    const row = document.createElement("div");
    palEl.append(row);
    return row;
  };
  const groups = section("Group colours");
  for (const [name, g] of Object.entries(th.groups || {})) groups.append(sw(name, g.color, g.bgcolor));
  const notes = section("Note styles");
  for (const [name, g] of Object.entries(th.note_styles || {})) notes.append(sw(name, g.color, g.bgcolor));
  const favRow = section("Favourites");
  const favs = store("fav_colours", []);
  const drawFavs = () => {
    favRow.innerHTML = "";
    for (const f of favs) favRow.append(sw("favourite " + f.color, f.color, f.bgcolor));
    if (!favs.length) favRow.textContent = "None yet. Pick a colour below and press Save as favourite.";
  };
  drawFavs();
  const custom = section("Your own colour");
  const pick = document.createElement("input");
  pick.type = "color";
  pick.value = th.tokens?.gold || "#d4a537";
  pick.setAttribute("aria-label", "Custom title colour");
  const mkBg = (hex) => {
    const n = parseInt(hex.slice(1), 16);
    const mix = (c) => Math.round(c * 0.2 + 0x24 * 0.8);
    return "#" + [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((c) => mix(c).toString(16).padStart(2, "0")).join("");
  };
  pick.oninput = () => applyColors(nodes, pick.value, mkBg(pick.value));
  const fav = document.createElement("button");
  fav.textContent = "Save as favourite";
  fav.onclick = () => {
    if (favs.length >= 15) favs.shift();
    favs.push({ color: pick.value, bgcolor: mkBg(pick.value) });
    save("fav_colours", favs);
    drawFavs();
  };
  custom.append(pick, fav);

  const foot = document.createElement("div");
  foot.style.cssText = "margin-top:12px;display:flex;gap:8px";
  const reset = document.createElement("button");
  reset.textContent = "Reset colour";
  reset.onclick = () => applyColors(nodes, null);
  const close = document.createElement("button");
  close.textContent = "Close";
  close.onclick = closePalette;
  for (const b of [fav, reset, close]) b.style.cssText = "cursor:pointer;border-radius:6px;border:1px solid " + P.gold_dim + ";background:transparent;color:inherit;padding:3px 8px";
  foot.append(reset, close);
  palEl.append(foot);
  palEl.addEventListener("keydown", (e) => { if (e.key === "Escape") closePalette(); });
  document.body.append(palEl);
  close.focus();
}

// ---- first-run tour -------------------------------------------------------------------------
const TOUR = [
  ["Welcome to SY Nodes", "These nodes are made by Stable Yogi. Each group has its own colour, so you can tell them apart at a glance."],
  ["Find a node", "Open the SY Nodes tab on the left side. Search, then click a node to add it."],
  ["Get help", "Press Alt+H any time. Or right-click a node and choose SY help for this node."],
  ["Change colours", "Right-click a node and choose SY colours. Ctrl+Z undoes it. Right-click a group to mute or bypass everything in it."],
];
let tourEl = null;

function endTour(markDone) {
  tourEl?.remove();
  tourEl = null;
  if (markDone) save("tour_done", true);
}

function showTour(step = 0) {
  endTour(false);
  const P = pal();
  tourEl = document.createElement("div");
  tourEl.setAttribute("role", "dialog");
  tourEl.setAttribute("aria-label", "SY Nodes tour");
  tourEl.style.cssText = "position:fixed;bottom:24px;left:24px;width:320px;z-index:9999;padding:14px;border-radius:10px;font-family:'DM Sans',sans-serif;" +
    "box-shadow:0 8px 30px rgba(0,0,0,.5);background:" + P.void + ";color:" + P.text + ";border:1px solid " + P.gold;
  const h = document.createElement("b");
  h.textContent = TOUR[step][0] + "  (" + (step + 1) + "/" + TOUR.length + ")";
  h.style.color = P.gold;
  const p = document.createElement("p");
  p.textContent = TOUR[step][1];
  p.style.cssText = "margin:8px 0;font-size:13px;line-height:1.4";
  const row = document.createElement("div");
  row.style.cssText = "display:flex;gap:8px;justify-content:flex-end";
  const mk = (txt, fn) => {
    const b = document.createElement("button");
    b.textContent = txt;
    b.style.cssText = "cursor:pointer;border-radius:6px;border:1px solid " + P.gold_dim + ";background:transparent;color:inherit;padding:3px 10px";
    b.onclick = fn;
    return b;
  };
  const last = step === TOUR.length - 1;
  const skip = mk("Skip", () => endTour(true));
  const next = mk(last ? "Done" : "Next", () => (last ? endTour(true) : showTour(step + 1)));
  row.append(skip, next);
  tourEl.append(h, p, row);
  tourEl.addEventListener("keydown", (e) => {
    if (e.key === "Escape") endTour(true);
    if (e.key === "Enter") next.click();
  });
  document.body.append(tourEl);
  next.focus();
}

// ---- System Info bars (live, drawn only while the node is on the canvas) ---------------------
function barLevel(pct) {
  return pct >= 95 ? "HIGH" : pct >= 85 ? "WARN" : "ok";
}

function addMonitor(node) {
  const P = pal();
  const box = document.createElement("div");
  box.style.cssText = "font:12px 'DM Sans',sans-serif;color:" + P.text + ";padding:4px";
  const rows = {};
  for (const key of ["VRAM", "RAM"]) {
    const line = document.createElement("div");
    line.style.cssText = "margin:4px 0";
    const label = document.createElement("div");
    const bar = document.createElement("div");
    bar.style.cssText = "height:8px;border-radius:4px;background:" + P.surface + ";overflow:hidden";
    const fill = document.createElement("div");
    fill.style.cssText = "height:100%;width:0%;" + (reducedMotion() ? "" : "transition:width .3s");
    bar.append(fill);
    line.append(label, bar);
    box.append(line);
    rows[key] = { label, fill };
  }
  const btn = document.createElement("button");
  btn.textContent = "Free memory now";
  btn.title = "Ask ComfyUI to unload models and free memory.";
  btn.style.cssText = "margin-top:6px;cursor:pointer;border-radius:6px;border:1px solid " + P.gold_dim + ";background:transparent;color:inherit;padding:3px 8px";
  btn.onclick = async () => {
    try {
      await api.fetchApi("/free", { method: "POST", body: JSON.stringify({ unload_models: true, free_memory: true }) });
    } catch (e) {
      console.warn("[SY] free memory request failed", e);
    }
  };
  box.append(btn);
  const widget = node.addDOMWidget("sy_monitor", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 100];
  const show = (key, used, total) => {
    const pct = total > 0 ? Math.round((used / total) * 100) : 0;
    const mb = (b) => Math.round(b / 1048576);
    rows[key].label.textContent = key + ": " + mb(used) + " / " + mb(total) + " MB (" + pct + "%) " + barLevel(pct);
    rows[key].fill.style.width = pct + "%";
    rows[key].fill.style.background = pct >= 95 ? "#ed4245" : pct >= 85 ? "#fee75c" : "#d4a537";
  };
  let alive = true;
  let seen = false;
  const tick = async () => {
    if (!alive) return;
    if (node.graph) seen = true;
    else if (seen) { alive = false; return; }
    if (!document.hidden) {
      try {
        const s = await (await api.fetchApi("/system_stats")).json();
        const dev = s.devices?.[0];
        if (dev) show("VRAM", dev.vram_total - dev.vram_free, dev.vram_total);
        show("RAM", s.system.ram_total - s.system.ram_free, s.system.ram_total);
      } catch (_) {
        rows.VRAM.label.textContent = "No reading right now.";
      }
    }
    setTimeout(tick, 2500);
  };
  const removed = node.onRemoved;
  node.onRemoved = function () {
    alive = false;
    if (removed) removed.apply(this, arguments);
  };
  setTimeout(tick, 400);
}

// ---- browser self check (headless run by the SY Watch) ---------------------------------------
async function runSelfCheck() {
  const out = { ok: true, failures: [], nodes: 0 };
  const fail = (m) => { out.ok = false; out.failures.push(m); };
  const types = listSyNodeTypes();
  out.nodes = types.length;
  if (types.length < 11) fail("only " + types.length + " SY nodes registered");
  for (const { type, data } of types) {
    try {
      const n = LiteGraph.createNode(type);
      if (!n) { fail("cannot create " + type); continue; }
      app.graph.add(n);
      if (!n.color && !type.includes("Note")) fail("no colour on " + type);
      for (const kind of ["required", "optional"]) {
        for (const [name, spec] of Object.entries(data.input?.[kind] || {})) {
          if (Array.isArray(spec) && !(spec[1] && spec[1].tooltip)) fail("no tooltip " + type + "." + name);
        }
      }
    } catch (e) {
      fail(type + ": " + e);
    }
  }
  if (!app.extensions.find((e) => e.name === "sy.ui")) fail("sy.ui extension missing");
  if (!app.extensionManager?.command) fail("no command api");
  const el = document.createElement("pre");
  el.id = "sy-selfcheck";
  el.textContent = "SYSELFCHECK " + JSON.stringify(out);
  document.body.append(el);
  document.title = "SYSELFCHECK " + (out.ok ? "PASS" : "FAIL");
}

app.registerExtension({
  name: "sy.extras",
  commands: [
    { id: "SY.Tour", label: "SY Nodes: show the tour", function: () => showTour(0) },
    { id: "SY.Colours", label: "SY Nodes: colours for the selected nodes", function: () => openPalette(Object.values(app.canvas?.selected_nodes || {})[0]) },
  ],
  getNodeMenuItems(node) {
    if (!node?.type?.startsWith("SY")) return [];
    return [{ content: "SY colours", callback: () => openPalette(node) }];
  },
  async nodeCreated(node) {
    if ((node.comfyClass || node.type) === "SYSystemInfo") {
      try { addMonitor(node); } catch (e) { console.warn("[SY] monitor not shown", e); }
    }
  },
  async setup() {
    await loadTheme();
    if (selfcheck) {
      setTimeout(runSelfCheck, 4000);
      return;
    }
    if (!store("tour_done", false)) setTimeout(() => showTour(0), 2500);
  },
});
