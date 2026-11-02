# Radial Zoom Blur SY (`SYRadialZoomBlur`)

Source: `nodes/sy_radial_zoom_blur.py`

**What it does:** Speed-tunnel blur. Pixels are smeared along lines going toward a chosen centre, stronger toward the edges and untouched at the centre itself.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (or batch of pictures) to blur. | picture batch [B,H,W,3] |
| amount | FLOAT | yes | How far the smear reaches, as a share of the distance to the centre. 0 is no blur. | 0.0 to 0.5, step 0.005, default 0.1 |
| samples | INT | yes | Number of copies averaged. More is smoother but slower. | 4 to 32, default 12 |
| centre_x | FLOAT | yes | Horizontal position of the blur centre. 0 is left, 1 is right. | 0.0 to 1.0, step 0.01, default 0.5 |
| centre_y | FLOAT | yes | Vertical position of the blur centre. 0 is top, 1 is bottom. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **centre_x** and **centre_y** to where the tunnel points (0 to 1, 0.5 is the middle).
3. Raise **amount** for a longer smear; 0 means no blur.
4. Raise **samples** for a smoother result (slower).
5. The output **IMAGE** is the blurred picture.
