# Assert SY (`SYAssert`)

Source: `nodes/sy_assert.py`

**What it does:** Stops the whole run with your message when the value is no. Use it to catch a wrong setting before the slow part starts.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| condition | BOOLEAN | yes | Must be yes for the run to go on. No stops the run. | default True |
| message | STRING | yes | The text shown when the run stops. | default 'Assert failed: the value was no.' |

Outputs: `BOOLEAN`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | BOOLEAN=bool True |
| 2 | condition = False | REJECTED | ValueError: Assert failed: the value was no. |
| 3 | message = '' (empty) | PASS | BOOLEAN=bool True |

Note: this node refuses on purpose here (stops on purpose when the checked value is false), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 3 cases behaved as expected (2 passed, 1 rejected with a clear message).
