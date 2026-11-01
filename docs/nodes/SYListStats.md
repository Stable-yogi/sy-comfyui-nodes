# List Stats SY (`SYListStats`)

Source: `nodes/sy_list_stats.py`

**What it does:** Reads a list of numbers and gives the count, sum, average, middle value, smallest and largest, plus the spread (stdev) and the sorted list. With ignore_bad on, pieces like 5px are skipped and listed in the info line instead of stopping the run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| numbers | STRING | yes | Numbers separated by commas, spaces or new lines. | default '1, 2, 3', multiline |
| ignore_bad | BOOLEAN | no | On skips pieces that are not numbers (like 5px) and says so in info. Off refuses them. | default False |

Outputs: `INT`, `FLOAT`, `FLOAT`, `FLOAT`, `FLOAT`, `FLOAT`, `STRING`, `FLOAT`, `STRING`, `STRING`

## How to use

1. Type or connect numbers separated by commas, spaces or new lines.
2. Turn on ignore_bad to skip pieces like 5px. They are listed in the info line. Off refuses them.
3. You get the count, sum, average, middle value, smallest, largest, the spread (stdev) and the sorted list.
