// SY Nodes by Stable Yogi: browser part for Paint Mask SY (a brush editor on the node).
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { pal } from "./sy_core.js";

const MAX_SIDE = 1024; // the mask canvas never grows past this on its long side
const MAX_CHARS = 1500000; // about 1.5 MB of text in the workflow
const MAX_UNDO = 12;

function viewUrl(f) {
  return api.apiURL("/view?filename=" + encodeURIComponent(f.filename) + "&type=" + (f.type || "input") +
    "&subfolder=" + encodeURIComponent(f.subfolder || "") + "&rand=" + Math.random());
}

function fitSize(w, h) {
  const k = Math.min(1, MAX_SIDE / Math.max(w, h));
  return [Math.max(1, Math.round(w * k)), Math.max(1, Math.round(h * k))];
}

function addPaintEditor(node) {
  const dataWidget = node.widgets?.find((w) => w.name === "mask_data");
  if (!dataWidget) return;
  const P = pal();

  // hide the text widget but keep it in the saved workflow
  dataWidget.hidden = true;
  dataWidget.computeSize = () => [0, -4];
  if (dataWidget.element) dataWidget.element.style.display = "none";

  // mask canvas: painted = opaque white, unpainted = transparent. It is the real data.
  const mask = document.createElement("canvas");
  mask.width = 512;
  mask.height = 512;
  const mctx = mask.getContext("2d", { willReadFrequently: true });
  const tint = document.createElement("canvas");
  const tctx = tint.getContext("2d");

  const box = document.createElement("div");
  box.style.cssText = "display:flex;flex-direction:column;gap:4px;width:100%;height:100%;font:12px 'DM Sans',sans-serif;color:" + P.text;

  const stage = document.createElement("div");
  stage.style.cssText = "position:relative;flex:1;min-height:120px;border-radius:6px;overflow:hidden;background:" + P.surface;
  const back = document.createElement("img");
  back.alt = "";
  back.style.cssText = "position:absolute;inset:0;width:100%;height:100%;object-fit:contain;pointer-events:none";
  const view = document.createElement("canvas");
  view.setAttribute("aria-label", "Mask painting area. Drag to paint.");
  view.style.cssText = "position:absolute;inset:0;width:100%;height:100%;object-fit:contain;touch-action:none;cursor:none";
  const ring = document.createElement("div");
  ring.style.cssText = "position:absolute;border-radius:50%;pointer-events:none;display:none;box-sizing:border-box;border:1px solid " + P.gold;
  stage.append(back, view, ring);

  const mk = (text, tip) => {
    const b = document.createElement("button");
    b.textContent = text;
    b.title = tip;
    b.style.cssText = "flex:1;cursor:pointer;border-radius:6px;border:1px solid " + P.gold_dim + ";background:transparent;color:inherit;padding:2px 4px;font:12px 'DM Sans',sans-serif";
    return b;
  };
  const toolRow = document.createElement("div");
  toolRow.style.cssText = "display:flex;gap:4px";
  const bBrush = mk("Brush", "Paint the mask.");
  const bErase = mk("Eraser", "Rub the mask away.");
  const bUndo = mk("Undo", "Go back one step.");
  const bClear = mk("Clear", "Remove the whole mask.");
  const bInvert = mk("Invert", "Swap painted and unpainted areas.");
  const bBack = mk("Backdrop", "Look for the picture that feeds this node and show it behind the mask.");
  toolRow.append(bBrush, bErase, bUndo, bClear, bInvert, bBack);

  const slider = (label, min, max, val, tip) => {
    const row = document.createElement("label");
    row.title = tip;
    row.style.cssText = "display:flex;align-items:center;gap:6px";
    const t = document.createElement("span");
    t.textContent = label;
    t.style.cssText = "width:62px";
    const s = document.createElement("input");
    s.type = "range";
    s.min = String(min);
    s.max = String(max);
    s.value = String(val);
    s.style.cssText = "flex:1;margin:0;min-width:0";
    s.setAttribute("aria-label", label);
    const v = document.createElement("span");
    v.style.cssText = "width:30px;text-align:right";
    v.textContent = String(val);
    s.addEventListener("input", () => (v.textContent = s.value));
    row.append(t, s, v);
    return { row, s };
  };
  const sizeS = slider("Size", 1, 200, 40, "Brush size in pixels of the mask area.");
  const hardS = slider("Hardness", 0, 100, 80, "100 is a sharp edge, 0 is very soft.");
  const note = document.createElement("div");
  note.style.cssText = "opacity:.8;font-size:11px";
  note.textContent = "Run once to see your picture here, then paint.";
  box.append(stage, toolRow, sizeS.row, hardS.row, note);

  let erasing = false;
  const undo = [];
  let painting = false;
  let last = null;
  let raf = 0;

  const styleTools = () => {
    for (const [b, on] of [[bBrush, !erasing], [bErase, erasing]]) {
      b.style.background = on ? P.gold_dim : "transparent";
      b.setAttribute("aria-pressed", on ? "true" : "false");
    }
  };

  const redraw = () => {
    raf = 0;
    if (view.width !== mask.width || view.height !== mask.height) {
      view.width = mask.width;
      view.height = mask.height;
      tint.width = mask.width;
      tint.height = mask.height;
    }
    const v = view.getContext("2d");
    v.clearRect(0, 0, view.width, view.height);
    tctx.globalCompositeOperation = "source-over";
    tctx.clearRect(0, 0, tint.width, tint.height);
    tctx.drawImage(mask, 0, 0);
    tctx.globalCompositeOperation = "source-in";
    tctx.fillStyle = P.gold;
    tctx.fillRect(0, 0, tint.width, tint.height);
    v.globalAlpha = 0.6;
    v.drawImage(tint, 0, 0);
    v.globalAlpha = 1;
  };
  const schedule = () => {
    if (!raf) raf = requestAnimationFrame(redraw);
  };

  const isEmpty = () => {
    const d = mctx.getImageData(0, 0, mask.width, mask.height).data;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 0) return false;
    return true;
  };

  // export white on black PNG, scaled down until the text fits the size limit
  const exportData = () => {
    if (isEmpty()) return "";
    let scale = 1;
    for (let i = 0; i < 5; i++) {
      const c = document.createElement("canvas");
      c.width = Math.max(1, Math.round(mask.width * scale));
      c.height = Math.max(1, Math.round(mask.height * scale));
      const x = c.getContext("2d");
      x.fillStyle = "black";
      x.fillRect(0, 0, c.width, c.height);
      x.drawImage(mask, 0, 0, c.width, c.height);
      const url = c.toDataURL("image/png");
      if (url.length <= MAX_CHARS) return url;
      scale *= 0.5;
    }
    note.textContent = "The mask is too detailed to save. Use Clear and paint with bigger strokes.";
    return dataWidget.value || "";
  };

  const commit = () => {
    try {
      dataWidget.value = exportData();
    } catch (e) {
      console.warn("[SY] could not store the mask", e);
    }
    node.setDirtyCanvas?.(true, true);
  };

  const pushUndo = () => {
    undo.push(mctx.getImageData(0, 0, mask.width, mask.height));
    if (undo.length > MAX_UNDO) undo.shift();
  };

  const stamp = (x, y) => {
    const r = Number(sizeS.s.value) / 2;
    const hard = Number(hardS.s.value) / 100;
    mctx.globalCompositeOperation = erasing ? "destination-out" : "source-over";
    if (hard >= 0.99) {
      mctx.fillStyle = "white";
      mctx.beginPath();
      mctx.arc(x, y, r, 0, Math.PI * 2);
      mctx.fill();
    } else {
      const g = mctx.createRadialGradient(x, y, r * hard, x, y, r);
      g.addColorStop(0, "rgba(255,255,255,1)");
      g.addColorStop(1, "rgba(255,255,255,0)");
      mctx.fillStyle = g;
      mctx.beginPath();
      mctx.arc(x, y, r, 0, Math.PI * 2);
      mctx.fill();
    }
    mctx.globalCompositeOperation = "source-over";
  };

  const stroke = (a, b) => {
    const r = Number(sizeS.s.value) / 2;
    const step = Math.max(1, r * 0.25);
    const dist = Math.hypot(b.x - a.x, b.y - a.y);
    const n = Math.max(1, Math.ceil(dist / step));
    for (let i = 1; i <= n; i++) stamp(a.x + ((b.x - a.x) * i) / n, a.y + ((b.y - a.y) * i) / n);
  };

  // pointer position in mask pixels (the canvas is drawn with object-fit: contain)
  const toMask = (ev) => {
    const r = view.getBoundingClientRect();
    const k = Math.min(r.width / mask.width, r.height / mask.height);
    const ox = r.left + (r.width - mask.width * k) / 2;
    const oy = r.top + (r.height - mask.height * k) / 2;
    return { x: (ev.clientX - ox) / k, y: (ev.clientY - oy) / k, k, px: ev.clientX - stage.getBoundingClientRect().left, py: ev.clientY - stage.getBoundingClientRect().top };
  };
  const moveRing = (p) => {
    const d = Number(sizeS.s.value) * p.k;
    ring.style.display = "block";
    ring.style.width = ring.style.height = d + "px";
    ring.style.left = p.px - d / 2 + "px";
    ring.style.top = p.py - d / 2 + "px";
  };

  view.addEventListener("pointerdown", (ev) => {
    if (ev.button !== 0) return;
    ev.preventDefault();
    ev.stopPropagation();
    view.setPointerCapture(ev.pointerId);
    pushUndo();
    painting = true;
    const p = toMask(ev);
    last = p;
    stamp(p.x, p.y);
    moveRing(p);
    schedule();
  });
  view.addEventListener("pointermove", (ev) => {
    const p = toMask(ev);
    moveRing(p);
    if (!painting) return;
    stroke(last, p);
    last = p;
    schedule();
  });
  const endStroke = () => {
    if (!painting) return;
    painting = false;
    commit();
  };
  view.addEventListener("pointerup", endStroke);
  view.addEventListener("pointercancel", endStroke);
  view.addEventListener("pointerleave", () => {
    if (!painting) ring.style.display = "none";
  });

  bBrush.onclick = () => ((erasing = false), styleTools());
  bErase.onclick = () => ((erasing = true), styleTools());
  bUndo.onclick = () => {
    const s = undo.pop();
    if (!s) return;
    if (s.width === mask.width && s.height === mask.height) mctx.putImageData(s, 0, 0);
    schedule();
    commit();
  };
  bClear.onclick = () => {
    pushUndo();
    mctx.clearRect(0, 0, mask.width, mask.height);
    schedule();
    commit();
  };
  bInvert.onclick = () => {
    pushUndo();
    const img = mctx.getImageData(0, 0, mask.width, mask.height);
    const d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      d[i] = d[i + 1] = d[i + 2] = 255;
      d[i + 3] = 255 - d[i + 3];
    }
    mctx.putImageData(img, 0, 0);
    schedule();
    commit();
  };

  // set the backdrop picture; the mask canvas follows its shape
  const setBackdrop = (url) => {
    const im = new Image();
    im.onload = () => {
      back.src = url;
      const [w, h] = fitSize(im.naturalWidth, im.naturalHeight);
      if (w !== mask.width || h !== mask.height) {
        const keep = document.createElement("canvas");
        keep.width = mask.width;
        keep.height = mask.height;
        keep.getContext("2d").drawImage(mask, 0, 0);
        mask.width = w;
        mask.height = h;
        mctx.drawImage(keep, 0, 0, w, h);
        undo.length = 0;
        commit();
      }
      note.textContent = "Painted areas show in gold. The picture is " + im.naturalWidth + " x " + im.naturalHeight + ".";
      schedule();
    };
    im.onerror = () => (note.textContent = "The picture could not be shown. Run the workflow again.");
    im.src = url;
  };

  // best effort: a picture loader in front of this node
  const findUpstream = () => {
    try {
      const up = node.getInputNode?.(0);
      const w = up?.widgets?.find((x) => x.name === "image" && typeof x.value === "string");
      if (w && w.value) {
        const parts = w.value.split("/");
        const name = parts.pop();
        return { filename: name, subfolder: parts.join("/"), type: "input" };
      }
    } catch (_) {
      /* not a loader: the backdrop comes after a run instead */
    }
    return null;
  };
  bBack.onclick = () => {
    const f = findUpstream();
    if (f) setBackdrop(viewUrl(f));
    else note.textContent = "No simple picture loader is connected. Run the workflow to see the picture.";
  };

  // bring a stored mask back (after loading a workflow)
  node._syPaintRestore = () => {
    const text = dataWidget.value;
    if (!text || typeof text !== "string" || !text.startsWith("data:image")) return;
    const im = new Image();
    im.onload = () => {
      const c = document.createElement("canvas");
      c.width = im.naturalWidth;
      c.height = im.naturalHeight;
      const x = c.getContext("2d", { willReadFrequently: true });
      x.drawImage(im, 0, 0);
      const img = x.getImageData(0, 0, c.width, c.height);
      const d = img.data;
      for (let i = 0; i < d.length; i += 4) {
        d[i + 3] = d[i];
        d[i] = d[i + 1] = d[i + 2] = 255;
      }
      x.putImageData(img, 0, 0);
      mask.width = c.width;
      mask.height = c.height;
      mctx.drawImage(c, 0, 0);
      schedule();
    };
    im.src = text;
  };
  node._syPaintShow = (files) => {
    if (files && files[0]) setBackdrop(viewUrl(files[0]));
  };

  const widget = node.addDOMWidget("sy_paint_view", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 380];
  if (node.size && node.size[1] < 520) node.size[1] = 520;
  styleTools();
  schedule();
  node._syPaintRestore();
  setTimeout(() => {
    const f = findUpstream();
    if (f && !back.src) setBackdrop(viewUrl(f));
  }, 400);
}

app.registerExtension({
  name: "sy.paint",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "SYPaintMask") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        addPaintEditor(this);
      } catch (e) {
        console.warn("[SY] paint editor not shown", e);
      }
      return r;
    };
    const configure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configure ? configure.apply(this, arguments) : undefined;
      if (this._syPaintRestore) setTimeout(() => this._syPaintRestore(), 0);
      return r;
    };
    const executed = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (msg) {
      if (executed) executed.apply(this, arguments);
      if (this._syPaintShow) this._syPaintShow(msg?.sy_paint);
    };
  },
});
