# Load Image Mini SY (`SYLoadImageMini`)

Source: `nodes/sy_load_image_mini.py`

**What it does:** Loads one picture from the ComfyUI input folder. Gives the image, its mask and its size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | COMBO | yes | The picture file in the ComfyUI input folder. | one of: example.png |

Outputs: `IMAGE`, `MASK`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 48, 64, 3]; MASK=tensor[1, 48, 64]; INT=int 64; INT=int 48 |

## Verdict

All 1 cases behaved as expected (1 passed, 0 rejected with a clear message).
