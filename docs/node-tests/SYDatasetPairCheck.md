# Dataset Pair Check SY (`SYDatasetPairCheck`)

Source: `nodes/sy_dataset_pair_check.py`

**What it does:** Checks that the number of pictures equals the number of caption lines, and lists empty caption lines.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| captions | STRING | yes | All captions, one caption per line. | default '', multiline |
| image_count | INT | yes | Number of pictures. Ignored when a picture batch is connected. | 0 to 10000000, default 0 |
| skip_blank_lines | BOOLEAN | yes | On: empty caption lines are not counted. Off: each one counts as a caption. | default False |
| images | IMAGE | no | Optional picture batch. When connected, its size is used as the picture count. | picture batch [B,H,W,3] |

Outputs: `BOOLEAN`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | BOOLEAN=bool False; STRING=str 'MISMATCH: 1 pictures but 0 captions. 1 caption missing; write them or remove ...' |
| 2 | captions = '' (empty) | PASS | BOOLEAN=bool False; STRING=str 'MISMATCH: 1 pictures but 0 captions. 1 caption missing; write them or remove ...' |
| 3 | image_count = 10000000 (max) | PASS | BOOLEAN=bool False; STRING=str 'MISMATCH: 1 pictures but 0 captions. 1 caption missing; write them or remove ...' |
| 4 | image_count = 5000000 (mid) | PASS | BOOLEAN=bool False; STRING=str 'MISMATCH: 1 pictures but 0 captions. 1 caption missing; write them or remove ...' |
| 5 | skip_blank_lines = True | PASS | BOOLEAN=bool False; STRING=str 'MISMATCH: 1 pictures but 0 captions. 1 caption missing; write them or remove ...' |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).
