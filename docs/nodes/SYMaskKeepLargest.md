# Mask Keep Largest SY (`SYMaskKeepLargest`)

Source: `nodes/sy_mask_keep_largest.py`

**What it does:** Keeps only the biggest separate blob or blobs of a mask and drops all the others. Masks longer than 1024 pixels are labelled on a shrunken copy (whole-number steps) and mapped back, so very thin bridges between blobs can be missed there, and sizes are close but not exact. With a batch the kept output is the total over all frames.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to clean up. | mask [B,H,W] |
| threshold | FLOAT | yes | Mask values above this count as white, the rest as black. | 0.0 to 1.0, step 0.01, default 0.5 |
| keep | INT | yes | How many of the biggest blobs to keep. | 1 to 16, step 1, default 1 |
| min_pixels | INT | yes | Blobs smaller than this many pixels are dropped even if they are among the biggest. | 0 to 1000000, step 1, default 0 |
| connectivity | COMBO | yes | 4: pixels join only side to side. 8: pixels also join diagonally. | one of: 4, 8 |

Outputs: `MASK`, `INT`

## How to use

1. Connect the mask to **mask**.
2. Set **keep** to how many of the biggest blobs you want to survive.
3. Raise **min_pixels** to drop blobs that are too small even when fewer than **keep** remain.
4. Pick **connectivity**: 8 joins blobs that touch at a corner.
5. The output **MASK** holds only the kept blobs; **kept** tells you how many there were.
