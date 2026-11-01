// SY Nodes by Stable Yogi: Review Pause SY. The window that opens when the workflow stops half-way.
// Pictures with tick boxes, an editable text, an optional mask painter, and Continue / Stop. Text is set with textContent only.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { tk, button, label } from "./sy_ui_kit.js";

const FONT = "'DM Sans', sans-serif";
const open = new Map(); // pause id -> { close }

function viewUrl(ref) {
  const q = new URLSearchParams({ filename: ref.filename, subfolder: ref.subfolder || "", type: ref.type || "temp" });
  return api.apiURL("/view?" + q.toString() + "&rand=" + Math.random());
}

function enlarge(src) {
  const back = document.createElement("div");
  back.style.cssText = "position:fixed;inset:0;z-index:10020;background:rgba(0,0,0,.8);display:flex;align-items:center;justify-content:center;cursor:zoom-out";
  const im = document.createElement("img");
  im.src = src;
  im.style.cssText = "max-width:94vw;max-height:94vh;border-radius:6px";
  back.append(im);
  back.addEventListener("click", () => back.remove());
  document.body.append(back);
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const im = new Image();
    im.onload = () => resolve(im);
    im.onerror = () => reject(new Error("picture did not load"));
    im.src = src;
  });
}

// The mask painter. Strokes live on a hidden canvas (white on clear). The visible canvas shows them tinted over the picture.
async function buildPainter(info, state) {
  const wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-direction:column;gap:6px";
  const pic = await loadImage(viewUrl(info.images[0]));
  const W = pic.naturalWidth;
  const H = pic.naturalHeight;
  const stage = document.createElement("div");
  stage.style.cssText = "position:relative;max-width:100%;line-height:0;touch-action:none";
  pic.style.cssText = "display:block;max-width:100%;height:auto;border-radius:6px";
  const mc = document.createElement("canvas");
  mc.width = W;
  mc.height = H;
  const mctx = mc.getContext("2d");
  const dc = document.createElement("canvas");
  dc.width = W;
  dc.height = H;
  dc.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%;opacity:.6;cursor:crosshair";
  const dctx = dc.getContext("2d");
  stage.append(pic, dc);

  const redraw = () => {
    dctx.globalCompositeOperation = "source-over";
    dctx.clearRect(0, 0, W, H);
    dctx.drawImage(mc, 0, 0);
    dctx.globalCompositeOperation = "source-in";
    dctx.fillStyle = tk("red_soft");
    dctx.fillRect(0, 0, W, H);
  };

  if (info.mask_preview) {
    try {
      const start = await loadImage(viewUrl(info.mask_preview));
      const tmp = document.createElement("canvas");
      tmp.width = W;
      tmp.height = H;
      const t = tmp.getContext("2d");
      t.drawImage(start, 0, 0, W, H);
      const data = t.getImageData(0, 0, W, H);
      for (let i = 0; i < data.data.length; i += 4) {
        const v = data.data[i];
        data.data[i] = data.data[i + 1] = data.data[i + 2] = 255;
        data.data[i + 3] = v;
      }
      mctx.putImageData(data, 0, 0);
    } catch (e) {
      /* the starting mask could not be shown: the painter starts empty */
    }
    redraw();
  }

  let brush = 24;
  let erase = false;
  let last = null;
  const pos = (e) => {
    const r = dc.getBoundingClientRect();
    return [((e.clientX - r.left) / r.width) * W, ((e.clientY - r.top) / r.height) * H];
  };
  const dab = (a, b) => {
    mctx.globalCompositeOperation = erase ? "destination-out" : "source-over";
    mctx.strokeStyle = tk("white");
    mctx.lineWidth = brush;
    mctx.lineCap = "round";
    mctx.lineJoin = "round";
    mctx.beginPath();
    mctx.moveTo(a[0], a[1]);
    mctx.lineTo(b[0], b[1]);
    mctx.stroke();
    state.touched = true;
    redraw();
  };
  dc.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    dc.setPointerCapture(e.pointerId);
    last = pos(e);
    dab(last, last);
  });
  dc.addEventListener("pointermove", (e) => {
    if (!last) return;
    const p = pos(e);
    dab(last, p);
    last = p;
  });
  const stop = () => {
    last = null;
  };
  dc.addEventListener("pointerup", stop);
  dc.addEventListener("pointercancel", stop);

  const bar = document.createElement("div");
  bar.style.cssText = "display:flex;flex-wrap:wrap;gap:6px;align-items:center";
  const drawBtn = button("Draw", "on", "Paint the area you want masked");
  const eraseBtn = button("Erase", "ghost", "Rub out part of the mask");
  const setMode = (er) => {
    erase = er;
    drawBtn.style.background = er ? tk("surface_3") : tk("gold");
    drawBtn.style.color = er ? tk("white") : tk("void");
    eraseBtn.style.background = er ? tk("gold") : tk("surface_3");
    eraseBtn.style.color = er ? tk("void") : tk("white");
  };
  drawBtn.onclick = () => setMode(false);
  eraseBtn.onclick = () => setMode(true);
  const clearBtn = button("Clear", "ghost", "Remove the whole mask");
  clearBtn.onclick = () => {
    mctx.globalCompositeOperation = "source-over";
    mctx.clearRect(0, 0, W, H);
    state.touched = true;
    redraw();
  };
  const invBtn = button("Invert", "ghost", "Swap masked and not masked");
  invBtn.onclick = () => {
    const d = mctx.getImageData(0, 0, W, H);
    for (let i = 0; i < d.data.length; i += 4) {
      d.data[i] = d.data[i + 1] = d.data[i + 2] = 255;
      d.data[i + 3] = 255 - d.data[i + 3];
    }
    mctx.putImageData(d, 0, 0);
    state.touched = true;
    redraw();
  };
  const size = document.createElement("input");
  size.type = "range";
  size.min = "2";
  size.max = String(Math.max(8, Math.round(Math.max(W, H) / 4)));
  size.value = String(brush);
  size.title = "Brush size";
  size.oninput = () => {
    brush = Number(size.value);
  };
  const sizeLabel = document.createElement("span");
  sizeLabel.textContent = "Brush size";
  sizeLabel.style.cssText = "font-size:12px;color:" + tk("text_2");
  bar.append(drawBtn, eraseBtn, clearBtn, invBtn, sizeLabel, size);

  state.exportMask = () => {
    const out = document.createElement("canvas");
    out.width = W;
    out.height = H;
    const o = out.getContext("2d");
    o.fillStyle = "black";
    o.fillRect(0, 0, W, H);
    o.drawImage(mc, 0, 0);
    return out.toDataURL("image/png").split(",")[1];
  };
  wrap.append(label("MASK (paint the area to change)"), bar, stage);
  return wrap;
}

async function openWindow(info) {
  if (!info || !info.id || open.has(info.id)) return;
  const state = { touched: false, exportMask: null };
  const picks = (info.images || []).map(() => true);

  const back = document.createElement("div");
  back.style.cssText = "position:fixed;inset:0;z-index:10010;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center";
  const box = document.createElement("div");
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-label", "Review Pause");
  box.style.cssText = "width:min(860px,94vw);max-height:90vh;overflow:auto;border-radius:10px;padding:16px;font:14px " + FONT +
    ";background:" + tk("void") + ";color:" + tk("white") + ";border:1px solid " + tk("gold_dim") +
    ";box-shadow:0 10px 40px rgba(0,0,0,.6);display:flex;flex-direction:column;gap:12px";
  box.addEventListener("keydown", (e) => e.stopPropagation());
  box.addEventListener("keyup", (e) => e.stopPropagation());

  const title = document.createElement("b");
  title.textContent = "Review Pause";
  title.style.cssText = "font-size:16px;color:" + tk("gold");
  const msg = document.createElement("div");
  msg.textContent = info.message || "Look at the result, then press Continue.";
  msg.style.cssText = "white-space:pre-wrap;color:" + tk("text");
  box.append(title, msg);

  if (info.images && info.images.length) {
    const head = label("PICTURES (tick the ones to keep; double-click to enlarge)");
    const grid = document.createElement("div");
    grid.style.cssText = "display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px";
    info.images.forEach((ref, i) => {
      const cell = document.createElement("div");
      cell.style.cssText = "position:relative;border-radius:6px;overflow:hidden;cursor:pointer;line-height:0;border:2px solid " + tk("gold");
      const im = document.createElement("img");
      im.src = viewUrl(ref);
      im.style.cssText = "width:100%;height:150px;object-fit:contain;background:" + tk("abyss");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = true;
      cb.title = "Keep picture " + (i + 1);
      cb.style.cssText = "position:absolute;left:6px;top:6px;width:20px;height:20px;cursor:pointer";
      const num = document.createElement("span");
      num.textContent = String(i + 1);
      num.style.cssText = "position:absolute;right:6px;top:6px;line-height:1;font:700 12px " + FONT + ";padding:3px 6px;border-radius:4px;background:" + tk("void") + ";color:" + tk("gold");
      const paint = () => {
        picks[i] = cb.checked;
        cell.style.borderColor = cb.checked ? tk("gold") : tk("surface_4");
        im.style.opacity = cb.checked ? "1" : "0.35";
      };
      cb.addEventListener("click", (e) => {
        e.stopPropagation();
        paint();
      });
      cell.addEventListener("click", () => {
        cb.checked = !cb.checked;
        paint();
      });
      cell.addEventListener("dblclick", () => enlarge(im.src));
      cell.append(im, cb, num);
      grid.append(cell);
    });
    box.append(head, grid);
  }

  let ta = null;
  if (info.has_text || (info.text || "") !== "") {
    ta = document.createElement("textarea");
    ta.value = info.text || "";
    ta.rows = 6;
    ta.style.cssText = "width:100%;box-sizing:border-box;resize:vertical;border-radius:6px;padding:8px;font:14px " + FONT +
      ";background:" + tk("surface") + ";color:" + tk("white") + ";border:1px solid " + tk("surface_4");
    box.append(label("TEXT (you may change it)"), ta);
  }

  if (info.draw && info.images && info.images.length) {
    try {
      box.append(await buildPainter(info, state));
    } catch (e) {
      const warn = document.createElement("div");
      warn.textContent = "The mask painter could not open, so the mask stays as it was.";
      warn.style.cssText = "color:" + tk("yellow");
      box.append(warn);
    }
  }

  const status = document.createElement("div");
  status.style.cssText = "min-height:18px;color:" + tk("yellow");
  const bar = document.createElement("div");
  bar.style.cssText = "display:flex;gap:10px;justify-content:flex-end";
  const stopBtn = button("Stop", "ghost", "End the run here");
  const goBtn = button("Continue", "gold", "Send your choices and carry on");
  for (const b of [stopBtn, goBtn]) b.style.padding = "8px 18px";
  bar.append(stopBtn, goBtn);
  box.append(status, bar);
  back.append(box);
  document.body.append(back);

  const close = () => {
    back.remove();
    open.delete(info.id);
  };
  open.set(info.id, { close });

  const send = async (action) => {
    stopBtn.disabled = goBtn.disabled = true;
    status.textContent = "";
    const body = { id: info.id, action, kept: [], text: ta ? ta.value : undefined };
    picks.forEach((on, i) => {
      if (on) body.kept.push(i);
    });
    if (state.touched && state.exportMask) body.mask_png_base64 = state.exportMask();
    try {
      const res = await api.fetchApi("/sy/pause/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) return close();
      let why = "";
      try {
        why = (await res.json()).error || "";
      } catch (e) {
        why = "";
      }
      status.textContent = why || "The answer was not accepted.";
      if (res.status === 404) {
        goBtn.textContent = "Close window";
        goBtn.disabled = false;
        goBtn.onclick = close;
        stopBtn.style.display = "none";
        return;
      }
    } catch (e) {
      status.textContent = "Could not reach ComfyUI. Check that it is still running, then try again.";
    }
    stopBtn.disabled = goBtn.disabled = false;
  };
  goBtn.onclick = () => send("continue");
  stopBtn.onclick = () => send("stop");
}

function closeAll() {
  for (const w of [...open.values()]) w.close();
}

// Esc must not close or stop anything while a window is open.
document.addEventListener(
  "keydown",
  (e) => {
    if (e.key === "Escape" && open.size) {
      e.preventDefault();
      e.stopPropagation();
    }
  },
  true,
);

app.registerExtension({
  name: "sy.review_pause",
  async setup() {
    try {
      api.addEventListener("sy.review.open", (ev) => {
        openWindow(ev.detail).catch((e) => console.warn("[SY] Review Pause window failed", e));
      });
      api.addEventListener("sy.review.close", (ev) => open.get(ev.detail?.id)?.close());
      for (const name of ["execution_interrupted", "execution_error"]) api.addEventListener(name, closeAll);
      const res = await api.fetchApi("/sy/pause/pending");
      if (res.ok) {
        const data = await res.json();
        for (const info of data.pending || []) await openWindow(info);
      }
    } catch (e) {
      console.warn("[SY] Review Pause could not start", e);
    }
  },
});
