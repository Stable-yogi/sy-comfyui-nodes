# System Info SY (`SYSystemInfo`)

Source: `nodes/sy_system_info.py`

**What it does:** Reports free video memory and free system memory as a short text and two numbers. Shows -1 if unknown.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| (none) | | | | |

Outputs: `STRING`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'VRAM: 3% used, 95346 of 97886 MB free (ok) RAM: 44% used, 109711 of 194196 MB...'; INT=int 95346; INT=int 109711 |

## Verdict

All 1 cases behaved as expected (1 passed, 0 rejected with a clear message).
