# Mask Island Cleanup SY (`SYMaskIslandCleanup`)

Source: `nodes/sy_mask_island_cleanup.py`

**What it does:** Tidies a mask by deleting tiny white specks and filling tiny black holes. The mask is first turned into pure black and white by the threshold.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to tidy. | mask [B,H,W] |
| min_island | INT | yes | White specks smaller than this many pixels are deleted. 0 keeps all. | 0 to 10000, step 1, default 64 |
| min_hole | INT | yes | Black holes smaller than this many pixels are filled. 0 keeps all. | 0 to 10000, step 1, default 64 |
| threshold | FLOAT | yes | Mask values above this count as white, the rest as black. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `MASK`

## How to use

1. Connect a mask to **mask**.
2. Set **threshold**: values above it count as white, the rest as black.
3. Set **min_island**: white specks smaller than this many pixels are deleted.
4. Set **min_hole**: black holes smaller than this many pixels are filled. Use 0 for either to keep everything.
5. The output **MASK** is the tidied black and white mask.
