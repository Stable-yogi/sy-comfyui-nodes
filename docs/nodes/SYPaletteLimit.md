# Palette Limit SY (`SYPaletteLimit`)

Source: `nodes/sy_palette_limit.py`

**What it does:** Reduces a picture to a small number of colours for a poster or pixel-art look. The colour list is also given as text, darkest first.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to reduce. All of them share one colour list. | picture batch [B,H,W,3] |
| colours | INT | yes | How many colours the result may use. | 2 to 64, default 8 |
| dither | COMBO | yes | Ordered 4x4 adds a fine checker pattern that hides banding. | one of: none, ordered 4x4 |
| seed | INT | yes | Same seed and same picture give the same colours every time. | 0 to 2147483647, default 0 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or a batch to **image**. All pictures share one colour list.
2. Set **colours** to how many colours the result may use, for example 8.
3. Set **dither** to ordered 4x4 for a fine pattern that hides banding, or none for flat areas.
4. Keep **seed** the same (for example 0) to get the same colours every time.
5. The second output **palette** gives the colour list as text, darkest first.
