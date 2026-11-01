# Posterize SY (`SYPosterize`)

Source: `nodes/sy_posterize.py`

**What it does:** Reduces each colour channel to a small number of flat levels for a poster or cartoon look. The info output lists the steps kept and the most colours left.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to flatten into fewer colours. | picture batch [B,H,W,3] |
| levels | INT | yes | How many brightness steps each colour channel keeps. 2 is the harshest. | 2 to 256, default 4 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture to image.
2. Set levels, the number of steps each colour channel keeps. 2 is the harshest.
3. The image comes out with flat colours. The info output lists the steps kept and the most colours left.
