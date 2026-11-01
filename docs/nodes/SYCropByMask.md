# CropByMask SY (`SYCropByMask`)

Source: `nodes/sy_crop_paste.py`

**What it does:** Cuts the picture and mask around the white part of the mask. Gives a crop info note for Paste Back SY. A mask of the wrong size can be stretched to fit instead of stopping, and a sentence says what was cut.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut. | picture batch [B,H,W,3] |
| mask | MASK | yes | Marks the area to keep. Must be the same size as the picture. | mask [B,H,W] |
| padding | INT | yes | Extra pixels kept around the white part for context. | 0 to 4096, step 1, default 32 |
| multiple_of | INT | yes | Crop width and height become a multiple of this. Models like 8 or 64. | 1 to 512, step 1, default 8 |
| threshold | FLOAT | yes | Mask values at or above this count as white. | 0.01 to 1.0, step 0.01, default 0.5 |
| on_empty | COMBO | yes | When nothing is white: crop the whole image, or stop with an error. | one of: whole_image, error |
| resize_mask | BOOLEAN | no | On: stretch a mask of another size to the picture. Off: stop with a message when sizes differ. | default False |

Outputs: `IMAGE`, `MASK`, `STRING`, `STRING`

## How to use

1. Connect the picture to image and a mask to mask.
2. The crop is made around the white part. Use padding to add room and multiple_of to snap the size. threshold sets what counts as white.
3. on_empty decides what happens with an empty mask: whole_image or error. Turn on resize_mask to stretch a mask of the wrong size.
4. Outputs: crop, crop_mask, crop_info (for Paste Back SY) and info.
