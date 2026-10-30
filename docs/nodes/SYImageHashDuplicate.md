# Image Hash Duplicate Check SY (`SYImageHashDuplicate`)

Source: `nodes/sy_image_hash_duplicate.py`

**What it does:** Compares two pictures with a small fingerprint. Tells you how different they are and if they are near duplicates.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | First picture. If it is a batch, the first picture of the batch is used. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | Second picture. If it is a batch, the first picture of the batch is used. | picture batch [B,H,W,3] |
| hash_size | INT | yes | Fingerprint grid size. 8 gives 64 bits. Bigger notices smaller differences. | 4 to 32, default 8 |
| threshold | INT | yes | Largest number of differing bits that still counts as a near duplicate. | 0 to 1024, default 5 |

Outputs: `INT`, `BOOLEAN`, `STRING`
