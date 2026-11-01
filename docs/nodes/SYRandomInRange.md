# Random In Range SY (`SYRandomInRange`)

Source: `nodes/sy_random_in_range.py`

**What it does:** Makes a random whole number and a random decimal between two limits. The same seed always gives the same answer. The optional step puts the decimal on a grid (like 0.5), and the info line tells what came out.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seed | INT | yes | Same seed, same numbers. Change it for new numbers. | 0 to 18446744073709551615, default 0 |
| min_value | FLOAT | yes | Lowest number that can come out. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| max_value | FLOAT | yes | Highest number that can come out. Not below min_value. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 100.0 |
| step | FLOAT | no | 0 is off. 0.5 makes the decimal land on 0.5 steps, like a CFG of 6.5. | 0.0 to 1000000000000000.0, step 0.01, default 0.0 |

Outputs: `INT`, `FLOAT`, `STRING`

## How to use

1. Set min_value and max_value (max must not be below min).
2. Set seed. The same seed always gives the same numbers.
3. Optional: step puts the decimal on a grid. 0.5 gives values like 6.5. 0 is off.
Outputs: a whole number, a decimal and an info line.
