// SY Nodes by Stable Yogi: Resource Monitor SY, plain rules. The same rules are in nodes/sy_resource_monitor.py.
const GB = 1024 ** 3;

export function percent(used, total) {
  const u = Number(used);
  const t = Number(total);
  if (!(t > 0) || !Number.isFinite(u)) return 0;
  return Math.round(Math.min(100, Math.max(0, (u / t) * 100)) * 10) / 10;
}

export function level(pct) {
  const p = Number(pct);
  return p >= 90 ? "hot" : p >= 70 ? "warn" : "ok";
}

export function tempLevel(celsius) {
  const c = Number(celsius);
  return c >= 85 ? "hot" : c >= 75 ? "warn" : "ok";
}

export function formatGb(bytes) {
  const b = Math.max(0, Number(bytes) || 0);
  return (b / GB).toFixed(1) + " GB";
}

export function cleanInterval(seconds) {
  const s = Number(seconds);
  if (!Number.isFinite(s)) return 1;
  return Math.min(10, Math.max(0.5, s));
}

export function cornerCss(corner) {
  const c = String(corner || "").trim().toLowerCase();
  const bottom = c.startsWith("bottom");
  const left = c.endsWith("left");
  return { top: bottom ? "auto" : "40px", bottom: bottom ? "12px" : "auto", left: left ? "12px" : "auto", right: left ? "auto" : "12px" };
}

// The meter rows to draw from one reading: [{key, label, percent, text, level}]. A source that is missing leaves its row out.
export function meterRows(snap) {
  const rows = [];
  if (!snap || typeof snap !== "object") return rows;
  if (snap.cpu != null) rows.push({ key: "cpu", label: "CPU", percent: snap.cpu, text: Math.round(snap.cpu) + "%", level: level(snap.cpu) });
  if (snap.ram) rows.push({ key: "ram", label: "RAM", percent: snap.ram.percent, text: formatGb(snap.ram.used) + " / " + formatGb(snap.ram.total), level: level(snap.ram.percent) });
  (snap.gpus || []).forEach((g, i) => {
    const tag = (snap.gpus.length > 1 ? "GPU" + i : "GPU");
    if (g.util != null) rows.push({ key: "gpu" + i, label: tag, percent: g.util, text: Math.round(g.util) + "%", level: level(g.util) });
    if (g.vram) rows.push({ key: "vram" + i, label: tag === "GPU" ? "VRAM" : "VRAM" + i, percent: g.vram.percent, text: formatGb(g.vram.used) + " / " + formatGb(g.vram.total), level: level(g.vram.percent) });
    if (g.temp != null) rows.push({ key: "temp" + i, label: tag === "GPU" ? "Temp" : "Temp" + i, percent: Math.min(100, Math.max(0, g.temp)), text: g.temp + " °C", level: tempLevel(g.temp) });
  });
  return rows;
}
