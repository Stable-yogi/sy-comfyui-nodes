// SY Nodes by Stable Yogi: Layout Box Draw SY. A small canvas inside the node where boxes are drawn with the mouse.
// The rules are in sy_layout_draw_logic.js and match nodes/sy_layout_box_draw.py. The boxes are written into the
// "boxes" text widget as JSON, so the saved workflow keeps them. Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, widgetValue } from "./sy_ui_kit.js";
import {
  COLOURS, MAX_BOXES, MIN_BOX, HANDLE, rgb, nextColour, parseBoxes, serialiseBoxes, viewFor, toPanel, toPicture,
  hitTest, boxFromDrag, moveBox, resizeBox, describe,
} from "./sy_layout_draw_logic.js";

const FONT = "'DM Sans', sans-serif";
const TYPE = "SYLayoutBoxDraw";
const PANEL_H = 300;

function setup(node) {
  const wrap = document.createElement("div");
  wrap.style.cssText = "width:100%;box-sizing:border-box;display:flex;flex-direction:column;gap:4px;font-family:" + FONT;
  const canvas = document.createElement("canvas");
  canvas.style.cssText = "width:100%;height:" + (PANEL_H - 56) + "px;border-radius:6px;touch-action:none;outline:none";
  canvas.tabIndex = 0;
  const bar = document.createElement("div");
  bar.style.cssText = "display:flex;flex-wrap:wrap;gap:4px;align-items:center";
  const colourBtn = button("Colour: red", "ghost", "Colour for the next box you draw. Click to change it; with a box selected it changes that box.");
  const nameBtn = button("Name", "ghost", "Give the selected box a name (or double-click a box).");
  const delBtn = button("Delete", "ghost", "Delete the selected box (or press Delete, or right-click a box).");
  const clearBtn = button("Clear", "ghost", "Remove every box.");
  const readout = document.createElement("div");
  readout.style.cssText = "font:500 11px " + FONT + ";min-height:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis";
  bar.append(colourBtn, nameBtn, delBtn, clearBtn);
  wrap.append(canvas, bar, readout);

  const state = { boxes: [], sel: -1, colour: "red", drag: null, lastText: null, hover: "", dirty: true };
  const dims = () => [Math.max(1, Math.round(Number(widgetValue(node, "canvas_width", 1024)) || 1024)), Math.max(1, Math.round(Number(widgetValue(node, "canvas_height", 1024)) || 1024))];
  const snap = () => Math.max(1, Math.round(Number(widgetValue(node, "snap_to", 1)) || 1));

  const boxesWidget = () => node.widgets?.find((x) => x.name === "boxes");
  function write() {
    const w = boxesWidget();
    if (!w) return;
    const text = serialiseBoxes(state.boxes);
    state.lastText = text;
    w.value = text;
    try { w.callback?.(text); } catch (e) { /* the value is already set */ }
    node.graph?.setDirtyCanvas?.(true, true);
    state.dirty = true;
  }
  function pullFromWidget() {
    const w = boxesWidget();
    if (!w) return;
    const text = String(w.value ?? "");
    if (text === state.lastText) return;
    state.lastText = text;
    state.boxes = parseBoxes(text);
    if (state.sel >= state.boxes.length) state.sel = -1;
    state.dirty = true;
  }

  function sizeCanvas() {
    const r = canvas.getBoundingClientRect();
    const w = Math.max(50, Math.round(r.width)), h = Math.max(50, Math.round(r.height));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; state.dirty = true; }
    return [w, h];
  }

  function draw() {
    const [pw, ph] = sizeCanvas();
    const [cw, ch] = dims();
    const view = viewFor(cw, ch, pw, ph);
    const g = canvas.getContext("2d");
    g.clearRect(0, 0, pw, ph);
    g.fillStyle = tk("void");
    g.fillRect(0, 0, pw, ph);
    // the picture area
    g.fillStyle = tk("surface");
    g.fillRect(view.ox, view.oy, cw * view.scale, ch * view.scale);
    g.strokeStyle = tk("surface_3");
    g.lineWidth = 1;
    const step = snap() > 1 ? snap() : Math.max(1, Math.pow(2, Math.round(Math.log2(Math.max(cw, ch) / 8))));
    if (step * view.scale >= 6) {
      g.beginPath();
      for (let x = step; x < cw; x += step) { const [sx] = toPanel(view, x, 0); g.moveTo(Math.round(sx) + 0.5, view.oy); g.lineTo(Math.round(sx) + 0.5, view.oy + ch * view.scale); }
      for (let y = step; y < ch; y += step) { const [, sy] = toPanel(view, 0, y); g.moveTo(view.ox, Math.round(sy) + 0.5); g.lineTo(view.ox + cw * view.scale, Math.round(sy) + 0.5); }
      g.stroke();
    }
    g.strokeStyle = tk("text_2");
    g.strokeRect(view.ox + 0.5, view.oy + 0.5, cw * view.scale, ch * view.scale);
    // boxes
    g.font = "600 11px " + FONT;
    g.textBaseline = "top";
    state.boxes.forEach((b, i) => {
      const [x0, y0] = toPanel(view, b.x, b.y);
      const bw = b.w * view.scale, bh = b.h * view.scale;
      g.fillStyle = rgb(b.colour, 0.28);
      g.fillRect(x0, y0, bw, bh);
      g.strokeStyle = rgb(b.colour);
      g.lineWidth = i === state.sel ? 3 : 1.5;
      g.strokeRect(x0, y0, bw, bh);
      if (b.label) {
        g.save();
        g.beginPath(); g.rect(x0, y0, bw, bh); g.clip();
        const dark = b.colour === "white" || b.colour === "yellow";
        g.fillStyle = dark ? "rgb(15,15,15)" : tk("white");
        g.fillText(b.label, x0 + 4, y0 + 3);
        g.restore();
      }
      if (i === state.sel) {
        g.fillStyle = tk("gold");
        for (const [hx, hy] of [[x0, y0], [x0 + bw, y0], [x0, y0 + bh], [x0 + bw, y0 + bh]]) g.fillRect(hx - HANDLE / 2, hy - HANDLE / 2, HANDLE, HANDLE);
      }
    });
    // the box being drawn
    if (state.drag?.kind === "create") {
      const d = state.drag;
      const b = boxFromDrag(d.x0, d.y0, d.x1, d.y1, cw, ch, snap(), "", state.colour);
      const [x0, y0] = toPanel(view, b.x, b.y);
      g.setLineDash([5, 4]);
      g.strokeStyle = rgb(state.colour);
      g.lineWidth = 2;
      g.strokeRect(x0, y0, b.w * view.scale, b.h * view.scale);
      g.setLineDash([]);
    }
    if (!state.boxes.length && !state.drag) {
      g.fillStyle = tk("text_2");
      g.textBaseline = "middle";
      g.textAlign = "center";
      g.font = "500 12px " + FONT;
      g.fillText("Drag here to draw a box", pw / 2, ph / 2);
      g.textAlign = "left";
    }
    // buttons and readout
    const cur = state.sel >= 0 ? state.boxes[state.sel].colour : state.colour;
    colourBtn.textContent = "Colour: " + cur;
    colourBtn.style.background = rgb(cur);
    colourBtn.style.color = cur === "black" ? tk("white") : "rgb(15,15,15)";
    const sel = state.sel >= 0 ? state.boxes[state.sel] : null;
    readout.style.color = tk("text_2");
    readout.textContent = state.hover || (sel ? describe(sel) : state.boxes.length + " box" + (state.boxes.length === 1 ? "" : "es") + " on " + cw + " x " + ch);
    state.dirty = false;
  }

  function pointer(e) {
    const r = canvas.getBoundingClientRect();
    return [(e.clientX - r.left) * (canvas.width / Math.max(1, r.width)), (e.clientY - r.top) * (canvas.height / Math.max(1, r.height))];
  }
  const viewNow = () => { const [cw, ch] = dims(); return viewFor(cw, ch, canvas.width, canvas.height); };

  canvas.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return;
    canvas.focus();
    const view = viewNow();
    const [sx, sy] = pointer(e);
    const hit = hitTest(state.boxes, view, sx, sy);
    const [px, py] = toPicture(view, sx, sy);
    if (hit) {
      state.sel = hit.index;
      state.drag = { kind: hit.part === "body" ? "move" : "resize", part: hit.part, index: hit.index, start: { ...state.boxes[hit.index] }, x0: px, y0: py };
    } else {
      state.sel = -1;
      state.drag = { kind: "create", x0: px, y0: py, x1: px, y1: py };
    }
    canvas.setPointerCapture?.(e.pointerId);
    e.preventDefault();
    e.stopPropagation();
    state.dirty = true;
  });
  canvas.addEventListener("pointermove", (e) => {
    const view = viewNow();
    const [cw, ch] = dims();
    const [sx, sy] = pointer(e);
    const [px, py] = toPicture(view, sx, sy);
    const d = state.drag;
    if (!d) {
      const hit = hitTest(state.boxes, view, sx, sy);
      canvas.style.cursor = !hit ? "crosshair" : hit.part === "body" ? "move" : hit.part === "tl" || hit.part === "br" ? "nwse-resize" : "nesw-resize";
      const text = hit ? describe(state.boxes[hit.index]) : "";
      if (text !== state.hover) { state.hover = text; state.dirty = true; }
      return;
    }
    if (d.kind === "create") { d.x1 = px; d.y1 = py; }
    else if (d.kind === "move") state.boxes[d.index] = moveBox(d.start, px - d.x0, py - d.y0, cw, ch, snap());
    else state.boxes[d.index] = resizeBox(d.start, d.part, px, py, cw, ch, snap());
    state.dirty = true;
    e.preventDefault();
  });
  const finish = (e) => {
    const d = state.drag;
    if (!d) return;
    state.drag = null;
    const [cw, ch] = dims();
    if (d.kind === "create") {
      const b = boxFromDrag(d.x0, d.y0, d.x1, d.y1, cw, ch, snap(), "", state.colour);
      const view = viewNow();
      if (Math.min(b.w, b.h) * view.scale >= MIN_BOX && state.boxes.length < MAX_BOXES) {
        state.boxes.push(b);
        state.sel = state.boxes.length - 1;
        state.colour = nextColour(state.colour);
        write();
      }
    } else {
      write();
    }
    state.dirty = true;
    try { canvas.releasePointerCapture?.(e.pointerId); } catch (err) { /* already released */ }
  };
  canvas.addEventListener("pointerup", finish);
  canvas.addEventListener("pointercancel", finish);
  canvas.addEventListener("pointerleave", () => { if (!state.drag && state.hover) { state.hover = ""; state.dirty = true; } });

  function removeAt(i) {
    if (i < 0 || i >= state.boxes.length) return;
    state.boxes.splice(i, 1);
    state.sel = -1;
    write();
  }
  function rename(i) {
    if (i < 0 || i >= state.boxes.length) return;
    const name = window.prompt("Name for this box (up to 80 characters):", state.boxes[i].label);
    if (name === null) return;
    state.boxes[i] = { ...state.boxes[i], label: name.slice(0, 80) };
    write();
  }
  canvas.addEventListener("dblclick", (e) => {
    const hit = hitTest(state.boxes, viewNow(), ...pointer(e));
    if (hit) { state.sel = hit.index; rename(hit.index); }
  });
  canvas.addEventListener("contextmenu", (e) => {
    const hit = hitTest(state.boxes, viewNow(), ...pointer(e));
    if (hit) { e.preventDefault(); e.stopPropagation(); removeAt(hit.index); }
  });
  canvas.addEventListener("keydown", (e) => {
    if ((e.key === "Delete" || e.key === "Backspace") && state.sel >= 0) { e.preventDefault(); removeAt(state.sel); }
  });
  colourBtn.addEventListener("click", () => {
    if (state.sel >= 0) { const b = state.boxes[state.sel]; state.boxes[state.sel] = { ...b, colour: nextColour(b.colour) }; write(); }
    else state.colour = nextColour(state.colour);
    state.dirty = true;
  });
  nameBtn.addEventListener("click", () => rename(state.sel));
  delBtn.addEventListener("click", () => removeAt(state.sel));
  clearBtn.addEventListener("click", () => { state.boxes = []; state.sel = -1; write(); });

  const w = node.addDOMWidget("sy_layout_draw_panel", "custom", wrap, { serialize: false });
  w.computeSize = (width) => [width, PANEL_H];
  node.__syLayoutDrawNode = true;
  const bw = boxesWidget();
  if (bw) {   // the text box is the saved copy; the canvas is the way to edit it, so keep it short
    bw.computeSize = (width) => [width, 60];
  }
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syDrawSeen) clearInterval(tick);
      return;
    }
    node._syDrawSeen = true;
    try {
      pullFromWidget();
      const r = canvas.getBoundingClientRect();   // the node can be resized or zoomed: redraw when the shown size changes
      if (Math.round(r.width) !== canvas.width || Math.round(r.height) !== canvas.height) state.dirty = true;
      if (state.dirty || state.drag) draw();
    } catch (e) {
      console.warn("[SY] box drawing panel could not draw", e);
    }
  }, 120);
  pullFromWidget();
  node.setSize?.([Math.max(node.size?.[0] ?? 0, 360), Math.max(node.size?.[1] ?? 0, node.computeSize?.()[1] ?? 0)]);
  node.__syLayoutDraw = state;   // for the browser check
}

app.registerExtension({
  name: "sy.layout_box_draw",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] box drawing panel not added", e);
      }
      return r;
    };
  },
});
