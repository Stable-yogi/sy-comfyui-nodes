# Gradient Map SY (`SYGradientMap`)

Source: `nodes/sy_gradient_map.py`

**What it does:** Recolours a picture by mapping its brightness to a colour gradient: darks get the first colour, lights the last. Add a middle colour for three tones. Type colours as web hex like fa0 or ffaa00.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to recolour. | picture batch [B,H,W,3] |
| color_1 | STRING | yes | Colour for the darkest parts, 3 or 6 hex digits. | default '#000000' |
| color_2 | STRING | yes | Colour for the lightest parts, 3 or 6 hex digits. | default '#ffffff' |
| strength | FLOAT | yes | 0 keeps the original picture, 1 uses only the gradient. | 0.0 to 1.0, step 0.01, default 1.0 |
| invert | BOOLEAN | yes | On: swap which parts get the first and last colour. | default False |
| color_3 | STRING | no | Optional middle colour. Leave empty for a plain two colour gradient. | default '' |
| mask | MASK | no | White recolours, black keeps the picture. A different size is stretched to fit. | mask [B,H,W] |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Type two colours as web hex, for example fa0 or ffaa00. **color_1** is for the dark parts, **color_2** for the light parts.
3. Add **color_3** for a middle tone (leave empty for two colours). Use **strength** below 1 to blend with the original.
4. Connect a **mask** to recolour only the white part. **invert** swaps dark and light colours.
