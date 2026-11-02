// SY Nodes by Stable Yogi: Global Seed SY (browser part). Before a job is built, the seed in this node is written into every other
// seed box in the graph. After the job is sent, the node moves on to the next seed by its mode (like "control after generate").
// Nothing here runs on the server: the job simply carries the seeds. Rules are in sy_global_seed_logic.js.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue, setWidget } from "./sy_ui_kit.js";
import { isSeedName, clampSeed, nextSeed, fitSeed, parseWords, skipByTitle, summary } from "./sy_global_seed_logic.js";

const TYPE = "SYGlobalSeed";
const FONT = "'DM Sans', sans-serif";
let hooked = false;

function globals(graph) {
  return (graph?._nodes ?? []).filter((n) => n.type === TYPE && n.mode === 0);
}

// Does a link feed this widget? Then the box is not ours to write.
function isLinked(node, widget) {
  const inp = (node.inputs || []).find((i) => i.widget?.name === widget.name);
  return !!(inp && inp.link != null);
}

// Write the seed into every other seed box. Returns how many boxes were set.
export function applySeed(graph, master) {
  if (widgetValue(master, "apply_to_all", true) === false) return 0;
  const seed = clampSeed(widgetValue(master, "seed", 0));
  const words = parseWords(widgetValue(master, "skip_titles", ""));
  let count = 0;
  for (const n of graph._nodes ?? []) {
    if (n === master || n.type === TYPE || n.mode === 2 || n.mode === 4) continue;
    if (skipByTitle(n.title || n.type, words)) continue;
    for (const w of n.widgets ?? []) {
      if (!isSeedName(w.name) || typeof w.value !== "number" || isLinked(n, w)) continue;
      w.value = fitSeed(seed, w.options?.max);
      count++;
    }
  }
  master._syCount = count;
  if (count) graph.setDirtyCanvas?.(true, true);
  return count;
}

function beforeBuild() {
  const g = app.graph;
  for (const m of globals(g)) {
    try {
      applySeed(g, m);
    } catch (e) {
      console.warn("[SY] global seed failed", e);
    }
  }
}

// After a job went to the server, every Global Seed node moves on to the next seed.
function afterQueued() {
  for (const m of globals(app.graph)) {
    try {
      const next = nextSeed(widgetValue(m, "seed", 0), widgetValue(m, "mode", "fixed"), Math.random());
      setWidget(m, "seed", next);
    } catch (e) {
      console.warn("[SY] global seed could not move on", e);
    }
  }
}

function hook() {
  if (hooked) return;
  hooked = true;
  const build = app.graphToPrompt;
  if (typeof build === "function") {
    app.graphToPrompt = function (...args) {
      beforeBuild();
      return build.apply(this, args);
    };
  } else {
    console.warn("[SY] global seed: graphToPrompt not found, the node will not set any seed");
  }
  const send = api.queuePrompt;
  if (typeof send === "function") {
    api.queuePrompt = async function (...args) {
      const r = await send.apply(this, args);
      afterQueued();
      return r;
    };
  } else {
    console.warn("[SY] global seed: queuePrompt not found, the seed will not move on");
  }
}

function setup(node) {
  const status = document.createElement("div");
  status.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2") + ";padding:2px 4px;box-sizing:border-box;width:100%";
  status.textContent = "Sets every seed box when you run";
  const w = node.addDOMWidget("sy_global_seed_status", "custom", status, { serialize: false });
  w.computeSize = (width) => [width, 24];
  node._syStatus = () => {
    status.textContent = node._syCount === undefined ? "Sets every seed box when you run" : summary(node._syCount);
  };
  // The front end adds its own "control after generate" to every seed box. Ours has a mode, so switch the extra one off.
  const quiet = () => {
    const c = (node.widgets ?? []).find((x) => x.name === "control_after_generate");
    if (!c) return;
    c.value = "fixed";
    c.hidden = true;
    c.computeSize = () => [0, -4];
  };
  quiet();
  setTimeout(quiet, 0);
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._sySeen) clearInterval(tick);
      return;
    }
    node._sySeen = true;
    try {
      node._syStatus();
    } catch (e) {
      console.warn("[SY] global seed status failed", e);
    }
  }, 700);
}

app.registerExtension({
  name: "sy.global_seed",
  async setup() {
    hook();
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        hook();
        setup(this);
      } catch (e) {
        console.warn("[SY] global seed panel not added", e);
      }
      return r;
    };
  },
});
