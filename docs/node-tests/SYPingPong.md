# Ping Pong SY (`SYPingPong`)

Source: `nodes/sy_ping_pong.py`

**What it does:** Adds the frames played backwards after the forward ones, so a clip goes there and back and loops smoothly.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to play forward and then backward. | picture batch [B,H,W,3] |
| repeat_ends | BOOLEAN | yes | On: show the first and last frame twice. Off: no doubled frames, best for loops. | default False |

Outputs: `IMAGE`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3]; INT=int 1 |
| 2 | repeat_ends = True | PASS | IMAGE=tensor[2, 64, 96, 3]; INT=int 2 |

## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).
