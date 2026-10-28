// SY Nodes by Stable Yogi: a help card that appears when you rest the mouse on the title of an SY node.
// It lists what the node does and what each input means. Off with the setting "SY.HelpCards".
import { app } from "../../scripts/app.js";
import { pal, setting, reducedMotion } from "./sy_core.js";

let card = null;
let timer = null;
let shownFor = null;

function hide() {
  clearTimeout(timer);
  timer = null;
  shownFor = null;
  if (card) card.style.display = "none";
}

function build(node) {
  const d = node.constructor?.nodeData;
  if (!d) return null;
  const P = pal();
  const wrap = document.createElement("div");
  const head = document.createElement("div");
  head.textContent = d.display_name || node.title;
  head.style.cssText = "font-weight:700;margin-bottom:4px;color:" + P.gold;
  wrap.append(head);
  if (d.description) {
    const p = document.createElement("div");
    p.textContent = d.description;
    p.style.marginBottom = "6px";
    wrap.append(p);
  }
  const groups = { ...(d.input?.required || {}), ...(d.input?.optional || {}) };
  for (const [name, spec] of Object.entries(groups)) {
    const tip = spec?.[1]?.tooltip;
    if (!tip) continue;
    const row = document.createElement("div");
    row.style.cssText = "margin-top:3px;color:" + P.muted;
    const b = document.createElement("b");
    b.textContent = name + ": ";
    b.style.color = P.text;
    row.append(b, document.createTextNode(tip));
    wrap.append(row);
  }
  return wrap;
}

function show(node, x, y) {
  const content = build(node);
  if (!content) return;
  const P = pal();
  if (!card) {
    card = document.createElement("div");
    card.setAttribute("role", "tooltip");
    document.body.append(card);
  }
  card.replaceChildren(content);
  card.style.cssText =
    "position:fixed;z-index:9999;max-width:340px;padding:10px 12px;border-radius:8px;pointer-events:none;" +
    "font:12px/1.4 'DM Sans',sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.35);background:" + P.abyss +
    ";color:" + P.text + ";border:1px solid " + P.gold_dim +
    (reducedMotion() ? "" : ";transition:opacity .15s");
  card.style.left = Math.min(x + 14, window.innerWidth - 360) + "px";
  card.style.top = Math.min(y + 14, window.innerHeight - 200) + "px";
  card.style.display = "block";
  shownFor = node.id;
}

function nodeUnderTitle() {
  const canvas = app.canvas;
  const pos = canvas?.graph_mouse;
  if (!canvas?.graph || !pos) return null;
  const th = window.LiteGraph?.NODE_TITLE_HEIGHT || 30;
  const nodes = canvas.graph._nodes || [];
  for (const n of nodes) {
    if (!(n.comfyClass || n.type || "").startsWith("SY")) continue;
    const inX = pos[0] >= n.pos[0] && pos[0] <= n.pos[0] + n.size[0];
    const inTitle = pos[1] >= n.pos[1] - th && pos[1] < n.pos[1];
    if (inX && inTitle) return n;
  }
  return null;
}

app.registerExtension({
  name: "sy.helpcards",
  settings: [
    {
      id: "SY.HelpCards",
      name: "SY nodes: show a help card when the mouse rests on a node title",
      type: "boolean",
      defaultValue: true,
      tooltip: "A small card with what the node does and what each input means. Off hides it.",
    },
  ],
  async setup() {
    const el = app.canvas?.canvas;
    if (!el) return;
    el.addEventListener("mousemove", (ev) => {
      if (!setting("SY.HelpCards", true)) return hide();
      const node = nodeUnderTitle(ev);
      if (!node) return hide();
      if (shownFor === node.id) return;
      clearTimeout(timer);
      timer = setTimeout(() => show(node, ev.clientX, ev.clientY), 550);
    });
    el.addEventListener("mouseleave", hide);
    el.addEventListener("mousedown", hide);
    el.addEventListener("wheel", hide, { passive: true });
  },
});
