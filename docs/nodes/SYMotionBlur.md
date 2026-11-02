# Motion Blur SY (`SYMotionBlur`)

Source: `nodes/sy_motion_blur.py`

**What it does:** Smears the picture along a direction, like a camera or object that moved while the photo was taken. Angle 0 smears to the right. Length 1 does nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to smear. | picture batch [B,H,W,3] |
| length | INT | yes | How far the smear reaches, in pixels. 1 does nothing. | 1 to 400, default 30 |
| angle | FLOAT | yes | Direction of the smear in degrees. 0 is to the right, 90 is up. | 0.0 to 360.0, step 1.0, default 0.0 |
| shape | COMBO | yes | even: same strength all along. fade out: trail that fades. centred: both sides. | one of: even, fade out, centred |
| samples | INT | yes | How many copies are mixed. More is smoother but slower. | 3 to 64, default 16 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **length** and **angle** for the smear.
3. Choose **shape**: centred keeps objects in place, fade out makes a trail.
4. For a long smear raise **samples** so the copies blend smoothly. The output has the same size.
