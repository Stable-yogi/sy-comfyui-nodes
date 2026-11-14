// SY Nodes by Stable Yogi: Video Frame Picker SY. A video player with a timeline slider inside the node.
// Scrub to a frame and leave the slider there: the frame number goes into the "frame" widget, so the saved workflow
// keeps it and the run exports exactly that frame. Frame count and fps come from GET /sy/video/info (read only).
// Text is set with textContent, never innerHTML.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { loadTheme } from "./sy_core.js";
import { tk, button, widgetValue } from "./sy_ui_kit.js";

const FONT = "'DM Sans', sans-serif";
const TYPE = "SYVideoFramePicker";
const PANEL_H = 330;

// frame i shows from i/fps to (i+1)/fps; seek to the middle so the browser never shows the frame before it
export const timeOfFrame = (i, fps) => (i + 0.5) / fps;
export const frameOfTime = (t, fps, frames) => Math.max(0, Math.min(frames - 1, Math.floor(t * fps + 1e-6)));
export const clampFrame = (i, frames) => Math.max(0, Math.min(Math.max(0, frames - 1), Math.round(i)));

function viewUrl(name) {
  let n = String(name || "").replace(/ \[input\]$/, "");
  const cut = n.lastIndexOf("/");
  const sub = cut >= 0 ? n.slice(0, cut) : "";
  const file = cut >= 0 ? n.slice(cut + 1) : n;
  return api.apiURL("/view?type=input&filename=" + encodeURIComponent(file) + "&subfolder=" + encodeURIComponent(sub));
}

function setup(node) {
  const wrap = document.createElement("div");
  wrap.style.cssText = "width:100%;box-sizing:border-box;display:flex;flex-direction:column;gap:4px;font-family:" + FONT;
  const video = document.createElement("video");
  video.muted = true;
  video.playsInline = true;
  video.preload = "auto";
  video.style.cssText = "width:100%;height:" + (PANEL_H - 78) + "px;object-fit:contain;border-radius:6px;background:" + tk("abyss");
  const slider = document.createElement("input");
  slider.type = "range";
  slider.min = "0";
  slider.max = "0";
  slider.step = "1";
  slider.value = "0";
  slider.title = "Drag to scrub. The frame where you leave it is the one the run exports.";
  slider.style.cssText = "width:100%;margin:0;accent-color:" + tk("gold");
  const bar = document.createElement("div");
  bar.style.cssText = "display:flex;flex-wrap:wrap;gap:4px;align-items:center";
  const back10 = button("-10", "ghost", "10 frames back");
  const back1 = button("-1", "ghost", "1 frame back (or the Left arrow key)");
  const play = button("Play", "ghost", "Play or pause the video; the slider follows");
  const fwd1 = button("+1", "ghost", "1 frame forward (or the Right arrow key)");
  const fwd10 = button("+10", "ghost", "10 frames forward");
  const readout = document.createElement("div");
  readout.style.cssText = "font:500 11px " + FONT + ";color:" + tk("white") + ";min-height:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis";
  bar.append(back10, back1, play, fwd1, fwd10);
  wrap.append(video, slider, bar, readout);

  const state = { name: null, fps: 0, frames: 0, frame: 0, error: "" };
  const frameWidget = () => node.widgets?.find((w) => w.name === "frame");

  function show() {
    if (state.error) { readout.textContent = state.error; return; }
    if (!state.frames) { readout.textContent = state.name ? "Reading the video..." : "Pick or upload a video."; return; }
    readout.textContent = "Frame " + state.frame + " (last " + (state.frames - 1) + ")  |  " +
      (state.frame / state.fps).toFixed(3) + " s  |  " + state.fps.toFixed(3) + " fps";
  }
  function setFrame(i, seek = true) {
    state.frame = state.frames ? clampFrame(i, state.frames) : Math.max(0, Math.round(i));
    slider.value = String(state.frame);
    const fw = frameWidget();
    if (fw && fw.value !== state.frame) { fw.value = state.frame; fw.callback?.(state.frame); node.setDirtyCanvas?.(true, true); }
    if (seek && state.fps && Number.isFinite(video.duration)) video.currentTime = Math.min(timeOfFrame(state.frame, state.fps), Math.max(0, video.duration - 0.001));
    show();
  }
  async function load(name) {
    state.name = name;
    state.fps = 0; state.frames = 0; state.error = "";
    slider.max = "0";
    video.pause();
    play.textContent = "Play";
    if (!name || name === "(none)") { video.removeAttribute("src"); video.load(); show(); return; }
    video.src = viewUrl(name);
    show();
    try {
      const r = await api.fetchApi("/sy/video/info?name=" + encodeURIComponent(name));
      const d = await r.json();
      if (state.name !== name) return;   // another video was picked meanwhile
      if (!r.ok || d.error) throw new Error(d.error || ("HTTP " + r.status));
      state.fps = Number(d.fps) || 0;
      state.frames = Number(d.frames) || 0;
      slider.max = String(Math.max(0, state.frames - 1));
      const want = Number(widgetValue(node, "frame", 0)) || 0;
      if (video.readyState >= 1) setFrame(want);
      else video.addEventListener("loadedmetadata", () => setFrame(Number(widgetValue(node, "frame", 0)) || 0), { once: true });
      show();
    } catch (e) {
      if (state.name === name) { state.error = "Could not read the video: " + (e?.message || e); show(); }
    }
  }

  slider.addEventListener("input", () => { video.pause(); play.textContent = "Play"; setFrame(Number(slider.value)); });
  const step = (n) => () => { video.pause(); play.textContent = "Play"; setFrame(state.frame + n); };
  back10.addEventListener("click", step(-10));
  back1.addEventListener("click", step(-1));
  fwd1.addEventListener("click", step(1));
  fwd10.addEventListener("click", step(10));
  play.addEventListener("click", () => {
    if (!state.frames) return;
    if (video.paused) { video.play().catch(() => {}); play.textContent = "Pause"; }
    else { video.pause(); play.textContent = "Play"; setFrame(frameOfTime(video.currentTime, state.fps, state.frames)); }
  });
  video.addEventListener("timeupdate", () => {
    if (!video.paused && state.frames) setFrame(frameOfTime(video.currentTime, state.fps, state.frames), false);
  });
  video.addEventListener("ended", () => { play.textContent = "Play"; setFrame(state.frames - 1, false); });
  wrap.tabIndex = 0;
  wrap.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault(); e.stopPropagation();
      step(e.key === "ArrowLeft" ? -1 : 1)();
    }
  });

  const w = node.addDOMWidget("sy_video_frame_picker_panel", "custom", wrap, { serialize: false });
  w.computeSize = (width) => [width, PANEL_H];
  const tick = setInterval(() => {
    if (!node.graph) {
      if (node._syVfpSeen) clearInterval(tick);
      return;
    }
    node._syVfpSeen = true;
    try {
      const name = widgetValue(node, "video", null);
      if (name !== state.name) load(name);
      const want = Number(widgetValue(node, "frame", 0)) || 0;   // typed into the number box, or loaded from a workflow
      if (state.frames && video.paused && want !== state.frame) setFrame(want);
    } catch (e) {
      console.warn("[SY] video frame picker could not update", e);
    }
  }, 250);
  node.setSize?.([Math.max(node.size?.[0] ?? 0, 360), Math.max(node.size?.[1] ?? 0, node.computeSize?.()[1] ?? 0)]);
  node.__syVideoFramePicker = { state, video, slider, setFrame };   // for the browser check
}

app.registerExtension({
  name: "sy.video_frame_picker",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== TYPE) return;
    await loadTheme();
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        setup(this);
      } catch (e) {
        console.warn("[SY] video frame picker panel not added", e);
      }
      return r;
    };
  },
});
