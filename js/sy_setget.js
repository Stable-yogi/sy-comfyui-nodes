// SY Nodes by Stable Yogi: Set SY / Get SY. A wireless link: put a value in a Set node, read it anywhere with a Get node.
// Both are "virtual": they never reach the server. The Get node hands ComfyUI the link that feeds its Set node.
// Wires helpers: double-click a Get to jump to its Set, a Set shows how many Gets read it, red marks a missing or doubled name,
// and the right-click menu can make a Get for a Set.
import { app } from "../../scripts/app.js";
import { pal } from "./sy_core.js";
import { tk } from "./sy_ui_kit.js";
import { cleanName, duplicateNames, isMissing, setTitle, getTitle, countGets } from "./sy_setget_logic.js";

const SET_TYPE = "SYSetVar";
const GET_TYPE = "SYGetVar";

function allSets(graph) {
  return (graph?._nodes || []).filter((n) => n.type === SET_TYPE);
}

function allGets(graph) {
  return (graph?._nodes || []).filter((n) => n.type === GET_TYPE);
}

function setNames(graph) {
  const names = allSets(graph).map((n) => cleanName(n.widgets?.[0]?.value)).filter(Boolean);
  return [...new Set(names)].sort();
}

function findSet(graph, name) {
  const want = cleanName(name);
  if (!want) return null;
  return allSets(graph).find((n) => cleanName(n.widgets?.[0]?.value) === want) || null;
}

// Move the view to a node and select it. Quiet when the canvas is not there.
function jumpTo(node) {
  const canvas = app.canvas;
  if (!canvas || !node) return false;
  try {
    if (typeof canvas.centerOnNode === "function") canvas.centerOnNode(node);
    canvas.deselectAll?.();
    canvas.selectNode ? canvas.selectNode(node) : canvas.select?.(node);
    canvas.setDirty?.(true, true);
    return true;
  } catch (e) {
    console.warn("[SY] set/get jump failed", e);
    return false;
  }
}

function register() {
  const LG = window.LiteGraph;
  if (!LG || LG.registered_node_types?.[SET_TYPE]) return;

  class SySetNode extends LG.LGraphNode {
    constructor() {
      super("Set SY");
      this.isVirtualNode = true;
      this.addInput("value", "*");
      this.addWidget("text", "name", "", () => this.setDirtyCanvas(true, true));
      this.serialize_widgets = true;
      this.size = [210, 58];
    }
    onDrawForeground() {
      const name = cleanName(this.widgets[0].value);
      const dup = !!name && duplicateNames(allSets(this.graph).map((n) => n.widgets?.[0]?.value)).includes(name);
      const reads = countGets(allGets(this.graph).map((n) => n.widgets?.[0]?.value))[name] || 0;
      this.title = setTitle(name, reads, dup);
      if (dup) this.boxcolor = tk("red_soft");
      else if (!this.inputs?.[0]?.link) this.boxcolor = pal().gold_dim;
      else this.boxcolor = undefined;
    }
    onDblClick() {
      const name = cleanName(this.widgets[0].value);
      const first = allGets(this.graph).find((n) => cleanName(n.widgets?.[0]?.value) === name);
      if (first) jumpTo(first);
    }
    getExtraMenuOptions(_canvas, options) {
      const name = cleanName(this.widgets[0].value);
      if (!name) return;
      options.unshift({
        content: "Make a Get SY for this name",
        callback: () => {
          const get = LG.createNode(GET_TYPE);
          if (!get) return;
          get.pos = [this.pos[0] + this.size[0] + 40, this.pos[1]];
          this.graph.add(get);
          get.widgets[0].value = name;
          this.graph.setDirtyCanvas(true, true);
        },
      });
    }
  }
  SySetNode.title = "Set SY";
  SySetNode.category = "SY/Utility";

  class SyGetNode extends LG.LGraphNode {
    constructor() {
      super("Get SY");
      this.isVirtualNode = true;
      this.addOutput("value", "*");
      this.addWidget("combo", "name", "", () => this.setDirtyCanvas(true, true), {
        values: () => setNames(this.graph),
      });
      this.serialize_widgets = true;
      this.size = [210, 58];
    }
    onDrawForeground() {
      const name = cleanName(this.widgets[0].value);
      const missing = !!name && isMissing(name, setNames(this.graph));
      this.title = getTitle(name, missing);
      this.boxcolor = missing ? tk("red_soft") : undefined;
    }
    onDblClick() {
      const set = findSet(this.graph, this.widgets[0].value);
      if (set) jumpTo(set);
    }
    getExtraMenuOptions(_canvas, options) {
      const set = findSet(this.graph, this.widgets[0].value);
      if (set) options.unshift({ content: "Go to the Set SY", callback: () => jumpTo(set) });
    }
    // ComfyUI walks through virtual nodes with this call, the same way it does for Reroute.
    getInputLink() {
      const set = findSet(this.graph, this.widgets[0].value);
      const id = set?.inputs?.[0]?.link;
      return id == null ? null : this.graph.links[id];
    }
    getInputNode() {
      const link = this.getInputLink();
      return link ? this.graph.getNodeById(link.origin_id) : null;
    }
  }
  SyGetNode.title = "Get SY";
  SyGetNode.category = "SY/Utility";

  LG.registerNodeType(SET_TYPE, SySetNode);
  LG.registerNodeType(GET_TYPE, SyGetNode);
}

app.registerExtension({
  name: "sy.setget",
  async setup() {
    register();
  },
  async nodeCreated(node) {
    if (node.type === SET_TYPE || node.type === GET_TYPE) node.isVirtualNode = true;
  },
});
