# Image Hash Duplicate Check SY (`SYImageHashDuplicate`)

Source: `nodes/sy_image_hash_duplicate.py`

**What it does:** Compares two pictures with a small fingerprint. Tells you how different they are, a match percentage, and if they are near duplicates. For a batch, choose which picture of each batch to compare.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | First picture. If it is a batch, the first picture of the batch is used. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | Second picture. If it is a batch, the first picture of the batch is used. | picture batch [B,H,W,3] |
| hash_size | INT | yes | Fingerprint grid size. 8 gives 64 bits. Bigger notices smaller differences. | 4 to 32, default 8 |
| threshold | INT | yes | Largest number of differing bits that still counts as a near duplicate. | 0 to 1024, default 5 |
| index_a | INT | no | Which picture of batch A to use. 0 is the first, -1 the last. | -1000000 to 1000000, default 0 |
| index_b | INT | no | Which picture of batch B to use. 0 is the first, -1 the last. | -1000000 to 1000000, default 0 |

Outputs: `INT`, `BOOLEAN`, `STRING`, `FLOAT`

## How to use

1. Connect two pictures to image_a and image_b. For a batch, the first picture is used unless you set index_a or index_b (-1 is the last).
2. hash_size sets the fingerprint grid. Bigger notices smaller differences.
3. threshold is the largest number of differing bits that still counts as a near duplicate.
4. You get the difference, a true or false for near duplicate, an info line and a match percentage.
