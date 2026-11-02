# Duplicate Frame Drop SY (`SYDuplicateFrameDrop`)

Source: `nodes/sy_duplicate_frame_drop.py`

**What it does:** Drops frames that did not change from the frame before. Tells you which frames stayed and how many were dropped. At least one frame always stays.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| tolerance | FLOAT | yes | A frame changing by no more than this (average per pixel, 0 to 1) counts as a copy. | 0.0 to 0.2, step 0.001, default 0.004 |
| keep_first | BOOLEAN | yes | On: always keep the first frame. Off: the first frame can be dropped too. | default True |

Outputs: `IMAGE`, `STRING`, `INT`

## How to use

1. Connect the clip frames, in order, to **images**.
2. Set **tolerance**: 0 drops only exact copies; a little higher also drops frames that differ only by noise.
3. Leave **keep_first** on unless the first frame should go too.
4. Use the output **IMAGE** as the shorter clip, and **kept_indices** to see which frames stayed.
