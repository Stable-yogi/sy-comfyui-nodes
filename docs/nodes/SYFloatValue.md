# Float Value SY (`SYFloatValue`)

Source: `nodes/sy_float_value.py`

**What it does:** A decimal number. Type it once and plug it into as many nodes as you like. Also gives the nearest whole number.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The decimal number to send out. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |

Outputs: `FLOAT`, `INT`
