// SY Nodes by Stable Yogi: a small status dot in the title bar of every SY node.
// Gold = ready, yellow = a needed input has no link, green = ran fine, red = the last run stopped here.
// Switch off with the setting "SY.StatusBadge".
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { pal, getTheme, setting } from "./sy_core.js";

const state = new Map(); // node id -> "ok" | "error"

function isSy(node) {
  return (node.comfyClass || node.type || "").startsWith("SY") && !node.isVirtualNode;
}

function missingInputs(node) {
  const out = [];
  for (const inp of node.inputs || []) {
    if (inp.widget) continue; // a value box, not a link
    if (inp.link == null && !inp.shape /* optional inputs have a shape */) out.push(inp.name);
  }
  return out;
}

function status(node) {
  const miss = missingInputs(node);
  const key = String(node.id);
  if (state.get(key) === "error") return { kind: "error", tip: "The last run stopped at this node." };
  if (miss.length) return { kind: "warn", tip: "Needs a link: " + miss.join(", ") };
  if (state.get(key) === "ok") return { kind: "ok", tip: "Ran fine." };
  return { kind: "ready", tip: "Ready." };
}

function colour(kind) {
  const t = getTheme().tokens || {};
  const P = pal();
  if (kind === "ok") return t.green || P.gold;
  if (kind === "warn") return t.yellow || P.gold_dim;
  if (kind === "error") return t.red_soft || P.text;
  return P.gold_dim;
}

app.registerExtension({
  name: "sy.badge",
  settings: [
    {
      id: "SY.StatusBadge",
      name: "SY nodes: show a status dot in the node title",
      type: "boolean",
      defaultValue: true,
      tooltip: "Gold ready, yellow missing link, green ran fine, red stopped. Off hides the dot.",
    },
  ],
  async setup() {
    api.addEventListener("execution_start", () => {
      state.clear();
      app.canvas?.setDirty(true, true);
    });
    // Node ids are text in newer ComfyUI ("3", or "12:3" inside a subgraph), so keys are always text.
    api.addEventListener("executed", (e) => {
      if (e.detail?.node != null) state.set(String(e.detail.node), "ok");
      app.canvas?.setDirty(true, true);
    });
    api.addEventListener("execution_cached", (e) => {
      for (const id of e.detail?.nodes || []) if (!state.has(String(id))) state.set(String(id), "ok");
      app.canvas?.setDirty(true, true);
    });
    api.addEventListener("execution_error", (e) => {
      if (e.detail?.node_id != null) state.set(String(e.detail.node_id), "error");
      app.canvas?.setDirty(true, true);
    });
  },
  async nodeCreated(node) {
    if (!isSy(node)) return;
    const prev = node.onDrawForeground;
    node.onDrawForeground = function (ctx) {
      if (prev) prev.apply(this, arguments);
      if (!setting("SY.StatusBadge", true)) return;
      try {
        const s = status(this);
        this._syBadgeTip = s.tip;
        const th = window.LiteGraph?.NODE_TITLE_HEIGHT || 30;
        ctx.save();
        ctx.fillStyle = colour(s.kind);
        ctx.beginPath();
        ctx.arc(this.size[0] - 14, -th / 2, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      } catch (_) {
        /* drawing must never break the canvas */
      }
    };
  },
});
