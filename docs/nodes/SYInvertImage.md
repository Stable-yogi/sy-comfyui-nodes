# Invert Image SY (`SYInvertImage`)

Source: `nodes/sy_invert_image.py`

**What it does:** Inverts the colours of a picture like a photo negative. Can invert only red, green or blue. Transparency is left alone. Add a mask to invert only part of the picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to invert. | picture batch [B,H,W,3] |
| channels | COMBO | yes | Which colours to flip. rgb flips all three; red, green or blue flips just that one. | one of: rgb, red, green, blue |
| mask | MASK | no | Optional. Change only where this mask is white. A different size is stretched to fit. | mask [B,H,W] |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or batch to image.
2. Pick channels. rgb flips all three colours; red, green or blue flips just that one. Transparency is left alone.
3. Optional: connect a mask to invert only the white area. The picture and an info line come out.
