// SY Nodes by Stable Yogi: shared helpers for the browser files (theme, light/dark, settings, safe storage).
import { app } from "../../scripts/app.js";

let theme = null;

export async function loadTheme() {
  if (theme) return theme;
  try {
    const res = await fetch(new URL("./sy_theme.json", import.meta.url));
    theme = await res.json();
  } catch (err) {
    console.warn("[SY] colour file not loaded", err);
    theme = { tokens: {}, groups: {}, note_styles: {} };
  }
  return theme;
}

export function getTheme() {
  return theme || { tokens: {}, groups: {}, note_styles: {} };
}

export function setting(id, fallback) {
  try {
    const v = app.extensionManager?.setting?.get(id) ?? app.ui?.settings?.getSettingValue(id);
    return v === undefined || v === null ? fallback : v;
  } catch (_) {
    return fallback;
  }
}

// Light or dark: read the real page colour, not a flag. Setting SY.Look can force one.
export function isLight() {
  const forced = setting("SY.Look", "Auto");
  if (forced === "Light") return true;
  if (forced === "Dark") return false;
  try {
    const c = getComputedStyle(document.body).backgroundColor.match(/\d+/g);
    if (!c) return false;
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2] > 150;
  } catch (_) {
    return false;
  }
}

// Colours for SY panels. Dark values come from sy_theme.json; light values are derived here.
export function pal() {
  const t = getTheme().tokens || {};
  if (!isLight()) {
    return { void: t.void || "#1a1b1e", abyss: t.abyss || "#1e1f22", surface: t.surface || "#2b2d31",
      text: t.text || "#f2f3f5", gold: t.gold || "#d4a537", gold_dim: t.gold_dim || "#8b6914", muted: t.text_2 || "#c2c6ce" };
  }
  return { void: "#fafafa", abyss: "#ffffff", surface: "#eceef1", text: "#1e1f22", gold: "#8b6914", gold_dim: "#b48a1c", muted: "#4a4d55" };
}

// Job colour of a node class: loaders blue, working nodes green, save and preview brown, and so on.
// An explicit list (role_of) wins, then the node group (group_roles). Returns {role, color, bgcolor} or null.
export function roleColors(type, group) {
  const th = getTheme();
  let role = null;
  for (const [r, list] of Object.entries(th.role_of || {})) if (list.includes(type)) role = r;
  if (!role) role = (th.group_roles || {})[group] || null;
  const c = role && th.roles ? th.roles[role] : null;
  return c ? { role, color: c.color, bgcolor: c.bgcolor } : null;
}

export function store(key, fallback) {
  try {
    const raw = localStorage.getItem("sy." + key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch (_) {
    return fallback;
  }
}

export function save(key, value) {
  try {
    localStorage.setItem("sy." + key, JSON.stringify(value));
  } catch (_) {
    /* private window or blocked storage: the page still works without it */
  }
}

export function listSyNodeTypes() {
  const out = [];
  const types = (window.LiteGraph && LiteGraph.registered_node_types) || {};
  for (const [type, ctor] of Object.entries(types)) {
    const d = ctor.nodeData;
    if (type.startsWith("SY") && d && (d.category || "").startsWith("SY/")) out.push({ type, data: d });
  }
  return out;
}

// reduced motion: panels never animate when the user asks for less motion
export const reducedMotion = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
