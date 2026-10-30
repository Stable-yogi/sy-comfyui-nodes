# Colour Match SY (`SYColourMatch`)

Source: `nodes/sy_colour_match.py`

**What it does:** Makes a picture look like the colours of a reference picture. Good for keeping a series of pictures in one look.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| reference | IMAGE | yes | The picture whose colours are copied. A batch is matched one to one, then repeats. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How far to move towards the reference. 0 changes nothing, 1 is a full match. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`
