// SY Nodes by Stable Yogi: Group Switch SY. A panel with one on/off switch for every group of the workflow.
// Off sets the nodes inside the group to bypass or mute, On sets them back to normal.
// The rules match nodes/sy_group_switch.py. The node runs nothing itself, so a workflow runs without this file.
// Text is always set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { loadTheme } from "./sy_core.js";
import { tk, widgetValue } from "./sy_ui_kit.js";

const FONT = "'DM Sans', sans-serif";
const MODE_ALWAYS = 0;
const MODE_MUTE = 2;
const MODE_BYPASS = 4;

export function visibleGroups(titles, needle) {
  const n = String(needle ?? "").trim().toLowerCase();
  return titles.filter((t) => String(t).toLowerCase().includes(n));
}

export function nextStates(states, clicked, turnOn, exclusive) {
  let out = states.map(Boolean);
  if (turnOn && exclusive) out = out.map(() => false);
  out[clicked] = !!turnOn;
  return out;
}

function boundsOf(g) {
  const b = g._bounding;
  if (b && b.length >= 4) return [b[0], b[1], b[2], b[3]];
  return [g.pos[0], g.pos[1], g.size[0], g.size[1]];
}

// nodes whose middle sits inside the group box, without the switch node itself
function membersOf(g, self) {
  const [x, y, w, h] = boundsOf(g);
  const out = [];
  for (const n of app.graph?._nodes ?? []) {
    if (n === self) continue;
    const cx = n.pos[0] + n.size[0] / 2;
    const cy = n.pos[1] + n.size[1] / 2;
    if (cx >= x && cx <= x + w && cy >= y && cy <= y + h) out.push(n);
  }
  return out;
}

function groupIsOn(members) {
  if (!members.length) return false;
  return members.some((n) => n.mode !== MODE_MUTE && n.mode !== MODE_BYPASS);
}

function setup(node) {
  const wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-direction:column;gap:4px;width:100%;box-sizing:border-box;padding:2px;font:12px " + FONT + ";color:" + tk("white");
  const empty = document.createElement("div");
  empty.style.cssText = "font:600 11px " + FONT + ";color:" + tk("text_2");
  wrap.append(empty);
  let rows = [];
  let signature = "";

  const list = () => {
    const needle = widgetValue(node, "title_filter", "");
    const sort = widgetValue(node, "sort", "position");
    let groups = (app.graph?._groups ?? []).filter((g) => visibleGroups([g.title], needle).length);
    if (sort === "alphabetical") groups = groups.slice().sort((a, b) => String(a.title).localeCompare(String(b.title)));
    else groups = groups.slice().sort((a, b) => boundsOf(a)[1] - boundsOf(b)[1] || boundsOf(a)[0] - boundsOf(b)[0]);
    return groups;
  };

  const apply = (groups, clickedIdx, turnOn) => {
    const exclusive = !!widgetValue(node, "one_at_a_time", false);
    const offMode = widgetValue(node, "off_mode", "bypass") === "mute" ? MODE_MUTE : MODE_BYPASS;
    const before = groups.map((g) => groupIsOn(membersOf(g, node)));
    const after = nextStates(before, clickedIdx, turnOn, exclusive);
    groups.forEach((g, i) => {
      if (before[i] === after[i]) return;
      for (const n of membersOf(g, node)) n.mode = after[i] ? MODE_ALWAYS : offMode;
    });
    app.graph?.setDirtyCanvas?.(true, true);
    refresh();
  };

  const refresh = () => {
    const groups = list();
    const sig = groups.map((g) => g.title).join("|");
    if (sig !== signature) {
      signature = sig;
      for (const r of rows) r.row.remove();
      rows = groups.map((g, i) => {
        const row = document.createElement("div");
        row.style.cssText = "display:flex;align-items:center;gap:8px;cursor:pointer";
        const sw = document.createElement("div");
        sw.style.cssText = "width:34px;height:18px;border-radius:9px;position:relative;flex:none;border:1px solid " + tk("gold_dim");
        const dot = document.createElement("div");
        dot.style.cssText = "position:absolute;top:2px;width:12px;height:12px;border-radius:6px;transition:left .1s";
        sw.append(dot);
        const label = document.createElement("span");
        label.style.cssText = "font:600 11px " + FONT + ";overflow:hidden;text-overflow:ellipsis;white-space:nowrap";
        label.textContent = String(g.title);
        row.append(sw, label);
        row.addEventListener("click", () => {
          const gs = list();
          const idx = gs.indexOf(g);
          if (idx < 0) return;
          apply(gs, idx, !groupIsOn(membersOf(g, node)));
        });
        wrap.append(row);
        return { row, sw, dot, g };
      });
      const need = 24 * Math.max(1, rows.length) + 12;
      node.__syGroupHeight = need;
      const size = node.computeSize?.();
      if (size && node.size[1] < size[1]) node.setSize([Math.max(node.size[0], 240), size[1]]);
    }
    empty.textContent = rows.length ? "" : "No groups to show. Make a group, or change the title filter.";
    empty.style.display = rows.length ? "none" : "block";
    for (const r of rows) {
      const on = groupIsOn(membersOf(r.g, node));
      r.sw.style.background = on ? tk("gold") : tk("surface_3");
      r.dot.style.left = on ? "18px" : "2px";
      r.dot.style.background = on ? tk("void") : tk("text_2");
      r.row.title = on ? "On. Click to switch the group off." : "Off. Click to switch the group on.";
    }
  };

  const w = node.addDOMWidget("sy_group_panel", "custom", wrap, { serialize: false });
  w.computeSize = (width) => [width, node.__syGroupHeight ?? 36];
  node.__syGroupHeight = 36;
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syGroupSeen) clearInterval(tick);
      return;
    }
    node._syGroupSeen = true;
    try {
      refresh();
    } catch (e) {
      console.warn("[SY] group switch refresh failed", e);
    }
  }, 500);
  refresh();
}

app.registerExtension({
  name: "sy.group_switch",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== "SYGroupSwitch") return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] group switch panel not added", e);
      }
      return r;
    };
  },
});
