# SY Master Test

One workflow that holds every SY node. Use it to check that all nodes still work after a ComfyUI update.

## Files
- `StableYogi-SY-Master-Test.json`: the workflow. Load it in ComfyUI. Every SY node sits in a group by node group, with a Result box next to it.
- `master_prompt.json`: the same graph in API form, used by the check script.
- `sy_master_fit.py`: makes a copy of the workflow that fits your computer (see below).
- `sy_master_check.py`: the check with no clicking. It sends the graph to ComfyUI, takes out each broken node, and sends it again. It writes `master_report.md`.
- `build_master.js`: makes the workflow again inside a ComfyUI page. Run it after you add a node.

## Check by hand
File names differ on every computer, so the workflow must be fitted to yours first.
1. Put one picture (PNG) in the ComfyUI `input` folder. Start ComfyUI.
2. Run: `py -3.12 sy_master_fit.py --port 8188`. It writes `StableYogi-SY-Master-Test-fitted.json` next to the script. It swaps each model name for a file you have, picks a test picture, and puts a small `notes.txt` in the input folder.
3. Load the fitted file in ComfyUI. Press Run. A red node is a broken node. Write down its name.
(The fitted file holds your own file names. It is not kept in git.)

## Check with no clicking
```
py -3.12 sy_master_check.py --port 8188
```
It needs a PNG in the ComfyUI `input` folder. It prints `Result: PASS` or `Result: NOT CLEAN` and writes `master_report.md`.
- PASS: every SY node ran. Two nodes may say "needs a file" (checkpoint list and safetensors header): they need a model file on the computer.
- NOT CLEAN: the report names each broken node and the error text. A node in the pack that is not in the master is also listed.

## Add a new node
1. Open a ComfyUI page with the pack loaded.
2. Run `build_master.js` in the browser console, as the first lines of the file say.
3. If the new node refuses empty text or needs a wire, add a sample value to `FILL` or `over` in the script.
4. Save the workflow and the API graph, copy them here, run the check.
