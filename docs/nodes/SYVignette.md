# Vignette SY (`SYVignette`)

Source: `nodes/sy_vignette.py`

**What it does:** Darkens the edges and corners of a picture. Strength sets how dark, softness sets how far in the fade reaches. Move the bright centre onto your subject with centre_x and centre_y. The info output says what was done.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to darken at the edges. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How dark the corners get. 0 changes nothing, 1 is black. | 0.0 to 1.0, step 0.01, default 0.5 |
| softness | FLOAT | yes | How wide the fade is. Small is a tight dark rim, 1 fades from the centre. | 0.05 to 1.0, step 0.01, default 0.5 |
| centre_x | FLOAT | no | Where the bright centre sits across the picture. 0 is left, 0.5 the middle, 1 right. | 0.0 to 1.0, step 0.01, default 0.5 |
| centre_y | FLOAT | no | Where the bright centre sits down the picture. 0 is top, 0.5 the middle, 1 bottom. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or a batch to image.
2. Set strength (0 changes nothing, 1 is black corners) and softness (small is a tight rim, 1 fades from the centre).
3. Optional: move the bright centre with centre_x and centre_y onto your subject.
4. The picture comes out on image with an info line.
