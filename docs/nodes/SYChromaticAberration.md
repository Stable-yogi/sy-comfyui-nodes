# Chromatic Aberration SY (`SYChromaticAberration`)

Source: `nodes/sy_chromatic_aberration.py`

**What it does:** Adds the colour fringes of a cheap lens: red slides outward and blue inward, more and more toward the edges. Strength 0 leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to give colour fringes. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How many pixels red and blue drift apart at the far corner. 0 does nothing. | 0.0 to 20.0, step 0.1, default 4.0 |
| centre_x | FLOAT | yes | Where the fringes start, left to right. 0.5 is the middle. | 0.0 to 1.0, step 0.01, default 0.5 |
| centre_y | FLOAT | yes | Where the fringes start, top to bottom. 0.5 is the middle. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **strength** to how far red and blue drift apart at the far corner, for example 4.0. At 0 nothing changes.
3. Leave **centre_x** and **centre_y** at 0.5 so the fringes grow from the middle. Move **centre_x** to 0.25 to start them nearer the left.
4. The picture comes out with colour fringes that get stronger toward the edges.
