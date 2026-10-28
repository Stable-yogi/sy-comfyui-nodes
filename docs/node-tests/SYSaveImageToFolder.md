# Save Image To Folder SY (`SYSaveImageToFolder`)

Source: `nodes/sy_save_image_to_folder.py`

**What it does:** Saves pictures into a folder inside the ComfyUI output folder. The name can use {date} {time} {seed} {counter}.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to save. | picture batch [B,H,W,3] |
| subfolder | STRING | yes | Folder inside the output folder. It is created if missing. No .. or drive letters. | default 'SY' |
| filename_pattern | STRING | yes | File name without extension. Tokens: {date} {time} {seed} {counter}. | default 'image_{counter}' |
| format | COMBO | yes | File type to save. | one of: png, jpg, webp |
| quality | INT | yes | Quality for jpg and webp. Png ignores it. | 1 to 100, default 95 |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |
| embed_workflow | BOOLEAN | yes | Store the prompt and workflow inside png files so you can reload them. | default True |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '[removed]' |
| 2 | subfolder = '' (empty) | PASS | STRING=str '[removed]' |
| 3 | filename_pattern = '' (empty) | REJECTED | ValueError: file name pattern is empty: type a name such as image_{counter} |
| 4 | format = 'jpg' | PASS | STRING=str '[removed]' |
| 5 | format = 'webp' | PASS | STRING=str '[removed]' |
| 6 | quality = 1 (min) | PASS | STRING=str '[removed]' |
| 7 | quality = 100 (max) | PASS | STRING=str '[removed]' |
| 8 | quality = 50 (mid) | PASS | STRING=str '[removed]' |
| 9 | seed = 9007199254740992 (max) | PASS | STRING=str '[removed]' |
| 10 | seed = 4503599627370496 (mid) | PASS | STRING=str '[removed]' |
| 11 | embed_workflow = False | PASS | STRING=str '[removed]' |

## Verdict

All 11 cases behaved as expected (10 passed, 1 rejected with a clear message).
