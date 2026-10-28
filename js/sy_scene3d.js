// SY Nodes by Stable Yogi: browser part for 3D Scene SY (a small 3D editor drawn on a plain 2D canvas, no libraries).
import { app } from "../../scripts/app.js";
import { pal } from "./sy_core.js";

const RENDER_SIDE = 512; // long side of the stored pictures; the node resizes them to width x height
const MAX_CHARS = 1500000; // about 1.5 MB of text per stored picture
const MAX_OBJECTS = 64;
const KINDS = ["cube", "sphere", "cylinder", "plane"];
const DEFAULT_CAM = { yaw: 0.7, pitch: 0.45, dist: 9 };
const DIST_MIN = 1.5;
const DIST_MAX = 60;
const PITCH_MAX = 1.4;
const FOV = (50 * Math.PI) / 180;
const LIGHT = norm([0.4, 0.9, 0.5]);
const NEAR = 0.2;

// ---------- small vector helpers ----------
function norm(a) {
  const l = Math.hypot(a[0], a[1], a[2]) || 1;
  return [a[0] / l, a[1] / l, a[2] / l];
}
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

// ---------- unit meshes: verts + tris [a, b, c, edgeMask]; edgeMask bit0 = a-b, bit1 = b-c, bit2 = c-a is drawn ----------
function quadTris(a, b, c, d) {
  return [[a, b, c, 3], [a, c, d, 6]]; // the shared diagonal is not drawn as a wire
}

function buildCube() {
  const v = [];
  for (let i = 0; i < 8; i++) v.push([i & 1 ? 0.5 : -0.5, i & 2 ? 0.5 : -0.5, i & 4 ? 0.5 : -0.5]);
  const quads = [[0, 2, 6, 4], [1, 3, 7, 5], [0, 1, 5, 4], [2, 3, 7, 6], [0, 1, 3, 2], [4, 5, 7, 6]];
  const t = [];
  for (const q of quads) t.push(...quadTris(q[0], q[1], q[2], q[3]));
  return { v, t, solid: true };
}

function buildSphere() {
  const rings = 8;
  const segs = 14;
  const v = [];
  for (let i = 0; i <= rings; i++) {
    const phi = (Math.PI * i) / rings;
    for (let j = 0; j < segs; j++) {
      const th = (2 * Math.PI * j) / segs;
      v.push([0.5 * Math.sin(phi) * Math.cos(th), 0.5 * Math.cos(phi), 0.5 * Math.sin(phi) * Math.sin(th)]);
    }
  }
  const at = (i, j) => i * segs + (j % segs);
  const t = [];
  for (let i = 0; i < rings; i++) {
    for (let j = 0; j < segs; j++) t.push(...quadTris(at(i, j), at(i, j + 1), at(i + 1, j + 1), at(i + 1, j)));
  }
  return { v, t, solid: true };
}

function buildCylinder() {
  const segs = 16;
  const v = [];
  for (let j = 0; j < segs; j++) {
    const th = (2 * Math.PI * j) / segs;
    v.push([0.5 * Math.cos(th), -0.5, 0.5 * Math.sin(th)]);
    v.push([0.5 * Math.cos(th), 0.5, 0.5 * Math.sin(th)]);
  }
  const bottom = v.length;
  v.push([0, -0.5, 0]);
  const top = v.length;
  v.push([0, 0.5, 0]);
  const t = [];
  for (let j = 0; j < segs; j++) {
    const j2 = (j + 1) % segs;
    t.push(...quadTris(2 * j, 2 * j2, 2 * j2 + 1, 2 * j + 1));
    t.push([bottom, 2 * j, 2 * j2, 7]);
    t.push([top, 2 * j + 1, 2 * j2 + 1, 7]);
  }
  return { v, t, solid: true };
}

function buildPlane() {
  const v = [[-1, 0, -1], [1, 0, -1], [1, 0, 1], [-1, 0, 1]];
  return { v, t: quadTris(0, 1, 2, 3), solid: false };
}

const MESH = { cube: buildCube(), sphere: buildSphere(), cylinder: buildCylinder(), plane: buildPlane() };

// ---------- projection and drawing ----------
function cameraBasis(cam) {
  const cp = Math.cos(cam.pitch);
  const pos = [cam.dist * cp * Math.sin(cam.yaw), cam.dist * Math.sin(cam.pitch), cam.dist * cp * Math.cos(cam.yaw)];
  const f = norm([-pos[0], -pos[1], -pos[2]]);
  const right = norm(cross(f, [0, 1, 0]));
  const up = cross(right, f);
  return { pos, f, right, up };
}

// Returns the triangles to paint, far to near, with screen points, light amount and depth.
function buildTris(scene, W, H) {
  const B = cameraBasis(scene.camera);
  const focal = H / 2 / Math.tan(FOV / 2);
  const out = [];
  scene.objects.forEach((o, oi) => {
    const mesh = MESH[o.kind];
    if (!mesh) return;
    const centre = [o.x, o.y, o.z];
    const world = mesh.v.map((p) => [p[0] * o.scale + o.x, p[1] * o.scale + o.y, p[2] * o.scale + o.z]);
    const cam = world.map((w) => {
      const r = sub(w, B.pos);
      return [dot(r, B.right), dot(r, B.up), dot(r, B.f)];
    });
    for (const tri of mesh.t) {
      const [a, b, c, mask] = tri;
      if (cam[a][2] < NEAR || cam[b][2] < NEAR || cam[c][2] < NEAR) continue;
      const wa = world[a];
      const n0 = cross(sub(world[b], wa), sub(world[c], wa));
      const len = Math.hypot(n0[0], n0[1], n0[2]);
      if (len < 1e-9) continue;
      let n = [n0[0] / len, n0[1] / len, n0[2] / len];
      const mid = [(wa[0] + world[b][0] + world[c][0]) / 3, (wa[1] + world[b][1] + world[c][1]) / 3, (wa[2] + world[b][2] + world[c][2]) / 3];
      if (mesh.solid) {
        if (dot(n, sub(mid, centre)) < 0) n = [-n[0], -n[1], -n[2]]; // make the normal point outward
        if (dot(n, sub(B.pos, mid)) <= 0) continue; // back face
      } else if (dot(n, sub(B.pos, mid)) < 0) {
        n = [-n[0], -n[1], -n[2]]; // a plane shows both sides
      }
      const pts = [a, b, c].map((i) => [W / 2 + (cam[i][0] / cam[i][2]) * focal, H / 2 - (cam[i][1] / cam[i][2]) * focal]);
      out.push({ pts, mask, oi, z: (cam[a][2] + cam[b][2] + cam[c][2]) / 3, light: 0.3 + 0.7 * Math.max(0, dot(n, LIGHT)) });
    }
  });
  out.sort((p, q) => q.z - p.z);
  return out;
}

function pathTri(ctx, pts) {
  ctx.beginPath();
  ctx.moveTo(pts[0][0], pts[0][1]);
  ctx.lineTo(pts[1][0], pts[1][1]);
  ctx.lineTo(pts[2][0], pts[2][1]);
  ctx.closePath();
}

function fillTri(ctx, pts, style) {
  pathTri(ctx, pts);
  ctx.fillStyle = style;
  ctx.fill();
  ctx.strokeStyle = style; // same colour line closes hairline gaps between neighbours
  ctx.lineWidth = 1;
  ctx.lineJoin = "round";
  ctx.stroke();
}

function wireTri(ctx, t) {
  const p = t.pts;
  for (let e = 0; e < 3; e++) {
    if (!(t.mask & (1 << e))) continue;
    const q = p[(e + 1) % 3];
    ctx.moveTo(p[e][0], p[e][1]);
    ctx.lineTo(q[0], q[1]);
  }
}

// Plain picture for the python side. mode = "shaded" or "depth". No selection marks, no wires, no theme colours.
function renderExport(scene, W, H, mode) {
  const c = document.createElement("canvas");
  c.width = W;
  c.height = H;
  const ctx = c.getContext("2d");
  ctx.fillStyle = mode === "depth" ? "rgb(0,0,0)" : "rgb(128,128,128)";
  ctx.fillRect(0, 0, W, H);
  const tris = buildTris(scene, W, H);
  let zmin = Infinity;
  let zmax = -Infinity;
  for (const t of tris) {
    zmin = Math.min(zmin, t.z);
    zmax = Math.max(zmax, t.z);
  }
  const span = zmax - zmin || 1;
  for (const t of tris) {
    let g;
    if (mode === "depth") g = Math.round(255 - 217 * ((t.z - zmin) / span)); // near = white
    else g = Math.round(235 * t.light);
    fillTri(ctx, t.pts, "rgb(" + g + "," + g + "," + g + ")");
  }
  return { canvas: c, any: tris.length > 0 };
}

function toDataUrl(canvas) {
  let c = canvas;
  for (let i = 0; i < 4; i++) {
    const url = c.toDataURL("image/png");
    if (url.length <= MAX_CHARS) return url;
    const s = document.createElement("canvas");
    s.width = Math.max(16, Math.round(c.width / 2));
    s.height = Math.max(16, Math.round(c.height / 2));
    s.getContext("2d").drawImage(c, 0, 0, s.width, s.height);
    c = s;
  }
  return "";
}

function wrapYaw(y) {
  const t = 2 * Math.PI;
  return ((((y + Math.PI) % t) + t) % t) - Math.PI;
}

function cleanScene(raw) {
  const sc = { camera: { ...DEFAULT_CAM }, objects: [] };
  if (!raw || typeof raw !== "object") return sc;
  const cam = raw.camera || {};
  const num = (v, d, lo, hi) => (typeof v === "number" && isFinite(v) ? Math.min(hi, Math.max(lo, v)) : d);
  sc.camera.yaw = wrapYaw(num(cam.yaw, DEFAULT_CAM.yaw, -1000, 1000));
  sc.camera.pitch = num(cam.pitch, DEFAULT_CAM.pitch, -PITCH_MAX, PITCH_MAX);
  sc.camera.dist = num(cam.dist, DEFAULT_CAM.dist, DIST_MIN, DIST_MAX);
  if (Array.isArray(raw.objects)) {
    raw.objects.slice(0, MAX_OBJECTS).forEach((o, i) => {
      if (!o || !KINDS.includes(o.kind)) return;
      sc.objects.push({
        id: Number.isInteger(o.id) ? o.id : i + 1,
        kind: o.kind,
        x: num(o.x, 0, -100, 100),
        y: num(o.y, 0, -100, 100),
        z: num(o.z, 0, -100, 100),
        scale: num(o.scale, 1, 0.05, 50),
      });
    });
  }
  return sc;
}

function pointInTri(px, py, p) {
  const d1 = (px - p[1][0]) * (p[0][1] - p[1][1]) - (p[0][0] - p[1][0]) * (py - p[1][1]);
  const d2 = (px - p[2][0]) * (p[1][1] - p[2][1]) - (p[1][0] - p[2][0]) * (py - p[2][1]);
  const d3 = (px - p[0][0]) * (p[2][1] - p[0][1]) - (p[2][0] - p[0][0]) * (py - p[0][1]);
  const neg = d1 < 0 || d2 < 0 || d3 < 0;
  const pos = d1 > 0 || d2 > 0 || d3 > 0;
  return !(neg && pos);
}

function addSceneEditor(node) {
  const wScene = node.widgets?.find((w) => w.name === "scene_json");
  const wRender = node.widgets?.find((w) => w.name === "render_data");
  const wDepth = node.widgets?.find((w) => w.name === "depth_data");
  if (!wScene || !wRender || !wDepth) return;
  const P = pal();

  // hide the three text widgets but keep them in the saved workflow
  for (const w of [wScene, wRender, wDepth]) {
    w.hidden = true;
    w.computeSize = () => [0, -4];
    if (w.element) w.element.style.display = "none";
  }

  // a colour from the palette as [r, g, b]
  const probe = document.createElement("canvas");
  probe.width = probe.height = 1;
  const pctx = probe.getContext("2d", { willReadFrequently: true });
  const rgbOf = (css) => {
    pctx.clearRect(0, 0, 1, 1);
    pctx.fillStyle = css;
    pctx.fillRect(0, 0, 1, 1);
    const d = pctx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2]];
  };
  const base = { cube: rgbOf(P.gold), sphere: rgbOf(P.text), cylinder: rgbOf(P.muted), plane: rgbOf(P.gold_dim) };

  const state = { scene: cleanScene(null), selected: null };
  let hits = [];
  let timer = 0;
  let raf = 0;

  const box = document.createElement("div");
  box.style.cssText = "display:flex;flex-direction:column;gap:4px;width:100%;height:100%;font:12px 'DM Sans',sans-serif;color:" + P.text;

  const stage = document.createElement("div");
  stage.style.cssText = "position:relative;flex:1;min-height:140px;border-radius:6px;overflow:hidden;background:" + P.surface;
  const view = document.createElement("canvas");
  view.setAttribute("aria-label", "3D scene. Drag to orbit, scroll to zoom, click an object to select it.");
  view.style.cssText = "position:absolute;inset:0;width:100%;height:100%;object-fit:contain;touch-action:none;cursor:grab";
  stage.append(view);

  const mk = (text, tip) => {
    const b = document.createElement("button");
    b.textContent = text;
    b.title = tip;
    b.style.cssText = "flex:1;cursor:pointer;border-radius:6px;border:1px solid " + P.gold_dim + ";background:transparent;color:inherit;padding:2px 4px;font:12px 'DM Sans',sans-serif";
    return b;
  };
  const addRow = document.createElement("div");
  addRow.style.cssText = "display:flex;gap:4px";
  const addButtons = KINDS.map((k) => {
    const b = mk("Add " + k, "Put a new " + k + " in the scene.");
    b.onclick = () => addObject(k);
    return b;
  });
  addRow.append(...addButtons);
  const toolRow = document.createElement("div");
  toolRow.style.cssText = "display:flex;gap:4px";
  const bDelete = mk("Delete selected", "Remove the selected object.");
  const bReset = mk("Reset camera", "Go back to the starting view.");
  toolRow.append(bDelete, bReset);

  const slider = (label, min, max, step, tip) => {
    const row = document.createElement("label");
    row.title = tip;
    row.style.cssText = "display:flex;align-items:center;gap:6px";
    const t = document.createElement("span");
    t.textContent = label;
    t.style.cssText = "width:46px";
    const s = document.createElement("input");
    s.type = "range";
    s.min = String(min);
    s.max = String(max);
    s.step = String(step);
    s.value = "0";
    s.style.cssText = "flex:1;margin:0;min-width:0";
    s.setAttribute("aria-label", label);
    const v = document.createElement("span");
    v.style.cssText = "width:38px;text-align:right";
    row.append(t, s, v);
    return { row, s, v };
  };
  const sX = slider("X", -10, 10, 0.1, "Move the selected object left or right.");
  const sY = slider("Y", -10, 10, 0.1, "Move the selected object up or down.");
  const sZ = slider("Z", -10, 10, 0.1, "Move the selected object forward or back.");
  const sS = slider("Scale", 0.1, 5, 0.05, "Make the selected object bigger or smaller.");
  const sliders = { x: sX, y: sY, z: sZ, scale: sS };
  const note = document.createElement("div");
  note.style.cssText = "opacity:.8;font-size:11px";
  box.append(stage, addRow, toolRow, sX.row, sY.row, sZ.row, sS.row, note);

  // ---------- sizes and drawing ----------
  const renderSize = () => {
    const w = Number(node.widgets?.find((x) => x.name === "width")?.value) || 768;
    const h = Number(node.widgets?.find((x) => x.name === "height")?.value) || 768;
    const k = RENDER_SIDE / Math.max(w, h);
    return [Math.max(16, Math.round(w * k)), Math.max(16, Math.round(h * k))];
  };

  const selectedObj = () => state.scene.objects.find((o) => o.id === state.selected) || null;

  const draw = () => {
    raf = 0;
    const [W, H] = renderSize();
    if (view.width !== W || view.height !== H) {
      view.width = W;
      view.height = H;
    }
    const ctx = view.getContext("2d");
    ctx.fillStyle = P.abyss;
    ctx.fillRect(0, 0, W, H);
    const tris = buildTris(state.scene, W, H);
    hits = tris;
    for (const t of tris) {
      const o = state.scene.objects[t.oi];
      const c = base[o.kind];
      fillTri(ctx, t.pts, "rgb(" + Math.round(c[0] * t.light) + "," + Math.round(c[1] * t.light) + "," + Math.round(c[2] * t.light) + ")");
    }
    ctx.lineJoin = "round";
    ctx.lineWidth = 1;
    ctx.strokeStyle = P.void;
    ctx.globalAlpha = 0.45;
    ctx.beginPath();
    for (const t of tris) if (state.scene.objects[t.oi].id !== state.selected) wireTri(ctx, t);
    ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.strokeStyle = P.gold;
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (const t of tris) if (state.scene.objects[t.oi].id === state.selected) wireTri(ctx, t);
    ctx.stroke();
  };
  const schedule = () => {
    if (!raf) raf = requestAnimationFrame(draw);
  };

  // ---------- storing the result in the hidden widgets ----------
  const commitNow = () => {
    timer = 0;
    try {
      const sc = state.scene;
      wScene.value = JSON.stringify({
        version: 1,
        camera: { yaw: sc.camera.yaw, pitch: sc.camera.pitch, dist: sc.camera.dist },
        objects: sc.objects.map((o) => ({ id: o.id, kind: o.kind, x: o.x, y: o.y, z: o.z, scale: o.scale })),
      });
      if (!sc.objects.length) {
        wRender.value = "";
        wDepth.value = "";
      } else {
        const [W, H] = renderSize();
        wRender.value = toDataUrl(renderExport(sc, W, H, "shaded").canvas);
        wDepth.value = toDataUrl(renderExport(sc, W, H, "depth").canvas);
      }
    } catch (e) {
      console.warn("[SY] could not store the 3D scene", e);
    }
    node.setDirtyCanvas?.(true, true);
  };
  const commit = (soon) => {
    if (timer) clearTimeout(timer);
    if (soon) timer = setTimeout(commitNow, 180);
    else commitNow();
  };

  const syncSliders = () => {
    const o = selectedObj();
    for (const key of Object.keys(sliders)) {
      const s = sliders[key];
      s.s.disabled = !o;
      if (o) {
        s.s.value = String(o[key]);
        s.v.textContent = o[key].toFixed(key === "scale" ? 2 : 1);
      } else {
        s.v.textContent = "";
      }
    }
    bDelete.disabled = !o;
    bDelete.style.opacity = o ? "1" : ".5";
    note.textContent = o
      ? "Selected: " + o.kind + ". Drag to orbit, scroll to zoom."
      : state.scene.objects.length ? "Click an object to select it. Drag to orbit, scroll to zoom." : "Add a shape to start.";
  };

  const changed = (soon) => {
    syncSliders();
    schedule();
    commit(soon);
  };

  function addObject(kind) {
    const sc = state.scene;
    if (sc.objects.length >= MAX_OBJECTS) {
      note.textContent = "That is the most objects this scene can hold (" + MAX_OBJECTS + ").";
      return;
    }
    const n = sc.objects.length;
    const id = sc.objects.reduce((m, o) => Math.max(m, o.id), 0) + 1;
    sc.objects.push({ id, kind, x: ((n % 5) - 2) * 1.5, y: 0, z: -Math.floor(n / 5) * 1.5, scale: 1 });
    state.selected = id;
    changed(false);
  }
  bDelete.onclick = () => {
    const o = selectedObj();
    if (!o) return;
    state.scene.objects = state.scene.objects.filter((x) => x.id !== o.id);
    state.selected = null;
    changed(false);
  };
  bReset.onclick = () => {
    state.scene.camera = { ...DEFAULT_CAM };
    changed(false);
  };
  for (const key of Object.keys(sliders)) {
    sliders[key].s.addEventListener("input", () => {
      const o = selectedObj();
      if (!o) return;
      o[key] = Number(sliders[key].s.value);
      sliders[key].v.textContent = o[key].toFixed(key === "scale" ? 2 : 1);
      schedule();
      commit(true);
    });
  }

  // ---------- mouse: orbit, zoom, select ----------
  const toView = (ev) => {
    const r = view.getBoundingClientRect();
    const k = Math.min(r.width / view.width, r.height / view.height) || 1;
    const ox = r.left + (r.width - view.width * k) / 2;
    const oy = r.top + (r.height - view.height * k) / 2;
    return { x: (ev.clientX - ox) / k, y: (ev.clientY - oy) / k };
  };
  let drag = null;
  view.addEventListener("pointerdown", (ev) => {
    if (ev.button !== 0) return;
    ev.preventDefault();
    ev.stopPropagation();
    view.setPointerCapture(ev.pointerId);
    drag = { x: ev.clientX, y: ev.clientY, moved: 0 };
    view.style.cursor = "grabbing";
  });
  view.addEventListener("pointermove", (ev) => {
    if (!drag) return;
    const dx = ev.clientX - drag.x;
    const dy = ev.clientY - drag.y;
    drag.x = ev.clientX;
    drag.y = ev.clientY;
    drag.moved += Math.abs(dx) + Math.abs(dy);
    const cam = state.scene.camera;
    cam.yaw = wrapYaw(cam.yaw - dx * 0.008);
    cam.pitch = Math.min(PITCH_MAX, Math.max(-PITCH_MAX, cam.pitch + dy * 0.008));
    schedule();
  });
  const endDrag = (ev) => {
    if (!drag) return;
    const wasClick = drag.moved < 4;
    drag = null;
    view.style.cursor = "grab";
    if (wasClick && ev.type === "pointerup") {
      const p = toView(ev);
      let found = null;
      for (let i = hits.length - 1; i >= 0 && found === null; i--) {
        if (pointInTri(p.x, p.y, hits[i].pts)) found = state.scene.objects[hits[i].oi].id;
      }
      state.selected = found;
      changed(false);
    } else {
      changed(false);
    }
  };
  view.addEventListener("pointerup", endDrag);
  view.addEventListener("pointercancel", endDrag);
  view.addEventListener(
    "wheel",
    (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      const cam = state.scene.camera;
      cam.dist = Math.min(DIST_MAX, Math.max(DIST_MIN, cam.dist * Math.exp(ev.deltaY * 0.0012)));
      schedule();
      commit(true);
    },
    { passive: false }
  );

  // keep the stored pictures in step with the width / height widgets
  for (const name of ["width", "height"]) {
    const w = node.widgets?.find((x) => x.name === name);
    if (!w) continue;
    const old = w.callback;
    w.callback = function () {
      const r = old ? old.apply(this, arguments) : undefined;
      schedule();
      commit(true);
      return r;
    };
  }

  // bring a stored scene back (after loading a workflow)
  node._sySceneRestore = () => {
    const text = wScene.value;
    if (!text || typeof text !== "string") return;
    try {
      state.scene = cleanScene(JSON.parse(text));
    } catch (e) {
      note.textContent = "The stored scene could not be read. Add shapes to start again.";
      return;
    }
    if (!selectedObj()) state.selected = null;
    syncSliders();
    schedule();
  };

  const widget = node.addDOMWidget("sy_scene3d_view", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 460];
  if (node.size && node.size[1] < 640) node.size[1] = 640;
  syncSliders();
  schedule();
  node._sySceneRestore();
}

app.registerExtension({
  name: "sy.scene3d",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "SYScene3D") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        addSceneEditor(this);
      } catch (e) {
        console.warn("[SY] 3D scene editor not shown", e);
      }
      return r;
    };
    const configure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configure ? configure.apply(this, arguments) : undefined;
      if (this._sySceneRestore) setTimeout(() => this._sySceneRestore(), 0);
      return r;
    };
  },
});
