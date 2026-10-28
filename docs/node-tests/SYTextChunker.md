# Text Chunker SY (`SYTextChunker`)

Source: `nodes/sy_text_chunker.py`

**What it does:** Splits a long text into pieces of at most a set number of characters, with overlap. Gives you one piece by index, and the piece count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The long text to split. | default '', multiline |
| max_chars | INT | yes | Longest allowed piece, in characters. | 1 to 1000000, default 1000 |
| overlap | INT | yes | Characters repeated at the start of the next piece. Less than max_chars. | 0 to 999999, default 100 |
| index | INT | yes | Which piece to output, counting from 0. | 0 to 1000000, default 0 |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: text is empty: there is nothing to split |
| 2 | text = '' (empty) | REJECTED | ValueError: text is empty: there is nothing to split |
| 3 | max_chars = 1 (min) | REJECTED | ValueError: overlap (100) must be smaller than max_chars (1) |
| 4 | max_chars = 1000000 (max) | REJECTED | ValueError: text is empty: there is nothing to split |
| 5 | max_chars = 500000 (mid) | REJECTED | ValueError: text is empty: there is nothing to split |
| 6 | overlap = 0 (min) | REJECTED | ValueError: text is empty: there is nothing to split |
| 7 | overlap = 999999 (max) | REJECTED | ValueError: overlap (999999) must be smaller than max_chars (1000) |
| 8 | overlap = 499999 (mid) | REJECTED | ValueError: overlap (499999) must be smaller than max_chars (1000) |
| 9 | index = 1000000 (max) | REJECTED | ValueError: text is empty: there is nothing to split |
| 10 | index = 500000 (mid) | REJECTED | ValueError: text is empty: there is nothing to split |

## Verdict

All 10 cases behaved as expected (0 passed, 10 rejected with a clear message).
