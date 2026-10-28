// Builds the SY Master Test workflow inside a ComfyUI page. Run it in the browser console of the test copy:
//   (0, eval)(await (await fetch('/api/userdata/master_build.js')).text())
// It makes one node for every SY node, wires the inputs, adds a preview for every result, groups by category,
// then saves the workflow and its API prompt next to each other.
// One part only: set window.__masterPart to "text", "picture", "tools" or "numbers" first. Without it you get all nodes in one file.
(async () => {
  const app = window.app, LG = window.LiteGraph, graph = app.graph;
  graph.clear();
  const PARTS = {
    text: { n: 1, name: "Text", cats: ["SY/Text"] },
    picture: { n: 2, name: "Picture", cats: ["SY/Image", "SY/Resize"] },
    tools: { n: 3, name: "Tools", cats: ["SY/Utility", "SY/Editors"] },
    numbers: { n: 4, name: "Numbers and logic", cats: ["SY/Values", "SY/Logic", "SY/Notes"] },
  };
  const PART = PARTS[window.__masterPart] || null;
  const log = { missing: [], noSink: [], noInput: [], made: 0 };
  const mk = (type, title) => {
    const n = LG.createNode(type);
    if (!n) { log.missing.push(type); return null; }
    if (title) n.title = title;
    graph.add(n);
    return n;
  };
  const size = (n) => { const s = n.computeSize(); n.size = [Math.max(s[0], n.size[0] || 0, 260), Math.max(s[1], 60)]; };

  // ---- sources
  const types = Object.entries(LG.registered_node_types)
    .filter(([t, c]) => t.startsWith("SY") && (c.nodeData?.category || "").startsWith("SY/") && t !== "SYWorkflowHeader")
    .map(([t, c]) => ({ t, cat: c.nodeData.category, name: c.nodeData.display_name || t }))
    .sort((a, b) => a.cat.localeCompare(b.cat) || a.name.localeCompare(b.name));
  const head = mk("SYWorkflowHeader", "Workflow Header SY");
  const load = mk("LoadImage", "Test picture (any picture works)");
  const toMask = mk("ImageToMask", "Test mask (from the picture)");
  toMask.widgets.find((w) => w.name === "channel").value = "red";
  const seedSrc = mk("SYSeed", "Seed source");
  const unet = mk("SYUnetLoader", "Model: Muse by Stable Yogi, Turbo");
  const clip = mk("SYCLIPLoader", "Text encoder");
  // the same file names as the Krea 2 Turbo W01 workflow
  const setCombo = (n, name, value) => { const w = n.widgets.find((x) => x.name === name); if (w) w.value = value; };
  const setFirst = (n, i, value) => { if (n.widgets?.[i]) n.widgets[i].value = value; };
  setFirst(unet, 0, "Muse by Stable Yogi Krea2 V3.0 Pro INT8-ConvRot C81.safetensors");
  setFirst(clip, 0, "qwen3vl_4b_fp8_scaled.safetensors");
  setFirst(clip, 1, "krea2");
  load.connect(0, toMask, 0);
  const yes = mk("PrimitiveBoolean", "A yes value (for Assert)");
  yes.widgets[0].value = true;
  const two = mk("ImageBatch", "Two pictures as one batch (for frame nodes)");
  load.connect(0, two, 0); load.connect(0, two, 1);

  const byType = {};
  const nodes = [];
  for (const { t, cat } of types) {
    if (t === "SYUnetLoader" || t === "SYCLIPLoader" || t === "SYSeed") { byType[t] = t === "SYSeed" ? seedSrc : t === "SYUnetLoader" ? unet : clip; nodes.push({ n: byType[t], cat, t, src: true }); continue; }
    const n = mk(t);
    if (!n) continue;
    byType[t] = n;
    nodes.push({ n, cat, t });
    log.made++;
  }
  // a producer for each special type
  const producerOf = {};
  for (const { n } of nodes) for (const [i, o] of (n.outputs || []).entries()) if (!(o.type in producerOf) && !n.inputs?.some((x) => !x.widget)) producerOf[o.type] = [n, i];

  // ---- wiring
  const over = {
    SYFreeVRAM: { value: [load, 0] }, SYRunTimer: { value: [load, 0] },
    SYShowText: { value: [seedSrc, 0] }, SYTextNumberFormat: { number_in: [seedSrc, 0] },
    SYSwitch: { a: [load, 0], b: [byType.SYColourSwatch, 0] },
    SYLayoutBoxesMerge: { boxes_3: [byType.SYLayoutBox, 0], boxes_4: [byType.SYLayoutBox, 0] },
    SYAssert: { condition: [yes, 0] }, SYFrameInterpolateBlend: { images: [two, 0] },
  };
  for (const { n, t } of nodes) {
    const ins = (n.inputs || []).filter((i) => !i.widget);
    for (const inp of ins) {
      if (inp.link != null) continue;
      const k = n.inputs.indexOf(inp);
      let from = over[t]?.[inp.name];
      if (!from) {
        if (inp.type === "IMAGE") from = [load, 0];
        else if (inp.type === "MASK") from = [toMask, 0];
        else if (inp.type === "MODEL") from = [unet, 0];
        else if (inp.type === "CLIP") from = [clip, 0];
        else if (producerOf[inp.type]) from = producerOf[inp.type];
      }
      if (from && from[0] && from[0] !== n) from[0].connect(from[1], n, k); else log.noInput.push(t + "." + inp.name);
    }
  }

  // ---- sample values for nodes that refuse empty text, and wires into text boxes
  const FILL = {
    SYCharacterSheetPrompt: { character: "a knight in silver armour" },
    SYChatPromptBuilder: { system: "You are a helpful guide.", user: "Say hello." },
    SYCyclePick: { items: "one\ntwo\nthree" },
    SYEmptyLatent: { latent_type: "flux 16ch /8" },
    SYEditInstruction: { target: "the sky", to_value: "a sunset sky" },
    SYEditStepsList: { step_1: "remove the lamp", step_2: "add a tree" },
    SYFewShotBlock: { task: "Translate to French", new_input: "hello" },
    SYImageMetadataReader: { file: load.widgets[0].value },
    SYJSONFieldGet: { json_text: '{"a": {"b": 2}}', path: "a.b" },
    SYJSONFromReply: { text: 'Here you go: {"a": 1}' },
    SYLinePick: { text: "one\ntwo\nthree" },
    SYMultiRefLabel: { task: "Put the cat next to the dog", ref_1: "a cat", ref_2: "a dog" },
    SYPromptEnhanceRequest: { idea: "a fox in the snow" },
    SYRandomChoice: { lines: "one\ntwo\nthree" },
    SYSaveWithCaption: { caption: "master test" },
    SYTagFrequency: { captions: "cat, dog\ncat, bird" },
    SYTextBetween: { text: "a [b] c", start_marker: "[", end_marker: "]" },
    SYTextChunker: { text: "one two three four five six seven eight nine ten" },
    SYTextContains: { text: "a blue cat", needle: "cat" },
    SYTextInImage: { text: "SY" },
    SYTextSplitLines: { text: "one\ntwo\nthree" },
    SYXYLabelStrip: { x_values: "1, 2, 3", y_values: "a, b" },
  };
  for (const [cls, vals] of Object.entries(FILL)) {
    const n = byType[cls]; if (!n) continue;
    for (const [k, v] of Object.entries(vals)) { const w = n.widgets.find((x) => x.name === k); if (w) w.value = v; else log.noInput.push(cls + "." + k + " (no box)"); }
  }
  const WIRE = [["SYPasteBack", "crop", "SYCropByMask", 0], ["SYPasteBack", "crop_info", "SYCropByMask", 2],
    ["SYLayoutBoxesMerge", "boxes_1", "SYLayoutBox", 0], ["SYLayoutBoxesMerge", "boxes_2", "SYLayoutBox", 0], ["SYLayoutBoxesPreview", "layout_boxes", "SYLayoutBox", 0]];
  for (const [to, input, from, slot] of WIRE) {
    const d = byType[to], s = byType[from]; if (!d || !s) { log.noInput.push(to + "." + input); continue; }
    const k = d.inputs.findIndex((i) => i.name === input);
    if (k < 0) { log.noInput.push(to + "." + input + " (no socket)"); continue; }
    s.connect(slot, d, k);
  }

  // ---- a preview for the first useful output of every node
  const sinkOf = (n) => {
    for (const [i, o] of (n.outputs || []).entries()) {
      if (o.type === "IMAGE") { const p = mk("PreviewImage", "Result: picture"); n.connect(i, p, 0); return [p]; }
      if (o.type === "MASK") {
        const m = mk("MaskToImage", "Mask as picture"); n.connect(i, m, 0);
        const p = mk("PreviewImage", "Result: mask"); m.connect(0, p, 0); return [m, p];
      }
      if (["STRING", "INT", "FLOAT", "BOOLEAN", "*"].includes(o.type)) { const p = mk("PreviewAny", "Result: " + o.name); n.connect(i, p, 0); return [p]; }
    }
    return [];
  };
  const cells = [];
  for (const rec of nodes) {
    if (rec.n === unet || rec.n === clip) { cells.push({ ...rec, sinks: [] }); continue; }
    let sinks = rec.n.constructor?.nodeData?.output_node ? [] : sinkOf(rec.n);
    if (rec.t === "SYVAELoader") {
      setFirst(rec.n, 0, "qwen_image_vae.safetensors");
      // a VAE decode needs a latent that fits that VAE (the Qwen VAE wants 5 dimensions): show the two results instead
      const p1 = mk("PreviewAny", "Result: VAE"), p2 = mk("PreviewAny", "Result: empty latent");
      rec.n.connect(0, p1, 0); byType.SYEmptyLatent.connect(0, p2, 0); sinks = [p1, p2];
    }
    if (!sinks.length && !rec.n.constructor?.nodeData?.output_node) log.noSink.push(rec.t);
    cells.push({ ...rec, sinks });
  }
  // ---- one part: keep its nodes and whatever feeds them, drop the rest
  if (PART) {
    const keep = new Set([load]);
    const up = (n) => {
      if (!n || keep.has(n)) return;
      keep.add(n);
      for (const i of n.inputs || []) if (i.link != null) { const l = graph.links[i.link]; if (l) up(graph.getNodeById(l.origin_id)); }
    };
    for (const c of cells) if (PART.cats.includes(c.cat)) { up(c.n); c.sinks.forEach(up); }
    for (const n of [...graph._nodes]) if (!keep.has(n) && n !== head) graph.remove(n);
    for (let i = cells.length - 1; i >= 0; i--) if (!keep.has(cells[i].n)) cells.splice(i, 1);
    for (const c of cells) { c.sinks = c.sinks.filter((s) => keep.has(s)); if (!PART.cats.includes(c.cat)) c.cat = "HELPERS"; }
    log.part = PART.name; log.partNodes = cells.filter((c) => c.cat !== "HELPERS").length;
  }
  // ---- layout
  const GAP = 60, TITLE = 30;
  for (const c of cells) { size(c.n); for (const s of c.sinks) { s.size = s.type === "PreviewImage" ? [240, 240] : (s.type === "MaskToImage" || s.type === "VAEDecode") ? [200, 60] : [240, 110]; } }
  const groups = [];
  const placeGroup = (title, list, x0, y0, cols, color) => {
    let x = x0 + 20, y = y0 + 80, rowH = 0, col = 0, maxX = x0 + 400;
    for (const c of list) {
      const sinkW = c.sinks.length ? 260 + GAP : 0;
      const sinkH = c.sinks.reduce((a, s) => a + s.size[1] + TITLE + 20, 0);
      c.n.pos = [x, y + TITLE];
      let sx = x + c.n.size[0] + GAP, sy = y + TITLE;
      for (const s of c.sinks) { s.pos = [sx, sy]; sy += s.size[1] + TITLE + 20; }
      const w = c.n.size[0] + sinkW, h = Math.max(c.n.size[1], sinkH) + TITLE;
      rowH = Math.max(rowH, h); maxX = Math.max(maxX, x + w);
      col++;
      if (col >= cols) { col = 0; x = x0 + 20; y += rowH + GAP; rowH = 0; } else x += w + GAP;
    }
    const bottom = col === 0 ? y : y + rowH;
    groups.push({ title, bounding: [x0, y0, maxX - x0 + 40, bottom - y0 + 40], color, font_size: 28 });
    return bottom + 40 + GAP;
  };
  const theme = await (await fetch("/extensions/sy-comfyui-nodes/sy_theme.json")).json().catch(() => null);
  const roleColor = (cat) => { const g = cat.replace("SY/", ""); const r = theme?.group_roles?.[g]; return (r && theme.roles[r]?.color) || "#3f3f3f"; };
  head.pos = [20, 40]; head.size = [1800, 170];
  let y = 280;
  // sources group
  const srcList = [{ n: load, sinks: [] }, { n: toMask, sinks: [] }, { n: two, sinks: [] }, { n: yes, sinks: [] }, { n: seedSrc, sinks: [] }, { n: unet, sinks: [] }, { n: clip, sinks: [] }]
    .filter((s) => !PART || graph._nodes.includes(s.n));
  for (const c of srcList) size(c.n);
  y = placeGroup("SOURCES: picture, mask, seed, two model files", srcList, 0, y, 5, "#1f4e79");
  const order = ["SY/Image", "SY/Resize", "SY/Editors", "SY/Text", "SY/Values", "SY/Logic", "SY/Utility", "SY/Notes", "HELPERS"];
  for (const cat of order) {
    const list = cells.filter((c) => c.cat === cat && !srcList.some((s) => s.n === c.n));
    if (list.length) y = placeGroup(cat.replace("SY/", "").toUpperCase() + " nodes (" + list.length + ")", list, 0, y, 5, roleColor(cat));
  }
  for (const [i, g] of groups.entries()) { const gr = new LG.LGraphGroup(g.title); gr.color = g.color; gr.font_size = g.font_size; gr.pos = [g.bounding[0], g.bounding[1]]; gr.size = [g.bounding[2], g.bounding[3]]; graph.add(gr); }

  head.properties.sy_title = PART ? "SY Test " + PART.n + " of 4: " + PART.name : "SY Master Test";
  head.properties.sy_subtitle = PART ? "Groups: " + PART.cats.map((c) => c.replace("SY/", "")).join(", ") + ". Press Run after each ComfyUI update." : "Every SY node in one workflow. Press Run after each ComfyUI update.";
  head.properties.sy_install = "This workflow needs only SY Nodes by Stable Yogi.\nTwo model files make the model nodes work: the Krea 2 Turbo model and the Qwen text encoder (the same two as in the Krea 2 Turbo workflow).\nThe test picture is the first picture in your ComfyUI input folder.";
  head.properties.sy_howto = "1. Press Run.\n2. Every SY node runs once. Each one has a Result box next to it.\n3. A red node means that node is broken now. Write down its name.\n4. Model nodes stay red if the two model files are missing. That is fine.\n\nFor a report with no clicking, run sy_master_check.py (see the docs).";
  head.properties.sy_info = "Groups follow the node groups: Image, Resize, Editors, Text, Values, Logic, Utility, Notes.\nThe SOURCES box feeds one picture, one mask and one seed to all nodes.\nWires can be hidden with the link button at the bottom right of the canvas.";
  head._syBannerRefresh && head._syBannerRefresh();
  app.canvas.setDirty(true, true);
  window.__masterLog = log;
  return JSON.stringify({ nodesInGraph: graph._nodes.length, groups: groups.length, ...log });
})();
