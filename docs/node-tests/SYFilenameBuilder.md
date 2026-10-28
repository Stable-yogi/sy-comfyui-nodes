# Filename Builder SY (`SYFilenameBuilder`)

Source: `nodes/sy_filename_builder.py`

**What it does:** Builds a file name from a pattern. Tokens: {date} {time} {seed} {counter}. Only makes text, saves nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| pattern | STRING | yes | Name with tokens: {date} {time} {seed} {counter}. No slashes. | default 'shot_{date}_{counter}' |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |
| counter | INT | yes | Number used for the {counter} token, shown with 5 digits. | 0 to 2147483647, default 1 |
| extension | STRING | yes | Optional ending such as png or .txt. Leave empty for none. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'shot_2026-10-28_00001' |
| 2 | pattern = '' (empty) | REJECTED | ValueError: pattern is empty: type a name such as shot_{counter} |
| 3 | seed = 9007199254740992 (max) | PASS | STRING=str 'shot_2026-10-28_00001' |
| 4 | seed = 4503599627370496 (mid) | PASS | STRING=str 'shot_2026-10-28_00001' |
| 5 | counter = 0 (min) | PASS | STRING=str 'shot_2026-10-28_00000' |
| 6 | counter = 2147483647 (max) | PASS | STRING=str 'shot_2026-10-28_2147483647' |
| 7 | counter = 1073741823 (mid) | PASS | STRING=str 'shot_2026-10-28_1073741823' |
| 8 | extension = '' (empty) | PASS | STRING=str 'shot_2026-10-28_00001' |

## Verdict

All 8 cases behaved as expected (7 passed, 1 rejected with a clear message).
