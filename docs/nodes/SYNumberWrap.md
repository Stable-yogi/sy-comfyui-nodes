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
