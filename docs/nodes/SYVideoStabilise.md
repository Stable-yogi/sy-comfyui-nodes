# Video Stabilise SY (`SYVideoStabilise`)

Source: `nodes/sy_video_stabilise.py`

**What it does:** Cancels camera shake. It follows how the whole picture moves from frame to frame and moves each frame back along a smoothed path. Shift only, no turning or zoom. Tells you the move used for every frame.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| smoothing | INT | yes | How many frames the camera path is averaged over. Higher is steadier but may drift. | 1 to 60, default 15 |
| crop_edges | BOOLEAN | yes | On: crop away the empty borders and scale back up. Off: leave black borders. | default True |
| max_shift | INT | yes | Biggest move allowed for any frame, in pixels. Keeps one bad measurement from throwing a frame away. | 1 to 400, default 80 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the clip frames, in order, to **images**.
2. Set **smoothing**: a bigger number gives a steadier shot but follows slow pans less closely.
3. Leave **crop_edges** on to hide the empty borders (the picture gets slightly bigger), or turn it off to keep every pixel and accept black borders.
4. Lower **max_shift** if single frames jump; raise it for strong shake.
5. Use the output **IMAGE** as the steadied clip. A clip with one frame comes back unchanged.
