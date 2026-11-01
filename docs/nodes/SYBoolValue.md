# Bool Value SY (`SYBoolValue`)

Source: `nodes/sy_bool_value.py`

**What it does:** A yes/no switch. Set it once and plug it into as many nodes as you like. Also gives 1 or 0, the opposite switch (so you do not need a Not node) and a plain info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | BOOLEAN | yes | The yes/no value to send out. | default False |

Outputs: `BOOLEAN`, `INT`, `BOOLEAN`, `STRING`
