# Pixel Count Info SY (`SYPixelCountInfo`)

Source: `nodes/sy_pixel_count_info.py`

**What it does:** Shows how big a picture size is: megapixels, total pixels and shape. Also gives a text line you can show or save.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width in pixels. | 0 to 1000000, default 1024 |
| height | INT | yes | Height in pixels. | 0 to 1000000, default 1024 |

Outputs: `FLOAT`, `INT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 1.04858; INT=int 1048576; STRING=str '1024x1024, 1048576 pixels, 1.049 megapixels, aspect 1:1 (1.000), square' |
| 2 | width = 0 (min) | PASS | FLOAT=float 0; INT=int 0; STRING=str '0x1024, 0 pixels, 0.000 megapixels, aspect no shape (a side is 0), empty' |
| 3 | width = 1000000 (max) | PASS | FLOAT=float 1024; INT=int 1024000000; STRING=str '1000000x1024, 1024000000 pixels, 1024.000 megapixels, aspect 15625:16 (976.56...' |
| 4 | width = 500000 (mid) | PASS | FLOAT=float 512; INT=int 512000000; STRING=str '500000x1024, 512000000 pixels, 512.000 megapixels, aspect 15625:32 (488.281),...' |
| 5 | height = 0 (min) | PASS | FLOAT=float 0; INT=int 0; STRING=str '1024x0, 0 pixels, 0.000 megapixels, aspect no shape (a side is 0), empty' |
| 6 | height = 1000000 (max) | PASS | FLOAT=float 1024; INT=int 1024000000; STRING=str '1024x1000000, 1024000000 pixels, 1024.000 megapixels, aspect 16:15625 (0.001)...' |
| 7 | height = 500000 (mid) | PASS | FLOAT=float 512; INT=int 512000000; STRING=str '1024x500000, 512000000 pixels, 512.000 megapixels, aspect 32:15625 (0.002), p...' |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
