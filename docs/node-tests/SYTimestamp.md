# Timestamp SY (`SYTimestamp`)

Source: `nodes/sy_timestamp.py`

**What it does:** Gives the current date and time as text. Handy for file names, folders and notes.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| format | COMBO | yes | Which look the text has. Compact has no separators. Unix is seconds. | one of: date, time, date_time, compact, unix |
| use_utc | BOOLEAN | yes | On: use world time (UTC). Off: use the clock of this computer. | default False |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '2026-10-28' |
| 2 | format = 'time' | PASS | STRING=str '11-52-11' |
| 3 | format = 'date_time' | PASS | STRING=str '2026-10-28_11-52-11' |
| 4 | format = 'compact' | PASS | STRING=str '20261028115211' |
| 5 | format = 'unix' | PASS | STRING=str '1793168531' |
| 6 | use_utc = True | PASS | STRING=str '2026-10-28' |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).
