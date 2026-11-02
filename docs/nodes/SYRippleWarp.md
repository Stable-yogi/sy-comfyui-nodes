# Ripple Warp SY (`SYRippleWarp`)

Source: `nodes/sy_ripple_warp.py`

**What it does:** Warps the picture in waves, like looking through rippling water. Set how far the picture is pushed sideways and up and down, and how long each wave is. Strength 0 does nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to ripple. | picture batch [B,H,W,3] |
| strength_x | FLOAT | yes | How far the picture is pushed sideways, in pixels. | 0.0 to 100.0, step 0.5, default 8.0 |
| strength_y | FLOAT | yes | How far the picture is pushed up and down, in pixels. | 0.0 to 100.0, step 0.5, default 8.0 |
| wavelength | FLOAT | yes | Distance between two wave crests, in pixels. | 4.0 to 2000.0, step 1.0, default 120.0 |
| phase | FLOAT | yes | Slides the waves along. Change it a little each frame to animate. | 0.0 to 360.0, step 1.0, default 0.0 |
| edge | COMBO | yes | What fills the border where the waves pull in space: stretch the edge, black, or mirror. | one of: stretch, black, mirror |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **strength_x** and **strength_y** for how strong the waves are.
3. Set **wavelength** for how wide each wave is.
4. For an animation, change **phase** by a few degrees on every frame.
5. Pick **edge** to choose what fills the border.
