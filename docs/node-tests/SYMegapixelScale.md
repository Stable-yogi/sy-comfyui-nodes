# Megapixel Scale SY (`SYMegapixelScale`)

Source: `nodes/sy_megapixel_scale.py`

**What it does:** Works out a new width and height that add up to a target number of megapixels. The shape (aspect) stays the same. Both sides are rounded to a multiple.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Current width in pixels. Only its shape against the height matters. | 1 to 65536, default 1024 |
| height | INT | yes | Current height in pixels. | 1 to 65536, default 1024 |
| megapixels | FLOAT | yes | Target size in millions of pixels. 1.0 is about 1024 by 1024. | 0.01 to 4096.0, step 0.05, default 1.0 |
| multiple | INT | yes | Width and height are rounded to a multiple of this. 16 suits most models. | 1 to 256, default 16 |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 992; INT=int 992 |
| 2 | width = 1 (min) | PASS | INT=int 32; INT=int 32768 |
| 3 | width = 65536 (max) | PASS | INT=int 8000; INT=int 128 |
| 4 | width = 32768 (mid) | PASS | INT=int 5648; INT=int 176 |
| 5 | height = 1 (min) | PASS | INT=int 32000; INT=int 32 |
| 6 | height = 65536 (max) | PASS | INT=int 128; INT=int 8192 |
| 7 | height = 32768 (mid) | PASS | INT=int 176; INT=int 5632 |
| 8 | megapixels = 0.01 (min) | PASS | INT=int 96; INT=int 96 |
| 9 | megapixels = 4096.0 (max) | PASS | INT=int 64000; INT=int 64000 |
| 10 | megapixels = 2048.005 (mid) | PASS | INT=int 45248; INT=int 45248 |
| 11 | multiple = 1 (min) | PASS | INT=int 1000; INT=int 1000 |
| 12 | multiple = 256 (max) | PASS | INT=int 1024; INT=int 1024 |
| 13 | multiple = 128 (mid) | PASS | INT=int 1024; INT=int 1024 |

## Verdict

All 13 cases behaved as expected (13 passed, 0 rejected with a clear message).
