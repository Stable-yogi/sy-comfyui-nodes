# MaskInvertThreshold SY (`SYMaskInvertThreshold`)

Source: `nodes/sy_mask_invert_threshold.py`

**What it does:** Flips a mask (white and black swap) and can first turn it into hard black and white at a cut-off value.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to change. | mask [B,H,W] |
| invert | BOOLEAN | yes | Swap white and black. | default True |
| use_threshold | BOOLEAN | yes | Turn soft grays into pure black or white first. | default False |
| threshold | FLOAT | yes | Values at or above this become white. Only used when use_threshold is on. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `MASK`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | MASK=tensor[1, 64, 96] |
| 2 | invert = False | PASS | MASK=tensor[1, 64, 96] |
| 3 | use_threshold = True | PASS | MASK=tensor[1, 64, 96] |
| 4 | threshold = 0.0 (min) | PASS | MASK=tensor[1, 64, 96] |
| 5 | threshold = 1.0 (max) | PASS | MASK=tensor[1, 64, 96] |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).
