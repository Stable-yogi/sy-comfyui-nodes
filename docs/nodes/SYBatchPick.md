# Batch Pick SY (`SYBatchPick`)

Source: `nodes/sy_batch_pick.py`

**What it does:** Picks a slice of pictures from a batch. Starts at the index and wraps around to the first one, or stops with a clear message when wrap is off. Tells you which positions it took.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to pick from. | picture batch [B,H,W,3] |
| index | INT | yes | First picture to take, counting from 0. Too big a number wraps around. | 0 to 2147483647, default 0 |
| count | INT | yes | How many pictures to take. It wraps to the start when the batch ends. | 1 to 64, default 1 |
| wrap | BOOLEAN | no | On: go round to the first picture at the end. Off: stop with an error if the slice does not fit. | default True |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a batch to images.
2. Set index (first picture to take, counting from 0) and count (how many).
3. Turn wrap on to go round to the first picture at the end. Off, the node stops with a message if the slice does not fit.
4. The chosen pictures come out as images, with info on which positions were taken.
