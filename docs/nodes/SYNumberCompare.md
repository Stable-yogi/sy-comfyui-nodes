# Number Compare SY (`SYNumberCompare`)

Source: `nodes/sy_number_compare.py`

**What it does:** Compares number a with number b and gives yes or no. Use it to drive a switch. The optional tolerance treats nearly equal decimals as equal. Also gives a plain info line and the difference a minus b.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| a | FLOAT | yes | The number on the left. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| operator | COMBO | yes | How to compare: equal, not equal, smaller, bigger and so on. | one of: ==, !=, <, <=, >, >= |
| b | FLOAT | yes | The number on the right. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| tolerance | FLOAT | no | Numbers this close count as equal. Fixes 0.1+0.2 vs 0.3. Example: 0.0001. | 0.0 to 1000000000000000.0, step 0.0001, default 0.0 |

Outputs: `BOOLEAN`, `STRING`, `FLOAT`
