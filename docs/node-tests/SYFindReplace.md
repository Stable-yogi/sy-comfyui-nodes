# Find Replace SY (`SYFindReplace`)

Source: `nodes/sy_find_replace.py`

**What it does:** Finds text and replaces it. Turn on use_regex for patterns. Also gives the number of replacements.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text you want to change. | default '', multiline |
| find | STRING | yes | The words to look for in the text. | default '' |
| replace | STRING | yes | What to put in place of every match. Empty removes the match. | default '' |
| use_regex | BOOLEAN | yes | On: Find is a pattern (regex) for advanced matching. Off: plain words. | default False |
| case_sensitive | BOOLEAN | yes | On: Cat and cat are different. Off: capital letters are ignored. | default True |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; INT=int 0 |
| 2 | text = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 3 | find = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 4 | replace = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 5 | use_regex = True | PASS | STRING=str ''; INT=int 0 |
| 6 | case_sensitive = False | PASS | STRING=str ''; INT=int 0 |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).
