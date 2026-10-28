# Frame Interpolate Blend SY (`SYFrameInterpolateBlend`)

Source: `nodes/sy_frame_interpolate_blend.py`

**What it does:** Inserts cross-fade frames between neighbouring frames. This is a plain blend, not motion interpolation, so fast motion looks ghosted.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to add blend frames to. Needs at least 2. | picture batch [B,H,W,3] |
| between | INT | yes | How many blend frames to insert between each pair of frames. | 1 to 32, default 1 |
| loop | BOOLEAN | yes | Also blend from the last frame back to the first, for a looping clip. | default False |

Outputs: `IMAGE`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[5, 64, 96, 3]; INT=int 5 |
| 2 | between = 32 (max) | PASS | IMAGE=tensor[67, 64, 96, 3]; INT=int 67 |
| 3 | between = 16 (mid) | PASS | IMAGE=tensor[35, 64, 96, 3]; INT=int 35 |
| 4 | loop = True | PASS | IMAGE=tensor[6, 64, 96, 3]; INT=int 6 |

Note: The starting pictures hold 3 frames because the node needs at least 2.


## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
