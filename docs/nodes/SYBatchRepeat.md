# Batch Repeat SY (`SYBatchRepeat`)

Source: `nodes/sy_batch_repeat.py`

**What it does:** Repeats each picture N times in a row, or repeats the whole batch N times.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to repeat. | picture batch [B,H,W,3] |
| times | INT | yes | How many copies of each picture, or of the whole batch. | 1 to 256, default 2 |
| mode | COMBO | yes | each_picture gives 1,1,2,2. whole_batch gives 1,2,1,2. | one of: each_picture, whole_batch |

Outputs: `IMAGE`, `INT`
