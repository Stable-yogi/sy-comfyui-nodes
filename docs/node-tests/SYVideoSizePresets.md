# Video Size Presets SY (`SYVideoSizePresets`)

Source: `nodes/sy_video_size_presets.py`

**What it does:** Video sizes for models like Wan and LTX. Pick 480p, 720p or 1080p and a shape: wide 16:9, tall 9:16 or square 1:1. Both sides are rounded to 16 or 32.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| resolution | COMBO | yes | Length of the short side. 720p is 720 pixels. | one of: 480p, 720p, 1080p |
| aspect | COMBO | yes | 16:9 is wide, 9:16 is tall like a phone, 1:1 is square. | one of: 16:9, 9:16, 1:1 |
| multiple | COMBO | yes | Round both sides to this multiple. LTX style models like 32. | one of: 16, 32 |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 848; INT=int 480 |
| 2 | resolution = '720p' | PASS | INT=int 1280; INT=int 720 |
| 3 | resolution = '1080p' | PASS | INT=int 1920; INT=int 1088 |
| 4 | aspect = '9:16' | PASS | INT=int 480; INT=int 848 |
| 5 | aspect = '1:1' | PASS | INT=int 480; INT=int 480 |
| 6 | multiple = '32' | PASS | INT=int 864; INT=int 480 |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).
