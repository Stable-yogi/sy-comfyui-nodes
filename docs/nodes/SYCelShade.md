# Cel Shade SY (`SYCelShade`)

Source: `nodes/sy_cel_shade.py`

**What it does:** Gives the picture a cartoon look: smooth colours are cut into a few flat steps of brightness and dark ink lines are drawn along the edges.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to turn into a cartoon. | picture batch [B,H,W,3] |
| levels | INT | yes | How many flat brightness steps to use. Fewer looks more graphic. | 2 to 12, default 5 |
| smooth | FLOAT | yes | Softens small detail first so the steps and lines come out clean. 0 skips it. | 0.0 to 3.0, step 0.1, default 1.0 |
| outline | FLOAT | yes | How dark the ink lines are. 0 draws no lines. | 0.0 to 1.0, step 0.01, default 0.6 |
| outline_width | INT | yes | How thick the ink lines are, in pixels. | 1 to 6, default 1 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **levels**: lower gives bolder, flatter colour areas.
3. Raise **smooth** if the result looks noisy or has too many tiny lines.
4. Set **outline** and **outline_width** for the ink lines. Outline 0 turns them off.
5. The output **IMAGE** has the same size; an alpha channel is passed through.
