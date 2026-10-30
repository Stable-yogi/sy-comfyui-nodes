# Video Loop Frames SY (`SYVideoLoopFrames`)

Source: `nodes/sy_video_loop_frames.py`

**What it does:** Fills a target frame count by repeating the frames from the start, or by playing them forward and back.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to loop. | picture batch [B,H,W,3] |
| target_frames | INT | yes | How many frames the result should have. | 1 to 100000, default 81 |
| mode | COMBO | yes | repeat starts over at the end. ping_pong plays back and forth. | one of: repeat, ping_pong |

Outputs: `IMAGE`, `INT`
