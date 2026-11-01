// SY Nodes by Stable Yogi: Power Lora Loader SY. A row editor on the node: any number of LoRAs, a switch per row,
// strength, optional separate clip strength, trigger words, a picture on hover, reorder and delete.
// The rows are stored as a JSON list in the hidden lora_rows widget, so they save in the workflow and reach the server.
// The node works without this file (the server reads lora_rows). Text is always set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, overlay, hideWidget } from "./sy_ui_kit.js";

const NODE_TYPE = "SYPowerLoraLoader";
const FONT = "'DM Sans', sans-serif";
const MAX_ROWS = 64;
const LIMIT = 10;
const STEP = 0.05;
const ROW_H = 66;
const HEAD_H = 40;
const MIN_W = 440;

// ---- pure helpers (same rules as nodes/sy_power_lora.py)
export function flat(name) {
  return String(name ?? "").replace(/\\/g, "/");
}

export function resolveName(name, available) {
  const want = flat(name).trim();
  if (!want) return null;
  const exact = available.find((a) => flat(a) === want);
  if (exact !== undefined) return exact;
  const tail = "/" + want.replace(/^\/+/, "");
  const hits = available.filter((a) => ("/" + flat(a)).endsWith(tail));
  return hits.length === 1 ? hits[0] : null;
}

export function clampStrength(v) {
  const x = Number(v);
  if (!Number.isFinite(x)) return 1;
  return Math.max(-LIMIT, Math.min(LIMIT, Math.round(x * 100) / 100));
}

export function cleanRow(r) {
  const sc = r && r.strength_clip !== null && r.strength_clip !== undefined ? clampStrength(r.strength_clip) : null;
  return {
    on: r && r.on !== false,
    name: String((r && r.name) || ""),
    strength: r && r.strength !== undefined ? clampStrength(r.strength) : 1,
    strength_clip: sc,
    triggers: String((r && r.triggers) || ""),
  };
}

export function parseRows(text) {
  try {
    const data = JSON.parse(text || "[]");
    return Array.isArray(data) ? data.slice(0, MAX_ROWS).map(cleanRow) : [];
  } catch (_) {
    return [];
  }
}

export function mergeWords(old, extra) {
  const seen = new Set();
  const out = [];
  for (const part of (String(old || "") + "," + extra.join(",")).split(/[,\n]+/)) {
    const w = part.trim();
    if (w && !seen.has(w.toLowerCase())) {
      seen.add(w.toLowerCase());
      out.push(w);
    }
  }
  return out.join(", ");
}

// ---- server calls
let loraListPromise = null;
async function loraList(fresh) {
  if (!loraListPromise || fresh) {
    loraListPromise = (async () => {
      try {
        const res = await api.fetchApi("/object_info/LoraLoader");
        const data = await res.json();
        const list = data?.LoraLoader?.input?.required?.lora_name?.[0];
        return Array.isArray(list) ? list.map(String) : [];
      } catch (_) {
        return [];
      }
    })();
  }
  return loraListPromise;
}

function el(tag, css, text) {
  const e = document.createElement(tag);
  if (css) e.style.cssText = css;
  if (text !== undefined) e.textContent = text;
  return e;
}

function stopKeys(input) {
  input.addEventListener("keydown", (e) => e.stopPropagation());
  input.addEventListener("keyup", (e) => e.stopPropagation());
}

// ---- hover picture
let hoverBox = null;
let hoverTimer = null;
function hideHover() {
  clearTimeout(hoverTimer);
  if (hoverBox) {
    hoverBox.remove();
    hoverBox = null;
  }
}

function showHoverSoon(target, name, triggers) {
  clearTimeout(hoverTimer);
  if (!name) return;
  hoverTimer = setTimeout(() => {
    const img = new Image();
    img.onload = () => {
      hideHover();
      const r = target.getBoundingClientRect();
      const box = el("div", "position:fixed;z-index:10001;max-width:260px;padding:6px;border-radius:8px;pointer-events:none;" +
        "font:12px " + FONT + ";background:" + tk("void") + ";color:" + tk("white") + ";border:1px solid " + tk("gold_dim") +
        ";box-shadow:0 6px 24px rgba(0,0,0,.6)");
      img.style.cssText = "display:block;max-width:248px;max-height:248px;border-radius:5px";
      box.append(img);
      if (triggers) box.append(el("div", "margin-top:4px;color:" + tk("text_2") + ";word-break:break-word", triggers));
      box.style.left = Math.min(r.left, window.innerWidth - 280) + "px";
      box.style.top = Math.min(r.bottom + 4, window.innerHeight - 280) + "px";
      document.body.append(box);
      hoverBox = box;
    };
    img.onerror = () => {}; // no picture: show nothing
    img.src = api.apiURL("/sy/lora/preview?name=" + encodeURIComponent(name));
  }, 400);
}

// ---- the pick list
async function pickLora(current, onPick) {
  const ov = overlay("Pick a LoRA", 560);
  const filter = el("input", "width:100%;box-sizing:border-box;margin-bottom:8px;padding:6px 8px;border-radius:6px;border:1px solid " +
    tk("gold_dim") + ";background:" + tk("surface") + ";color:" + tk("white") + ";font:14px " + FONT);
  filter.placeholder = "Type to filter the list";
  stopKeys(filter);
  const list = el("div", "display:flex;flex-direction:column;gap:3px");
  ov.body.append(filter, list);
  const all = await loraList(true);
  const draw = () => {
    list.textContent = "";
    const q = filter.value.trim().toLowerCase();
    const hits = all.filter((n) => n.toLowerCase().includes(q));
    if (!all.length) list.append(el("div", "color:" + tk("text_2"), "ComfyUI lists no LoRAs. Put .safetensors files in the loras folder and refresh."));
    else if (!hits.length) list.append(el("div", "color:" + tk("text_2"), "No LoRA matches this filter."));
    for (const n of hits.slice(0, 300)) {
      const b = button(n, n === current ? "on" : "ghost");
      b.style.textAlign = "left";
      b.style.wordBreak = "break-all";
      b.onclick = () => {
        onPick(n);
        ov.close();
      };
      list.append(b);
    }
    if (hits.length > 300) list.append(el("div", "color:" + tk("text_2"), "Showing the first 300 of " + hits.length + ". Type more to narrow it down."));
  };
  filter.oninput = draw;
  draw();
  filter.focus();
}

// ---- training tags window
async function fillTriggers(row, name, done) {
  const ov = overlay("Trigger words from training tags", 520);
  const msg = el("div", "color:" + tk("text_2") + ";margin-bottom:8px", "Reading the file header...");
  ov.body.append(msg);
  try {
    const res = await api.fetchApi("/sy/lora/info?name=" + encodeURIComponent(name));
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "could not read the file");
    const words = [...new Set([...(data.triggers || []), ...(data.tags || [])])];
    if (!words.length) {
      msg.textContent = "This LoRA file has no training tags or trigger words stored in it.";
      return;
    }
    msg.textContent = "Click a word to leave it out. Then press the button to add the rest to this row.";
    const chosen = new Set(words);
    const chips = el("div", "display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px");
    const paint = (b, w) => {
      b.style.opacity = chosen.has(w) ? "1" : ".4";
    };
    for (const w of words) {
      const b = button(w, "on");
      b.onclick = () => {
        if (chosen.has(w)) chosen.delete(w);
        else chosen.add(w);
        paint(b, w);
      };
      chips.append(b);
    }
    const ok = button("Add these words to the row", "gold");
    ok.onclick = () => {
      done(words.filter((w) => chosen.has(w)));
      ov.close();
    };
    ov.body.append(chips, ok);
  } catch (e) {
    msg.textContent = String(e.message || e);
  }
}

// ---- the editor
function buildEditor(node) {
  const rawW = node.widgets.find((w) => w.name === "lora_rows");
  const onW = node.widgets.find((w) => w.name === "all_on");
  if (!rawW) return null;
  hideWidget(rawW);
  if (onW) hideWidget(onW);

  let rows = parseRows(rawW.value);
  let available = [];
  const root = el("div", "box-sizing:border-box;width:100%;display:flex;flex-direction:column;gap:4px;font:12px " + FONT + ";color:" + tk("white"));
  const head = el("div", "display:flex;flex-wrap:wrap;gap:4px;align-items:center;height:" + (HEAD_H - 8) + "px");
  const body = el("div", "display:flex;flex-direction:column;gap:4px");
  root.append(head, body);

  const save = () => {
    rawW.value = JSON.stringify(rows);
    node.setDirtyCanvas?.(true, true);
  };
  const height = () => HEAD_H + Math.max(1, rows.length) * (rows.length ? ROW_H + 4 : 28);
  const resize = () => {
    const h = height();
    domW.computeSize = (w) => [w, h];
    const need = node.computeSize?.() || [MIN_W, h];
    node.setSize([Math.max(node.size[0], MIN_W), Math.max(need[1], 60)]);
    node.setDirtyCanvas?.(true, true);
  };
  const change = (redraw = true) => {
    save();
    if (redraw) render();
  };

  const missing = (name) => !!name && available.length > 0 && resolveName(name, available) === null;

  function numInput(value, onSet, tip) {
    const wrap = el("div", "display:flex;align-items:center;gap:2px");
    const grip = el("span", "cursor:ew-resize;user-select:none;color:" + tk("text_2") + ";padding:0 2px", "<>");
    grip.title = "Drag left or right to change the strength";
    const inp = el("input", "width:58px;box-sizing:border-box;padding:3px 4px;border-radius:5px;border:1px solid " + tk("surface_4") +
      ";background:" + tk("surface") + ";color:" + tk("white") + ";font:12px " + FONT);
    inp.type = "number";
    inp.step = String(STEP);
    inp.min = String(-LIMIT);
    inp.max = String(LIMIT);
    inp.value = String(value);
    inp.title = tip + " Double-click to set 1.0.";
    stopKeys(inp);
    inp.onchange = () => {
      const v = clampStrength(inp.value);
      inp.value = String(v);
      onSet(v);
    };
    inp.ondblclick = () => {
      inp.value = "1";
      onSet(1);
    };
    grip.onpointerdown = (e) => {
      e.preventDefault();
      grip.setPointerCapture(e.pointerId);
      let x0 = e.clientX;
      let v0 = Number(inp.value) || 0;
      grip.onpointermove = (ev) => {
        const v = clampStrength(v0 + Math.round((ev.clientX - x0) / 4) * STEP);
        inp.value = String(v);
        onSet(v, false);
      };
      grip.onpointerup = (ev) => {
        grip.releasePointerCapture(ev.pointerId);
        grip.onpointermove = null;
        grip.onpointerup = null;
        onSet(clampStrength(inp.value));
      };
    };
    wrap.append(grip, inp);
    return wrap;
  }

  function dot(on, onClick, tip) {
    const b = el("button", "width:22px;height:22px;border-radius:50%;border:2px solid " + tk("gold") + ";cursor:pointer;padding:0;flex:none;" +
      "background:" + (on ? tk("gold") : "transparent"));
    b.type = "button";
    b.title = tip;
    b.setAttribute("aria-pressed", on ? "true" : "false");
    b.onclick = onClick;
    return b;
  }

  function small(text, tip, onClick) {
    const b = button(text, "ghost", tip);
    b.style.padding = "2px 7px";
    b.onclick = onClick;
    return b;
  }

  let dragFrom = -1;
  function render() {
    body.textContent = "";
    if (!rows.length) {
      body.append(el("div", "color:" + tk("text_2") + ";padding:4px", "No LoRAs yet. Press + Add LoRA."));
    }
    rows.forEach((r, i) => {
      const gone = missing(r.name);
      const line = el("div", "display:flex;flex-direction:column;gap:3px;height:" + ROW_H + "px;box-sizing:border-box;padding:4px 6px;border-radius:7px;" +
        "background:" + tk("surface_2") + ";border:1px solid " + (gone ? tk("red_soft") : tk("surface_3")) + (r.on ? "" : ";opacity:.6"));
      const l1 = el("div", "display:flex;align-items:center;gap:5px;height:26px");
      const l2 = el("div", "display:flex;align-items:center;gap:5px;height:24px");

      const grab = el("span", "cursor:grab;color:" + tk("text_2") + ";user-select:none;flex:none", "::");
      grab.title = "Drag to move this row";
      grab.onmousedown = () => {
        line.draggable = true;
      };
      line.ondragstart = (e) => {
        dragFrom = i;
        e.dataTransfer?.setData("text/plain", String(i));
      };
      line.ondragend = () => {
        line.draggable = false;
        dragFrom = -1;
      };
      line.ondragover = (e) => {
        if (dragFrom >= 0) e.preventDefault();
      };
      line.ondrop = (e) => {
        e.preventDefault();
        if (dragFrom < 0 || dragFrom === i) return;
        const [moved] = rows.splice(dragFrom, 1);
        rows.splice(i, 0, moved);
        dragFrom = -1;
        change();
      };

      const sw = dot(r.on, () => {
        r.on = !r.on;
        change();
      }, r.on ? "On. Click to switch this LoRA off." : "Off. Click to switch this LoRA on.");

      const nameBtn = button(r.name ? (gone ? r.name + "  (file not found)" : r.name) : "Pick a LoRA...", "ghost", "Click to pick a LoRA from the list");
      nameBtn.style.cssText += ";flex:1;min-width:0;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap";
      if (gone) nameBtn.style.color = tk("red_soft");
      nameBtn.onclick = () => {
        hideHover();
        pickLora(r.name, (n) => {
          r.name = n;
          change();
        });
      };
      nameBtn.onmouseenter = () => {
        if (!gone) showHoverSoon(nameBtn, r.name, r.triggers);
      };
      nameBtn.onmouseleave = hideHover;

      const str = numInput(r.strength, (v, redraw = true) => {
        r.strength = v;
        change(redraw);
      }, "How strongly the LoRA changes the model.");

      l1.append(grab, sw, nameBtn, str);
      if (r.strength_clip === null) {
        const link = small("separate clip strength", "Give the text encoder its own strength", () => {
          r.strength_clip = r.strength;
          change();
        });
        link.style.fontWeight = "400";
        l1.append(link);
      } else {
        const clipIn = numInput(r.strength_clip, (v, redraw = true) => {
          r.strength_clip = v;
          change(redraw);
        }, "Strength for the text encoder (clip).");
        const same = small("clip", "Back to the same strength as the model", () => {
          r.strength_clip = null;
          change();
        });
        l1.append(same, clipIn);
      }

      const trig = el("input", "flex:1;min-width:0;box-sizing:border-box;padding:3px 6px;border-radius:5px;border:1px solid " + tk("surface_4") +
        ";background:" + tk("surface") + ";color:" + tk("white") + ";font:12px " + FONT);
      trig.type = "text";
      trig.placeholder = "words to add to the prompt";
      trig.value = r.triggers;
      stopKeys(trig);
      trig.oninput = () => {
        r.triggers = trig.value;
        save();
      };
      const fill = small("Fill trigger words", "Read the training tags from the file and choose which to add", () => {
        if (!r.name) return;
        fillTriggers(r, r.name, (words) => {
          r.triggers = mergeWords(r.triggers, words);
          change();
        });
      });
      const up = small("up", "Move this row up", () => {
        if (i > 0) {
          [rows[i - 1], rows[i]] = [rows[i], rows[i - 1]];
          change();
        }
      });
      const down = small("down", "Move this row down", () => {
        if (i < rows.length - 1) {
          [rows[i + 1], rows[i]] = [rows[i], rows[i + 1]];
          change();
        }
      });
      const del = small("X", "Delete this row", () => {
        rows.splice(i, 1);
        change();
        resize();
      });
      l2.append(trig, fill, up, down, del);
      line.append(l1, l2);
      body.append(line);
    });
    resize();
  }

  function renderHead() {
    head.textContent = "";
    const master = button("", "on", "Master switch. Off passes the model and clip on unchanged.");
    const paintMaster = () => {
      const on = onW ? !!onW.value : true;
      master.textContent = on ? "LoRAs on" : "LoRAs off";
      master.style.background = on ? tk("gold") : tk("surface_3");
      master.style.color = on ? tk("void") : tk("white");
    };
    master.onclick = () => {
      if (onW) onW.value = !onW.value;
      paintMaster();
      node.setDirtyCanvas?.(true, true);
    };
    paintMaster();
    const add = button("+ Add LoRA", "gold", "Add a row");
    add.onclick = () => {
      if (rows.length >= MAX_ROWS) return;
      rows.push(cleanRow({}));
      change();
      pickLora("", (n) => {
        rows[rows.length - 1].name = n;
        change();
      });
    };
    const allOn = button("All on", "ghost", "Switch every row on");
    allOn.onclick = () => {
      rows.forEach((r) => (r.on = true));
      change();
    };
    const allOff = button("All off", "ghost", "Switch every row off");
    allOff.onclick = () => {
      rows.forEach((r) => (r.on = false));
      change();
    };
    head.append(master, add, allOn, allOff);
  }

  const domW = node.addDOMWidget("sy_power_lora_rows", "sy_power_lora", root, {
    serialize: false,
    hideOnZoom: false,
    getMinHeight: () => height(),
  });
  domW.computeSize = (w) => [w, height()];

  renderHead();
  render();
  loraList(false).then((list) => {
    available = list;
    render();
  });

  // called after a saved workflow was loaded into the node
  node._syPowerLoraReload = () => {
    rows = parseRows(rawW.value);
    renderHead();
    render();
  };
  return root;
}

app.registerExtension({
  name: "sy.power_lora",
  async setup() {
    try {
      await loadTheme();
    } catch (_) {
      /* the colours fall back to transparent; the node still works */
    }
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== NODE_TYPE) return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        buildEditor(this);
      } catch (e) {
        console.warn("[SY] Power Lora Loader editor could not start:", e);
      }
      return r;
    };
    const configure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configure ? configure.apply(this, arguments) : undefined;
      try {
        this._syPowerLoraReload?.();
      } catch (e) {
        console.warn("[SY] Power Lora Loader could not read the saved rows:", e);
      }
      return r;
    };
  },
});
