# Batch Average SY (`SYBatchAverage`)

Source: `nodes/sy_batch_average.py`

**What it does:** Averages the frames of a clip into one picture, like a long exposure. It smooths away moving crowds and traffic. Frames are added one at a time, so long clips are fine.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| start | INT | yes | The first frame to use. 0 is the first frame of the clip. | 0 to 100000, default 0 |
| count | INT | yes | How many frames to average. 0 means all frames to the end. | 0 to 100000, default 0 |
| weighting | COMBO | yes | Even counts every frame the same. Fade in favours later frames, fade out earlier ones. | one of: even, fade in, fade out |

Outputs: `IMAGE`

## How to use

1. Connect the clip's frames, in order, to **images**.
2. Set **start** and **count** to pick a part of the clip. Leave **count** at 0 to use everything to the end.
3. Pick **weighting**. Even gives a plain long exposure.
4. The output **image** is one picture. If **start** is past the end of the clip, the node stops and tells you to lower it.
