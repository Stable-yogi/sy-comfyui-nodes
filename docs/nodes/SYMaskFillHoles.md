# Mask Fill Holes SY (`SYMaskFillHoles`)

Source: `nodes/sy_mask_fill_holes.py`

**What it does:** Fills enclosed holes inside a mask, so a donut becomes a disc. A hole is a black area that cannot reach the edge of the picture. A ring with a gap in it is not closed, so it stays open. The result is pure black and white.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask whose holes should be filled. | mask [B,H,W] |
| threshold | FLOAT | yes | Mask values above this count as white, the rest as black. | 0.0 to 1.0, step 0.01, default 0.5 |
| max_hole_size | INT | yes | Fill only holes up to this many pixels. 0 fills every hole. | 0 to 1000000, step 1, default 0 |
| connectivity | COMBO | yes | 4: outside leaks only in straight lines, diagonal gaps stay shut. 8: it also leaks through diagonal gaps. | one of: 4, 8 |

Outputs: `MASK`

## How to use

1. Connect the mask to **mask**.
2. Set **threshold** to decide what counts as white.
3. Leave **max_hole_size** at 0 to fill every hole, or set a pixel count to fill only small holes and keep the big ones.
4. Pick **connectivity**: 4 treats a diagonal gap in a wall as closed, 8 treats it as open.
5. The output **MASK** is pure black and white with the holes filled.
