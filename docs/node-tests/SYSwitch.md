# Switch SY (`SYSwitch`)

Source: `nodes/sy_switch.py`

**What it does:** One switch, two inputs. On sends input A. Off sends input B. The branch you do not pick is not run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| use_a | BOOLEAN | yes | On sends input A. Off sends input B. | default True |
| a | * | no | Sent when the switch is on. |  |
| b | * | no | Sent when the switch is off. |  |

Outputs: `*`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | *=str 'test' |
| 2 | use_a = False | PASS | *=str 'test' |

## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).
