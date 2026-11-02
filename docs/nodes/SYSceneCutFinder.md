# Scene Cut Finder SY (`SYSceneCutFinder`)

Source: `nodes/sy_scene_cut_finder.py`

**What it does:** Finds the frames where the picture suddenly changes (hard cuts) in a batch, so a long clip can be split or checked. cut_indices lists where each scene starts (always begins with 0). cut_count is the number of cuts found.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| sensitivity | FLOAT | yes | Average pixel change between two frames that counts as a cut. Lower finds more cuts. | 0.01 to 1.0, step 0.01, default 0.25 |
| downscale | INT | yes | Shrinks frames before comparing. Bigger is faster and ignores fine noise. | 1 to 16, default 4 |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Connect the clip's frames, in order, to **images**.
2. Set **sensitivity**: lower finds more cuts, higher only finds big jumps.
3. Raise **downscale** to compare faster and ignore fine noise.
4. The outputs give **cut_indices** (the frame where each scene starts, always beginning with 0), **cut_count**, and the **scores** of the changes.
