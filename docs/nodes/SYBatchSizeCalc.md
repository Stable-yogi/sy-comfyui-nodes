# Batch Size Calc SY (`SYBatchSizeCalc`)

Source: `nodes/sy_batch_size_calc.py`

**What it does:** Splits a total number of pictures into runs of at most a set size. Gives the number of runs, the size of the last run and what is left over. Adds the size of a normal run and a plain text such as '10 pictures, at most 4 per run -> 3 runs: 4 + 4 + 2'.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| total | INT | yes | How many pictures you want in all. | 0 to 10000000, default 10 |
| max_per_pass | INT | yes | The most pictures one run can hold, such as what fits in memory. | 1 to 100000, default 4 |

Outputs: `INT`, `INT`, `INT`, `INT`, `STRING`

## How to use

1. Set total (how many pictures you want) and max_per_pass (the most one run can hold).
2. You get passes (number of runs), pass_size, last_pass_size and remainder.
3. The info line reads like: 10 pictures, at most 4 per run -> 3 runs: 4 + 4 + 2.
