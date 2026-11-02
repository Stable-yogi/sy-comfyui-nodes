# Halftone Dots SY (`SYHalftoneDots`)

Source: `nodes/sy_halftone_dots.py`

**What it does:** Gives the picture a newspaper-print look. It is cut into a tilted grid of cells and every cell becomes a round dot: the darker the cell, the bigger the dot.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (or batch of pictures) to turn into dots. | picture batch [B,H,W,3] |
| cell_size | INT | yes | Width of one dot cell in pixels. Bigger cells give coarser dots. | 3 to 64, default 5 |
| angle | FLOAT | yes | Tilt of the dot grid in degrees. 45 is the classic print angle. | 0.0 to 90.0, step 1.0, default 45.0 |
| colour_mode | COMBO | yes | Black dots on white paper, or dots that keep the colour of their cell. | one of: black on white, keep colour |
| softness | FLOAT | yes | How soft the dot edges are. 0 is crisp, 1 is very blurry. | 0.0 to 1.0, step 0.01, default 0.2 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **cell_size**: small cells give fine dots, big cells give coarse dots.
3. Set **angle**; 45 is the classic print look.
4. Pick **colour_mode**: black on white, or keep colour to keep each cell's colour.
5. Raise **softness** if you want soft dot edges. The output **IMAGE** is the dotted picture.
