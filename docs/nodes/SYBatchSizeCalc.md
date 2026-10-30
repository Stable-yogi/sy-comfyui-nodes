# Batch Size Calc SY (`SYBatchSizeCalc`)

Source: `nodes/sy_batch_size_calc.py`

**What it does:** Splits a total number of pictures into runs of at most a set size. Gives the number of runs, the size of the last run and what is left over.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| total | INT | yes | How many pictures you want in all. | 0 to 10000000, default 10 |
| max_per_pass | INT | yes | The most pictures one run can hold, such as what fits in memory. | 1 to 100000, default 4 |

Outputs: `INT`, `INT`, `INT`
