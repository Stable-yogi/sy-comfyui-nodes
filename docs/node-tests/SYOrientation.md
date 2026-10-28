# Orientation SY (`SYOrientation`)

Source: `nodes/sy_orientation.py`

**What it does:** Tells if an image is landscape, portrait or square, and gives its width and height.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to measure. For a batch the first size is used. | picture batch [B,H,W,3] |
| tolerance_percent | FLOAT | yes | Sides this close (in percent of the longer side) count as square. | 0.0 to 100.0, step 0.5, default 0.0 |

Outputs: `STRING`, `BOOLEAN`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'landscape'; BOOLEAN=bool True; INT=int 96; INT=int 64 |
| 2 | tolerance_percent = 100.0 (max) | PASS | STRING=str 'square'; BOOLEAN=bool False; INT=int 96; INT=int 64 |
| 3 | tolerance_percent = 50.0 (mid) | PASS | STRING=str 'square'; BOOLEAN=bool False; INT=int 96; INT=int 64 |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
