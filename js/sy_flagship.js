// SY Nodes by Stable Yogi: own buttons and live helpers for the 16 most used nodes.
// Every button only sets the same widgets you can set by hand, so a workflow still runs without this file.
// Text is always set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme, store, save } from "./sy_core.js";
import { button, setSwitch, row, label, overlay, tk, setWidget, widgetValue } from "./sy_ui_kit.js";

const FONT = "'DM Sans', sans-serif";

// ---- small helpers ------------------------------------------------------------------------
function box(gap = 4) {
  const d = document.createElement("div");
  d.style.cssText = "display:flex;flex-direction:column;gap:" + gap + "px;width:100%;box-sizing:border-box;padding:2px;font:12px " + FONT + ";color:" + tk("white");
  return d;
}

function note(text = "") {
  const d = document.createElement("div");
  d.textContent = text;
  d.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2");
  return d;
}

function panel(node, name, el, h) {
  const w = node.addDOMWidget(name, "custom", el, { serialize: false });
  w.computeSize = (width) => [width, h];
  const need = node.computeSize?.();
  if (need && node.size[1] < need[1]) node.setSize([Math.max(node.size[0], 250), need[1]]);
  return w;
}

function widget(node, name) {
  return node.widgets?.find((w) => w.name === name);
}

// run fn whenever a normal widget of the node changes, and once after a workflow is loaded
function onChange(node, fn) {
  const run = () => {
    try { fn(); } catch (e) { console.warn("[SY] button helper", e); }
  };
  for (const w of node.widgets || []) {
    if (w.name.startsWith("sy_")) continue;
    const orig = w.callback;
    w.callback = function () {
      const r = orig ? orig.apply(this, arguments) : undefined;
      run();
      return r;
    };
  }
  const conf = node.onConfigure;
  node.onConfigure = function () {
    const r = conf ? conf.apply(this, arguments) : undefined;
    setTimeout(run, 50);
    return r;
  };
  setTimeout(run, 300);
  return run;
}

// run fn when the user types in a multiline text widget
function onTyping(node, wname, fn) {
  let done = false;
  const attach = () => {
    const el = widget(node, wname)?.inputEl;
    if (el && !done) {
      done = true;
      el.addEventListener("input", fn);
    }
    fn();
  };
  for (const t of [100, 500, 1500]) setTimeout(attach, t);
}

function choiceRow(node, wname, values, tip) {
  const r = row();
  const btns = values.map((v) => {
    const b = button(v, "ghost", tip);
    b.onclick = () => { setWidget(node, wname, v); refresh(); };
    r.append(b);
    return [v, b];
  });
  const refresh = () => {
    const cur = String(widgetValue(node, wname, ""));
    for (const [v, b] of btns) setSwitch(b, v === cur);
  };
  r.refresh = refresh;
  return r;
}

function shape(canvas, w, h) {
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  if (!(w > 0 && h > 0)) return;
  const s = Math.min((W - 8) / w, (H - 8) / h);
  const rw = w * s, rh = h * s;
  ctx.fillStyle = tk("surface_3");
  ctx.strokeStyle = tk("gold");
  ctx.lineWidth = 2;
  ctx.fillRect((W - rw) / 2, (H - rh) / 2, rw, rh);
  ctx.strokeRect((W - rw) / 2, (H - rh) / 2, rw, rh);
}

// ---- one setup function per node ------------------------------------------------------------
const SETUP = {};

SETUP.SYSeed = (node) => {
  const el = box();
  const last = note("Last run used: not run yet");
  const rnd = button("New random seed", "gold", "Put a new random number in the seed box.");
  const reuse = button("Use last seed", "ghost", "Take the seed the last run really used and keep it fixed. Good to repeat a random pick.");
  el.append(row(rnd, reuse), last);
  let lastSeed = null;
  rnd.onclick = () => {
    const w = widget(node, "seed");
    const max = Math.min(Number(w?.options?.max ?? Number.MAX_SAFE_INTEGER), Number.MAX_SAFE_INTEGER);
    setWidget(node, "seed", Math.floor(Math.random() * max));
  };
  reuse.onclick = () => {
    if (lastSeed === null) { last.textContent = "Run the node first."; return; }
    setWidget(node, "seed", lastSeed);
    setWidget(node, "mode", "fixed");
  };
  node._syOnResult = (msg) => {
    const t = msg?.sy_text?.find((i) => i.name === "seed")?.text;
    if (t === undefined) return;
    lastSeed = Number(t);
    last.textContent = "Last run used: " + t;
  };
  panel(node, "sy_seed_buttons", el, 62);
};

function sizeNode(node, buttons, readTarget) {
  const el = box();
  const cv = document.createElement("canvas");
  cv.width = 120;
  cv.height = 64;
  cv.style.cssText = "align-self:center;width:120px;height:64px";
  const txt = note("");
  txt.style.textAlign = "center";
  el.append(cv, txt);
  for (const b of buttons) el.append(b);
  let seq = 0;
  const refresh = async () => {
    for (const b of buttons) b.refresh?.();
    const my = ++seq;
    const q = new URLSearchParams({ node: node.comfyClass || node.type });
    for (const w of node.widgets || []) if (!w.name.startsWith("sy_")) q.set(w.name, String(w.value));
    try {
      const res = await api.fetchApi("/sy/flagship/size?" + q.toString());
      const d = await res.json();
      if (my !== seq) return;
      if (!res.ok) throw new Error(d.error || "no size");
      shape(cv, d.width, d.height);
      txt.textContent = d.width + " x " + d.height + "  |  " + d.megapixels + " MP";
      readTarget?.(d);
    } catch (e) {
      shape(cv, 0, 0);
      txt.textContent = "No size: " + String(e.message || e);
    }
  };
  onChange(node, refresh);
  panel(node, "sy_size_view", el, 100 + buttons.length * 30);
  return refresh;
}

SETUP.SYResolution = (node) => {
  const ratios = choiceRow(node, "aspect", ["1:1", "4:3", "3:2", "16:9", "21:9"], "Set the shape of the picture.");
  const flip = button("Flip portrait / landscape", "ghost", "Turn the picture on its side.");
  const wrap = box(3);
  wrap.append(ratios, row(flip));
  wrap.refresh = ratios.refresh;
  flip.onclick = () => {
    const cur = widgetValue(node, "orientation", "landscape");
    setWidget(node, "orientation", cur === "landscape" ? "portrait" : "landscape");
  };
  sizeNode(node, [wrap]);
};

SETUP.SYSizePresets = (node) => {
  const names = () => (widget(node, "preset")?.options?.values || []).slice();
  const step = (d) => {
    const list = names();
    const i = list.indexOf(widgetValue(node, "preset", ""));
    if (list.length) setWidget(node, "preset", list[(i + d + list.length) % list.length]);
  };
  const flip = (name) => {
    const m = /^(\d+)x(\d+)/.exec(name);
    return m ? names().find((n) => n.startsWith(m[2] + "x" + m[1] + " ")) : null;
  };
  const prev = button("< Previous", "ghost", "Go to the previous size in the list.");
  const next = button("Next >", "ghost", "Go to the next size in the list.");
  const sw = button("Flip width / height", "ghost", "Switch to the same size on its side, if the list has it.");
  prev.onclick = () => step(-1);
  next.onclick = () => step(1);
  sw.onclick = () => {
    const f = flip(widgetValue(node, "preset", ""));
    if (f) setWidget(node, "preset", f);
  };
  const wrap = box(3);
  wrap.append(row(prev, next), row(sw));
  sizeNode(node, [wrap]);
};

SETUP.SYVideoSizePresets = (node) => {
  const res = choiceRow(node, "resolution", ["480p", "720p", "1080p"], "Length of the short side.");
  const asp = choiceRow(node, "aspect", ["16:9", "9:16", "1:1"], "Wide, tall or square.");
  const wrap = box(3);
  wrap.append(res, asp);
  wrap.refresh = () => { res.refresh(); asp.refresh(); };
  sizeNode(node, [wrap]);
};

SETUP.SYSwitch = (node) => {
  const big = button("", "gold");
  big.style.cssText += ";width:100%;padding:8px;font-size:14px";
  const el = box();
  el.append(big);
  const sync = () => {
    const a = !!widgetValue(node, "use_a", true);
    big.textContent = a ? "A is sent  (click for B)" : "B is sent  (click for A)";
    setSwitch(big, a);
  };
  big.onclick = () => { setWidget(node, "use_a", !widgetValue(node, "use_a", true)); sync(); };
  onChange(node, sync);
  panel(node, "sy_switch_button", el, 44);
};

SETUP.SYNumberCompare = (node) => {
  const lamp = note("Run the node to see the answer");
  lamp.style.cssText += ";text-align:center;padding:6px;border-radius:6px;font-size:14px;background:" + tk("surface_3");
  const el = box();
  el.append(lamp);
  node._syOnResult = (msg) => {
    const t = msg?.sy_text?.[0]?.text;
    if (t === undefined) return;
    const yes = t === "True";
    lamp.textContent = (yes ? "YES" : "NO") + "  (a " + widgetValue(node, "operator", "?") + " b is " + t + ")";
    lamp.style.background = yes ? tk("green_btn") : "#8a2d2d";
    lamp.style.color = tk("white");
  };
  panel(node, "sy_compare_lamp", el, 42);
};

function counterValue(i, start, step, max, wrap) {
  const raw = step * i;
  if (!wrap) return start + raw;
  const span = max - start + 1;
  if (span <= 0) return NaN;
  return start + (((raw % span) + span) % span);
}

SETUP.SYCounter = (node) => {
  const seqTxt = note("");
  seqTxt.style.whiteSpace = "normal";
  const minus = button("-1", "ghost", "Go back one run.");
  const plus = button("+1", "ghost", "Go forward one run.");
  const reset = button("Reset to run 0", "gold", "Set the run number back to 0.");
  const el = box();
  el.append(row(minus, plus, reset), seqTxt);
  const num = (n, d) => Number(widgetValue(node, n, d));
  const update = () => {
    const i0 = num("run_index", 0);
    const vals = [];
    for (let k = 0; k < 8; k++) vals.push(counterValue(i0 + k, num("start", 0), num("step", 1), num("max_value", 9), !!widgetValue(node, "wrap", true)));
    seqTxt.textContent = "From run " + i0 + ": " + vals.join(", ") + " ...";
  };
  minus.onclick = () => setWidget(node, "run_index", Math.max(0, num("run_index", 0) - 1));
  plus.onclick = () => setWidget(node, "run_index", num("run_index", 0) + 1);
  reset.onclick = () => setWidget(node, "run_index", 0);
  onChange(node, update);
  panel(node, "sy_counter_buttons", el, 78);
};

function textStats(node, wname, extra) {
  const info = note("");
  const el = box();
  el.append(info);
  const update = () => {
    const t = String(widgetValue(node, wname, ""));
    const words = (t.match(/\S+/g) || []).length;
    const lines = t ? t.split("\n").length : 0;
    info.textContent = t.length + " characters | " + words + " words | " + lines + " lines" + (extra ? " | " + extra(t) : "");
  };
  onTyping(node, wname, update);
  onChange(node, update);
  panel(node, "sy_text_count", el, 30);
  return { el, info, update };
}

SETUP.SYMultilineText = (node) => {
  textStats(node, "text");
};

SETUP.SYPromptCleaner = (node) => {
  const tags = (t) => t.split(",").filter((x) => x.trim()).length;
  const s = textStats(node, "text", (t) => tags(t) + " tags");
  const out = note("");
  s.el.append(out);
  node._syOnResult = (msg) => {
    const t = msg?.sy_text?.[0]?.text;
    if (t === undefined) return;
    const before = String(widgetValue(node, "text", ""));
    out.textContent = "Cleaned: " + before.length + " -> " + t.length + " characters, " + tags(before) + " -> " + tags(t) + " tags";
  };
  addPresets(node, "SYPromptCleaner");
};

SETUP.SYLoadText = (node) => {
  const pick = button("Pick a .txt file...", "gold", "Choose a text file from the ComfyUI input folder.");
  const el = box();
  el.append(pick);
  pick.onclick = async () => {
    const ov = overlay("Text files in the input folder", 460);
    ov.body.textContent = "Looking...";
    try {
      const res = await api.fetchApi("/sy/flagship/textfiles");
      const d = await res.json();
      ov.body.textContent = "";
      if (!d.files?.length) ov.body.textContent = "No .txt files in the input folder yet.";
      for (const f of d.files || []) {
        const b = button(f, "ghost");
        b.style.cssText += ";display:block;width:100%;text-align:left;margin-bottom:4px";
        b.onclick = () => { setWidget(node, "file", f); ov.close(); };
        ov.body.append(b);
      }
    } catch (e) {
      ov.body.textContent = "Could not read the list.";
    }
  };
  panel(node, "sy_text_picker", el, 38);
};

SETUP.SYXYGridAssemble = (node) => {
  const info = note("");
  const el = box();
  el.append(info);
  const count = (n) => {
    const lines = String(widgetValue(node, n, "")).split("\n").filter((x) => x.trim()).length;
    return Math.max(1, lines);
  };
  const update = () => {
    const x = count("x_labels"), y = count("y_labels");
    info.textContent = "Needs " + x + " x " + y + " = " + x * y + " pictures (X changes fastest)";
  };
  onTyping(node, "x_labels", update);
  onTyping(node, "y_labels", update);
  onChange(node, update);
  panel(node, "sy_grid_count", el, 30);
};

// ---- saved settings (presets) for nodes with many settings ----------------------------------
function defaultsOf(node) {
  const spec = { ...(node.constructor?.nodeData?.input?.required || {}), ...(node.constructor?.nodeData?.input?.optional || {}) };
  const out = {};
  for (const [name, def] of Object.entries(spec)) {
    if (!widget(node, name)) continue;
    const kind = def[0];
    if (Array.isArray(kind)) out[name] = def[1]?.default ?? kind[0];
    else if (def[1] && "default" in def[1]) out[name] = def[1].default;
  }
  return out;
}

function addPresets(node, key) {
  const skip = new Set(["model", "clip", "image", "images", "reference"]);
  const plain = () => (node.widgets || []).filter((w) => !w.name.startsWith("sy_") && !skip.has(w.name) && w.serialize !== false && ["number", "combo", "toggle", "text", "string", "customtext"].includes(w.type));
  const sel = document.createElement("select");
  sel.setAttribute("aria-label", "Saved settings");
  sel.style.cssText = "flex:1;min-width:80px;font:12px " + FONT + ";background:" + tk("surface_3") + ";color:" + tk("white") + ";border:0;border-radius:6px;padding:3px";
  const load = button("Load", "ghost", "Put the saved settings into this node.");
  const keep = button("Save as...", "gold", "Save the current settings under a name.");
  const del = button("Delete", "ghost", "Forget the chosen saved settings.");
  const reset = button("Reset", "ghost", "Put every setting back to its default.");
  const msg = note("");
  const el = box();
  el.append(row(sel, load), row(keep, del, reset), msg);
  const all = () => store("presets." + key, {});
  const fill = (pick) => {
    sel.textContent = "";
    const names = Object.keys(all()).sort();
    const first = document.createElement("option");
    first.value = "";
    first.textContent = names.length ? "Saved settings..." : "No saved settings yet";
    sel.append(first);
    for (const n of names) {
      const o = document.createElement("option");
      o.value = n;
      o.textContent = n;
      sel.append(o);
    }
    if (pick) sel.value = pick;
  };
  fill();
  keep.onclick = () => {
    const name = (window.prompt("Name for these settings:") || "").trim();
    if (!name) return;
    const data = {};
    for (const w of plain()) data[w.name] = w.value;
    const a = all();
    a[name] = data;
    save("presets." + key, a);
    fill(name);
    msg.textContent = "Saved: " + name;
  };
  load.onclick = () => {
    const data = all()[sel.value];
    if (!data) { msg.textContent = "Pick a saved name first."; return; }
    for (const [n, v] of Object.entries(data)) setWidget(node, n, v);
    msg.textContent = "Loaded: " + sel.value;
  };
  del.onclick = () => {
    const a = all();
    if (!a[sel.value]) { msg.textContent = "Pick a saved name first."; return; }
    delete a[sel.value];
    save("presets." + key, a);
    msg.textContent = "Deleted.";
    fill();
  };
  reset.onclick = () => {
    for (const [n, v] of Object.entries(defaultsOf(node))) setWidget(node, n, v);
    msg.textContent = "Back to the defaults.";
  };
  panel(node, "sy_presets", el, 92);
}

for (const [cls, key] of [["SYLoraLoaderStack", "lora"], ["SYColourMatch", "colour"], ["SYLevelsAdjust", "levels"], ["SYFaceDetect", "face"], ["SYXYValuesList", "xyvalues"]]) {
  SETUP[cls] = (node) => addPresets(node, key);
}

app.registerExtension({
  name: "sy.flagship",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const setup = SETUP[nodeData?.name];
    if (!setup) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] node buttons not added to " + nodeData.name, e);
      }
      return r;
    };
    const executed = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (msg) {
      if (executed) executed.apply(this, arguments);
      try {
        this._syOnResult?.(msg);
      } catch (e) {
        console.warn("[SY] result helper", e);
      }
    };
  },
});
