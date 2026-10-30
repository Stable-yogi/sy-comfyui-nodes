# Invert Image SY (`SYInvertImage`)

Source: `nodes/sy_invert_image.py`

**What it does:** Inverts the colours of a picture like a photo negative. Can invert only red, green or blue. Transparency is left alone.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to invert. | picture batch [B,H,W,3] |
| channels | COMBO | yes | Which colours to flip. rgb flips all three; red, green or blue flips just that one. | one of: rgb, red, green, blue |

Outputs: `IMAGE`
