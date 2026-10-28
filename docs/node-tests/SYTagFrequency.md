# Tag Frequency SY (`SYTagFrequency`)

Source: `nodes/sy_tag_frequency.py`

**What it does:** Counts how many captions use each tag and lists them from the most common to the rarest.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| captions | STRING | yes | All captions, one caption per line. | default '', multiline |
| separator | STRING | yes | The character that splits one tag from the next. Usually a comma. | default ',' |
| lowercase | BOOLEAN | yes | On: Dog and dog count as the same tag. | default True |
| min_count | INT | yes | Hide tags that appear in fewer captions than this. | 1 to 1000000, default 1 |
| top_n | INT | yes | Show only the most common tags. 0 shows all of them. | 0 to 100000, default 0 |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'captions: 1 different tags: 1 1 test'; INT=int 1 |
| 2 | captions = '' (empty) | REJECTED | ValueError: no captions found; put one caption on each line |
| 3 | separator = '' (empty) | REJECTED | ValueError: separator must not be empty; use a comma for normal tag captions |
| 4 | lowercase = False | PASS | STRING=str 'captions: 1 different tags: 1 1 test'; INT=int 1 |
| 5 | min_count = 1000000 (max) | PASS | STRING=str 'captions: 1 different tags: 1 showing: 0'; INT=int 1 |
| 6 | min_count = 500000 (mid) | PASS | STRING=str 'captions: 1 different tags: 1 showing: 0'; INT=int 1 |
| 7 | top_n = 100000 (max) | PASS | STRING=str 'captions: 1 different tags: 1 1 test'; INT=int 1 |
| 8 | top_n = 50000 (mid) | PASS | STRING=str 'captions: 1 different tags: 1 1 test'; INT=int 1 |

Note: Empty text boxes were filled with sample text in the starting inputs, because the node refuses empty text.


## Verdict

All 8 cases behaved as expected (6 passed, 2 rejected with a clear message).
