// SY Nodes by Stable Yogi: Set SY / Get SY. A wireless link: put a value in a Set node, read it anywhere with a Get node.
// Both are "virtual": they never reach the server. The Get node hands ComfyUI the link that feeds its Set node.
import { app } from "../../scripts/app.js";
import { pal } from "./sy_core.js";

const SET_TYPE = "SYSetVar";
const GET_TYPE = "SYGetVar";

function allSets(graph) {
  return (graph?._nodes || []).filter((n) => n.type === SET_TYPE);
}

function setNames(graph) {
  const names = allSets(graph).map((n) => String(n.widgets?.[0]?.value || "").trim()).filter(Boolean);
  return [...new Set(names)].sort();
}

function findSet(graph, name) {
  const want = String(name || "").trim();
  if (!want) return null;
  return allSets(graph).find((n) => String(n.widgets?.[0]?.value || "").trim() === want) || null;
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
      this.title = this.widgets[0].value ? "Set: " + this.widgets[0].value : "Set SY";
      if (!this.inputs?.[0]?.link) this.boxcolor = pal().gold_dim;
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
      this.title = this.widgets[0].value ? "Get: " + this.widgets[0].value : "Get SY";
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
