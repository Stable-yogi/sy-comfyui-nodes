# Number Series SY (`SYNumberSeries`)

Source: `nodes/sy_number_series.py`

**What it does:** Makes a list of evenly spaced numbers from a start to a stop value, both included, as text and a count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| start | FLOAT | yes | The first number in the list. | -1000000000.0 to 1000000000.0, step 0.01, default 0.0 |
| stop | FLOAT | yes | The last number in the list. | -1000000000.0 to 1000000000.0, step 0.01, default 1.0 |
| count | INT | yes | How many numbers to make, including the first and last. | 2 to 1000, step 1, default 5 |
| decimals | INT | yes | How many digits after the point to keep. | 0 to 8, step 1, default 3 |

Outputs: `STRING`, `INT`
