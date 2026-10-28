# Tag Sort SY (`SYTagSort`)

Source: `nodes/sy_tag_sort.py`

**What it does:** Splits a prompt into tags, then sorts them (A to Z, by length, or a repeatable shuffle) and removes repeats.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt whose tags you want to sort. | default '', multiline |
| separator | STRING | yes | The character that splits one tag from the next. | default ',' |
| order | COMBO | yes | keep = same order. Others sort A to Z, by length, or shuffle the same way every time. | one of: keep, alphabetical, shortest_first, longest_first, shuffle_seeded |
| seed | INT | yes | Number for the shuffle. The same number gives the same order. | 0 to 9223372036854775807, default 0 |
| dedupe | BOOLEAN | yes | On: remove tags that appear twice (capital letters are ignored). | default True |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | separator = '' (empty) | REJECTED | ValueError: separator is empty: type the character that splits the tags, for example a comma |
| 4 | order = 'alphabetical' | PASS | STRING=str '' |
| 5 | order = 'shortest_first' | PASS | STRING=str '' |
| 6 | order = 'longest_first' | PASS | STRING=str '' |
| 7 | order = 'shuffle_seeded' | PASS | STRING=str '' |
| 8 | seed = 9223372036854775807 (max) | PASS | STRING=str '' |
| 9 | seed = 4611686018427387903 (mid) | PASS | STRING=str '' |
| 10 | dedupe = False | PASS | STRING=str '' |

## Verdict

All 10 cases behaved as expected (9 passed, 1 rejected with a clear message).
