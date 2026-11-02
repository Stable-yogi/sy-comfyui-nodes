# Seamless Tile Blend SY (`SYSeamlessTileBlend`)

Source: `nodes/sy_seamless_tile_blend.py`

**What it does:** Turns a texture into one that repeats without visible seams. The edges are faded into the opposite side of the picture, so the left meets the right and the top meets the bottom.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The texture (or batch of textures) to make seamless. | picture batch [B,H,W,3] |
| blend_width | FLOAT | yes | Share of the picture used for the fade at each edge. Bigger hides seams better. | 0.05 to 0.5, step 0.01, default 0.25 |
| axis | COMBO | yes | Which edges to blend: left and right, top and bottom, or all four. | one of: both, horizontal, vertical |

Outputs: `IMAGE`

## How to use

1. Connect the texture (or a batch of textures) to **image**.
2. Set **blend_width**: bigger hides seams better but fades more of the picture.
3. Pick **axis**: both for a texture that repeats every way, or only horizontal or vertical.
4. The output **IMAGE** is the texture that repeats without visible seams. Place several copies side by side to check it.
