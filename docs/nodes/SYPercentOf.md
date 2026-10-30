# PercentOf SY (`SYPercentOf`)

Source: `nodes/sy_percent_of.py`

**What it does:** Does percentage sums. Find a percent of a number, find what percent one number is of another, or raise or lower a number by a percent.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | percent_of: a% of b. what_percent: a is what % of b. change_by_percent: a changed by b%. | one of: percent_of, what_percent, change_by_percent |
| a | FLOAT | yes | The first number. See the mode for how it is used. | -1000000000.0 to 1000000000.0, step 0.01, default 10.0 |
| b | FLOAT | yes | The second number. See the mode for how it is used. | -1000000000.0 to 1000000000.0, step 0.01, default 200.0 |

Outputs: `FLOAT`, `STRING`
