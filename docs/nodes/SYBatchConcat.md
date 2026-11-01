# Batch Concat SY (`SYBatchConcat`)

Source: `nodes/sy_batch_concat.py`

**What it does:** Joins two to four picture batches into one batch, in order. Other sizes can be resized to match the first. Also tells you how many pictures each part gave and the final size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_1 | IMAGE | yes | First batch. Its size and channels set the size of the result. | picture batch [B,H,W,3] |
| image_2 | IMAGE | yes | Second batch, added after the first. | picture batch [B,H,W,3] |
| resize_to_first | BOOLEAN | yes | On: resize other batches to the first one's size. Off: stop with an error when sizes differ. | default True |
| image_3 | IMAGE | no | Optional third batch. | picture batch [B,H,W,3] |
| image_4 | IMAGE | no | Optional fourth batch. | picture batch [B,H,W,3] |

Outputs: `IMAGE`, `INT`, `STRING`

## How to use

1. Connect two batches to image_1 and image_2. Add image_3 and image_4 if needed.
2. They are joined in order. The size of image_1 sets the size of the result.
3. With resize_to_first on, other batches are resized to match. Off, the node stops with an error when sizes differ.
4. Outputs: the joined images, the total count, and an info line with the count of each part.
