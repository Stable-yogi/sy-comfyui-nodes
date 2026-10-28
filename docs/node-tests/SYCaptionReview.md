# Caption Review SY (`SYCaptionReview`)

Source: `nodes/sy_caption_review.py`

**What it does:** Reviews one caption for training: too short or long, words repeated too often, words you banned. Gives true or false and a report.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| caption | STRING | yes | The caption to review. | default '', multiline |
| min_words | INT | yes | Fewer words than this counts as too short. | 0 to 1000, default 5 |
| max_words | INT | yes | More words than this counts as too long. | 1 to 1000, default 75 |
| max_repeat | INT | yes | How often one word may appear. Small words like the and of are ignored. | 1 to 100, default 3 |
| banned_words | STRING | yes | Words or phrases that must not appear. Separate with commas or new lines. | default '', multiline |

Outputs: `BOOLEAN`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |
| 2 | caption = '' (empty) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |
| 3 | min_words = 0 (min) | PASS | BOOLEAN=bool True; STRING=str 'OK: 0 words, no problems.' |
| 4 | min_words = 1000 (max) | REJECTED | ValueError: min_words must be 0 or more and not bigger than max_words (got 1000 and 75) |
| 5 | min_words = 500 (mid) | REJECTED | ValueError: min_words must be 0 or more and not bigger than max_words (got 500 and 75) |
| 6 | max_words = 1 (min) | REJECTED | ValueError: min_words must be 0 or more and not bigger than max_words (got 5 and 1) |
| 7 | max_words = 1000 (max) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |
| 8 | max_words = 500 (mid) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |
| 9 | max_repeat = 1 (min) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |
| 10 | max_repeat = 100 (max) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |
| 11 | max_repeat = 50 (mid) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |
| 12 | banned_words = '' (empty) | PASS | BOOLEAN=bool False; STRING=str 'NOT OK: 1 problem - too short: 0 words, at least 5 wanted' |

## Verdict

All 12 cases behaved as expected (9 passed, 3 rejected with a clear message).
