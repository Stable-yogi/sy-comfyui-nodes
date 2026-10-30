# Levels Adjust SY (`SYLevelsAdjust`)

Source: `nodes/sy_levels_adjust.py`

**What it does:** Brightness, contrast, saturation and gamma in one node. Default values change nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to adjust. | picture batch [B,H,W,3] |
| brightness | FLOAT | yes | Adds light. Below 0 darkens, above 0 brightens. | -1.0 to 1.0, step 0.01, default 0.0 |
| contrast | FLOAT | yes | Spread between dark and light. 1 is unchanged, 0 is flat grey. | 0.0 to 3.0, step 0.01, default 1.0 |
| saturation | FLOAT | yes | Colour strength. 1 is unchanged, 0 is black and white. | 0.0 to 3.0, step 0.01, default 1.0 |
| gamma | FLOAT | yes | Middle tones. Above 1 brightens the shadows, below 1 darkens them. | 0.1 to 5.0, step 0.01, default 1.0 |

Outputs: `IMAGE`
