# DateParts SY (`SYDateParts`)

Source: `nodes/sy_date_parts.py`

**What it does:** Splits a date into year, month, day, weekday name, day of the year and week number. Use today or type a date.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | now uses today's date. from_text reads the date you type. | one of: now, from_text |
| date_text | STRING | yes | Date as YYYY-MM-DD. Only used in from_text mode. | default '2026-01-01' |

Outputs: `INT`, `INT`, `INT`, `STRING`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 2026; INT=int 10; INT=int 28; STRING=str 'Wednesday'; INT=int 301; INT=int 44 |
| 2 | mode = 'from_text' | PASS | INT=int 2026; INT=int 1; INT=int 1; STRING=str 'Thursday'; INT=int 1; INT=int 1 |
| 3 | date_text = '' (empty) | PASS | INT=int 2026; INT=int 10; INT=int 28; STRING=str 'Wednesday'; INT=int 301; INT=int 44 |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
