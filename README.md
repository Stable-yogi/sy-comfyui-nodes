# SY Nodes for ComfyUI

199 helper nodes by Stable Yogi. Every node name ends with **SY** and sits in the **SY** folder of the node library.
They load models, set sizes and seeds, switch parts of a graph on and off, edit masks and pictures, work with text,
and save results. Our workflows use them, so one install of this pack gives you the nodes the workflows need.

License: MIT. See `LICENSE` and `NOTICE.md`.

Missing a node? Tell me.

## What you need

| | |
|---|---|
| ComfyUI | **v0.42.1 or newer.** Tested on v0.42.1 and v0.43.0. Older versions are not tested. |
| Python packages | Most nodes use only what ComfyUI already has. A few need one extra package (the node page says which). If it is missing, the node tells you so and how to add it. |
| Models | The nodes hold none. A workflow tells you which model files it needs (see its banner). |

The H3 video workflows need a ComfyUI that knows the H3 model type (it is in v0.42.1 and newer).

## Install

1. Close ComfyUI.
2. Put the `sy-comfyui-nodes` folder into `ComfyUI/custom_nodes/`.
   (Or run `git clone https://github.com/Stable-yogi/sy-comfyui-nodes` inside that folder.)
3. Start ComfyUI. Look for a **SY** folder in the node library (double-click the canvas and type `SY`).

**Do not keep two copies.** If you have an older folder called `sy-nodes` or an older `sy-comfyui-nodes` in
`custom_nodes`, remove it first. Two copies use the same node names and clash.

## Update

Replace the folder with the new one and restart ComfyUI. Saved workflows keep working: node names and ids do not change.

## The groups

| Group | Nodes | What is in it |
|---|---|---|
| SY/Text | 52 | Prompt and caption helpers, text join, find and replace, JSON, chat prompt builders |
| SY/Image | 43 | Picture tools, masks, crop and paste, compare, grids, loaders and save steps |
| SY/Resize | 10 | Sizes, aspect ratios, video sizes, H3 latent upscaler |
| SY/Values | 20 | Seed, numbers, switches, lists |
| SY/Logic | 9 | Switch, pick by number, compare, gate |
| SY/Utility | 53 | Model and LoRA loaders, batch and video helpers, timers, memory tools, H3 bundle save and load |
| SY/Editors | 10 | Mask editor, 3D scene, XY grids, paint |
| SY/Notes | 2 | Workflow header and notes |

The full list: [`docs/NODES.md`](docs/NODES.md). Every node has its own help page in [`docs/nodes/`](docs/nodes/)
with its inputs and what it does.

## Workflows that use the pack

Our workflows put an install box at the top. It names this pack, the model files the workflow needs, and the folder each file goes in.
Some workflows also use free packs from other authors. The banner of each workflow lists the ones it uses.
Face Detect SY uses the `opencv-python-headless` package for its built-in detector. If it is missing, the node tells you how to add it.

## If something does not work

- **Red nodes with "missing" on load.** The pack is not in `custom_nodes`, or ComfyUI was not restarted. Do both again.
- **Node shows twice, or the wrong list.** An older copy is still in `custom_nodes`. Remove it and restart.
- **"model not found" or an empty model list.** Put the model file in the folder named in the workflow banner, then press `r` in ComfyUI to refresh.
- **H3LatentUpscaler SY needs its model.** Download the upscaler model file from its author (Apache-2.0) and put it in `ComfyUI/models/latent_upscale_models`.
- **Your ComfyUI is older than v0.42.1.** Update ComfyUI first.
- **Still stuck.** Open an issue here and tell us your ComfyUI version, the node name, and the red error text.

## Tests

Each ComfyUI release is checked with four test workflows that hold every SY node (folder `master/`).
Result for v0.42.1 and v0.43.0: all nodes pass.

## Credits

Written by Stable Yogi. Some nodes are rebuilt from open-source packs under their
open-source licences. The authors and licences are listed in `NOTICE.md` and in `third_party/`.
