# Text Template SY (`SYTextTemplate`)

Source: `nodes/sy_text_template.py`

**What it does:** Fills {name} placeholders in a text with up to four named values. A name with no matching input gives an error.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| template | STRING | yes | Text with {name} placeholders to fill in. | default 'a photo of {name}, {style}', multiline |
| name_1 | STRING | no | Placeholder name for value 1, used as {name} in the template. | default 'name' |
| value_1 | STRING | no | Text that replaces the placeholder named in name_1. | default '' |
| name_2 | STRING | no | Placeholder name for value 2, used as {name} in the template. | default 'style' |
| value_2 | STRING | no | Text that replaces the placeholder named in name_2. | default '' |
| name_3 | STRING | no | Placeholder name for value 3, used as {name} in the template. | default '' |
| value_3 | STRING | no | Text that replaces the placeholder named in name_3. | default '' |
| name_4 | STRING | no | Placeholder name for value 4, used as {name} in the template. | default '' |
| value_4 | STRING | no | Text that replaces the placeholder named in name_4. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'a photo of ,' |
| 2 | template = '' (empty) | PASS | STRING=str '' |
| 3 | name_1 = '' (empty) | REJECTED | ValueError: the template uses {name} but no input has that name: set a name_N field to it |
| 4 | value_1 = '' (empty) | PASS | STRING=str 'a photo of ,' |
| 5 | name_2 = '' (empty) | REJECTED | ValueError: the template uses {style} but no input has that name: set a name_N field to it |
| 6 | value_2 = '' (empty) | PASS | STRING=str 'a photo of ,' |
| 7 | name_3 = '' (empty) | PASS | STRING=str 'a photo of ,' |
| 8 | value_3 = '' (empty) | PASS | STRING=str 'a photo of ,' |
| 9 | name_4 = '' (empty) | PASS | STRING=str 'a photo of ,' |
| 10 | value_4 = '' (empty) | PASS | STRING=str 'a photo of ,' |

## Verdict

All 10 cases behaved as expected (8 passed, 2 rejected with a clear message).
