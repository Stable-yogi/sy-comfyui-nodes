# Size Presets SY (`SYSizePresets`)

Source: `nodes/sy_size_presets.py`

**What it does:** Pick a common picture size by name, like 1024x1024 square or 2048x1152 wide. Gives a width and a height.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | A common picture size. Portrait is taller than wide. | one of: 512x512 square, 512x768 portrait, 768x512 landscape, 768x768 square, 768x1024 portrait, 1024x768 landscape, 832x1216 portrait, 1216x832 landscape, 896x1152 portrait, 1152x896 landscape, 1024x1024 square, 1024x1536 portrait ... |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 512; INT=int 512 |
| 2 | preset = '512x768 portrait' | PASS | INT=int 512; INT=int 768 |
| 3 | preset = '768x512 landscape' | PASS | INT=int 768; INT=int 512 |
| 4 | preset = '768x768 square' | PASS | INT=int 768; INT=int 768 |
| 5 | preset = '768x1024 portrait' | PASS | INT=int 768; INT=int 1024 |
| 6 | preset = '1024x768 landscape' | PASS | INT=int 1024; INT=int 768 |
| 7 | preset = '832x1216 portrait' | PASS | INT=int 832; INT=int 1216 |
| 8 | preset = '1216x832 landscape' | PASS | INT=int 1216; INT=int 832 |
| 9 | preset = '896x1152 portrait' | PASS | INT=int 896; INT=int 1152 |
| 10 | preset = '1152x896 landscape' | PASS | INT=int 1152; INT=int 896 |
| 11 | preset = '1024x1024 square' | PASS | INT=int 1024; INT=int 1024 |
| 12 | preset = '1024x1536 portrait' | PASS | INT=int 1024; INT=int 1536 |
| 13 | preset = '1536x1024 landscape' | PASS | INT=int 1536; INT=int 1024 |
| 14 | preset = '720x1280 portrait 9:16' | PASS | INT=int 720; INT=int 1280 |
| 15 | preset = '1280x720 wide 16:9' | PASS | INT=int 1280; INT=int 720 |
| 16 | preset = '1080x1920 portrait 9:16' | PASS | INT=int 1080; INT=int 1920 |
| 17 | preset = '1920x1080 wide 16:9' | PASS | INT=int 1920; INT=int 1080 |
| 18 | preset = '1152x2048 portrait 9:16' | PASS | INT=int 1152; INT=int 2048 |
| 19 | preset = '2048x1152 wide 16:9' | PASS | INT=int 2048; INT=int 1152 |
| 20 | preset = '2048x2048 square' | PASS | INT=int 2048; INT=int 2048 |

## Verdict

All 20 cases behaved as expected (20 passed, 0 rejected with a clear message).
