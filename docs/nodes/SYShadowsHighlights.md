# Shadows Highlights SY (`SYShadowsHighlights`)

Source: `nodes/sy_shadows_highlights.py`

**What it does:** Opens up dark areas and calms very bright areas without a mask. It looks at how bright each neighbourhood is, so edges stay free of bright rims. Shadows 0 and highlights 0 do nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to rebalance. | picture batch [B,H,W,3] |
| shadows | FLOAT | yes | Above 0 brightens the dark areas, below 0 darkens them. | -1.0 to 1.0, step 0.01, default 0.3 |
| highlights | FLOAT | yes | Below 0 darkens the very bright areas, above 0 brightens them. | -1.0 to 1.0, step 0.01, default -0.2 |
| tonal_width | FLOAT | yes | How far into the mid-tones each of the two effects reaches. | 0.1 to 1.0, step 0.01, default 0.5 |
| radius | INT | yes | Softness of the brightness map in pixels. Bigger avoids bright rims on edges. | 1 to 200, default 30 |
| colour_keep | FLOAT | yes | How much of the original colour stays while brightness changes. | 0.0 to 1.0, step 0.01, default 0.8 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Raise **shadows** to lift dark areas; lower **highlights** to bring back detail in bright areas.
3. Use **tonal_width** to let the effect reach further into the mid-tones.
4. Increase **radius** if you see bright or dark rims along edges.
5. Lower **colour_keep** if lifted shadows look too colourful.
6. The output **IMAGE** has the same size; an alpha channel is passed through.
