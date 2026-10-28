# Free VRAM SY (`SYFreeVRAM`)

Source: `nodes/sy_free_vram.py`

**What it does:** Passes any value through. When enabled, unloads models and clears the GPU memory cache so the next step has more room.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | * | yes | Anything you pass through. It comes out unchanged, after memory is freed. |  |
| enabled | BOOLEAN | yes | On: free graphics card memory when this runs. Off: do nothing. | default True |

Outputs: `*`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | *=str 'test'; STRING=str 'comfy not available' |
| 2 | enabled = False | PASS | *=str 'test'; STRING=str 'disabled' |

## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).
