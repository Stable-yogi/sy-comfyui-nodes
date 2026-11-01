# Video Loop Frames SY (`SYVideoLoopFrames`)

Source: `nodes/sy_video_loop_frames.py`

**What it does:** Fills a target frame count by repeating the frames from the start, or by playing them forward and back. Can move the target to a count a video model accepts (4n+1). The info output says how the frames were filled and warns when the last loop is cut short.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to loop. | picture batch [B,H,W,3] |
| target_frames | INT | yes | How many frames the result should have. | 1 to 100000, default 81 |
| mode | COMBO | yes | repeat starts over at the end. ping_pong plays back and forth. | one of: repeat, ping_pong |
| snap_to_rule | BOOLEAN | no | On: move the target to the nearest count that fits the Kn+1 rule, for example 80 becomes 81. | default False |
| frame_step | INT | no | The n in the Kn+1 rule: 4 for Wan and most models, 8 for LTX. Used with snap_to_rule. | 1 to 64, default 4 |

Outputs: `IMAGE`, `INT`, `STRING`
