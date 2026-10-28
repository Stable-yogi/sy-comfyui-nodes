# Bool Value SY (`SYBoolValue`)

Source: `nodes/sy_bool_value.py`

**What it does:** A yes/no switch. Set it once and plug it into as many nodes as you like. Also gives 1 for yes and 0 for no.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | BOOLEAN | yes | The yes/no value to send out. | default False |

Outputs: `BOOLEAN`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | BOOLEAN=bool False; INT=int 0 |
| 2 | value = True | PASS | BOOLEAN=bool True; INT=int 1 |

## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).
