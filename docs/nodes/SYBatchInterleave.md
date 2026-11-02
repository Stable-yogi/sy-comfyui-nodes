# Batch Interleave SY (`SYBatchInterleave`)

Source: `nodes/sy_batch_interleave.py`

**What it does:** Weaves two batches of pictures into one: first of A, first of B, second of A, and so on. If one batch is longer you can keep its extra pictures or stop at the shorter one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images_a | IMAGE | yes | The first batch. Its pictures go first in each pair. | picture batch [B,H,W,3] |
| images_b | IMAGE | yes | The second batch. Its pictures go second in each pair. | picture batch [B,H,W,3] |
| when_uneven | COMBO | yes | If the batches differ in length: keep the extra pictures or stop. | one of: stop at shorter, keep the rest |
| resize_b | BOOLEAN | yes | On: resize B to the size of A if they differ. Off: stop with an error. | default True |

Outputs: `IMAGE`

## How to use

1. Connect the first batch to **images_a** and the second to **images_b**.
2. Choose **when_uneven**.
3. Leave **resize_b** on if the sizes may differ. With it off, different sizes stop with a message.
4. The output **IMAGE** is the woven batch. Batches with different colour channels (3 vs 4) are refused.
