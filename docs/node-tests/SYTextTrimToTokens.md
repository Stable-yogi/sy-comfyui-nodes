# Text Trim To Tokens SY (`SYTextTrimToTokens`)

Source: `nodes/sy_text_trim_to_tokens.py`

**What it does:** Cuts a text to a rough token budget, counting 4 characters as 1 token. Keep the start, the end or the middle.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to shorten. | default '', multiline |
| max_tokens | INT | yes | Token budget. One token is counted as 4 characters. | 1 to 1000000, default 256 |
| keep | COMBO | yes | Which part survives when the text is too long. | one of: start, end, middle |

Outputs: `STRING`, `INT`, `BOOLEAN`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; INT=int 0; BOOLEAN=bool False |
| 2 | text = '' (empty) | PASS | STRING=str ''; INT=int 0; BOOLEAN=bool False |
| 3 | max_tokens = 1 (min) | PASS | STRING=str ''; INT=int 0; BOOLEAN=bool False |
| 4 | max_tokens = 1000000 (max) | PASS | STRING=str ''; INT=int 0; BOOLEAN=bool False |
| 5 | max_tokens = 500000 (mid) | PASS | STRING=str ''; INT=int 0; BOOLEAN=bool False |
| 6 | keep = 'end' | PASS | STRING=str ''; INT=int 0; BOOLEAN=bool False |
| 7 | keep = 'middle' | PASS | STRING=str ''; INT=int 0; BOOLEAN=bool False |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
