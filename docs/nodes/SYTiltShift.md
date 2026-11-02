# Tilt Shift SY (`SYTiltShift`)

Source: `nodes/sy_tilt_shift.py`

**What it does:** Gives the miniature-model look: one band of the picture stays sharp and the rest gets blurrier the farther it is from the band. Blur 0 leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to turn into a miniature look. | picture batch [B,H,W,3] |
| focus_position | FLOAT | yes | Where the sharp band sits: 0 is the top (or left), 1 the bottom (or right). | 0.0 to 1.0, step 0.01, default 0.5 |
| focus_width | FLOAT | yes | How wide the sharp band is, as a share of the picture. | 0.0 to 1.0, step 0.01, default 0.2 |
| blur | FLOAT | yes | The biggest blur in pixels, reached at the far edge. 0 does nothing. | 0.0 to 40.0, step 0.5, default 12.0 |
| vertical | BOOLEAN | yes | Off: the band runs left to right. On: the band runs top to bottom. | default False |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **focus_position** for where the sharp band sits, for example 0.5 for the middle.
3. Set **focus_width** for how wide the band is, for example 0.2, and **blur** for the biggest blur in pixels, for example 12. Blur 0 does nothing.
4. Turn **vertical** on if the band should run top to bottom instead of left to right.
