// SY Nodes by Stable Yogi: Random Unmuter SY. Before every run it switches ON one node of a set (nodes whose title holds one of your words)
// and switches the others OFF (mute or bypass). The rules are in sy_random_unmuter_logic.js and match nodes/sy_random_unmuter.py.
// The node runs nothing on the server, so a workflow still runs without this file (all nodes then keep the state you left them in).
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue } from "./sy_ui_kit.js";
import { matchTitles, pickIndex, planModes } from "./sy_random_unmuter_logic.js";

const TYPE = "SYRandomUnmuter";
const FONT = "'DM Sans', sans-serif";
let hooked = false;

function unmuters(graph) {
  return (graph?._nodes ?? []).filter((n) => n.type === TYPE);
}

// Switch one node set. Returns {count, chosen} where chosen is the title that is now on, or null when nothing was switched.
export function applyOne(graph, unmuter) {
  if (widgetValue(unmuter, "enabled", true) === false) return null;
  const candidates = (graph._nodes ?? []).filter((n) => n.type !== TYPE);
  const hits = matchTitles(candidates.map((n) => n.title || n.type), widgetValue(unmuter, "title_filter", ""));
  if (!hits.length) return { count: 0, chosen: null };
  const props = (unmuter.properties = unmuter.properties || {});
  const counter = Number(props.sy_counter) || 0;
  const idx = pickIndex(hits.length, widgetValue(unmuter, "pick", "random"), Number(widgetValue(unmuter, "seed", 0)) || 0, counter, Math.random());
  const modes = planModes(hits.length, idx, widgetValue(unmuter, "off_mode", "Mute"));
  hits.forEach((h, i) => { candidates[h].mode = modes[i]; });
  props.sy_counter = counter + 1;
  const chosen = candidates[hits[idx]];
  props.sy_last = chosen.title || chosen.type;
  return { count: hits.length, chosen: props.sy_last };
}

function applyAll(graph) {
  for (const u of unmuters(graph)) {
    try {
      applyOne(graph, u);
    } catch (e) {
      console.warn("[SY] random unmuter failed", e);
    }
  }
}

// graphToPrompt is what builds the job from the graph, so the switching happens right before it, on every run.
function hook() {
  if (hooked) return;
  hooked = true;
  const original = app.graphToPrompt;
  if (typeof original !== "function") {
    console.warn("[SY] random unmuter: graphToPrompt not found, the node will not switch anything");
    return;
  }
  app.graphToPrompt = function (...args) {
    try {
      applyAll(app.graph);
    } catch (e) {
      console.warn("[SY] random unmuter", e);
    }
    return original.apply(this, args);
  };
}

function setup(node) {
  const status = document.createElement("div");
  status.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2") + ";padding:2px 4px;box-sizing:border-box;width:100%";
  const refresh = () => {
    const g = node.graph;
    if (!g) return;
    const candidates = (g._nodes ?? []).filter((n) => n.type !== TYPE);
    const hits = matchTitles(candidates.map((n) => n.title || n.type), widgetValue(node, "title_filter", ""));
    const last = node.properties?.sy_last;
    status.textContent = (hits.length ? hits.length + " node(s) in the set." : "No node title matches yet.") + (last ? " Last run used: " + last : "");
  };
  const w = node.addDOMWidget("sy_unmuter_status", "custom", status, { serialize: false });
  w.computeSize = (width) => [width, 34];
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syUnmSeen) clearInterval(tick);
      return;
    }
    node._syUnmSeen = true;
    try {
      refresh();
    } catch (e) {
      console.warn("[SY] random unmuter status failed", e);
    }
  }, 700);
  refresh();
}

app.registerExtension({
  name: "sy.random_unmuter",
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
        console.warn("[SY] random unmuter panel not added", e);
      }
      return r;
    };
  },
});
