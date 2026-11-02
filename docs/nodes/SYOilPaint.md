# Oil Paint SY (`SYOilPaint`)

Source: `nodes/sy_oil_paint.py`

**What it does:** Gives the picture a painted look. Each pixel takes the average colour of the calmest of four neighbouring patches, so areas turn smooth while edges stay sharp.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to turn into a painting. | picture batch [B,H,W,3] |
| radius | INT | yes | Size of the brush patches in pixels. Bigger gives broader strokes and runs slower. | 1 to 10, default 4 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **radius**: 1 or 2 for a light touch, 6 to 10 for heavy brush strokes.
3. The output **IMAGE** has the same size; an alpha channel is passed through.
