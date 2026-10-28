# InpaintCrop SY (`SYInpaintCrop`)

Source: `nodes/sy_inpaint_crop_stitch.py`

**What it does:** Cuts a box around the painted part and scales it up, so the model draws a small hand or face at full size. Send 'stitch' to Inpaint Stitch to put the result back.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | Your whole picture. | picture batch [B,H,W,3] |
| mask | MASK | yes | The painted part (already grown and softened is best). | mask [B,H,W] |
| context | FLOAT | yes | Room around the painted part, as a factor of its size. More room matches the scene better. | 1.0 to 4.0, step 0.05, default 1.5 |
| size | INT | yes | Long side of the crop the model draws, in pixels. 1024 suits Krea 2. | 256 to 2048, step 16, default 1024 |
| min_box | INT | yes | Smallest crop box on the original picture, so a tiny mark still gets some scene around it. | 64 to 2048, step 16, default 256 |

Outputs: `SY_STITCH`, `IMAGE`, `MASK`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 688, 1024, 3]; MASK=tensor[1, 688, 1024] |
| 2 | context = 1.0 (min) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 688, 1024, 3]; MASK=tensor[1, 688, 1024] |
| 3 | context = 4.0 (max) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 688, 1024, 3]; MASK=tensor[1, 688, 1024] |
| 4 | context = 2.5 (mid) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 688, 1024, 3]; MASK=tensor[1, 688, 1024] |
| 5 | size = 256 (min) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 176, 256, 3]; MASK=tensor[1, 176, 256] |
| 6 | size = 2048 (max) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 1360, 2048, 3]; MASK=tensor[1, 1360, 2048] |
| 7 | size = 1152 (mid) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 768, 1152, 3]; MASK=tensor[1, 768, 1152] |
| 8 | min_box = 64 (min) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 912, 1024, 3]; MASK=tensor[1, 912, 1024] |
| 9 | min_box = 2048 (max) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 688, 1024, 3]; MASK=tensor[1, 688, 1024] |
| 10 | min_box = 1056 (mid) | PASS | SY_STITCH=dict(original, mask, box, crop_size); IMAGE=tensor[1, 688, 1024, 3]; MASK=tensor[1, 688, 1024] |

## Verdict

All 10 cases behaved as expected (10 passed, 0 rejected with a clear message).
