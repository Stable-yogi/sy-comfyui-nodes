// SY Nodes by Stable Yogi: Done Alert SY (browser part). Plays a sound and shows a small note when the run reaches the node.
// No sound files: the tones are made with the Web Audio API. Nothing here can stop a run; every step is wrapped.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk } from "./sy_ui_kit.js";

const TYPE = "SYDoneAlert";
const FONT = "'DM Sans', sans-serif";
const POLL_MS = 1000;
const POLL_MAX_MS = 10 * 60 * 1000;
const TOAST_MS = 6000;

let audio = null;
let waiting = false;
let pending = null; // latest settings waiting for an empty queue
let pendingId = null; // the run (prompt id) that sent the latest settings

function ctx() {
  try {
    if (!audio) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      audio = new AC();
    }
    if (audio.state === "suspended") audio.resume().catch(() => {});
    return audio;
  } catch (_) {
    return null;
  }
}

// One tone with a short fade in and fade out so it does not click.
function tone(ac, freq, start, length, volume) {
  const osc = ac.createOscillator();
  const gain = ac.createGain();
  osc.type = "sine";
  osc.frequency.value = freq;
  const peak = Math.max(0.0001, volume * 0.5);
  const t0 = ac.currentTime + start;
  gain.gain.setValueAtTime(0.0001, t0);
  gain.gain.exponentialRampToValueAtTime(peak, t0 + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, t0 + length);
  osc.connect(gain);
  gain.connect(ac.destination);
  osc.start(t0);
  osc.stop(t0 + length + 0.05);
}

export function playSound(kind, volume) {
  try {
    if (kind === "none" || !(volume > 0)) return;
    const ac = ctx();
    if (!ac) return;
    const v = Math.min(1, Math.max(0, volume));
    if (kind === "beep") {
      tone(ac, 880, 0, 0.25, v);
    } else if (kind === "two beeps") {
      tone(ac, 880, 0, 0.18, v);
      tone(ac, 880, 0.28, 0.18, v);
    } else {
      // chime: three rising notes that ring out
      tone(ac, 659.25, 0, 0.7, v);
      tone(ac, 880, 0.18, 0.7, v);
      tone(ac, 1318.5, 0.36, 1.1, v);
    }
  } catch (err) {
    console.warn("[SY] done alert sound", err);
  }
}

function toast(s) {
  try {
    const box = document.createElement("div");
    box.setAttribute("role", "status");
    box.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:10001;max-width:340px;padding:12px 14px;border-radius:10px;" +
      "font:14px " + FONT + ";background:" + tk("void") + ";color:" + tk("white") + ";border:1px solid " + tk("gold_dim") +
      ";box-shadow:0 8px 30px rgba(0,0,0,.5)";
    const title = document.createElement("div");
    title.textContent = "Done Alert";
    title.style.cssText = "font:700 11px " + FONT + ";letter-spacing:.06em;color:" + tk("gold") + ";margin-bottom:4px";
    const msg = document.createElement("div");
    msg.textContent = s.message;
    box.append(title, msg);
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      const ask = document.createElement("button");
      ask.type = "button";
      ask.textContent = "Allow notices";
      ask.style.cssText = "margin-top:8px;cursor:pointer;border:0;border-radius:6px;padding:4px 9px;font:600 12px " + FONT +
        ";background:" + tk("gold") + ";color:" + tk("void");
      ask.onclick = () => {
        try {
          Notification.requestPermission().then(() => ask.remove()).catch(() => {});
        } catch (_) { /* the browser refused; nothing else to do */ }
      };
      box.append(ask);
    }
    document.body.append(box);
    setTimeout(() => box.remove(), TOAST_MS);
  } catch (err) {
    console.warn("[SY] done alert note", err);
  }
}

function systemNotice(s) {
  try {
    if (typeof Notification === "undefined" || Notification.permission !== "granted") return;
    new Notification("ComfyUI", { body: s.message });
  } catch (_) { /* some browsers only allow this from a service worker */ }
}

function fire(s) {
  playSound(s.sound, s.volume);
  if (s.show_message) toast(s);
  if (s.desktop_notice) systemNotice(s);
}

function queueIsEmpty(q, ownId) {
  const jobs = [...(q?.Running || []), ...(q?.Pending || [])];
  if (!ownId) return jobs.length <= 1; // run id unknown: our own run may still be listed as running
  return jobs.every((j) => (j?.id ?? j?.prompt?.[1]) === ownId); // only the run that sent the alert may be left (new and old queue formats)
}

async function waitThenFire(s, runId) {
  pending = s;
  pendingId = runId || null;
  if (waiting) return;
  waiting = true;
  const t0 = Date.now();
  try {
    while (Date.now() - t0 < POLL_MAX_MS) {
      await new Promise((r) => setTimeout(r, POLL_MS));
      let empty = false;
      try {
        empty = queueIsEmpty(await api.getQueue(), pendingId);
      } catch (_) {
        empty = true; // cannot ask the queue: better to alert than to stay silent
      }
      if (empty) break;
    }
    if (pending) fire(pending);
  } catch (err) {
    console.warn("[SY] done alert wait", err);
  } finally {
    pending = null;
    pendingId = null;
    waiting = false;
  }
}

function onExecuted(ev) {
  try {
    const d = ev.detail || {};
    const node = app.graph?.getNodeById?.(Number(d.node));
    if (!node || node.type !== TYPE) return;
    const raw = d.output?.sy_alert?.[0];
    if (!raw) return;
    const s = JSON.parse(raw);
    if (s.only_when_idle) waitThenFire(s, d.prompt_id);
    else fire(s);
  } catch (err) {
    console.warn("[SY] done alert", err);
  }
}

app.registerExtension({
  name: "sy.done_alert",
  async setup() {
    await loadTheme();
    api.addEventListener("executed", onExecuted);
    // browsers only let sound start after a click: wake the audio on the first one
    window.addEventListener("pointerdown", () => ctx(), { once: true, capture: true });
  },
});
