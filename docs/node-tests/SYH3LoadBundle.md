# H3LoadBundle SY (`SYH3LoadBundle`)

Source: `nodes/sy_h3_bundle.py`

**What it does:** Loads a bundle made by H3 Save Bundle: the latent, prompt, seed, folder path and the first reference picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| bundle | COMBO | yes | A saved bundle folder from output/sy_bundles. | one of: (none) |

Outputs: `LATENT`, `STRING`, `INT`, `STRING`, `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: no bundle chosen: save a bundle first, then pick it in the list |

Note: this node refuses on purpose here (refuses to run when no bundle has been saved yet, with a plain message (the save-then-load round trip is tested with real tensors in a throw-away folder)), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 1 cases behaved as expected (0 passed, 1 rejected with a clear message).
