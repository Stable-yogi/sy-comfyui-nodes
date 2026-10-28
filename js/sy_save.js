// SY Nodes by Stable Yogi: the browser part of Save Image To Folder SY (and the folder buttons of Load Image From Folder SY).
// Token buttons, a live "Will save as" line, Open / Copy / Folder, a format switch, a Save / Preview switch, a picture grid.
// The node still works without this file. Folder access goes through /sy/folder/* and stays inside output and input.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { tk, button, setSwitch, row, label, pickFolder, hideWidget, setWidget, widgetValue, listFolder } from "./sy_ui_kit.js";

const TOKENS = [
  ["+ Date", "{date}"], ["+ Time", "{time}"], ["+ Seed", "{seed}"], ["+ Counter", "{counter}"],
  ["+ Width", "{width}"], ["+ Height", "{height}"], ["+ Batch", "{batch}"], ["+ Model", "{model}"], ["+ Input", "{input}"],
];
const DEFAULT_PATTERN = "image_{counter}";
const FORMATS = ["png", "jpg", "webp"];

function viewUrl(f) {
  return api.apiURL("/view?filename=" + encodeURIComponent(f.filename) + "&type=" + (f.type || "output") +
    "&subfolder=" + encodeURIComponent(f.subfolder || "") + "&rand=" + Math.random());
}

async function post(path, body) {
  const res = await api.fetchApi(path, { method: "POST", body: JSON.stringify(body) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "the request failed");
  return data;
}

function addSaveView(node) {
  const patW = node.widgets?.find((w) => w.name === "filename_pattern");
  if (!patW) return;
  const state = { last: [], root: "", plan: null, w: 0, h: 0 };

  // ---- the two combo boxes become switches, so hide them -------------------------------------------------
  hideWidget(node.widgets.find((w) => w.name === "format"));
  hideWidget(node.widgets.find((w) => w.name === "output_mode"));

  // ComfyUI adds its own big preview widget when pictures arrive; our grid already shows them, so make that widget empty
  const addCustom = node.addCustomWidget;
  node.addCustomWidget = function (w) {
    if (w && w.name === "$$canvas-image-preview") {
      w.computeSize = () => [0, -4];
      w.draw = () => {};
      w.hidden = true;
    }
    return addCustom.apply(this, arguments);
  };

  const box = document.createElement("div");
  box.style.cssText = "display:flex;flex-direction:column;gap:6px;width:100%;box-sizing:border-box;padding:2px 0;color:" + tk("white");

  // ---- file name tokens -----------------------------------------------------------------------------------
  const tokenRow = row();
  for (const [text, tok] of TOKENS) {
    const b = button(text, "ghost", "Add " + tok + " to the file name");
    b.onclick = () => {
      const cur = String(patW.value || "");
      if (tok === "{counter}" && cur.includes("{counter}")) return;
      const at = cur.indexOf("{counter}");
      if (tok !== "{counter}" && at >= 0) {
        // keep the counter last so numbers stay at the end of the name
        const head = cur.slice(0, at).replace(/_$/, "");
        setWidget(node, "filename_pattern", (head ? head + "_" : "") + tok + "_" + cur.slice(at));
      } else {
        setWidget(node, "filename_pattern", cur + (cur && !cur.endsWith("_") ? "_" : "") + tok);
      }
    };
    tokenRow.append(b);
  }
  const clear = button("Clear", "ghost", "Empty the file name");
  clear.onclick = () => setWidget(node, "filename_pattern", "");
  const reset = button("Reset", "ghost", "Back to " + DEFAULT_PATTERN);
  reset.onclick = () => setWidget(node, "filename_pattern", DEFAULT_PATTERN);
  tokenRow.append(clear, reset);

  // ---- the path the next save will use ------------------------------------------------------------------
  const will = document.createElement("div");
  will.style.cssText = "font:12px 'DM Sans',sans-serif;color:" + tk("gold_light") + ";word-break:break-all";

  // ---- Open / Copy / Folder, folder picker, date folder ---------------------------------------------------
  const note = document.createElement("div");
  note.style.cssText = "font:11px 'DM Sans',sans-serif;color:" + tk("text_2") + ";min-height:14px";
  const say = (t) => { note.textContent = t; };
  const openB = button("Open", "gold", "Open the last saved picture");
  const copyB = button("Copy", "gold", "Copy the full path of the last saved picture");
  const folderB = button("Folder", "gold", "Open the save folder in Explorer");
  const browseB = button("Browse folders", "ghost", "Choose the save folder from the folders that exist");
  const dateB = button("Date folder", "ghost", "Put pictures in a folder named with today's date");
  const fullPath = () => {
    const f = state.last[0];
    if (f && f.type === "output") return joinPath(state.root, f.subfolder, f.filename);
    return state.plan ? state.plan.full : "";
  };
  openB.onclick = async () => {
    const f = state.last[0];
    try {
      if (f && f.type === "output") await post("/sy/folder/open", { root: "output", sub: f.subfolder, filename: f.filename });
      else await post("/sy/folder/open", { root: "output", sub: currentSub() });
      say("Opened.");
    } catch (e) { say(String(e.message || e)); }
  };
  copyB.onclick = async () => {
    const p = fullPath();
    if (!p) return say("Nothing to copy yet.");
    try {
      await navigator.clipboard.writeText(p);
      say("Path copied.");
    } catch (_) {
      // older rule: a hidden text box and the copy command
      const t = document.createElement("textarea");
      t.value = p;
      t.style.cssText = "position:fixed;opacity:0";
      document.body.append(t);
      t.select();
      let ok = false;
      try { ok = document.execCommand("copy"); } catch (_e) { ok = false; }
      t.remove();
      say(ok ? "Path copied." : "The browser blocked copying.");
    }
  };
  folderB.onclick = async () => {
    try { await post("/sy/folder/open", { root: "output", sub: currentSub() }); say("Folder opened."); } catch (e) { say(String(e.message || e)); }
  };
  browseB.onclick = () => pickFolder("output", String(widgetValue(node, "subfolder", "")), (sub) => setWidget(node, "subfolder", sub));
  const syncDate = () => setSwitch(dateB, !!widgetValue(node, "date_folder", false));
  dateB.onclick = () => { setWidget(node, "date_folder", !widgetValue(node, "date_folder", false)); syncDate(); };

  // ---- format and Save / Preview switches ------------------------------------------------------------------
  const fmtBtns = FORMATS.map((f) => {
    const b = button(f === "jpg" ? "JPG" : f.toUpperCase(), "ghost", "Save as " + f);
    b.onclick = () => { setWidget(node, "format", f); syncSwitches(); };
    return [f, b];
  });
  const modeBtns = [["save", "Save", "Write the pictures to the output folder"], ["preview", "Preview", "Only show the pictures. No copy is kept in the output folder."]]
    .map(([m, text, tip]) => {
      const b = button(text, "ghost", tip);
      b.onclick = () => { setWidget(node, "output_mode", m); syncSwitches(); };
      return [m, b];
    });
  const syncSwitches = () => {
    const f = widgetValue(node, "format", "png");
    const m = widgetValue(node, "output_mode", "save");
    for (const [k, b] of fmtBtns) setSwitch(b, k === f);
    for (const [k, b] of modeBtns) setSwitch(b, k === m);
    syncDate();
    refresh();
  };

  // ---- pictures ------------------------------------------------------------------------------------------
  const grid = document.createElement("div");
  grid.style.cssText = "display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:6px;max-height:420px;overflow:auto";
  const foot = document.createElement("div");
  foot.style.cssText = "font:600 12px 'DM Sans',sans-serif;color:" + tk("gold");
  foot.textContent = "Run the workflow to see the pictures here.";

  box.append(label("FILE NAME"), tokenRow, will, row(openB, copyB, folderB, browseB, dateB),
    row(...fmtBtns.map((x) => x[1]), ...modeBtns.map((x) => x[1])), note, grid, foot);
  const widget = node.addDOMWidget("sy_save_view", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 360];

  // ---- live "Will save as" ---------------------------------------------------------------------------------
  function currentSub() {
    const s = String(widgetValue(node, "subfolder", "")).trim();
    if (!widgetValue(node, "date_folder", false)) return s;
    const d = new Date();
    const day = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    return s ? s + "/" + day : day;
  }
  let timer = 0;
  function refresh() {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      const preview = widgetValue(node, "output_mode", "save") === "preview";
      if (preview) {
        will.textContent = "Preview only: nothing is kept in the output folder.";
        return;
      }
      const q = new URLSearchParams({
        sub: String(widgetValue(node, "subfolder", "")), pattern: String(patW.value || ""), format: String(widgetValue(node, "format", "png")),
        seed: String(widgetValue(node, "seed", 0)), width: String(state.w), height: String(state.h),
        model: String(widgetValue(node, "model_name", "")), input: String(widgetValue(node, "input_name", "")),
        date_folder: widgetValue(node, "date_folder", false) ? "1" : "0",
      });
      try {
        const res = await api.fetchApi("/sy/folder/plan?" + q.toString());
        const d = await res.json();
        if (!res.ok) throw new Error(d.error || "bad name");
        state.plan = d;
        state.root = d.root_path;
        will.style.color = tk("gold_light");
        will.textContent = "Will save as: " + d.full;
      } catch (e) {
        will.style.color = tk("red_soft");
        will.textContent = "Check the name: " + String(e.message || e);
      }
    }, 250);
  }
  for (const name of ["subfolder", "filename_pattern", "seed", "model_name", "input_name", "date_folder"]) {
    const w = node.widgets.find((x) => x.name === name);
    if (!w) continue;
    const orig = w.callback;
    w.callback = function () { const r = orig ? orig.apply(this, arguments) : undefined; refresh(); return r; };
  }

  // ---- after a run -----------------------------------------------------------------------------------------
  node._sySavedShow = (msg) => {
    const files = msg?.sy_saved || [];
    state.last = files;
    if (files.length) { state.w = files[0].width || 0; state.h = files[0].height || 0; }
    grid.textContent = "";
    files.forEach((f, i) => {
      const cell = document.createElement("a");
      cell.href = viewUrl(f);
      cell.target = "_blank";
      cell.rel = "noopener";
      cell.title = f.filename;
      cell.style.cssText = "position:relative;display:block;border-radius:6px;overflow:hidden;background:" + tk("surface_3");
      const img = document.createElement("img");
      img.src = viewUrl(f);
      img.alt = f.filename;
      img.style.cssText = "display:block;width:100%;aspect-ratio:1/1;object-fit:cover";
      const tag = document.createElement("span");
      tag.textContent = (i + 1) + "/" + files.length;
      tag.style.cssText = "position:absolute;right:4px;bottom:4px;padding:1px 6px;border-radius:4px;font:700 11px 'DM Sans',sans-serif;background:" + tk("gold") + ";color:" + tk("void");
      cell.append(img, tag);
      grid.append(cell);
    });
    foot.textContent = (msg?.sy_summary && msg.sy_summary[0]) || "";
    refresh();
  };
  node.setSize([Math.max(node.size[0], 520), Math.max(node.size[1], 640)]);
  setTimeout(syncSwitches, 200);
}

// ---- Load Image From Folder: Browse button and "picture n of m" ---------------------------------------------
function addLoadFolderView(node) {
  const subW = node.widgets?.find((w) => w.name === "subfolder");
  if (!subW) return;
  const info = document.createElement("div");
  info.style.cssText = "font:600 12px 'DM Sans',sans-serif;color:" + tk("gold");
  const browse = button("Browse folders", "gold", "Choose a folder inside the ComfyUI input folder");
  browse.onclick = () => pickFolder("input", String(subW.value || ""), (sub) => setWidget(node, "subfolder", sub));
  const box = row(browse, info);
  box.style.width = "100%";
  let timer = 0;
  const refresh = () => {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      try {
        const d = await listFolder("input", String(subW.value || ""));
        const idx = Number(widgetValue(node, "index", 0)) || 0;
        info.textContent = d.exists ? (d.images ? "Picks picture " + ((idx % d.images) + 1) + " of " + d.images : "No pictures in this folder.") : "This folder does not exist.";
      } catch (e) { info.textContent = String(e.message || e); }
    }, 250);
  };
  for (const name of ["subfolder", "index"]) {
    const w = node.widgets.find((x) => x.name === name);
    if (!w) continue;
    const orig = w.callback;
    w.callback = function () { const r = orig ? orig.apply(this, arguments) : undefined; refresh(); return r; };
  }
  const widget = node.addDOMWidget("sy_loadfolder_view", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 36];
  setTimeout(refresh, 300);
}

function joinPath(root, sub, name) {
  const sep = root.includes("\\") ? "\\" : "/";
  return [root, ...(sub ? sub.split("/") : []), name].join(sep);
}

app.registerExtension({
  name: "sy.save",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const name = nodeData.name;
    if (name !== "SYSaveImageToFolder" && name !== "SYLoadImageFromFolder") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        if (name === "SYSaveImageToFolder") addSaveView(this);
        else addLoadFolderView(this);
      } catch (e) {
        console.warn("[SY] folder buttons not shown", e);
      }
      return r;
    };
    if (name === "SYSaveImageToFolder") {
      const executed = nodeType.prototype.onExecuted;
      nodeType.prototype.onExecuted = function (msg) {
        if (executed) executed.apply(this, arguments);
        if (this._sySavedShow) this._sySavedShow(msg);
        // ComfyUI adds its own big preview under the node; our grid already shows the pictures, so hide it
        const hide = () => {
          const w = this.widgets?.find((x) => x.name === "$$canvas-image-preview");
          if (w) hideWidget(w);
          this.imgs = [];
          this.setDirtyCanvas?.(true, true);
        };
        hide();
        setTimeout(hide, 150);
        setTimeout(hide, 800);
      };
    }
  },
});
