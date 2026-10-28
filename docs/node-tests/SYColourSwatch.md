# Colour Swatch SY (`SYColourSwatch`)

Source: `nodes/sy_colour_swatch.py`

**What it does:** Reads a colour code (like d4a537), gives red, green and blue numbers, a clean code and a small colour picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| colour | STRING | yes | A hex colour: 3 or 6 digits, with or without the # sign. | default 'd4a537' |

Outputs: `INT`, `INT`, `INT`, `STRING`, `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 212; INT=int 165; INT=int 55; STRING=str '#d4a537'; IMAGE=tensor[1, 64, 64, 3] |
| 2 | colour = '' (empty) | REJECTED | ValueError: colour '' is not valid - use 3 or 6 hex digits such as d4a537, with or withou... |

## Verdict

All 2 cases behaved as expected (1 passed, 1 rejected with a clear message).
