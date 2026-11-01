// SY Nodes by Stable Yogi: pure rules for Label SY. No page code in here, so it can be tested with node.
// They match nodes/sy_label.py.
export const COLOURS = ["gold", "white", "grey", "blue", "green", "red", "purple"];
export const ALIGNS = ["left", "centre", "right"];
export const MIN_SIZE = 10;
export const MAX_SIZE = 200;
export const MAX_TEXT = 2000;
// the theme token behind each colour name
export const TOKEN = { gold: "gold", white: "white", grey: "text_2", blue: "cyan", green: "green", red: "red_soft", purple: "purple_accent" };
const CSS_ALIGN = { left: "left", centre: "center", right: "right" };

export function cleanLabel(text, size, colour, align) {
  let s = Number.parseInt(size, 10);
  if (!Number.isFinite(s)) s = 36;
  return {
    text: text == null ? "" : String(text).slice(0, MAX_TEXT),
    size: Math.max(MIN_SIZE, Math.min(MAX_SIZE, s)),
    colour: COLOURS.includes(colour) ? colour : "gold",
    align: ALIGNS.includes(align) ? align : "left",
  };
}

export function labelLines(text) {
  const lines = String(text ?? "").replace(/\r\n?/g, "\n").split("\n");
  while (lines.length && !lines[0].trim()) lines.shift();
  while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
  return lines;
}

// What the page needs to draw a label: lines, font size in pixels, theme token, CSS text-align
export function labelLook(text, size, colour, align) {
  const c = cleanLabel(text, size, colour, align);
  return { lines: labelLines(c.text), px: c.size, token: TOKEN[c.colour], textAlign: CSS_ALIGN[c.align] };
}

// Height the node needs for a label, in pixels
export function labelHeight(look) {
  return Math.max(1, look.lines.length) * Math.round(look.px * 1.25) + 12;
}
