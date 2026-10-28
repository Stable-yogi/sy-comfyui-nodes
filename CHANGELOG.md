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
