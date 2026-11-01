# PasteBack SY (`SYPasteBack`)

Source: `nodes/sy_crop_paste.py`

**What it does:** Pastes a processed crop back into the original picture with a soft edge, using the crop info from Crop By Mask SY. Has a strength slider and an on/off switch, and keeps the original transparency.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The original picture, the same one that was cropped. | picture batch [B,H,W,3] |
| crop | IMAGE | yes | The processed crop. It is resized to the crop box if its size differs. | picture batch [B,H,W,3] |
| crop_info | STRING | yes | The crop_info output of Crop By Mask SY. | default '' |
| feather | INT | yes | Width in pixels of the soft seam. 0 gives a hard edge. | 0 to 512, step 1, default 16 |
| crop_mask | MASK | no | Only paste where this mask is white. Leave empty to paste the whole crop. | mask [B,H,W] |
| strength | FLOAT | no | How strongly the crop replaces the original. 1 = fully, 0.5 = half blend, 0 = nothing. | 0.0 to 1.0, step 0.01, default 1.0 |
| enabled | BOOLEAN | no | Turn off to pass the original picture through untouched. | default True |

Outputs: `IMAGE`, `STRING`
