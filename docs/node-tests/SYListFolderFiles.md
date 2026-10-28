# List Folder Files SY (`SYListFolderFiles`)

Source: `nodes/sy_list_folder_files.py`

**What it does:** Lists the files in a folder inside the input or output folder, one per line, with a count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| root | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output |
| subfolder | STRING | yes | Folder inside it. Empty means the folder itself. | default '' |
| extensions | STRING | yes | File endings to keep, like png, jpg or txt. Empty lists every file. | default '' |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'example.png notes.txt'; INT=int 2 |
| 2 | root = 'output' | PASS | STRING=str ''; INT=int 0 |
| 3 | subfolder = '' (empty) | PASS | STRING=str 'example.png notes.txt'; INT=int 2 |
| 4 | extensions = '' (empty) | PASS | STRING=str 'example.png notes.txt'; INT=int 2 |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
