// SY Nodes by Stable Yogi: pure helpers for the Seed Vault SY table. No page code in here, so it can be tested with node.
export function stars(rating) {
  const r = Math.max(0, Math.min(5, Math.trunc(Number(rating)) || 0));
  return "★".repeat(r) + "☆".repeat(5 - r);
}

// One short line for a tooltip: note, tags and prompt.
export function detailText(row) {
  const parts = [];
  if (row && row.note) parts.push(String(row.note));
  if (row && Array.isArray(row.tags) && row.tags.length) parts.push("tags: " + row.tags.join(", "));
  if (row && row.prompt) parts.push("prompt: " + String(row.prompt));
  return parts.join("\n");
}

// The cell text for the "what" column: the note, else the tags, else the start of the prompt.
export function shortLabel(row, max = 48) {
  if (!row) return "";
  let t = row.note ? String(row.note) : Array.isArray(row.tags) && row.tags.length ? row.tags.join(", ") : row.prompt ? String(row.prompt) : "";
  t = t.replace(/\s+/g, " ").trim();
  return t.length > max ? t.slice(0, max - 3) + "..." : t;
}

// The whole table as Markdown, for pasting into your notes. The pipe character is escaped so a note cannot break a row.
export function tableMarkdown(collection, rows) {
  const esc = (s) => String(s ?? "").replace(/\|/g, "\|").replace(/\s+/g, " ").trim();
  const out = ["## " + esc(collection) + " (" + (rows || []).length + " saved)", "", "| # | seed | stars | saved | note | tags |", "|---|---|---|---|---|---|"];
  for (const r of rows || []) {
    out.push("| " + r.rank + " | " + r.seed + " | " + stars(r.rating) + " | " + r.count + " | " + esc(r.note) + " | " + esc((r.tags || []).join(", ")) + " |");
  }
  return out.join("\n");
}

// The server answer must look like {collections:[{name,count}], collection, rows:[...]}. Anything else gives an empty view.
export function cleanView(data) {
  const empty = { collections: [], collection: "", rows: [] };
  if (!data || typeof data !== "object" || data.error) return empty;
  const cols = Array.isArray(data.collections) ? data.collections.filter((c) => c && typeof c.name === "string").map((c) => ({ name: c.name, count: Number(c.count) || 0 })) : [];
  const rows = Array.isArray(data.rows)
    ? data.rows.filter((r) => r && Number.isFinite(Number(r.seed))).map((r, i) => ({
        rank: Number(r.rank) || i + 1, seed: String(r.seed), rating: Number(r.rating) || 0, count: Number(r.count) || 1,
        note: String(r.note || ""), tags: Array.isArray(r.tags) ? r.tags.map(String) : [], prompt: String(r.prompt || ""), saved_at: String(r.saved_at || ""),
      }))
    : [];
  return { collections: cols, collection: typeof data.collection === "string" ? data.collection : "", rows };
}
