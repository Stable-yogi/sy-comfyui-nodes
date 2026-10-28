# Save With Caption SY (`SYSaveWithCaption`)

Source: `nodes/sy_save_with_caption.py`

**What it does:** Saves each picture plus a text file with the same name holding the caption. Good for making training datasets.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to save. | picture batch [B,H,W,3] |
| caption | STRING | yes | Text written to the .txt file next to each picture. | default '', multiline |
| subfolder | STRING | yes | Folder inside the output folder. It is created if missing. | default 'SY/dataset' |
| filename_pattern | STRING | yes | File name without extension. Tokens: {date} {time} {seed} {counter}. | default 'img_{counter}' |
| format | COMBO | yes | Picture file type. | one of: png, jpg, webp |
| quality | INT | yes | Quality for jpg and webp. Png ignores it. | 1 to 100, default 95 |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: the caption is empty: type the caption text |
| 2 | caption = '' (empty) | REJECTED | ValueError: the caption is empty: type the caption text |
| 3 | subfolder = '' (empty) | REJECTED | ValueError: the caption is empty: type the caption text |
| 4 | filename_pattern = '' (empty) | REJECTED | ValueError: the caption is empty: type the caption text |
| 5 | format = 'jpg' | REJECTED | ValueError: the caption is empty: type the caption text |
| 6 | format = 'webp' | REJECTED | ValueError: the caption is empty: type the caption text |
| 7 | quality = 1 (min) | REJECTED | ValueError: the caption is empty: type the caption text |
| 8 | quality = 100 (max) | REJECTED | ValueError: the caption is empty: type the caption text |
| 9 | quality = 50 (mid) | REJECTED | ValueError: the caption is empty: type the caption text |
| 10 | seed = 9007199254740992 (max) | REJECTED | ValueError: the caption is empty: type the caption text |
| 11 | seed = 4503599627370496 (mid) | REJECTED | ValueError: the caption is empty: type the caption text |

## Verdict

All 11 cases behaved as expected (0 passed, 11 rejected with a clear message).
