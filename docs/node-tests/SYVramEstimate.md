# VRAM Estimate SY (`SYVramEstimate`)

Source: `nodes/sy_vram_estimate.py`

**What it does:** Rough estimate of the VRAM a model needs: file size times an overhead factor. Only a guide, not a measurement.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file_size_gb | FLOAT | yes | Size of the model file in gigabytes. | 0.01 to 1000.0, step 0.1, default 6.0 |
| overhead_factor | FLOAT | yes | Extra room for work memory. 1.2 to 1.5 is common. | 1.0 to 5.0, step 0.05, default 1.3 |

Outputs: `STRING`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'Estimate: about 7.8 GB of VRAM (6.0 GB file x 1.30 overhead). This is only a ...'; FLOAT=float 7.8 |
| 2 | file_size_gb = 0.01 (min) | PASS | STRING=str 'Estimate: about 0.0 GB of VRAM (0.0 GB file x 1.30 overhead). This is only a ...'; FLOAT=float 0.013 |
| 3 | file_size_gb = 1000.0 (max) | PASS | STRING=str 'Estimate: about 1300.0 GB of VRAM (1000.0 GB file x 1.30 overhead). This is o...'; FLOAT=float 1300 |
| 4 | file_size_gb = 500.005 (mid) | PASS | STRING=str 'Estimate: about 650.0 GB of VRAM (500.0 GB file x 1.30 overhead). This is onl...'; FLOAT=float 650.006 |
| 5 | overhead_factor = 1.0 (min) | PASS | STRING=str 'Estimate: about 6.0 GB of VRAM (6.0 GB file x 1.00 overhead). This is only a ...'; FLOAT=float 6 |
| 6 | overhead_factor = 5.0 (max) | PASS | STRING=str 'Estimate: about 30.0 GB of VRAM (6.0 GB file x 5.00 overhead). This is only a...'; FLOAT=float 30 |
| 7 | overhead_factor = 3.0 (mid) | PASS | STRING=str 'Estimate: about 18.0 GB of VRAM (6.0 GB file x 3.00 overhead). This is only a...'; FLOAT=float 18 |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
