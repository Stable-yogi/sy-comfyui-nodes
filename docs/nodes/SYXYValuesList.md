# XY Values List SY (`SYXYValuesList`)

Source: `nodes/sy_xy_values_list.py`

**What it does:** Builds the list of values for one side of an XY plot: a number range, a typed list, or a run of seeds.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | numbers = a range, text list = values you type, seeds = a run of seed numbers. | one of: numbers, text list, seeds |
| start | FLOAT | yes | First number of the range (numbers mode). | -1000000.0 to 1000000.0, step 0.01, default 1.0 |
| stop | FLOAT | yes | Last number of the range (numbers mode). | -1000000.0 to 1000000.0, step 0.01, default 8.0 |
| steps | INT | yes | How many numbers in the range, including first and last. | 1 to 64, default 4 |
| text | STRING | yes | Values separated by commas or new lines (text list mode). | default 'euler, dpmpp_2m, ddim', multiline |
| seed_first | INT | yes | First seed (seeds mode). | 0 to 9223372036854775807, default 0 |
| seed_count | INT | yes | How many seeds to make (seeds mode). | 1 to 64, default 4 |
| seed_step | INT | yes | Added to each seed to get the next one (seeds mode). | -1000000 to 1000000, default 1 |

Outputs: `STRING`, `INT`
