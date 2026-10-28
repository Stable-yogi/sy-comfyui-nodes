# Counter SY (`SYCounter`)

Source: `nodes/sy_counter.py`

**What it does:** Counts up by a step on each run. You feed it the run number, so the same number always gives the same answer.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| run_index | INT | yes | Which run this is, from 0. Connect a batch index or a run counter. | 0 to 9007199254740991, default 0 |
| start | INT | yes | The value on run 0. | -9007199254740991 to 9007199254740991, default 0 |
| step | INT | yes | How much the value changes on each run. Can be negative. | -9007199254740991 to 9007199254740991, default 1 |
| max_value | INT | yes | Highest value before it starts over at start. Used only when wrap is on. | -9007199254740991 to 9007199254740991, default 9 |
| wrap | BOOLEAN | yes | On starts over at start after max_value. Off keeps counting. | default True |

Outputs: `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 0 |
| 2 | run_index = 9007199254740991 (max) | PASS | INT=int 1 |
| 3 | run_index = 4503599627370495 (mid) | PASS | INT=int 5 |
| 4 | start = -9007199254740991 (min) | PASS | INT=int -9007199254740991 |
| 5 | start = 9007199254740991 (max) | REJECTED | ValueError: max_value (9) is below start (9007199254740991). Raise max_value or turn wrap... |
| 6 | step = -9007199254740991 (min) | PASS | INT=int 0 |
| 7 | step = 9007199254740991 (max) | PASS | INT=int 0 |
| 8 | step = 0 (mid) | PASS | INT=int 0 |
| 9 | max_value = -9007199254740991 (min) | REJECTED | ValueError: max_value (-9007199254740991) is below start (0). Raise max_value or turn wra... |
| 10 | max_value = 9007199254740991 (max) | PASS | INT=int 0 |
| 11 | max_value = 0 (mid) | PASS | INT=int 0 |
| 12 | wrap = False | PASS | INT=int 0 |

## Verdict

All 12 cases behaved as expected (10 passed, 2 rejected with a clear message).
