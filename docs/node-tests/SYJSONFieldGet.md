# JSON Field Get SY (`SYJSONFieldGet`)

Source: `nodes/sy_json_field_get.py`

**What it does:** Reads one value from a JSON text. The path is dots between keys, and numbers pick list items, like a.b.0.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| json_text | STRING | yes | The JSON text to read from. | default '', multiline |
| path | STRING | yes | Keys joined by dots, numbers for list items, like a.b.0. Empty gives it all. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '{"a": 1}' |
| 2 | json_text = '' (empty) | REJECTED | ValueError: json_text is not valid JSON (Expecting value: line 1 column 1 (char 0)): fix ... |
| 3 | path = '' (empty) | PASS | STRING=str '{"a": 1}' |

Note: Empty text boxes were filled with sample text in the starting inputs, because the node refuses empty text.


## Verdict

All 3 cases behaved as expected (2 passed, 1 rejected with a clear message).
