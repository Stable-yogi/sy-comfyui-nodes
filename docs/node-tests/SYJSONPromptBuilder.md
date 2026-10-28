# JSON Prompt Builder SY (`SYJSONPromptBuilder`)

Source: `nodes/sy_json_prompt_builder.py`

**What it does:** Turns lines like 'subject: a fox' into a valid JSON text. Quotes and special characters are escaped for you.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lines | STRING | yes | One key: value per line. Lines starting with # are skipped. | default 'subject: a fox\nmood: calm', multiline |
| auto_types | BOOLEAN | yes | On: true, false, null and numbers become real JSON values. Off: all text. | default True |
| indent | INT | yes | Spaces per level. 0 gives one compact line. | 0 to 8, default 2 |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '{ "subject": "a fox", "mood": "calm" }' |
| 2 | lines = '' (empty) | REJECTED | ValueError: no key: value lines found: write at least one line |
| 3 | auto_types = False | PASS | STRING=str '{ "subject": "a fox", "mood": "calm" }' |
| 4 | indent = 0 (min) | PASS | STRING=str '{"subject": "a fox", "mood": "calm"}' |
| 5 | indent = 8 (max) | PASS | STRING=str '{ "subject": "a fox", "mood": "calm" }' |
| 6 | indent = 4 (mid) | PASS | STRING=str '{ "subject": "a fox", "mood": "calm" }' |

## Verdict

All 6 cases behaved as expected (5 passed, 1 rejected with a clear message).
