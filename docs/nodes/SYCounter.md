# Counter SY (`SYCounter`)

Source: `nodes/sy_counter.py`

**What it does:** Counts up by a step on each run. You feed it the run number, so the same number always gives the same answer.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| run_index | INT | yes | Which run this is, from 0. Connect a batch index or a run counter. | 0 to 9007199254740991, default 0 |
| start | INT | yes | The value on run 0. | -9007199254740991 to 9007199254740991, default 0 |
| step | INT | yes | How much the value changes on each run. Can be negative. | -9007199254740991 to 9007199254740991, default 1 |
| max_value | INT | yes | Highest value before it starts over at start. Used only when wrap is on. | -9007199254740991 to 9007199254740991, default 9 |
| wrap | BOOLEAN | yes | On starts over at start after max_value. Off keeps counting. | default True |

Outputs: `INT`
