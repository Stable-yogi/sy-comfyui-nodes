# Posterize SY (`SYPosterize`)

Source: `nodes/sy_posterize.py`

**What it does:** Reduces each colour channel to a small number of flat levels for a poster or cartoon look.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to flatten into fewer colours. | picture batch [B,H,W,3] |
| levels | INT | yes | How many brightness steps each colour channel keeps. 2 is the harshest. | 2 to 256, default 4 |

Outputs: `IMAGE`
