# If Else Number SY (`SYIfElseNumber`)

Source: `nodes/sy_if_else_number.py`

**What it does:** Picks one of two numbers. Yes sends if_true. No sends if_false.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| condition | BOOLEAN | yes | Yes sends if_true. No sends if_false. | default True |
| if_true | FLOAT | yes | The number sent when the condition is yes. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| if_false | FLOAT | yes | The number sent when the condition is no. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |

Outputs: `FLOAT`, `INT`
