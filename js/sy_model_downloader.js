// SY Nodes by Stable Yogi: Model Downloader SY. A list of models (folder, file, link) with a Download button per row.
// The list is kept in node.properties.sy_models (JSON text), so it travels inside the workflow file.
// Nothing here runs by itself: a download starts ONLY after the user presses a button AND confirms the size.
// Text is always set with textContent, colours come from tk() tokens only.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { tk, button, row as flexRow, overlay } from "./sy_ui_kit.js";

const PROP = "sy_models";
const FONT = "'DM Sans', sans-serif";

function readRows(node) {
  try {
    const v = JSON.parse(node.properties?.[PROP] || "[]");
    return Array.isArray(v) ? v.filter((r) => r && typeof r === "object") : [];
  } catch (e) {
    return [];
  }
}

function writeRows(node, rows) {
  node.properties = node.properties || {};
  node.properties[PROP] = JSON.stringify(rows);
}

function sizeText(n) {
  if (typeof n !== "number" || !(n >= 0)) return "unknown size";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  while (n >= 1024 && i < units.length - 1) {
    n /= 1024;
    i++;
  }
  return (i === 0 ? String(Math.round(n)) : n.toFixed(1)) + " " + units[i];
}

async function post(path, body) {
  const res = await api.fetchApi(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  let data = {};
  try {
    data = await res.json();
  } catch (e) {
    data = {};
  }
  if (!res.ok) throw new Error(data.error || "The request failed.");
  return data;
}

async function getJson(path) {
  const res = await api.fetchApi(path);
  let data = {};
  try {
    data = await res.json();
  } catch (e) {
    data = {};
  }
  if (!res.ok) throw new Error(data.error || "The request failed.");
  return data;
}

function note(text, color) {
  const d = document.createElement("div");
  d.textContent = text;
  d.style.cssText = "font-size:13px;line-height:1.45;margin:4px 0;color:" + (color || tk("white"));
  return d;
}

function listToText(rows) {
  return rows
    .map((r) => [r.folder, r.file, r.url, r.note || ""].join(" | ").replace(/( \| )+$/, ""))
    .join("\n");
}

// Parsing is checked again by the server before any download; this only gives quick, friendly feedback.
function parseText(text) {
  const rows = [];
  const problems = [];
  const seen = new Set();
  text.split(/\r?\n/).forEach((line, i) => {
    const s = line.trim();
    if (!s || s.startsWith("#")) return;
    const p = s.split("|").map((x) => x.trim());
    if (p.length < 3 || p.length > 5) {
      problems.push("Line " + (i + 1) + ": write it as  folder | file name | link | note (the note is optional).");
      return;
    }
    const r = { folder: p[0].toLowerCase(), file: p[1], url: p[2], note: p[3] || "" };
    if (p[4]) r.sha256 = p[4];
    const key = r.folder + "/" + r.file.toLowerCase();
    if (seen.has(key)) {
      problems.push("Line " + (i + 1) + ": " + r.file + " is in the list twice.");
      return;
    }
    seen.add(key);
    rows.push(r);
  });
  if (!rows.length && !problems.length) problems.push("The list is empty. Add at least one model.");
  return { rows, problems };
}

function chip(text, kind) {
  const c = document.createElement("span");
  c.textContent = text;
  const fill = { ok: tk("green_btn"), missing: tk("gold"), busy: tk("blue"), bad: tk("red_soft") }[kind] || tk("surface_3");
  const ink = kind === "missing" ? tk("void") : tk("white");
  c.style.cssText = "display:inline-block;padding:2px 8px;border-radius:10px;font:700 11px " + FONT + ";white-space:nowrap;background:" + fill + ";color:" + ink;
  return c;
}

function addDownloader(node) {
  node.properties = node.properties || {};
  if (typeof node.properties[PROP] !== "string") node.properties[PROP] = "[]";
  // file key -> {state: "installed" | "missing" | "downloading" | "error", pct, message, jobId}
  const status = {};
  const keyOf = (r) => String(r.folder).toLowerCase() + "/" + String(r.file).toLowerCase();
  let timer = null;

  const box = document.createElement("div");
  box.style.cssText = "display:flex;flex-direction:column;gap:6px;width:100%;box-sizing:border-box;padding:6px 4px;font:13px " + FONT + ";color:" + tk("white");
  const bar = flexRow();
  const downAll = button("Download all missing", "gold", "Downloads every missing model after you confirm the total size");
  const edit = button("Edit list", "ghost", "Type or paste the models: one per line");
  const again = button("Check again", "ghost", "Look in the models folders again");
  bar.append(downAll, edit, again);
  const msg = document.createElement("div");
  msg.style.cssText = "font-size:12px;color:" + tk("text_2");
  const list = document.createElement("div");
  list.style.cssText = "display:flex;flex-direction:column;gap:4px";
  box.append(bar, msg, list);

  const setMsg = (t) => {
    msg.textContent = t || "";
  };

  const render = () => {
    list.textContent = "";
    const rows = readRows(node);
    if (!rows.length) {
      list.append(note("No models in the list yet. Press Edit list and add one model per line: folder | file name | link.", tk("text_2")));
    }
    for (const r of rows) {
      const st = status[keyOf(r)] || { state: "unknown" };
      const line = document.createElement("div");
      line.style.cssText = "display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:4px 6px;border-radius:6px;background:" + tk("surface_2");
      const where = document.createElement("span");
      where.textContent = r.folder;
      where.style.cssText = "font:700 11px " + FONT + ";color:" + tk("gold") + ";min-width:90px";
      const name = document.createElement("span");
      name.textContent = r.file;
      name.title = r.note || r.url || "";
      name.style.cssText = "flex:1;min-width:140px;word-break:break-all";
      let chipEl;
      if (st.state === "installed") chipEl = chip("Installed", "ok");
      else if (st.state === "missing") chipEl = chip("Missing", "missing");
      else if (st.state === "downloading") chipEl = chip("Downloading " + (st.pct || 0) + "%", "busy");
      else if (st.state === "error") chipEl = chip("Problem", "bad");
      else chipEl = chip("Checking...", "busy");
      line.append(where, name, chipEl);
      if (st.state === "missing" || st.state === "error") {
        const dl = button("Download", "green", "Check the size and download this model");
        dl.onclick = () => confirmDownload([r]);
        line.append(dl);
      }
      if (st.state === "downloading") {
        const stop = button("Cancel", "ghost", "Stop this download and remove the unfinished file");
        stop.onclick = async () => {
          try {
            await post("/sy/download/cancel", { id: st.jobId });
          } catch (e) {
            setMsg(String(e.message || e));
          }
        };
        line.append(stop);
      }
      const open = button("Open in browser", "ghost", "Open the link in a new browser tab");
      open.onclick = () => window.open(r.url, "_blank", "noopener,noreferrer");
      line.append(open);
      if (st.message) {
        const m = document.createElement("div");
        m.textContent = st.message;
        m.style.cssText = "flex-basis:100%;font-size:12px;color:" + (st.state === "error" ? tk("red_soft") : tk("text_2"));
        line.append(m);
      }
      list.append(line);
    }
    node.setDirtyCanvas?.(true, true);
  };

  const checkAll = async () => {
    const rows = readRows(node);
    for (const r of rows) {
      const k = keyOf(r);
      if (status[k]?.state === "downloading") continue;
      try {
        const d = await getJson("/sy/download/check?folder=" + encodeURIComponent(r.folder) + "&file=" + encodeURIComponent(r.file));
        status[k] = { state: d.installed ? "installed" : "missing" };
      } catch (e) {
        status[k] = { state: "error", message: String(e.message || e) };
      }
      render();
    }
  };

  const poll = async () => {
    let busy = false;
    for (const r of readRows(node)) {
      const k = keyOf(r);
      const st = status[k];
      if (!st || st.state !== "downloading") continue;
      try {
        const d = await getJson("/sy/download/status?id=" + encodeURIComponent(st.jobId));
        if (d.state === "done") status[k] = { state: "installed", message: "Installed." };
        else if (d.state === "error" || d.state === "cancelled") status[k] = { state: d.state === "error" ? "error" : "missing", message: d.message };
        else {
          busy = true;
          st.pct = d.total ? Math.floor((100 * d.done) / d.total) : 0;
        }
      } catch (e) {
        status[k] = { state: "error", message: String(e.message || e) };
      }
    }
    render();
    if (!busy && timer) {
      clearInterval(timer);
      timer = null;
    }
  };

  const startPolling = () => {
    if (!timer) timer = setInterval(poll, 1000);
  };

  // The confirm window: file name, folder, size, free disk space, "this uses the internet". Nothing starts before "Yes, download".
  const confirmDownload = async (rows) => {
    const ov = overlay(rows.length > 1 ? "Download all missing models?" : "Download this model?", 560);
    ov.body.append(note("Checking the size and your free disk space..."));
    let plan;
    try {
      plan = await post("/sy/download/plan", { rows });
    } catch (e) {
      ov.body.textContent = "";
      ov.body.append(note(String(e.message || e), tk("red_soft")));
      return;
    }
    ov.body.textContent = "";
    const items = plan.rows || [];
    const good = [];
    for (const it of items) {
      const l = document.createElement("div");
      l.style.cssText = "padding:4px 0;border-bottom:1px solid " + tk("surface_3");
      const head = document.createElement("div");
      head.textContent = it.file || "(row " + (it.index + 1) + ")";
      head.style.cssText = "font-weight:700";
      const info = document.createElement("div");
      info.style.cssText = "font-size:12px;color:" + (it.ok ? tk("text_2") : tk("red_soft"));
      info.textContent = it.ok
        ? "Goes into the " + it.folder + " folder. Size: " + sizeText(it.size) + "."
        : it.error || "This one cannot be downloaded.";
      l.append(head, info);
      ov.body.append(l);
      if (it.ok) good.push(rows[it.index]);
    }
    ov.body.append(note("Total to download: " + sizeText(plan.total) + ". Free disk space: " + sizeText(plan.free) + " (1 GB is always kept spare)."));
    ov.body.append(note("This uses the internet. Only Hugging Face, Civitai and GitHub links are allowed.", tk("gold")));
    const act = flexRow();
    const no = button("No, cancel", "ghost");
    no.onclick = () => ov.close();
    act.append(no);
    if (good.length && plan.total_ok) {
      const yes = button("Yes, download", "gold");
      yes.onclick = async () => {
        ov.close();
        for (const r of good) {
          try {
            const d = await post("/sy/download/start", { row: r });
            status[keyOf(r)] = { state: "downloading", pct: 0, jobId: d.id };
          } catch (e) {
            status[keyOf(r)] = { state: "error", message: String(e.message || e) };
          }
        }
        render();
        startPolling();
      };
      act.append(yes);
    } else if (good.length) {
      ov.body.append(note("There is not enough free disk space for all of them together.", tk("red_soft")));
    }
    ov.body.append(act);
  };

  downAll.onclick = () => {
    const missing = readRows(node).filter((r) => status[keyOf(r)]?.state === "missing");
    if (!missing.length) {
      setMsg("Nothing is missing.");
      return;
    }
    setMsg("");
    confirmDownload(missing);
  };

  again.onclick = () => {
    setMsg("");
    checkAll();
  };

  edit.onclick = () => {
    const ov = overlay("Edit the model list", 720);
    ov.body.append(note("One model per line:  folder | file name | link | note (the note is optional). Lines starting with # are ignored."));
    ov.body.append(note("Folders: checkpoints, diffusion_models, unet, vae, loras, text_encoders, clip, clip_vision, controlnet, upscale_models, embeddings, vae_approx, style_models, gligen, diffusers, model_patches.", tk("text_2")));
    const ta = document.createElement("textarea");
    ta.value = listToText(readRows(node));
    ta.spellcheck = false;
    ta.style.cssText = "display:block;width:100%;box-sizing:border-box;min-height:220px;padding:6px;border-radius:6px;resize:vertical;border:1px solid " +
      tk("gold_dim") + ";background:" + tk("abyss") + ";color:" + tk("white") + ";font:12px monospace";
    const problems = document.createElement("div");
    problems.style.cssText = "font-size:12px;margin:6px 0;color:" + tk("red_soft") + ";white-space:pre-wrap";
    const save = button("Save list", "gold");
    save.onclick = () => {
      const r = parseText(ta.value);
      if (r.problems.length) {
        problems.textContent = "Not saved:\n" + r.problems.join("\n");
        return;
      }
      writeRows(node, r.rows);
      for (const k of Object.keys(status)) delete status[k];
      ov.close();
      render();
      checkAll();
    };
    ov.body.append(ta, problems, save);
  };

  const widget = node.addDOMWidget("sy_model_list", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 90 + 34 * Math.max(1, readRows(node).length)];
  node._syModelsRefresh = () => {
    render();
    checkAll();
  };
  node.setSize([Math.max(node.size[0], 560), Math.max(node.size[1], 220)]);
  render();
  checkAll();
  const removed = node.onRemoved;
  node.onRemoved = function () {
    if (timer) clearInterval(timer);
    return removed ? removed.apply(this, arguments) : undefined;
  };
}

app.registerExtension({
  name: "sy.model_downloader",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "SYModelDownloader") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        addDownloader(this);
      } catch (e) {
        console.warn("[SY] model downloader not shown", e);
      }
      return r;
    };
    // after a workflow loads, the saved list is in node.properties: show it again
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configured ? configured.apply(this, arguments) : undefined;
      if (this._syModelsRefresh) this._syModelsRefresh();
      return r;
    };
  },
});
