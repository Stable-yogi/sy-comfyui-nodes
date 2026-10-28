# Regex Extract SY (`SYRegexExtract`)

Source: `nodes/sy_regex_extract.py`

**What it does:** Finds the first match of a regular expression in a text and gives one group of it, or a default. Limits: pattern 200, text 100000 characters.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to search in (up to 100000 characters). | default '', multiline |
| pattern | STRING | yes | Regular expression to look for (up to 200 characters). | default '(\\d+)' |
| group | INT | yes | Which bracket group to return. 0 is the whole match. | 0 to 99, default 1 |
| default | STRING | yes | Text to return when nothing matches. | default '' |
| ignore_case | BOOLEAN | yes | Treat upper and lower case letters as the same. | default False |

Outputs: `STRING`, `BOOLEAN`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; BOOLEAN=bool False |
| 2 | text = '' (empty) | PASS | STRING=str ''; BOOLEAN=bool False |
| 3 | pattern = '' (empty) | REJECTED | ValueError: pattern is empty: type a regular expression |
| 4 | group = 0 (min) | PASS | STRING=str ''; BOOLEAN=bool False |
| 5 | group = 99 (max) | REJECTED | ValueError: group 99 does not exist: the pattern has 1 group(s) |
| 6 | group = 49 (mid) | REJECTED | ValueError: group 49 does not exist: the pattern has 1 group(s) |
| 7 | default = '' (empty) | PASS | STRING=str ''; BOOLEAN=bool False |
| 8 | ignore_case = True | PASS | STRING=str ''; BOOLEAN=bool False |

## Verdict

All 8 cases behaved as expected (5 passed, 3 rejected with a clear message).
