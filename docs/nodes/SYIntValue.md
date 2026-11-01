# Int Value SY (`SYIntValue`)

Source: `nodes/sy_int_value.py`

**What it does:** A whole number. Type it once and plug it into as many nodes as you like. Also gives the same number as a decimal, as text, and an info line that tells if it fits size rules (multiple of 8 or 64) and the video frame rule (4n+1).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | INT | yes | The whole number to send out. | -9007199254740991 to 9007199254740991, default 0 |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`
