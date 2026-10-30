# Round To Multiple SY (`SYRoundToMultiple`)

Source: `nodes/sy_round_to_multiple.py`

**What it does:** Rounds a number to a multiple of a step, like 64 for image sizes. Choose nearest, round up or round down.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The number to round. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 100.0 |
| multiple | FLOAT | yes | Round to a whole number of these steps. Must be above 0. | 1e-06 to 1000000000000000.0, step 0.01, default 64.0 |
| mode | COMBO | yes | nearest goes to the closest step. up goes higher. down goes lower. | one of: nearest, up, down |

Outputs: `FLOAT`, `INT`
