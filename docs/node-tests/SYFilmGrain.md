# Film Grain SY (`SYFilmGrain`)

Source: `nodes/sy_film_grain.py`

**What it does:** Adds film grain. The same seed always gives the same grain. Choose grey or colour grain and how coarse it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to add grain to. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How visible the grain is. 0 changes nothing. | 0.0 to 1.0, step 0.01, default 0.1 |
| size | INT | yes | Grain size in pixels. 1 is fine grain, bigger is coarse. | 1 to 32, default 1 |
| seed | INT | yes | Number that fixes the grain pattern. Change it for a new pattern. | 0 to 4294967295, default 0 |
| color_grain | BOOLEAN | yes | On gives coloured grain, off gives grey grain. | default False |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | strength = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | strength = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | strength = 0.5 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | size = 32 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | size = 16 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 7 | seed = 4294967295 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 8 | seed = 2147483647 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 9 | color_grain = True | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
