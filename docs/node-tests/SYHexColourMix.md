# HexColourMix SY (`SYHexColourMix`)

Source: `nodes/sy_hex_colour_mix.py`

**What it does:** Blends two colours given as hex text. Amount 0 keeps the first colour and 1 gives the second.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| colour_a | STRING | yes | First colour as 3 or 6 hex digits. The # sign is optional. | default '000000' |
| colour_b | STRING | yes | Second colour as 3 or 6 hex digits. The # sign is optional. | default 'ffffff' |
| amount | FLOAT | yes | 0 gives the first colour, 1 gives the second, 0.5 the middle. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `STRING`, `INT`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '#808080'; INT=int 128; INT=int 128; INT=int 128 |
| 2 | colour_a = '' (empty) | REJECTED | ValueError: colour must be 3 or 6 hex digits like the ones in a web colour, got '' |
| 3 | colour_b = '' (empty) | REJECTED | ValueError: colour must be 3 or 6 hex digits like the ones in a web colour, got '' |
| 4 | amount = 0.0 (min) | PASS | STRING=str '#000000'; INT=int 0; INT=int 0; INT=int 0 |
| 5 | amount = 1.0 (max) | PASS | STRING=str '#ffffff'; INT=int 255; INT=int 255; INT=int 255 |

## Verdict

All 5 cases behaved as expected (3 passed, 2 rejected with a clear message).
