# Clarity SY (`SYClarity`)

Source: `nodes/sy_clarity.py`

**What it does:** Adds local contrast so mid-tone detail looks crisper, without the bright glow lines a plain sharpen makes. Negative amounts soften the detail. 0 does nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to add crispness to. | picture batch [B,H,W,3] |
| radius | INT | yes | How big the detail is, in pixels. Bigger works on broader shapes. | 2 to 100, default 20 |
| amount | FLOAT | yes | How strong the effect is. Below 0 softens. 0 does nothing. | -1.0 to 2.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **radius**: small for fine texture, large for broad shapes.
3. Raise **amount** until the detail looks crisp but not harsh.
4. The output **IMAGE** has the same size; an alpha channel is passed through.
