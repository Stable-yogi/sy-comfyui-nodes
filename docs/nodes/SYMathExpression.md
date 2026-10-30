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
