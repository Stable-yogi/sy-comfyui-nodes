// SY Nodes by Stable Yogi: Bookmark SY. Press 1 to 9 (not while typing) and the view jumps to the bookmark with that key.
// The rules are in sy_bookmark_logic.js and match nodes/sy_bookmark.py. The node runs nothing, so a workflow runs without this file.
// Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue } from "./sy_ui_kit.js";
import { findBookmark, sharedKeys, centreOffset, clampZoom, isJumpKey } from "./sy_bookmark_logic.js";

const FONT = "'DM Sans', sans-serif";
const TYPE = "SYBookmark";
let keyHooked = false;

function bookmarksOf(graph) {
  return (graph?._nodes ?? [])
    .filter((n) => n.type === TYPE)
    .map((n) => ({ id: n.id, key: widgetValue(n, "key", "1"), node: n }));
}

// Moves the view so the node sits in the middle at its zoom. Returns true when it jumped.
export function jumpTo(node) {
  const canvas = app.canvas;
  const el = canvas?.canvas;
  if (!canvas?.ds || !el) return false;
  const zoom = clampZoom(widgetValue(node, "zoom", 1));
  const rect = el.getBoundingClientRect();
  const off = centreOffset(node.pos, node.size, zoom, rect.width, rect.height);
  canvas.ds.scale = zoom;
  canvas.ds.offset[0] = off[0];
  canvas.ds.offset[1] = off[1];
  canvas.setDirty?.(true, true);
  return true;
}

function hookKeys() {
  if (keyHooked) return;
  keyHooked = true;
  window.addEventListener("keydown", (e) => {
    try {
      const key = isJumpKey(e);
      if (!key) return;
      const hit = findBookmark(bookmarksOf(app.graph), key);
      if (hit && jumpTo(hit.node)) {
        e.preventDefault();
        e.stopPropagation();
      }
    } catch (err) {
      console.warn("[SY] bookmark jump failed", err);
    }
  });
}

function setup(node) {
  const status = document.createElement("div");
  status.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2") + ";padding:2px 4px;box-sizing:border-box;width:100%";
  const refresh = () => {
    const key = widgetValue(node, "key", "1");
    const clash = sharedKeys(bookmarksOf(node.graph)).includes(String(key));
    status.textContent = clash ? "Key " + key + " is used by more than one bookmark. Only the first one jumps." : "Press " + key + " to jump here.";
    status.style.color = clash ? tk("red_soft") : tk("text_2");
  };
  const w = node.addDOMWidget("sy_bookmark_status", "custom", status, { serialize: false });
  w.computeSize = (width) => [width, 26];
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syBookSeen) clearInterval(tick);
      return;
    }
    node._syBookSeen = true;
    try {
      refresh();
    } catch (e) {
      console.warn("[SY] bookmark status failed", e);
    }
  }, 700);
  refresh();
}

app.registerExtension({
  name: "sy.bookmark",
  async setup() {
    hookKeys();
  },
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        hookKeys();
        setup(this);
      } catch (e) {
        console.warn("[SY] bookmark panel not added", e);
      }
      return r;
    };
  },
});
