// SY Nodes by Stable Yogi: Resource Monitor SY (browser part). Small live meters in a screen corner for CPU, RAM, GPU, VRAM and temperature.
// It reads GET /sy/resources only while a Resource Monitor node that is switched on is in the graph. Text is set with textContent.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue } from "./sy_ui_kit.js";
import { meterRows, cleanInterval, cornerCss } from "./sy_resource_monitor_logic.js";

const TYPE = "SYResourceMonitor";
const FONT = "'DM Sans', sans-serif";

let box = null;
let timer = null;
let busy = false;
let lastInterval = 0;

function monitorNode() {
  return (app.graph?._nodes ?? []).find((n) => n.type === TYPE && n.mode === 0 && widgetValue(n, "enabled", true) !== false) || null;
}

function ensureBox() {
  if (box && box.isConnected) return;
  box = document.createElement("div");
  box.style.cssText = "position:fixed;z-index:99989;pointer-events:none;min-width:190px;padding:6px 8px;box-sizing:border-box;border-radius:8px;" +
    "background:" + tk("abyss") + ";border:1px solid " + tk("gold_dim") + ";font:600 11px " + FONT + ";color:" + tk("text") + ";display:none";
  document.body.append(box);
}

function levelColour(level) {
  return level === "hot" ? tk("red_soft") : level === "warn" ? tk("yellow") : tk("green");
}

function draw(snap, node) {
  ensureBox();
  const css = cornerCss(widgetValue(node, "corner", "top right"));
  Object.assign(box.style, css);
  const rows = meterRows(snap);
  box.replaceChildren();
  for (const r of rows) {
    const line = document.createElement("div");
    line.style.cssText = "display:grid;grid-template-columns:44px 1fr auto;gap:6px;align-items:center;margin:2px 0";
    const name = document.createElement("span");
    name.textContent = r.label;
    name.style.color = tk("text_2");
    const track = document.createElement("span");
    track.style.cssText = "height:7px;border-radius:4px;background:" + tk("surface_3") + ";overflow:hidden;display:block";
    const bar = document.createElement("span");
    bar.style.cssText = "display:block;height:100%;width:" + Math.max(0, Math.min(100, r.percent)) + "%;background:" + levelColour(r.level) + ";transition:width .3s ease";
    track.append(bar);
    const val = document.createElement("span");
    val.textContent = r.text;
    val.style.cssText = "text-align:right;white-space:nowrap";
    line.append(name, track, val);
    box.append(line);
  }
  box.style.display = rows.length ? "block" : "none";
}

async function poll() {
  const node = monitorNode();
  if (!node) {
    if (box) box.style.display = "none";
    return;
  }
  if (busy) return;
  busy = true;
  try {
    const res = await api.fetchApi("/sy/resources");
    if (res.ok) draw(await res.json(), node);
  } catch (e) {
    console.warn("[SY] resource monitor read failed", e);
  } finally {
    busy = false;
  }
}

// One timer for the whole page. It is re-made when the interval box changes.
function schedule() {
  const node = monitorNode();
  const secs = cleanInterval(node ? widgetValue(node, "interval", 1) : 1);
  if (timer && secs === lastInterval) return;
  if (timer) clearInterval(timer);
  lastInterval = secs;
  timer = setInterval(() => {
    schedule();
    poll();
  }, secs * 1000);
}

app.registerExtension({
  name: "sy.resource_monitor",
  async setup() {
    await loadTheme();
    schedule();
    poll();
  },
});
