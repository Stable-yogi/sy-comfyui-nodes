# NumberWrap SY (`SYNumberWrap`)

Source: `nodes/sy_number_wrap.py`

**What it does:** Keeps a number inside a range. It can wrap round, bounce back and forth, or stop at the edges.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The number to keep inside the range. | -1000000000.0 to 1000000000.0, step 0.01, default 0.0 |
| low | FLOAT | yes | Lowest allowed number. | -1000000000.0 to 1000000000.0, step 0.01, default 0.0 |
| high | FLOAT | yes | Highest allowed number. Must be bigger than low. | -1000000000.0 to 1000000000.0, step 0.01, default 1.0 |
| mode | COMBO | yes | wrap loops round, ping_pong bounces back, clamp stops at the edge. | one of: wrap, ping_pong, clamp |

Outputs: `FLOAT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 0; STRING=str 'wrap: 0.0 -> 0.0 (range 0.0 to 1.0)' |
| 2 | value = -1000000000.0 (min) | PASS | FLOAT=float 0; STRING=str 'wrap: -1000000000.0 -> 0.0 (range 0.0 to 1.0)' |
| 3 | value = 1000000000.0 (max) | PASS | FLOAT=float 0; STRING=str 'wrap: 1000000000.0 -> 0.0 (range 0.0 to 1.0)' |
| 4 | low = -1000000000.0 (min) | PASS | FLOAT=float 0; STRING=str 'wrap: 0.0 -> 0.0 (range -1000000000.0 to 1.0)' |
| 5 | low = 1000000000.0 (max) | REJECTED | ValueError: high must be bigger than low, got low=1000000000.0 high=1.0 |
| 6 | high = -1000000000.0 (min) | REJECTED | ValueError: high must be bigger than low, got low=0.0 high=-1000000000.0 |
| 7 | high = 1000000000.0 (max) | PASS | FLOAT=float 0; STRING=str 'wrap: 0.0 -> 0.0 (range 0.0 to 1000000000.0)' |
| 8 | high = 0.0 (mid) | REJECTED | ValueError: high must be bigger than low, got low=0.0 high=0.0 |
| 9 | mode = 'ping_pong' | PASS | FLOAT=float 0; STRING=str 'ping_pong: 0.0 -> 0.0 (range 0.0 to 1.0)' |
| 10 | mode = 'clamp' | PASS | FLOAT=float 0; STRING=str 'clamp: 0.0 -> 0.0 (range 0.0 to 1.0)' |

## Verdict

All 10 cases behaved as expected (7 passed, 3 rejected with a clear message).
