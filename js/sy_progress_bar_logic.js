// SY Nodes by Stable Yogi: Progress Bar SY, plain rules. The same rules are in nodes/sy_progress_bar.py.

// Overall percent (0 to 100). total = nodes in the job, finished = nodes already done (cached ones count),
// subValue/subMax = the step counter inside the running node (a sampler shows 12 of 30). Never 100 until the job says so.
export function overallPercent(total, finished, subValue = 0, subMax = 0, done = false) {
  if (done) return 100;
  const t = Math.max(0, Math.floor(Number(total) || 0));
  if (t === 0) return 0;
  const f = Math.min(t, Math.max(0, Math.floor(Number(finished) || 0)));
  const sm = Number(subMax) || 0;
  const frac = sm > 0 ? Math.min(1, Math.max(0, (Number(subValue) || 0) / sm)) : 0;
  const pct = ((f + (f < t ? frac : 0)) / t) * 100;
  return Math.min(99, Math.max(0, Math.round(pct * 10) / 10));
}

// 0:07, 1:05, 1:02:03. Whole seconds, never negative.
export function formatElapsed(ms) {
  const s = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const r = s % 60;
  const two = (x) => String(x).padStart(2, "0");
  return h > 0 ? h + ":" + two(m) + ":" + two(r) : m + ":" + two(r);
}

export function shortTitle(title, max = 32) {
  const t = String(title || "").replace(/\s+/g, " ").trim();
  const n = Math.max(4, Math.floor(Number(max) || 32));
  return t.length > n ? t.slice(0, n - 1).trimEnd() + "…" : t;
}

// The one line shown on the bar.
export function barText(opts) {
  const o = opts || {};
  const parts = [];
  if (o.state === "error") parts.push("Stopped by an error");
  else if (o.state === "done") parts.push("Done");
  else if (o.state === "stopped") parts.push("Stopped");
  else parts.push(Math.round(Number(o.percent) || 0) + "%");
  if (o.showStep && o.state === "running" && Number(o.subMax) > 0) parts.push("step " + Math.floor(Number(o.subValue) || 0) + " of " + Math.floor(Number(o.subMax)));
  if (o.showNode && o.state === "running" && o.node) parts.push(shortTitle(o.node));
  if (o.showTime) parts.push(formatElapsed(o.elapsedMs));
  return parts.join("  ·  ");
}

export function positionStyle(pos) {
  return String(pos || "").trim().toLowerCase() === "bottom" ? "bottom" : "top";
}
