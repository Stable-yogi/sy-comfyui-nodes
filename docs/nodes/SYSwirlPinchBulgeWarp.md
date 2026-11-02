# Swirl Pinch Bulge Warp SY (`SYSwirlPinchBulgeWarp`)

Source: `nodes/sy_swirl_pinch_bulge_warp.py`

**What it does:** Twists, pinches or bulges the picture around a point. Swirl turns the picture, pinch pulls it towards the point, bulge pushes it out like a lens. Pixels outside the radius stay as they are.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to warp. | picture batch [B,H,W,3] |
| mode | COMBO | yes | swirl twists, pinch pulls inwards, bulge pushes outwards. | one of: swirl, pinch, bulge |
| strength | FLOAT | yes | How strong the warp is. Negative goes the other way. 0 does nothing. | -2.0 to 2.0, step 0.01, default 0.6 |
| radius | FLOAT | yes | Size of the warped area, as a fraction of the shorter side. | 0.05 to 1.5, step 0.01, default 0.5 |
| centre_x | FLOAT | yes | Where the warp is centred across the picture. 0 is the left edge, 1 the right edge. | 0.0 to 1.0, step 0.01, default 0.5 |
| centre_y | FLOAT | yes | Where the warp is centred down the picture. 0 is the top edge, 1 the bottom edge. | 0.0 to 1.0, step 0.01, default 0.5 |
| edge | COMBO | yes | What fills places that the warp pulls from outside the picture. | one of: stretch, mirror, black |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Pick a **mode** and move **centre_x** and **centre_y** to the spot you want to warp.
3. Set **radius** to the size of the area, then raise **strength** until the look is right. A negative strength goes the other way.
4. The output **IMAGE** has the same size. The warp fades out smoothly at the radius, so there is no hard seam.
