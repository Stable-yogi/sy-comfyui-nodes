# Motion Mask SY (`SYMotionMask`)

Source: `nodes/sy_motion_mask.py`

**What it does:** Shows what moved between frames as a mask. White where a frame differs from the frame before it (or from the first frame), with optional grow and blur to make the shape easier to use.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| threshold | FLOAT | yes | How much a pixel must change to count as moved. Lower finds smaller changes. | 0.0 to 1.0, step 0.01, default 0.08 |
| grow | INT | yes | Makes the white areas bigger by this many pixels, to close small gaps. | 0 to 50, default 3 |
| blur | INT | yes | Softens the edge of the mask. 0 keeps it hard. | 0 to 50, default 2 |
| compare | COMBO | yes | Compare each frame with the one before it, or with the first frame of the clip. | one of: previous frame, first frame |

Outputs: `MASK`

## How to use

1. Connect the clip frames, in order, to **images**.
2. Pick **compare**: previous frame shows fresh movement, first frame shows everything that has changed since the start.
3. Set **threshold**: lower picks up faint movement, higher keeps only strong changes.
4. Use **grow** and **blur** to fill small holes and soften the edge.
5. Use the output **MASK** to cut out or protect the moving parts.
