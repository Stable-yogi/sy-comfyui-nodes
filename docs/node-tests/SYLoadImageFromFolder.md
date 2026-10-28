# Load Image From Folder SY (`SYLoadImageFromFolder`)

Source: `nodes/sy_load_image_from_folder.py`

**What it does:** Loads one picture from a folder inside the ComfyUI input folder. The index picks which one and wraps around.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| subfolder | STRING | yes | Folder inside the input folder. Empty means the input folder itself. | default '' |
| index | INT | yes | Which picture to load, from 0. Too big a number wraps to the start. | 0 to 2147483647, default 0 |
| sort_by | COMBO | yes | Order of the pictures: by file name, or by date (oldest first). | one of: name, date |

Outputs: `IMAGE`, `MASK`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 48, 64, 3]; MASK=tensor[1, 48, 64]; STRING=str 'example.png' |
| 2 | subfolder = '' (empty) | PASS | IMAGE=tensor[1, 48, 64, 3]; MASK=tensor[1, 48, 64]; STRING=str 'example.png' |
| 3 | index = 2147483647 (max) | PASS | IMAGE=tensor[1, 48, 64, 3]; MASK=tensor[1, 48, 64]; STRING=str 'example.png' |
| 4 | index = 1073741823 (mid) | PASS | IMAGE=tensor[1, 48, 64, 3]; MASK=tensor[1, 48, 64]; STRING=str 'example.png' |
| 5 | sort_by = 'date' | PASS | IMAGE=tensor[1, 48, 64, 3]; MASK=tensor[1, 48, 64]; STRING=str 'example.png' |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).
