# Text Contains SY (`SYTextContains`)

Source: `nodes/sy_text_contains.py`

**What it does:** Checks if a text contains a word or phrase. Gives true or false, and passes the text through.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to look in. It also comes out unchanged. | default '', multiline |
| needle | STRING | yes | The word or phrase to look for. | default '' |
| case_sensitive | BOOLEAN | yes | On: upper and lower case must match exactly. | default False |

Outputs: `BOOLEAN`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: needle is empty: type the word or phrase to look for |
| 2 | text = '' (empty) | REJECTED | ValueError: needle is empty: type the word or phrase to look for |
| 3 | needle = '' (empty) | REJECTED | ValueError: needle is empty: type the word or phrase to look for |
| 4 | case_sensitive = True | REJECTED | ValueError: needle is empty: type the word or phrase to look for |

## Verdict

All 4 cases behaved as expected (0 passed, 4 rejected with a clear message).
