# Apply LUT SY (`SYApplyLUT`)

Source: `nodes/sy_apply_lut.py`

**What it does:** Changes the colours of a picture with a colour look. Pick a built-in look, or a .cube file from the models/luts or input/luts folder, or paste the text of a .cube file into lut_text (the text wins). Strength 0 keeps the picture, 1 gives the full look. A transparent background (alpha) stays as it was.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to colour. RGB or RGBA; transparency is kept. | picture batch [B,H,W,3] |
| lut | COMBO | yes | A built-in look, or a .cube file from models/luts or input/luts. | one of: none, warm, cool, teal and orange, faded film, black and white, high contrast |
| strength | FLOAT | yes | 0 = original colours, 1 = the full look. | 0.0 to 1.0, step 0.01, default 1.0 |
| lut_text | STRING | no | Paste the text of a .cube file here. If filled, it is used instead of the list. | default '', multiline |

Outputs: `IMAGE`
