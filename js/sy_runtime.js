// SY Nodes by Stable Yogi: a time badge on each node ("1.2 s") and a run clock in the top right corner.
// Both only read the progress messages ComfyUI already sends. Switch them off in the settings "SY.TimeBadge" and "SY.RunClock".
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { tk } from "./sy_ui_kit.js";
import { setting } from "./sy_core.js";

const times = new Map(); // node id (text) -> seconds, or "cached"
let current = null; // { id, start }
let runStart = 0;
let lastTotal = null;
let ticker = 0;
let clock = null;

function now() {
  return performance.now() / 1000;
}

function fmt(sec) {
  if (sec < 10) return sec.toFixed(1) + " s";
  if (sec < 60) return Math.round(sec) + " s";
  return Math.floor(sec / 60) + " min " + String(Math.round(sec % 60)).padStart(2, "0") + " s";
}

function closeCurrent() {
  if (!current) return;
  times.set(current.id, now() - current.start);
  current = null;
}

function dirty() {
  app.canvas?.setDirty(true, true);
}

function makeClock() {
  if (clock) return clock;
  clock = document.createElement("div");
  clock.setAttribute("aria-live", "off");
  clock.style.cssText = "position:fixed;top:56px;right:16px;z-index:900;display:none;padding:4px 12px;border-radius:14px;" +
    "font:700 13px 'DM Sans',sans-serif;pointer-events:none;background:" + tk("void") + ";color:" + tk("gold") +
    ";border:1px solid " + tk("gold_dim");
  document.body.append(clock);
  return clock;
}

function paintClock() {
  if (!setting("SY.RunClock", true)) {
    if (clock) clock.style.display = "none";
    return;
  }
  const c = makeClock();
  if (runStart) {
    c.style.display = "block";
    c.textContent = "Running " + fmt(now() - runStart);
  } else if (lastTotal != null) {
    c.style.display = "block";
    c.textContent = "Last run " + fmt(lastTotal);
  } else {
    c.style.display = "none";
  }
}

function endRun() {
  closeCurrent();
  if (runStart) lastTotal = now() - runStart;
  runStart = 0;
  clearInterval(ticker);
  ticker = 0;
  paintClock();
  dirty();
}

function badgeText(node) {
  const id = String(node.id);
  const v = times.get(id);
  if (v === "cached") return "cached";
  if (typeof v === "number") return fmt(v);
  if (current && current.id === id) return fmt(now() - current.start);
  return "";
}

function wanted(node) {
  const mode = setting("SY.TimeBadge", "All nodes");
  if (mode === "Off") return false;
  if (mode === "SY nodes") return (node.comfyClass || node.type || "").startsWith("SY");
  return true;
}

app.registerExtension({
  name: "sy.runtime",
  settings: [
    {
      id: "SY.TimeBadge",
      name: "SY: show how long each node took",
      type: "combo",
      options: ["All nodes", "SY nodes", "Off"],
      defaultValue: "All nodes",
      tooltip: "A small time such as 1.2 s in the title of each node after a run.",
    },
    {
      id: "SY.RunClock",
      name: "SY: show a run clock in the top right corner",
      type: "boolean",
      defaultValue: true,
      tooltip: "Shows the time of the run that is going on, and the total time of the last run.",
    },
  ],
  async setup() {
    api.addEventListener("execution_start", () => {
      times.clear();
      current = null;
      runStart = now();
      clearInterval(ticker);
      ticker = setInterval(() => {
        paintClock();
        if (current) dirty();
      }, 250);
      paintClock();
    });
    api.addEventListener("execution_cached", (e) => {
      for (const id of e.detail?.nodes || []) times.set(String(id), "cached");
      dirty();
    });
    api.addEventListener("executing", (e) => {
      const d = e.detail;
      const id = d && typeof d === "object" ? d.node : d;
      closeCurrent();
      if (id == null) return endRun();
      current = { id: String(id), start: now() };
      dirty();
    });
    for (const name of ["execution_success", "execution_error", "execution_interrupted"]) {
      api.addEventListener(name, () => {
        if (runStart) endRun();
      });
    }
  },
  async nodeCreated(node) {
    const prev = node.onDrawForeground;
    node.onDrawForeground = function (ctx) {
      if (prev) prev.apply(this, arguments);
      try {
        if (!wanted(this)) return;
        const text = badgeText(this);
        if (!text) return;
        const th = window.LiteGraph?.NODE_TITLE_HEIGHT || 30;
        ctx.save();
        ctx.font = "600 11px 'DM Sans', sans-serif";
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        const w = ctx.measureText(text).width + 12;
        const x = this.size[0] - 28; // left of the status dot
        ctx.fillStyle = tk("void");
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(x - w, -th / 2 - 8, w, 16, 8);
        else ctx.rect(x - w, -th / 2 - 8, w, 16);
        ctx.fill();
        ctx.fillStyle = text === "cached" ? tk("text_2") : tk("gold_light");
        ctx.fillText(text, x - 6, -th / 2 + 1);
        ctx.restore();
      } catch (_) {
        /* drawing must never break the canvas */
      }
    };
  },
});
