# Paste Back Box SY (`SYPasteBackBox`)

Source: `nodes/sy_paste_back.py`

**What it does:** Puts an outpainted or inpainted picture back, or cuts the original area out again, using the crop_box from Outpaint Pad SY. Cut out: returns the part of the picture inside the box. Paste: the box is given in the coordinates of the edited picture, and that part is placed into the target picture at the SAME x,y. Optional soft mask (1 = take from the edited picture) and edge feather make a soft join. Pictures keep their alpha.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The edited or padded picture the box is measured in. | picture batch [B,H,W,3] |
| crop_box | STRING | yes | x,y,width,height from Outpaint Pad SY. Example: 100,0,512,512 | default '' |
| mode | COMBO | yes | Cut the box out of the image, or paste it into the target. | one of: cut out the original area, paste into another picture |
| target | IMAGE | no | Picture to paste into (needed for paste). The box lands at the same x,y. | picture batch [B,H,W,3] |
| mask | MASK | no | Soft paste mask, 1 = take from image. Same size as image or the box. No mask = hard paste. | mask [B,H,W] |
| feather | INT | no | Soft edge of the pasted box, pixels inward. Example: 16 | 0 to 256, default 0 |

Outputs: `IMAGE`, `STRING`
