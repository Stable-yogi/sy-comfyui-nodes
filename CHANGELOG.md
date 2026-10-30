# Changelog

## 1.3.0
- Face Detect SY: finds faces and makes a mask (box or oval) for Inpaint Crop SY. Built-in detector needs only the opencv package; an optional YuNet .onnx file in models/sy_face_detect gives better results. No face found gives an empty mask and no error.

## 1.2.0
- IndexSwitch SY: pick one of up to four inputs by number. Only the chosen branch runs.

## 1.1.0
- GGUF loaders: Unet, CLIP and Dual CLIP (SY versions, same file names and results as the outside loader). Needs the `gguf` pip package.
- H3 Speed Optimizer SY and H3 Low VRAM SY (speed-up and memory helpers for the H3 video model; the sparse kernel is not bundled).

## 1.0.0
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
- docs/nodes/: one help page per node (inputs and what it does).
- Batches H and I: Frame Count Snap, Duration Frames, Prompt Schedule, Prompt Schedule List, Video Size Fit, Time Code, Number Wrap, Text Repeat, Date Parts, Cycle Pick, Percent Of, Line Pick, Hex Colour Mix, Ratio Split (167 nodes with Set/Get). Node-test docs now cover file nodes in a throw-away folder.
- Batches J and K: LLM Reply Clean, JSON From Reply, Prompt Emphasis Strip, Prompt Diff, Tag Sort, Prompt Sections, Few Shot Block, Text Between, Sentence Pick, Edit Instruction, Multi Ref Label, Character Sheet Prompt, Text In Image, Edit Preset Pick, Edit Steps List (182 nodes with Set/Get). Lora Loader Stack and Sampler Settings Unpack were run in a real graph with a real checkpoint and LoRAs.
- Look update: nodes are coloured by job (loaders blue, working nodes green, text teal, numbers and logic purple, save brown, notes gold) with white titles; setting "SY.ColorMode" (Role colours, Group colours, Gold only, Off).
- Workflow Header SY: a title banner with three buttons (Nodes to Install, How to Use, Nodes Info) and an edit panel; the texts travel inside the workflow file.
- Save Image To Folder SY: token buttons (+Date +Time +Seed +Counter +Width +Height +Batch +Model +Input), live "Will save as" line, Open / Copy / Folder buttons, Browse folders, PNG / JPG / WebP and Save / Preview switches, date folder, picture grid with n/N badges and a size line. New tokens width, height, batch, model, input.
- Load Image From Folder SY: Browse folders button and a "picks picture n of m" line.
- Folder helper routes /sy/folder/list, /plan, /open: limited to the ComfyUI output and input folders, picture files only (the one audited place that opens Explorer).
- Time badge on each node after a run and a run clock in the top right corner (settings SY.TimeBadge, SY.RunClock).
- Browser parts (js/sy_header.js, js/sy_save.js, js/sy_runtime.js, js/sy_ui_kit.js) were run on the CPU test ComfyUI: banner, token buttons, Will save as, preview mode, picker window and graph reload checked. Open and Folder buttons (Explorer) were not clicked in the test.
- Krea 2 Turbo W01 replacement rebuilt with the header, role colours and a 20 px grid (181 nodes in the pack).
- Colour roles split: sampler, second sampler, seed, pick and save, decode, preview and save now have their own colours (js/sy_theme.json).
- Master test: one workflow with all 181 SY nodes plus sy_master_check.py, which runs it on a ComfyUI server and reports which node is broken (folder master/). Use it after every ComfyUI update.
- Master test split in 4 workflows (Text 52, Picture 51, Tools 48, Numbers and logic 29 nodes, plus the header in each) with a written pass rule. sy_master_check.py runs all four and checks that no SY node is missing; sy_master_fit.py fits all four to one computer; the 3-hour watcher runs the check after every ComfyUI update.
- CLIP Loader SY now reads the type list from your ComfyUI, so new model families (for example minimax) work without an update here.
- Older nodes now in this pack with the same ids as before, so saved workflows still load: Inpaint Crop SY, Inpaint Stitch SY, Krea2 One-Click SY. New: H3 Save Bundle SY and H3 Load Bundle SY (save and reload a latent, prompt, seed and up to 3 reference pictures as one folder). 186 nodes with Set/Get.
- Five Krea 2 nodes added, ported from open-source packs (licences and authors in NOTICE.md and third_party/): Krea2 Edit Model Patch SY, Krea2 Edit Grounded Encode SY, Krea2 Conditioning Rebalance SY, Krea2T Enhancer SY, Krea2T Enhancer Advanced SY. Same inputs and outputs as the originals, new SY ids so both can exist side by side. 191 nodes with Set/Get. Not run on a real Krea 2 model yet.
- Krea2T Enhancer Advanced SY: on a wrong text shape the node now passes its own saved forward function (the original raised an error there). Changed by Stable Yogi.
- Master test rebuilt so all 191 nodes are in the four test prompts (the 10 newest nodes were missing, which failed the ComfyUI v0.43.0 check). A node that cannot find a model file now counts as "needs a file", not as a fault.
- H3 Save Bundle SY now saves a latent that holds video and audio together (a nested tensor). Before, it stopped with "latent holds no tensor to save". H3 Load Bundle SY rebuilds it in the same order. Run on a real H3 preview file.
- H3 Latent Upscaler SY added (192 nodes). It makes an H3 video latent bigger (by a multiplier, to a size, or to a megapixel count) with the 3D upscale model, in chunks for long clips. Rebuilt from the MIT-licensed ComfyUI Minimax H3 Latent Upscaler by LBH-123-AI (licence in third_party/, row in NOTICE.md). Same result as the original on the real model file. Changed by Stable Yogi: clear errors, size planning, node name and grouping.
- Master test: the Tools part now holds H3LatentUpscaler SY too (192 nodes in the four test prompts). A node that needs a real H3 latent counts as "needs a file", not as a fault.
- README written: what you need (ComfyUI v0.42.1 or newer; tested on v0.42.1 and v0.43.0), install, update, groups, troubleshooting. Full node list in docs/NODES.md.
