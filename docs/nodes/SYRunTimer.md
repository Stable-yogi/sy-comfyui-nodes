# Run Timer SY (`SYRunTimer`)

Source: `nodes/sy_run_timer.py`

**What it does:** Passes any value through and tells how many seconds passed since this node first ran. Turn on reset to restart the clock.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | * | yes | Anything you pass through. It comes out unchanged, and the timer measures the time. |  |
| reset | BOOLEAN | yes | On: restart the timer from zero on this run. | default False |

Outputs: `*`, `FLOAT`
