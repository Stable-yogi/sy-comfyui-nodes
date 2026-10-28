# Resolution SY (`SYResolution`)

Source: `nodes/sy_resolution.py`

**What it does:** Picks a width and height for a model. Choose a model preset and an aspect ratio. Custom uses the megapixels and multiple you set.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model_preset | COMBO | yes | Picks the size the chosen model works best at. | one of: Krea 2 (1 MP), Qwen Image 2.1 (1.5 MP), MOSS-Image (multiple of 32), Flux (1 MP), Custom |
| aspect | COMBO | yes | The shape of the picture. 1:1 is square, 16:9 is wide screen. | one of: 1:1, 4:3, 3:2, 16:9, 21:9, 3:4, 2:3, 9:16 |
| orientation | COMBO | yes | Landscape is wider than tall. Portrait is taller than wide. | one of: landscape, portrait |
| megapixels | FLOAT | yes | Picture size in millions of pixels. 1.0 is about 1024 by 1024. | 0.1 to 16.0, step 0.05, default 1.0 |
| multiple | INT | yes | Width and height are rounded to a multiple of this. 16 suits most models. | 8 to 64, step 8, default 16 |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 992; INT=int 1008 |
| 2 | model_preset = 'Qwen Image 2.1 (1.5 MP)' | PASS | INT=int 1232; INT=int 1232 |
| 3 | model_preset = 'MOSS-Image (multiple of 32)' | PASS | INT=int 992; INT=int 992 |
| 4 | model_preset = 'Flux (1 MP)' | PASS | INT=int 992; INT=int 1008 |
| 5 | model_preset = 'Custom' | PASS | INT=int 992; INT=int 1008 |
| 6 | aspect = '4:3' | PASS | INT=int 1152; INT=int 864 |
| 7 | aspect = '3:2' | PASS | INT=int 1232; INT=int 816 |
| 8 | aspect = '16:9' | PASS | INT=int 1328; INT=int 752 |
| 9 | aspect = '21:9' | PASS | INT=int 1520; INT=int 656 |
| 10 | aspect = '3:4' | PASS | INT=int 1152; INT=int 864 |
| 11 | aspect = '2:3' | PASS | INT=int 1232; INT=int 816 |
| 12 | aspect = '9:16' | PASS | INT=int 1328; INT=int 752 |
| 13 | orientation = 'portrait' | PASS | INT=int 1008; INT=int 992 |
| 14 | megapixels = 0.1 (min) | PASS | INT=int 992; INT=int 1008 |
| 15 | megapixels = 16.0 (max) | PASS | INT=int 992; INT=int 1008 |
| 16 | megapixels = 8.05 (mid) | PASS | INT=int 992; INT=int 1008 |
| 17 | multiple = 8 (min) | PASS | INT=int 992; INT=int 1008 |
| 18 | multiple = 64 (max) | PASS | INT=int 992; INT=int 1008 |
| 19 | multiple = 32 (mid) | PASS | INT=int 992; INT=int 1008 |

## Verdict

All 19 cases behaved as expected (19 passed, 0 rejected with a clear message).
