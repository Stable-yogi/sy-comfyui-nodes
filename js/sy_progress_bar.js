// SY Nodes by Stable Yogi: Progress Bar SY (browser part). A bar at the top or bottom of the screen while a workflow runs.
// It listens to the run messages ComfyUI already sends; it changes nothing in the run. Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue } from "./sy_ui_kit.js";
import { overallPercent, barText, positionStyle } from "./sy_progress_bar_logic.js";

const TYPE = "SYProgressBar";
const FONT = "'DM Sans', sans-serif";
const HIDE_AFTER_MS = 6000;

const run = { state: "idle", total: 0, finished: 0, subValue: 0, subMax: 0, node: "", nodeId: null, t0: 0 };
let box = null;
let fill = null;
let label = null;
let tick = null;
let hideTimer = null;
let wired = false;

function barNode() {
  return (app.graph?._nodes ?? []).find((n) => n.type === TYPE && n.mode === 0 && widgetValue(n, "enabled", true) !== false) || null;
}

function titleOf(id) {
  const g = app.graph;
  const n = g?.getNodeById ? g.getNodeById(Number.isNaN(Number(id)) ? id : Number(id)) : null;
  return n ? n.title || n.type : String(id);
}

function ensureBox() {
  if (box && box.isConnected) return;
  box = document.createElement("div");
  box.style.cssText = "position:fixed;left:0;right:0;z-index:99990;pointer-events:none;height:30px;box-sizing:border-box;display:none;background:" +
    tk("abyss") + ";border-bottom:1px solid " + tk("gold_dim") + ";font:700 13px " + FONT + ";color:" + tk("white");
  fill = document.createElement("div");
  fill.style.cssText = "position:absolute;left:0;top:0;bottom:0;width:0;background:" + tk("gold_dim") + ";transition:width .25s ease";
  label = document.createElement("div");
  label.style.cssText = "position:relative;height:100%;display:flex;align-items:center;justify-content:center;white-space:nowrap;overflow:hidden;padding:0 12px";
  box.append(fill, label);
  document.body.append(box);
}

function paint() {
  const bar = barNode();
  if (!bar) {
    if (box) box.style.display = "none";
    return;
  }
  ensureBox();
  const pos = positionStyle(widgetValue(bar, "position", "top"));
  box.style.top = pos === "top" ? "0" : "auto";
  box.style.bottom = pos === "bottom" ? "0" : "auto";
  box.style.borderBottom = pos === "top" ? "1px solid " + tk("gold_dim") : "0";
  box.style.borderTop = pos === "bottom" ? "1px solid " + tk("gold_dim") : "0";
  const done = run.state === "done";
  const percent = overallPercent(run.total, run.finished, run.subValue, run.subMax, done);
  fill.style.width = (run.state === "idle" ? 0 : percent) + "%";
  fill.style.background = run.state === "error" ? tk("red_soft") : done ? tk("green_btn") : tk("gold_dim");
  label.textContent = barText({
    state: run.state === "idle" ? "running" : run.state,
    percent,
    subValue: run.subValue,
    subMax: run.subMax,
    node: run.node,
    elapsedMs: Date.now() - run.t0,
    showStep: widgetValue(bar, "show_step", true) !== false,
    showNode: widgetValue(bar, "show_node", true) !== false,
    showTime: widgetValue(bar, "show_time", true) !== false,
  });
  box.style.display = run.state === "idle" ? "none" : "block";
}

function startTick() {
  if (tick) return;
  tick = setInterval(() => {
    try {
      paint();
    } catch (e) {
      console.warn("[SY] progress bar paint failed", e);
    }
  }, 250);
}

function stopTick() {
  if (tick) clearInterval(tick);
  tick = null;
}

// How many nodes will run: every normal node that is switched on. Cached ones are counted as finished when ComfyUI says so.
function countNodes() {
  const list = app.graph?._nodes ?? [];
  return list.filter((n) => n.mode === 0 && !n.isVirtualNode && n.type !== TYPE).length;
}

function finish(state) {
  if (run.state === "idle") return;
  run.state = state;
  run.node = "";
  stopTick();
  paint();
  if (hideTimer) clearTimeout(hideTimer);
  hideTimer = setTimeout(() => {
    run.state = "idle";
    paint();
  }, HIDE_AFTER_MS);
}

function wire() {
  if (wired) return;
  wired = true;
  const on = (name, fn) =>
    api.addEventListener(name, (e) => {
      try {
        fn(e.detail);
      } catch (err) {
        console.warn("[SY] progress bar", name, err);
      }
    });
  on("execution_start", () => {
    if (hideTimer) clearTimeout(hideTimer);
    Object.assign(run, { state: "running", total: countNodes(), finished: 0, subValue: 0, subMax: 0, node: "", nodeId: null, t0: Date.now() });
    startTick();
    paint();
  });
  on("execution_cached", (d) => {
    run.finished += (d?.nodes || []).length;
  });
  on("executing", (d) => {
    const id = d && typeof d === "object" ? d.node : d;
    if (id == null) return;
    if (run.nodeId !== null && String(run.nodeId) !== String(id)) run.finished += 1;
    run.nodeId = id;
    run.subValue = 0;
    run.subMax = 0;
    run.node = titleOf(id);
  });
  on("progress", (d) => {
    run.subValue = Number(d?.value) || 0;
    run.subMax = Number(d?.max) || 0;
  });
  on("execution_success", () => finish("done"));
  on("execution_error", () => finish("error"));
  on("execution_interrupted", () => finish("stopped"));
}

app.registerExtension({
  name: "sy.progress_bar",
  async setup() {
    await loadTheme();
    wire();
  },
});
