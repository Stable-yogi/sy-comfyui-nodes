// SY Nodes by Stable Yogi: small shared pieces for the node panels (buttons, overlay window, folder picker).
// Colours come from sy_theme.json through sy_core.js. Text is always set with textContent, never innerHTML.
import { api } from "../../scripts/api.js";
import { getTheme } from "./sy_core.js";

export function tk(name) {
  return (getTheme().tokens || {})[name] || "transparent";
}

const FONT = "'DM Sans', sans-serif";

// kind: gold (filled), green, blue, ghost (quiet), on (a switch that is on)
export function button(text, kind = "ghost", tip = "") {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = text;
  if (tip) b.title = tip;
  const fill = { gold: tk("gold"), on: tk("gold"), green: tk("green_btn"), blue: tk("blue"), ghost: tk("surface_3") }[kind] || tk("surface_3");
  const ink = kind === "gold" || kind === "on" ? tk("void") : tk("white");
  b.style.cssText = "cursor:pointer;border:0;border-radius:6px;padding:4px 9px;font:600 12px " + FONT +
    ";background:" + fill + ";color:" + ink;
  return b;
}

export function setSwitch(b, on) {
  b.style.background = on ? tk("gold") : tk("surface_3");
  b.style.color = on ? tk("void") : tk("white");
}

export function row(...kids) {
  const r = document.createElement("div");
  r.style.cssText = "display:flex;flex-wrap:wrap;gap:4px;align-items:center";
  r.append(...kids);
  return r;
}

export function label(text) {
  const d = document.createElement("div");
  d.textContent = text;
  d.style.cssText = "font:700 11px " + FONT + ";letter-spacing:.06em;color:" + tk("gold");
  return d;
}

// A window in the middle of the page. Returns {box, body, close}. Escape or a click outside closes it.
export function overlay(title, width = 560) {
  const back = document.createElement("div");
  back.style.cssText = "position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center";
  const box = document.createElement("div");
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-label", title);
  box.style.cssText = "width:min(" + width + "px,92vw);max-height:80vh;overflow:auto;border-radius:10px;padding:14px;" +
    "font:14px " + FONT + ";background:" + tk("void") + ";color:" + tk("white") + ";border:1px solid " + tk("gold_dim") +
    ";box-shadow:0 10px 40px rgba(0,0,0,.6)";
  const head = document.createElement("div");
  head.style.cssText = "display:flex;justify-content:space-between;align-items:center;margin-bottom:10px";
  const h = document.createElement("b");
  h.textContent = title;
  h.style.cssText = "font-size:16px;color:" + tk("gold");
  const x = button("Close", "ghost");
  head.append(h, x);
  const body = document.createElement("div");
  box.append(head, body);
  back.append(box);
  const close = () => {
    back.remove();
    document.removeEventListener("keydown", onKey, true);
  };
  const onKey = (e) => {
    if (e.key === "Escape") {
      e.stopPropagation();
      close();
    }
  };
  document.addEventListener("keydown", onKey, true);
  x.onclick = close;
  back.addEventListener("mousedown", (e) => {
    if (e.target === back) close();
  });
  document.body.append(back);
  return { box, body, close, head: h };
}

export async function listFolder(root, sub) {
  const res = await api.fetchApi("/sy/folder/list?root=" + encodeURIComponent(root) + "&sub=" + encodeURIComponent(sub || ""));
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "could not read the folder");
  return data;
}

// Folder picker: click a folder to go inside, "Use this folder" returns the path under the ComfyUI folder.
export function pickFolder(root, startSub, onPick) {
  const ov = overlay("Choose a folder (" + root + ")", 460);
  let sub = startSub || "";
  const path = document.createElement("div");
  path.style.cssText = "font-size:12px;color:" + tk("text_2") + ";margin-bottom:8px;word-break:break-all";
  const list = document.createElement("div");
  list.style.cssText = "display:flex;flex-direction:column;gap:4px;margin-bottom:10px";
  const use = button("Use this folder", "gold");
  ov.body.append(path, list, use);
  const show = async () => {
    list.textContent = "";
    try {
      const d = await listFolder(root, sub);
      sub = d.sub;
      path.textContent = d.root_path + (sub ? "/" + sub : "") + "   (" + d.images + " pictures here)";
      if (sub) {
        const up = button("Up one level", "ghost");
        up.onclick = () => {
          sub = sub.split("/").slice(0, -1).join("/");
          show();
        };
        list.append(up);
      }
      for (const name of d.dirs) {
        const b = button(name, "ghost");
        b.style.textAlign = "left";
        b.onclick = () => {
          sub = sub ? sub + "/" + name : name;
          show();
        };
        list.append(b);
      }
      if (!d.dirs.length) {
        const none = document.createElement("div");
        none.textContent = "No folders inside.";
        none.style.cssText = "font-size:12px;color:" + tk("text_2");
        list.append(none);
      }
    } catch (e) {
      path.textContent = String(e.message || e);
    }
  };
  use.onclick = () => {
    onPick(sub);
    ov.close();
  };
  show();
}

export function hideWidget(w) {
  if (!w || w._syHidden) return;
  w._syHidden = true;
  w.hidden = true;
  w._syType = w.type;
  w.type = "hidden";
  w.computeSize = () => [0, -4];
  if (w.element?.style) w.element.style.display = "none";
}

export function setWidget(node, name, value) {
  const w = node.widgets?.find((x) => x.name === name);
  if (!w) return;
  w.value = value;
  if (w.callback) w.callback(value);
  node.setDirtyCanvas?.(true, true);
}

export function widgetValue(node, name, fallback) {
  const w = node.widgets?.find((x) => x.name === name);
  return w && w.value !== undefined ? w.value : fallback;
}
