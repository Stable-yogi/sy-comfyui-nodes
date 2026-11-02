# Batch Max Blend SY (`SYBatchMaxBlend`)

Source: `nodes/sy_batch_max_blend.py`

**What it does:** Keeps the brightest value at every pixel over all frames: light trails, stars, sparks. With decay above 0, older light fades. Frames are processed one at a time.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| start | INT | yes | The first frame to use. 0 is the first frame of the clip. | 0 to 100000, default 0 |
| count | INT | yes | How many frames to use. 0 means all frames to the end. | 0 to 100000, default 0 |
| decay | FLOAT | yes | 0 = trails never fade. Higher = older light fades faster. | 0.0 to 1.0, step 0.01, default 0.0 |
| output | COMBO | yes | One finished picture, or the growing trail after every frame. | one of: last frame of trail, every step |

Outputs: `IMAGE`

## How to use

1. Connect the clip's frames, in order, to **images**.
2. Set **start** and **count** to pick a part of the clip.
3. Set **decay**: 0 keeps every trail forever, higher values make old light fade.
4. Pick **output**: "last frame of trail" gives one picture, "every step" gives a clip of the same length as the used range, showing the trail growing.
