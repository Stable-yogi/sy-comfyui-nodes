# Camera Shake SY (`SYCameraShake`)

Source: `nodes/sy_camera_shake.py`

**What it does:** Adds a smooth hand-held camera shake to a batch of frames. Each frame moves and turns a little, and the same seed always gives the same shake. crop_zoom enlarges slightly so no empty border shows.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to shake, in order. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | Biggest sideways or up-down shift in pixels. | 0.0 to 500.0, step 0.1, default 6.0 |
| rotation | FLOAT | yes | Biggest turn in degrees. | 0.0 to 45.0, step 0.05, default 0.4 |
| speed | FLOAT | yes | How fast the shake wobbles. Higher is more nervous. | 0.05 to 20.0, step 0.05, default 1.0 |
| seed | INT | yes | Same seed gives the same shake. | 0 to 2147483647, default 0 |
| edge | COMBO | yes | What fills the border: reflect mirrors, border stretches, crop_zoom enlarges so none shows. | one of: reflect, border, crop_zoom |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the frames of your clip to **images**.
2. Set **strength** (how far it moves, in pixels), **rotation** (how much it turns) and **speed** (how nervous it is).
3. Keep **edge** on crop_zoom so no empty border shows. The same **seed** always gives the same shake.
4. Connect the **IMAGE** output to your video save node.
