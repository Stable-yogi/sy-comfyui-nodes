# MultiRefLabel SY (`SYMultiRefLabel`)

Source: `nodes/sy_multi_ref_label.py`

**What it does:** Labels your reference pictures as 'Image 1', 'Image 2' and so on, then adds the task. Use it when an edit model gets several pictures.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| task | STRING | yes | What the model should do, using the names Image 1, Image 2 and so on. | default '', multiline |
| ref_1 | STRING | no | Short description of the first picture. Leave empty if unused. | default '' |
| ref_2 | STRING | no | Short description of the second picture. Leave empty if unused. | default '' |
| ref_3 | STRING | no | Short description of the third picture. Leave empty if unused. | default '' |
| ref_4 | STRING | no | Short description of the fourth picture. Leave empty if unused. | default '' |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'Image 1: test Image 2: test Image 3: test Image 4: test test'; INT=int 4 |
| 2 | task = '' (empty) | REJECTED | ValueError: task is empty: say what the model should do with the pictures |
| 3 | ref_1 = '' (empty) | PASS | STRING=str 'Image 2: test Image 3: test Image 4: test test'; INT=int 3 |
| 4 | ref_2 = '' (empty) | PASS | STRING=str 'Image 1: test Image 3: test Image 4: test test'; INT=int 3 |
| 5 | ref_3 = '' (empty) | PASS | STRING=str 'Image 1: test Image 2: test Image 4: test test'; INT=int 3 |
| 6 | ref_4 = '' (empty) | PASS | STRING=str 'Image 1: test Image 2: test Image 3: test test'; INT=int 3 |

Note: Empty text boxes were filled with sample text in the starting inputs, because the node refuses empty text.


## Verdict

All 6 cases behaved as expected (5 passed, 1 rejected with a clear message).
