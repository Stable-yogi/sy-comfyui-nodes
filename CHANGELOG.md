# Changelog

## 0.0.1 (unreleased)
- Repo skeleton, theme file, naming checker, standard.
- Seed SY (fixed / random / increment, up to 2^64-1).
- Wave 1 batch A: Resolution, Aspect From Size, Text, Text Join, Find Replace, Prompt Choice, Image Info, Compare Metrics, Run Timer, Free VRAM (all SY). Tensor and ComfyUI paths not run yet.
- Automatic test on every new ComfyUI release (kept outside this repo).
- Batch B2: Image Compare SY (5 modes), Load Image Mini SY, System Info SY (live VRAM and RAM bars, Free memory button), Batch Pick SY.
- Colour palette on right-click (with undo and reset), first-run tour, light and dark theme detection.
- Browser self-check built in for the 3-hour watcher.
- Batches C1-C9: 100+ new nodes: image tools, masks and crop/paste, text and prompt tools, values and logic, sizes and latents, file save/load, model and LoRA helpers, batch/grid/video helpers, dataset and layout helpers. Every node has a tooltip on each input, a description and a test.
- Image Compare slider and Load Image Mini upload/preview buttons (browser side).
- Batches D1 and D2: LLM text helpers (chat/system prompt builders, chunker, token trim, JSON build/get, negative prompts, caption request) and loaders (checkpoint, VAE, CLIP, Unet, name picker) plus video helpers (frame counter, loop, frame rate convert, split, range info). 137 nodes in total.
- Batch E: XY Values List, XY Pick, XY Grid Assemble, XY Label Strip; Paint Mask editor; Set SY / Get SY (wireless links); hover help cards (144 nodes).
- Batch F: 3D Scene SY (no-library 3D scene editor with shaded and depth output); real-file test of the 4 loaders; Paint backdrop and save/reload verified (145 nodes).
- Batch G: Timestamp, Seed Stepper, Seed List, Random Choice, Short ID, Text Stats, Orientation, Colour Swatch (everyday helpers, 153 nodes).
- 3D Scene SY loads .glb model files (up to 3000 triangles, shown as shaded and depth pictures).
- Status dot in the node title: gold ready, yellow missing link, green ran fine, red stopped (setting SY.StatusBadge).
- docs/node-tests/: one test page per node plus an index, made by a harness that tries every option.
- Batches H and I: Frame Count Snap, Duration Frames, Prompt Schedule, Prompt Schedule List, Video Size Fit, Time Code, Number Wrap, Text Repeat, Date Parts, Cycle Pick, Percent Of, Line Pick, Hex Colour Mix, Ratio Split (167 nodes with Set/Get). Node-test docs now cover file nodes in a throw-away folder.
- Batches J and K: LLM Reply Clean, JSON From Reply, Prompt Emphasis Strip, Prompt Diff, Tag Sort, Prompt Sections, Few Shot Block, Text Between, Sentence Pick, Edit Instruction, Multi Ref Label, Character Sheet Prompt, Text In Image, Edit Preset Pick, Edit Steps List (182 nodes with Set/Get). Lora Loader Stack and Sampler Settings Unpack were run in a real graph with a real checkpoint and LoRAs.
