# Duotone SY (`SYDuotone`)

Source: `nodes/sy_duotone.py`

**What it does:** Recolours a picture using only two colours: one for the dark parts and one for the bright parts. Adds a mask (recolour only the white part), an on/off switch and an info line, and keeps transparency.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to recolour. | picture batch [B,H,W,3] |
| shadow_colour | STRING | yes | Colour for the darkest parts, as 3 or 6 hex digits like a web colour. | default '#1b1b2f' |
| highlight_colour | STRING | yes | Colour for the brightest parts, as 3 or 6 hex digits like a web colour. | default '#f5d58a' |
| strength | FLOAT | yes | How much duotone to apply. 0 keeps the original colours. | 0.0 to 1.0, step 0.01, default 1.0 |
| mask | MASK | no | Optional. White = apply the effect, black = keep the original. A different size is stretched to fit. | mask [B,H,W] |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture to image.
2. Set shadow_colour (dark parts) and highlight_colour (bright parts) as hex codes.
3. Set strength. Optional: connect a mask (recolour only the white part) or turn enabled off.
4. The result comes out as image. Transparency is kept.
