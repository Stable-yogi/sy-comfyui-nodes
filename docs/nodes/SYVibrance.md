# Vibrance SY (`SYVibrance`)

Source: `nodes/sy_vibrance.py`

**What it does:** Makes dull colours richer without blowing out the colours that are already strong. Skin tones are protected a little. Negative values calm the weak colours instead.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to give richer colours. | picture batch [B,H,W,3] |
| amount | FLOAT | yes | Above 0 lifts dull colours. Below 0 mutes them. 0 does nothing. | -1.0 to 1.0, step 0.01, default 0.4 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **amount**. Start at 0.4 and raise it for a bolder look.
3. Use a negative **amount** to quiet weak colours.
4. The output **IMAGE** has the same size; an alpha channel is passed through.
