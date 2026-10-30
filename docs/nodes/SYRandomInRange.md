# Random In Range SY (`SYRandomInRange`)

Source: `nodes/sy_random_in_range.py`

**What it does:** Makes a random whole number and a random decimal between two limits. The same seed always gives the same answer.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seed | INT | yes | Same seed, same numbers. Change it for new numbers. | 0 to 18446744073709551615, default 0 |
| min_value | FLOAT | yes | Lowest number that can come out. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| max_value | FLOAT | yes | Highest number that can come out. Not below min_value. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 100.0 |

Outputs: `INT`, `FLOAT`
