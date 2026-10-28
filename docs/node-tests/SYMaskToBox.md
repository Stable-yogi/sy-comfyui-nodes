# MaskToBox SY (`SYMaskToBox`)

Source: `nodes/sy_mask_to_box.py`

**What it does:** Finds the rectangle around the white part of a mask and returns x, y, width, height, with optional padding.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to measure. A batch gives one box around all of them. | mask [B,H,W] |
| padding | INT | yes | Extra pixels added around the box. The box stays inside the image. | 0 to 4096, step 1, default 0 |
| threshold | FLOAT | yes | Mask values at or above this count as white. | 0.01 to 1.0, step 0.01, default 0.5 |
| on_empty | COMBO | yes | When nothing is white: use the whole image, or stop with an error. | one of: whole_image, error |

Outputs: `INT`, `INT`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 24; INT=int 16; INT=int 48; INT=int 32 |
| 2 | padding = 4096 (max) | PASS | INT=int 0; INT=int 0; INT=int 96; INT=int 64 |
| 3 | padding = 2048 (mid) | PASS | INT=int 0; INT=int 0; INT=int 96; INT=int 64 |
| 4 | threshold = 0.01 (min) | PASS | INT=int 24; INT=int 16; INT=int 48; INT=int 32 |
| 5 | threshold = 1.0 (max) | PASS | INT=int 24; INT=int 16; INT=int 48; INT=int 32 |
| 6 | threshold = 0.505 (mid) | PASS | INT=int 24; INT=int 16; INT=int 48; INT=int 32 |
| 7 | on_empty = 'error' | PASS | INT=int 24; INT=int 16; INT=int 48; INT=int 32 |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
