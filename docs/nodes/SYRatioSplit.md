# RatioSplit SY (`SYRatioSplit`)

Source: `nodes/sy_ratio_split.py`

**What it does:** Shares a number out by a ratio. For example 100 split 1:3 gives 25 and 75. Up to four parts.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| total | FLOAT | yes | The number to share out. | -1000000000.0 to 1000000000.0, step 0.01, default 100.0 |
| ratios | STRING | yes | Up to four numbers split by colons, like 1:2:1. No negatives. | default '1:2:1' |

Outputs: `FLOAT`, `FLOAT`, `FLOAT`, `FLOAT`, `STRING`
