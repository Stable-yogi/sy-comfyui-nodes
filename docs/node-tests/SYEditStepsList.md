# EditStepsList SY (`SYEditStepsList`)

Source: `nodes/sy_edit_steps_list.py`

**What it does:** Joins up to five edit steps into one list for an image edit model. Empty steps are skipped and the order is kept.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| style | COMBO | yes | How to write the list: numbers, bullets, or First, Then, Finally. | one of: numbered, bullets, then_words |
| step_1 | STRING | no | Edit step number 1. Leave empty to skip it. | default '' |
| step_2 | STRING | no | Edit step number 2. Leave empty to skip it. | default '' |
| step_3 | STRING | no | Edit step number 3. Leave empty to skip it. | default '' |
| step_4 | STRING | no | Edit step number 4. Leave empty to skip it. | default '' |
| step_5 | STRING | no | Edit step number 5. Leave empty to skip it. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '1. test 2. test 3. test 4. test 5. test' |
| 2 | style = 'bullets' | PASS | STRING=str '- test - test - test - test - test' |
| 3 | style = 'then_words' | PASS | STRING=str 'First, test. Then, test. Then, test. Then, test. Finally, test.' |
| 4 | step_1 = '' (empty) | PASS | STRING=str '1. test 2. test 3. test 4. test' |
| 5 | step_2 = '' (empty) | PASS | STRING=str '1. test 2. test 3. test 4. test' |
| 6 | step_3 = '' (empty) | PASS | STRING=str '1. test 2. test 3. test 4. test' |
| 7 | step_4 = '' (empty) | PASS | STRING=str '1. test 2. test 3. test 4. test' |
| 8 | step_5 = '' (empty) | PASS | STRING=str '1. test 2. test 3. test 4. test' |

Note: Empty text boxes were filled with sample text in the starting inputs, because the node refuses empty text.


## Verdict

All 8 cases behaved as expected (8 passed, 0 rejected with a clear message).
