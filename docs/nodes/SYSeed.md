# Seed SY (`SYSeed`)

Source: `nodes/sy_seed.py`

**What it does:** Gives one seed number. Fixed keeps it. Random picks a new one each run. Increment adds 1 each run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seed | INT | yes | The seed number. Same number gives the same picture. | 0 to 18446744073709551615, default 0 |
| mode | COMBO | yes | Fixed keeps the number. Random picks a new one each run. Increment adds 1 each run. | one of: fixed, random, increment |

Outputs: `INT`
