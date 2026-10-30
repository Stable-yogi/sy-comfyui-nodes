# Vignette SY (`SYVignette`)

Source: `nodes/sy_vignette.py`

**What it does:** Darkens the edges and corners of a picture. Strength sets how dark, softness sets how far in the fade reaches.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to darken at the edges. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How dark the corners get. 0 changes nothing, 1 is black. | 0.0 to 1.0, step 0.01, default 0.5 |
| softness | FLOAT | yes | How wide the fade is. Small is a tight dark rim, 1 fades from the centre. | 0.05 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`
