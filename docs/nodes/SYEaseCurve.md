# Ease Curve SY (`SYEaseCurve`)

Source: `nodes/sy_ease_curve.py`

**What it does:** Turns a position from 0 to 1 into a smooth curve value, then scales it between a start and an end number.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| t | FLOAT | yes | How far along, from 0 (start) to 1 (end). | 0.0 to 1.0, step 0.01, default 0.5 |
| curve | COMBO | yes | The shape of the movement. in starts slow, out ends slow, in_out does both. | one of: linear, ease_in_quad, ease_out_quad, ease_in_out_quad, ease_in_cubic, ease_out_cubic, ease_in_out_cubic, smoothstep, smootherstep |
| start | FLOAT | yes | The result when t is 0. | -1000000000.0 to 1000000000.0, step 0.01, default 0.0 |
| end | FLOAT | yes | The result when t is 1. | -1000000000.0 to 1000000000.0, step 0.01, default 1.0 |

Outputs: `FLOAT`, `FLOAT`
