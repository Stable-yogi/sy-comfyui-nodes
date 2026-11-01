// SY Nodes by Stable Yogi: a small, safe text format for banners and help windows (Workflow Header SY).
// Pure functions, no page needed. The result is a list of blocks; the page builds them with textContent, so no HTML is ever read.
// Lines: "# big", "## medium", "### small" (a space after the hashes), "- item" or "* item" (a list), a blank line ends a paragraph.
// Inside a line: **bold**, *italic*, `code`. Anything else is plain text, shown as typed.

export const MAX_TEXT = 20000;

// One line of text -> pieces [{k: "text"|"b"|"i"|"code", s}]
export function parseInline(line) {
  const text = String(line ?? "");
  const out = [];
  let plain = "";
  const flush = () => {
    if (plain) out.push({ k: "text", s: plain });
    plain = "";
  };
  let i = 0;
  while (i < text.length) {
    const rest = text.slice(i);
    let m = /^\*\*(?=\S)([^*]*?\S)\*\*/.exec(rest);
    if (m) { flush(); out.push({ k: "b", s: m[1] }); i += m[0].length; continue; }
    m = /^`([^`]+)`/.exec(rest);
    if (m) { flush(); out.push({ k: "code", s: m[1] }); i += m[0].length; continue; }
    m = /^\*(?=[^\s*])([^*]*?[^\s*])\*/.exec(rest);
    if (m) { flush(); out.push({ k: "i", s: m[1] }); i += m[0].length; continue; }
    plain += text[i];
    i++;
  }
  flush();
  return out;
}

// A whole text -> blocks [{type: "h1"|"h2"|"h3"|"p"|"li", inline}]
export function parseMarkdown(text) {
  const src = String(text ?? "").slice(0, MAX_TEXT).replace(/\r\n?/g, "\n");
  const blocks = [];
  let para = [];
  const endPara = () => {
    if (para.length) blocks.push({ type: "p", inline: parseInline(para.join(" ")) });
    para = [];
  };
  for (const raw of src.split("\n")) {
    const line = raw.replace(/\s+$/, "");
    if (!line.trim()) { endPara(); continue; }
    let m = /^\s{0,3}(#{1,3})\s+(.*\S)\s*$/.exec(line);
    if (m) { endPara(); blocks.push({ type: "h" + m[1].length, inline: parseInline(m[2]) }); continue; }
    m = /^\s{0,3}[-*]\s+(.*\S)\s*$/.exec(line);
    if (m) { endPara(); blocks.push({ type: "li", inline: parseInline(m[1]) }); continue; }
    para.push(line.trim());
  }
  endPara();
  return blocks;
}

// The plain words of a text without the marks (used for the node title and for tests).
export function plainText(text) {
  return parseMarkdown(text).map((b) => b.inline.map((p) => p.s).join("")).join(" ").trim();
}
