# Math Expression SY (`SYMathExpression`)

Source: `nodes/sy_math_expression.py`

**What it does:** Works out a formula you type, like a * 2 + b. Uses a, b, c and min max abs round floor ceil sqrt. Safe: it only does maths.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| expression | STRING | yes | The formula. Use + - * / // % ** brackets, a b c and functions. | default 'a + b' |
| a | FLOAT | no | Value for the letter a in the formula. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| b | FLOAT | no | Value for the letter b in the formula. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| c | FLOAT | no | Value for the letter c in the formula. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |

Outputs: `INT`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 0; FLOAT=float 0 |
| 2 | expression = '' (empty) | REJECTED | ValueError: The formula is empty. Type something like a * 2 + b. |
| 3 | a = -1000000000000000.0 (min) | PASS | INT=int -1000000000000000; FLOAT=float -1e+15 |
| 4 | a = 1000000000000000.0 (max) | PASS | INT=int 1000000000000000; FLOAT=float 1e+15 |
| 5 | b = -1000000000000000.0 (min) | PASS | INT=int -1000000000000000; FLOAT=float -1e+15 |
| 6 | b = 1000000000000000.0 (max) | PASS | INT=int 1000000000000000; FLOAT=float 1e+15 |
| 7 | c = -1000000000000000.0 (min) | PASS | INT=int 0; FLOAT=float 0 |
| 8 | c = 1000000000000000.0 (max) | PASS | INT=int 0; FLOAT=float 0 |

## Verdict

All 8 cases behaved as expected (7 passed, 1 rejected with a clear message).
