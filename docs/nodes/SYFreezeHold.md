# Freeze Hold SY (`SYFreezeHold`)

Source: `nodes/sy_freeze_hold.py`

**What it does:** Holds one frame still for a while inside a clip, then carries on. Either adds extra frames (the clip gets longer) or overwrites the next frames (same length).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| freeze_at | INT | yes | Frame to hold, counting from 0. A number past the end uses the last frame. | 0 to 100000, default 0 |
| hold_frames | INT | yes | How many frames the picture stays still. | 1 to 1000, default 24 |
| replace | BOOLEAN | yes | Off: add extra frames. On: overwrite the following frames so the length stays. | default False |

Outputs: `IMAGE`, `INT`

## How to use

1. Connect the clip's frames, in order, to **images**.
2. Set **freeze_at** to the frame number to hold, counting from 0.
3. Set **hold_frames** to how long it stays still.
4. Set **replace**: off adds extra frames (the clip gets longer), on overwrites the next frames (same length).
5. The outputs give the new **images** and the **new_count** of frames.
