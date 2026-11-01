# Clamp Remap SY (`SYClampRemap`)

Source: `nodes/sy_clamp_remap.py`

**What it does:** Keeps a number inside a range, and moves it from one range to another. Example: 0 to 1 becomes 0 to 255. Also tells you when the number was outside the range, with a plain info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The number to change. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.5 |
| in_min | FLOAT | yes | Start of the range the number comes from. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| in_max | FLOAT | yes | End of the range the number comes from. Must differ from in_min. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 1.0 |
| out_min | FLOAT | yes | Start of the range the number goes to. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| out_max | FLOAT | yes | End of the range the number goes to. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 100.0 |
| clamp | BOOLEAN | yes | On keeps the result inside the output range. Off lets it run past. | default True |

Outputs: `FLOAT`, `FLOAT`, `BOOLEAN`, `STRING`

## How to use

1. Set value.
2. Set in_min and in_max (the range it is in) and out_min and out_max (the range you want).
3. Turn clamp on to keep the number inside the range.
4. Outputs: remapped, clamped, was_outside and info. Example: 0 to 1 becomes 0 to 255.
