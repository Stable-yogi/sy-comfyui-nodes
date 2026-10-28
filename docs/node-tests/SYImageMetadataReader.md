# Image Metadata Reader SY (`SYImageMetadataReader`)

Source: `nodes/sy_image_metadata_reader.py`

**What it does:** Reads the prompt and workflow text saved inside a png file from the input folder. It never changes the file.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file | STRING | yes | A .png file inside the input folder, like image.png or a/b.png. | default '' |

Outputs: `STRING`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: only .png files carry this metadata, got '' |
| 2 | file = '' (empty) | REJECTED | ValueError: only .png files carry this metadata, got '' |

Note: this node refuses on purpose here (refuses an empty or non-png file name with a clear message), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 2 cases behaved as expected (0 passed, 2 rejected with a clear message).
