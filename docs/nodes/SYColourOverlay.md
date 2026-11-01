# Colour Overlay SY (`SYColourOverlay`)

Source: `nodes/sy_colour_overlay.py`

**What it does:** Lays a flat colour over a picture using a blend mode and opacity. An optional mask limits where it shows (a mask of another size is stretched to fit). Adds an on/off switch and an info line, and keeps transparency.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to colour. | picture batch [B,H,W,3] |
| colour | STRING | yes | The overlay colour, 3 or 6 hex digits like a web colour. | default '#d4a537' |
| opacity | FLOAT | yes | 0 leaves the picture alone, 1 applies the full blend. | 0.0 to 1.0, step 0.01, default 0.5 |
| mode | COMBO | yes | normal paints the colour; multiply darkens; screen lightens; overlay boosts contrast. | one of: normal, multiply, screen, overlay |
| mask | MASK | no | White applies the colour, black keeps the picture. A different size is stretched to fit. | mask [B,H,W] |
| enabled | BOOLEAN | no | Turn off to pass the picture through untouched (handy to compare before and after). | default True |

Outputs: `IMAGE`, `STRING`
