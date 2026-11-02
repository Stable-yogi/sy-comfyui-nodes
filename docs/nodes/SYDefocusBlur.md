# Defocus Blur SY (`SYDefocusBlur`)

Source: `nodes/sy_defocus_blur.py`

**What it does:** Blurs like a camera lens that is out of focus: bright points turn into soft round discs. Highlight boost lets bright points glow into clear discs. Radius under 0.5 does nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to blur. | picture batch [B,H,W,3] |
| radius | FLOAT | yes | Size of the blur discs in pixels. Bigger is blurrier. | 0.5 to 60.0, step 0.5, default 8.0 |
| shape | COMBO | yes | Shape of the lens opening: round disc or six-sided hexagon. | one of: disc, hexagon |
| highlight_boost | FLOAT | yes | Makes bright points glow into clear discs. 0 is a plain even blur. | 0.0 to 1.0, step 0.01, default 0.3 |
| edge | COMBO | yes | What fills the area beyond the picture edge: copy the edge pixels or mirror the picture. | one of: replicate, mirror |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **radius** for how blurry the background should be.
3. Pick **shape**: disc for round highlights, hexagon for a camera-iris look.
4. Raise **highlight_boost** to make bright lights stand out as discs (bright pixels count more in the average, then the result is scaled back, so the picture does not get brighter overall).
5. The output **IMAGE** has the same size; an alpha channel is passed through.

Notes: every disc pixel counts the same. A big radius uses a spread-out pattern of at most 400 samples, and radii above about 7 pixels are worked on a shrunken copy, so large pictures stay fast.
