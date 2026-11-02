# Sharpest Frame Pick SY (`SYSharpestFramePick`)

Source: `nodes/sy_sharpest_frame_pick.py`

**What it does:** From a batch (a burst of renders or video frames) keeps the frames that are least blurry. Also gives a sharpness number for every input frame. Higher means sharper.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of frames to look through. | picture batch [B,H,W,3] |
| keep | INT | yes | How many of the sharpest frames to keep. More than the batch keeps all. | 1 to 64, default 1 |
| keep_order | COMBO | yes | Keep the kept frames in clip order, or put the sharpest first. | one of: original order, best first |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the batch of frames to **images**.
2. Set **keep** to how many of the sharpest frames you want.
3. Pick **keep_order**: original order, or best first.
4. The outputs give the kept **images** and **scores**, a sharpness number for every input frame (higher is sharper).
