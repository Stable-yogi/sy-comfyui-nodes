# Text Between SY (`SYTextBetween`)

Source: `nodes/sy_text_between.py`

**What it does:** Cuts out the text between a start marker and an end marker. Stops with a clear error if a marker is missing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to search in. | default '', multiline |
| start_marker | STRING | yes | The text just before the part you want. | default '' |
| end_marker | STRING | yes | The text just after the part you want. | default '' |
| which | COMBO | yes | If the pair appears many times: take the first one or the last one. | one of: first, last |
| include_markers | BOOLEAN | yes | On: keep the start and end markers in the result. | default False |
| case_sensitive | BOOLEAN | yes | On: capital letters must match. Off: they are ignored. | default True |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: start_marker is empty: type the text that comes before the part you want |
| 2 | text = '' (empty) | REJECTED | ValueError: start_marker is empty: type the text that comes before the part you want |
| 3 | start_marker = '' (empty) | REJECTED | ValueError: start_marker is empty: type the text that comes before the part you want |
| 4 | end_marker = '' (empty) | REJECTED | ValueError: start_marker is empty: type the text that comes before the part you want |
| 5 | which = 'last' | REJECTED | ValueError: start_marker is empty: type the text that comes before the part you want |
| 6 | include_markers = True | REJECTED | ValueError: start_marker is empty: type the text that comes before the part you want |
| 7 | case_sensitive = False | REJECTED | ValueError: start_marker is empty: type the text that comes before the part you want |

## Verdict

All 7 cases behaved as expected (0 passed, 7 rejected with a clear message).
