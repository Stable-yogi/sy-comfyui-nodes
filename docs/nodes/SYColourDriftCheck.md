# Colour Drift Check SY (`SYColourDriftCheck`)

Source: `nodes/sy_colour_drift_check.py`

**What it does:** Shows how much brightness and colour strength crept up or down along a clip. Chained clips often get more saturated; this tells you by how much.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| compare_frames | INT | yes | Compare the first this-many frames with the last this-many. | 1 to 50, default 3 |
| warn_percent | INT | yes | Warn when brightness or colour changed by more than this many percent. | 1 to 100, default 5 |

Outputs: `STRING`, `FLOAT`, `FLOAT`, `BOOLEAN`

## How to use

1. Connect the clip's frames, in order, to **images**. It needs at least 2 frames.
2. Set **compare_frames**. The first N frames are compared with the last N, so the clip needs at least twice N frames.
3. Set **warn_percent**: how big a change counts as drift.
4. Read the **report**: first and last numbers, each change in percent, a one-line verdict and a small table of frames.
5. Use **drift_warning** to stop or flag a chain when it turns True.
