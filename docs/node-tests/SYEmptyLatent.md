# Empty Latent SY (`SYEmptyLatent`)

Source: `nodes/sy_empty_latent.py`

**What it does:** Makes a blank latent to start a render from. 'standard 4ch /8' has 4 channels (SD 1.5, SDXL). 'flux 16ch /8' has 16 channels (Flux, SD3 style). Both are 8 times smaller than the picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Picture width in pixels. | 8 to 16384, step 8, default 1024 |
| height | INT | yes | Picture height in pixels. | 8 to 16384, step 8, default 1024 |
| batch | INT | yes | How many blank latents to make at once. | 1 to 4096, default 1 |
| latent_type | COMBO | yes | 4 channels for SD 1.5 and SDXL. 16 channels for Flux style models. | one of: standard 4ch /8, flux 16ch /8 |

Outputs: `LATENT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | LATENT=dict(samples) |
| 2 | width = 8 (min) | PASS | LATENT=dict(samples) |
| 3 | width = 16384 (max) | PASS | LATENT=dict(samples) |
| 4 | width = 8192 (mid) | PASS | LATENT=dict(samples) |
| 5 | height = 8 (min) | PASS | LATENT=dict(samples) |
| 6 | height = 16384 (max) | PASS | LATENT=dict(samples) |
| 7 | height = 8192 (mid) | PASS | LATENT=dict(samples) |
| 8 | batch = 4096 (max) | PASS | LATENT=dict(samples) |
| 9 | batch = 2048 (mid) | PASS | LATENT=dict(samples) |
| 10 | latent_type = 'flux 16ch /8' | PASS | LATENT=dict(samples) |

## Verdict

All 10 cases behaved as expected (10 passed, 0 rejected with a clear message).
