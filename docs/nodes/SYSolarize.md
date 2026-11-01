# Solarize SY (`SYSolarize`)

Source: `nodes/sy_solarize.py`

**What it does:** Flips every colour value that is above a limit, like a darkroom solarize effect. Alpha is left alone. The info output says which values were flipped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| threshold | FLOAT | yes | Colour values at or above this limit are flipped. 0.5 is the classic look. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or a batch to image.
2. Set threshold. Colour values at or above it are flipped. 0.5 is the classic look.
3. The picture comes out on image. Alpha is left alone. The info line says which values were flipped.
