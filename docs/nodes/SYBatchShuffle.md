# Batch Shuffle SY (`SYBatchShuffle`)

Source: `nodes/sy_batch_shuffle.py`

**What it does:** Shuffles the order of a batch of pictures. The same seed always gives the same order, and the order is also given as text such as 3,0,2,1.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to shuffle. | picture batch [B,H,W,3] |
| seed | INT | yes | Same number, same order. Change it for a different order. | 0 to 9007199254740992, default 0 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the batch to **images**.
2. Pick a **seed**. Keep it to repeat an order, change it for a new one.
3. Use **images** for the shuffled batch.
4. Read **order** to see which original picture ended up in each place. One picture comes back as "0".
