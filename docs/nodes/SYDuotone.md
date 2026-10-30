# Duotone SY (`SYDuotone`)

Source: `nodes/sy_duotone.py`

**What it does:** Recolours a picture using only two colours: one for the dark parts and one for the bright parts.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to recolour. | picture batch [B,H,W,3] |
| shadow_colour | STRING | yes | Colour for the darkest parts, as 3 or 6 hex digits like a web colour. | default '#1b1b2f' |
| highlight_colour | STRING | yes | Colour for the brightest parts, as 3 or 6 hex digits like a web colour. | default '#f5d58a' |
| strength | FLOAT | yes | How much duotone to apply. 0 keeps the original colours. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`
