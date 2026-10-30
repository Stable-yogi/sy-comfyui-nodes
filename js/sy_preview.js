// SY Nodes by Stable Yogi: result preview. After a run, a small picture or text of what the node made shows on the node.
// The data comes from nodes/_sy_preview.py (the "ui" part of the run). Nothing is added to a saved workflow.
// Text is always set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme, pal, setting } from "./sy_core.js";

const SETTING = "SY.ResultPreview";
const FONT = "'DM Sans', sans-serif";
const IMG_H = 190;

function viewUrl(f) {
  return api.apiURL("/view?filename=" + encodeURIComponent(f.filename) + "&type=" + (f.type || "temp") +
    "&subfolder=" + encodeURIComponent(f.subfolder || ""));
}

function small(text, tip) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = text;
  if (tip) b.title = tip;
  const P = pal();
  b.style.cssText = "cursor:pointer;border-radius:5px;border:1px solid " + P.gold_dim + ";background:transparent;color:inherit;padding:1px 7px;font:600 11px " + FONT;
  return b;
}

function build(node) {
  const P = pal();
  const box = document.createElement("div");
  box.style.cssText = "display:flex;flex-direction:column;gap:4px;width:100%;box-sizing:border-box;padding:2px;font:12px " + FONT + ";color:" + P.text;
  const bar = document.createElement("div");
  bar.style.cssText = "display:flex;gap:5px;align-items:center;flex-wrap:wrap";
  const info = document.createElement("span");
  info.style.cssText = "flex:1;min-width:60px;font:600 11px " + FONT + ";color:" + P.gold;
  const hold = small("Hold: before", "Press and hold to see the picture before this node changed it.");
  const copy = small("Copy text", "Copy the result text to the clipboard.");
  const hide = small("Hide", "Hide or show this result.");
  bar.append(info, hold, copy, hide);
  const imgs = document.createElement("div");
  imgs.style.cssText = "display:flex;gap:4px;justify-content:center;height:" + IMG_H + "px";
  const texts = document.createElement("div");
  texts.style.cssText = "display:flex;flex-direction:column;gap:3px";
  box.append(bar, imgs, texts);

  const st = { box, info, hold, copy, hide, imgs, texts, files: [], items: [], showBefore: false, hidden: false, widget: null };
  const draw = () => {
    imgs.textContent = "";
    const role = st.showBefore ? "before" : "after";
    const list = st.files.filter((f) => f.role === role);
    for (const f of list) {
      const im = document.createElement("img");
      im.alt = role === "before" ? "Picture before this node" : "Result of this node";
      im.src = viewUrl(f);
      im.style.cssText = "flex:1 1 0;min-width:0;max-height:100%;object-fit:contain;border-radius:5px;background:" + P.surface;
      imgs.append(im);
    }
    hold.textContent = st.showBefore ? "Before" : "Hold: before";
    hold.style.background = st.showBefore ? P.gold : "transparent";
    hold.style.color = st.showBefore ? P.void : "inherit";
  };
  st.draw = draw;
  hold.addEventListener("pointerdown", () => { st.showBefore = true; draw(); });
  for (const ev of ["pointerup", "pointerleave", "pointercancel"]) hold.addEventListener(ev, () => { if (st.showBefore) { st.showBefore = false; draw(); } });
  hold.addEventListener("keydown", (e) => {
    if (e.key === " " || e.key === "Enter") { e.preventDefault(); st.showBefore = !st.showBefore; draw(); }
  });
  copy.onclick = async () => {
    const all = st.items.map((i) => (st.items.length > 1 ? i.name + ": " : "") + i.text).join("\n");
    try {
      await navigator.clipboard.writeText(all);
      copy.textContent = "Copied";
    } catch (_) {
      copy.textContent = "Copy failed";
    }
    setTimeout(() => { copy.textContent = "Copy text"; }, 1200);
  };
  hide.onclick = () => {
    st.hidden = !st.hidden;
    imgs.style.display = st.hidden ? "none" : "flex";
    texts.style.display = st.hidden ? "none" : "flex";
    hide.textContent = st.hidden ? "Show" : "Hide";
    size(node, st);
  };
  return st;
}

function height(st) {
  if (st.hidden) return 30;
  let h = 30;
  if (st.files.length) h += IMG_H + 6;
  if (st.items.length) h += Math.min(st.items.length, 3) * 62 + 4;
  return h;
}

function size(node, st) {
  if (st.widget) st.widget.computeSize = (w) => [w, height(st)];
  const need = node.computeSize?.();
  if (need) node.setSize([Math.max(node.size[0], 250), Math.max(node.size[1], need[1])]);
  node.setDirtyCanvas?.(true, true);
}

function show(node, msg) {
  if (!setting(SETTING, true)) return;
  const files = msg?.sy_preview || [];
  const items = msg?.sy_text || [];
  if (!files.length && !items.length) return;
  if (!node._syPv) {
    node._syPv = build(node);
    node._syPv.widget = node.addDOMWidget("sy_result", "custom", node._syPv.box, { serialize: false });
  }
  const st = node._syPv;
  st.files = files;
  st.items = items;
  st.info.textContent = (msg?.sy_info?.[0]) || (items.length ? "Result" : "");
  st.hold.style.display = files.some((f) => f.role === "before") ? "" : "none";
  st.copy.style.display = items.length ? "" : "none";
  st.imgs.style.display = files.length && !st.hidden ? "flex" : "none";
  st.texts.style.display = items.length && !st.hidden ? "flex" : "none";
  st.texts.textContent = "";
  const P = pal();
  for (const it of items) {
    const row = document.createElement("div");
    row.style.cssText = "display:flex;flex-direction:column";
    const name = document.createElement("span");
    name.textContent = it.name;
    name.style.cssText = "font:600 10px " + FONT + ";letter-spacing:.05em;opacity:.75";
    const val = document.createElement("div");
    val.textContent = it.text;
    val.style.cssText = "max-height:48px;overflow:auto;white-space:pre-wrap;word-break:break-word;border-radius:5px;padding:3px 5px;font:11px ui-monospace,Consolas,monospace;background:" + P.surface;
    row.append(name, val);
    st.texts.append(row);
  }
  st.draw();
  size(node, st);
}

app.registerExtension({
  name: "sy.preview",
  settings: [
    {
      id: SETTING,
      name: "SY nodes: show the result on the node",
      type: "boolean",
      defaultValue: true,
      tooltip: "After a run, a small picture or text of what the node made shows on the node. Hold the Before button to see the picture before the change.",
    },
  ],
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (!nodeData?.name?.startsWith("SY")) return;
    await loadTheme();
    const executed = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (msg) {
      if (executed) executed.apply(this, arguments);
      try {
        show(this, msg);
      } catch (e) {
        console.warn("[SY] result preview not shown", e);
      }
    };
  },
});
