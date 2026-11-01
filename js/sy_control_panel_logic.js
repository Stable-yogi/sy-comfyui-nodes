// SY Nodes by Stable Yogi: pure logic for Control Panel SY. No page code in here, so it can be tested with node.
// The same rules as nodes/sy_control_panel.py.
export const MAX_ROWS = 32;
export const KINDS = ["float", "int", "switch", "text", "dropdown", "seed"];
export const KIND_NAMES = { float: "Number", int: "Whole number", switch: "Switch", text: "Text", dropdown: "Dropdown", seed: "Seed" };
export const OUT_TYPES = { float: "FLOAT", int: "INT", seed: "INT", switch: "BOOLEAN", text: "STRING", dropdown: "COMBO,STRING" }; // a dropdown row also plugs into dropdown inputs
export const SEED_MODES = ["fixed", "random", "increment"];
export const MAX_SEED = Number.MAX_SAFE_INTEGER;

const num = (v) => (typeof v === "number" && Number.isFinite(v) ? v : null);

// One clean row from whatever was saved (a missing key gets its default; a wrong type is dropped).
export function cleanRow(r) {
  const src = r && typeof r === "object" ? r : {};
  const kind = KINDS.includes(src.kind) ? src.kind : "float";
  let value = src.value;
  if (kind === "switch") value = value === true;
  else if (kind === "text" || kind === "dropdown") value = typeof value === "string" ? value : "";
  else value = num(value) ?? 0;
  if (kind === "int" || kind === "seed") value = Math.round(value);
  const options = Array.isArray(src.options) ? src.options.filter((o) => typeof o === "string") : [];
  const mn = num(src.min);
  const mx = num(src.max);
  const step = num(src.step) > 0 ? src.step : null;
  return {
    name: typeof src.name === "string" ? src.name : "",
    kind,
    value,
    min: mn,
    max: mx !== null && mn !== null && mx < mn ? mn : mx,
    step,
    options,
    mode: SEED_MODES.includes(src.mode) ? src.mode : "fixed",
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

// The row name shown on the panel and on the output slot. A row without a name is called Row N.
export function rowLabel(row, index) {
  const n = String(row.name || "").trim();
  return n || "Row " + (index + 1);
}

// New row of a kind with sensible starting numbers.
export function newRow(kind, name = "") {
  const base = { name, kind, value: 0, min: null, max: null, step: null, options: [], mode: "fixed" };
  if (kind === "float") return { ...base, min: 0, max: 100, step: 0.01, value: 1 };
  if (kind === "int") return { ...base, min: 0, max: 100, step: 1, value: 1 };
  if (kind === "seed") return { ...base, value: 0 };
  if (kind === "text") return { ...base, value: "" };
  if (kind === "dropdown") return { ...base, options: ["option 1", "option 2"], value: "option 1" };
  if (kind === "switch") return { ...base, value: false };
  return base;
}

// Change the kind of a row and keep what still fits (a number stays a number, text stays text).
export function changeKind(row, kind) {
  const fresh = newRow(kind, row.name);
  if (["float", "int", "seed"].includes(kind) && ["float", "int", "seed"].includes(row.kind)) {
    fresh.value = kind === "float" ? row.value : Math.round(row.value);
    if (kind !== "seed") {
      fresh.min = row.min ?? fresh.min;
      fresh.max = row.max ?? fresh.max;
      fresh.step = kind === "int" ? Math.max(1, Math.round(row.step ?? 1)) : row.step ?? fresh.step;
    }
  } else if (["text", "dropdown"].includes(kind) && ["text", "dropdown"].includes(row.kind)) {
    fresh.value = row.value;
    if (kind === "dropdown" && !fresh.options.includes(fresh.value)) fresh.options = [fresh.value || "option 1", ...fresh.options.filter((o) => o !== fresh.value)].slice(0, 20);
    if (kind === "dropdown" && !fresh.value) fresh.value = fresh.options[0];
  }
  return fresh;
}

// How many decimals a step needs (0.01 -> 2, 1 -> 0, 0.25 -> 2).
export function decimalsOf(step) {
  const s = num(step);
  if (!s || s >= 1 && Number.isInteger(s)) return 0;
  const text = String(s);
  if (text.includes("e-")) return Math.min(10, parseInt(text.split("e-")[1], 10));
  return Math.min(10, (text.split(".")[1] || "").length);
}

// A typed number: never cut to the range. Whole-number kinds are rounded.
export function typedValue(row, text) {
  const x = Number(String(text).replace(",", "."));
  if (!Number.isFinite(x)) return null;
  if (row.kind === "int" || row.kind === "seed") {
    const r = Math.round(x);
    return row.kind === "seed" ? Math.max(0, r) : r;
  }
  return x;
}

// The slider only covers min..max (both must be set). A value outside the range pins the knob to the end.
export function sliderPosition(row) {
  if (row.min === null || row.max === null || row.max === row.min) return null;
  return Math.max(0, Math.min(1, (row.value - row.min) / (row.max - row.min)));
}

export function valueAtPosition(row, pos) {
  const raw = row.min + Math.max(0, Math.min(1, pos)) * (row.max - row.min);
  const step = row.kind === "int" ? Math.max(1, Math.round(row.step || 1)) : row.step || 0;
  const stepped = step ? row.min + Math.round((raw - row.min) / step) * step : raw;
  const d = decimalsOf(step || 0.01);
  return row.kind === "int" ? Math.round(stepped) : Number(stepped.toFixed(Math.max(d, 0)));
}

// The text of the dropdown list box -> the list (one entry per line, blanks and repeats dropped).
export function optionsFromText(text) {
  const seen = new Set();
  const out = [];
  for (const line of String(text || "").split(/\r?\n/)) {
    const t = line.trim();
    if (t && !seen.has(t)) {
      seen.add(t);
      out.push(t);
    }
  }
  return out.slice(0, 500);
}

// What kind of row a widget of another node becomes. widget = {type, value, options:{min,max,step,precision,round,values}}.
// Returns a row, or null when the widget cannot be moved into the panel.
export function rowFromWidget(widget, name) {
  const o = widget.options || {};
  const t = String(widget.type || "").toLowerCase();
  const wname = String(widget.name || "");
  if (t === "toggle" || t === "boolean") return { ...newRow("switch", name), value: widget.value === true };
  if (t === "combo") {
    const values = Array.isArray(o.values) ? o.values.filter((v) => typeof v === "string") : [];
    if (!values.length) return null;
    const value = typeof widget.value === "string" ? widget.value : values[0];
    return { ...newRow("dropdown", name), options: values.slice(0, 500), value };
  }
  if (t === "number" || t === "slider") {
    const v = num(widget.value) ?? 0;
    const whole = o.precision === 0 || o.round === 1 || (Number.isInteger(v) && o.precision === undefined && Number.isInteger(o.step2 ?? o.step ?? 1));
    if (/seed/i.test(wname) && whole) return { ...newRow("seed", name), value: Math.max(0, Math.round(v)) };
    const step = num(o.step2) || (num(o.step) ? o.step / 10 : null) || (whole ? 1 : 0.01);
    if (whole) return { ...newRow("int", name), value: Math.round(v), min: num(o.min), max: num(o.max), step: Math.max(1, Math.round(step)) };
    return { ...newRow("float", name), value: v, min: num(o.min), max: num(o.max), step };
  }
  if (t === "text" || t === "string" || t === "customtext") {
    return { ...newRow("text", name), value: typeof widget.value === "string" ? widget.value : "" };
  }
  return null;
}

// A name for a new row that is not used yet: "cfg", then "cfg 2", "cfg 3" ...
export function uniqueName(base, rows) {
  const used = new Set(rows.map((r) => r.name));
  const b = String(base || "").trim() || "Row";
  if (!used.has(b)) return b;
  for (let i = 2; i < 1000; i++) if (!used.has(b + " " + i)) return b + " " + i;
  return b;
}

// Move a row (and tell which two output slots swap places).
export function moveRow(rows, from, to) {
  if (from === to || from < 0 || to < 0 || from >= rows.length || to >= rows.length) return false;
  const [r] = rows.splice(from, 1);
  rows.splice(to, 0, r);
  return true;
}

// The seed rows' used numbers sent back by the server after a run: '{"0": 123}' -> {0: 123}.
export function parseSeeds(list) {
  const out = {};
  for (const item of Array.isArray(list) ? list : []) {
    try {
      const d = JSON.parse(item);
      for (const [k, v] of Object.entries(d)) if (Number.isFinite(Number(k)) && typeof v === "number") out[Number(k)] = v;
    } catch (_) {
      /* a bad answer from the server: leave the rows alone */
    }
  }
  return out;
}
