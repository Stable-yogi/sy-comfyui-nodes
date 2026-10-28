# Folder Image Count SY (`SYFolderImageCount`)

Source: `nodes/sy_folder_image_count.py`

**What it does:** Counts the picture files (png, jpg, jpeg, webp, bmp, gif, tif) in a folder inside the input or output folder.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| root | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output |
| subfolder | STRING | yes | Folder inside it. Empty means the folder itself. | default '' |

Outputs: `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 1 |
| 2 | root = 'output' | PASS | INT=int 0 |
| 3 | subfolder = '' (empty) | PASS | INT=int 1 |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
