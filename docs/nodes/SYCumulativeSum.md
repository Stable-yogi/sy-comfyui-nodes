# Cumulative Sum SY (`SYCumulativeSum`)

Source: `nodes/sy_cumulative_sum.py`

**What it does:** Running total of a list of numbers. Also running average, maximum, minimum, or the difference from the previous number. Separate the numbers with commas, spaces or new lines.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| numbers | STRING | yes | The numbers, separated by commas, spaces or new lines. | default '1, 2, 3, 4', multiline |
| mode | COMBO | yes | What to work out after each number. | one of: running total, running average, running maximum, running minimum, difference from previous |
| separator | STRING | yes | Text put between the numbers in the result. | default ', ' |
| decimals | INT | yes | How many decimals to show in the result text. | 0 to 10, default 2 |

Outputs: `STRING`, `FLOAT`, `INT`

## How to use

1. Paste the numbers into **numbers**.
2. Pick the **mode**.
3. Set the **separator** and **decimals**.
4. Use **result** as text; **last** is the final value and **count** how many numbers were read.
