// SY Nodes by Stable Yogi: Stacking Keeper SY. Keeps the front-to-back stacking of the nodes across save and open.
// ComfyUI draws nodes in an order it does not save, so a raised node (a Set or Get node, say) falls back behind others on open.
// While a Stacking Keeper SY is in the workflow, every raise or lowering of a node is noted, the list (back to front) is kept in the
// node and saved with the workflow, and it is put back when the workflow opens. Rules: sy_stacking_keeper_logic.js.
// Tested on frontend 1.57.4: the canvas has bringToFront and sendToBack, and the order it draws is canvas.visible_nodes.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue, hideWidget } from "./sy_ui_kit.js";
import { parseOrder, mergeOrder, raiseToFront, sendToBack, startOrder } from "./sy_stacking_keeper_logic.js";

const FONT = "'DM Sans', sans-serif";
const TYPE = "SYStackingKeeper";
const lists = new WeakMap(); // graph -> ids back to front

function keepersOf(graph) {
  return (graph?._nodes ?? []).filter((n) => n.type === TYPE);
}

function idsOf(graph) {
  return (graph?._nodes ?? []).filter((n) => n.type !== TYPE).map((n) => String(n.id));
}

// The current stacking of a graph, always complete and without nodes that are gone.
function currentOrder(graph) {
  const ids = idsOf(graph);
  let list = lists.get(graph);
  if (!list) {
    const keeper = keepersOf(graph)[0];
    const saved = keeper ? parseOrder(widgetValue(keeper, "order", "[]")) : [];
    if (saved.length) list = mergeOrder(saved, ids);
    else {
      const visible = (app.canvas?.visible_nodes ?? []).map((n) => String(n.id));
      list = startOrder(ids, visible);
    }
  }
  list = mergeOrder(list, ids);
  lists.set(graph, list);
  return list;
}

function store(graph) {
  const text = JSON.stringify(currentOrder(graph));
  for (const k of keepersOf(graph)) {
    const w = k.widgets?.find((x) => x.name === "order");
    if (w && w.value !== text) w.value = text;
    k._syKeeper?.refresh();
  }
}

// Puts the saved stacking back: every node is raised in saved order, the last one ends on top.
export function restore(graph) {
  const canvas = app.canvas;
  const keeper = keepersOf(graph)[0];
  if (!canvas || !keeper) return 0;
  const order = mergeOrder(parseOrder(widgetValue(keeper, "order", "[]")), idsOf(graph));
  lists.set(graph, order);
  const byId = new Map((graph._nodes ?? []).map((n) => [String(n.id), n]));
  const was = canvas.__syKeeperBusy;
  canvas.__syKeeperBusy = true; // the raises below are not new user actions
  let n = 0;
  try {
    for (const id of order) {
      const node = byId.get(id);
      if (!node) continue;
      canvas.bringToFront(node);
      n++;
    }
  } finally {
    canvas.__syKeeperBusy = was;
  }
  graph.setDirtyCanvas?.(true, true);
  store(graph);
  return n;
}

let hooked = false;
function hookCanvas() {
  const canvas = app.canvas;
  if (hooked || !canvas) return;
  const proto = Object.getPrototypeOf(canvas);
  if (typeof proto.bringToFront !== "function" || typeof proto.sendToBack !== "function") return;
  hooked = true;
  // a graph that is shown later (a subgraph that is opened, or the main graph when you come back): its keeper puts the stacking back
  const origSet = proto.setGraph;
  if (typeof origSet === "function") {
    proto.setGraph = function (graph) {
      const r = origSet.apply(this, arguments);
      try {
        if (graph && !app.configuringGraph && keepersOf(graph).length) {
          const keeper = keepersOf(graph)[0];
          if (widgetValue(keeper, "restore_on_open", true)) setTimeout(() => restore(graph), 50);
        }
      } catch (e) {
        console.warn("[SY] stacking keeper could not handle a subgraph", e);
      }
      return r;
    };
  }
  for (const [name, move] of [["bringToFront", raiseToFront], ["sendToBack", sendToBack]]) {
    const orig = proto[name];
    proto[name] = function (node) {
      const r = orig.apply(this, arguments);
      try {
        const graph = this.graph;
        if (!this.__syKeeperBusy && graph && node && node.id != null && keepersOf(graph).length) {
          lists.set(graph, move(currentOrder(graph), String(node.id)));
          store(graph);
        }
      } catch (e) {
        console.warn("[SY] stacking keeper could not note a move", e);
      }
      return r;
    };
  }
}

function setup(node) {
  const wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-direction:column;gap:6px;width:100%;box-sizing:border-box;padding:2px;font:12px " + FONT + ";color:" + tk("white");
  const status = document.createElement("div");
  status.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2");
  const btn = document.createElement("button");
  btn.textContent = "Put the stacking back now";
  btn.title = "Raises every node again in the saved order.";
  btn.style.cssText = "cursor:pointer;font:600 11px " + FONT + ";padding:4px 8px;border-radius:6px;border:1px solid " + tk("gold_dim") + ";background:transparent;color:" + tk("white");
  btn.addEventListener("click", () => {
    if (node.graph) restore(node.graph);
  });
  wrap.append(status, btn);
  hideWidget(node.widgets?.find((x) => x.name === "order"));
  const refresh = () => {
    const n = node.graph ? idsOf(node.graph).length : 0;
    status.textContent = "Keeping the stacking of " + n + " node" + (n === 1 ? "" : "s") + ".";
  };
  const w = node.addDOMWidget("sy_stacking_keeper_panel", "custom", wrap, { serialize: false });
  w.computeSize = (width) => [width, 56];
  node._syKeeper = { refresh };
  refresh();
}

app.registerExtension({
  name: "sy.stacking_keeper",
  async setup() {
    hookCanvas();
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] stacking keeper panel not added", e);
      }
      return r;
    };
    // a node added by hand: start the list from what is on screen. A node that comes with an opened workflow has no graph yet.
    const added = nodeType.prototype.onAdded;
    nodeType.prototype.onAdded = function (graph) {
      const r = added ? added.apply(this, arguments) : undefined;
      try {
        hookCanvas();
        const g = graph ?? this.graph;
        if (g && !app.configuringGraph) store(g);
      } catch (e) {
        console.warn("[SY] stacking keeper could not start", e);
      }
      return r;
    };
  },
  // a workflow has just opened: put the saved stacking back
  afterConfigureGraph() {
    hookCanvas();
    const graph = app.graph;
    const keeper = keepersOf(graph)[0];
    if (!keeper) return;
    if (!widgetValue(keeper, "restore_on_open", true)) {
      lists.delete(graph);
      return;
    }
    try {
      restore(graph);
    } catch (e) {
      console.warn("[SY] stacking keeper could not put the stacking back", e);
    }
  },
});
