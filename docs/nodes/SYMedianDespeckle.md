# Median Despeckle SY (`SYMedianDespeckle`)

Source: `nodes/sy_median_despeckle.py`

**What it does:** Removes small specks and hot pixels by replacing each pixel with the middle value of its neighbours. Edges stay sharp.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch to clean. | picture batch [B,H,W,3] |
| size | INT | yes | Width of the neighbour square in pixels. Odd numbers only; bigger removes bigger specks. | 3 to 15, step 2, default 3 |
| passes | INT | yes | How many times to repeat the cleaning. | 1 to 4, step 1, default 1 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **size** (odd numbers only); bigger removes bigger specks.
3. Raise **passes** to repeat the cleaning if specks remain.
4. The output **IMAGE** is the cleaned picture. Start with the defaults, since too much cleaning softens fine detail.
