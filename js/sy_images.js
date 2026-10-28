// SY Nodes by Stable Yogi: browser parts for Image Compare (slider) and Load Image Mini (upload + preview).
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { pal } from "./sy_core.js";

function viewUrl(f) {
  return api.apiURL("/view?filename=" + encodeURIComponent(f.filename) + "&type=" + (f.type || "input") +
    "&subfolder=" + encodeURIComponent(f.subfolder || "") + "&rand=" + Math.random());
}

function addCompareView(node) {
  const P = pal();
  const box = document.createElement("div");
  box.style.cssText = "position:relative;width:100%;height:100%;min-height:160px;overflow:hidden;border-radius:6px;background:" + P.surface;
  const imgB = document.createElement("img");
  const imgA = document.createElement("img");
  for (const im of [imgA, imgB]) {
    im.style.cssText = "position:absolute;inset:0;width:100%;height:calc(100% - 26px);object-fit:contain";
    im.alt = "";
    box.append(im);
  }
  const hint = document.createElement("div");
  hint.textContent = "Run the workflow to see both pictures here. Drag the slider to compare.";
  hint.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:8px;text-align:center;font:12px 'DM Sans',sans-serif;color:" + P.text;
  box.append(hint);
  const line = document.createElement("div");
  line.style.cssText = "position:absolute;top:0;bottom:26px;width:2px;background:" + P.gold + ";left:50%;pointer-events:none;display:none";
  box.append(line);
  const slider = document.createElement("input");
  slider.type = "range";
  slider.min = "0";
  slider.max = "100";
  slider.value = "50";
  slider.setAttribute("aria-label", "Compare slider: left shows A, right shows B");
  slider.style.cssText = "position:absolute;left:6px;right:6px;bottom:2px;height:22px;margin:0";
  box.append(slider);
  const apply = () => {
    const v = Number(slider.value);
    imgA.style.clipPath = "inset(0 " + (100 - v) + "% 0 0)";
    line.style.left = v + "%";
  };
  slider.addEventListener("input", apply);
  apply();
  const widget = node.addDOMWidget("sy_compare_view", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 220];
  node._syCompareShow = (files) => {
    if (!files || files.length < 2) return;
    imgA.src = viewUrl(files[0]);
    imgB.src = viewUrl(files[1]);
    hint.style.display = "none";
    line.style.display = "block";
  };
}

function addLoadMini(node) {
  const P = pal();
  const combo = node.widgets?.find((w) => w.name === "image");
  if (!combo) return;
  const box = document.createElement("div");
  box.style.cssText = "display:flex;flex-direction:column;gap:4px;width:100%;height:100%";
  const img = document.createElement("img");
  img.alt = "Preview of the chosen picture";
  img.style.cssText = "flex:1;min-height:80px;width:100%;object-fit:contain;border-radius:6px;background:" + P.surface;
  const row = document.createElement("div");
  row.style.cssText = "display:flex;gap:6px";
  const mk = (text, tip) => {
    const b = document.createElement("button");
    b.textContent = text;
    b.title = tip;
    b.style.cssText = "flex:1;cursor:pointer;border-radius:6px;border:1px solid " + P.gold_dim + ";background:transparent;color:inherit;padding:3px 6px;font:12px 'DM Sans',sans-serif";
    return b;
  };
  const up = mk("Upload picture", "Choose a picture on this computer. It is copied to the ComfyUI input folder.");
  const re = mk("Refresh list", "Look again at the files in the input folder.");
  const note = document.createElement("div");
  note.style.cssText = "font:11px 'DM Sans',sans-serif;opacity:.8";
  row.append(up, re);
  box.append(img, row, note);
  const show = () => {
    if (combo.value) img.src = viewUrl({ filename: combo.value, type: "input" });
  };
  const orig = combo.callback;
  combo.callback = function () {
    show();
    if (orig) return orig.apply(this, arguments);
  };
  const file = document.createElement("input");
  file.type = "file";
  file.accept = "image/*";
  file.style.display = "none";
  up.onclick = () => file.click();
  file.onchange = async () => {
    const f = file.files?.[0];
    if (!f) return;
    note.textContent = "Uploading...";
    try {
      const body = new FormData();
      body.append("image", f);
      body.append("type", "input");
      const res = await api.fetchApi("/upload/image", { method: "POST", body });
      if (!res.ok) throw new Error("upload answered " + res.status);
      const data = await res.json();
      const name = data.subfolder ? data.subfolder + "/" + data.name : data.name;
      if (!combo.options.values.includes(name)) combo.options.values.push(name);
      combo.value = name;
      show();
      note.textContent = "Uploaded: " + name;
    } catch (e) {
      note.textContent = "Upload failed. Try a smaller picture.";
      console.warn("[SY] upload failed", e);
    }
    file.value = "";
  };
  re.onclick = async () => {
    try {
      const info = await (await api.fetchApi("/object_info/SYLoadImageMini")).json();
      const list = info.SYLoadImageMini?.input?.required?.image?.[0];
      if (Array.isArray(list)) {
        combo.options.values = list;
        note.textContent = list.length + " pictures in the input folder.";
      }
    } catch (e) {
      note.textContent = "Could not read the list.";
    }
  };
  const widget = node.addDOMWidget("sy_load_view", "custom", box, { serialize: false });
  widget.computeSize = (w) => [w, 190];
  setTimeout(show, 300);
}

app.registerExtension({
  name: "sy.images",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const name = nodeData.name;
    if (name !== "SYImageCompare" && name !== "SYLoadImageMini") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created ? created.apply(this, arguments) : undefined;
      try {
        if (name === "SYImageCompare") addCompareView(this);
        else addLoadMini(this);
      } catch (e) {
        console.warn("[SY] image view not shown", e);
      }
      return r;
    };
    if (name === "SYImageCompare") {
      const executed = nodeType.prototype.onExecuted;
      nodeType.prototype.onExecuted = function (msg) {
        if (executed) executed.apply(this, arguments);
        if (this._syCompareShow) this._syCompareShow(msg?.sy_compare);
      };
    }
  },
});
