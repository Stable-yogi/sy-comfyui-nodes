// SY Nodes by Stable Yogi: the banner of Workflow Header SY. A workflow number, a title, a subtitle, three buttons that open a help window and three link buttons (GitHub, website, YouTube).
// The texts are kept in node.properties, so they travel inside the workflow file. Text is always set with textContent.
import { app } from "../../scripts/app.js";
import { tk, button, row, overlay } from "./sy_ui_kit.js";
import { parseMarkdown } from "./sy_markdown_logic.js";

const PANELS = [
  ["sy_install", "Nodes to Install", "gold", "Which custom nodes this workflow needs"],
  ["sy_howto", "How to Use", "green", "Steps to run this workflow"],
  ["sy_info", "Nodes Info", "blue", "What the main nodes do"],
];
const LINKS = [
  ["GitHub", "https://github.com/Stable-yogi/sy-comfyui-nodes", "The Stable Yogi Nodes (S Y Nodes) page on GitHub"],
  ["Website", "https://stableyogi.com", "stableyogi.com"],
  ["YouTube", "https://www.youtube.com/channel/UCt6qODfTcDy4eEPXLDlGizA", "The Stable Yogi YouTube channel"],
];
const DEFAULTS = { sy_number: "", sy_title: "Workflow title", sy_subtitle: "Made with SY Nodes by Stable Yogi", sy_install: "", sy_howto: "", sy_info: "" };

function prop(node, key) {
  const v = node.properties?.[key];
  return typeof v === "string" ? v : DEFAULTS[key];
}

function numberText(node) {
  const n = String(prop(node, "sy_number") || "").trim();
  return n ? "Workflow " + n : "";
}


// Builds the marked text (headers, lists, bold, italic, code) into a box. Only textContent is used, so no HTML is ever read.
const HEAD_SIZE = { h1: "22px", h2: "17px", h3: "14px" };
function renderMarked(box, text, fallback) {
  box.textContent = "";
  const blocks = parseMarkdown(text);
  if (!blocks.length) {
    box.textContent = fallback || "";
    return;
  }
  let list = null;
  for (const b of blocks) {
    let el;
    if (b.type === "li") {
      if (!list) {
        list = document.createElement("ul");
        list.style.cssText = "margin:2px 0 2px 18px;padding:0";
        box.append(list);
      }
      el = document.createElement("li");
      list.append(el);
    } else {
      list = null;
      el = document.createElement("div");
      if (HEAD_SIZE[b.type]) el.style.cssText = "font-weight:700;font-size:" + HEAD_SIZE[b.type] + ";margin:4px 0 2px;color:" + tk("white");
      box.append(el);
    }
    for (const p of b.inline) {
      if (p.k === "text") el.append(document.createTextNode(p.s));
      else {
        const span = document.createElement(p.k === "code" ? "code" : p.k === "b" ? "strong" : "em");
        if (p.k === "code") span.style.cssText = "font-family:'JetBrains Mono',monospace;font-size:0.9em;padding:0 3px;border-radius:3px;background:" + tk("abyss");
        span.textContent = p.s;
        el.append(span);
      }
    }
  }
}

function showText(title, text) {
  const ov = overlay(title, 620);
  const body = document.createElement("div");
  body.style.cssText = "line-height:1.5;font-size:14px";
  renderMarked(body, text, "Nothing written here yet. Click the pencil on the banner to add text.");
  ov.body.append(body);
}

function editTexts(node, refresh) {
  const ov = overlay("Edit the banner", 620);
  const fields = {};
  const make = (key, labelText, tall) => {
    const wrap = document.createElement("label");
    wrap.style.cssText = "display:block;margin-bottom:8px;font-size:12px;color:" + tk("gold");
    wrap.textContent = labelText;
    const input = document.createElement(tall ? "textarea" : "input");
    input.value = prop(node, key);
    input.style.cssText = "display:block;width:100%;box-sizing:border-box;margin-top:3px;padding:6px;border-radius:6px;border:1px solid " +
      tk("gold_dim") + ";background:" + tk("abyss") + ";color:" + tk("white") + ";font:13px 'DM Sans',sans-serif" + (tall ? ";min-height:90px;resize:vertical" : "");
    wrap.append(input);
    ov.body.append(wrap);
    fields[key] = input;
  };
  make("sy_number", "WORKFLOW NUMBER (for example 3, shown as Workflow 3)", false);
  make("sy_title", "TITLE", false);
  make("sy_subtitle", "SUBTITLE (lines may start with #, ## or ### for headers; **bold**, *italic*, - list)", true);
  make("sy_install", "NODES TO INSTALL (one line per node pack; # headers, **bold** and - lists work)", true);
  make("sy_howto", "HOW TO USE (one step per line)", true);
  make("sy_info", "NODES INFO", true);
  const save = button("Save", "gold");
  save.onclick = () => {
    node.properties = node.properties || {};
    for (const [key, input] of Object.entries(fields)) node.properties[key] = input.value;
    refresh();
    node.setDirtyCanvas?.(true, true);
    ov.close();
  };
  ov.body.append(save);
}

function addBanner(node) {
  node.properties = node.properties || {};
  for (const [k, v] of Object.entries(DEFAULTS)) if (typeof node.properties[k] !== "string") node.properties[k] = v;

  const box = document.createElement("div");
  box.style.cssText = "display:flex;flex-direction:column;gap:8px;width:100%;box-sizing:border-box;padding:6px 4px";
  const title = document.createElement("div");
  title.style.cssText = "display:inline-block;align-self:flex-start;padding:6px 16px;border-radius:4px;font:700 22px 'DM Sans',sans-serif;background:" +
    tk("gold") + ";color:" + tk("void");
  const num = document.createElement("div");
  num.style.cssText = "align-self:flex-start;font:700 12px 'JetBrains Mono',monospace;letter-spacing:1px;text-transform:uppercase;color:" + tk("gold");
  const sub = document.createElement("div");
  sub.style.cssText = "font:13px 'DM Sans',sans-serif;color:" + tk("text_2");
  const buttons = row();
  const edit = button("Edit", "ghost", "Change the title and the three help texts");
  for (const [key, text, kind, tip] of PANELS) {
    const b = button(text, kind, tip);
    b.style.padding = "8px 16px";
    b.style.fontSize = "14px";
    b.onclick = () => showText(text, prop(node, key));
    buttons.append(b);
  }
  buttons.append(edit);
  const links = row();
  for (const [text, url, tip] of LINKS) {
    const b = button(text, "ghost", tip);
    b.onclick = () => window.open(url, "_blank", "noopener,noreferrer");
    links.append(b);
  }
  box.append(num, title, sub, buttons, links);

  const refresh = () => {
    num.textContent = numberText(node);
    num.style.display = num.textContent ? "block" : "none";
    title.textContent = prop(node, "sy_title");
    renderMarked(sub, prop(node, "sy_subtitle"));
  };
  edit.onclick = () => editTexts(node, refresh);
  const widget = node.addDOMWidget("sy_banner", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 160];
  refresh();
  node._syBannerRefresh = refresh;
  node.setSize([Math.max(node.size[0], 460), Math.max(node.size[1], 190)]);
}

app.registerExtension({
  name: "sy.header",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "SYWorkflowHeader") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try { addBanner(this); } catch (e) { console.warn("[SY] banner not shown", e); }
      return r;
    };
    // after a workflow loads, the saved texts are in node.properties: show them
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configured ? configured.apply(this, arguments) : undefined;
      if (this._syBannerRefresh) this._syBannerRefresh();
      return r;
    };
  },
});
