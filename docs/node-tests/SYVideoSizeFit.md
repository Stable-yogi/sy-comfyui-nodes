# Video Size Fit SY (`SYVideoSizeFit`)

Source: `nodes/sy_video_size_fit.py`

**What it does:** Gives a new width and height with the same shape that stays inside a pixel budget and is a multiple of a number.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Current width in pixels. | 1 to 16384, default 1280 |
| height | INT | yes | Current height in pixels. | 1 to 16384, default 720 |
| max_pixels | FLOAT | yes | Pixel budget in megapixels. The result never goes above it. | 0.001 to 1000.0, step 0.01, default 0.9 |
| multiple_of | INT | yes | Width and height are rounded to a multiple of this number. | 1 to 256, default 32 |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 1248; INT=int 704 |
| 2 | width = 1 (min) | PASS | INT=int 32; INT=int 704 |
| 3 | width = 16384 (max) | PASS | INT=int 4512; INT=int 192 |
| 4 | width = 8192 (mid) | PASS | INT=int 3200; INT=int 256 |
| 5 | height = 1 (min) | PASS | INT=int 1280; INT=int 32 |
| 6 | height = 16384 (max) | PASS | INT=int 256; INT=int 3392 |
| 7 | height = 8192 (mid) | PASS | INT=int 352; INT=int 2400 |
| 8 | max_pixels = 0.001 (min) | REJECTED | ValueError: max_pixels is too small: even 32x32 is over the budget |
| 9 | max_pixels = 1000.0 (max) | PASS | INT=int 1280; INT=int 704 |
| 10 | max_pixels = 500.0005 (mid) | PASS | INT=int 1280; INT=int 704 |
| 11 | multiple_of = 1 (min) | PASS | INT=int 1265; INT=int 711 |
| 12 | multiple_of = 256 (max) | PASS | INT=int 1280; INT=int 512 |
| 13 | multiple_of = 128 (mid) | PASS | INT=int 1280; INT=int 640 |

## Verdict

All 13 cases behaved as expected (12 passed, 1 rejected with a clear message).
