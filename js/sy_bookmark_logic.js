// SY Nodes by Stable Yogi: pure rules for Bookmark SY. No page code in here, so it can be tested with node.
// They match nodes/sy_bookmark.py.
export const KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"];
export const MIN_ZOOM = 0.2;
export const MAX_ZOOM = 3;

export function clampZoom(zoom) {
  let z = zoom === null || zoom === undefined || zoom === "" ? NaN : Number(zoom);
  if (!Number.isFinite(z)) z = 1;
  return Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, z));
}

// bookmarks: [{id, key}]. The one that owns the key; with a shared key the lower id wins.
export function findBookmark(bookmarks, key) {
  const hits = (bookmarks || []).filter((b) => String(b.key) === String(key));
  if (!hits.length) return null;
  const rank = (b) => {
    const num = Number(b.id);
    return Number.isFinite(num) ? [0, num, ""] : [1, 0, String(b.id)];
  };
  hits.sort((a, b) => {
    const ra = rank(a), rb = rank(b);
    return ra[0] - rb[0] || ra[1] - rb[1] || (ra[2] < rb[2] ? -1 : ra[2] > rb[2] ? 1 : 0);
  });
  return hits[0];
}

export function sharedKeys(bookmarks) {
  const seen = {};
  for (const b of bookmarks || []) seen[String(b.key)] = (seen[String(b.key)] || 0) + 1;
  return KEYS.filter((k) => (seen[k] || 0) > 1);
}

// The canvas draws a point p at (p + offset) * zoom, so the offset that centres a node is view / (2 * zoom) - middle.
export function centreOffset(pos, size, zoom, viewW, viewH) {
  const z = clampZoom(zoom);
  const cx = pos[0] + size[0] / 2;
  const cy = pos[1] + size[1] / 2;
  return [viewW / (2 * z) - cx, viewH / (2 * z) - cy];
}

// Is this key press ours? A plain digit, no ctrl/alt/meta, and the user is not typing in a field.
export function isJumpKey(e) {
  if (!e || e.ctrlKey || e.altKey || e.metaKey || e.shiftKey) return null;
  if (!KEYS.includes(e.key)) return null;
  const t = e.target;
  const tag = t && t.tagName ? String(t.tagName).toUpperCase() : "";
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable)) return null;
  return e.key;
}
