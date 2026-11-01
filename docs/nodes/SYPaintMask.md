# Paint Mask SY (`SYPaintMask`)

Source: `nodes/sy_paint_mask.py`

**What it does:** Paint a mask by hand on top of your picture. Gives the mask, a cut-out preview (the mask becomes transparency) and how much is covered.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to paint on. It is shown behind the brush after a run. | picture batch [B,H,W,3] |
| mask_data | STRING | yes | Filled in by the painting area on the node. Leave it alone. | default '' |
| grow | INT | yes | Makes the painted area bigger (plus) or smaller (minus) by this many pixels. | -512 to 512, step 1, default 0 |
| feather | INT | yes | Softens the mask edge by this many pixels. 0 keeps it sharp. | 0 to 512, step 1, default 0 |
| invert | BOOLEAN | yes | Swap painted and unpainted areas (done last). | default False |

Outputs: `MASK`, `IMAGE`, `FLOAT`

## How to use

1. Connect your picture to image and run once. The picture shows on the node.
2. Paint on it with the brush on the node. mask_data is filled in for you, so leave it alone.
3. Set grow (bigger or smaller), feather (soft edge) and invert (swap, done last).
Outputs: the mask, a cut-out preview where the mask becomes transparency, and the percent covered.
