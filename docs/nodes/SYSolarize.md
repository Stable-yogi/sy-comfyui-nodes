# Solarize SY (`SYSolarize`)

Source: `nodes/sy_solarize.py`

**What it does:** Flips every colour value that is above a limit, like a darkroom solarize effect. Alpha is left alone.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| threshold | FLOAT | yes | Colour values at or above this limit are flipped. 0.5 is the classic look. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`
