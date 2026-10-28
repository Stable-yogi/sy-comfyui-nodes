# Few Shot Block SY (`SYFewShotBlock`)

Source: `nodes/sy_few_shot_block.py`

**What it does:** Builds a few-shot text: your task, up to 4 worked examples, then the new input with an empty output line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| task | STRING | yes | What the examples teach, in plain words. | default '', multiline |
| new_input | STRING | yes | The new text that should be answered like the examples. | default '', multiline |
| input_label | STRING | yes | The word printed before each example input. | default 'Input' |
| output_label | STRING | yes | The word printed before each example output. | default 'Output' |
| example_in_1 | STRING | no | Example 1: the input. Empty skips the pair. | default '', multiline |
| example_out_1 | STRING | no | Example 1: the answer you want. Empty skips the pair. | default '', multiline |
| example_in_2 | STRING | no | Example 2: the input. Empty skips the pair. | default '', multiline |
| example_out_2 | STRING | no | Example 2: the answer you want. Empty skips the pair. | default '', multiline |
| example_in_3 | STRING | no | Example 3: the input. Empty skips the pair. | default '', multiline |
| example_out_3 | STRING | no | Example 3: the answer you want. Empty skips the pair. | default '', multiline |
| example_in_4 | STRING | no | Example 4: the input. Empty skips the pair. | default '', multiline |
| example_out_4 | STRING | no | Example 4: the answer you want. Empty skips the pair. | default '', multiline |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 2 | task = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 3 | new_input = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 4 | input_label = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 5 | output_label = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 6 | example_in_1 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 7 | example_out_1 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 8 | example_in_2 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 9 | example_out_2 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 10 | example_in_3 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 11 | example_out_3 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 12 | example_in_4 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |
| 13 | example_out_4 = '' (empty) | REJECTED | ValueError: new_input is empty: type the text the examples should be applied to |

## Verdict

All 13 cases behaved as expected (0 passed, 13 rejected with a clear message).
