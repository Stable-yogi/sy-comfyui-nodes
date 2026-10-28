# Aspect From Size SY (`SYAspectFromSize`)

Source: `nodes/sy_aspect_from_image.py`

**What it does:** Reads a width and height and gives the ratio as text, like 16:9, plus the ratio as a number. An odd ratio is matched to the nearest common one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Picture width in pixels. Used with height to find the shape, like 16:9. | 1 to 65536, default 1024 |
| height | INT | yes | Picture height in pixels. Used with width to find the shape, like 16:9. | 1 to 65536, default 1024 |

Outputs: `STRING`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '1:1'; FLOAT=float 1 |
| 2 | width = 1 (min) | PASS | STRING=str '9:21'; FLOAT=float 0.000976562 |
| 3 | width = 65536 (max) | PASS | STRING=str '21:9'; FLOAT=float 64 |
| 4 | width = 32768 (mid) | PASS | STRING=str '21:9'; FLOAT=float 32 |
| 5 | height = 1 (min) | PASS | STRING=str '21:9'; FLOAT=float 1024 |
| 6 | height = 65536 (max) | PASS | STRING=str '9:21'; FLOAT=float 0.015625 |
| 7 | height = 32768 (mid) | PASS | STRING=str '9:21'; FLOAT=float 0.03125 |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
