// SY Nodes by Stable Yogi: a live colour chip under every hex colour field, with a colour picker.
// The chip only reads the text and the picker only writes the same text, so a workflow runs without this file.
// Text is always set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, setWidget, widgetValue } from "./sy_ui_kit.js";

const FONT = "'DM Sans', sans-serif";
// node class -> the text widgets that hold a colour
const FIELDS = {
  SYAddBorder: ["colour"],
  SYCheckerboard: ["colour_a", "colour_b"],
  SYColourOverlay: ["colour"],
  SYColourSwatch: ["colour"],
  SYGradientImage: ["colour_a", "colour_b"],
  SYHexColourMix: ["colour_a", "colour_b"],
};

// same rule as the nodes: 3 or 6 hex digits, the # sign is optional. Returns "#rrggbb" or null.
export function parseHex(text) {
  let s = String(text ?? "").trim();
  if (s.startsWith("#")) s = s.slice(1);
  if (!/^([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(s)) return null;
  if (s.length === 3) s = [...s].map((c) => c + c).join("");
  return "#" + s.toLowerCase();
}

function setup(node, names) {
  const wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-direction:column;gap:4px;width:100%;box-sizing:border-box;padding:2px;font:12px " + FONT + ";color:" + tk("white");
  const chips = names.map((name) => {
    const r = document.createElement("div");
    r.style.cssText = "display:flex;align-items:center;gap:6px";
    const chip = document.createElement("div");
    chip.style.cssText = "width:34px;height:20px;border-radius:5px;border:1px solid " + tk("gold_dim") + ";flex:none";
    const pick = document.createElement("input");
    pick.type = "color";
    pick.title = "Pick a colour. It fills in the " + name + " text.";
    pick.style.cssText = "width:30px;height:22px;padding:0;border:none;background:none;cursor:pointer;flex:none";
    const txt = document.createElement("span");
    txt.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2");
    r.append(chip, pick, txt);
    pick.addEventListener("input", () => setWidget(node, name, pick.value));
    wrap.append(r);
    return { name, chip, pick, txt };
  });
  const update = () => {
    for (const c of chips) {
      const hex = parseHex(widgetValue(node, c.name, ""));
      if (hex) {
        c.chip.style.background = hex;
        c.pick.value = hex;
        c.txt.textContent = c.name + ": " + hex;
        c.txt.style.color = tk("text_2");
      } else {
        c.chip.style.background = "repeating-linear-gradient(45deg,#444,#444 4px,#666 4px,#666 8px)";
        c.txt.textContent = c.name + ": not a colour (use 3 or 6 hex digits)";
        c.txt.style.color = tk("red_soft");
      }
    }
  };
  const w = node.addDOMWidget("sy_colour_chips", "custom", wrap, { serialize: false });
  w.computeSize = (width) => [width, 28 * names.length + 6];
  const need = node.computeSize?.();
  if (need && node.size[1] < need[1]) node.setSize([Math.max(node.size[0], 250), need[1]]);
  for (const c of chips) {
    const tw = node.widgets.find((x) => x.name === c.name);
    if (!tw) continue;
    const orig = tw.callback;
    tw.callback = function () {
      const r = orig ? orig.apply(this, arguments) : undefined;
      update();
      return r;
    };
  }
  const conf = node.onConfigure;
  node.onConfigure = function () {
    const r = conf ? conf.apply(this, arguments) : undefined;
    setTimeout(update, 50);
    return r;
  };
  // typing in the text box does not call the callback until you press Enter, so look again now and then
  let last = "";
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syColourSeen) clearInterval(tick);
      return;
    }
    node._syColourSeen = true;
    const now = names.map((n) => widgetValue(node, n, "")).join("|");
    if (now !== last) {
      last = now;
      update();
    }
  }, 400);
  update();
}

app.registerExtension({
  name: "sy.colours",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const names = FIELDS[nodeData?.name];
    if (!names) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this, names);
      } catch (e) {
        console.warn("[SY] colour chip not added to " + nodeData.name, e);
      }
      return r;
    };
  },
});
