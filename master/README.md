# SY Master Test

Four workflows that together hold every SY node. Use them to check that all nodes still work after a ComfyUI update.

| Workflow file | Groups | Nodes |
|---|---|---|
| `StableYogi-SY-Test-1-Text.json` | Text | 59 |
| `StableYogi-SY-Test-2-Picture.json` | Image, Resize | 82 |
| `StableYogi-SY-Test-3-Tools.json` | Utility, Editors | 68 |
| `StableYogi-SY-Test-4-Numbers-Logic.json` | Values, Logic, Notes | 35 |

Each file also holds the nodes that feed its nodes (a picture, a mask, a seed), in a group called HELPERS or SOURCES. Each node has a Result box next to it.

## Files
- `StableYogi-SY-Test-*.json`: the four workflows. Load one in ComfyUI.
- `prompt_*.json`: the same four in API form, used by the check script.
- `sy_master_fit.py`: makes a copy of each workflow that fits your computer (see below).
- `sy_master_check.py`: the check with no clicking. It writes `master_report.md`.
- `build_master.js` and `build_all_parts.js`: make the workflows again inside a ComfyUI page. Run them after you add a node.
- `StableYogi-SY-Master-Test.json` and `master_prompt.json`: the older one-file version with all nodes. Not used by the check any more.

## What counts as a pass
- Every SY node of every part ran, or says "needs a file" (a model or file this computer does not have: not a fault).
- No node is broken. No node waits behind a broken one.
- No SY node known to ComfyUI is missing from the four prompts.
One part not clean = NOT CLEAN.

## Check by hand
File names differ on every computer, so the workflows must be fitted to yours first.
1. Put one picture (PNG) in the ComfyUI `input` folder. Start ComfyUI.
2. Run: `py -3.12 sy_master_fit.py --port 8188`. It writes a `-fitted` copy of each workflow next to the script. It swaps each model name for a file you have, picks a test picture, and puts a small `notes.txt` in the input folder.
3. Load a fitted file in ComfyUI. Press Run. A red node is a broken node. Write down its name.
(The fitted files hold your own file names. They are not kept in git.)

## Check with no clicking
```
py -3.12 sy_master_check.py --port 8188
```
It needs a PNG in the ComfyUI `input` folder. It prints one line per part and `Result: PASS` or `Result: NOT CLEAN`, and writes `master_report.md`. Exit code 0 = PASS, 1 = NOT CLEAN, 2 = the check could not run (no server).
The 3-hour watcher runs the same check on its test copy after every ComfyUI update.

## Add a new node
1. Open a ComfyUI test copy with the pack loaded. Copy `build_master.js` to `user/default/master_build.js` and `build_all_parts.js` to `user/default/build_all_parts.js` in that ComfyUI.
2. In the browser console: `(0, eval)(await (await fetch('/api/userdata/build_all_parts.js')).text())`. It saves the four workflows and four prompts in that ComfyUI's `user/default` folder (`workflows/` and the folder itself).
3. If the new node refuses empty text or needs a wire, add a sample value to `FILL` or `over` in `build_master.js` first.
4. Copy the eight files here. Run the check.
5. A new group needs a place in `PARTS` in `build_master.js` (and in `build_all_parts.js` if you add a fifth part).
