# CropByMask SY (`SYCropByMask`)

Source: `nodes/sy_crop_paste.py`

**What it does:** Cuts the picture and mask around the white part of the mask. Gives a crop info note for Paste Back SY.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut. | picture batch [B,H,W,3] |
| mask | MASK | yes | Marks the area to keep. Must be the same size as the picture. | mask [B,H,W] |
| padding | INT | yes | Extra pixels kept around the white part for context. | 0 to 4096, step 1, default 32 |
| multiple_of | INT | yes | Crop width and height become a multiple of this. Models like 8 or 64. | 1 to 512, step 1, default 8 |
| threshold | FLOAT | yes | Mask values at or above this count as white. | 0.01 to 1.0, step 0.01, default 0.5 |
| on_empty | COMBO | yes | When nothing is white: crop the whole image, or stop with an error. | one of: whole_image, error |

Outputs: `IMAGE`, `MASK`, `STRING`
