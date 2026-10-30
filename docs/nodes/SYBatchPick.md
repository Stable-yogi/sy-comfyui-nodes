# Batch Pick SY (`SYBatchPick`)

Source: `nodes/sy_batch_pick.py`

**What it does:** Picks a slice of pictures from a batch. Starts at the index and wraps around to the first one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to pick from. | picture batch [B,H,W,3] |
| index | INT | yes | First picture to take, counting from 0. Too big a number wraps around. | 0 to 2147483647, default 0 |
| count | INT | yes | How many pictures to take. It wraps to the start when the batch ends. | 1 to 64, default 1 |

Outputs: `IMAGE`
