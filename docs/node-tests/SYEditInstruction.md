# EditInstruction SY (`SYEditInstruction`)

Source: `nodes/sy_edit_instruction.py`

**What it does:** Writes one clear sentence for an image edit model, such as 'Replace the hat with a red cap.' It can add a line to keep the rest unchanged.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| action | COMBO | yes | What kind of change you want. | one of: replace, remove, add, recolour, restyle, change_background, fix_lighting |
| target | STRING | yes | The part of the picture to change, for example 'red hat'. | default '' |
| keep_rest | BOOLEAN | yes | Adds a line asking the model to leave everything else alone. | default True |
| to_value | STRING | no | What it should become. Needed for every action except remove and fix_lighting. | default '' |
| extra | STRING | no | Optional extra detail added after the main sentence. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 2 | action = 'remove' | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 3 | action = 'add' | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 4 | action = 'recolour' | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 5 | action = 'restyle' | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 6 | action = 'change_background' | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 7 | action = 'fix_lighting' | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 8 | target = '' (empty) | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 9 | keep_rest = False | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 10 | to_value = '' (empty) | REJECTED | ValueError: target is empty: say what part of the picture to change |
| 11 | extra = '' (empty) | REJECTED | ValueError: target is empty: say what part of the picture to change |

## Verdict

All 11 cases behaved as expected (0 passed, 11 rejected with a clear message).
