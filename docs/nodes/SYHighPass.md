# High Pass SY (`SYHighPass`)

Source: `nodes/sy_high_pass.py`

**What it does:** Keeps only the fine detail of a picture and turns everything else mid grey. Use it to see texture, or choose 'added to original' to sharpen the picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (or batch of pictures) to filter. | picture batch [B,H,W,3] |
| radius | INT | yes | Detail bigger than this many pixels is removed. Small keeps only fine texture. | 1 to 100, default 6 |
| strength | FLOAT | yes | How strongly the detail shows. 0 gives flat grey (or the original). | 0.0 to 4.0, step 0.05, default 1.0 |
| output | COMBO | yes | Show the detail on grey, or add the detail back onto the original to sharpen. | one of: grey detail, added to original |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **radius**: small keeps only fine texture, bigger lets in broader detail.
3. Pick **output**: grey detail shows the detail on grey, added to original sharpens the picture.
4. Raise **strength** to make the detail stronger.
5. The output **IMAGE** is the filtered picture.
