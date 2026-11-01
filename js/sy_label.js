// SY Nodes by Stable Yogi: Label SY. A big floating text for titles and step names. It runs nothing.
// The rules are in sy_label_logic.js and match nodes/sy_label.py. Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue } from "./sy_ui_kit.js";
import { labelLook, labelHeight } from "./sy_label_logic.js";

const FONT = "'DM Sans', sans-serif";
const TYPE = "SYLabel";

function setup(node) {
  const box = document.createElement("div");
  box.style.cssText = "width:100%;box-sizing:border-box;padding:2px 6px;font-family:" + FONT + ";font-weight:700;line-height:1.25;overflow:hidden;pointer-events:none;white-space:pre-wrap;word-break:break-word";
  let last = "";
  const draw = () => {
    const look = labelLook(widgetValue(node, "text", "Label"), widgetValue(node, "size", 36), widgetValue(node, "colour", "gold"), widgetValue(node, "align", "left"));
    const key = JSON.stringify(look);
    if (key === last) return;
    last = key;
    box.textContent = look.lines.join("\n");
    box.style.fontSize = look.px + "px";
    box.style.color = tk(look.token);
    box.style.textAlign = look.textAlign;
    node.__syLabelHeight = labelHeight(look);
    const size = node.computeSize?.();
    if (size && node.size[1] < size[1]) node.setSize([Math.max(node.size[0], 200), size[1]]);
    node.graph?.setDirtyCanvas?.(true, true);
  };
  const w = node.addDOMWidget("sy_label_text", "custom", box, { serialize: false });
  w.computeSize = (width) => [width, node.__syLabelHeight ?? 60];
  node.__syLabelHeight = 60;
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syLabelSeen) clearInterval(tick);
      return;
    }
    node._syLabelSeen = true;
    try {
      draw();
    } catch (e) {
      console.warn("[SY] label could not draw", e);
    }
  }, 400);
  draw();
}

app.registerExtension({
  name: "sy.label",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] label panel not added", e);
      }
      return r;
    };
  },
});
