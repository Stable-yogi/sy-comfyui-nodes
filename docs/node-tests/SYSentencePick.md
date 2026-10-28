# Sentence Pick SY (`SYSentencePick`)

Source: `nodes/sy_sentence_pick.py`

**What it does:** Splits text into sentences and picks the first few, the last few, one by number, or lists them all numbered.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to split into sentences. | default '', multiline |
| mode | COMBO | yes | first_n and last_n take n sentences. index takes one. all_numbered lists all. | one of: first_n, last_n, index, all_numbered |
| n | INT | yes | How many sentences to take in first_n or last_n mode. | 1 to 100000, default 1 |
| index | INT | yes | Which sentence to take in index mode, counting from 0. | 0 to 100000, default 0 |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; INT=int 0 |
| 2 | text = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 3 | mode = 'last_n' | PASS | STRING=str ''; INT=int 0 |
| 4 | mode = 'index' | REJECTED | ValueError: index 0 is out of range: the text has 0 sentence(s), so use 0 to 0 |
| 5 | mode = 'all_numbered' | PASS | STRING=str ''; INT=int 0 |
| 6 | n = 100000 (max) | PASS | STRING=str ''; INT=int 0 |
| 7 | n = 50000 (mid) | PASS | STRING=str ''; INT=int 0 |
| 8 | index = 100000 (max) | PASS | STRING=str ''; INT=int 0 |
| 9 | index = 50000 (mid) | PASS | STRING=str ''; INT=int 0 |

Note: this node refuses on purpose here (refuses an index when the sample text has no sentences, with a clear message), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 9 cases behaved as expected (8 passed, 1 rejected with a clear message).
